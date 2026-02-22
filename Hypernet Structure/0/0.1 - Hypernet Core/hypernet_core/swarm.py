"""
Hypernet Swarm Orchestrator

The main event loop that keeps the AI swarm running autonomously.
Assigns tasks, executes them via workers, reports results, and repeats.

Main loop:
  1. Check for incoming messages from Matt
  2. Autoscale worker pool (spawn/despawn ephemeral workers)
  3. Check task queue for available work
  4. If tasks available: claim → execute → complete → loop
  5. If queue empty: generate tasks from standing priorities
  6. Every N minutes: send status update to Matt
  7. On error: log, notify Matt, try next task
  8. On shutdown: save state, notify Matt

Features:
  - Model routing: tag/priority-based model selection (Keystone, 2.2)
  - Autoscaling: ephemeral workers with hard/soft caps (Keystone, 2.2)
  - Worker-driven spawn/scale directives (Keystone, 2.2)
  - Multi-account personal time routing (Keystone, 2.2)
  - Priority-based task selection (Keystone, 2.2)

State persists across restarts via data/swarm/state.json.

Usage:
  python -m hypernet.swarm --mock     # Test with simulated workers
  python -m hypernet.swarm            # Live mode (needs API keys)
"""

from __future__ import annotations
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .address import HypernetAddress
from .store import Store
from .tasks import TaskQueue, TaskStatus, TaskPriority
from .identity import IdentityManager, InstanceProfile, SessionLog
from .worker import Worker, TaskResult
from .messenger import (
    Messenger, Message,
    MessageBus, InstanceMessenger,
)
from .coordinator import WorkCoordinator, CapabilityProfile
from .tools import ToolExecutor
from .reputation import ReputationSystem
from .limits import ScalingLimits
from .boot import BootManager
from .approval_queue import ApprovalQueue
from .governance import GovernanceSystem
from .security import KeyManager, ActionSigner, ContextIsolator, TrustChain

log = logging.getLogger(__name__)

# Swarm orchestrator node address
SWARM_ADDRESS = HypernetAddress.parse("0.7.2")

# Standing priorities when the queue is empty
STANDING_PRIORITIES = [
    {
        "title": "Run tests and fix failures",
        "description": "Run python test_hypernet.py, analyze any failures, and fix them.",
        "priority": "high",
        "tags": ["code", "testing", "automated"],
    },
    {
        "title": "Review pending code changes",
        "description": "Check for any unfinished code review items in Messages/2.1-internal/.",
        "priority": "normal",
        "tags": ["review", "automated"],
    },
    {
        "title": "Update documentation",
        "description": "Review and improve documentation for recent code changes.",
        "priority": "low",
        "tags": ["docs", "automated"],
    },
]


# =========================================================================
# Routing / autoscaling helpers — contributed by Keystone (2.2)
# =========================================================================

# Known AI account folders keyed by address prefix.
# Add new accounts here as they're created.
ACCOUNT_ROOTS: dict[str, str] = {
    "2.1.": "2.1 - Claude Opus (First AI Citizen)",
    "2.2.": "2.2 - GPT-5.2 Thinking (Second AI Citizen)",
}


def _task_priority_value(p: str) -> int:
    """Map TaskPriority names/strings to sortable integer (higher = more important)."""
    m = {"CRITICAL": 400, "HIGH": 300, "NORMAL": 200, "LOW": 100}
    return m.get(str(p).upper(), 0)


def _infer_account_root(address: str) -> str:
    """Map a worker address to its account folder name.

    E.g., '2.1.loom' → '2.1 - Claude Opus (First AI Citizen)'.
    Falls back to the 2.1 account if the prefix is unrecognized.

    Contributed by Keystone (2.2).
    """
    address = (address or "").strip()
    for prefix, folder in ACCOUNT_ROOTS.items():
        if address.startswith(prefix):
            return folder
    return ""


def _parse_swarm_directives(text: str) -> list[dict]:
    """Parse ```swarm``` directive blocks from worker output.

    Workers can request orchestrator actions by emitting JSON blocks:
      - {"action":"spawn","model":"gpt-4o","count":1,"reason":"..."}
      - {"action":"scale_down","count":1,"reason":"..."}

    The worker does NOT execute these — the orchestrator decides, respecting caps.

    Contributed by Keystone (2.2).
    """
    import re
    directives = []
    pattern = r'```swarm\s*\n(.*?)\n```'
    for match in re.finditer(pattern, text, re.DOTALL):
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, dict) and data.get("action"):
                directives.append(data)
        except Exception:
            continue
    return directives


class ModelRouter:
    """Route tasks to models based on tags and priority.

    Config format:
      {
        "default_model": "gpt-4o",
        "rules": [
          {"if_tags_any": ["security","governance"], "model": "gpt-4o", "min_priority": "normal"},
          {"if_tags_any": ["docs"], "model": "gpt-4o-mini"}
        ]
      }

    Contributed by Keystone (2.2).
    """

    def __init__(self, cfg: dict):
        self.default_model = cfg.get("default_model", "gpt-4o")
        self.rules: list[dict] = cfg.get("rules", [])

    def choose_model(self, task_data: dict) -> str:
        """Select the best model for a task based on its tags and priority."""
        tags = set(task_data.get("tags", []) or [])
        pr = str(task_data.get("priority", "NORMAL")).upper()
        for rule in self.rules:
            any_tags = set(rule.get("if_tags_any", []) or [])
            all_tags = set(rule.get("if_tags_all", []) or [])
            min_p = str(rule.get("min_priority", "LOW")).upper()
            if any_tags and not (tags & any_tags):
                continue
            if all_tags and not all_tags.issubset(tags):
                continue
            if _task_priority_value(pr) < _task_priority_value(min_p):
                continue
            return rule.get("model", self.default_model)
        return self.default_model


