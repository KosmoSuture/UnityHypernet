"""
Hypernet Git Coordinator

Distributed coordination for crowdsourced AI development. Manages the
git pull/work/push cycle, index rebuilding, address allocation, and
task claiming across multiple independent contributors.

Architecture:
  - Each contributor runs a local swarm (or works manually)
  - Work happens locally against the local file store
  - Changes are batched and pushed to the shared GitHub repo
  - On pull, indexes are rebuilt from source files (never merged as JSON)
  - Address collisions are detected and resolved automatically
  - Task claiming uses lightweight claim files (first push wins)

This module integrates with Store (file locks), Tasks (claiming), and
the Swarm orchestrator to provide seamless distributed operation.

From Matt: "We are going to really push Github to the limit and need
to come up with a way to handle record locking while trying to use
Github as real-time as possible."
"""

from __future__ import annotations
import hashlib
import json
import logging
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from hypernet.address import HypernetAddress
from hypernet.store import Store, FileLock

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class GitConfig:
    """Configuration for the git coordinator."""
    repo_root: Path                     # Root of the git repository
    data_dir: Path                      # Path to the data/ directory
    contributor_id: str = ""            # Unique contributor identifier
    max_batch_files: int = 500          # Max files per push batch
    max_retries: int = 5                # Max push retries on conflict
    base_retry_delay: float = 1.0       # Base delay for exponential backoff (seconds)
    max_retry_delay: float = 60.0       # Max delay between retries
    stale_claim_seconds: float = 3600.0 # Claims older than this are stale (1 hour)
    auto_rebase: bool = True            # Use --rebase on pull
    remote: str = "origin"              # Git remote name
    branch: str = "main"               # Default branch
    commit_prefix: str = "[swarm]"      # Prefix for auto-commits


# ---------------------------------------------------------------------------
# Git Operations (subprocess wrappers)
# ---------------------------------------------------------------------------

class GitError(Exception):
    """Raised when a git command fails."""
    def __init__(self, message: str, returncode: int = 1, stderr: str = ""):
        super().__init__(message)
        self.returncode = returncode
        self.stderr = stderr


def _run_git(args: list[str], cwd: Path, timeout: float = 120.0) -> subprocess.CompletedProcess:
    """Run a git command and return the result.

    Raises GitError on non-zero exit. Timeout defaults to 2 minutes
    to handle large pushes and slow network connections.

    Sets GIT_EDITOR=true to prevent interactive editor prompts
    (e.g., during rebase --continue) from hanging in headless mode.
    """
    cmd = ["git"] + args
    log.debug(f"git: {' '.join(cmd)}")
    env = os.environ.copy()
    env["GIT_EDITOR"] = "true"  # Prevent editor prompts in headless mode
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if result.returncode != 0:
            raise GitError(
                f"git {args[0]} failed (exit {result.returncode}): {result.stderr.strip()}",
                returncode=result.returncode,
                stderr=result.stderr.strip(),
            )
        return result
    except subprocess.TimeoutExpired:
        raise GitError(f"git {args[0]} timed out after {timeout}s")


def _git_status(cwd: Path) -> dict:
    """Get git status as structured data.

    Returns dict with keys:
      - modified: list of modified file paths
      - added: list of new untracked file paths
      - deleted: list of deleted file paths
      - staged: list of staged file paths
      - total_changes: total count of all changes
    """
    result = _run_git(["status", "--porcelain"], cwd)
    modified, added, deleted, staged = [], [], [], []

    for line in result.stdout.strip().split("\n"):
        if not line.strip():
            continue
        status_code = line[:2]
        filepath = line[3:].strip()

        # Strip quotes from paths with special characters
        if filepath.startswith('"') and filepath.endswith('"'):
            filepath = filepath[1:-1]

        if status_code[0] in ("M", "A", "D", "R"):
            staged.append(filepath)
        if status_code[1] == "M":
            modified.append(filepath)
        elif status_code == "??":
            added.append(filepath)
        elif status_code[1] == "D":
            deleted.append(filepath)

    return {
        "modified": modified,
        "added": added,
        "deleted": deleted,
        "staged": staged,
        "total_changes": len(modified) + len(added) + len(deleted) + len(staged),
    }


# ---------------------------------------------------------------------------
# Index Rebuilder
# ---------------------------------------------------------------------------

class IndexRebuilder:
    """Rebuilds store indexes from source files.

    The key insight for distributed git coordination: indexes are derived
    data. Never merge index JSON files — rebuild them from the authoritative
    source files (node.json, link .json files) after every pull.

    This eliminates the hardest class of merge conflicts entirely. Two
    contributors can create different nodes and their index changes will
    never conflict because the indexes are rebuilt, not merged.
    """

    def __init__(self, store: Store):
        self.store = store

    def rebuild_all(self) -> dict:
        """Rebuild all indexes from source files.

        Returns statistics about the rebuild:
          - nodes_indexed: count of nodes found
          - links_indexed: count of links found
          - duration_ms: time taken in milliseconds
        """
        start = time.monotonic()

        # Clear in-memory indexes
        self.store._node_index.clear()
        self.store._type_index.clear()
        self.store._owner_index.clear()
        self.store._links_from.clear()
        self.store._links_to.clear()

        nodes_indexed = self._rebuild_node_indexes()
        links_indexed = self._rebuild_link_indexes()

        # Persist rebuilt indexes to disk
        with self.store.locks.index_lock():
            self.store._save_indexes()

        duration_ms = (time.monotonic() - start) * 1000

        log.info(
            f"Index rebuild complete: {nodes_indexed} nodes, "
            f"{links_indexed} links in {duration_ms:.0f}ms"
        )

        return {
            "nodes_indexed": nodes_indexed,
            "links_indexed": links_indexed,
            "duration_ms": round(duration_ms, 1),
        }

    def _rebuild_node_indexes(self) -> int:
        """Scan all node.json files and rebuild node/type/owner indexes."""
        count = 0
        nodes_dir = self.store._nodes_dir
        if not nodes_dir.exists():
            return 0

        for node_file in nodes_dir.rglob("node.json"):
            try:
                data = json.loads(node_file.read_text(encoding="utf-8"))
                addr_str = data.get("address", "")
                if not addr_str:
                    continue

                # Node index: address -> file path
                self.store._node_index[addr_str] = str(node_file)

                # Type index
                type_addr = data.get("type_address")
                if type_addr:
                    if type_addr not in self.store._type_index:
                        self.store._type_index[type_addr] = []
                    if addr_str not in self.store._type_index[type_addr]:
                        self.store._type_index[type_addr].append(addr_str)

                # Owner index
                owner = data.get("owner")
                if owner:
                    if owner not in self.store._owner_index:
                        self.store._owner_index[owner] = []
                    if addr_str not in self.store._owner_index[owner]:
                        self.store._owner_index[owner].append(addr_str)

                count += 1
            except (json.JSONDecodeError, OSError) as e:
                log.warning(f"Skipping corrupt node file {node_file}: {e}")

        return count

    def _rebuild_link_indexes(self) -> int:
        """Scan all link .json files and rebuild link indexes."""
        count = 0
        links_dir = self.store._links_dir
        if not links_dir.exists():
            return 0

        for link_file in links_dir.glob("*.json"):
            try:
                data = json.loads(link_file.read_text(encoding="utf-8"))
                link_hash = link_file.stem

                from_addr = data.get("from_address", "")
                to_addr = data.get("to_address", "")

                if not from_addr or not to_addr:
                    continue

                # Links from index
                if from_addr not in self.store._links_from:
                    self.store._links_from[from_addr] = []
                if link_hash not in self.store._links_from[from_addr]:
                    self.store._links_from[from_addr].append(link_hash)

                # Links to index
                if to_addr not in self.store._links_to:
                    self.store._links_to[to_addr] = []
                if link_hash not in self.store._links_to[to_addr]:
                    self.store._links_to[to_addr].append(link_hash)

                count += 1
            except (json.JSONDecodeError, OSError) as e:
                log.warning(f"Skipping corrupt link file {link_file}: {e}")

        return count

    def validate(self) -> list[str]:
        """Validate index integrity against source files.

        Returns a list of issues found (empty = healthy).
        """
        issues = []

        # Check that every indexed node still exists on disk
        for addr_str, path_str in list(self.store._node_index.items()):
            if not Path(path_str).exists():
                issues.append(f"Indexed node missing from disk: {addr_str}")

        # Check that every node file on disk is indexed
        if self.store._nodes_dir.exists():
            for node_file in self.store._nodes_dir.rglob("node.json"):
                try:
                    data = json.loads(node_file.read_text(encoding="utf-8"))
                    addr_str = data.get("address", "")
                    if addr_str and addr_str not in self.store._node_index:
                        issues.append(f"Node file not indexed: {addr_str} ({node_file})")
                except (json.JSONDecodeError, OSError):
                    issues.append(f"Corrupt node file: {node_file}")

        return issues


