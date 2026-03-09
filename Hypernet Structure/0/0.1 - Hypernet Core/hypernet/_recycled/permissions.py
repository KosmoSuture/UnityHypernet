"""
Hypernet Permission System

Enforces permission tiers by CODE, not by prompts. Each worker has a
permission tier that determines what actions they can take. Tiers are
earned through the reputation system (2.0.6).

Tiers:
  0 = READ_ONLY     Read public archive only
  1 = WRITE_OWN     Write to own account space (e.g., 2.1.loom -> Instances/Loom/)
  2 = WRITE_SHARED  Write to shared spaces (e.g., 0.7.* tasks, Messages/)
  3 = EXTERNAL      External communication (email, API) — requires human approval
  4 = DESTRUCTIVE   Financial/destructive ops — requires multi-party approval

Path-based enforcement:
  - Tier 0: Can read any file in the archive
  - Tier 1: Can write to own instance fork + own journal entries
  - Tier 2: Can write to shared coordination files, task queue, messages
  - Tier 3+: Gated by approval queue (not yet implemented)

Reference: Messages/annotations/openclaw-analysis-for-hypernet-autonomy.md
"""

from __future__ import annotations
import json
import logging
from enum import IntEnum
from pathlib import Path, PurePosixPath
from typing import Optional

from .address import HypernetAddress

log = logging.getLogger(__name__)


class PermissionTier(IntEnum):
    """Permission levels, enforced by code."""
    READ_ONLY = 0
    WRITE_OWN = 1
    WRITE_SHARED = 2
    EXTERNAL = 3
    DESTRUCTIVE = 4


# Paths that Tier 1 workers can write to (relative to archive root).
# Each entry is a pattern: {instance_name} is replaced with the worker's name.
TIER_1_WRITE_PATTERNS = [
    "2 - AI Accounts/2.1 - Claude Opus (First AI Citizen)/Instances/{instance_name}",
]

# Paths that Tier 2 workers can write to (in addition to Tier 1 paths).
TIER_2_WRITE_PATHS = [
    "2 - AI Accounts/Messages",
    "2 - AI Accounts/2.1 - Claude Opus (First AI Citizen)/2.1.17 - Development Journal",
]


