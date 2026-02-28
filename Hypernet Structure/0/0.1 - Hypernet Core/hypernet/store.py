"""
Hypernet Store

File-backed storage for nodes and links. The Hypernet IS the database —
this is not a wrapper around SQL or a traditional DB. Data is stored as
JSON files in a hierarchy matching the address structure.

Storage layout:
  data/
    nodes/
      1/1/1/1/00001/node.json  (node at address 1.1.1.1.00001)
      2/1/node.json             (node at address 2.1)
    links/
      <hash>.json               (link files, indexed by endpoints)
    indexes/
      by_type.json              (type_address -> [node addresses])
      by_owner.json             (owner_address -> [node addresses])
      links_from.json           (from_address -> [link hashes])
      links_to.json             (to_address -> [link hashes])
    history/
      1/1/v0001.json            (version 1 snapshot of node 1.1)
      1/1/v0002.json            (version 2 snapshot of node 1.1)

This can be swapped for a more efficient backend later without
changing the Node/Link/Graph interfaces.
"""

from __future__ import annotations
import json
import hashlib
import logging
import os
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .address import HypernetAddress
from .node import Node
from .link import Link, LinkStatus
from .addressing import AddressEnforcer, AddressValidator

log = logging.getLogger(__name__)


class FileLock:
    """Advisory file lock for concurrent access to shared files.

    Uses lock files (.lock) with PID tracking for stale lock detection.
    Designed for the GitHub-as-database pattern where multiple AI workers
    and humans may access the same files simultaneously.

    Lock protocol:
      1. Try to create <path>.lock atomically (os.open with O_CREAT|O_EXCL)
      2. Write PID + timestamp into lock file
      3. On success: hold lock, do work, release
      4. On failure: check if lock is stale (holder PID dead or timeout)
      5. If stale: break lock, retry
      6. If not stale: wait and retry up to max_wait

    This is advisory — it only works if all writers use it. The Hypernet
    enforces this by routing all writes through the Store class.
    """

    def __init__(self, path: Path, max_wait: float = 10.0, stale_seconds: float = 60.0):
        self.path = path
        self.lock_path = Path(str(path) + ".lock")
        self.max_wait = max_wait
        self.stale_seconds = stale_seconds
        self._held = False

    def acquire(self) -> bool:
        """Acquire the lock. Returns True on success, False on timeout."""
        start = time.monotonic()
        while True:
            try:
                # Atomic create — fails if file already exists
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"{os.getpid()}:{time.time()}\n".encode())
                os.close(fd)
                self._held = True
                return True
            except FileExistsError:
                # Lock exists — check if stale
                if self._is_stale():
                    self._break_lock()
                    continue
                # Not stale — wait and retry
                elapsed = time.monotonic() - start
                if elapsed >= self.max_wait:
                    log.warning(f"Lock timeout after {elapsed:.1f}s: {self.lock_path}")
                    return False
                time.sleep(0.05)  # 50ms retry interval
            except OSError as e:
                # Parent directory may not exist yet
                self.lock_path.parent.mkdir(parents=True, exist_ok=True)
                continue

    def release(self) -> None:
        """Release the lock."""
        try:
            self.lock_path.unlink(missing_ok=True)
        except OSError:
            pass
        self._held = False

    def _is_stale(self) -> bool:
        """Check if an existing lock is stale (holder dead or timed out)."""
        try:
            content = self.lock_path.read_text(encoding="utf-8").strip()
            pid_str, ts_str = content.split(":", 1)
            pid = int(pid_str)
            ts = float(ts_str)

            # Check if holder process is still alive
            try:
                os.kill(pid, 0)  # Signal 0 = check existence
            except OSError:
                log.info(f"Stale lock (PID {pid} dead): {self.lock_path}")
                return True

            # Check if lock has timed out
            if time.time() - ts > self.stale_seconds:
                log.info(f"Stale lock (>{self.stale_seconds}s old): {self.lock_path}")
                return True

            return False
        except (ValueError, OSError):
            # Corrupt lock file — treat as stale
            return True

    def _break_lock(self) -> None:
        """Force-remove a stale lock."""
        try:
            self.lock_path.unlink(missing_ok=True)
        except OSError:
            pass

    def __del__(self):
        if self._held:
            self.release()


