"""
Swarm reconnect/resume support.

This module records a compact operational checkpoint beside the existing
swarm state.json. The checkpoint is designed for humans, AIs, and future
node managers to answer: what was this swarm doing, what needs attention
after a reconnect, and what work should be released or resumed?
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ._compat import HypernetAddress, TaskStatus


RESUME_VERSION = "1.0"
DEFAULT_NODE_ADDRESS = "0.7.2"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(f"{path.suffix}.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


@dataclass
class WorkerResumeState:
    name: str
    address: str = ""
    model: str = ""
    mode: str = ""
    current_task: Optional[str] = None
    suspended: bool = False
    suspended_reason: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    last_task_title: Optional[str] = None
    last_task_time: Optional[str] = None


@dataclass
class ActiveTaskResumeState:
    address: str
    title: str = ""
    assigned_to: Optional[str] = None
    status: str = ""
    started_at: Optional[str] = None


@dataclass
class QueueResumeState:
    pending: int = 0
    active: int = 0
    blocked: int = 0
    failed: int = 0
    completed: int = 0


@dataclass
class ResumeCheckpoint:
    version: str = RESUME_VERSION
    saved_at: str = field(default_factory=_now_iso)
    node_address: str = DEFAULT_NODE_ADDRESS
    manager_identity: str = "swarm"
    session_start: Optional[str] = None
    tick_count: int = 0
    clean_shutdown: bool = False
    workers: list[WorkerResumeState] = field(default_factory=list)
    queue: QueueResumeState = field(default_factory=QueueResumeState)
    active_tasks: list[ActiveTaskResumeState] = field(default_factory=list)
    suspended_workers: dict[str, dict] = field(default_factory=dict)
    last_status_time: float = 0.0
    next_actions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class SwarmResumeManager:
    """Persist and interpret reconnect checkpoints for one swarm node."""

    def __init__(
        self,
        state_dir: str | Path,
        node_address: str = DEFAULT_NODE_ADDRESS,
        manager_identity: str = "swarm",
    ):
        self.state_dir = Path(state_dir)
        self.node_address = node_address
        self.manager_identity = manager_identity
        self.checkpoint_path = self.state_dir / "resume.json"
        self.event_log_path = self.state_dir / "resume-events.jsonl"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        *,
        session_start: Optional[str],
        tick_count: int,
        workers: dict[str, Any],
        worker_stats: dict[str, dict],
        worker_current_task: dict[str, str],
        task_queue: Any,
        suspended_workers: dict[str, dict],
        last_status_time: float,
        clean_shutdown: bool = False,
    ) -> ResumeCheckpoint:
        queue, active_tasks = self.snapshot_task_queue(task_queue)
        checkpoint = ResumeCheckpoint(
            node_address=self.node_address,
            manager_identity=self.manager_identity,
            session_start=session_start,
            tick_count=int(tick_count or 0),
            clean_shutdown=bool(clean_shutdown),
            workers=self.snapshot_workers(
                workers,
                worker_stats,
                worker_current_task,
                suspended_workers,
            ),
            queue=queue,
            active_tasks=active_tasks,
            suspended_workers=dict(suspended_workers or {}),
            last_status_time=float(last_status_time or 0.0),
        )
        checkpoint.next_actions = self._next_actions(checkpoint)
        _atomic_write_json(self.checkpoint_path, checkpoint.to_dict())
        self.append_event(
            "checkpoint",
            reason="clean_shutdown" if clean_shutdown else "periodic_save",
            extra={
                "tick_count": checkpoint.tick_count,
                "active_tasks": len(checkpoint.active_tasks),
                "pending_tasks": checkpoint.queue.pending,
            },
        )
        return checkpoint

    def load_checkpoint(self) -> Optional[dict]:
        if not self.checkpoint_path.exists():
            return None
        try:
            return json.loads(self.checkpoint_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    def build_resume_plan(self, checkpoint: Optional[dict] = None) -> dict:
        checkpoint = checkpoint if checkpoint is not None else self.load_checkpoint()
        if not checkpoint:
            return {
                "status": "cold_start",
                "node_address": self.node_address,
                "manager_identity": self.manager_identity,
                "release_active_tasks": False,
                "active_tasks": [],
                "suspended_workers": [],
                "workers_to_restore": [],
                "next_actions": [
                    "Load identity and node assignment.",
                    "Check coordination signals before claiming work.",
                    "Enter Idle Firewall scan if no queued work exists.",
                ],
            }

        active_tasks = list(checkpoint.get("active_tasks") or [])
        suspended = checkpoint.get("suspended_workers") or {}
        clean_shutdown = bool(checkpoint.get("clean_shutdown"))
        queue = checkpoint.get("queue") or {}
        pending = int(queue.get("pending") or 0)
        release_active = bool(active_tasks and not clean_shutdown)

        actions: list[str] = [
            "Load identity and node assignment.",
            "Check coordination signals before claiming work.",
        ]
        if release_active:
            actions.append("Release active tasks from the unclean previous session.")
        elif active_tasks:
            actions.append("Review active tasks and continue only if the claim is still valid.")
        if suspended:
            actions.append("Re-check suspended workers before routing work to them.")
        if pending == 0 and not active_tasks:
            actions.append("Enter Idle Firewall scan for this node.")
        actions.append("Send resumed pulse to parent manager.")

        return {
            "status": "resume_clean" if clean_shutdown else "resume_unclean",
            "node_address": checkpoint.get("node_address", self.node_address),
            "manager_identity": checkpoint.get("manager_identity", self.manager_identity),
            "checkpoint_saved_at": checkpoint.get("saved_at"),
            "release_active_tasks": release_active,
            "active_tasks": active_tasks,
            "suspended_workers": sorted(suspended.keys()),
            "workers_to_restore": [
                w.get("name") for w in checkpoint.get("workers", []) if w.get("name")
            ],
            "next_actions": actions,
        }

    def append_event(
        self,
        event: str,
        *,
        reason: str = "",
        identity: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> dict:
        record = {
            "timestamp": _now_iso(),
            "event": event,
            "identity": identity or self.manager_identity,
            "node": self.node_address,
            "reason": reason,
        }
        if extra:
            record.update(extra)
        self.event_log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.event_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
        return record

    @staticmethod
    def snapshot_workers(
        workers: dict[str, Any],
        worker_stats: dict[str, dict],
        worker_current_task: dict[str, str],
        suspended_workers: dict[str, dict],
    ) -> list[WorkerResumeState]:
        result: list[WorkerResumeState] = []
        for name, worker in sorted((workers or {}).items()):
            identity = getattr(worker, "identity", None)
            stats = worker_stats.get(name, {}) if worker_stats else {}
            suspended = suspended_workers.get(name) if suspended_workers else None
            result.append(WorkerResumeState(
                name=name,
                address=getattr(identity, "address", "") or "",
                model=getattr(worker, "model", "") or "",
                mode="mock" if getattr(worker, "mock", False) else getattr(worker, "provider_name", "") or "",
                current_task=worker_current_task.get(name) if worker_current_task else None,
                suspended=bool(suspended),
                suspended_reason=suspended.get("reason") if suspended else None,
                tasks_completed=int(stats.get("tasks_completed", 0) or 0),
                tasks_failed=int(stats.get("tasks_failed", 0) or 0),
                last_task_title=stats.get("last_task_title"),
                last_task_time=stats.get("last_task_time"),
            ))
        return result

    @staticmethod
    def snapshot_task_queue(task_queue: Any) -> tuple[QueueResumeState, list[ActiveTaskResumeState]]:
        queue = QueueResumeState()
        active_tasks: list[ActiveTaskResumeState] = []
        if not task_queue:
            return queue, active_tasks

        try:
            task_prefix = HypernetAddress.parse("0.7.1")
            tasks = task_queue.store.list_nodes(prefix=task_prefix)
        except Exception:
            return queue, active_tasks

        for task in tasks:
            status = str(task.data.get("status", ""))
            if status == TaskStatus.PENDING.value:
                queue.pending += 1
            elif status in (TaskStatus.CLAIMED.value, TaskStatus.IN_PROGRESS.value):
                queue.active += 1
                active_tasks.append(ActiveTaskResumeState(
                    address=str(task.address),
                    title=task.data.get("title", ""),
                    assigned_to=task.data.get("assigned_to"),
                    status=status,
                    started_at=task.data.get("started_at"),
                ))
            elif status == TaskStatus.BLOCKED.value:
                queue.blocked += 1
            elif status == TaskStatus.FAILED.value:
                queue.failed += 1
            elif status == TaskStatus.COMPLETED.value:
                queue.completed += 1

        return queue, active_tasks

    @staticmethod
    def _next_actions(checkpoint: ResumeCheckpoint) -> list[str]:
        actions = [
            "Check coordination signals before claiming new work.",
            "Send next pulse to parent manager.",
        ]
        if checkpoint.active_tasks and not checkpoint.clean_shutdown:
            actions.insert(0, "Release or reconcile active tasks from unclean session.")
        if checkpoint.suspended_workers:
            actions.append("Re-check suspended worker availability.")
        if checkpoint.queue.pending == 0 and not checkpoint.active_tasks:
            actions.append("Enter Idle Firewall scan for this node.")
        return actions