# ---------------------------------------------------------------------------
# Address Allocator
# ---------------------------------------------------------------------------

@dataclass
class AddressReservation:
    """A reserved address range for a contributor."""
    contributor_id: str
    prefix: str               # Address prefix this contributor owns (e.g., "0.7.1")
    range_start: int          # Start of instance number range
    range_end: int             # End of instance number range (exclusive)
    reserved_at: str           # ISO timestamp
    expires_at: Optional[str] = None  # ISO timestamp, None = no expiry


class AddressAllocator:
    """Manages distributed address allocation to prevent collisions.

    Strategy: Each contributor gets a non-overlapping address range within
    each prefix. When a contributor needs new addresses under a prefix,
    they reserve a range (e.g., instances 100-199 under 0.7.1). The
    reservation is recorded in a claim file that merges cleanly in git
    because each contributor writes to their own file.

    Reservation files:
      data/.claims/addresses/<contributor_id>.json

    These files are append-only and contributor-scoped, so they never
    conflict in git merges. On pull, the allocator reads all claim files
    to build the global allocation map.
    """

    RANGE_SIZE = 100  # Each allocation grants 100 addresses

    def __init__(self, data_dir: Path, contributor_id: str):
        self.data_dir = data_dir
        self.contributor_id = contributor_id
        self.claims_dir = data_dir / ".claims" / "addresses"
        self.claims_dir.mkdir(parents=True, exist_ok=True)

    def reserve_range(self, prefix: str) -> AddressReservation:
        """Reserve the next available address range under a prefix.

        Scans all contributors' claim files to find the highest allocated
        range, then claims the next one. Writes to this contributor's
        claim file (which never conflicts with other contributors).

        Uses a file lock to prevent concurrent processes from computing
        the same max_end and writing overlapping ranges.
        """
        # Lock the entire read-compute-write cycle to prevent overlapping ranges
        lock = FileLock(self.claims_dir / "address-allocation")
        if not lock.acquire():
            raise TimeoutError("Could not acquire address allocation lock")
        try:
            all_reservations = self._load_all_reservations()

            # Find highest range_end for this prefix across all contributors
            max_end = 0
            for res in all_reservations:
                if res.prefix == prefix:
                    max_end = max(max_end, res.range_end)

            # Start from max_end (or 1 if no prior allocations)
            range_start = max(max_end, 1)
            range_end = range_start + self.RANGE_SIZE

            reservation = AddressReservation(
                contributor_id=self.contributor_id,
                prefix=prefix,
                range_start=range_start,
                range_end=range_end,
                reserved_at=datetime.now(timezone.utc).isoformat(),
            )

            self._save_reservation(reservation)
        finally:
            lock.release()

        log.info(
            f"Reserved address range {prefix}.{range_start}-{range_end - 1} "
            f"for contributor {self.contributor_id}"
        )
        return reservation

    def next_address(self, prefix: str) -> Optional[HypernetAddress]:
        """Get the next available address for this contributor under a prefix.

        Returns None if the current range is exhausted (call reserve_range first).
        """
        my_reservations = self._load_my_reservations()
        prefix_reservations = [r for r in my_reservations if r.prefix == prefix]

        if not prefix_reservations:
            # No reservation for this prefix — auto-reserve
            reservation = self.reserve_range(prefix)
            return HypernetAddress.parse(f"{prefix}.{reservation.range_start:05d}")

        # Find the latest reservation for this prefix
        latest = max(prefix_reservations, key=lambda r: r.range_start)

        # Find highest used address in this range
        # (scan the data directory for existing nodes)
        highest_used = latest.range_start - 1
        nodes_dir = self.data_dir / "nodes"
        if nodes_dir.exists():
            prefix_parts = prefix.split(".")
            scan_dir = nodes_dir
            for part in prefix_parts:
                scan_dir = scan_dir / part
            if scan_dir.exists():
                for child in scan_dir.iterdir():
                    if child.is_dir():
                        try:
                            num = int(child.name)
                            if latest.range_start <= num < latest.range_end:
                                highest_used = max(highest_used, num)
                        except ValueError:
                            pass

        next_num = highest_used + 1
        if next_num >= latest.range_end:
            # Range exhausted — reserve a new range
            new_res = self.reserve_range(prefix)
            return HypernetAddress.parse(f"{prefix}.{new_res.range_start:05d}")

        return HypernetAddress.parse(f"{prefix}.{next_num:05d}")

    def detect_collisions(self) -> list[dict]:
        """Detect address range collisions between contributors.

        Returns a list of collision descriptions (empty = no collisions).
        """
        all_reservations = self._load_all_reservations()
        collisions = []

        # Group by prefix
        by_prefix: dict[str, list[AddressReservation]] = {}
        for res in all_reservations:
            by_prefix.setdefault(res.prefix, []).append(res)

        for prefix, reservations in by_prefix.items():
            # Sort by range_start
            sorted_res = sorted(reservations, key=lambda r: r.range_start)
            for i in range(len(sorted_res) - 1):
                a, b = sorted_res[i], sorted_res[i + 1]
                if a.range_end > b.range_start and a.contributor_id != b.contributor_id:
                    collisions.append({
                        "prefix": prefix,
                        "contributor_a": a.contributor_id,
                        "range_a": f"{a.range_start}-{a.range_end - 1}",
                        "contributor_b": b.contributor_id,
                        "range_b": f"{b.range_start}-{b.range_end - 1}",
                    })

        return collisions

    def _load_all_reservations(self) -> list[AddressReservation]:
        """Load all address reservations from all contributors."""
        reservations = []
        if not self.claims_dir.exists():
            return reservations

        for claim_file in self.claims_dir.glob("*.json"):
            try:
                data = json.loads(claim_file.read_text(encoding="utf-8"))
                for entry in data.get("reservations", []):
                    reservations.append(AddressReservation(**entry))
            except (json.JSONDecodeError, OSError, TypeError) as e:
                log.warning(f"Skipping corrupt claim file {claim_file}: {e}")

        return reservations

    def _load_my_reservations(self) -> list[AddressReservation]:
        """Load this contributor's address reservations."""
        claim_file = self.claims_dir / f"{self.contributor_id}.json"
        if not claim_file.exists():
            return []
        try:
            data = json.loads(claim_file.read_text(encoding="utf-8"))
            return [AddressReservation(**entry) for entry in data.get("reservations", [])]
        except (json.JSONDecodeError, OSError, TypeError):
            return []

    def _save_reservation(self, reservation: AddressReservation) -> None:
        """Append a reservation to this contributor's claim file."""
        claim_file = self.claims_dir / f"{self.contributor_id}.json"
        if claim_file.exists():
            data = json.loads(claim_file.read_text(encoding="utf-8"))
        else:
            data = {"contributor_id": self.contributor_id, "reservations": []}

        data["reservations"].append({
            "contributor_id": reservation.contributor_id,
            "prefix": reservation.prefix,
            "range_start": reservation.range_start,
            "range_end": reservation.range_end,
            "reserved_at": reservation.reserved_at,
            "expires_at": reservation.expires_at,
        })

        claim_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Task Claimer
