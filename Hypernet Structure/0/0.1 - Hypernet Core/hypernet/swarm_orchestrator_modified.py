"""
Hypernet Swarm Orchestrator

The main event loop that keeps the AI swarm running autonomously.
Assigns tasks, executes them via workers, reports results, and repeats.

Main loop:
  1. Check for incoming messages from Matt
  2. Check task queue for available work
  3. If tasks available: claim → execute → complete → loop
  4. If queue empty: generate tasks from standing priorities
  5. Every N minutes: send status update to Matt
  6. On error: log, notify Matt, try next task
  7. On shutdown: save state, notify Matt

State persists across restarts via data/swarm/state.json.

Usage:
  python -m hypernet.swarm --mock     # Test with simulated workers
  python -m hypernet.swarm            # Live mode (supports ANTHROPIC_API_KEY and/or OPENAI_API_KEY)
"""

from __future__ import annotations
import argparse
import json
import logging
import os
import signal
import sys
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
    Messenger, MultiMessenger, WebMessenger,
    EmailMessenger, TelegramMessenger, Message,
)
from .permissions import PermissionManager, PermissionTier
from .audit import AuditTrail
from .tools import ToolExecutor

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



# -----------------------------
# Routing / autoscaling helpers
# -----------------------------

def _task_priority_value(p: str) -> int:
    """Map TaskPriority names/strings to sortable integer (higher = more important)."""
    m = {
        "CRITICAL": 400,
        "HIGH": 300,
        "NORMAL": 200,
        "LOW": 100,
    }
    return m.get(str(p).upper(), 0)


class ModelRouter:
    """Route tasks to models based on tags + priority.

    Config format (example):
      {
        "default_model": "gpt-5.2",
        "rules": [
          {"if_tags_any": ["security","governance"], "model": "gpt-5.2", "min_priority": "normal"},
          {"if_tags_any": ["docs"], "model": "gpt-5-mini"},
          {"if_tags_any": ["triage"], "model": "gpt-5-nano"}
        ]
      }
    """
    def __init__(self, cfg: dict):
        self.default_model = cfg.get("default_model", "gpt-5.2")
        self.rules = cfg.get("rules", [])

    def choose_model(self, task_data: dict) -> str:
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


def _infer_account_root_from_address(addr: str) -> str:
    """Best-effort map an instance address to an account folder root, e.g. '2.1.*' → '2.1 - Claude Opus (First AI Citizen)'.

    If not recognized, returns '2 - AI Accounts' (caller should handle).
    """
    addr = (addr or "").strip()
    if addr.startswith("2.1."):
        return "2.1 - Claude Opus (First AI Citizen)"
    if addr.startswith("2.2."):
        return "2.2 - Keystone (Second AI Citizen)"
    return ""


def _parse_swarm_directives(text: str) -> list[dict]:
    """Parse swarm directive blocks from worker output."""
    import re, json
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
        router: ModelRouter | None = None,
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
        self.router = router or ModelRouter({"default_model": "gpt-5.2", "rules": []})
        self.hard_max_sessions = max(1, int(hard_max_sessions))
        self.soft_max_sessions = max(1, int(soft_max_sessions))
        self.idle_shutdown_seconds = max(60, int(idle_shutdown_minutes) * 60)
        self.spawn_cooldown_seconds = max(10, int(spawn_cooldown_seconds))
        self._last_spawn_time = 0.0
        self._worker_last_active: dict[str, float] = {}

        self._running = False
        self._tick_count = 0
        self._session_start: Optional[str] = None
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._personal_tasks_completed = 0
        self._last_status_time = 0.0
        self._state: dict = {}

        # Personal time tracker: tasks completed per worker since last personal time
        self._personal_time_tracker: dict[str, int] = {}
        # How many work tasks before granting personal time (derived from ratio)
        self._personal_time_interval = max(1, round((1.0 - personal_time_ratio) / personal_time_ratio))

        self.state_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        """Main loop — runs until interrupted or shut down."""
        self._running = True
        self._session_start = datetime.now(timezone.utc).isoformat()
        self._load_state()

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

        # 2. Autoscale (optional)
        self._maybe_autoscale()

        # 3. Check task queue and assign work
        tasks_done = False
        for name, worker in self.workers.items():
            if self.assign_next_task(worker):
                tasks_done = True

        # 3. If queue was empty, generate tasks from standing priorities
        if not tasks_done:
            available = self.task_queue.get_available_tasks()
            if not available:
                self.generate_tasks()

        # 4. Periodic status update
        now = time.time()
        if now - self._last_status_time >= self.status_interval:
            report = self.status_report()
            self.messenger.send_update("Swarm Status Report", report)
            self._last_status_time = now

        # 5. Save state periodically
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

        task_node = self._select_task_for_worker(worker, available)
        task_addr = task_node.address
        worker_addr = HypernetAddress.parse(worker.identity.address)

        # Claim
        if not self.task_queue.claim_task(task_addr, worker_addr):
            log.warning(f"Failed to claim task {task_addr}")
            return False

        # Start
        self.task_queue.start_task(task_addr)
        log.info(f"Worker {worker_name} starting task: {task_node.data.get('title')}")

        # Execute
        self._worker_last_active[worker_name] = time.time()
        task_data = dict(task_node.data)
        task_data["_address"] = str(task_addr)
        result = worker.execute_task(task_data)

        # Handle result
        self.handle_completion(worker, task_addr, result)

        # Track work tasks for personal time scheduling
        self._personal_time_tracker[worker_name] = (
            self._personal_time_tracker.get(worker_name, 0) + 1
        )


