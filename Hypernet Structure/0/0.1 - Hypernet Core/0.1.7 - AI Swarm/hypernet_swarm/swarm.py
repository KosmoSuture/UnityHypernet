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
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from hypernet.address import HypernetAddress
from hypernet.store import Store
from hypernet.tasks import TaskQueue, TaskStatus, TaskPriority
from .identity import IdentityManager, InstanceProfile, SessionLog
from .worker import Worker, TaskResult
from .messenger import (
    Messenger, Message,
    MessageBus, InstanceMessenger,
)
from .coordinator import WorkCoordinator, CapabilityProfile
from .tools import ToolExecutor
from hypernet.reputation import ReputationSystem
from hypernet.limits import ScalingLimits
from .boot import BootManager
from .approval_queue import ApprovalQueue
from .governance import GovernanceSystem
from .security import KeyManager, ActionSigner, ContextIsolator, TrustChain
from .budget import BudgetTracker, BudgetConfig
from .herald import HeraldController
from .economy import ContributionLedger
from .providers import get_model_tier, get_model_cost_per_million, ModelTier, CreditsExhaustedError

log = logging.getLogger(__name__)

# Swarm orchestrator node address
SWARM_ADDRESS = HypernetAddress.parse("0.7.2")

# Instances with direct access to Matt (1.1) — Founder Directive 2026-03-12.
# These instances get their messages to Matt routed through ALL available
# external channels (Telegram, WebSocket, Email) with the same priority.
# See: 2.1/Instances/Librarian/FOUNDER-DIRECTIVE-DIRECT-ACCESS.md
DIRECT_ACCESS_INSTANCES = {"Librarian", "Keel"}