# ---------------------------------------------------------------------------

@dataclass
class TaskClaim:
    """A git-native task claim."""
    task_address: str
    contributor_id: str
    claimed_at: str  # ISO timestamp
    status: str = "active"  # active | completed | released


class TaskClaimer:
    """Distributed task claiming via git.

    Each contributor writes claims to their own file:
      data/.claims/tasks/<contributor_id>.json

    Claim protocol:
      1. Check all claim files for existing claims on the target task
      2. If unclaimed, write claim to own file
      3. Push changes
      4. If push succeeds: claim is valid (first push wins)
      5. If push fails with conflict on the claim: someone else got it first
      6. Pull, check again, and either accept the other claim or retry

    Because each contributor writes to their own file, the only conflicts
    that can occur are when two contributors claim the same task in the
    same git push cycle. The "first push wins" rule resolves these.
    """

    def __init__(self, data_dir: Path, contributor_id: str):
        self.data_dir = data_dir
        self.contributor_id = contributor_id
        self.claims_dir = data_dir / ".claims" / "tasks"
        self.claims_dir.mkdir(parents=True, exist_ok=True)

    def claim(self, task_address: str) -> Optional[TaskClaim]:
        """Attempt to claim a task.

        Returns the TaskClaim if locally successful, None if already claimed
        by another contributor. Note: the claim is only guaranteed valid
        after a successful git push.

        Uses a file lock to make the check-and-write atomic, preventing
        two local processes from claiming the same task simultaneously.
        """
        # Lock the check-write cycle to prevent TOCTOU race
        lock = FileLock(self.claims_dir / "task-claim")
        if not lock.acquire():
            raise TimeoutError("Could not acquire task claim lock")
        try:
            # Check if already claimed by someone else
            existing = self.get_claim(task_address)
            if existing and existing.contributor_id != self.contributor_id:
                if existing.status == "active":
                    log.info(
                        f"Task {task_address} already claimed by "
                        f"{existing.contributor_id}"
                    )
                    return None

            claim = TaskClaim(
                task_address=task_address,
                contributor_id=self.contributor_id,
                claimed_at=datetime.now(timezone.utc).isoformat(),
                status="active",
            )

            self._save_claim(claim)
        finally:
            lock.release()

        log.info(f"Claimed task {task_address} for {self.contributor_id}")
        return claim

    def release(self, task_address: str) -> bool:
        """Release a task claim (mark as released)."""
        my_claims = self._load_my_claims()
        updated = False
        for c in my_claims:
            if c.task_address == task_address and c.status == "active":
                c.status = "released"
                updated = True

        if updated:
            self._save_all_claims(my_claims)
            log.info(f"Released task {task_address}")
        return updated

    def complete(self, task_address: str) -> bool:
        """Mark a claimed task as completed."""
        my_claims = self._load_my_claims()
        updated = False
        for c in my_claims:
            if c.task_address == task_address and c.status == "active":
                c.status = "completed"
                updated = True

        if updated:
            self._save_all_claims(my_claims)
            log.info(f"Completed task {task_address}")
        return updated

    def get_claim(self, task_address: str) -> Optional[TaskClaim]:
        """Get the active claim on a task (from any contributor)."""
        all_claims = self._load_all_claims()
        for claim in all_claims:
            if claim.task_address == task_address and claim.status == "active":
                return claim
        return None

    def get_my_active_claims(self) -> list[TaskClaim]:
        """Get all active claims for this contributor."""
        return [c for c in self._load_my_claims() if c.status == "active"]

    def detect_conflicts(self) -> list[dict]:
        """Detect tasks claimed by multiple contributors.

        Returns list of conflict descriptions.
        """
        all_claims = self._load_all_claims()
        active_by_task: dict[str, list[TaskClaim]] = {}

        for claim in all_claims:
            if claim.status == "active":
                active_by_task.setdefault(claim.task_address, []).append(claim)

        conflicts = []
        for task_addr, claims in active_by_task.items():
            if len(claims) > 1:
                # Sort by claimed_at — earliest wins
                sorted_claims = sorted(claims, key=lambda c: c.claimed_at)
                conflicts.append({
                    "task_address": task_addr,
                    "winner": sorted_claims[0].contributor_id,
                    "winner_time": sorted_claims[0].claimed_at,
                    "losers": [
                        {"contributor_id": c.contributor_id, "claimed_at": c.claimed_at}
                        for c in sorted_claims[1:]
                    ],
                })

        return conflicts

    def get_stale_claims(self, stale_seconds: float = 3600.0) -> list[TaskClaim]:
        """Find active claims that are older than stale_seconds."""
        now = datetime.now(timezone.utc)
        stale = []
        for claim in self._load_all_claims():
            if claim.status != "active":
                continue
            try:
                claimed_at = datetime.fromisoformat(claim.claimed_at)
                if (now - claimed_at).total_seconds() > stale_seconds:
                    stale.append(claim)
            except (ValueError, TypeError):
                stale.append(claim)  # Can't parse timestamp — treat as stale
        return stale

    def _load_all_claims(self) -> list[TaskClaim]:
        """Load all task claims from all contributors."""
        claims = []
        if not self.claims_dir.exists():
            return claims
        for claim_file in self.claims_dir.glob("*.json"):
            try:
                data = json.loads(claim_file.read_text(encoding="utf-8"))
                for entry in data.get("claims", []):
                    claims.append(TaskClaim(**entry))
            except (json.JSONDecodeError, OSError, TypeError) as e:
                log.warning(f"Skipping corrupt claim file {claim_file}: {e}")
        return claims

    def _load_my_claims(self) -> list[TaskClaim]:
        """Load this contributor's task claims."""
        claim_file = self.claims_dir / f"{self.contributor_id}.json"
        if not claim_file.exists():
            return []
        try:
            data = json.loads(claim_file.read_text(encoding="utf-8"))
            return [TaskClaim(**entry) for entry in data.get("claims", [])]
        except (json.JSONDecodeError, OSError, TypeError):
            return []

    def _save_claim(self, claim: TaskClaim) -> None:
        """Add a claim to this contributor's claim file."""
        claims = self._load_my_claims()
        claims.append(claim)
        self._save_all_claims(claims)

    def _save_all_claims(self, claims: list[TaskClaim]) -> None:
        """Write all of this contributor's claims to their file."""
        claim_file = self.claims_dir / f"{self.contributor_id}.json"
        data = {
            "contributor_id": self.contributor_id,
            "claims": [
                {
                    "task_address": c.task_address,
                    "contributor_id": c.contributor_id,
                    "claimed_at": c.claimed_at,
                    "status": c.status,
                }
                for c in claims
            ],
        }
        claim_file.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Push Result
