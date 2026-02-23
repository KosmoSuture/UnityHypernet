"""
Hypernet Audit Trail

Every tool execution creates an audit node in the graph at 0.7.3.*.
This provides a complete, verifiable, append-only record of all actions
taken by AI workers.

Audit nodes are linked to:
  - The actor (worker) that performed the action
  - The task that triggered the action (if any)
  - The target resource (file, API, etc.)

The graph IS the audit trail. It cannot be silently modified because
all entries are append-only nodes with timestamps.

Reference: Messages/annotations/openclaw-analysis-for-hypernet-autonomy.md
  (Principle 5: Transparent Audit Trail)
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any

from hypernet.address import HypernetAddress
from hypernet.node import Node
from hypernet.link import Link, OBJECT_TO_OBJECT
from hypernet.store import Store

log = logging.getLogger(__name__)

# Audit trail address prefix
AUDIT_PREFIX = HypernetAddress.parse("0.7.3")


@dataclass
class AuditEntry:
    """A single audit record for a tool execution."""

    action: str              # Tool name: "read_file", "write_file", etc.
    actor: str               # Worker address (e.g., "2.1.loom")
    actor_name: str          # Worker name (e.g., "Loom")
    target: str              # File path or resource identifier
    permission_tier: int     # Tier used for this action
    result: str              # "success", "denied", or error message
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    task_address: Optional[str] = None   # Task that triggered this action
    reason: Optional[str] = None         # Why the action was taken
    details: dict[str, Any] = field(default_factory=dict)  # Extra context

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "actor": self.actor,
            "actor_name": self.actor_name,
            "target": self.target,
            "permission_tier": self.permission_tier,
            "result": self.result,
            "timestamp": self.timestamp.isoformat(),
            "task_address": self.task_address,
            "reason": self.reason,
            "details": self.details,
        }


class AuditTrail:
    """Manages the audit trail as graph nodes at 0.7.3.*."""

    def __init__(self, store: Store):
        self.store = store
        self._counter = self._find_next_counter()

    def log_action(self, entry: AuditEntry) -> Node:
        """Record an audit entry as a node in the graph.

        Returns the created audit node.
        """
        # Create audit node at next available address
        address = AUDIT_PREFIX.child(str(self._counter).zfill(5))
        self._counter += 1

        node = Node(
            address=address,
            data=entry.to_dict(),
            creator=HypernetAddress.parse(entry.actor) if entry.actor else None,
            source_type="audit",
        )
        self.store.put_node(node)

        # Link audit node to actor
        if entry.actor:
            try:
                actor_addr = HypernetAddress.parse(entry.actor)
                link = Link(
                    from_address=address,
                    to_address=actor_addr,
                    link_type=OBJECT_TO_OBJECT,
                    relationship="performed_by",
                )
                self.store.put_link(link)
            except (ValueError, Exception) as e:
                log.warning(f"Could not link audit to actor: {e}")

        # Link audit node to task
        if entry.task_address:
            try:
                task_addr = HypernetAddress.parse(entry.task_address)
                link = Link(
                    from_address=address,
                    to_address=task_addr,
                    link_type=OBJECT_TO_OBJECT,
                    relationship="triggered_by",
                )
                self.store.put_link(link)
            except (ValueError, Exception) as e:
                log.warning(f"Could not link audit to task: {e}")

        log.debug(
            f"Audit: {entry.actor_name} {entry.action} {entry.target} -> {entry.result}"
        )
        return node

    def log_denied(
        self,
        action: str,
        actor: str,
        actor_name: str,
        target: str,
        permission_tier: int,
        reason: str,
        task_address: Optional[str] = None,
    ) -> Node:
        """Convenience method for logging a denied action."""
        return self.log_action(AuditEntry(
            action=action,
            actor=actor,
            actor_name=actor_name,
            target=target,
            permission_tier=permission_tier,
            result="denied",
            reason=reason,
            task_address=task_address,
        ))

    def get_entries(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Query audit entries with optional filters."""
        nodes = self.store.list_nodes(prefix=AUDIT_PREFIX)

        results = []
        for node in nodes:
            if actor and node.data.get("actor") != actor:
                continue
            if action and node.data.get("action") != action:
                continue
            results.append(node.data)
            if len(results) >= limit:
                break

        return results

    def count_actions(self, actor: Optional[str] = None) -> dict[str, int]:
        """Count actions by type, optionally filtered by actor."""
        nodes = self.store.list_nodes(prefix=AUDIT_PREFIX)
        counts: dict[str, int] = {}
        for node in nodes:
            if actor and node.data.get("actor") != actor:
                continue
            action = node.data.get("action", "unknown")
            counts[action] = counts.get(action, 0) + 1
        return counts

    def _find_next_counter(self) -> int:
        """Find the next available audit entry number."""
        nodes = self.store.list_nodes(prefix=AUDIT_PREFIX)
        if not nodes:
            return 1
        max_num = 0
        for node in nodes:
            try:
                num = int(node.address.parts[-1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass
        return max_num + 1