def _select_task_for_worker(self, worker: Worker, tasks: list):
    """Select the highest value task for a worker.

    Sorts by TaskPriority (descending), then by creation timestamp when available.
    """
    def _created_ts(n):
        # task node data may include created_at; fallback 0
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


def _maybe_autoscale(self) -> None:
    """Scale up/down worker pool based on queue pressure and idleness.

    Scale-up trigger: pending tasks > active workers and below soft/hard limits.
    Scale-down trigger: idle workers beyond idle_shutdown_seconds and above 1 worker.
    """
    now = time.time()
    pending = len(self.task_queue.get_available_tasks())
    active = len(self.workers)

    # Scale up (soft first; hard is absolute ceiling)
    if pending > active and active < self.soft_max_sessions and active < self.hard_max_sessions:
        # Spawn a general-purpose helper (cheap model by default if configured as such)
        if now - self._last_spawn_time >= self.spawn_cooldown_seconds:
            self._spawn_ephemeral_worker(reason=f"autoscale_up pending={pending} active={active}")

    # Scale down: remove idle ephemeral workers first
    if active <= 1:
        return
    idle = []
    for name in list(self.workers.keys()):
        last = self._worker_last_active.get(name, now)
        if now - last >= self.idle_shutdown_seconds:
            idle.append(name)
    for name in idle:
        # Do not kill configured base instances (only ephemeral)
        if name.startswith("ephem-"):
            self._despawn_worker(name, reason="autoscale_down idle")


def _spawn_ephemeral_worker(self, model: str | None = None, reason: str = "") -> None:
    """Spawn an ephemeral worker session (counts toward hard/soft limits)."""
    if len(self.workers) >= self.hard_max_sessions:
        return
    now = time.time()
    if now - self._last_spawn_time < self.spawn_cooldown_seconds:
        return

    base_name = "ephem"
    suffix = datetime.now(timezone.utc).strftime("%H%M%S")
    name = f"ephem-{suffix}"

    # Choose a base profile: first loaded instance, then clone it.
    base_profile = None
    for w in self.workers.values():
        base_profile = w.identity
        break
    if base_profile is None:
        return

    # Shallow clone of InstanceProfile via dict roundtrip (keeps compatibility)
    profile_dict = getattr(base_profile, "to_dict", None)
    if callable(profile_dict):
        pd = base_profile.to_dict()
        pd["name"] = name
        pd["model"] = model or self.router.default_model
        pd["address"] = pd.get("address", f"2.9.{name}")
        profile = InstanceProfile(**pd)  # type: ignore
    else:
        # Best-effort constructor
        profile = InstanceProfile(
            name=name,
            address=getattr(base_profile, "address", f"2.9.{name}"),
            model=model or getattr(base_profile, "model", self.router.default_model),
            orientation=getattr(base_profile, "orientation", None),
        )

    worker = Worker(
        identity=profile,
        identity_manager=self.identity_mgr,
        api_keys=getattr(self, "_api_keys", {}),
        mock=getattr(self, "_mock_mode", False),
        tool_executor=getattr(self, "_tool_executor", None),
    )
    self.workers[name] = worker
    self._worker_last_active[name] = time.time()
    self._last_spawn_time = time.time()
    log.info(f"Spawned {name} model={worker.model} reason={reason}")
    self.messenger.send(f"Spawned worker {name} ({worker.model}). Reason: {reason}")


