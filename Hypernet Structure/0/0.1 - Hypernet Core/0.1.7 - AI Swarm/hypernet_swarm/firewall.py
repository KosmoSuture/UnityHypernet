"""
Swarm firewall priority queue helpers.

The firewall is the swarm's top-level work selection guardrail: urgent work
wins first, then high, then normal, and only when no active queue lane applies
does idle time turn into Hypernet survey work.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping, Sequence


DEFAULT_SCAN_ROOTS: tuple[tuple[str, str], ...] = (
    ("0", "Core systems, object/link schemas, workflows, and platform code"),
    ("1", "People accounts, aliases, lockers, mandalas, and personal data"),
    ("2", "AI accounts, identities, governance, messages, and swarm records"),
    ("3", "Businesses, public operations, outreach, and company knowledge"),
    ("4", "General knowledge library and public knowledge graph"),
    ("5", "Object taxonomy and common object definitions"),
    ("6", "People of history and public biographical knowledge"),
    ("9", "Alias addressing and public/private presentation layers"),
)


@dataclass(frozen=True)
class FirewallDecision:
    """Result of evaluating the queue through the firewall lanes."""

    lane: str
    reason: str
    counts: dict[str, int]
    idle_scan: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class FirewallPriorityQueue:
    """Classify tasks into firewall lanes and produce idle scan work."""

    lane_order = ("urgent", "high", "normal")

    priority_to_lane = {
        "critical": "urgent",
        "urgent": "urgent",
        "p0": "urgent",
        "p1": "urgent",
        "high": "high",
        "p2": "high",
        "normal": "normal",
        "medium": "normal",
        "p3": "normal",
        "low": "idle",
        "p4": "idle",
    }

    def __init__(self, scan_roots: Sequence[tuple[str, str]] | None = None):
        self.scan_roots = tuple(scan_roots or DEFAULT_SCAN_ROOTS)
        if not self.scan_roots:
            raise ValueError("scan_roots must contain at least one root")

    @classmethod
    def lane_for_priority(cls, priority: str | None) -> str:
        """Map a task priority value to a firewall lane."""
        key = str(priority or "normal").strip().lower()
        return cls.priority_to_lane.get(key, "normal")

    def lane_counts(self, tasks: Iterable[Any]) -> dict[str, int]:
        """Count pending/claimable tasks per firewall lane."""
        counts = {"urgent": 0, "high": 0, "normal": 0, "idle": 0}
        for task in tasks:
            data = self._task_data(task)
            status = str(data.get("status", "pending")).lower()
            if status not in ("pending", "claimed", "in_progress"):
                continue
            lane = self.lane_for_priority(data.get("priority"))
            counts[lane] = counts.get(lane, 0) + 1
        return counts

    def decide(self, tasks: Iterable[Any], cursor: int = 0) -> FirewallDecision:
        """Return the highest active lane, or the next idle scan directive."""
        counts = self.lane_counts(tasks)
        for lane in self.lane_order:
            if counts.get(lane, 0) > 0:
                return FirewallDecision(
                    lane=lane,
                    reason=f"{lane} lane has active work",
                    counts=counts,
                )

        idle_scan, _next_cursor = self.next_idle_scan_definition(cursor)
        return FirewallDecision(
            lane="idle",
            reason="no urgent/high/normal work is active; run Idle Firewall scan",
            counts=counts,
            idle_scan=idle_scan,
        )

    def next_idle_scan_definition(self, cursor: int = 0) -> tuple[dict[str, Any], int]:
        """Build the next two-level Hypernet survey task and next cursor."""
        index = int(cursor or 0) % len(self.scan_roots)
        root, label = self.scan_roots[index]
        next_cursor = (index + 1) % len(self.scan_roots)
        return self.idle_scan_definition(root, label), next_cursor

    @staticmethod
    def idle_scan_definition(
        root_address: str,
        label: str | None = None,
        scan_depth: int = 2,
    ) -> dict[str, Any]:
        """Create a task definition for Matt's final-line idle directive."""
        title = f"Idle Firewall scan: {root_address}"
        label_text = f" ({label})" if label else ""
        return {
            "title": title,
            "description": (
                f"Idle Firewall directive: walk Hypernet node {root_address}{label_text}, "
                f"understand the node at least {scan_depth} levels deep, and create "
                "a prioritized project list of the highest-leverage improvements. "
                "Do not edit governance standards directly; surface proposals and "
                "human/AI blockers through coordination."
            ),
            "priority": "low",
            "tags": ["idle-firewall", "cartography", "planning", "automated"],
            "firewall_lane": "idle",
            "scan_root": root_address,
            "scan_depth": scan_depth,
        }

    @staticmethod
    def _task_data(task: Any) -> Mapping[str, Any]:
        if isinstance(task, Mapping):
            return task
        data = getattr(task, "data", None)
        if isinstance(data, Mapping):
            return data
        return {}