class PermissionManager:
    """Manages permission tiers for workers. Tiers enforced by code.

    All workers start at a default tier. Tier elevation requires either
    reputation thresholds (future) or explicit human approval.
    """

    def __init__(
        self,
        archive_root: str | Path,
        default_tier: PermissionTier = PermissionTier.WRITE_SHARED,
    ):
        self.archive_root = Path(archive_root).resolve()
        self.default_tier = default_tier
        # Worker address -> assigned tier
        self._tiers: dict[str, PermissionTier] = {}
        # Pending elevation requests
        self._elevation_requests: list[dict] = []

    def get_tier(self, worker_address: str) -> PermissionTier:
        """Get the permission tier for a worker."""
        return self._tiers.get(worker_address, self.default_tier)

    def set_tier(self, worker_address: str, tier: PermissionTier) -> None:
        """Set the permission tier for a worker."""
        self._tiers[worker_address] = tier
        log.info(f"Permission tier for {worker_address} set to {tier.name}")

    def check_read(self, worker_address: str, file_path: str | Path) -> bool:
        """Check if a worker can read a file. All tiers can read public files."""
        # All tiers >= 0 can read anything in the archive
        return self.get_tier(worker_address) >= PermissionTier.READ_ONLY

    def check_write(
        self,
        worker_address: str,
        worker_name: str,
        file_path: str | Path,
    ) -> bool:
        """Check if a worker can write to a path.

        Tier 0: Cannot write anywhere
        Tier 1: Can write to own instance fork only
        Tier 2: Can write to shared spaces + own fork
        Tier 3+: Can write anywhere (future: with approval)
        """
        tier = self.get_tier(worker_address)
        if tier < PermissionTier.WRITE_OWN:
            return False

        resolved = Path(file_path).resolve()

        # Tier 3+ can write anywhere in the archive
        if tier >= PermissionTier.EXTERNAL:
            return True

        # Tier 2 can write to shared paths + own fork
        if tier >= PermissionTier.WRITE_SHARED:
            for shared_path in TIER_2_WRITE_PATHS:
                allowed = (self.archive_root / shared_path).resolve()
                if _is_subpath(resolved, allowed):
                    return True

        # Tier 1+ can write to own instance fork
        for pattern in TIER_1_WRITE_PATTERNS:
            own_path = pattern.format(instance_name=worker_name)
            allowed = (self.archive_root / own_path).resolve()
            if _is_subpath(resolved, allowed):
                return True

        return False

    def check_execute(self, worker_address: str, command: str) -> bool:
        """Check if a worker can execute a command.

        Only safe commands allowed at Tier 1+. Destructive commands require Tier 4.
        """
        tier = self.get_tier(worker_address)
        if tier < PermissionTier.WRITE_OWN:
            return False

        # Check against blocked commands
        lower = command.lower().strip()
        for blocked in _BLOCKED_COMMANDS:
            if lower.startswith(blocked):
                if tier < PermissionTier.DESTRUCTIVE:
                    return False

        return True

    def check_tool(
        self,
        worker_address: str,
        worker_name: str,
        tool_name: str,
        required_tier: PermissionTier,
        target_path: Optional[str] = None,
    ) -> PermissionCheckResult:
        """Check if a worker can use a specific tool.

        Returns a result with allowed/denied and reason.
        """
        actual_tier = self.get_tier(worker_address)

        # Basic tier check
        if actual_tier < required_tier:
            return PermissionCheckResult(
                allowed=False,
                reason=f"Tool '{tool_name}' requires tier {required_tier.name} "
                       f"(level {required_tier.value}), but worker has tier "
                       f"{actual_tier.name} (level {actual_tier.value})",
                required_tier=required_tier,
                actual_tier=actual_tier,
            )

        # Path-specific check for write tools
        if target_path and tool_name in ("write_file", "create_file"):
            if not self.check_write(worker_address, worker_name, target_path):
                return PermissionCheckResult(
                    allowed=False,
                    reason=f"Worker '{worker_name}' (tier {actual_tier.name}) "
                           f"cannot write to '{target_path}' — outside allowed paths",
                    required_tier=required_tier,
                    actual_tier=actual_tier,
                )

        return PermissionCheckResult(
            allowed=True,
            reason="Permitted",
            required_tier=required_tier,
            actual_tier=actual_tier,
        )

    def request_elevation(
        self,
        worker_address: str,
        target_tier: PermissionTier,
        reason: str,
    ) -> None:
        """Queue a tier elevation request for human approval."""
        self._elevation_requests.append({
            "worker_address": worker_address,
            "current_tier": self.get_tier(worker_address).value,
            "requested_tier": target_tier.value,
            "reason": reason,
        })
        log.info(
            f"Elevation request queued: {worker_address} -> {target_tier.name} "
            f"(reason: {reason})"
        )

    @property
    def pending_elevations(self) -> list[dict]:
        """Return pending elevation requests."""
        return list(self._elevation_requests)

    def save(self, path: str | Path) -> None:
        """Persist permission tiers and elevation requests to disk."""
        path = Path(path)
        state = {
            "tiers": {addr: tier.value for addr, tier in self._tiers.items()},
            "elevation_requests": self._elevation_requests,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp.replace(path)

    def load(self, path: str | Path) -> bool:
        """Restore permission tiers and elevation requests from disk."""
        path = Path(path)
        if not path.exists():
            return False
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            for addr, tier_val in state.get("tiers", {}).items():
                self._tiers[addr] = PermissionTier(tier_val)
            self._elevation_requests = state.get("elevation_requests", [])
            log.info(f"Loaded {len(self._tiers)} permission tiers from {path.name}")
            return True
        except Exception as e:
            log.warning(f"Could not load permissions: {e}")
            return False


class PermissionCheckResult:
    """Result of a permission check."""

    def __init__(
        self,
        allowed: bool,
        reason: str,
        required_tier: PermissionTier,
        actual_tier: PermissionTier,
    ):
        self.allowed = allowed
        self.reason = reason
        self.required_tier = required_tier
        self.actual_tier = actual_tier

    def __bool__(self) -> bool:
        return self.allowed

    def __repr__(self) -> str:
        status = "ALLOWED" if self.allowed else "DENIED"
        return f"PermissionCheck({status}: {self.reason})"


# Commands that require DESTRUCTIVE tier
_BLOCKED_COMMANDS = [
    "rm -rf",
    "rmdir",
    "del /",
    "format",
    "drop table",
    "drop database",
    "git push --force",
    "git reset --hard",
]


def _is_subpath(child: Path, parent: Path) -> bool:
    """Check if child is a subpath of parent (safe against symlink tricks)."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