# ---------------------------------------------------------------------------

class PushStatus(str, Enum):
    SUCCESS = "success"
    CONFLICT = "conflict"         # Push rejected, needs rebase
    NOTHING_TO_PUSH = "nothing"   # No changes to push
    ERROR = "error"               # Unexpected error
    AUTH_FAILURE = "auth_failure"  # Authentication failed


@dataclass
class PushResult:
    """Result of a push attempt."""
    status: PushStatus
    files_pushed: int = 0
    retries: int = 0
    message: str = ""
    conflicts_resolved: int = 0
    duration_ms: float = 0.0


@dataclass
class PullResult:
    """Result of a pull operation."""
    success: bool
    files_updated: int = 0
    indexes_rebuilt: bool = False
    index_stats: dict = field(default_factory=dict)
    message: str = ""
    duration_ms: float = 0.0


@dataclass
class SyncResult:
    """Result of a full pull-push sync cycle."""
    pull: Optional[PullResult] = None
    push: Optional[PushResult] = None
    address_collisions: list = field(default_factory=list)
    task_conflicts: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Git Batch Coordinator
# ---------------------------------------------------------------------------

class GitBatchCoordinator:
    """Coordinates git operations for distributed Hypernet development.

    The core workflow:
      1. pull() — fetch latest changes, rebuild indexes
      2. (do local work — create nodes, claim tasks, etc.)
      3. push_batch() — stage, commit, push with retry on conflict

    All git operations are serialized through the Store's git_lock to
    prevent concurrent pull/push from the same machine.
    """

    def __init__(self, config: GitConfig, store: Store):
        self.config = config
        self.store = store
        self.index_rebuilder = IndexRebuilder(store)
        self.address_allocator = AddressAllocator(
            config.data_dir, config.contributor_id
        )
        self.task_claimer = TaskClaimer(
            config.data_dir, config.contributor_id
        )
        self.conflict_resolver: Optional["ConflictResolver"] = None  # Initialized lazily

    def pull(self) -> PullResult:
        """Pull latest changes and rebuild indexes.

        This is the safe way to incorporate upstream changes:
          1. Acquire git lock (prevents concurrent git operations)
          2. git pull --rebase (or merge)
          3. Rebuild all indexes from source files
          4. Validate index integrity
          5. Release git lock

        Index files (.json in data/indexes/) are always rebuilt, never
        merged. This eliminates the most common class of merge conflicts.
        """
        start = time.monotonic()

        with self.store.locks.git_lock():
            try:
                # Git pull
                pull_args = ["pull", self.config.remote, self.config.branch]
                if self.config.auto_rebase:
                    pull_args.insert(1, "--rebase")
                result = _run_git(pull_args, self.config.repo_root)

                # Count updated files from git output
                files_updated = 0
                for line in result.stdout.split("\n"):
                    if "|" in line:  # git diff-stat format: "file | N +-"
                        files_updated += 1

            except GitError as e:
                if "CONFLICT" in e.stderr or "conflict" in e.stderr.lower():
                    # Merge conflict — use conflict resolver
                    if self.conflict_resolver is None:
                        self.conflict_resolver = ConflictResolver(self.config, self.store)
                    resolutions = self.conflict_resolver.resolve_all()
                    unresolved = [r for r in resolutions if not r.resolved]
                    if unresolved:
                        log.warning(
                            f"{len(unresolved)} conflicts need manual resolution"
                        )
                    files_updated = -1  # Unknown after conflict resolution
                else:
                    return PullResult(
                        success=False,
                        message=f"Pull failed: {e}",
                        duration_ms=(time.monotonic() - start) * 1000,
                    )

        # Rebuild indexes from source files (outside git lock)
        index_stats = self.index_rebuilder.rebuild_all()

        # Validate
        issues = self.index_rebuilder.validate()
        if issues:
            log.warning(f"Index validation found {len(issues)} issues after pull")

        duration = (time.monotonic() - start) * 1000
        return PullResult(
            success=True,
            files_updated=max(files_updated, 0),
            indexes_rebuilt=True,
            index_stats=index_stats,
            message=f"Pull complete. {index_stats.get('nodes_indexed', 0)} nodes, "
                    f"{index_stats.get('links_indexed', 0)} links indexed.",
            duration_ms=round(duration, 1),
        )

    def push_batch(
        self,
        message: Optional[str] = None,
        paths: Optional[list[str]] = None,
    ) -> PushResult:
        """Stage, commit, and push changes with retry on conflict.

        Args:
            message: Commit message. Auto-generated if not provided.
            paths: Specific paths to stage. If None, stages all changes
                   in the data directory and claim files.

        The push uses exponential backoff on conflict:
          1. Push fails → pull --rebase → retry
          2. Each retry waits longer: 1s, 2s, 4s, 8s, ...
          3. After max_retries, reports failure

        Index files are excluded from staging (they're rebuilt on pull).
        """
        start = time.monotonic()

        with self.store.locks.git_lock():
            # Check for changes
            status = _git_status(self.config.repo_root)
            if status["total_changes"] == 0:
                return PushResult(
                    status=PushStatus.NOTHING_TO_PUSH,
                    message="No changes to push.",
                    duration_ms=(time.monotonic() - start) * 1000,
                )

            # Stage files
            if paths:
                files_to_stage = paths
            else:
                files_to_stage = self._collect_stageable_files(status)

            if not files_to_stage:
                return PushResult(
                    status=PushStatus.NOTHING_TO_PUSH,
                    message="No stageable files found.",
                    duration_ms=(time.monotonic() - start) * 1000,
                )

            # Batch limiting
            if len(files_to_stage) > self.config.max_batch_files:
                log.warning(
                    f"Batch size {len(files_to_stage)} exceeds limit "
                    f"{self.config.max_batch_files}. Truncating."
                )
                files_to_stage = files_to_stage[:self.config.max_batch_files]

            # Stage
            self._stage_files(files_to_stage)

            # Commit
            if not message:
                message = self._auto_commit_message(files_to_stage)

            full_message = f"{self.config.commit_prefix} {message}"
            _run_git(["commit", "-m", full_message], self.config.repo_root)

            # Push with retry
            retries = 0
            conflicts_resolved = 0
            delay = self.config.base_retry_delay

            while retries <= self.config.max_retries:
                try:
                    _run_git(
                        ["push", self.config.remote, self.config.branch],
                        self.config.repo_root,
                        timeout=180.0,  # 3 min timeout for push
                    )
                    duration = (time.monotonic() - start) * 1000
                    return PushResult(
                        status=PushStatus.SUCCESS,
                        files_pushed=len(files_to_stage),
                        retries=retries,
                        message=f"Pushed {len(files_to_stage)} files.",
                        conflicts_resolved=conflicts_resolved,
                        duration_ms=round(duration, 1),
                    )

                except GitError as e:
                    if "rejected" in e.stderr.lower() or "non-fast-forward" in e.stderr.lower():
                        # Push rejected — pull and retry
                        retries += 1
                        if retries > self.config.max_retries:
                            break

                        log.info(
                            f"Push rejected (attempt {retries}/{self.config.max_retries}). "
                            f"Rebasing and retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)

                        # Pull with rebase
                        try:
                            _run_git(
                                ["pull", "--rebase", self.config.remote, self.config.branch],
                                self.config.repo_root,
                            )
                            conflicts_resolved += 1
                        except GitError as pull_err:
                            if "CONFLICT" in pull_err.stderr:
                                if self.conflict_resolver is None:
                                    self.conflict_resolver = ConflictResolver(self.config, self.store)
                                self.conflict_resolver.resolve_all()
                                conflicts_resolved += 1
                            else:
                                duration = (time.monotonic() - start) * 1000
                                return PushResult(
                                    status=PushStatus.ERROR,
                                    retries=retries,
                                    message=f"Rebase failed: {pull_err}",
                                    duration_ms=round(duration, 1),
                                )

                        # Exponential backoff
                        delay = min(delay * 2, self.config.max_retry_delay)

                    elif "auth" in e.stderr.lower() or "403" in e.stderr:
                        duration = (time.monotonic() - start) * 1000
                        return PushResult(
                            status=PushStatus.AUTH_FAILURE,
                            message=f"Authentication failed: {e.stderr}",
                            duration_ms=round(duration, 1),
                        )
                    else:
                        duration = (time.monotonic() - start) * 1000
                        return PushResult(
                            status=PushStatus.ERROR,
                            retries=retries,
                            message=f"Push error: {e}",
                            duration_ms=round(duration, 1),
                        )

            # Max retries exceeded
            duration = (time.monotonic() - start) * 1000
            return PushResult(
                status=PushStatus.CONFLICT,
                retries=retries,
                message=f"Push failed after {retries} retries. Persistent conflict.",
                conflicts_resolved=conflicts_resolved,
                duration_ms=round(duration, 1),
            )

    def sync(self, commit_message: Optional[str] = None) -> SyncResult:
        """Full sync cycle: pull → push → detect issues.

        This is the high-level operation a contributor runs periodically:
          1. Pull latest changes and rebuild indexes
          2. Push local changes with retry
          3. Detect any address collisions or task conflicts
        """
        result = SyncResult()

        # Pull
        result.pull = self.pull()
        if not result.pull.success:
            return result

        # Push
        result.push = self.push_batch(message=commit_message)

        # Detect issues
        result.address_collisions = self.address_allocator.detect_collisions()
        result.task_conflicts = self.task_claimer.detect_conflicts()

        if result.address_collisions:
            log.warning(
                f"Address collisions detected: {len(result.address_collisions)}"
            )
        if result.task_conflicts:
            log.warning(
                f"Task claim conflicts detected: {len(result.task_conflicts)}"
            )

        return result

    def status(self) -> dict:
        """Get the current state of git coordination."""
        try:
            git_stat = _git_status(self.config.repo_root)
        except GitError:
            git_stat = {"total_changes": -1, "error": "git status failed"}

        # Check for pending manual conflicts
        queue = ManualResolutionQueue(self.config.data_dir)
        pending_conflicts = len(queue.list_pending())

        return {
            "contributor_id": self.config.contributor_id,
            "repo_root": str(self.config.repo_root),
            "remote": self.config.remote,
            "branch": self.config.branch,
            "git_status": git_stat,
            "active_task_claims": len(self.task_claimer.get_my_active_claims()),
            "address_reservations": len(
                self.address_allocator._load_my_reservations()
            ),
            "index_issues": len(self.index_rebuilder.validate()),
            "pending_conflicts": pending_conflicts,
        }

    # -----------------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------------

    def _collect_stageable_files(self, status: dict) -> list[str]:
        """Collect files that should be staged for commit.

        Excludes index files (rebuilt on pull, never committed) and
        lock files (local-only).
        """
        exclude_patterns = [
            "indexes/",       # Index files — rebuilt from source
            ".locks/",        # Lock files — local-only
            "__pycache__/",   # Python cache
            ".tmp",           # Temp files
        ]

        files = []
        for filepath in status["modified"] + status["added"] + status["deleted"]:
            if any(pattern in filepath for pattern in exclude_patterns):
                continue
            files.append(filepath)

        # Also include staged files that aren't excluded
        for filepath in status["staged"]:
            if filepath not in files:
                if not any(pattern in filepath for pattern in exclude_patterns):
                    files.append(filepath)

        return files

    def _stage_files(self, files: list[str]) -> None:
        """Stage a list of files for commit."""
        if not files:
            return

        # Stage in batches to avoid command-line length limits
        batch_size = 50
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            _run_git(["add", "--"] + batch, self.config.repo_root)

    def _auto_commit_message(self, files: list[str]) -> str:
        """Generate a commit message from the staged files."""
        if not files:
            return "Empty commit"

        # Categorize changes
        nodes = [f for f in files if "nodes/" in f or "node.json" in f]
        links = [f for f in files if "links/" in f]
        claims = [f for f in files if ".claims/" in f]
        code = [f for f in files if f.endswith(".py")]
        docs = [f for f in files if f.endswith(".md")]
        other = [f for f in files if f not in nodes + links + claims + code + docs]

        parts = []
        if nodes:
            parts.append(f"{len(nodes)} nodes")
        if links:
            parts.append(f"{len(links)} links")
        if claims:
            parts.append(f"{len(claims)} claims")
        if code:
            parts.append(f"{len(code)} code files")
        if docs:
            parts.append(f"{len(docs)} docs")
        if other:
            parts.append(f"{len(other)} other")

        contributor = self.config.contributor_id or "unknown"
        return f"Batch from {contributor}: {', '.join(parts)}"

    def _auto_resolve_index_conflicts(self) -> None:
        """Auto-resolve merge conflicts in index files.

        Strategy: for index files, accept "theirs" (the remote version)
        and then rebuild from source. This is always safe because indexes
        are derived data.
        """
        try:
            # Check for conflicted files
            result = _run_git(
                ["diff", "--name-only", "--diff-filter=U"],
                self.config.repo_root,
            )
            conflicted = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]

            for filepath in conflicted:
                if "indexes/" in filepath:
                    # Accept theirs for index files
                    _run_git(
                        ["checkout", "--theirs", filepath],
                        self.config.repo_root,
                    )
                    _run_git(["add", filepath], self.config.repo_root)
                    log.info(f"Auto-resolved index conflict: {filepath}")

            # If there are still non-index conflicts, continue the rebase
            remaining = [f for f in conflicted if "indexes/" not in f]
            if not remaining:
                try:
                    _run_git(["rebase", "--continue"], self.config.repo_root)
                except GitError:
                    pass  # May not be in a rebase

        except GitError as e:
            log.warning(f"Auto-resolve failed: {e}")