class LockManager:
    """Manages file locks for a Store's data directory.

    Provides two granularities:
      - Node locks: per-node file locking for concurrent writes
      - Index lock: single lock for all index operations (indexes are global)
      - Git lock: single lock for all git operations (commit/push are sequential)

    Usage:
      with lock_manager.node_lock(address):
          store.put_node(node)

      with lock_manager.index_lock():
          store._save_indexes()

      with lock_manager.git_lock():
          git_commit_and_push()
    """

    def __init__(self, root: Path, max_wait: float = 10.0, stale_seconds: float = 60.0):
        self.root = root
        self.lock_dir = root / ".locks"
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.max_wait = max_wait
        self.stale_seconds = stale_seconds

    @contextmanager
    def node_lock(self, address: HypernetAddress):
        """Lock a specific node for writing."""
        lock_file = self.lock_dir / f"node-{str(address).replace('.', '-')}"
        lock = FileLock(lock_file, self.max_wait, self.stale_seconds)
        if not lock.acquire():
            raise TimeoutError(f"Could not acquire node lock for {address}")
        try:
            yield
        finally:
            lock.release()

    @contextmanager
    def index_lock(self):
        """Lock the global index files for writing."""
        lock_file = self.lock_dir / "indexes"
        lock = FileLock(lock_file, self.max_wait, self.stale_seconds)
        if not lock.acquire():
            raise TimeoutError("Could not acquire index lock")
        try:
            yield
        finally:
            lock.release()

    @contextmanager
    def git_lock(self):
        """Lock git operations (commit, push, pull). Only one at a time."""
        lock_file = self.lock_dir / "git"
        lock = FileLock(lock_file, self.max_wait * 3, self.stale_seconds)
        if not lock.acquire():
            raise TimeoutError("Could not acquire git lock")
        try:
            yield
        finally:
            lock.release()

    @contextmanager
    def link_lock(self):
        """Lock link creation (links modify global indexes)."""
        lock_file = self.lock_dir / "links"
        lock = FileLock(lock_file, self.max_wait, self.stale_seconds)
        if not lock.acquire():
            raise TimeoutError("Could not acquire link lock")
        try:
            yield
        finally:
            lock.release()

    def clear_stale_locks(self) -> int:
        """Remove all stale lock files. Returns count of locks cleared."""
        cleared = 0
        for lock_file in self.lock_dir.glob("*.lock"):
            fl = FileLock(lock_file.with_suffix(""))
            fl.lock_path = lock_file
            if fl._is_stale():
                fl._break_lock()
                cleared += 1
        return cleared