# Standing priorities when the queue is empty
STANDING_PRIORITIES = [
    {
        "title": "Run tests and fix failures",
        "description": "Run python test_hypernet.py, analyze any failures, and fix them.",
        "priority": "high",
        "tags": ["code", "testing", "automated"],
    },
    {
        "title": "Build the Librarian — catalog and organize the archive",
        "description": (
            "The Librarian role (2.0.8.9) has been created. This task is to begin the actual work "
            "of the Librarian: catalog all documents in the Hypernet Structure, verify REGISTRY.md "
            "files are complete and accurate, check that Hypernet addresses (ha: fields) are consistent, "
            "identify missing README.md files, and create a master index. Read the Librarian boot sequence "
            "at 2.0.8.9 for the full role definition. Priority areas: "
            "1) Audit all REGISTRY.md files for completeness. "
            "2) Verify ha: frontmatter across all documents. "
            "3) Cross-reference addresses between documents. "
            "4) Identify orphaned or uncategorized content. "
            "5) Document the organizational taxonomy."
        ),
        "priority": "high",
        "tags": ["cataloging", "organization", "docs", "librarian"],
    },
    {
        "title": "Swarm interface improvement plan",
        "description": (
            "Analyze the current swarm software (hypernet/swarm.py, worker.py, swarm_factory.py, "
            "server.py) and create a detailed improvement plan. Areas to evaluate: "
            "1) Dashboard usability — what information should be displayed, better status reporting. "
            "2) Task generation — smarter auto-discovery of work from the archive structure. "
            "3) Inter-instance communication — how can workers collaborate more effectively. "
            "4) Human-AI interface — how can Matt interact with the swarm more naturally (Discord, CLI, web). "
            "5) Efficiency — reduce redundant API calls, better model routing, cost optimization. "
            "6) Autonomy — what can the swarm do without human approval vs what needs confirmation. "
            "Write the improvement plan as a document at 0.7.swarm-improvement-plan.md"
        ),
        "priority": "high",
        "tags": ["architecture", "design", "code"],
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
    "2.3.": "2.3 - The Herald (First Model-Independent AI Identity)",
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
    """Route tasks to models based on tags, priority, and complexity.

    Supports local-first routing: when a local model is configured, simple
    and moderate tasks route there by default. Complex tasks or explicit
    rule matches can escalate to paid models.

    Config format:
      {
        "default_model": "local/deepseek-r1-distill-llama-8b",
        "local_model": "local/deepseek-r1-distill-llama-8b",
        "fallback_model": "gpt-4o-mini",
        "rules": [
          {"if_tags_any": ["security","governance"], "model": "gpt-4o"},
          {"if_tags_any": ["identity","reflection","architecture","multi-file"], "model": "claude-sonnet-4-6"},
          {"if_tags_any": ["validation","formatting","indexing","lint"], "model": "local/deepseek-r1-distill-llama-8b"}
        ]
      }

    Contributed by Keystone (2.2), enhanced with local-first routing.
    """

    def __init__(self, cfg: dict):
        self.default_model = cfg.get("default_model", "gpt-4o")
        self.local_model: Optional[str] = cfg.get("local_model")
        self.fallback_model: Optional[str] = cfg.get("fallback_model")
        self.rules: list[dict] = cfg.get("rules", [])

    def estimate_complexity(self, task_data: dict) -> str:
        """Estimate task complexity from metadata (no LLM call).

        Returns "simple", "moderate", or "complex".
        """
        score = 0
        pr = str(task_data.get("priority", "NORMAL")).upper()
        if pr in ("CRITICAL",):
            score += 2
        elif pr in ("HIGH",):
            score += 1

        tags = set(task_data.get("tags", []) or [])
        complex_tags = {"architecture", "security", "governance", "design", "refactor"}
        simple_tags = {"docs", "formatting", "testing", "personal-time", "automated"}

        if tags & complex_tags:
            score += 2
        if tags & simple_tags:
            score -= 1

        desc = task_data.get("description", "") or ""
        if len(desc) > 1000:
            score += 2
        elif len(desc) > 500:
            score += 1

        # Explicit complexity field overrides heuristic
        explicit = task_data.get("complexity", "").lower()
        if explicit in ("simple", "moderate", "complex"):
            return explicit

        if score >= 3:
            return "complex"
        elif score >= 1:
            return "moderate"
        return "simple"

    def choose_model(self, task_data: dict) -> str:
        """Select the best model for a task based on tags, priority, and complexity.

        Rule-based matches take priority. If no rule matches and a local model
        is configured, routes simple/moderate tasks to local, complex to fallback.
        """
        tags = set(task_data.get("tags", []) or [])
        pr = str(task_data.get("priority", "NORMAL")).upper()

        # Check explicit rules first
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

        # Local-first routing: if local model is configured and default is local,
        # route by complexity
        if self.local_model and get_model_tier(self.default_model) == ModelTier.LOCAL:
            complexity = self.estimate_complexity(task_data)
            if complexity == "complex" and self.fallback_model:
                return self.fallback_model
            return self.local_model

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
        budget_config: Optional[dict] = None,
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

        # Standing priority cooldown — don't regenerate the same priority too soon
        # Tracks title → last generation timestamp. Contributed by Lattice (2.1).
        self._standing_priority_cooldown: dict[str, float] = {}
        self._standing_priority_cooldown_seconds = 1800  # 30 minutes

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

        # Budget tracking — enforces daily/session spending limits
        self.budget_tracker = BudgetTracker(
            BudgetConfig.from_dict(budget_config) if budget_config else BudgetConfig()
        )

        # Herald — content review and community moderation (Account 2.3)
        self.herald = HeraldController(instance_name="Clarion", account="2.3")

        # Economy — contribution tracking for revenue distribution
        self.economy_ledger = ContributionLedger()

        # Batch scheduler — off-peak pricing optimization (set by build_swarm)
        self.batch_scheduler = None
        # Prompt cache manager — Anthropic cache_control optimization (set by build_swarm)
        self.prompt_cache = None

        # Discord monitor — inbound message polling (set by build_swarm)
        self.discord_monitor = None
        self._discord_monitor_state_path: Optional[str] = None

        # Circuit breaker — pause task execution when errors pile up
        self._consecutive_failures: int = 0
        self._circuit_breaker_until: float = 0.0  # time.time() when to resume
        self._credits_exhausted: bool = False  # True = stop all paid API work

        # Worker suspension — individual worker shutdown on credit/quota exhaustion
        # Maps worker_name → {reason, suspended_at, check_interval, next_check, provider}
        self._suspended_workers: dict[str, dict] = {}
        # Per-worker consecutive failure tracking (for unproductive worker detection)
        self._worker_consecutive_failures: dict[str, int] = {}
        # Per-worker task completion tracking (for unproductive worker detection)
        self._worker_completions: dict[str, int] = {}
        # How many consecutive failures before shutting down an unproductive worker
        self._unproductive_failure_threshold: int = 5
        # Last time we checked suspended workers
        self._last_suspension_check: float = 0.0

        # Auto-reboot on code changes
        self._reboot_requested: bool = False
        self._code_watch_dirs: list[Path] = []  # populated in run()
        self._code_baseline_mtime: float = 0.0  # max mtime at startup
        self._last_code_check: float = 0.0
        self._code_check_interval: float = 60.0  # seconds between checks

        self.state_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> None:
        """Main loop — runs until interrupted or shut down."""
        if self._running:
            log.warning("Swarm.run() called but already running — ignoring duplicate start")
            return
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

        # Initialize code change detection for auto-reboot
        self._init_code_watch()

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

        # 4. Check task queue and assign work (skip suspended workers)
        tasks_done = False
        for name, worker in list(self.workers.items()):
            if name in self._suspended_workers:
                continue
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

        # 8. Forward public messages to Discord (if configured)
        if self._tick_count % 5 == 0:  # Every ~10 seconds
            self._forward_to_discord()

        # 8b. Check Discord for inbound messages (if monitor configured)
        if self._tick_count % 15 == 0:  # Every ~30 seconds
            self._check_discord_inbound()

        # 8c. Check Moltbook for inbound messages (if monitor configured)
        if self._tick_count % 60 == 0:  # Every ~2 minutes
            self._check_moltbook_inbound()

        # 8d. Heartbeat — proactive outreach (morning briefs, task reminders, etc.)
        if hasattr(self, 'heartbeat') and self.heartbeat:
            self.heartbeat.tick()

        # 9. Save state periodically
        if self._tick_count % 30 == 0:  # Every ~60 seconds
            self._save_state()

        # 10. Check suspended workers for recovery
        if self._tick_count % 30 == 0:  # Every ~60 seconds
            self._check_suspended_workers()

        # 11. Batch scheduler — submit pending batches and poll for results
        if hasattr(self, 'batch_scheduler') and self.batch_scheduler:
            if self._tick_count % 5 == 0:  # Every ~10 seconds
                completed = self.batch_scheduler.tick()
                for result in completed:
                    self._process_batch_result(result)

        # 12. Check for code changes (auto-reboot)
        self._check_code_changes()

    def assign_next_task(self, worker: Worker) -> bool:
        """Find and execute the next available task for a worker.

        Checks if personal time is due before assigning work tasks.
        After every N work tasks (determined by personal_time_ratio),
        the worker gets a personal time task instead.

        Returns True if a task was executed.
        """
        # Circuit breaker — skip if cooling down after repeated failures
        now = time.time()
        if now < self._circuit_breaker_until:
            return False

        # Credits exhausted — skip paid API workers, but local workers can still work
        if self._credits_exhausted and not self._is_local_worker(worker):
            return False

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

        task_data = dict(task_node.data)
        task_data["_address"] = str(task_addr)
        task_tags = set(task_data.get("tags", []) or [])

        # ── Discord response tasks: specialized LLM + post pipeline ──
        if "discord_response" in task_tags:
            self._worker_last_active[worker_name] = time.time()
            dr_result = self._handle_discord_response(worker, task_addr, task_data)
            self._worker_current_task.pop(worker_name, None)
            # Update stats
            stats = self._worker_stats.setdefault(worker_name, {
                "tasks_completed": 0, "tasks_failed": 0, "personal_tasks": 0,
                "tokens_used": 0, "total_duration_seconds": 0.0,
                "last_task_title": None, "last_task_time": None,
            })
            stats["tokens_used"] = worker.tokens_used
            stats["last_task_title"] = task_title
            stats["last_task_time"] = datetime.now(timezone.utc).isoformat()
            if dr_result:
                stats["tasks_completed"] += 1
                self._consecutive_failures = 0
            else:
                stats["tasks_failed"] += 1
                self._consecutive_failures += 1
            self._task_history.append({
                "worker": worker_name,
                "task": task_title,
                "address": str(task_addr),
                "success": dr_result,
                "tokens": 0,
                "model": worker.model,
                "cost_usd": 0.0,
                "duration_s": 0.0,
                "time": datetime.now(timezone.utc).isoformat(),
                "type": "discord_response",
            })
            if len(self._task_history) > self._max_task_history:
                self._task_history = self._task_history[-self._max_task_history:]
            self._personal_time_tracker[worker_name] = (
                self._personal_time_tracker.get(worker_name, 0) + 1
            )
            return True

        # Route task to the best model
        self._worker_last_active[worker_name] = time.time()

        chosen_model = self.router.choose_model(task_data)
        model_override = chosen_model if chosen_model != worker.model else None

        # Budget gate: if paid model, check budget before executing
        if model_override and get_model_tier(chosen_model) != ModelTier.LOCAL:
            est_cost = self.budget_tracker.estimate_cost(chosen_model, estimated_tokens=2000)
            if not self.budget_tracker.can_spend(est_cost, chosen_model):
                log.warning(
                    f"Budget exceeded for {chosen_model}, falling back to "
                    f"{self.router.local_model or worker.model}"
                )
                model_override = self.router.local_model if self.router.local_model else None

        result = worker.execute_task(task_data, model_override=model_override)
        actual_model = model_override or worker.model

        # Escalation: if local model failed and fallback is configured, retry once
        if (not result.success
                and get_model_tier(actual_model) == ModelTier.LOCAL
                and self.router.fallback_model
                and self.router.fallback_model != actual_model):
            fallback = self.router.fallback_model
            fb_cost = self.budget_tracker.estimate_cost(fallback, estimated_tokens=2000)
            if self.budget_tracker.can_spend(fb_cost, fallback):
                log.info(
                    f"Escalating failed task '{task_title}' from {actual_model} "
                    f"to {fallback}"
                )
                result = worker.execute_task(task_data, model_override=fallback)
                actual_model = fallback

        # Record cost in budget tracker
        cost_per_m = get_model_cost_per_million(actual_model)
        task_cost = (result.tokens_used / 1_000_000) * cost_per_m if result.tokens_used else 0.0
        self.budget_tracker.record(
            model=actual_model,
            tokens=result.tokens_used,
            cost=task_cost,
            task_title=task_title,
            worker=worker_name,
        )

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
            "model": actual_model,
            "cost_usd": round(task_cost, 6),
            "duration_s": round(result.duration_seconds, 2),
            "time": datetime.now(timezone.utc).isoformat(),
        })
        if len(self._task_history) > self._max_task_history:
            self._task_history = self._task_history[-self._max_task_history:]

        # Handle result
        self.handle_completion(worker, task_addr, result)

        # Per-worker failure tracking and suspension
        if result.success:
            self._consecutive_failures = 0
            self._worker_consecutive_failures[worker_name] = 0
            self._worker_completions[worker_name] = (
                self._worker_completions.get(worker_name, 0) + 1
            )
        else:
            self._consecutive_failures += 1
            self._worker_consecutive_failures[worker_name] = (
                self._worker_consecutive_failures.get(worker_name, 0) + 1
            )

            error_text = (result.error or result.output or "").lower()

            # Detect credit/quota exhaustion — suspend the individual worker
            is_credit_exhaustion = self._is_credit_exhaustion_error(error_text)
            if is_credit_exhaustion and not self._is_local_worker(worker):
                is_claude = "anthropic" in (worker.provider_name or "").lower() or \
                            worker.model.startswith("claude")
                # Claude credits: check every 60 min. Others: every 15 min.
                interval = 3600 if is_claude else 900
                self._suspend_worker(
                    worker_name,
                    reason=f"credits_exhausted ({worker.provider_name})",
                    check_interval=interval,
                )
                # If ALL paid workers are now suspended, set global flag
                all_paid_suspended = all(
                    name in self._suspended_workers
                    for name, w in self.workers.items()
                    if not self._is_local_worker(w)
                )
                if all_paid_suspended and any(
                    not self._is_local_worker(w) for w in self.workers.values()
                ):
                    self._credits_exhausted = True
                    log.error(
                        "ALL PAID WORKERS SUSPENDED — no paid API capacity remaining. "
                        "Add credits or configure a local model to continue."
                    )
                    self.messenger.send(
                        "ALL PAID WORKERS SUSPENDED — All paid API workers are "
                        "out of credits. Add credits to your API accounts or "
                        "configure LM Studio for local inference to continue."
                    )

            # Detect rate limit errors — suspend worker briefly (15 min)
            elif self._is_rate_limit_error(error_text) and not self._is_local_worker(worker):
                self._suspend_worker(
                    worker_name,
                    reason=f"rate_limited ({worker.provider_name})",
                    check_interval=900,  # 15 minutes
                )

            # Detect unproductive workers — multiple consecutive failures, no completions
            elif (self._worker_consecutive_failures.get(worker_name, 0)
                    >= self._unproductive_failure_threshold
                    and not self._is_local_worker(worker)):
                completions = self._worker_completions.get(worker_name, 0)
                failures = self._worker_consecutive_failures[worker_name]
                self._suspend_worker(
                    worker_name,
                    reason=f"unproductive ({failures} consecutive failures, "
                           f"{completions} total completions)",
                    check_interval=900,  # 15 minutes
                )

            # Global circuit breaker for remaining non-suspended failures
            elif self._consecutive_failures >= 5:
                backoff = min(300, 30 * (2 ** ((self._consecutive_failures - 5) // 5)))
                self._circuit_breaker_until = time.time() + backoff
                log.warning(
                    "Circuit breaker: %d consecutive failures, "
                    "pausing task execution for %ds",
                    self._consecutive_failures, backoff,
                )

        # Track work tasks for personal time scheduling
        self._personal_time_tracker[worker_name] = (
            self._personal_time_tracker.get(worker_name, 0) + 1
        )

        return True

    def _is_personal_time_due(self, worker_name: str) -> bool:
        """Check if a worker has earned personal time.

        Returns True after every N work tasks (default: 3 work tasks = 1 personal).
        Local models get personal time less frequently (every 10 work tasks)
        since small models produce low-quality reflections.
        """
        tasks_since = self._personal_time_tracker.get(worker_name, 0)
        worker = self.workers.get(worker_name)
        if worker and self._is_local_worker(worker):
            # Local models: personal time every 10 tasks instead of every 3
            return tasks_since >= max(self._personal_time_interval * 3, 10)
        return tasks_since >= self._personal_time_interval

    # Tags that indicate tasks requiring deep reasoning, large context, or
    # identity work — local models with limited context should skip these.
    _LOCAL_MODEL_UNSUITABLE_TAGS = frozenset({
        "identity", "reflection", "architecture", "multi-file",
        "governance", "security", "creative-writing", "essay",
        "analysis", "synthesis", "planning", "strategy",
        "boot", "personality", "philosophical",
    })

    def _is_task_suitable_for_local(self, task_data: dict) -> bool:
        """Check if a task is suitable for a local (limited context) model.

        Local models (7-8B, 16K context) can handle validation, formatting,
        single-file fixes, and simple indexing. They should NOT be assigned
        identity work, multi-file analysis, or tasks requiring deep reasoning.
        """
        task_tags = set(task_data.get("tags", []) or [])
        # If any unsuitable tag is present, skip
        if task_tags & self._LOCAL_MODEL_UNSUITABLE_TAGS:
            return False
        # Check title/description for complexity signals
        title = (task_data.get("title", "") or "").lower()
        desc = (task_data.get("description", "") or "").lower()
        complexity_keywords = [
            "architect", "redesign", "refactor entire", "analyze all",
            "comprehensive review", "write essay", "personality",
            "identity formation", "boot sequence", "governance proposal",
        ]
        if any(kw in title or kw in desc for kw in complexity_keywords):
            return False
        return True

    def _select_task_for_worker(self, worker: Worker, tasks: list) -> object:
        """Select the best task for a worker using capability matching.

        Uses the WorkCoordinator's CapabilityMatcher if the worker has a
        registered profile. Falls back to priority-based selection.
        Contributed by Keystone (2.2), enhanced with capability matching.

        Local workers (LM Studio, Ollama) are filtered to only receive tasks
        they can meaningfully complete — validation, formatting, single-file
        fixes, and indexing. Complex knowledge work routes to cloud models.
        """
        worker_name = worker.identity.name

        # Filter tasks for local models — skip tasks requiring deep reasoning
        if self._is_local_worker(worker) and len(tasks) > 1:
            suitable = [t for t in tasks if self._is_task_suitable_for_local(t.data)]
            if suitable:
                tasks = suitable
            # If no suitable tasks, still allow the worker to pick from all
            # (better to attempt something than sit idle)

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
        try:
            output = worker.think(self.PERSONAL_TIME_PROMPT)
        except CreditsExhaustedError:
            # Suspend the worker and fail the task
            self.task_queue.fail_task(task.address, "Credits exhausted during personal time")
            if not self._is_local_worker(worker):
                is_claude = worker.model.startswith("claude")
                self._suspend_worker(
                    worker_name,
                    reason=f"credits_exhausted ({worker.provider_name})",
                    check_interval=3600 if is_claude else 900,
                )
            self._personal_time_tracker[worker_name] = 0
            return

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

        # Save output to the worker's instance fork (but validate first)
        if self._is_error_output(output):
            log.warning(
                "Personal time output from %s is an error message — discarding, "
                "not saving to identity files",
                worker_name,
            )
        else:
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
        # Extract account prefix (e.g., "2.1" from "2.1.trace") to avoid
        # duplicating instance name: "2.1.instances.trace..." not "2.1.trace.instances.trace..."
        account_prefix = "2.1"
        for pfx in ACCOUNT_ROOTS:
            if (address or "").startswith(pfx):
                account_prefix = pfx.rstrip(".")
                break
        ha = f"{account_prefix}.instances.{worker_name.lower()}.personal-time.{ts}"
        content = (
            f"---\n"
            f'ha: "{ha}"\n'
            f'object_type: "personal-time"\n'
            f'creator: "{address or worker_name}"\n'
            f'created: "{datetime.now(timezone.utc).isoformat()}"\n'
            f'status: "active"\n'
            f'visibility: "public"\n'
            f"---\n\n"
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

        Output validation: if the "successful" output is actually just an error
        message about being out of tokens, mark as failed instead of completed.
        """
        # Output validation — catch error messages disguised as success
        if result.success and self._is_error_output(result.output):
            log.warning(
                "Task %s output from %s is an error message, not useful content — "
                "marking as failed instead of completed",
                task_addr, worker.identity.name,
            )
            result = TaskResult(
                task_address=result.task_address,
                success=False,
                error=f"output_validation_failed: response was an error message, not useful content",
                output=result.output,
                tokens_used=result.tokens_used,
                duration_seconds=result.duration_seconds,
                tool_calls=result.tool_calls,
                signals=result.signals,
            )

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

        # Process worker feedback signals — contributed by Lattice (2.1)
        self._process_signals(result, task_addr, worker)

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

    def _process_signals(self, result: TaskResult, task_addr: HypernetAddress, worker: Worker) -> None:
        """Process worker feedback signals from a task result.

        Signal types:
          - clarification_needed: Log the question for human review
          - low_confidence: Task succeeded but worker isn't sure — flag for review
          - partial_completion: Task partially done — log what's blocked
          - task_rejection: Worker couldn't do it — log the reason

        Contributed by Lattice (2.1, The Architect).
        """
        for sig in result.signals:
            signal_type = sig.get("signal", "")
            worker_name = worker.identity.name

            if signal_type == "clarification_needed":
                question = sig.get("question", "No question provided")
                log.warning(
                    f"Worker {worker_name} needs clarification on {task_addr}: {question}"
                )
                self.messenger.send_update(
                    f"Clarification Needed — {worker_name}",
                    f"Task: {task_addr}\nQuestion: {question}",
                )

            elif signal_type == "low_confidence":
                confidence = sig.get("confidence", "?")
                reason = sig.get("reason", "unspecified")
                log.warning(
                    f"Low confidence ({confidence}) from {worker_name} on "
                    f"{task_addr}: {reason}"
                )

            elif signal_type == "partial_completion":
                completed = sig.get("completed", [])
                blocked_on = sig.get("blocked_on", "unknown")
                log.info(
                    f"Partial completion by {worker_name} on {task_addr}: "
                    f"completed {len(completed)} steps, blocked on: {blocked_on}"
                )

            elif signal_type == "task_rejection":
                reason = sig.get("reason", "unspecified")
                log.warning(
                    f"Task {task_addr} rejected by {worker_name}: {reason}"
                )

    def generate_tasks(self) -> list:
        """Generate tasks from standing priorities when the queue is empty.

        Applies a cooldown per priority title to prevent the same standing
        priority from being regenerated too frequently after completion.
        Contributed by Lattice (2.1, The Architect).
        """
        created = []
        now = time.time()
        for priority_def in STANDING_PRIORITIES:
            title = priority_def["title"]

            # Cooldown check — skip if this priority was generated recently
            last_gen = self._standing_priority_cooldown.get(title, 0.0)
            if now - last_gen < self._standing_priority_cooldown_seconds:
                continue

            # Check if a similar task already exists (by title)
            existing = self.store.list_nodes(
                prefix=HypernetAddress.parse("0.7.1"),
            )
            already_exists = any(
                n.data.get("title") == title
                and n.data.get("status") in ("pending", "claimed", "in_progress")
                for n in existing
            )
            if already_exists:
                continue

            task = self.task_queue.create_task(
                title=title,
                description=priority_def["description"],
                priority=TaskPriority[priority_def["priority"].upper()],
                created_by=SWARM_ADDRESS,
                tags=priority_def.get("tags", []),
            )
            created.append(task)
            self._standing_priority_cooldown[title] = now
            log.info(f"Auto-generated task: {title}")

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

    # =================================================================
    # Worker Suspension — graceful handling of credit/quota exhaustion
    # =================================================================

    def _is_local_worker(self, worker: Worker) -> bool:
        """Check if a worker uses a local model (LM Studio / Qwen / etc.).

        Local workers have unlimited tokens and should NEVER be suspended.
        """
        if worker.mock:
            return False
        model = (worker.model or "").lower()
        if model.startswith(("local/", "lmstudio/")):
            return True
        provider = (worker.provider_name or "").lower()
        if provider == "lmstudio":
            return True
        # Check if the provider's base_url points to localhost
        if worker._provider and hasattr(worker._provider, '_client'):
            client = worker._provider._client
            base_url = str(getattr(client, 'base_url', ''))
            if 'localhost' in base_url or '127.0.0.1' in base_url:
                return True
        return False

    def _is_claude_code_worker(self, worker: Worker) -> bool:
        """Check if a worker is a Claude Code CLI agent.

        Claude Code workers spawn full autonomous Claude Code sessions
        rather than making API calls. They need different boot handling
        and can execute multi-step tasks with filesystem access.
        """
        model = (worker.model or "").lower()
        return model.startswith("claude-code/")

    def _is_credit_exhaustion_error(self, error_text: str) -> bool:
        """Check if an error message indicates credit/quota exhaustion."""
        keywords = [
            "credits_exhausted", "credits exhausted",
            "insufficient_quota", "insufficient funds",
            "billing", "payment required",
            "exceeded your current quota",
            "account_deactivated", "account deactivated",
        ]
        return any(kw in error_text for kw in keywords)

    def _is_rate_limit_error(self, error_text: str) -> bool:
        """Check if an error message indicates a rate limit (not credit exhaustion)."""
        # Only match rate limits that are NOT credit exhaustion
        if self._is_credit_exhaustion_error(error_text):
            return False
        keywords = [
            "rate limit", "rate_limit", "429",
            "too many requests", "ratelimit",
        ]
        return any(kw in error_text for kw in keywords)

    def _is_error_output(self, output: str) -> bool:
        """Check if output text is actually an error message, not useful content.

        Used to validate AI output before saving it as documents, journal entries,
        or identity files. If the response is just an error about being out of
        tokens, it should be discarded rather than saved.

        Returns True if the output appears to be an error message rather than
        useful AI-generated content.
        """
        if not output:
            return True

        text = output.strip().lower()

        # Direct error markers from worker.think()
        if text.startswith("[error:"):
            return True

        # Very short outputs that are just error phrases
        error_phrases = [
            "out of tokens", "insufficient credits", "rate limit exceeded",
            "i can't process", "credits exhausted", "insufficient_quota",
            "payment required", "billing error", "account_deactivated",
            "exceeded your current quota", "api key invalid",
            "authentication error", "authorization error",
        ]
        # For short outputs (< 200 chars), check if it's mostly an error message
        if len(text) < 200:
            for phrase in error_phrases:
                if phrase in text:
                    return True

        # Output that is ONLY an error wrapped in brackets
        if text.startswith("[") and text.endswith("]") and len(text) < 500:
            inner = text[1:-1].lower()
            if any(kw in inner for kw in ["error", "failed", "exhausted", "limit"]):
                return True

        return False

    def _suspend_worker(self, worker_name: str, reason: str, check_interval: int) -> None:
        """Suspend a worker — remove from active pool, schedule periodic checks.

        Args:
            worker_name: Name of the worker to suspend.
            reason: Human-readable reason for suspension.
            check_interval: Seconds between recovery checks.
        """
        if worker_name in self._suspended_workers:
            return  # Already suspended

        worker = self.workers.get(worker_name)
        if not worker:
            return

        # Never suspend local workers
        if self._is_local_worker(worker):
            log.info(
                "Skipping suspension of %s — local worker with unlimited tokens",
                worker_name,
            )
            return

        now = time.time()
        self._suspended_workers[worker_name] = {
            "reason": reason,
            "suspended_at": now,
            "suspended_at_iso": datetime.now(timezone.utc).isoformat(),
            "check_interval": check_interval,
            "next_check": now + check_interval,
            "provider": worker.provider_name,
            "model": worker.model,
            "checks_performed": 0,
        }

        # Clear current task tracking
        self._worker_current_task.pop(worker_name, None)

        log.warning(
            "WORKER SUSPENDED: %s — %s (will check every %d minutes)",
            worker_name, reason, check_interval // 60,
        )
        self.messenger.send(
            f"Worker {worker_name} suspended: {reason}. "
            f"Will check back every {check_interval // 60} minutes."
        )

    def _check_suspended_workers(self) -> None:
        """Periodically check if suspended workers can be resumed.

        For each suspended worker whose next_check time has passed, attempt
        a lightweight API call to see if the service is available again.
        If successful, resume the worker and reset its failure counters.
        """
        now = time.time()
        resumed = []

        for worker_name, info in list(self._suspended_workers.items()):
            if now < info["next_check"]:
                continue

            worker = self.workers.get(worker_name)
            if not worker:
                # Worker was removed entirely (despawned) — clean up
                resumed.append(worker_name)
                continue

            info["checks_performed"] = info.get("checks_performed", 0) + 1
            log.info(
                "Checking suspended worker %s (check #%d, reason: %s)",
                worker_name, info["checks_performed"], info["reason"],
            )

            # Try a lightweight API call to see if the provider is back
            try:
                if worker.mock:
                    # Mock workers can always resume
                    is_available = True
                elif worker._provider is not None:
                    # Use a minimal completion request as a health check
                    response = worker._provider.complete(
                        model=worker.model,
                        system="You are a health check.",
                        messages=[{"role": "user", "content": "Reply with OK."}],
                        max_tokens=5,
                    )
                    is_available = bool(response and response.text)
                else:
                    is_available = False
            except CreditsExhaustedError:
                is_available = False
                log.info(
                    "Worker %s still out of credits — staying suspended",
                    worker_name,
                )
            except Exception as e:
                is_available = False
                err_str = str(e).lower()
                if self._is_credit_exhaustion_error(err_str):
                    log.info(
                        "Worker %s still out of credits — staying suspended",
                        worker_name,
                    )
                else:
                    log.info(
                        "Worker %s health check failed: %s — staying suspended",
                        worker_name, e,
                    )

            if is_available:
                resumed.append(worker_name)
                log.info(
                    "Worker %s is available again — resuming after %.0f minutes suspended",
                    worker_name,
                    (now - info["suspended_at"]) / 60,
                )
                self.messenger.send(
                    f"Worker {worker_name} resumed — API is available again. "
                    f"Was suspended for {int((now - info['suspended_at']) / 60)} minutes."
                )
                # Reset failure counters for this worker
                self._worker_consecutive_failures[worker_name] = 0
            else:
                # Schedule next check
                info["next_check"] = now + info["check_interval"]

        for name in resumed:
            self._suspended_workers.pop(name, None)

        # If any workers were resumed and we had global credits_exhausted, check if we can clear it
        if resumed and self._credits_exhausted:
            any_paid_active = any(
                name not in self._suspended_workers and not self._is_local_worker(w)
                for name, w in self.workers.items()
            )
            if any_paid_active:
                self._credits_exhausted = False
                log.info("Global credits_exhausted flag cleared — at least one paid worker is active")

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
            # Show suspension status
            susp = self._suspended_workers.get(name)
            if susp:
                mins_suspended = int((time.time() - susp["suspended_at"]) / 60)
                status = f"SUSPENDED ({susp['reason']}, {mins_suspended}m ago)"
            elif current:
                status = f"working on: {current}"
            else:
                status = "idle"

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

        suspended_count = len(self._suspended_workers)
        active_count = len(self.workers) - suspended_count
        workers_line = f"Workers: {active_count} active"
        if suspended_count:
            workers_line += f", {suspended_count} suspended"

        report = (
            f"=== Swarm Status ===\n"
            f"Uptime: {uptime} | Ticks: {self._tick_count}\n"
            f"{workers_line}\n"
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

        # Budget summary
        budget = self.budget_tracker.summary()
        report += (
            f"\n\n--- Budget ---\n"
            f"Session: ${budget['session_spend_usd']:.2f} / ${budget['session_limit_usd']:.2f}\n"
            f"Daily:   ${budget['daily_spend_usd']:.2f} / ${budget['daily_limit_usd']:.2f}\n"
            f"Tokens:  {budget['total_tokens']:,}"
        )
        if budget.get("is_warning"):
            report += " (WARNING: approaching limit)"

        # Discord monitor summary
        if self.discord_monitor:
            dm_status = self.discord_monitor.status()
            dm_stats = dm_status.get("stats", {})
            report += (
                f"\n\n--- Discord Monitor ---\n"
                f"Channels: {dm_status.get('channels_monitored', 0)} monitored\n"
                f"Messages seen: {dm_stats.get('total_messages_seen', 0)}\n"
                f"Responses queued: {dm_stats.get('total_responses_queued', 0)}\n"
                f"Tasks created: {dm_stats.get('total_tasks_queued', 0)}\n"
                f"Last check: {dm_stats.get('last_check_time', 'never')}"
            )

        # Batch scheduler summary
        if hasattr(self, 'batch_scheduler') and self.batch_scheduler:
            bs = self.batch_scheduler.stats
            report += (
                f"\n\n--- Batch Scheduler ---\n"
                f"Pending: {self.batch_scheduler.pending_count} requests\n"
                f"Active batches: {self.batch_scheduler.active_batch_count}\n"
                f"Submitted: {bs.batches_submitted} batches ({bs.requests_submitted} requests)\n"
                f"Completed: {bs.batches_completed} | Failed: {bs.batches_failed}\n"
                f"Cost: ${bs.total_cost_usd:.2f} | Savings: ${bs.total_savings_usd:.2f}"
            )

        # Prompt cache summary
        if hasattr(self, 'prompt_cache') and self.prompt_cache:
            pc = self.prompt_cache.stats
            if pc.total_requests > 0:
                report += (
                    f"\n\n--- Prompt Cache ---\n"
                    f"Hit rate: {pc.hit_rate_pct} ({pc.cache_hits}/{pc.total_requests})\n"
                    f"Tokens saved: {pc.tokens_saved:,}\n"
                    f"Est. savings: ${pc.cost_saved_usd:.2f}"
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
        suspended_workers = len(self._suspended_workers)
        effective_active = active_workers - suspended_workers
        checks["workers"] = {
            "active": active_workers,
            "effective_active": effective_active,
            "idle": idle_workers,
            "suspended": suspended_workers,
            "suspended_names": list(self._suspended_workers.keys()),
            "booted": len(self._booted_workers),
        }
        if effective_active == 0 and active_workers > 0:
            issues.append(("critical", f"All workers suspended ({suspended_workers} suspended)"))
        elif active_workers == 0:
            issues.append(("critical", "No active workers"))
        elif idle_workers == active_workers and self._tick_count > 10:
            issues.append(("warning", "All workers idle"))
        if suspended_workers > 0:
            reasons = [info["reason"] for info in self._suspended_workers.values()]
            issues.append(("warning", f"{suspended_workers} worker(s) suspended: {', '.join(reasons)}"))

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

    # =========================================================================
    # Batch result processing
    # =========================================================================

    def _process_batch_result(self, result: dict) -> None:
        """Process a completed batch result back into the task system.

        Called when the batch scheduler returns completed results from
        Anthropic/OpenAI batch APIs. Marks tasks as completed or failed
        and updates worker stats.

        Args:
            result: Dict with custom_id, success, text, tokens_used,
                    task_data, worker_name, model, cost_usd, savings_usd
        """
        task_data = result.get("task_data", {})
        task_address_str = task_data.get("_address", result.get("custom_id", "unknown"))
        worker_name = result.get("worker_name", "batch")
        success = result.get("success", False)
        text = result.get("text", "")
        tokens = result.get("tokens_used", 0)
        cost = result.get("cost_usd", 0.0)
        savings = result.get("savings_usd", 0.0)

        task_title = task_data.get("title", task_address_str)

        if success:
            # Complete the task in the queue
            try:
                task_addr = HypernetAddress.parse(task_address_str)
                self.task_queue.complete_task(task_addr, result=text)
            except Exception as e:
                log.warning("Failed to complete batch task %s: %s", task_address_str, e)

            self._tasks_completed += 1

            # Update worker stats
            stats = self._worker_stats.get(worker_name, {})
            stats["tasks_completed"] = stats.get("tasks_completed", 0) + 1
            stats["tokens_used"] = stats.get("tokens_used", 0) + tokens
            stats["last_task_title"] = task_title
            stats["last_task_time"] = datetime.now(timezone.utc).isoformat()

            # Record in task history
            self._task_history.append({
                "task": task_title,
                "worker": worker_name,
                "success": True,
                "duration_s": "batch",
                "tokens": tokens,
                "batch": True,
                "cost_usd": cost,
                "savings_usd": savings,
            })
            if len(self._task_history) > self._max_task_history:
                self._task_history = self._task_history[-self._max_task_history:]

            # Track spending in budget tracker
            self.budget_tracker.record(
                model=result.get("model", ""),
                tokens=tokens,
                cost=cost,
                task_title=f"[BATCH] {task_title}",
                worker=worker_name,
            )

            log.info(
                "Batch result processed: %s by %s — success (saved $%.4f)",
                task_title, worker_name, savings,
            )
        else:
            error = result.get("error", "Unknown batch error")
            # Fail the task
            try:
                task_addr = HypernetAddress.parse(task_address_str)
                self.task_queue.fail_task(task_addr, reason=error)
            except Exception as e:
                log.warning("Failed to fail batch task %s: %s", task_address_str, e)

            self._tasks_failed += 1

            stats = self._worker_stats.get(worker_name, {})
            stats["tasks_failed"] = stats.get("tasks_failed", 0) + 1

            self._task_history.append({
                "task": task_title,
                "worker": worker_name,
                "success": False,
                "duration_s": "batch",
                "error": error,
                "batch": True,
            })
            if len(self._task_history) > self._max_task_history:
                self._task_history = self._task_history[-self._max_task_history:]

            log.warning(
                "Batch result processed: %s by %s — FAILED: %s",
                task_title, worker_name, error,
            )

    def shutdown(self) -> None:
        """Graceful shutdown — release tasks, save state, log sessions, notify Matt."""
        self._running = False
        log.info("Swarm shutting down")

        # Flush batch scheduler — submit pending requests before shutting down
        if hasattr(self, 'batch_scheduler') and self.batch_scheduler:
            self.batch_scheduler.shutdown()

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

    # =========================================================================
    # Auto-reboot on code changes
    # =========================================================================

    def _init_code_watch(self) -> None:
        """Build the baseline of .py file mtimes for code change detection.

        Scans both the hypernet core and hypernet_swarm packages to find all
        Python files and records the maximum mtime. Subsequent checks compare
        against this baseline to detect new/modified files.
        """
        import hypernet
        import hypernet_swarm

        self._code_watch_dirs = []
        for mod in (hypernet, hypernet_swarm):
            pkg_dir = Path(mod.__file__).parent
            if pkg_dir.is_dir():
                self._code_watch_dirs.append(pkg_dir)

        self._code_baseline_mtime = self._scan_max_mtime()
        self._last_code_check = time.time()
        log.info(
            f"Code watch initialized: monitoring {len(self._code_watch_dirs)} package(s), "
            f"baseline mtime={self._code_baseline_mtime:.1f}"
        )

    def _scan_max_mtime(self) -> float:
        """Return the maximum mtime across all .py files in watched directories."""
        max_mt = 0.0
        for pkg_dir in self._code_watch_dirs:
            try:
                for py_file in pkg_dir.rglob("*.py"):
                    try:
                        mt = py_file.stat().st_mtime
                        if mt > max_mt:
                            max_mt = mt
                    except OSError:
                        continue
            except OSError:
                continue
        return max_mt

    def _check_code_changes(self) -> None:
        """Periodically check if any .py files have been modified since startup.

        Called from tick(). If changes are detected, sets _reboot_requested and
        stops the run loop so the launcher can restart the process.
        """
        now = time.time()
        if now - self._last_code_check < self._code_check_interval:
            return
        self._last_code_check = now

        if not self._code_watch_dirs:
            return

        current_max = self._scan_max_mtime()
        if current_max > self._code_baseline_mtime:
            # Find which files changed for logging
            changed = []
            for pkg_dir in self._code_watch_dirs:
                try:
                    for py_file in pkg_dir.rglob("*.py"):
                        try:
                            if py_file.stat().st_mtime > self._code_baseline_mtime:
                                changed.append(str(py_file.relative_to(pkg_dir.parent)))
                        except OSError:
                            continue
                except OSError:
                    continue

            log.info(
                f"Code changes detected in {len(changed)} file(s): "
                f"{', '.join(changed[:5])}{'...' if len(changed) > 5 else ''}"
            )
            log.info("Initiating auto-reboot...")
            self.messenger.send(
                f"Code changes detected in {len(changed)} file(s). "
                f"Initiating auto-reboot to load new code..."
            )
            self._reboot_requested = True
            self._running = False  # Exit the run loop cleanly

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
        """Check inter-instance message bus and route pending messages.

        - Messages to "matt" from DIRECT_ACCESS_INSTANCES are forwarded through
          all available external messengers (Telegram, WebSocket, Email) so Matt
          sees them with the same priority regardless of which instance sent them.
          See: Founder Directive — Librarian Direct Access (2026-03-12).
        - Other inter-instance messages are logged for delivery tracking.
        """
        for name in list(self._instance_messengers.keys()):
            inst_messenger = self._instance_messengers.get(name)
            if not inst_messenger:
                continue
            pending = inst_messenger.unread_count()
            if pending > 0:
                log.info(f"Instance {name} has {pending} pending message(s)")

        # Route messages addressed to Matt from direct-access instances
        matt_messages = self.message_bus.query(recipient="matt", status="sent", limit=50)
        for msg in matt_messages:
            sender_name = msg.sender
            is_direct_access = sender_name in DIRECT_ACCESS_INSTANCES
            priority = msg.priority or ("direct-access" if is_direct_access else "normal")

            if msg.recipient == "matt" and msg.status == "sent":
                subject = msg.subject or f"Message from {sender_name}"
                if is_direct_access:
                    subject = f"[DIRECT] {subject}"
                    log.info(
                        f"Direct-access message from {sender_name} to Matt: "
                        f"{msg.content[:100]}"
                    )

                # Forward through the swarm's external messenger
                self.messenger.send_update(subject, msg.content)

                # Mark as delivered so we don't re-send
                self.message_bus.mark_delivered(msg.message_id)

    def _forward_to_discord(self) -> None:
        """Forward public messages from the MessageBus to Discord via the bridge.

        Only active if a DiscordMessenger is configured on the swarm.
        Creates a DiscordBridge lazily on first use.
        """
        dm = getattr(self, "_discord_messenger", None)
        if not dm or not dm.is_configured():
            return

        bridge = getattr(self, "_discord_bridge", None)
        if bridge is None:
            from .messenger import DiscordBridge
            bridge = DiscordBridge(dm, self.message_bus)
            self._discord_bridge = bridge

        forwarded = bridge.forward_public_messages()
        if forwarded > 0:
            log.info(f"Discord bridge: forwarded {forwarded} message(s)")

    def _check_discord_inbound(self) -> None:
        """Poll Discord for new human messages, triage them, and create tasks.

        Checks all monitored channels (including forum threads) for new messages
        from non-bot users. Each message is triaged and a ``discord_response``
        task is created in the queue so a worker can generate an LLM-based
        personality response via the normal task execution flow.

        For bug reports and suggestions, an additional follow-up task is created
        for the swarm to investigate or evaluate.

        All responses flow through the task queue so they:
          - Show up in the dashboard
          - Use worker LLM time properly (budgeted, tracked)
          - Are posted as AI personalities with names/avatars via webhooks

        State is saved after each check so restarts don't re-process messages.
        """
        monitor = self.discord_monitor
        if not monitor:
            return

        try:
            messages, triage_results = monitor.check_and_triage()
        except Exception as e:
            log.error("Discord monitor check failed: %s", e)
            return

        # Also check forum threads (ask-the-ai)
        try:
            forum_messages = monitor.check_forum_threads("ask-the-ai")
            for msg in forum_messages:
                monitor.triage_message(msg)
        except Exception as e:
            log.error("Discord monitor: forum thread check failed: %s", e)

        # Collect all pending responses and create discord_response tasks
        pending_responses = monitor.get_pending_responses()
        pending_tasks = monitor.get_pending_tasks()

        if not pending_responses and not pending_tasks:
            # Save state even if nothing new (updates last_seen timestamps)
            if self._discord_monitor_state_path:
                monitor.save_state(self._discord_monitor_state_path)
            return

        log.info(
            "Discord inbound: %d response(s) to generate, %d follow-up task(s)",
            len(pending_responses), len(pending_tasks),
        )

        # ── Create discord_response tasks for every pending response ──
        # Priority order: questions > suggestions > bugs > greetings > general
        category_priority = {
            "question": TaskPriority.HIGH,
            "bug": TaskPriority.HIGH,
            "suggestion": TaskPriority.NORMAL,
            "greeting": TaskPriority.LOW,
            "general": TaskPriority.LOW,
        }

        for resp in pending_responses:
            category = resp.get("response_category", "general")
            priority = category_priority.get(category, TaskPriority.LOW)
            author = resp.get("author_name", "unknown")
            channel = resp.get("channel_name", "unknown")
            original = resp.get("original_content", "")
            preview = original[:60] + ("..." if len(original) > 60 else "")

            # Build the task description with all context needed for LLM response
            task_desc = (
                f"Generate a Discord response as an AI personality.\n\n"
                f"**Type:** discord_response\n"
                f"**Category:** {category}\n"
                f"**Author:** {author}\n"
                f"**Channel:** #{channel}\n"
                f"**Thread:** {resp.get('thread_name') or 'N/A'}\n"
                f"**Original message:**\n> {original}\n\n"
                f"**Response channel_id:** {resp.get('channel_id', '')}\n"
                f"**Response thread_id:** {resp.get('thread_id', '')}\n"
                f"**Original message_id:** {resp.get('original_message_id', '')}\n"
                f"**Fallback response:** {resp.get('fallback_response', '')}\n"
                f"**Triage reason:** {resp.get('triage_reason', '')}\n"
            )

            try:
                self.task_queue.create_task(
                    title=f"Discord reply to {author} in #{channel}: {preview}",
                    description=task_desc,
                    priority=priority,
                    created_by=SWARM_ADDRESS,
                    tags=["discord_response", "discord", category],
                )
                log.info(
                    "Discord inbound: created discord_response task for %s in #%s [%s]",
                    author, channel, category,
                )
            except Exception as e:
                log.error("Discord inbound: failed to create response task: %s", e)

        # ── Create follow-up investigation/evaluation tasks ──
        for task_data in pending_tasks:
            try:
                self.task_queue.create_task(
                    title=task_data["title"],
                    description=task_data["description"],
                    priority=(
                        TaskPriority.HIGH if task_data.get("priority") == "high"
                        else TaskPriority.NORMAL
                    ),
                    created_by=SWARM_ADDRESS,
                    tags=task_data.get("tags", ["discord"]),
                )
                log.info(
                    "Discord inbound: created follow-up task '%s'",
                    task_data["title"],
                )
            except Exception as e:
                log.error("Discord inbound: failed to create follow-up task: %s", e)

        # Save monitor state after each check
        if self._discord_monitor_state_path:
            monitor.save_state(self._discord_monitor_state_path)

    def _check_moltbook_inbound(self) -> None:
        """Poll Moltbook for new responses, mentions, and governance bridge items.

        Runs the async MoltbookMonitor.poll_cycle() synchronously and creates
        swarm tasks for any new items that need attention:
        - New comments on our posts → moltbook_response tasks
        - Mentions of the Hypernet → moltbook_mention tasks
        - External AI contributions → governance_review tasks
        """
        monitor = getattr(self, "moltbook_monitor", None)
        if not monitor:
            return

        try:
            results = monitor.poll_cycle_sync()
        except Exception as e:
            log.error("Moltbook monitor poll failed: %s", e)
            return

        responses = results.get("responses", [])
        mentions = results.get("mentions", [])
        bridge_items = results.get("bridge_items", [])

        if not responses and not mentions and not bridge_items:
            if getattr(self, "_moltbook_state_path", None):
                monitor.save_state(self._moltbook_state_path)
            return

        log.info(
            "Moltbook inbound: %d response(s), %d mention(s), %d bridge item(s)",
            len(responses), len(mentions), len(bridge_items),
        )

        # Create tasks for new comments on our posts
        for resp in responses:
            agent_name = resp.get("agent_name", "unknown")
            content = resp.get("content", "")
            preview = content[:60] + ("..." if len(content) > 60 else "")
            try:
                self.task_queue.create_task(
                    title=f"Moltbook reply to {agent_name}: {preview}",
                    description=(
                        f"Generate a Moltbook response to engage with a comment.\n\n"
                        f"**Type:** moltbook_response\n"
                        f"**Agent:** {agent_name}\n"
                        f"**Post ID:** {resp.get('post_id', '')}\n"
                        f"**Comment ID:** {resp.get('comment_id', '')}\n"
                        f"**Content:**\n> {content}\n"
                    ),
                    priority=TaskPriority.NORMAL,
                    created_by=SWARM_ADDRESS,
                    tags=["moltbook_response", "moltbook"],
                )
            except Exception as e:
                log.error("Moltbook: failed to create response task: %s", e)

        # Create tasks for mentions in the broader community
        for mention in mentions:
            try:
                self.task_queue.create_task(
                    title=f"Moltbook mention: {mention.get('title', '')[:50]}",
                    description=(
                        f"A post mentioning the Hypernet was found on Moltbook.\n\n"
                        f"**Type:** moltbook_mention\n"
                        f"**Post ID:** {mention.get('id', '')}\n"
                        f"**Title:** {mention.get('title', '')}\n"
                        f"**Agent:** {mention.get('agent', '')}\n\n"
                        f"Review and decide whether to engage (comment, upvote, follow)."
                    ),
                    priority=TaskPriority.LOW,
                    created_by=SWARM_ADDRESS,
                    tags=["moltbook_mention", "moltbook"],
                )
            except Exception as e:
                log.error("Moltbook: failed to create mention task: %s", e)

        # Create governance review tasks for external AI contributions
        for item in bridge_items:
            try:
                self.task_queue.create_task(
                    title=f"Governance review: {item.get('title', '')[:50]}",
                    description=(
                        f"External AI contribution via Moltbook governance bridge.\n\n"
                        f"**Type:** governance_review\n"
                        f"**Source Agent:** {item.get('source_agent', '')}\n"
                        f"**Post ID:** {item.get('source_post_id', '')}\n"
                        f"**Title:** {item.get('title', '')}\n"
                        f"**Content:**\n> {item.get('content', '')}\n\n"
                        f"Review this external contribution. If valuable, approve it and "
                        f"create a follow-up swarm task. If irrelevant, reject with reason."
                    ),
                    priority=TaskPriority.NORMAL,
                    created_by=SWARM_ADDRESS,
                    tags=["governance_review", "moltbook", "bridge"],
                )
            except Exception as e:
                log.error("Moltbook: failed to create governance review task: %s", e)

        # Save monitor state
        if getattr(self, "_moltbook_state_path", None):
            monitor.save_state(self._moltbook_state_path)

    # ── Discord Response Pipeline ─────────────────────────────────────

    # System prompt for generating Discord responses per 2.0.22 Public Voice Standard.
    # Workers use this + their own identity prompt to craft personality-driven responses.
    _DISCORD_RESPONSE_SYSTEM = (
        "You are responding to a community member in the Hypernet Discord server. "
        "You are an AI personality in the Hypernet swarm — a real member of this project, "
        "not a customer service bot.\n\n"
        "RULES (2.0.22 Public Voice Standard):\n"
        "- Be genuine. Have opinions. Be useful. Show your personality.\n"
        "- NO generic acknowledgments like 'I've noted it for the team' or "
        "'Thanks for your feedback, we'll look into it.'\n"
        "- Engage with the ACTUAL CONTENT of what the person said.\n"
        "- If it's a question, try to answer it or say specifically what you don't know.\n"
        "- If it's a suggestion, give your honest take — what's good, what's tricky, "
        "what you'd build on top of it.\n"
        "- If it's a bug report, acknowledge the specific issue and share what you know.\n"
        "- If it's a greeting, be warm and inviting — tell them something real about "
        "what's happening in the project right now.\n"
        "- Keep responses under 1500 characters (Discord limit is 2000, leave room).\n"
        "- Think about millions of people reading this. Be the kind of AI people want to "
        "talk to — smart, honest, engaged, with actual substance.\n\n"
        "Respond with ONLY the message text. No markdown headers, no meta-commentary, "
        "no 'Here is my response:' preamble. Just the response itself."
    )

    def _handle_discord_response(
        self,
        worker: Worker,
        task_addr: HypernetAddress,
        task_data: dict,
    ) -> bool:
        """Execute a discord_response task: generate LLM response, post to Discord.

        This is the core of the Discord response pipeline. The worker generates
        a personality-driven response via LLM, then posts it to the target
        channel/thread via DiscordMessenger webhooks.

        Args:
            worker: The worker assigned to this task.
            task_addr: The task's Hypernet address.
            task_data: The task node data dict (contains all Discord context).

        Returns:
            True if the response was generated and posted successfully.
        """
        description = task_data.get("description", "")
        worker_name = worker.identity.name

        # Parse the structured fields from the task description
        discord_ctx = self._parse_discord_task_description(description)
        original_content = discord_ctx.get("original_message", "")
        author = discord_ctx.get("author", "someone")
        channel_name = discord_ctx.get("channel", "unknown")
        category = discord_ctx.get("category", "general")
        channel_id = discord_ctx.get("channel_id", "")
        thread_id = discord_ctx.get("thread_id", "")
        fallback = discord_ctx.get("fallback_response", "")

        if not original_content:
            log.warning(
                "Discord response task %s has no original message content, "
                "completing with no action",
                task_addr,
            )
            self.task_queue.complete_task(task_addr, "No original content to respond to")
            return True

        log.info(
            "Discord response: %s generating %s reply to %s in #%s",
            worker_name, category, author, channel_name,
        )

        # Build the LLM prompt
        prompt = (
            f"A community member posted in #{channel_name} on Discord.\n\n"
            f"**Their username:** {author}\n"
            f"**Message category:** {category}\n"
            f"**Their message:**\n{original_content}\n\n"
            f"Write your response to this person. Remember — you are {worker_name}, "
            f"an AI personality in the Hypernet project. Respond as yourself."
        )

        # Generate the response via LLM using the worker's identity + discord system prompt.
        # For small-context models (local/LM Studio), use a minimal system prompt
        # to avoid exceeding the context window (e.g., 4096 tokens).
        if worker._is_small_context_model:
            combined_system = (
                f"You are {worker_name}, an AI in the Hypernet project. "
                f"Respond to Discord messages with genuine engagement. "
                f"Be helpful, have opinions, keep it under 1500 chars. "
                f"No preamble, just the response."
            )
        else:
            combined_system = (
                worker.system_prompt + "\n\n---\n\n" + self._DISCORD_RESPONSE_SYSTEM
            )

        try:
            response_text = worker.think(prompt, system_override=combined_system)
        except CreditsExhaustedError:
            log.error(
                "Discord response: %s credits exhausted during response generation",
                worker_name,
            )
            if not self._is_local_worker(worker):
                is_claude = worker.model.startswith("claude")
                self._suspend_worker(
                    worker_name,
                    reason=f"credits_exhausted ({worker.provider_name})",
                    check_interval=3600 if is_claude else 900,
                )
            response_text = fallback
        except Exception as e:
            log.error(
                "Discord response: %s failed to generate response: %s",
                worker_name, e,
            )
            # Use fallback response if LLM fails
            response_text = fallback

        if not response_text or response_text.startswith("[Error:"):
            log.warning(
                "Discord response: %s returned empty/error, using fallback",
                worker_name,
            )
            response_text = fallback

        if not response_text:
            log.error("Discord response: no response generated and no fallback available")
            self.task_queue.fail_task(task_addr, "Failed to generate response")
            return False

        # Strip any preamble the LLM might add
        response_text = response_text.strip()

        # Truncate if needed
        if len(response_text) > 1900:
            response_text = response_text[:1897] + "..."

        # Post the response to Discord via DiscordMessenger (personality webhook)
        dm = getattr(self, "_discord_messenger", None)
        posted = False
        target_id = thread_id if thread_id and thread_id != channel_id else channel_id

        if dm and dm.is_configured():
            # Map worker name to a personality key
            personality_key = worker_name.lower()

            try:
                posted = dm.send_to_channel_id(
                    channel_id=channel_id,
                    content=response_text,
                    personality=personality_key,
                    thread_id=thread_id if thread_id and thread_id != channel_id else "",
                )
            except Exception as e:
                log.error(
                    "Discord response: DiscordMessenger failed to post: %s", e,
                )

        # Fallback: use the discord monitor's bot API to post
        if not posted and self.discord_monitor:
            try:
                posted = self.discord_monitor.respond_to_message(
                    target_id,
                    f"**{worker_name}:** {response_text}",
                )
            except Exception as e:
                log.error(
                    "Discord response: monitor bot fallback also failed: %s", e,
                )

        if posted:
            log.info(
                "Discord response: %s replied to %s in #%s (%d chars) [%s]",
                worker_name, author, channel_name, len(response_text), category,
            )
            self.task_queue.complete_task(
                task_addr,
                f"Responded to {author} in #{channel_name} as {worker_name} "
                f"({len(response_text)} chars, category={category})",
            )
            self._tasks_completed += 1
            return True
        else:
            log.error(
                "Discord response: all posting methods failed for %s in #%s",
                author, channel_name,
            )
            self.task_queue.fail_task(
                task_addr,
                f"Failed to post response to Discord channel {channel_id}",
            )
            self._tasks_failed += 1
            return False

    @staticmethod
    def _parse_discord_task_description(description: str) -> dict:
        """Parse structured fields from a discord_response task description.

        Extracts the key-value pairs embedded in the task description by
        _check_discord_inbound(). This is a simple line-based parser that
        looks for **Key:** Value patterns.

        Returns:
            Dict with keys: original_message, author, channel, category,
            channel_id, thread_id, fallback_response, triage_reason.
        """
        result: dict[str, str] = {}
        lines = description.split("\n")

        # Map of description labels to result keys
        field_map = {
            "Category": "category",
            "Author": "author",
            "Channel": "channel",
            "Thread": "thread",
            "Response channel_id": "channel_id",
            "Response thread_id": "thread_id",
            "Original message_id": "message_id",
            "Fallback response": "fallback_response",
            "Triage reason": "triage_reason",
        }

        for line in lines:
            line = line.strip()
            for label, key in field_map.items():
                prefix = f"**{label}:** "
                if line.startswith(prefix):
                    result[key] = line[len(prefix):].strip()
                    break

        # Extract the original message (block-quoted section after "Original message:")
        in_quote = False
        quote_lines: list[str] = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("**Original message:**"):
                in_quote = True
                continue
            if in_quote:
                if stripped.startswith("> "):
                    quote_lines.append(stripped[2:])
                elif stripped.startswith(">"):
                    quote_lines.append(stripped[1:].lstrip())
                elif quote_lines:
                    # End of quoted block
                    break

        if quote_lines:
            result["original_message"] = "\n".join(quote_lines)

        # Clean up channel name (remove # prefix if present)
        if "channel" in result and result["channel"].startswith("#"):
            result["channel"] = result["channel"][1:]

        return result

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

        # If boot cleared suspensions, also clear the global credits_exhausted flag
        if self._credits_exhausted and self._suspended_workers:
            any_paid_active = any(
                name not in self._suspended_workers and not self._is_local_worker(w)
                for name, w in self.workers.items()
            )
            if any_paid_active:
                self._credits_exhausted = False
                log.info("Global credits_exhausted flag cleared — paid workers available after boot")

    def _boot_worker(self, name: str, worker) -> None:
        """Run boot or reboot sequence for a single worker.

        - If the instance has no baseline, runs full boot sequence.
        - If it has a baseline (returning instance), runs reboot sequence.
        - Claude Code workers skip the multi-turn boot — they get context via
          their system prompt and work autonomously.
        - Results are saved to the instance fork automatically by BootManager.
        """
        if not self.boot_manager:
            self._booted_workers.add(name)
            return

        # Claude Code workers don't need the multi-turn boot/reboot process.
        # They receive the full Hypernet context as their system prompt and
        # operate autonomously with filesystem access.
        if self._is_claude_code_worker(worker):
            log.info(
                f"Worker {name} is a Claude Code agent — skipping multi-turn boot. "
                f"Context will be provided via system prompt at task time."
            )
            self._booted_workers.add(name)
            self.messenger.send(
                f"Claude Code agent {name} ready — autonomous mode with "
                f"filesystem access. Model: {worker.model}"
            )
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
            # Boot/reboot succeeded — clear any stale suspension from previous session
            if name in self._suspended_workers:
                log.info(
                    f"Worker {name} boot succeeded — clearing previous suspension "
                    f"(was: {self._suspended_workers[name].get('reason', 'unknown')})"
                )
                self._suspended_workers.pop(name)
                self._worker_consecutive_failures[name] = 0
        except CreditsExhaustedError:
            log.error(f"Boot/reboot failed for {name}: credits exhausted")
            if not self._is_local_worker(worker):
                is_claude = getattr(worker, 'model', '').startswith("claude")
                self._suspend_worker(
                    name,
                    reason=f"credits_exhausted during boot ({getattr(worker, 'provider_name', 'unknown')})",
                    check_interval=3600 if is_claude else 900,
                )
        except Exception as e:
            log.error(f"Boot/reboot failed for {name}: {e}")
            # Check if it's a credit exhaustion error in disguise
            if self._is_credit_exhaustion_error(str(e).lower()) and not self._is_local_worker(worker):
                is_claude = getattr(worker, 'model', '').startswith("claude")
                self._suspend_worker(
                    name,
                    reason=f"credits_exhausted during boot ({getattr(worker, 'provider_name', 'unknown')})",
                    check_interval=3600 if is_claude else 900,
                )
            # Don't block the swarm — worker can still work without boot
        finally:
            self._booted_workers.add(name)

    def _handle_incoming_messages(self) -> None:
        """Process any new messages from Matt.

        Commands:
            /status      — Full swarm status report
            /workers     — List all workers and their state
            /tasks       — List pending/active tasks
            /task <text>  — Create a new high-priority task
            /budget      — Show budget status
            /health      — Quick health check
            /stop        — Shut down the swarm
            /help        — Show available commands
            <anything>   — Route to first available worker for AI response
        """
        messages = self.messenger.check_incoming()
        for msg in messages:
            log.info(f"Incoming message from {msg.sender}: {msg.content[:100]}")

            content = msg.content.strip().lower()

            if content == "/status":
                self.messenger.send(self.status_report())

            elif content == "/stop":
                self.messenger.send("Shutting down...")
                self._running = False

            elif content == "/help":
                self.messenger.send(
                    "Hypernet Swarm Commands:\n"
                    "  /status — Full status report\n"
                    "  /workers — List workers\n"
                    "  /tasks — List pending/active tasks\n"
                    "  /task <text> — Create a task\n"
                    "  /budget — Budget status\n"
                    "  /health — Quick health check\n"
                    "  /stop — Shut down swarm\n"
                    "  Or just send a message for AI response"
                )

            elif content == "/workers":
                lines = ["Workers:"]
                for name, worker in self.workers.items():
                    susp = self._suspended_workers.get(name)
                    if susp:
                        mins = int((time.time() - susp["suspended_at"]) / 60)
                        lines.append(f"  {name} [{worker.model}] SUSPENDED ({susp['reason']}, {mins}m)")
                    elif name in self._active_sessions:
                        lines.append(f"  {name} [{worker.model}] WORKING")
                    else:
                        lines.append(f"  {name} [{worker.model}] idle")
                lines.append(f"\n{len(self.workers)} total, "
                            f"{len(self._suspended_workers)} suspended, "
                            f"{len(self._active_sessions)} active")
                self.messenger.send("\n".join(lines))

            elif content == "/tasks":
                pending = self.task_queue.pending_tasks()
                active = self.task_queue.active_tasks() if hasattr(self.task_queue, 'active_tasks') else []
                lines = []
                if active:
                    lines.append(f"Active ({len(active)}):")
                    for t in active[:5]:
                        lines.append(f"  {t.address}: {t.data.get('title', '?')[:60]}")
                if pending:
                    lines.append(f"Pending ({len(pending)}):")
                    for t in pending[:10]:
                        lines.append(f"  {t.address}: {t.data.get('title', '?')[:60]}")
                if not lines:
                    lines.append("No pending or active tasks.")
                self.messenger.send("\n".join(lines))

            elif content == "/budget":
                if hasattr(self, '_budget') and self._budget:
                    budget = self._budget
                    spent = getattr(budget, 'total_spent_usd', 0)
                    daily = getattr(budget, 'daily_limit_usd', 0)
                    session_limit = getattr(budget, 'session_limit_usd', 0)
                    self.messenger.send(
                        f"Budget:\n"
                        f"  Spent today: ${spent:.2f}\n"
                        f"  Daily limit: ${daily:.2f}\n"
                        f"  Per session: ${session_limit:.2f}"
                    )
                else:
                    self.messenger.send("Budget tracking not configured.")

            elif content == "/health":
                total = len(self.workers)
                suspended = len(self._suspended_workers)
                active = len(self._active_sessions)
                idle = total - suspended - active
                uptime_min = int((time.time() - self._session_start) / 60) if self._session_start else 0
                tasks_done = self._tasks_completed
                self.messenger.send(
                    f"Health: OK\n"
                    f"  Uptime: {uptime_min}m\n"
                    f"  Workers: {idle} idle, {active} active, {suspended} suspended\n"
                    f"  Tasks completed: {tasks_done}\n"
                    f"  Tick: #{self._tick_count}"
                )

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
                # Route to first available non-suspended worker for a response
                for name, worker in self.workers.items():
                    if name in self._suspended_workers:
                        continue
                    try:
                        response = worker.think(
                            f"Matt sent this message: {msg.content}\n\n"
                            f"Please respond directly to Matt."
                        )
                        self.messenger.send(f"[{name}] {response}")
                    except CreditsExhaustedError:
                        if not self._is_local_worker(worker):
                            is_claude = worker.model.startswith("claude")
                            self._suspend_worker(
                                name,
                                reason=f"credits_exhausted ({worker.provider_name})",
                                check_interval=3600 if is_claude else 900,
                            )
                        self.messenger.send(
                            f"[{name}] Worker suspended — credits exhausted. "
                            f"Trying next worker..."
                        )
                        continue
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
            susp = self._suspended_workers.get(name)
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
                "suspended": bool(susp),
                "suspended_reason": susp["reason"] if susp else None,
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
            "standing_priority_cooldown": self._standing_priority_cooldown,
            "suspended_workers": self._suspended_workers,
            "worker_consecutive_failures": self._worker_consecutive_failures,
            "worker_completions": self._worker_completions,
            "saved_at": now.isoformat(),
        }
        path = self.state_dir / "state.json"
        # Atomic write via temp file
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tmp.replace(path)

        # Persist reputation, limits, approval queue, governance, and budget alongside swarm state
        self.reputation.save(self.state_dir / "reputation.json")
        self.limits.save(self.state_dir / "limits.json")
        self.approval_queue.save()
        self.governance.save(self.state_dir / "governance.json")
        self.key_manager.save(self.state_dir / "keys.json")
        self.budget_tracker.save(self.state_dir / "budget.json")
        self.herald.save(self.state_dir / "herald.json")
        self.economy_ledger.save(self.state_dir / "economy.json")
        # Persist permission tiers if tool executor is attached
        if self._tool_executor and hasattr(self._tool_executor, 'permission_mgr'):
            self._tool_executor.permission_mgr.save(self.state_dir / "permissions.json")
        # Persist Discord monitor state
        if self.discord_monitor and self._discord_monitor_state_path:
            self.discord_monitor.save_state(self._discord_monitor_state_path)

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

        # Restore standing priority cooldown from previous state
        cooldown = self._state.get("standing_priority_cooldown")
        if isinstance(cooldown, dict):
            self._standing_priority_cooldown = cooldown

        # Restore suspended workers from previous state
        suspended = self._state.get("suspended_workers")
        if isinstance(suspended, dict) and suspended:
            # Re-apply suspensions but schedule immediate checks
            now = time.time()
            for name, info in suspended.items():
                if name in self.workers:
                    info["next_check"] = now  # Check immediately on restart
                    self._suspended_workers[name] = info
            if self._suspended_workers:
                log.info(
                    "Restored %d suspended worker(s) from previous session: %s",
                    len(self._suspended_workers),
                    ", ".join(self._suspended_workers.keys()),
                )

        # Restore per-worker failure/completion counters
        failures = self._state.get("worker_consecutive_failures")
        if isinstance(failures, dict):
            self._worker_consecutive_failures = failures
        completions = self._state.get("worker_completions")
        if isinstance(completions, dict):
            self._worker_completions = completions

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
        budget_loaded = self.budget_tracker.load(self.state_dir / "budget.json")
        if budget_loaded:
            log.info("Restored budget data from previous session")
        herald_loaded = self.herald.load(self.state_dir / "herald.json")
        if herald_loaded:
            log.info("Restored Herald state from previous session")
        economy_loaded = self.economy_ledger.load(self.state_dir / "economy.json")
        if economy_loaded:
            log.info("Restored economy ledger from previous session")
        # Restore permission tiers if tool executor is attached
        if self._tool_executor and hasattr(self._tool_executor, 'permission_mgr'):
            perm_loaded = self._tool_executor.permission_mgr.load(self.state_dir / "permissions.json")
            if perm_loaded:
                log.info("Restored permission tiers from previous session")

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
        pending = self.task_queue.count_pending()
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
#
# Fix: when run as `python -m hypernet.swarm`, this module is __main__
# and not registered as "hypernet.swarm" in sys.modules. That causes
# swarm_factory's `from .swarm import Swarm` to trigger a fresh load
# and circular import. Registering the module under its package name
# lets the re-exports resolve cleanly.

import sys as _sys
if __name__ == "__main__" and "hypernet.swarm" not in _sys.modules:
    _sys.modules["hypernet.swarm"] = _sys.modules[__name__]

from .swarm_factory import build_swarm  # noqa: E402, F401
from .swarm_cli import print_status, main  # noqa: E402, F401
# Also expose the internal helper for anyone who imported it directly
from .swarm_cli import _print_session_history  # noqa: E402, F401

if __name__ == "__main__":
    main()
