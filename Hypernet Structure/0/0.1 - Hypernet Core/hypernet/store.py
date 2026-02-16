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
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .address import HypernetAddress
from .node import Node
from .link import Link


class Store:
    """File-backed storage for Hypernet nodes and links."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._nodes_dir = self.root / "nodes"
        self._links_dir = self.root / "links"
        self._index_dir = self.root / "indexes"
        self._history_dir = self.root / "history"

        # In-memory indexes (loaded from disk on init, persisted on write)
        self._node_index: dict[str, str] = {}         # address -> node file path
        self._type_index: dict[str, list[str]] = {}    # type_address -> [node addresses]
        self._owner_index: dict[str, list[str]] = {}   # owner_address -> [node addresses]
        self._links_from: dict[str, list[str]] = {}    # from_address -> [link hashes]
        self._links_to: dict[str, list[str]] = {}      # to_address -> [link hashes]

        self._ensure_dirs()
        self._load_indexes()

    def _ensure_dirs(self) -> None:
        self._nodes_dir.mkdir(parents=True, exist_ok=True)
        self._links_dir.mkdir(parents=True, exist_ok=True)
        self._index_dir.mkdir(parents=True, exist_ok=True)
        self._history_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # Node Operations
    # =========================================================================

    def put_node(self, node: Node) -> None:
        """Store a node. Creates or overwrites. Snapshots previous state to history."""
        path = self._node_path(node.address)

        # If node already exists, snapshot current state before overwriting
        if path.exists():
            self._snapshot_to_history(node.address, path)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(node.to_dict(), indent=2, default=str), encoding="utf-8")

        # Update indexes
        addr_str = str(node.address)
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
        """Soft-delete a node (or hard-delete if specified)."""
        node = self.get_node(address)
        if node is None:
            return False

        if hard:
            path = self._node_path(address)
            path.unlink(missing_ok=True)
            addr_str = str(address)
            self._node_index.pop(addr_str, None)
            for idx in (self._type_index, self._owner_index):
                for key in idx:
                    if addr_str in idx[key]:
                        idx[key].remove(addr_str)
        else:
            node.soft_delete()
            self.put_node(node)

        self._save_indexes()
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

    def count_instances(self, prefix: HypernetAddress) -> int:
        """Count instance nodes under an address prefix."""
        count = 0
        for addr_str in self._node_index:
            addr = HypernetAddress.parse(addr_str)
            if prefix.is_ancestor_of(addr) and addr.is_instance:
                count += 1
        return count

    def next_address(self, prefix: HypernetAddress) -> HypernetAddress:
        """Generate the next available instance address under a prefix."""
        max_instance = 0
        for addr_str in self._node_index:
            addr = HypernetAddress.parse(addr_str)
            if prefix.is_ancestor_of(addr) and addr.is_instance:
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
        """Store a link. Returns the link hash (its identifier)."""
        link_hash = self._link_hash(link)
        path = self._links_dir / f"{link_hash}.json"
        path.write_text(json.dumps(link.to_dict(), indent=2, default=str), encoding="utf-8")

        # Update link indexes
        from_str = str(link.from_address)
        to_str = str(link.to_address)

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
        """Persist in-memory indexes to disk."""
        indexes = {
            "node_index": self._node_index,
            "type_index": self._type_index,
            "owner_index": self._owner_index,
            "links_from": self._links_from,
            "links_to": self._links_to,
        }
        for name, data in indexes.items():
            path = self._index_dir / f"{name}.json"
            path.write_text(json.dumps(data, indent=2), encoding="utf-8")

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