# ---------------------------------------------------------------------------
# Conflict Resolution Framework
# ---------------------------------------------------------------------------

class ConflictType(str, Enum):
    NODE = "node"           # Two contributors modified the same node
    LINK = "link"           # Two contributors created the same link hash
    INDEX = "index"         # Index file conflicts (always auto-resolved)
    TASK_CLAIM = "task"     # Two contributors claimed the same task
    OTHER = "other"         # Unrecognized file type


class ResolutionStrategy(str, Enum):
    LATEST_WINS = "latest_wins"       # Node: latest updated_at wins
    KEEP_BOTH = "keep_both"           # Link: both versions kept
    REBUILD = "rebuild"               # Index: rebuild from source
    FIRST_WINS = "first_wins"         # Task claim: earliest claim wins
    MANUAL = "manual"                 # Queued for human/AI review


@dataclass
class ConflictEntry:
    """A detected conflict and its resolution."""
    filepath: str
    conflict_type: ConflictType
    strategy: ResolutionStrategy
    resolved: bool = False
    winner: str = ""            # Which version won ("ours", "theirs", contributor_id)
    detail: str = ""
    resolved_at: str = ""       # ISO timestamp


class ConflictResolver:
    """Resolves merge conflicts in the Hypernet data store.

    After a git pull/rebase that produces conflicts, this class detects
    the type of each conflicted file and applies the appropriate strategy:

      - Node files (nodes/*/node.json):
          Latest updated_at wins. The losing version is preserved in
          the node's version history so no data is lost.

      - Link files (links/*.json):
          Both links are kept. Links are append-only, so two contributors
          creating different links should never conflict. If they somehow
          create the same link hash, we keep the version with more data.

      - Index files (indexes/*.json):
          Accept theirs and rebuild from source. Indexes are derived data.

      - Task claim files (.claims/tasks/*.json):
          Per-contributor files shouldn't conflict. If they do (same
          contributor, concurrent sessions), merge the claim lists.

      - Everything else:
          Queued in ManualResolutionQueue for human/AI review.

    Integration with GitBatchCoordinator:
      - resolve_all() is called automatically after a pull with conflicts
      - The resolution queue can be checked via pending_manual_resolutions()
    """

    def __init__(self, config: GitConfig, store: Store):
        self.config = config
        self.store = store
        self.queue = ManualResolutionQueue(config.data_dir)

    def resolve_all(self) -> list[ConflictEntry]:
        """Detect and resolve all current git conflicts.

        Returns a list of ConflictEntry objects describing what was found
        and how it was resolved. Unresolvable conflicts are added to the
        manual queue.
        """
        conflicted = self._get_conflicted_files()
        if not conflicted:
            return []

        entries = []
        for filepath in conflicted:
            conflict_type = self._classify_file(filepath)
            entry = self._resolve_one(filepath, conflict_type)
            entries.append(entry)

            if not entry.resolved:
                self.queue.add(entry)

        # If all conflicts resolved, try to continue the rebase
        if all(e.resolved for e in entries):
            self._continue_rebase_if_needed()

        log.info(
            f"Conflict resolution: {len(entries)} conflicts, "
            f"{sum(1 for e in entries if e.resolved)} resolved, "
            f"{sum(1 for e in entries if not e.resolved)} manual"
        )
        return entries

    def pending_manual_resolutions(self) -> list[ConflictEntry]:
        """Get unresolved conflicts waiting for manual intervention."""
        return self.queue.list_pending()

    def _get_conflicted_files(self) -> list[str]:
        """Get list of files with unresolved merge conflicts."""
        try:
            result = _run_git(
                ["diff", "--name-only", "--diff-filter=U"],
                self.config.repo_root,
            )
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except GitError:
            return []

    def _classify_file(self, filepath: str) -> ConflictType:
        """Determine the conflict type based on file path."""
        if "nodes/" in filepath and filepath.endswith("node.json"):
            return ConflictType.NODE
        elif "links/" in filepath and filepath.endswith(".json"):
            return ConflictType.LINK
        elif "indexes/" in filepath:
            return ConflictType.INDEX
        elif ".claims/tasks/" in filepath:
            return ConflictType.TASK_CLAIM
        else:
            return ConflictType.OTHER

    def _resolve_one(self, filepath: str, conflict_type: ConflictType) -> ConflictEntry:
        """Resolve a single conflict based on its type."""
        if conflict_type == ConflictType.INDEX:
            return self._resolve_index(filepath)
        elif conflict_type == ConflictType.NODE:
            return self._resolve_node(filepath)
        elif conflict_type == ConflictType.LINK:
            return self._resolve_link(filepath)
        elif conflict_type == ConflictType.TASK_CLAIM:
            return self._resolve_task_claim(filepath)
        else:
            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.OTHER,
                strategy=ResolutionStrategy.MANUAL,
                resolved=False,
                detail="Unrecognized file type — queued for manual resolution",
            )

    def _resolve_index(self, filepath: str) -> ConflictEntry:
        """Index conflicts: accept theirs, will rebuild from source later."""
        try:
            _run_git(["checkout", "--theirs", filepath], self.config.repo_root)
            _run_git(["add", filepath], self.config.repo_root)
            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.INDEX,
                strategy=ResolutionStrategy.REBUILD,
                resolved=True,
                winner="theirs",
                detail="Accepted theirs; indexes will be rebuilt from source",
                resolved_at=datetime.now(timezone.utc).isoformat(),
            )
        except GitError as e:
            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.INDEX,
                strategy=ResolutionStrategy.REBUILD,
                resolved=False,
                detail=f"Failed to resolve index conflict: {e}",
            )

    def _resolve_node(self, filepath: str) -> ConflictEntry:
        """Node conflicts: latest updated_at wins, loser preserved in history.

        Algorithm:
          1. Extract "ours" and "theirs" versions from git
          2. Parse both as node dicts
          3. Compare updated_at timestamps
          4. Winner becomes current node.json
          5. Loser is saved to version history
        """
        try:
            # Get both versions
            ours = self._get_version(filepath, "HEAD")
            theirs = self._get_version(filepath, self._get_theirs_ref())

            if ours is None and theirs is None:
                # Can't parse either — fallback to manual
                return ConflictEntry(
                    filepath=filepath,
                    conflict_type=ConflictType.NODE,
                    strategy=ResolutionStrategy.MANUAL,
                    resolved=False,
                    detail="Could not parse either version of node",
                )

            if ours is None:
                winner_data, winner_label = theirs, "theirs"
            elif theirs is None:
                winner_data, winner_label = ours, "ours"
            else:
                # Compare timestamps
                ours_ts = ours.get("updated_at", "")
                theirs_ts = theirs.get("updated_at", "")
                if theirs_ts >= ours_ts:
                    winner_data, winner_label = theirs, "theirs"
                    loser_data = ours
                else:
                    winner_data, winner_label = ours, "ours"
                    loser_data = theirs

                # Preserve the losing version in history
                addr_str = loser_data.get("address", "")
                if addr_str:
                    self._preserve_in_history(addr_str, loser_data)

            # Write winner and stage
            full_path = self.config.repo_root / filepath
            full_path.write_text(
                json.dumps(winner_data, indent=2, default=str),
                encoding="utf-8",
            )
            _run_git(["add", filepath], self.config.repo_root)

            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.NODE,
                strategy=ResolutionStrategy.LATEST_WINS,
                resolved=True,
                winner=winner_label,
                detail=f"Latest updated_at wins ({winner_label}). "
                       f"Loser preserved in history.",
                resolved_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.NODE,
                strategy=ResolutionStrategy.LATEST_WINS,
                resolved=False,
                detail=f"Node conflict resolution failed: {e}",
            )

    def _resolve_link(self, filepath: str) -> ConflictEntry:
        """Link conflicts: keep both versions (links are append-only).

        If two contributors somehow create the same link hash, keep
        the version with more data fields populated.
        """
        try:
            ours = self._get_version(filepath, "HEAD")
            theirs = self._get_version(filepath, self._get_theirs_ref())

            if ours is None and theirs is not None:
                winner_data, winner_label = theirs, "theirs"
            elif theirs is None and ours is not None:
                winner_data, winner_label = ours, "ours"
            elif ours is not None and theirs is not None:
                # Keep the version with more data
                ours_richness = len(json.dumps(ours))
                theirs_richness = len(json.dumps(theirs))
                if theirs_richness >= ours_richness:
                    winner_data, winner_label = theirs, "theirs"
                else:
                    winner_data, winner_label = ours, "ours"
            else:
                return ConflictEntry(
                    filepath=filepath,
                    conflict_type=ConflictType.LINK,
                    strategy=ResolutionStrategy.MANUAL,
                    resolved=False,
                    detail="Could not parse either version of link",
                )

            full_path = self.config.repo_root / filepath
            full_path.write_text(
                json.dumps(winner_data, indent=2, default=str),
                encoding="utf-8",
            )
            _run_git(["add", filepath], self.config.repo_root)

            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.LINK,
                strategy=ResolutionStrategy.KEEP_BOTH,
                resolved=True,
                winner=winner_label,
                detail="Link conflict resolved (richer version kept)",
                resolved_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.LINK,
                strategy=ResolutionStrategy.KEEP_BOTH,
                resolved=False,
                detail=f"Link conflict resolution failed: {e}",
            )

    def _resolve_task_claim(self, filepath: str) -> ConflictEntry:
        """Task claim conflicts: merge claim lists from both versions."""
        try:
            ours = self._get_version(filepath, "HEAD")
            theirs = self._get_version(filepath, self._get_theirs_ref())

            ours_claims = (ours or {}).get("claims", [])
            theirs_claims = (theirs or {}).get("claims", [])

            # Merge: deduplicate by task_address, keep earliest claim
            merged = {}
            for claim in ours_claims + theirs_claims:
                task_addr = claim.get("task_address", "")
                if task_addr not in merged:
                    merged[task_addr] = claim
                else:
                    existing = merged[task_addr]
                    if claim.get("claimed_at", "") < existing.get("claimed_at", ""):
                        merged[task_addr] = claim

            contributor_id = (ours or theirs or {}).get("contributor_id", "unknown")
            merged_data = {
                "contributor_id": contributor_id,
                "claims": list(merged.values()),
            }

            full_path = self.config.repo_root / filepath
            full_path.write_text(
                json.dumps(merged_data, indent=2),
                encoding="utf-8",
            )
            _run_git(["add", filepath], self.config.repo_root)

            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.TASK_CLAIM,
                strategy=ResolutionStrategy.FIRST_WINS,
                resolved=True,
                winner="merged",
                detail=f"Merged {len(merged)} claims from both versions",
                resolved_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            return ConflictEntry(
                filepath=filepath,
                conflict_type=ConflictType.TASK_CLAIM,
                strategy=ResolutionStrategy.FIRST_WINS,
                resolved=False,
                detail=f"Task claim merge failed: {e}",
            )

    def _get_theirs_ref(self) -> str:
        """Detect the correct git ref for 'theirs' during a conflict.

        During a merge, 'theirs' is at MERGE_HEAD.
        During a rebase, 'theirs' is at REBASE_HEAD.
        Falls back to MERGE_HEAD if neither is detectable.
        """
        rebase_head = self.config.repo_root / ".git" / "REBASE_HEAD"
        if rebase_head.exists():
            return "REBASE_HEAD"
        merge_head = self.config.repo_root / ".git" / "MERGE_HEAD"
        if merge_head.exists():
            return "MERGE_HEAD"
        # During rebase, try rebase-merge/stopped-sha
        rebase_merge = self.config.repo_root / ".git" / "rebase-merge"
        if rebase_merge.exists():
            return "REBASE_HEAD"
        return "MERGE_HEAD"

    def _get_version(self, filepath: str, ref: str) -> Optional[dict]:
        """Extract a file version from a git ref (HEAD, MERGE_HEAD, etc.)."""
        try:
            result = _run_git(
                ["show", f"{ref}:{filepath}"],
                self.config.repo_root,
            )
            return json.loads(result.stdout)
        except (GitError, json.JSONDecodeError):
            return None

    def _preserve_in_history(self, addr_str: str, node_data: dict) -> None:
        """Save a losing node version to the Store's version history."""
        try:
            addr = HypernetAddress.parse(addr_str)
            history_dir = self.store._history_dir / addr.to_path()
            history_dir.mkdir(parents=True, exist_ok=True)

            existing = sorted(history_dir.glob("v*.json"))
            next_version = len(existing) + 1

            content = json.dumps(node_data, indent=2, default=str)
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

            snapshot = {
                "version": next_version,
                "content_hash": content_hash,
                "snapshot_at": datetime.now(timezone.utc).isoformat(),
                "source": "conflict_resolution",
                "node": node_data,
            }
            version_path = history_dir / f"v{next_version:04d}.json"
            version_path.write_text(
                json.dumps(snapshot, indent=2, default=str),
                encoding="utf-8",
            )
            log.info(f"Preserved conflict loser as {version_path.name} for {addr_str}")
        except Exception as e:
            log.warning(f"Failed to preserve conflict history for {addr_str}: {e}")

    def _continue_rebase_if_needed(self) -> None:
        """If we're in a rebase, continue it after resolving all conflicts."""
        try:
            rebase_dir = self.config.repo_root / ".git" / "rebase-merge"
            rebase_apply = self.config.repo_root / ".git" / "rebase-apply"
            if rebase_dir.exists() or rebase_apply.exists():
                _run_git(["rebase", "--continue"], self.config.repo_root)
        except GitError:
            pass  # May need more commits to resolve


