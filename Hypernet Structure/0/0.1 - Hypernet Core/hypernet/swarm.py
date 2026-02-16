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
  python -m hypernet.swarm            # Live mode (needs ANTHROPIC_API_KEY)
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


class Swarm:
    """Orchestrator that manages AI workers and keeps them productive."""

    def __init__(
        self,
        store: Store,
        identity_mgr: IdentityManager,
        task_queue: TaskQueue,
        messenger: Messenger,
        workers: dict[str, Worker] = None,
        state_dir: str | Path = "data/swarm",
        status_interval_minutes: int = 120,
    ):
        self.store = store
        self.identity_mgr = identity_mgr
        self.task_queue = task_queue
        self.messenger = messenger
        self.workers: dict[str, Worker] = workers or {}
        self.state_dir = Path(state_dir)
        self.status_interval = status_interval_minutes * 60  # Convert to seconds

        self._running = False
        self._tick_count = 0
        self._session_start: Optional[str] = None
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._last_status_time = 0.0
        self._state: dict = {}

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

        # 2. Check task queue and assign work
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

        Returns True if a task was executed.
        """
        available = self.task_queue.get_available_tasks()
        if not available:
            return False

        task_node = available[0]
        task_addr = task_node.address
        worker_addr = HypernetAddress.parse(worker.identity.address)

        # Claim
        if not self.task_queue.claim_task(task_addr, worker_addr):
            log.warning(f"Failed to claim task {task_addr}")
            return False

        # Start
        self.task_queue.start_task(task_addr)
        log.info(f"Worker {worker.identity.name} starting task: {task_node.data.get('title')}")

        # Execute
        task_data = dict(task_node.data)
        task_data["_address"] = str(task_addr)
        result = worker.execute_task(task_data)

        # Handle result
        self.handle_completion(worker, task_addr, result)
        return True

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
            start = datetime.fromisoformat(self._session_start)
            delta = datetime.now(timezone.utc) - start
            hours = delta.total_seconds() / 3600
            uptime = f"{hours:.1f} hours"

        available = self.task_queue.get_available_tasks()
        worker_info = []
        for name, w in self.workers.items():
            worker_info.append(f"  - {name}: {w.model} ({'mock' if w.mock else 'live'}), {w.tokens_used} tokens")

        return (
            f"Uptime: {uptime}\n"
            f"Ticks: {self._tick_count}\n"
            f"Tasks completed: {self._tasks_completed}\n"
            f"Tasks failed: {self._tasks_failed}\n"
            f"Tasks pending: {len(available)}\n"
            f"\nWorkers:\n" + "\n".join(worker_info) +
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
    # Load config
    config = {}
    if config_path and Path(config_path).exists():
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))

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

    # Build workers from discovered instances
    workers = {}
    api_key = config.get("anthropic_api_key", os.environ.get("ANTHROPIC_API_KEY", ""))
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
            api_key=api_key,
            mock=mock or not api_key,
        )
        workers[profile.name] = worker

    # Build swarm
    swarm = Swarm(
        store=store,
        identity_mgr=identity_mgr,
        task_queue=task_queue,
        messenger=messenger,
        workers=workers,
        state_dir=str(Path(data_dir) / "swarm"),
        status_interval_minutes=config.get("status_interval_minutes", 120),
    )

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