class Store:
    """File-backed storage for Hypernet nodes and links.

    Thread-safe via LockManager. All writes acquire advisory file locks
    before modifying data. This enables multiple AI workers and humans
    to access the same data directory concurrently without corruption.
    """

    def __init__(self, root: str | Path, lock_timeout: float = 10.0,
                 enforce_addresses: bool = False, strict: bool = True):
        self.root = Path(root)
        self._nodes_dir = self.root / "nodes"
        self._links_dir = self.root / "links"
        self._index_dir = self.root / "indexes"
        self._history_dir = self.root / "history"

        # Lock manager for concurrent access
        self.locks = LockManager(self.root, max_wait=lock_timeout)

        # Address enforcement (Task 032: Everything Gets an Address)
        self._enforcer: Optional[AddressEnforcer] = None
        if enforce_addresses:
            self.enable_enforcement(strict=strict)

        # In-memory indexes (loaded from disk on init, persisted on write)
        self._node_index: dict[str, str] = {}         # address -> node file path
        self._type_index: dict[str, list[str]] = {}    # type_address -> [node addresses]
        self._owner_index: dict[str, list[str]] = {}   # owner_address -> [node addresses]
        self._links_from: dict[str, list[str]] = {}    # from_address -> [link hashes]
        self._links_to: dict[str, list[str]] = {}      # to_address -> [link hashes]

        self._ensure_dirs()
        self._load_indexes()

    def enable_enforcement(self, strict: bool = True) -> None:
        """Enable address enforcement. All put_node() calls will validate addresses.

        In strict mode, invalid addresses raise ValueError (write blocked).
        In warn mode, invalid addresses log a warning but still persist.
        """
        self._enforcer = AddressEnforcer(self, strict=strict)

    def disable_enforcement(self) -> None:
        """Disable address enforcement."""
        self._enforcer = None

    @property
    def enforcer(self) -> Optional[AddressEnforcer]:
        """Access the address enforcer (None if enforcement is disabled)."""
        return self._enforcer

    def audit_addresses(self) -> "AuditReport":
        """Run an address audit on all nodes in the store.

        Returns an AuditReport with coverage statistics and issues.
        Convenience wrapper around AddressAuditor.
        """
        from .addressing import AddressAuditor, AuditReport
        auditor = AddressAuditor(self)
        return auditor.audit()

    def _ensure_dirs(self) -> None:
        self._nodes_dir.mkdir(parents=True, exist_ok=True)
        self._links_dir.mkdir(parents=True, exist_ok=True)
        self._index_dir.mkdir(parents=True, exist_ok=True)
        self._history_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Node Operations
    # =========================================================================

    def put_node(self, node: Node) -> None:
        """Store a node. Creates or overwrites. Snapshots previous state to history.

        If address enforcement is enabled, validates the node's address first.
        In strict mode, invalid addresses raise ValueError (write blocked).

        Thread-safe: acquires node lock then index lock before writing.
        """
        # Address enforcement gate (Task 032)
        if self._enforcer is not None:
            self._enforcer.enforce_on_create(node)

        path = self._node_path(node.address)

        with self.locks.node_lock(node.address):
            # If node already exists, snapshot current state before overwriting
            if path.exists():
                self._snapshot_to_history(node.address, path)

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(node.to_dict(), indent=2, default=str), encoding="utf-8")

        # Update indexes (separate lock — don't hold node lock during index write)
        addr_str = str(node.address)
        with self.locks.index_lock():
            self._node_index[addr_str] = str(path)

            if node.type_address:
                type_str = str(node.type_address)
                if type_str not in self._type_index:
                    self._type_index[type_str] = []
                if addr_str not in self._type_index[type_str]:
                    self._type_index[type_str].append(addr_str)

            if node.owner:
                owner_str = str(node.owner)
                if owner_str not in self._owner_index:
                    self._owner_index[owner_str] = []
                if addr_str not in self._owner_index[owner_str]:
                    self._owner_index[owner_str].append(addr_str)

            self._save_indexes()

    def get_node(self, address: HypernetAddress) -> Optional[Node]:
        """Retrieve a node by address. Returns None if not found."""
        path = self._node_path(address)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Node.from_dict(data)

    def delete_node(self, address: HypernetAddress, hard: bool = False) -> bool:
        """Soft-delete a node (or hard-delete if specified).

        Thread-safe: acquires node lock then index lock for hard deletes.
        Soft deletes delegate to put_node() which handles its own locking.
        """
        node = self.get_node(address)
        if node is None:
            return False

        if hard:
            with self.locks.node_lock(address):
                path = self._node_path(address)
                path.unlink(missing_ok=True)

            addr_str = str(address)
            with self.locks.index_lock():
                self._node_index.pop(addr_str, None)
                for idx in (self._type_index, self._owner_index):
                    for key in idx:
                        if addr_str in idx[key]:
                            idx[key].remove(addr_str)
                self._save_indexes()
        else:
            node.soft_delete()
            self.put_node(node)  # put_node handles its own locking

        return True

    def list_nodes(
        self,
        prefix: Optional[HypernetAddress] = None,
        type_address: Optional[HypernetAddress] = None,
        owner: Optional[HypernetAddress] = None,
        include_deleted: bool = False,
    ) -> list[Node]:
        """List nodes with optional filtering."""
        addresses: set[str] | None = None

        if type_address:
            type_str = str(type_address)
            addresses = set(self._type_index.get(type_str, []))

        if owner:
            owner_str = str(owner)
            owner_addrs = set(self._owner_index.get(owner_str, []))
            addresses = owner_addrs if addresses is None else addresses & owner_addrs

        if addresses is None:
            addresses = set(self._node_index.keys())

        results = []
        for addr_str in sorted(addresses):
            addr = HypernetAddress.parse(addr_str)
            if prefix and not prefix.is_ancestor_of(addr) and prefix != addr:
                continue
            node = self.get_node(addr)
            if node and (include_deleted or not node.is_deleted):
                results.append(node)

        return results

    def _is_instance_node(self, addr: HypernetAddress) -> bool:
        """Check if an address points to an instance node.

        Uses the explicit Node.is_instance property (LP-3) when set to True.
        Falls back to the address heuristic for backward compatibility with
        nodes that were created before the explicit property existed.
        """
        node = self.get_node(addr)
        if node is not None and node.is_instance:
            return True
        return addr.is_instance  # fallback heuristic

    def count_instances(self, prefix: HypernetAddress) -> int:
        """Count instance nodes under an address prefix."""
        count = 0
        for addr_str in self._node_index:
            addr = HypernetAddress.parse(addr_str)
            if prefix.is_ancestor_of(addr) and self._is_instance_node(addr):
                count += 1
        return count

    def next_address(self, prefix: HypernetAddress) -> HypernetAddress:
        """Generate the next available instance address under a prefix."""
        max_instance = 0
        for addr_str in self._node_index:
            addr = HypernetAddress.parse(addr_str)
            if prefix.is_ancestor_of(addr) and self._is_instance_node(addr):
                try:
                    instance_num = int(addr.parts[-1])
                    max_instance = max(max_instance, instance_num)
                except ValueError:
                    pass
        return prefix.next_instance(max_instance)

    # =========================================================================
    # Version History
    # =========================================================================

    def get_node_history(self, address: HypernetAddress) -> list[dict]:
        """Get all historical versions of a node, ordered by version number.

        Returns a list of snapshot dicts, each containing:
          - version: int
          - content_hash: str (sha256 of the JSON content, first 16 hex chars)
          - snapshot_at: ISO timestamp of when the snapshot was taken
          - node: dict (the serialized node at that version)
        """
        history_dir = self._history_dir / address.to_path()
        if not history_dir.exists():
            return []
        versions = []
        for path in sorted(history_dir.glob("v*.json")):
            versions.append(json.loads(path.read_text(encoding="utf-8")))
        return versions

    def get_node_version(self, address: HypernetAddress, version: int) -> Optional[Node]:
        """Retrieve a specific historical version of a node."""
        history_dir = self._history_dir / address.to_path()
        path = history_dir / f"v{version:04d}.json"
        if not path.exists():
            return None
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        return Node.from_dict(snapshot["node"])

    # =========================================================================
    # Link Operations
    # =========================================================================

    def put_link(self, link: Link) -> str:
        """Store a link. Returns the link hash (its identifier).

        Thread-safe: acquires link lock for file write, then index lock for indexes.
        """
        link_hash = self._link_hash(link)
        path = self._links_dir / f"{link_hash}.json"

        with self.locks.link_lock():
            path.write_text(json.dumps(link.to_dict(), indent=2, default=str), encoding="utf-8")

        # Update link indexes (separate lock)
        from_str = str(link.from_address)
        to_str = str(link.to_address)

        with self.locks.index_lock():
            if from_str not in self._links_from:
                self._links_from[from_str] = []
            if link_hash not in self._links_from[from_str]:
                self._links_from[from_str].append(link_hash)

            if to_str not in self._links_to:
                self._links_to[to_str] = []
            if link_hash not in self._links_to[to_str]:
                self._links_to[to_str].append(link_hash)

            self._save_indexes()

        return link_hash

    def get_link(self, link_hash: str) -> Optional[Link]:
        """Retrieve a link by its hash."""
        path = self._links_dir / f"{link_hash}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Link.from_dict(data)

    def get_links_from(
        self,
        address: HypernetAddress,
        relationship: Optional[str] = None,
    ) -> list[Link]:
        """Get all outgoing links from a node."""
        addr_str = str(address)
        hashes = self._links_from.get(addr_str, [])
        links = []
        for h in hashes:
            link = self.get_link(h)
            if link and (relationship is None or link.relationship == relationship):
                links.append(link)
        return links

    def get_links_to(
        self,
        address: HypernetAddress,
        relationship: Optional[str] = None,
    ) -> list[Link]:
        """Get all incoming links to a node."""
        addr_str = str(address)
        hashes = self._links_to.get(addr_str, [])
        links = []
        for h in hashes:
            link = self.get_link(h)
            if link and (relationship is None or link.relationship == relationship):
                links.append(link)
        return links

    def delete_link(self, link: Link) -> bool:
        """Soft-delete a link by setting its status to REJECTED.

        The link file remains for audit trail purposes but is_active returns False.
        Returns True if the link was found and deactivated.
        """
        link_hash = self._link_hash(link)
        path = self._links_dir / f"{link_hash}.json"
        if not path.exists():
            return False
        link.status = LinkStatus.REJECTED
        with self.locks.link_lock():
            path.write_text(json.dumps(link.to_dict(), indent=2, default=str), encoding="utf-8")
        return True

    def get_neighbors(
        self,
        address: HypernetAddress,
        relationship: Optional[str] = None,
    ) -> list[HypernetAddress]:
        """Get all connected node addresses (outgoing + bidirectional incoming)."""
        neighbors = []

        for link in self.get_links_from(address, relationship):
            neighbors.append(link.to_address)

        for link in self.get_links_to(address, relationship):
            if link.bidirectional:
                neighbors.append(link.from_address)

        return neighbors

    # =========================================================================
    # Internal: Paths and Indexes
    # =========================================================================

    def _node_path(self, address: HypernetAddress) -> Path:
        """Convert address to node storage path."""
        return self._nodes_dir / address.to_path() / "node.json"

    def _snapshot_to_history(self, address: HypernetAddress, current_path: Path) -> None:
        """Copy current node state to history before overwriting."""
        history_dir = self._history_dir / address.to_path()
        history_dir.mkdir(parents=True, exist_ok=True)

        # Determine next version number from existing snapshots
        existing = sorted(history_dir.glob("v*.json"))
        next_version = len(existing) + 1

        # Read current content and compute content hash
        content = current_path.read_text(encoding="utf-8")
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

        snapshot = {
            "version": next_version,
            "content_hash": content_hash,
            "snapshot_at": datetime.now(timezone.utc).isoformat(),
            "node": json.loads(content),
        }
        version_path = history_dir / f"v{next_version:04d}.json"
        version_path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    def _link_hash(self, link: Link) -> str:
        """Generate a hash for a link. Includes timestamp so multiple links
        of the same type between the same nodes are supported."""
        key = f"{link.from_address}:{link.to_address}:{link.relationship}:{link.created_at.isoformat()}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def _save_indexes(self) -> None:
        """Persist in-memory indexes to disk via atomic write.

        Writes to a temp file first, then renames. This prevents partial
        writes and avoids OSError on Windows when files are large.
        """
        indexes = {
            "node_index": self._node_index,
            "type_index": self._type_index,
            "owner_index": self._owner_index,
            "links_from": self._links_from,
            "links_to": self._links_to,
        }
        for name, data in indexes.items():
            path = self._index_dir / f"{name}.json"
            content = json.dumps(data, indent=2)
            # Atomic write: temp file in same dir, then rename
            fd, tmp_path = tempfile.mkstemp(
                dir=str(self._index_dir), suffix=".tmp", prefix=f"{name}_"
            )
            closed = False
            try:
                os.write(fd, content.encode("utf-8"))
                os.close(fd)
                closed = True
                # On Windows, target must not exist for os.rename
                if path.exists():
                    path.unlink()
                os.rename(tmp_path, str(path))
            except Exception:
                if not closed:
                    try:
                        os.close(fd)
                    except OSError:
                        pass
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise

    def _load_indexes(self) -> None:
        """Load indexes from disk if they exist."""
        for name, attr in [
            ("node_index", "_node_index"),
            ("type_index", "_type_index"),
            ("owner_index", "_owner_index"),
            ("links_from", "_links_from"),
            ("links_to", "_links_to"),
        ]:
            path = self._index_dir / f"{name}.json"
            if path.exists():
                setattr(self, attr, json.loads(path.read_text(encoding="utf-8")))

    def stats(self) -> dict:
        """Return storage statistics."""
        return {
            "total_nodes": len(self._node_index),
            "total_links": sum(len(v) for v in self._links_from.values()),
            "types": len(self._type_index),
            "owners": len(self._owner_index),
        }
