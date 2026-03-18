"""
Hypernet Task Queue

A coordination layer for AI instances. Tasks are nodes in the Hypernet graph
(stored under 0.7.* per the addressing spec) with structured data for status,
assignment, and dependency tracking.

This is the foundation of the "AI army" architecture — a standard way for
AI instances to:
  - Discover available work
  - Claim tasks
  - Report progress
  - Hand off work
  - Chain dependent tasks

Tasks are just nodes with a specific data schema, linked to their assignee
and to other tasks via the standard link system.

Task lifecycle: pending -> claimed -> in_progress -> completed | failed
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from .address import HypernetAddress
from .node import Node
from .link import Link
from .store import Store


class TaskStatus(str, Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# Task type prefix in the addressing system
TASK_PREFIX = HypernetAddress.parse("0.7.1")


class TaskQueue:
    """Coordinate work between AI instances using the Hypernet graph."""

    def __init__(self, store: Store):
        self.store = store

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: TaskPriority = TaskPriority.NORMAL,
        created_by: Optional[HypernetAddress] = None,
        tags: Optional[list[str]] = None,
        depends_on: Optional[list[HypernetAddress]] = None,
    ) -> Node:
        """Create a new task in the queue."""
        address = self.store.next_address(TASK_PREFIX)

        task_data = {
            "title": title,
            "description": description,
            "status": TaskStatus.PENDING.value,
            "priority": priority.value,
            "created_by": str(created_by) if created_by else None,
            "assigned_to": None,
            "tags": tags or [],
            "progress": None,
            "result": None,
        }

        node = Node(
            address=address,
            type_address=TASK_PREFIX,
            data=task_data,
            source_type="task_queue",
        )
        self.store.put_node(node)

        # Link to creator
        if created_by:
            self.store.put_link(Link(
                from_address=created_by,
                to_address=address,
                link_type="0.6.2",
                relationship="created_task",
            ))

        # Create dependency links
        if depends_on:
            for dep_addr in depends_on:
                self.store.put_link(Link(
                    from_address=address,
                    to_address=dep_addr,
                    link_type="0.6.3",
                    relationship="depends_on",
                ))
            # Mark as blocked if dependencies exist
            node.data["status"] = TaskStatus.BLOCKED.value
            self.store.put_node(node)

        return node

    def claim_task(
        self,
        task_address: HypernetAddress,
        assignee: HypernetAddress,
    ) -> bool:
        """Claim a pending task for an AI instance. Returns True if successful."""
        node = self.store.get_node(task_address)
        if not node:
            return False

        status = node.data.get("status")
        if status not in (TaskStatus.PENDING.value, TaskStatus.BLOCKED.value):
            return False  # Already claimed or completed

        # Check if blocked by incomplete dependencies
        if status == TaskStatus.BLOCKED.value:
            deps = self.store.get_links_from(task_address, "depends_on")
            for dep_link in deps:
                dep_node = self.store.get_node(dep_link.to_address)
                if dep_node and dep_node.data.get("status") != TaskStatus.COMPLETED.value:
                    return False  # Still blocked

        node.data["status"] = TaskStatus.CLAIMED.value
        node.data["assigned_to"] = str(assignee)
        node.update_data()
        self.store.put_node(node)

        # Link assignee to task
        self.store.put_link(Link(
            from_address=assignee,
            to_address=task_address,
            link_type="0.6.2",
            relationship="assigned_to",
        ))

        return True

    def start_task(self, task_address: HypernetAddress) -> bool:
        """Mark a claimed task as in progress."""
        node = self.store.get_node(task_address)
        if not node or node.data.get("status") != TaskStatus.CLAIMED.value:
            return False

        node.data["status"] = TaskStatus.IN_PROGRESS.value
        node.data["started_at"] = datetime.now(timezone.utc).isoformat()
        node.update_data()
        self.store.put_node(node)
        return True

    def update_progress(
        self,
        task_address: HypernetAddress,
        progress: str,
    ) -> bool:
        """Update progress notes on an in-progress task."""
        node = self.store.get_node(task_address)
        if not node or node.data.get("status") != TaskStatus.IN_PROGRESS.value:
            return False

        node.data["progress"] = progress
        node.update_data()
        self.store.put_node(node)
        return True

    def complete_task(
        self,
        task_address: HypernetAddress,
        result: Optional[str] = None,
    ) -> bool:
        """Mark a task as completed, optionally with a result summary."""
        node = self.store.get_node(task_address)
        if not node or node.data.get("status") not in (
            TaskStatus.CLAIMED.value, TaskStatus.IN_PROGRESS.value
        ):
            return False

        node.data["status"] = TaskStatus.COMPLETED.value
        node.data["completed_at"] = datetime.now(timezone.utc).isoformat()
        if result:
            node.data["result"] = result
        node.update_data()
        self.store.put_node(node)

        # Unblock dependent tasks
        self._check_unblock_dependents(task_address)

        return True

    def fail_task(
        self,
        task_address: HypernetAddress,
        reason: str = "",
    ) -> bool:
        """Mark a task as failed."""
        node = self.store.get_node(task_address)
        if not node or node.data.get("status") not in (
            TaskStatus.CLAIMED.value, TaskStatus.IN_PROGRESS.value
        ):
            return False

        node.data["status"] = TaskStatus.FAILED.value
        node.data["failed_at"] = datetime.now(timezone.utc).isoformat()
        node.data["failure_reason"] = reason
        node.update_data()
        self.store.put_node(node)
        return True

    def release_task(self, task_address: HypernetAddress) -> bool:
        """Release a claimed/in-progress task back to pending.

        Used during graceful shutdown so tasks aren't left stuck.
        Clears assignment metadata so the task can be re-claimed.
        """
        node = self.store.get_node(task_address)
        if not node or node.data.get("status") not in (
            TaskStatus.CLAIMED.value, TaskStatus.IN_PROGRESS.value
        ):
            return False

        node.data["status"] = TaskStatus.PENDING.value
        node.data.pop("assigned_to", None)
        node.data.pop("started_at", None)
        node.data["released_at"] = datetime.now(timezone.utc).isoformat()
        node.update_data()
        self.store.put_node(node)
        return True

    def release_all_active(self) -> int:
        """Release all claimed/in-progress tasks back to pending.

        Called during shutdown or crash recovery. Returns count released.
        """
        all_tasks = self.store.list_nodes(prefix=TASK_PREFIX)
        released = 0
        for task in all_tasks:
            if task.data.get("status") in (
                TaskStatus.CLAIMED.value, TaskStatus.IN_PROGRESS.value
            ):
                if self.release_task(task.address):
                    released += 1
        return released

    def get_available_tasks(
        self,
        tags: Optional[list[str]] = None,
        priority: Optional[TaskPriority] = None,
    ) -> list[Node]:
        """Get all pending tasks that can be claimed."""
        all_tasks = self.store.list_nodes(prefix=TASK_PREFIX)
        available = []

        for task in all_tasks:
            if task.data.get("status") != TaskStatus.PENDING.value:
                continue
            if tags:
                task_tags = set(task.data.get("tags", []))
                if not task_tags.intersection(tags):
                    continue
            if priority and task.data.get("priority") != priority.value:
                continue
            available.append(task)

        # Sort by priority: critical > high > normal > low
        priority_order = {"critical": 0, "high": 1, "normal": 2, "low": 3}
        available.sort(key=lambda t: priority_order.get(t.data.get("priority", "normal"), 2))

        return available

    def get_tasks_for(self, assignee: HypernetAddress) -> list[Node]:
        """Get all tasks assigned to a specific AI instance."""
        all_tasks = self.store.list_nodes(prefix=TASK_PREFIX)
        return [
            t for t in all_tasks
            if t.data.get("assigned_to") == str(assignee)
            and t.data.get("status") in (TaskStatus.CLAIMED.value, TaskStatus.IN_PROGRESS.value)
        ]

    def _check_unblock_dependents(self, completed_address: HypernetAddress) -> None:
        """Check if completing this task unblocks any dependent tasks."""
        # Find tasks that depend on the completed task
        incoming = self.store.get_links_to(completed_address, "depends_on")
        for link in incoming:
            dependent = self.store.get_node(link.from_address)
            if not dependent or dependent.data.get("status") != TaskStatus.BLOCKED.value:
                continue

            # Check if all dependencies are now completed
            deps = self.store.get_links_from(link.from_address, "depends_on")
            all_done = all(
                self.store.get_node(d.to_address) is not None
                and self.store.get_node(d.to_address).data.get("status") == TaskStatus.COMPLETED.value
                for d in deps
            )

            if all_done:
                dependent.data["status"] = TaskStatus.PENDING.value
                dependent.update_data()
                self.store.put_node(dependent)