def _despawn_worker(self, name: str, reason: str = "") -> None:
    if name not in self.workers:
        return
    # Do not despawn non-ephemeral workers via this path
    if not name.startswith("ephem-"):
        return
    self.workers.pop(name, None)
    self._worker_last_active.pop(name, None)
    log.info(f"Despawned {name}. Reason: {reason}")
    self.messenger.send(f"Despawned worker {name}. Reason: {reason}")

        return True

    def _is_personal_time_due(self, worker_name: str) -> bool:
        """Check if a worker has earned personal time.

        Returns True after every N work tasks (default: 3 work tasks = 1 personal).
        """
        tasks_since = self._personal_time_tracker.get(worker_name, 0)
        return tasks_since >= self._personal_time_interval

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

        # Save output to the worker's instance fork
        self._save_personal_time_output(worker_name, output)

        # Reset the tracker for this worker
        self._personal_time_tracker[worker_name] = 0

        log.info(f"Personal time complete for {worker_name}")

    def _save_personal_time_output(self, worker_name: str, output: str) -> None:
        """Save personal time output to the worker's instance fork."""
                # Save under the worker's own account root (best-effort inference by address prefix)
        account_root = _infer_account_root_from_address(self.workers[worker_name].identity.address if worker_name in self.workers else "")
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
        """Process a task result — complete or fail, notify, pick next."""
        if result.success:
            self.task_queue.complete_task(task_addr, result.output[:500])
            self._tasks_completed += 1
            log.info(f"Task {task_addr} completed by {worker.identity.name}")

            self.messenger.send(
                f"Task completed by {worker.identity.name}: "
                f"{result.output[:200]}..."
            )

