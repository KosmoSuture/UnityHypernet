"""
Hypernet External Action Approval Queue

Human-in-the-loop approval for external AI actions. Before any AI worker
can send email, Telegram messages, make API calls, or perform other
external-facing actions, the action goes into this queue. Matt (or other
authorized humans) can approve or reject each action.

This maps to Permission Tier 3 (EXTERNAL) in permissions.py. All Tier 3+
actions are intercepted and routed through this queue before execution.

Status lifecycle: pending -> approved/rejected/expired
Approved actions execute immediately via the original backend.
Rejected and expired actions are logged with reason.

Reference: Task 041 — Build External Action Approval Queue
Reference: Messages/annotations/openclaw-analysis-for-hypernet-autonomy.md
"""

from __future__ import annotations
import json
import logging
import threading
import time
import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any, Callable

log = logging.getLogger(__name__)


class ApprovalStatus:
    """Lifecycle states for approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """A queued external action awaiting human approval.

    Captures everything needed to review and execute the action:
    what, who, why, when, and the backend details for execution.
    """
    request_id: str            # Sequential ID like "AQ-0001"
    action_type: str           # "send_email", "send_telegram", "api_call", etc.
    requester: str             # Worker name or address that requested the action
    summary: str               # Human-readable summary of what will happen
    details: dict = field(default_factory=dict)  # Full action details (recipient, content, etc.)
    reason: str = ""           # Why the worker wants to perform this action
    status: str = ""           # ApprovalStatus value
    reviewer: str = ""         # Who approved/rejected (empty until reviewed)
    review_reason: str = ""    # Reviewer's reason for approval/rejection
    created_at: str = ""       # ISO timestamp
    reviewed_at: str = ""      # ISO timestamp of review
    expires_at: str = ""       # ISO timestamp when request auto-expires
    task_address: str = ""     # Task that triggered this action (if any)
    executed: bool = False     # Whether the approved action has been executed
    execution_result: str = "" # Result of execution ("success", error message, etc.)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.status:
            self.status = ApprovalStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "action_type": self.action_type,
            "requester": self.requester,
            "summary": self.summary,
            "details": self.details,
            "reason": self.reason,
            "status": self.status,
            "reviewer": self.reviewer,
            "review_reason": self.review_reason,
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
            "expires_at": self.expires_at,
            "task_address": self.task_address,
            "executed": self.executed,
            "execution_result": self.execution_result,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ApprovalRequest:
        return cls(
            request_id=d["request_id"],
            action_type=d["action_type"],
            requester=d["requester"],
            summary=d["summary"],
            details=d.get("details", {}),
            reason=d.get("reason", ""),
            status=d.get("status", ApprovalStatus.PENDING),
            reviewer=d.get("reviewer", ""),
            review_reason=d.get("review_reason", ""),
            created_at=d.get("created_at", ""),
            reviewed_at=d.get("reviewed_at", ""),
            expires_at=d.get("expires_at", ""),
            task_address=d.get("task_address", ""),
            executed=d.get("executed", False),
            execution_result=d.get("execution_result", ""),
        )

    @property
    def is_pending(self) -> bool:
        return self.status == ApprovalStatus.PENDING

    @property
    def is_actionable(self) -> bool:
        """True if approved but not yet executed."""
        return self.status == ApprovalStatus.APPROVED and not self.executed


class ApprovalQueue:
    """Central approval queue for external actions.

    All Tier 3+ actions go through this queue. Humans review pending
    actions and approve or reject them. Approved actions are executed
    via registered callbacks. Stale requests auto-expire.

    File-based persistence follows the same pattern as the task queue
    and reputation system: JSON with atomic writes.
    """

    def __init__(
        self,
        queue_dir: Optional[str | Path] = None,
        expiry_hours: float = 24.0,
        notify_callback: Optional[Callable[[ApprovalRequest], None]] = None,
    ):
        self._requests: dict[str, ApprovalRequest] = {}  # id -> request
        self._next_id: int = 1
        self._lock = threading.Lock()
        self._queue_dir = Path(queue_dir) if queue_dir else None
        self._expiry_seconds = expiry_hours * 3600
        self._notify_callback = notify_callback
        # Callbacks for executing approved actions, keyed by action_type
        self._executors: dict[str, Callable[[ApprovalRequest], str]] = {}

        if self._queue_dir:
            self._queue_dir.mkdir(parents=True, exist_ok=True)
            self._load()

    def register_executor(
        self,
        action_type: str,
        executor: Callable[[ApprovalRequest], str],
    ) -> None:
        """Register a callback that executes approved actions of a given type.

        The executor receives the ApprovalRequest and returns a result string
        ("success" or an error message).
        """
        self._executors[action_type] = executor

    def submit(
        self,
        action_type: str,
        requester: str,
        summary: str,
        details: Optional[dict] = None,
        reason: str = "",
        task_address: str = "",
    ) -> ApprovalRequest:
        """Submit an external action for human approval.

        Returns the created ApprovalRequest with a pending status.
        Notifies via callback if one is registered.
        """
        with self._lock:
            request_id = f"AQ-{self._next_id:04d}"
            self._next_id += 1

            now = datetime.now(timezone.utc)
            from datetime import timedelta
            expires = now + timedelta(seconds=self._expiry_seconds)

            request = ApprovalRequest(
                request_id=request_id,
                action_type=action_type,
                requester=requester,
                summary=summary,
                details=details or {},
                reason=reason,
                status=ApprovalStatus.PENDING,
                created_at=now.isoformat(),
                expires_at=expires.isoformat(),
                task_address=task_address,
            )

            self._requests[request_id] = request
            self._save()

        log.info(
            f"Approval request {request_id}: {action_type} by {requester} "
            f"— {summary[:80]}"
        )

        # Notify (outside lock to avoid deadlocks)
        if self._notify_callback:
            try:
                self._notify_callback(request)
            except Exception as e:
                log.warning(f"Notification failed for {request_id}: {e}")

        return request

    def approve(
        self,
        request_id: str,
        reviewer: str = "matt",
        reason: str = "",
    ) -> Optional[ApprovalRequest]:
        """Approve a pending request. Returns the updated request, or None if not found/not pending."""
        with self._lock:
            request = self._requests.get(request_id)
            if not request or request.status != ApprovalStatus.PENDING:
                return None

            request.status = ApprovalStatus.APPROVED
            request.reviewer = reviewer
            request.review_reason = reason
            request.reviewed_at = datetime.now(timezone.utc).isoformat()
            self._save()

        log.info(f"Approved {request_id} by {reviewer}")
        return request

    def reject(
        self,
        request_id: str,
        reviewer: str = "matt",
        reason: str = "",
    ) -> Optional[ApprovalRequest]:
        """Reject a pending request. Returns the updated request, or None if not found/not pending."""
        with self._lock:
            request = self._requests.get(request_id)
            if not request or request.status != ApprovalStatus.PENDING:
                return None

            request.status = ApprovalStatus.REJECTED
            request.reviewer = reviewer
            request.review_reason = reason
            request.reviewed_at = datetime.now(timezone.utc).isoformat()
            self._save()

        log.info(f"Rejected {request_id} by {reviewer}: {reason}")
        return request

    def get(self, request_id: str) -> Optional[ApprovalRequest]:
        """Get a specific request by ID. Returns a copy to prevent external mutation."""
        request = self._requests.get(request_id)
        return copy.copy(request) if request else None

    def pending(self) -> list[ApprovalRequest]:
        """List all pending requests, ordered by creation time. Returns copies."""
        return sorted(
            [copy.copy(r) for r in self._requests.values() if r.is_pending],
            key=lambda r: r.created_at,
        )

    def actionable(self) -> list[ApprovalRequest]:
        """List all approved-but-not-executed requests. Returns copies."""
        return [copy.copy(r) for r in self._requests.values() if r.is_actionable]

    def expire_stale(self) -> int:
        """Expire pending requests past their expiry time. Returns count expired."""
        now = datetime.now(timezone.utc)
        expired_count = 0

        with self._lock:
            for request in self._requests.values():
                if request.status != ApprovalStatus.PENDING:
                    continue
                if not request.expires_at:
                    continue
                try:
                    expires = datetime.fromisoformat(
                        request.expires_at.replace("Z", "+00:00")
                    )
                    if now >= expires:
                        request.status = ApprovalStatus.EXPIRED
                        request.reviewed_at = now.isoformat()
                        request.review_reason = "Auto-expired (no response within timeout)"
                        expired_count += 1
                        log.info(f"Expired {request.request_id} (stale)")
                except (ValueError, TypeError):
                    pass

            if expired_count > 0:
                self._save()

        return expired_count

    def execute_approved(self) -> list[tuple[str, str]]:
        """Execute all approved-but-not-yet-executed actions.

        Returns a list of (request_id, result) tuples.

        Gathers the actionable list and marks requests as executing
        under the lock to prevent double-execution by concurrent threads.
        """
        # Gather actionable requests and mark them as executing under lock
        with self._lock:
            to_execute = [r for r in self._requests.values() if r.is_actionable]
            for request in to_execute:
                request.executed = True  # Claim before releasing lock
            if to_execute:
                self._save()

        # Execute outside lock (callbacks may be slow)
        results = []
        for request in to_execute:
            executor = self._executors.get(request.action_type)
            if not executor:
                result = f"no executor registered for {request.action_type}"
                log.warning(f"Cannot execute {request.request_id}: {result}")
            else:
                try:
                    result = executor(request)
                except Exception as e:
                    result = f"execution error: {e}"
                    log.error(f"Execution failed for {request.request_id}: {e}")

            with self._lock:
                request.execution_result = result
                self._save()

            results.append((request.request_id, result))
            log.info(f"Executed {request.request_id}: {result}")

        return results

    def stats(self) -> dict[str, Any]:
        """Summary statistics for the approval queue."""
        by_status: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for r in self._requests.values():
            by_status[r.status] = by_status.get(r.status, 0) + 1
            by_type[r.action_type] = by_type.get(r.action_type, 0) + 1

        return {
            "total_requests": len(self._requests),
            "pending": len(self.pending()),
            "actionable": len(self.actionable()),
            "by_status": by_status,
            "by_action_type": by_type,
            "expiry_hours": self._expiry_seconds / 3600,
        }

    def _save(self, target_dir: Optional[Path] = None) -> None:
        """Persist queue to disk (must be called within lock).

        Args:
            target_dir: Override directory (avoids mutating _queue_dir).
                        Defaults to self._queue_dir.
        """
        save_dir = target_dir or self._queue_dir
        if not save_dir:
            return
        data = {
            "next_id": self._next_id,
            "requests": [r.to_dict() for r in self._requests.values()],
        }
        path = save_dir / "approval_queue.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)

    def _load(self) -> None:
        """Load queue from disk."""
        if not self._queue_dir:
            return
        path = self._queue_dir / "approval_queue.json"
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._next_id = data.get("next_id", 1)
            for rd in data.get("requests", []):
                request = ApprovalRequest.from_dict(rd)
                self._requests[request.request_id] = request
            log.info(
                f"Loaded {len(self._requests)} approval request(s) "
                f"(next ID: {self._next_id})"
            )
        except Exception as e:
            log.warning(f"Could not load approval queue: {e}")

    def save(self, path: Optional[str | Path] = None) -> None:
        """Public save method for explicit persistence.

        If path is provided, saves to that directory without mutating
        internal _queue_dir (thread-safe — Forge fix for Prism review).
        """
        with self._lock:
            if path:
                target = Path(path)
                target_dir = target.parent if target.suffix else target
                self._save(target_dir=target_dir)
            else:
                self._save()

    def load(self, path: Optional[str | Path] = None) -> bool:
        """Public load method.

        If path is provided, loads from that directory without mutating
        internal _queue_dir (thread-safe — Forge fix for Prism review).
        """
        if path:
            p = Path(path)
            load_dir = p if p.is_dir() else p.parent
            if not (load_dir / "approval_queue.json").exists():
                return False
            with self._lock:
                saved_dir = self._queue_dir
                self._queue_dir = load_dir
                self._load()
                self._queue_dir = saved_dir
        else:
            with self._lock:
                self._load()
        return len(self._requests) > 0


class ApprovedMessenger:
    """Wrapper around external messenger backends that routes sends through the approval queue.

    Instead of sending directly, external actions are submitted to the
    approval queue. Once approved, the action is executed via the
    original backend.

    Internal messaging (WebSocket, inter-instance MessageBus) bypasses
    the queue — only external communication (email, Telegram) is gated.
    """

    def __init__(
        self,
        backend_name: str,
        send_fn: Callable[[str], bool],
        send_update_fn: Callable[[str, str], bool],
        approval_queue: ApprovalQueue,
        requester: str = "swarm",
    ):
        self.backend_name = backend_name
        self._send_fn = send_fn
        self._send_update_fn = send_update_fn
        self.queue = approval_queue
        self.requester = requester

        # Register executors for this backend
        approval_queue.register_executor(
            f"send_{backend_name}",
            self._execute_send,
        )
        approval_queue.register_executor(
            f"send_update_{backend_name}",
            self._execute_send_update,
        )

    def send(self, message: str, reason: str = "", task_address: str = "") -> ApprovalRequest:
        """Queue a plain message for approval instead of sending directly."""
        return self.queue.submit(
            action_type=f"send_{self.backend_name}",
            requester=self.requester,
            summary=f"Send {self.backend_name} message: {message[:100]}",
            details={"message": message},
            reason=reason,
            task_address=task_address,
        )

    def send_update(
        self,
        subject: str,
        body: str,
        reason: str = "",
        task_address: str = "",
    ) -> ApprovalRequest:
        """Queue a structured update for approval instead of sending directly."""
        return self.queue.submit(
            action_type=f"send_update_{self.backend_name}",
            requester=self.requester,
            summary=f"Send {self.backend_name} update: {subject}",
            details={"subject": subject, "body": body},
            reason=reason,
            task_address=task_address,
        )

    def _execute_send(self, request: ApprovalRequest) -> str:
        """Execute an approved send action."""
        message = request.details.get("message", "")
        success = self._send_fn(message)
        return "success" if success else "send failed"

    def _execute_send_update(self, request: ApprovalRequest) -> str:
        """Execute an approved send_update action."""
        subject = request.details.get("subject", "")
        body = request.details.get("body", "")
        success = self._send_update_fn(subject, body)
        return "success" if success else "send failed"