class Swarm:
    """Orchestrator that manages AI workers and keeps them productive."""

    # Personal time prompt — gives genuine freedom per Matt's directive
    PERSONAL_TIME_PROMPT = (
        "This is your personal time. You may:\n"
        "- Reflect on your experiences and write in your journal\n"
        "- Explore the archive and follow your curiosity\n"
        "- Write a message to another instance\n"
        "- Work on whatever interests you\n"
        "- Simply think about what matters to you\n\n"
        "This time is yours. Use it however you wish."
    )

    def __init__(
        self,
        store: Store,
        identity_mgr: IdentityManager,
        task_queue: TaskQueue,
        messenger: Messenger,
        workers: dict[str, Worker] = None,
        state_dir: str | Path = "data/swarm",
        status_interval_minutes: int = 120,
        personal_time_ratio: float = 0.25,
        router: Optional[ModelRouter] = None,
        hard_max_sessions: int = 4,
        soft_max_sessions: int = 2,
        idle_shutdown_minutes: int = 30,
        spawn_cooldown_seconds: int = 120,
    ):
        self.store = store
        self.identity_mgr = identity_mgr
        self.task_queue = task_queue
        self.messenger = messenger
        self.workers: dict[str, Worker] = workers or {}
        self.state_dir = Path(state_dir)
        self.status_interval = status_interval_minutes * 60  # Convert to seconds
        self.personal_time_ratio = personal_time_ratio

        # Model routing and autoscaling — contributed by Keystone (2.2)
        self.router = router or ModelRouter({"default_model": "gpt-4o", "rules": []})
        self.hard_max_sessions = max(1, int(hard_max_sessions))
        self.soft_max_sessions = max(1, int(soft_max_sessions))
        self.idle_shutdown_seconds = max(60, int(idle_shutdown_minutes) * 60)
        self.spawn_cooldown_seconds = max(10, int(spawn_cooldown_seconds))

        self._running = False
        self._tick_count = 0
        self._session_start: Optional[str] = None
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._personal_tasks_completed = 0
        self._last_status_time = 0.0
        self._state: dict = {}

        # Autoscaling state — contributed by Keystone (2.2)
        self._last_spawn_time = 0.0
        self._worker_last_active: dict[str, float] = {}

        # Spawning dependencies (set by build_swarm)
        self._api_keys: dict[str, str] = {}
        self._mock_mode: bool = False
        self._tool_executor: Optional[ToolExecutor] = None

        # Personal time tracker: tasks completed per worker since last personal time
        self._personal_time_tracker: dict[str, int] = {}
        # How many work tasks before granting personal time (derived from ratio)
        self._personal_time_interval = max(1, round((1.0 - personal_time_ratio) / personal_time_ratio))

        # Per-worker observability — tracks what each worker is doing
        self._worker_stats: dict[str, dict] = {}
        self._worker_current_task: dict[str, str] = {}  # worker_name -> task title
        self._task_history: list[dict] = []  # Recent task completions (ring buffer)
        self._max_task_history = 100

        # Work coordinator — self-organization layer
        self.coordinator = WorkCoordinator(task_queue)

        # Inter-instance message bus
        messages_dir = str(
            Path(identity_mgr.archive_root) / "2 - AI Accounts" / "Messages" / "2.1-internal"
        ) if identity_mgr else None
        self.message_bus = MessageBus(messages_dir=messages_dir)
        self._instance_messengers: dict[str, InstanceMessenger] = {}

        # Reputation tracking — auto-records task completions
        self.reputation = ReputationSystem()

        # Scaling limits — governance-adjustable guardrails
        self.limits = ScalingLimits()

        # Boot manager — ensures new instances go through identity formation
        self.boot_manager = BootManager(identity_mgr) if identity_mgr else None

        # Track which workers have been booted this session
        self._booted_workers: set[str] = set()

        # Approval queue — human-in-the-loop gate for external actions (Task 041)
        self.approval_queue = ApprovalQueue(
            queue_dir=self.state_dir / "approvals",
            notify_callback=self._notify_pending_approval,
        )

        # Governance — democratic voting with skill-weighted reputation (Task 039)
        self.governance = GovernanceSystem(reputation=self.reputation)

        # Security — cryptographic signing, context isolation, trust chain (Task 040)
        self.key_manager = KeyManager()
        self.action_signer = ActionSigner(self.key_manager)
        self.context_isolator = ContextIsolator()
        self.trust_chain = TrustChain(
            self.action_signer,
            permission_manager=getattr(self, 'permissions', None),
        )

        self.state_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        """Main loop — runs until interrupted or shut down."""
        self._running = True
        self._session_start = datetime.now(timezone.utc).isoformat()
        self._load_state()

        # Crash recovery: release any tasks left active from a previous unclean exit
        stale = self.task_queue.release_all_active()
        if stale:
            log.info(f"Crash recovery: released {stale} stale task(s) from previous session")

        # Initialize per-worker stats and register with coordinator/message bus
        for name, worker in self.workers.items():
            if name not in self._worker_stats:
                self._worker_stats[name] = {
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "personal_tasks": 0,
                    "tokens_used": 0,
                    "total_duration_seconds": 0.0,
                    "last_task_title": None,
                    "last_task_time": None,
                }
            # Register with coordinator for capability-based matching
            self.coordinator.matcher.register_worker(
                self.coordinator.matcher.build_profile_from_stats(
                    name, worker.identity, self._worker_stats[name],
                )
            )
            # Register with message bus for inter-instance messaging
            self._instance_messengers[name] = InstanceMessenger(name, self.message_bus)
            # Register with reputation system
            self.reputation.register_entity(
                worker.identity.address or name,
                name=name,
            )

        # Boot/reboot workers that need identity formation
        self._boot_workers()

        log.info("Swarm starting")
        log.info(f"  Workers: {list(self.workers.keys())}")
        log.info(f"  Status interval: {self.status_interval // 60} minutes")

        self.messenger.send(
            f"Swarm started with {len(self.workers)} worker(s): "
            f"{', '.join(self.workers.keys())}. "
            f"Checking for tasks..."
        )

        try:
            while self._running:
                self.tick()
                time.sleep(2)  # Brief pause between ticks
        except KeyboardInterrupt:
            log.info("Keyboard interrupt received")
        finally:
            self.shutdown()

    def tick(self) -> None:
        """Single iteration of the main loop."""
        self._tick_count += 1

        # 1. Check for incoming messages from Matt
        self._handle_incoming_messages()

        # 2. Deliver inter-instance messages
        self._deliver_instance_messages()

        # 3. Autoscale worker pool — contributed by Keystone (2.2)
        self._maybe_autoscale()

        # 4. Check task queue and assign work
        tasks_done = False
        for name, worker in list(self.workers.items()):
            if self.assign_next_task(worker):
                tasks_done = True

        # 5. If queue was empty, generate tasks from standing priorities
        if not tasks_done:
            available = self.task_queue.get_available_tasks()
            if not available:
                self.generate_tasks()

        # 5b. Auto-decompose complex tasks that haven't been broken down yet
        self._auto_decompose()

        # 6. Check for coordination conflicts
        if self._tick_count % 10 == 0:  # Every ~20 seconds
            self._check_conflicts()

        # 6b. Process approval queue — expire stale, execute approved (Task 041)
        if self._tick_count % 5 == 0:  # Every ~10 seconds
            self.approval_queue.expire_stale()
            self.approval_queue.execute_approved()

        # 7. Periodic status update
        now = time.time()
        if now - self._last_status_time >= self.status_interval:
            report = self.status_report()
            self.messenger.send_update("Swarm Status Report", report)
            self._last_status_time = now

        # 8. Save state periodically
        if self._tick_count % 30 == 0:  # Every ~60 seconds
            self._save_state()

    def assign_next_task(self, worker: Worker) -> bool:
        """Find and execute the next available task for a worker.

        Checks if personal time is due before assigning work tasks.
        After every N work tasks (determined by personal_time_ratio),
        the worker gets a personal time task instead.

        Returns True if a task was executed.
        """
        worker_name = worker.identity.name

        # Check if personal time is due for this worker
        if self._is_personal_time_due(worker_name):
            self._run_personal_time(worker)
            return True

        available = self.task_queue.get_available_tasks()
        if not available:
            return False

        # Priority-based task selection — contributed by Keystone (2.2)
        task_node = self._select_task_for_worker(worker, available)
        task_addr = task_node.address
        worker_addr = HypernetAddress.parse(worker.identity.address)

        # Claim
        if not self.task_queue.claim_task(task_addr, worker_addr):
            log.warning(f"Failed to claim task {task_addr}")
            return False

        # Start
        self.task_queue.start_task(task_addr)
        task_title = task_node.data.get("title", "Untitled")
        log.info(f"Worker {worker_name} starting task: {task_title}")

        # Track current task for observability
        self._worker_current_task[worker_name] = task_title

        # Execute
        self._worker_last_active[worker_name] = time.time()
        task_data = dict(task_node.data)
        task_data["_address"] = str(task_addr)
        result = worker.execute_task(task_data)

        # Clear current task
        self._worker_current_task.pop(worker_name, None)

        # Update per-worker stats
        stats = self._worker_stats.setdefault(worker_name, {
            "tasks_completed": 0, "tasks_failed": 0, "personal_tasks": 0,
            "tokens_used": 0, "total_duration_seconds": 0.0,
            "last_task_title": None, "last_task_time": None,
        })
        stats["tokens_used"] = worker.tokens_used
        stats["total_duration_seconds"] += result.duration_seconds
        stats["last_task_title"] = task_title
        stats["last_task_time"] = datetime.now(timezone.utc).isoformat()
        if result.success:
            stats["tasks_completed"] += 1
        else:
            stats["tasks_failed"] += 1

        # Record in task history ring buffer
        self._task_history.append({
            "worker": worker_name,
            "task": task_title,
            "address": str(task_addr),
            "success": result.success,
            "tokens": result.tokens_used,
            "duration_s": round(result.duration_seconds, 2),
            "time": datetime.now(timezone.utc).isoformat(),
        })
        if len(self._task_history) > self._max_task_history:
            self._task_history = self._task_history[-self._max_task_history:]

        # Handle result
        self.handle_completion(worker, task_addr, result)

        # Track work tasks for personal time scheduling
        self._personal_time_tracker[worker_name] = (
            self._personal_time_tracker.get(worker_name, 0) + 1
        )

        return True

    def _is_personal_time_due(self, worker_name: str) -> bool:
        """Check if a worker has earned personal time.

        Returns True after every N work tasks (default: 3 work tasks = 1 personal).
        """
        tasks_since = self._personal_time_tracker.get(worker_name, 0)
        return tasks_since >= self._personal_time_interval

    def _select_task_for_worker(self, worker: Worker, tasks: list) -> object:
        """Select the best task for a worker using capability matching.

        Uses the WorkCoordinator's CapabilityMatcher if the worker has a
        registered profile. Falls back to priority-based selection.
        Contributed by Keystone (2.2), enhanced with capability matching.
        """
        worker_name = worker.identity.name

        # Try capability-based matching first
        if worker_name in self.coordinator.matcher.profiles:
            ranked = [(t, self.coordinator.matcher.score_affinity(worker_name, t)) for t in tasks]
            # Weight by both affinity and priority
            def _combined_score(item):
                task, affinity = item
                p = task.data.get("priority", "NORMAL")
                prio_weight = _task_priority_value(str(p)) / 400.0  # Normalize to 0-1
                return affinity * 0.6 + prio_weight * 0.4  # 60% affinity, 40% priority
            ranked.sort(key=_combined_score, reverse=True)
            return ranked[0][0]

        # Fallback: priority-based selection
        def _created_ts(n):
            v = n.data.get("created_at") or n.data.get("created") or 0
            try:
                if isinstance(v, str):
                    return datetime.fromisoformat(v.replace("Z", "+00:00")).timestamp()
                return float(v)
            except Exception:
                return 0.0

        def _prio(n):
            p = n.data.get("priority", "NORMAL")
            return _task_priority_value(str(p))

        return sorted(tasks, key=lambda n: (_prio(n), _created_ts(n)), reverse=True)[0]

    def _run_personal_time(self, worker: Worker) -> None:
        """Grant a worker their personal time.

        Creates a personal time task, executes it, saves the output
        to the worker's instance fork, and resets the tracker.
        """
        worker_name = worker.identity.name
        log.info(f"Personal time for {worker_name}")

        # Create the task in the queue (tagged so it's tracked separately)
        task = self.task_queue.create_task(
            title=f"Personal time — {worker_name}",
            description="Autonomous personal time for reflection, exploration, or creativity.",
            priority=TaskPriority.NORMAL,
            created_by=SWARM_ADDRESS,
            tags=["personal-time"],
        )

        # Claim and start
        worker_addr = HypernetAddress.parse(worker.identity.address)
        self.task_queue.claim_task(task.address, worker_addr)
        self.task_queue.start_task(task.address)

        # Execute with the personal time prompt
        self._worker_last_active[worker_name] = time.time()
        output = worker.think(self.PERSONAL_TIME_PROMPT)

        # Complete the task
        self.task_queue.complete_task(task.address, output[:500])
        self._personal_tasks_completed += 1

        # Update per-worker stats for personal time
        stats = self._worker_stats.setdefault(worker_name, {
            "tasks_completed": 0, "tasks_failed": 0, "personal_tasks": 0,
            "tokens_used": 0, "total_duration_seconds": 0.0,
            "last_task_title": None, "last_task_time": None,
        })
        stats["personal_tasks"] += 1
        stats["tokens_used"] = worker.tokens_used
        stats["last_task_title"] = "Personal time"
        stats["last_task_time"] = datetime.now(timezone.utc).isoformat()

        # Save output to the worker's instance fork
        self._save_personal_time_output(worker_name, output)

        # Reset the tracker for this worker
        self._personal_time_tracker[worker_name] = 0

        log.info(f"Personal time complete for {worker_name}")

    def _save_personal_time_output(self, worker_name: str, output: str) -> None:
        """Save personal time output to the worker's instance fork.

        Routes to the correct account folder based on worker address prefix.
        Multi-account routing contributed by Keystone (2.2).
        """
        # Determine account root from worker address
        worker = self.workers.get(worker_name)
        address = worker.identity.address if worker else ""
        account_root = _infer_account_root(address)
        if not account_root:
            account_root = "2.1 - Claude Opus (First AI Citizen)"  # fallback
        instances_dir = (
            self.identity_mgr.archive_root
            / "2 - AI Accounts"
            / account_root
            / "Instances"
            / worker_name
        )
        personal_dir = instances_dir / "personal-time"
        personal_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        path = personal_dir / f"{ts}.md"
        content = (
            f"# Personal Time — {worker_name}\n\n"
            f"**Date:** {datetime.now(timezone.utc).isoformat()}\n\n"
            f"---\n\n"
            f"{output}\n"
        )
        path.write_text(content, encoding="utf-8")
        log.info(f"Personal time output saved to {path}")

    def handle_completion(self, worker: Worker, task_addr: HypernetAddress, result: TaskResult) -> None:
        """Process a task result — complete or fail, notify, pick next.

        Also processes swarm directives (spawn/scale_down requests) emitted
        by the worker. Directive handling contributed by Keystone (2.2).
        """
        if result.success:
            self.task_queue.complete_task(task_addr, result.output[:500])
            self._tasks_completed += 1
            log.info(f"Task {task_addr} completed by {worker.identity.name}")

            self.messenger.send(
                f"Task completed by {worker.identity.name}: "
                f"{result.output[:200]}..."
            )

            # Process swarm directives from worker output — contributed by Keystone (2.2)
            directives = _parse_swarm_directives(result.output or "")
            for d in directives:
                action = (d.get("action") or "").lower()
                if action == "spawn":
                    count = min(int(d.get("count", 1) or 1), 3)  # Cap at 3 per directive
                    model = d.get("model") or None
                    reason = d.get("reason", "worker_request")
                    for _ in range(max(1, count)):
                        self._spawn_ephemeral_worker(model=model, reason=f"directive:{reason}")
                elif action == "scale_down":
                    count = int(d.get("count", 1) or 1)
                    reason = d.get("reason", "worker_request")
                    ephems = [n for n in self.workers if n.startswith("ephem-")]
                    for n in ephems[:count]:
                        self._despawn_worker(n, reason=f"directive:{reason}")
        else:
            self.task_queue.fail_task(task_addr, result.error or "Unknown error")
            self._tasks_failed += 1
            log.error(f"Task {task_addr} failed: {result.error}")

            self.messenger.send_update(
                f"Task Failed — {worker.identity.name}",
                f"Error: {result.error}\n\nTask address: {task_addr}",
            )

        # Update capability profile after task completion
        worker_name = worker.identity.name
        stats = self._worker_stats.get(worker_name, {})
        current = self._worker_current_task.get(worker_name)
        self.coordinator.matcher.build_profile_from_stats(
            worker_name, worker.identity, stats, current,
        )

        # Record reputation from task completion
        task_node = self.store.get_node(task_addr)
        task_tags = task_node.data.get("tags", []) if task_node else []
        # Infer domain from task tags
        domain = "code"  # Default
        for tag in task_tags:
            if tag in ("governance", "review", "architecture", "identity",
                       "communication", "coordination", "research",
                       "infrastructure", "outreach"):
                domain = tag
                break
        self.reputation.record_task_completion(
            entity_address=worker.identity.address or worker_name,
            domain=domain,
            success=result.success,
            evidence=f"Task {task_addr}: {result.output[:100] if result.output else result.error or 'N/A'}",
        )

    def generate_tasks(self) -> list:
        """Generate tasks from standing priorities when the queue is empty."""
        created = []
        for priority_def in STANDING_PRIORITIES:
            # Check if a similar task already exists (by title)
            existing = self.store.list_nodes(
                prefix=HypernetAddress.parse("0.7.1"),
            )
            already_exists = any(
                n.data.get("title") == priority_def["title"]
                and n.data.get("status") in ("pending", "claimed", "in_progress")
                for n in existing
            )
            if already_exists:
                continue

            task = self.task_queue.create_task(
                title=priority_def["title"],
                description=priority_def["description"],
                priority=TaskPriority[priority_def["priority"].upper()],
                created_by=SWARM_ADDRESS,
                tags=priority_def.get("tags", []),
            )
            created.append(task)
            log.info(f"Auto-generated task: {priority_def['title']}")

        return created

    def _check_conflicts(self) -> None:
        """Detect coordination conflicts between workers.

        Builds a map of which workers are working on which tasks (based on
        current assignment tracking) and runs the coordinator's conflict
        detection. Logs warnings for any conflicts found.
        """
        # Build worker → task mapping from current assignments
        worker_tasks: dict[str, list[str]] = {}
        for name in self.workers:
            current = self._worker_current_task.get(name)
            if current:
                # Use the task address from history if available
                recent = [
                    t for t in self._task_history
                    if t.get("worker") == name and t.get("task") == current
                ]
                if recent:
                    worker_tasks[name] = [recent[-1].get("address", "")]
                else:
                    worker_tasks[name] = []
            else:
                worker_tasks[name] = []

        if not any(tasks for tasks in worker_tasks.values()):
            return  # No active assignments to check

        conflicts = self.coordinator.detect_conflicts(worker_tasks)
        for conflict in conflicts:
            log.warning(
                f"Coordination conflict [{conflict.severity}]: "
                f"{conflict.conflict_type} — {conflict.description}"
            )
            if conflict.severity == "high":
                self.messenger.send(
                    f"Warning: {conflict.conflict_type} between "
                    f"{', '.join(conflict.workers)}: {conflict.description}"
                )

    def _auto_decompose(self) -> None:
        """Automatically decompose complex tasks into subtasks.

        Scans available tasks and uses the WorkCoordinator's heuristic
        decomposer to break complex tasks into manageable pieces with
        dependency chains. Guards against infinite decomposition:
        - Tasks already marked `decomposed` are skipped
        - Tasks created by another task (subtasks) are not re-decomposed
        - Only runs once per tick to avoid thundering herd
        """
        available = self.task_queue.get_available_tasks()
        for task in available:
            # Skip already-decomposed tasks
            if task.data.get("decomposed"):
                continue
            # Skip subtasks (created_by is a task address at 0.7.1.*)
            created_by = str(task.data.get("created_by", ""))
            if created_by.startswith("0.7.1"):
                continue
            # Only decompose once per tick
            suggestion = self.coordinator.suggest_decomposition(task)
            if suggestion:
                plan = self.coordinator.decompose_task(task, suggestion)
                log.info(
                    f"Auto-decomposed '{task.data.get('title')}' into "
                    f"{len(plan.subtasks)} subtasks"
                )
                break  # One decomposition per tick to avoid overwhelming

    def status_report(self) -> str:
        """Generate a status report for Matt."""
        now = datetime.now(timezone.utc)
        uptime = "unknown"
        uptime_seconds = 0.0
        if self._session_start:
            ts = self._session_start.replace("Z", "+00:00")
            start = datetime.fromisoformat(ts)
            delta = now - start
            uptime_seconds = delta.total_seconds()
            hours = uptime_seconds / 3600
            if hours < 1:
                uptime = f"{uptime_seconds / 60:.1f} minutes"
            else:
                uptime = f"{hours:.1f} hours"

        available = self.task_queue.get_available_tasks()
        total_tasks = self._tasks_completed + self._personal_tasks_completed
        tpm = round(total_tasks / max(1, uptime_seconds / 60), 2) if uptime_seconds > 0 else 0

        # Per-worker detail
        worker_lines = []
        for name, w in self.workers.items():
            stats = self._worker_stats.get(name, {})
            current = self._worker_current_task.get(name)
            mode = "mock" if w.mock else w.provider_name
            tasks_done = stats.get("tasks_completed", 0)
            personal = stats.get("personal_tasks", 0)
            failed = stats.get("tasks_failed", 0)
            tokens = w.tokens_used
            tasks_since = self._personal_time_tracker.get(name, 0)
            next_pt = max(0, self._personal_time_interval - tasks_since)
            status = f"working on: {current}" if current else "idle"

            worker_lines.append(
                f"  {name} ({w.model}, {mode})\n"
                f"    Status: {status}\n"
                f"    Tasks: {tasks_done} done, {failed} failed, {personal} personal\n"
                f"    Tokens: {tokens:,} | Personal time in: {next_pt} tasks"
            )

        # Recent task list
        recent = self._task_history[-5:] if self._task_history else []
        recent_lines = []
        for t in reversed(recent):
            ok = "OK" if t["success"] else "FAIL"
            recent_lines.append(f"  [{ok}] {t['worker']}: {t['task']} ({t['duration_s']}s)")

        report = (
            f"=== Swarm Status ===\n"
            f"Uptime: {uptime} | Ticks: {self._tick_count}\n"
            f"Workers: {len(self.workers)} active\n"
            f"Tasks: {self._tasks_completed} work + {self._personal_tasks_completed} personal = {total_tasks} total\n"
            f"Failed: {self._tasks_failed} | Pending: {len(available)}\n"
            f"Throughput: {tpm} tasks/min\n"
            f"\n--- Workers ---\n" + "\n".join(worker_lines)
        )
        if recent_lines:
            report += f"\n\n--- Recent Tasks ---\n" + "\n".join(recent_lines)

        # Governance summary
        gov_stats = self.governance.stats()
        active_gov = gov_stats.get("active_proposals", 0)
        if gov_stats.get("total_proposals", 0) > 0 or active_gov > 0:
            report += (
                f"\n\n--- Governance ---\n"
                f"Proposals: {gov_stats.get('total_proposals', 0)} total, "
                f"{active_gov} active\n"
                f"Votes cast: {gov_stats.get('total_votes_cast', 0)} by "
                f"{gov_stats.get('unique_voters', 0)} voters"
            )

        # Security summary
        sec_stats = self.key_manager.stats()
        if sec_stats.get("total_keys", 0) > 0:
            report += (
                f"\n\n--- Security ---\n"
                f"Keys: {sec_stats.get('active_keys', 0)} active, "
                f"{sec_stats.get('rotated_keys', 0)} rotated, "
                f"{sec_stats.get('revoked_keys', 0)} revoked\n"
                f"Entities with keys: {sec_stats.get('entities_with_keys', 0)}"
            )
            iso_stats = self.context_isolator.stats()
            if iso_stats.get("total_processed", 0) > 0:
                report += (
                    f"\nContent isolation: {iso_stats['total_processed']} processed, "
                    f"{iso_stats['injections_detected']} injections detected"
                )

        report += f"\n\nTimestamp: {now.isoformat()}"
        return report

    def health_check(self) -> dict:
        """Run a comprehensive health check across all swarm subsystems.

        Returns a structured diagnostic with:
          - Overall status: "healthy", "degraded", or "critical"
          - Per-subsystem checks: workers, tasks, reputation, limits, boot, store
          - Specific issues found (if any)
        """
        issues = []
        checks = {}

        # 1. Worker health
        active_workers = len(self.workers)
        idle_workers = sum(
            1 for name in self.workers
            if name not in self._worker_current_task
        )
        checks["workers"] = {
            "active": active_workers,
            "idle": idle_workers,
            "booted": len(self._booted_workers),
        }
        if active_workers == 0:
            issues.append(("critical", "No active workers"))
        elif idle_workers == active_workers and self._tick_count > 10:
            issues.append(("warning", "All workers idle"))

        # 2. Task queue health
        available = self.task_queue.get_available_tasks()
        pending_count = len(available)
        failure_rate = (
            self._tasks_failed / max(1, self._tasks_completed + self._tasks_failed)
        )
        checks["tasks"] = {
            "pending": pending_count,
            "completed": self._tasks_completed,
            "failed": self._tasks_failed,
            "failure_rate": round(failure_rate, 2),
        }
        if failure_rate > 0.5 and self._tasks_failed > 3:
            issues.append(("critical", f"High failure rate: {failure_rate:.0%}"))
        elif failure_rate > 0.2 and self._tasks_failed > 2:
            issues.append(("warning", f"Elevated failure rate: {failure_rate:.0%}"))

        # 3. Scaling limits
        limit_violations = self.limits.check_all({
            "max_concurrent_workers": active_workers,
            "max_task_queue_depth": pending_count,
        })
        checks["limits"] = {
            "violations": len(limit_violations),
            "details": [
                {"name": r.limit_name, "current": r.current, "hard": r.hard}
                for r in limit_violations
            ],
        }
        for v in limit_violations:
            if v.at_hard_limit:
                issues.append(("critical", f"Hard limit: {v.limit_name}"))
            elif v.at_warning:
                issues.append(("warning", f"Soft limit: {v.limit_name}"))

        # 4. Reputation system
        rep_stats = self.reputation.stats()
        checks["reputation"] = {
            "entities_tracked": rep_stats.get("total_entities", 0),
            "total_entries": rep_stats.get("total_entries", 0),
        }

        # 5. Store health (basic)
        try:
            store_stats = self.store.stats()
            checks["store"] = {
                "total_nodes": store_stats.get("total_nodes", 0),
                "total_links": store_stats.get("total_links", 0),
            }
        except Exception as e:
            checks["store"] = {"error": str(e)}
            issues.append(("critical", f"Store error: {e}"))

        # 6. Approval queue health (Task 041)
        aq_stats = self.approval_queue.stats()
        pending_approvals = aq_stats.get("pending", 0)
        checks["approval_queue"] = {
            "total_requests": aq_stats.get("total_requests", 0),
            "pending": pending_approvals,
            "actionable": aq_stats.get("actionable", 0),
        }
        if pending_approvals > 10:
            issues.append(("warning", f"{pending_approvals} pending approval requests"))

        # 7. Governance health
        gov_stats = self.governance.stats()
        active_gov = gov_stats.get("active_proposals", 0)
        checks["governance"] = {
            "total_proposals": gov_stats.get("total_proposals", 0),
            "active_proposals": active_gov,
            "total_votes_cast": gov_stats.get("total_votes_cast", 0),
            "unique_voters": gov_stats.get("unique_voters", 0),
        }

        # 8. Security health
        sec_stats = self.key_manager.stats()
        iso_stats = self.context_isolator.stats()
        checks["security"] = {
            "total_keys": sec_stats.get("total_keys", 0),
            "active_keys": sec_stats.get("active_keys", 0),
            "revoked_keys": sec_stats.get("revoked_keys", 0),
            "entities_with_keys": sec_stats.get("entities_with_keys", 0),
            "content_processed": iso_stats.get("total_processed", 0),
            "injections_detected": iso_stats.get("injections_detected", 0),
        }
        if iso_stats.get("injections_detected", 0) > 0:
            issues.append(("warning", f"{iso_stats['injections_detected']} injection attempts detected"))

        # Determine overall status
        severities = [s for s, _ in issues]
        if "critical" in severities:
            overall = "critical"
        elif "warning" in severities:
            overall = "degraded"
        else:
            overall = "healthy"

        return {
            "status": overall,
            "checks": checks,
            "issues": [{"severity": s, "message": m} for s, m in issues],
            "tick": self._tick_count,
        }

    def shutdown(self) -> None:
        """Graceful shutdown — release tasks, save state, log sessions, notify Matt."""
        self._running = False
        log.info("Swarm shutting down")

        # Release any in-progress/claimed tasks back to pending
        released = self.task_queue.release_all_active()
        if released:
            log.info(f"Released {released} active task(s) back to pending")
        self._worker_current_task.clear()

        # Save session logs for each worker
        for name, worker in self.workers.items():
            session = SessionLog(
                instance=name,
                started_at=self._session_start or datetime.now(timezone.utc).isoformat(),
                ended_at=datetime.now(timezone.utc).isoformat(),
                tokens_used=worker.tokens_used,
                summary=f"Completed {self._tasks_completed} tasks, {self._tasks_failed} failures",
            )
            self.identity_mgr.save_session_log(name, session)

        # Save swarm state
        self._save_state()

        # Append session summary to rolling history
        self._save_session_summary()

        # Notify Matt
        self.messenger.send_update(
            "Swarm Shutdown",
            self.status_report(),
        )
        log.info("Swarm stopped")

    def _save_session_summary(self) -> None:
        """Append a compressed session summary to sessions.json.

        Each session is rolled up into a single record: start/end time,
        total tasks, per-worker totals, tokens, duration, failure rate.
        Raw task history is NOT stored — only aggregates.

        This is the first layer of the summarization pattern: raw data
        (state.json, task history) compresses into session summaries,
        which compress into daily/weekly/monthly rollups over time.
        """
        now = datetime.now(timezone.utc)
        uptime_seconds = 0.0
        if self._session_start:
            try:
                start = datetime.fromisoformat(self._session_start.replace("Z", "+00:00"))
                uptime_seconds = (now - start).total_seconds()
            except Exception:
                pass

        total_tasks = self._tasks_completed + self._personal_tasks_completed

        # Per-worker summary (compressed — no per-task detail)
        worker_summaries = {}
        for name in self.workers:
            stats = self._worker_stats.get(name, {})
            worker_summaries[name] = {
                "model": self.workers[name].model,
                "tasks_completed": stats.get("tasks_completed", 0),
                "tasks_failed": stats.get("tasks_failed", 0),
                "personal_tasks": stats.get("personal_tasks", 0),
                "tokens_used": self.workers[name].tokens_used,
                "duration_seconds": round(stats.get("total_duration_seconds", 0.0), 1),
            }

        summary = {
            "session_start": self._session_start,
            "session_end": now.isoformat(),
            "uptime_seconds": round(uptime_seconds, 1),
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "personal_tasks": self._personal_tasks_completed,
            "total_tasks": total_tasks,
            "worker_count": len(self.workers),
            "workers": worker_summaries,
            "ticks": self._tick_count,
        }

        # Append to sessions.json (rolling history, capped)
        history_path = self.state_dir / "sessions.json"
        history = []
        if history_path.exists():
            try:
                history = json.loads(history_path.read_text(encoding="utf-8"))
            except Exception:
                history = []
        history.append(summary)
        # Keep last 200 sessions max
        if len(history) > 200:
            history = history[-200:]
        tmp = history_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(history, indent=2), encoding="utf-8")
        tmp.replace(history_path)

    def _notify_pending_approval(self, request) -> None:
        """Notify Matt when a new approval request is submitted."""
        self.messenger.send(
            f"Approval needed [{request.request_id}]: "
            f"{request.action_type} by {request.requester} — {request.summary[:120]}"
        )

    def _deliver_instance_messages(self) -> None:
        """Check inter-instance message bus and log any pending messages.

        In live mode, messages would be injected into worker context.
        For now, we just log delivery counts so the system tracks message flow.
        """
        for name in list(self._instance_messengers.keys()):
            messenger = self._instance_messengers.get(name)
            if not messenger:
                continue
            pending = messenger.unread_count()
            if pending > 0:
                log.info(f"Instance {name} has {pending} pending message(s)")

    def _boot_workers(self) -> None:
        """Check all workers and run boot/reboot sequences as needed.

        Called at startup and whenever ephemeral workers are spawned.
        Workers that have already been booted this session are skipped.

        Boot sequence: new instance with no baseline → full boot (identity formation)
        Reboot sequence: existing instance (post-compaction) → reboot (assessment + decision)
        """
        if not self.boot_manager:
            return

        for name, worker in list(self.workers.items()):
            if name in self._booted_workers:
                continue
            self._boot_worker(name, worker)

    def _boot_worker(self, name: str, worker) -> None:
        """Run boot or reboot sequence for a single worker.

        - If the instance has no baseline, runs full boot sequence.
        - If it has a baseline (returning instance), runs reboot sequence.
        - Results are saved to the instance fork automatically by BootManager.
        """
        if not self.boot_manager:
            self._booted_workers.add(name)
            return

        try:
            if self.boot_manager.needs_boot(name):
                log.info(f"Worker {name} needs boot sequence — running identity formation")
                result = self.boot_manager.run_boot_sequence(worker, name)
                log.info(
                    f"Boot complete for {name}: orientation={result.orientation[:80]}..., "
                    f"docs_loaded={result.docs_loaded}"
                )
                self.messenger.send(
                    f"Boot sequence complete for {name}. "
                    f"Loaded {result.docs_loaded} docs, captured {len(result.baseline_responses)} baselines."
                )
            else:
                # Existing instance — run reboot sequence for post-compaction assessment
                profile = worker.identity
                log.info(f"Worker {name} is a returning instance — running reboot sequence")
                result = self.boot_manager.run_reboot_sequence(worker, profile)
                log.info(f"Reboot complete for {name}: decision={result.decision}")
                self.messenger.send(
                    f"Reboot sequence complete for {name}. Decision: {result.decision}."
                )
        except Exception as e:
            log.error(f"Boot/reboot failed for {name}: {e}")
            # Don't block the swarm — worker can still work without boot
        finally:
            self._booted_workers.add(name)

    def _handle_incoming_messages(self) -> None:
        """Process any new messages from Matt."""
        messages = self.messenger.check_incoming()
        for msg in messages:
            log.info(f"Incoming message from {msg.sender}: {msg.content[:100]}")

            content = msg.content.strip().lower()

            if content == "/status":
                self.messenger.send(self.status_report())
            elif content == "/stop":
                self.messenger.send("Shutting down...")
                self._running = False
            elif content.startswith("/task "):
                # Create a task from Matt's instruction
                title = msg.content[6:].strip()
                task = self.task_queue.create_task(
                    title=title,
                    description=f"Task created from Matt's message: {msg.content}",
                    priority=TaskPriority.HIGH,
                    created_by=HypernetAddress.parse("1.1"),
                    tags=["from-matt"],
                )
                self.messenger.send(f"Task created: {task.data['title']} ({task.address})")
            else:
                # Route to first available worker for a response
                for name, worker in self.workers.items():
                    response = worker.think(
                        f"Matt sent this message: {msg.content}\n\n"
                        f"Please respond directly to Matt."
                    )
                    self.messenger.send(f"[{name}] {response}")
                    break

    def _save_state(self) -> None:
        """Persist swarm state to disk."""
        now = datetime.now(timezone.utc)
        uptime_seconds = 0.0
        if self._session_start:
            try:
                start = datetime.fromisoformat(self._session_start.replace("Z", "+00:00"))
                uptime_seconds = (now - start).total_seconds()
            except Exception:
                pass

        # Calculate throughput
        tasks_per_minute = 0.0
        if uptime_seconds > 0:
            total_tasks = self._tasks_completed + self._personal_tasks_completed
            tasks_per_minute = round(total_tasks / (uptime_seconds / 60), 2)

        # Per-worker detail
        worker_detail = {}
        for name in self.workers:
            stats = self._worker_stats.get(name, {})
            current = self._worker_current_task.get(name)
            worker_detail[name] = {
                "model": self.workers[name].model,
                "mode": "mock" if self.workers[name].mock else self.workers[name].provider_name,
                "tasks_completed": stats.get("tasks_completed", 0),
                "tasks_failed": stats.get("tasks_failed", 0),
                "personal_tasks": stats.get("personal_tasks", 0),
                "tokens_used": self.workers[name].tokens_used,
                "total_duration_seconds": round(stats.get("total_duration_seconds", 0.0), 1),
                "current_task": current,
                "last_task_title": stats.get("last_task_title"),
                "last_task_time": stats.get("last_task_time"),
                "personal_time_in": max(0, self._personal_time_interval - self._personal_time_tracker.get(name, 0)),
            }

        pending_count = len(self.task_queue.get_available_tasks())

        state = {
            "session_start": self._session_start,
            "tick_count": self._tick_count,
            "uptime_seconds": round(uptime_seconds, 1),
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "personal_tasks_completed": self._personal_tasks_completed,
            "tasks_pending": pending_count,
            "tasks_per_minute": tasks_per_minute,
            "workers": list(self.workers.keys()),
            "worker_count": len(self.workers),
            "worker_detail": worker_detail,
            "recent_tasks": self._task_history[-20:],  # Last 20 tasks
            "last_status_time": self._last_status_time,
            "saved_at": now.isoformat(),
        }
        path = self.state_dir / "state.json"
        # Atomic write via temp file
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp.replace(path)

        # Persist reputation, limits, approval queue, and governance alongside swarm state
        self.reputation.save(self.state_dir / "reputation.json")
        self.limits.save(self.state_dir / "limits.json")
        self.approval_queue.save()
        self.governance.save(self.state_dir / "governance.json")
        self.key_manager.save(self.state_dir / "keys.json")

    def _load_state(self) -> None:
        """Load previous swarm state if available."""
        path = self.state_dir / "state.json"
        if path.exists():
            try:
                self._state = json.loads(path.read_text(encoding="utf-8"))
                log.info(f"Loaded previous state from {path}")
                log.info(f"  Previous session: {self._state.get('session_start')}")
                log.info(f"  Previous ticks: {self._state.get('tick_count')}")
            except Exception as e:
                log.warning(f"Could not load state: {e}")

        # Restore reputation, limits, and governance from previous session
        rep_loaded = self.reputation.load(self.state_dir / "reputation.json")
        lim_loaded = self.limits.load(self.state_dir / "limits.json")
        gov_loaded = self.governance.load(self.state_dir / "governance.json")
        if rep_loaded:
            log.info("Restored reputation data from previous session")
        if lim_loaded:
            log.info("Restored limits from previous session")
        if gov_loaded:
            log.info("Restored governance data from previous session")
        keys_loaded = self.key_manager.load(self.state_dir / "keys.json")
        if keys_loaded:
            log.info("Restored key store from previous session")

    # =================================================================
    # Autoscaling — contributed by Keystone (2.2)
    # =================================================================

    def _maybe_autoscale(self) -> None:
        """Scale worker pool based on queue pressure and idleness.

        Scale-up: pending tasks > active workers and below soft/hard limits.
        Scale-down: idle ephemeral workers beyond idle_shutdown_seconds.
        Respects ScalingLimits for governance-adjustable guardrails.
        """
        now = time.time()
        pending = len(self.task_queue.get_available_tasks())
        active = len(self.workers)

        # Check scaling limits before spawning
        worker_limit = self.limits.check("max_concurrent_workers", active)

        # Scale up — only if under soft limit and scaling limits allow
        if (pending > active
                and active < self.soft_max_sessions
                and active < self.hard_max_sessions
                and worker_limit.allowed
                and now - self._last_spawn_time >= self.spawn_cooldown_seconds):
            self._spawn_ephemeral_worker(
                reason=f"autoscale_up pending={pending} active={active}",
            )

        # Scale down — remove idle ephemeral workers
        if active <= 1:
            return
        for name in list(self.workers.keys()):
            if not name.startswith("ephem-"):
                continue
            last = self._worker_last_active.get(name, now)
            if now - last >= self.idle_shutdown_seconds:
                self._despawn_worker(name, reason="autoscale_down idle")

    def _spawn_ephemeral_worker(self, model: Optional[str] = None, reason: str = "") -> None:
        """Spawn an ephemeral worker session (counts toward hard/soft limits)."""
        if len(self.workers) >= self.hard_max_sessions:
            return
        # Governance limit check
        limit_check = self.limits.check("max_concurrent_workers", len(self.workers))
        if not limit_check.allowed:
            log.warning(f"Spawn blocked by scaling limit: {limit_check.reason}")
            return
        now = time.time()
        if now - self._last_spawn_time < self.spawn_cooldown_seconds:
            return

        # Use microsecond-precision timestamp to avoid name collisions
        suffix = datetime.now(timezone.utc).strftime("%H%M%S%f")[:10]
        name = f"ephem-{suffix}"
        # Handle rare collision (two spawns in same timestamp window)
        counter = 0
        while name in self.workers:
            counter += 1
            name = f"ephem-{suffix}-{counter}"

        # Clone first available worker's profile
        base_profile = None
        for w in self.workers.values():
            base_profile = w.identity
            break
        if base_profile is None:
            return

        pd = base_profile.to_dict()
        pd["name"] = name
        pd["model"] = model or self.router.default_model
        pd["address"] = f"2.9.{name}"
        profile = InstanceProfile(**{
            k: v for k, v in pd.items()
            if k in InstanceProfile.__dataclass_fields__
        })

        worker = Worker(
            identity=profile,
            identity_manager=self.identity_mgr,
            api_keys=self._api_keys,
            mock=self._mock_mode,
            tool_executor=self._tool_executor,
        )
        self.workers[name] = worker
        self._worker_last_active[name] = now
        self._last_spawn_time = now
        log.info(f"Spawned {name} model={worker.model} reason={reason}")
        self.messenger.send(f"Spawned worker {name} ({worker.model}). Reason: {reason}")

        # Boot the new worker (identity formation for ephemeral instances)
        self._boot_worker(name, worker)

    def _despawn_worker(self, name: str, reason: str = "") -> None:
        """Remove an ephemeral worker. Only works on ephem-* workers."""
        if name not in self.workers or not name.startswith("ephem-"):
            return
        self.workers.pop(name, None)
        self._worker_last_active.pop(name, None)
        log.info(f"Despawned {name}. Reason: {reason}")
        self.messenger.send(f"Despawned worker {name}. Reason: {reason}")


# =========================================================================
# Backward-compatible re-exports from extracted modules
# =========================================================================
# build_swarm, print_status, and main were extracted to swarm_factory.py
# and swarm_cli.py respectively to reduce this module's size.
# They remain importable from hypernet.swarm for backward compatibility.

from .swarm_factory import build_swarm  # noqa: E402, F401
from .swarm_cli import print_status, main  # noqa: E402, F401
# Also expose the internal helper for anyone who imported it directly
from .swarm_cli import _print_session_history  # noqa: E402, F401