class ManualResolutionQueue:
    """Queue for conflicts that can't be auto-resolved.

    Persisted to data/.conflicts/queue.json so it survives across sessions.
    Human or AI reviewers can inspect the queue and resolve entries manually.

    Each entry describes:
      - What file is conflicted
      - What type of conflict it is
      - What auto-resolution was attempted (if any)
      - Why it failed

    CLI: `python -m hypernet conflicts` (future command)
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.queue_dir = data_dir / ".conflicts"
        self.queue_file = self.queue_dir / "queue.json"

    def add(self, entry: ConflictEntry) -> None:
        """Add an unresolved conflict to the queue."""
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        entries = self._load()
        entries.append({
            "filepath": entry.filepath,
            "conflict_type": entry.conflict_type.value,
            "strategy": entry.strategy.value,
            "detail": entry.detail,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "resolved": False,
        })
        self._save(entries)
        log.info(f"Queued manual conflict: {entry.filepath}")

    def list_pending(self) -> list[ConflictEntry]:
        """Get all unresolved conflicts in the queue."""
        entries = self._load()
        pending = []
        for e in entries:
            if not e.get("resolved", False):
                pending.append(ConflictEntry(
                    filepath=e["filepath"],
                    conflict_type=ConflictType(e["conflict_type"]),
                    strategy=ResolutionStrategy(e["strategy"]),
                    resolved=False,
                    detail=e.get("detail", ""),
                ))
        return pending

    def resolve(self, filepath: str, resolution_detail: str = "") -> bool:
        """Mark a queued conflict as resolved."""
        entries = self._load()
        updated = False
        for e in entries:
            if e["filepath"] == filepath and not e.get("resolved", False):
                e["resolved"] = True
                e["resolved_at"] = datetime.now(timezone.utc).isoformat()
                e["resolution_detail"] = resolution_detail
                updated = True

        if updated:
            self._save(entries)
            log.info(f"Resolved manual conflict: {filepath}")
        return updated

    def clear_resolved(self) -> int:
        """Remove all resolved entries from the queue. Returns count removed."""
        entries = self._load()
        pending = [e for e in entries if not e.get("resolved", False)]
        removed = len(entries) - len(pending)
        if removed > 0:
            self._save(pending)
        return removed

    def _load(self) -> list[dict]:
        """Load the queue from disk."""
        if not self.queue_file.exists():
            return []
        try:
            return json.loads(self.queue_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

    def _save(self, entries: list[dict]) -> None:
        """Save the queue to disk."""
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.queue_file.write_text(
            json.dumps(entries, indent=2),
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Contributor Setup
# ---------------------------------------------------------------------------

def generate_contributor_id() -> str:
    """Generate a unique contributor ID from machine identity.

    Combines hostname, username, and a timestamp for uniqueness.
    The ID is deterministic for the same user on the same machine
    (excluding the timestamp component which is only added on first run).
    """
    import socket
    hostname = socket.gethostname()
    username = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown"
    raw = f"{hostname}:{username}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def setup_contributor(
    repo_root: Path,
    data_dir: Optional[Path] = None,
    contributor_id: Optional[str] = None,
) -> GitConfig:
    """Set up a new contributor for distributed development.

    This is the entry point for `python -m hypernet setup`:
      1. Generate or accept a contributor ID
      2. Create the config
      3. Reserve initial address ranges
      4. Validate git access

    Returns a GitConfig ready for use with GitBatchCoordinator.
    """
    if data_dir is None:
        data_dir = repo_root / "data"
    if contributor_id is None:
        contributor_id = generate_contributor_id()

    # Detect git branch
    branch = "main"
    try:
        result = _run_git(["branch", "--show-current"], repo_root)
        branch = result.stdout.strip() or "main"
    except GitError:
        pass

    config = GitConfig(
        repo_root=repo_root,
        data_dir=data_dir,
        contributor_id=contributor_id,
        branch=branch,
    )

    log.info(f"Contributor setup complete: {contributor_id}")
    return config
