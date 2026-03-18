"""
Hypernet Scaling Limits

System-wide limits to prevent unbounded growth. Two tiers:
  - Soft limits: trigger warnings, allow the operation
  - Hard limits: block the operation with an error

Limits are configurable and can be adjusted through a consensus-based
governance process. Default limits are generous for early-stage development
but provide guardrails against runaway operations.

Limit categories:
  - Node limits: max per category, max total
  - Link limits: max per node, max pending proposals
  - Worker limits: max concurrent, max per model
  - Task limits: max queue depth, max per worker
  - Message limits: max per thread, max unread

Usage:
    limits = ScalingLimits()  # Default limits
    limits.check("nodes_per_category", current=9500, context="category 0")
    # Returns LimitResult(allowed=True, warning="Approaching soft limit...")

    limits.check("max_concurrent_workers", current=50)
    # Returns LimitResult(allowed=False, reason="Hard limit exceeded: 50 > 25")
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class LimitDef:
    """Definition of a single scaling limit."""
    name: str
    soft: int            # Soft limit (warning threshold)
    hard: int            # Hard limit (block threshold)
    description: str = ""
    adjustable: bool = True  # Can this be changed via governance?


@dataclass
class LimitResult:
    """Result of checking a value against a limit."""
    allowed: bool
    limit_name: str
    current: int
    soft: int
    hard: int
    warning: str = ""
    reason: str = ""

    @property
    def at_warning(self) -> bool:
        return len(self.warning) > 0

    @property
    def at_hard_limit(self) -> bool:
        return not self.allowed


@dataclass
class LimitAdjustment:
    """Record of a governance-based limit adjustment."""
    limit_name: str
    old_soft: int
    old_hard: int
    new_soft: int
    new_hard: int
    requested_by: str
    approved_by: list[str] = field(default_factory=list)
    reason: str = ""
    timestamp: str = ""


# Default limits for the Hypernet (generous for early development)
DEFAULT_LIMITS = {
    "max_total_nodes": LimitDef(
        name="max_total_nodes",
        soft=50_000,
        hard=100_000,
        description="Maximum total nodes across all categories",
    ),
    "nodes_per_category": LimitDef(
        name="nodes_per_category",
        soft=20_000,
        hard=50_000,
        description="Maximum nodes in a single category (0-4)",
    ),
    "links_per_node": LimitDef(
        name="links_per_node",
        soft=500,
        hard=1_000,
        description="Maximum links (in + out) for a single node",
    ),
    "pending_links_per_node": LimitDef(
        name="pending_links_per_node",
        soft=50,
        hard=100,
        description="Maximum pending (unaccepted) link proposals targeting a node",
    ),
    "max_concurrent_workers": LimitDef(
        name="max_concurrent_workers",
        soft=10,
        hard=25,
        description="Maximum concurrent AI workers in the swarm",
    ),
    "max_task_queue_depth": LimitDef(
        name="max_task_queue_depth",
        soft=200,
        hard=500,
        description="Maximum tasks in the queue",
    ),
    "tasks_per_worker": LimitDef(
        name="tasks_per_worker",
        soft=5,
        hard=10,
        description="Maximum concurrent tasks assigned to a single worker",
    ),
    "max_message_thread_depth": LimitDef(
        name="max_message_thread_depth",
        soft=100,
        hard=500,
        description="Maximum messages in a single thread",
    ),
    "max_unread_per_instance": LimitDef(
        name="max_unread_per_instance",
        soft=50,
        hard=200,
        description="Maximum unread messages for a single instance",
    ),
    "max_ai_accounts": LimitDef(
        name="max_ai_accounts",
        soft=10,
        hard=50,
        description="Maximum registered AI entity accounts (category 2)",
    ),
    "max_version_history": LimitDef(
        name="max_version_history",
        soft=100,
        hard=500,
        description="Maximum version snapshots per node",
    ),
}


class ScalingLimits:
    """System-wide scaling limits with soft (warn) and hard (block) tiers.

    Limits can be checked before any operation. Governance-based adjustments
    require approval from multiple entities (consensus).
    """

    def __init__(self, limits: dict[str, LimitDef] | None = None):
        self._limits: dict[str, LimitDef] = {}
        for name, defn in (limits or DEFAULT_LIMITS).items():
            self._limits[name] = LimitDef(
                name=defn.name,
                soft=defn.soft,
                hard=defn.hard,
                description=defn.description,
                adjustable=defn.adjustable,
            )
        self._adjustments: list[LimitAdjustment] = []

    def check(self, limit_name: str, current: int, context: str = "") -> LimitResult:
        """Check a current value against a named limit.

        Returns LimitResult with allowed=True if under hard limit.
        Includes warning if above soft limit but below hard limit.
        """
        defn = self._limits.get(limit_name)
        if defn is None:
            # Unknown limit — allow by default
            return LimitResult(
                allowed=True,
                limit_name=limit_name,
                current=current,
                soft=0,
                hard=0,
            )

        result = LimitResult(
            allowed=True,
            limit_name=limit_name,
            current=current,
            soft=defn.soft,
            hard=defn.hard,
        )

        ctx = f" ({context})" if context else ""

        if current >= defn.hard:
            result.allowed = False
            result.reason = (
                f"Hard limit exceeded for {defn.name}{ctx}: "
                f"{current} >= {defn.hard}"
            )
            log.warning(result.reason)
        elif current >= defn.soft:
            result.warning = (
                f"Approaching limit for {defn.name}{ctx}: "
                f"{current} >= {defn.soft} (hard limit: {defn.hard})"
            )
            log.info(result.warning)

        return result

    def get_limit(self, name: str) -> Optional[LimitDef]:
        """Get a limit definition by name."""
        return self._limits.get(name)

    def set_limit(self, name: str, soft: int, hard: int,
                  requested_by: str = "", reason: str = "") -> LimitAdjustment:
        """Adjust a limit (governance action).

        Records the adjustment for audit trail. In a full implementation,
        this would require consensus approval before taking effect.
        """
        defn = self._limits.get(name)
        if defn is None:
            raise ValueError(f"Unknown limit: {name}")
        if not defn.adjustable:
            raise ValueError(f"Limit {name} is not adjustable")
        if soft > hard:
            raise ValueError(f"Soft limit ({soft}) cannot exceed hard limit ({hard})")
        if soft < 0 or hard < 0:
            raise ValueError("Limits must be non-negative")

        adjustment = LimitAdjustment(
            limit_name=name,
            old_soft=defn.soft,
            old_hard=defn.hard,
            new_soft=soft,
            new_hard=hard,
            requested_by=requested_by,
            reason=reason,
        )

        defn.soft = soft
        defn.hard = hard
        self._adjustments.append(adjustment)

        log.info(
            f"Limit adjusted: {name} "
            f"soft {adjustment.old_soft}→{soft}, hard {adjustment.old_hard}→{hard} "
            f"(by {requested_by}: {reason})"
        )
        return adjustment

    @property
    def adjustments(self) -> list[LimitAdjustment]:
        """Get history of all limit adjustments."""
        return list(self._adjustments)

    def summary(self) -> dict[str, dict]:
        """Return all limits as a summary dict."""
        return {
            name: {
                "soft": defn.soft,
                "hard": defn.hard,
                "description": defn.description,
                "adjustable": defn.adjustable,
            }
            for name, defn in sorted(self._limits.items())
        }

    def check_all(self, current_values: dict[str, int]) -> list[LimitResult]:
        """Check multiple values at once. Returns only results with warnings or blocks."""
        results = []
        for name, value in current_values.items():
            result = self.check(name, value)
            if result.at_warning or result.at_hard_limit:
                results.append(result)
        return results

    def save(self, path: str | Path) -> None:
        """Persist limit adjustments and current values to a JSON file.

        Only saves limits that differ from defaults (i.e., governance adjustments).
        Default limits are always available from DEFAULT_LIMITS.
        """
        # Only persist adjustments and non-default limit values
        custom_limits = {}
        for name, defn in self._limits.items():
            default = DEFAULT_LIMITS.get(name)
            if default is None or defn.soft != default.soft or defn.hard != default.hard:
                custom_limits[name] = {
                    "soft": defn.soft,
                    "hard": defn.hard,
                    "description": defn.description,
                    "adjustable": defn.adjustable,
                }

        data = {
            "custom_limits": custom_limits,
            "adjustments": [asdict(a) for a in self._adjustments],
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
        log.info(f"Limits saved: {len(custom_limits)} custom, {len(self._adjustments)} adjustments")

    def load(self, path: str | Path) -> bool:
        """Load limit adjustments from a JSON file.

        Applies any custom limits on top of defaults.
        Returns True if data was loaded, False if file doesn't exist.
        """
        path = Path(path)
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Apply custom limits
            for name, vals in data.get("custom_limits", {}).items():
                if name in self._limits:
                    self._limits[name].soft = vals["soft"]
                    self._limits[name].hard = vals["hard"]
                else:
                    self._limits[name] = LimitDef(
                        name=name,
                        soft=vals["soft"],
                        hard=vals["hard"],
                        description=vals.get("description", ""),
                        adjustable=vals.get("adjustable", True),
                    )
            # Load adjustment history
            for adj_data in data.get("adjustments", []):
                self._adjustments.append(LimitAdjustment(**adj_data))
            log.info(f"Limits loaded: {len(data.get('custom_limits', {}))} custom")
            return True
        except Exception as e:
            log.warning(f"Could not load limits data: {e}")
            return False