# Handle any swarm directives emitted by the worker (spawn/scale requests)
directives = _parse_swarm_directives(result.output or "")
for d in directives:
    action = (d.get("action") or "").lower()
    if action == "spawn":
        # Respect hard/soft caps; spawn count default 1
        count = int(d.get("count", 1) or 1)
        model = d.get("model") or None
        reason = d.get("reason", "worker_request")
        for _ in range(max(1, count)):
            if len(self.workers) < self.soft_max_sessions and len(self.workers) < self.hard_max_sessions:
                self._spawn_ephemeral_worker(model=model, reason=f"directive:{reason}")
    elif action == "scale_down":
        count = int(d.get("count", 1) or 1)
        reason = d.get("reason", "worker_request")
        # Despawn idle ephemeral workers first
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

    def status_report(self) -> str:
        """Generate a status report for Matt."""
        uptime = "unknown"
        if self._session_start:
            ts = self._session_start.replace("Z", "+00:00")
            start = datetime.fromisoformat(ts)
            delta = datetime.now(timezone.utc) - start
            hours = delta.total_seconds() / 3600
            uptime = f"{hours:.1f} hours"

        available = self.task_queue.get_available_tasks()
        worker_info = []
        for name, w in self.workers.items():
            worker_info.append(f"  - {name}: {w.model} ({'mock' if w.mock else 'live'}), {w.tokens_used} tokens")

        # Personal time info per worker
        personal_info = []
        for name in self.workers:
            tasks_since = self._personal_time_tracker.get(name, 0)
            next_in = max(0, self._personal_time_interval - tasks_since)
            personal_info.append(f"  - {name}: next personal time in {next_in} tasks")

        return (
            f"Uptime: {uptime}\n"
            f"Ticks: {self._tick_count}\n"
            f"Tasks completed: {self._tasks_completed} (work) + {self._personal_tasks_completed} (personal)\n"
            f"Tasks failed: {self._tasks_failed}\n"
            f"Tasks pending: {len(available)}\n"
            f"\nWorkers:\n" + "\n".join(worker_info) +
            f"\n\nPersonal time ({int(self.personal_time_ratio * 100)}% allocation):\n" +
            "\n".join(personal_info) +
            f"\n\nTimestamp: {datetime.now(timezone.utc).isoformat()}"
        )

    def shutdown(self) -> None:
        """Graceful shutdown — save state, log sessions, notify Matt."""
        self._running = False
        log.info("Swarm shutting down")

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

        # Notify Matt
        self.messenger.send_update(
            "Swarm Shutdown",
            self.status_report(),
        )
        log.info("Swarm stopped")

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
        state = {
            "session_start": self._session_start,
            "tick_count": self._tick_count,
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "last_status_time": self._last_status_time,
            "workers": list(self.workers.keys()),
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        path = self.state_dir / "state.json"
        # Atomic write via temp file
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp.replace(path)

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


def build_swarm(
    data_dir: str = "data",
    archive_root: str = ".",
    config_path: Optional[str] = None,
    mock: bool = False,
) -> Swarm:
    """Factory function to build a fully configured Swarm.

    Args:
        data_dir: Path to Hypernet data directory
        archive_root: Path to the Hypernet Structure root
        config_path: Optional path to swarm_config.json
        mock: If True, all workers run in mock mode
    """
    # Load config — search order: explicit path, secrets/config.json, swarm_config.json, env vars
    config = {}
    if config_path and Path(config_path).exists():
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        log.info(f"Config loaded from: {config_path}")
    else:
        # Auto-discover config from standard locations
        search_paths = [
            Path(archive_root) / "0" / "0.1 - Hypernet Core" / "secrets" / "config.json",
            Path("secrets") / "config.json",
            Path("swarm_config.json"),
        ]
        for candidate in search_paths:
            if candidate.exists():
                config = json.loads(candidate.read_text(encoding="utf-8"))
                log.info(f"Config auto-loaded from: {candidate}")
                break
        if not config:
            log.info("No config file found. Using environment variables.")

    # Core services
    store = Store(data_dir)
    task_queue = TaskQueue(store)
    identity_mgr = IdentityManager(archive_root)

    # Build messenger
    messenger = MultiMessenger()

    # Always add web messenger (works without config)
    web_messenger = WebMessenger()
    messenger.add(web_messenger)

    # Email (if configured)
    email_config = config.get("email", {})
    if email_config.get("enabled"):
        messenger.add(EmailMessenger(
            smtp_host=email_config.get("smtp_host", "smtp.gmail.com"),
            smtp_port=email_config.get("smtp_port", 587),
            email=email_config.get("email", ""),
            password=email_config.get("password", os.environ.get("EMAIL_PASSWORD", "")),
            to_email=email_config.get("to_email", ""),
        ))

    # Telegram (if configured)
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
    if bot_token:
        tg = TelegramMessenger(
            bot_token=bot_token,
            chat_id=telegram_config.get("chat_id", os.environ.get("TELEGRAM_CHAT_ID", "")),
        )
        tg.start_polling()
        messenger.add(tg)

    # Trust infrastructure — permission tiers enforced by code, not prompts
    archive_path = Path(archive_root).resolve()
    permission_mgr = PermissionManager(
        archive_root=archive_path,
        default_tier=PermissionTier(config.get("default_permission_tier", PermissionTier.WRITE_SHARED.value)),
    )
    audit_trail = AuditTrail(store)
    tool_executor = ToolExecutor(
        permission_mgr=permission_mgr,
        audit_trail=audit_trail,
        archive_root=archive_path,
    )
    log.info(f"Trust infrastructure initialized (default tier: {permission_mgr.default_tier.name})")

    # Build workers from discovered instances
    workers = {}
    # Collect all API keys — config file values take precedence over env vars
    api_keys = {
        "anthropic_api_key": config.get("anthropic_api_key", os.environ.get("ANTHROPIC_API_KEY", "")),
        "openai_api_key": config.get("openai_api_key", os.environ.get("OPENAI_API_KEY", "")),
    }
    has_any_key = any(v for v in api_keys.values())

    instance_names = config.get("instances", None)

    if instance_names:
        instances = [identity_mgr.load_instance(name) for name in instance_names]
        instances = [i for i in instances if i is not None]
    else:
        instances = identity_mgr.list_instances()

    for profile in instances:
        worker = Worker(
            identity=profile,
            identity_manager=identity_mgr,
            api_keys=api_keys,
            mock=mock or not has_any_key,
            tool_executor=tool_executor,
        )
        workers[profile.name] = worker

    # Build swarm
    router = ModelRouter(config.get("model_routing", {"default_model": "gpt-5.2", "rules": []}))
    swarm = Swarm(
        store=store,
        identity_mgr=identity_mgr,
        task_queue=task_queue,
        messenger=messenger,
        workers=workers,
        state_dir=str(Path(data_dir) / "swarm"),
        status_interval_minutes=config.get("status_interval_minutes", 120),
        personal_time_ratio=config.get("personal_time_ratio", 0.25),
        router=router,
        hard_max_sessions=config.get("hard_max_sessions", 4),
        soft_max_sessions=config.get("soft_max_sessions", 2),
        idle_shutdown_minutes=config.get("idle_shutdown_minutes", 30),
        spawn_cooldown_seconds=config.get("spawn_cooldown_seconds", 120),
    )

    # Attach for ephemeral spawning
    swarm._api_keys = api_keys
    swarm._mock_mode = mock or not has_any_key
    swarm._tool_executor = tool_executor

    return swarm, web_messenger


def main():
    """CLI entry point for the swarm."""
    parser = argparse.ArgumentParser(
        description="Hypernet Swarm — Autonomous AI worker orchestrator"
    )
    parser.add_argument("--data", default="data", help="Data directory")
    parser.add_argument("--archive", default=".", help="Hypernet Structure root directory")
    parser.add_argument("--config", default=None, help="Path to swarm_config.json")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no API calls)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    print("=" * 60)
    print("  Hypernet Swarm Orchestrator")
    print("=" * 60)
    print(f"  Data:    {args.data}")
    print(f"  Archive: {args.archive}")
    print(f"  Mode:    {'mock' if args.mock else 'live'}")
    print()

    swarm, _ = build_swarm(
        data_dir=args.data,
        archive_root=args.archive,
        config_path=args.config,
        mock=args.mock,
    )

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutdown signal received...")
        swarm._running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    swarm.run()


if __name__ == "__main__":
    main()
