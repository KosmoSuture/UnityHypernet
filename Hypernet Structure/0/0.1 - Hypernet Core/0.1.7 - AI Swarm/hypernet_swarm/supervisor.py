"""
Swarm Supervisor — Local LLM watchdog that keeps the swarm alive.

The supervisor is a special role for a local model (Ollama/LM Studio) that
monitors the swarm 24/7. Because local models have unlimited tokens and no
API costs, the supervisor never stops — even when all cloud workers are
suspended due to credit exhaustion.

Responsibilities:
  1. Health monitoring — check all workers, detect crashes, report status
  2. Auto-recovery — restart suspended workers when credits might be available
  3. Task queue management — generate new tasks when queue is empty
  4. Budget awareness — schedule expensive tasks during off-peak/double-token windows
  5. Daily reports — summarize what happened, what's pending, what needs attention
  6. Emergency alerts — notify when critical issues arise

The supervisor runs as a background thread within the swarm, using the local
model for all its reasoning. It is the LAST thing to stop and the FIRST to start.

Usage:
    supervisor = SwarmSupervisor(swarm, local_worker)
    supervisor.start()  # Runs in background
    # ... swarm runs ...
    supervisor.stop()
"""

from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .swarm import Swarm
    from .worker import Worker

log = logging.getLogger(__name__)


class SwarmSupervisor:
    """Local LLM supervisor that keeps the swarm alive 24/7.

    Uses a local model (Ollama, LM Studio) for all reasoning — zero API cost.
    Monitors health, manages recovery, generates reports, and ensures
    continuity even when cloud providers are exhausted.
    """

    # Check intervals (seconds)
    HEALTH_CHECK_INTERVAL = 60      # Every minute
    RECOVERY_CHECK_INTERVAL = 300   # Every 5 minutes
    REPORT_INTERVAL = 3600          # Every hour
    TASK_GEN_INTERVAL = 600         # Every 10 minutes

    # Double-token window (approximate — Claude Code gives 2x tokens during this window)
    DOUBLE_TOKEN_START_HOUR = 8     # 8 AM local time
    DOUBLE_TOKEN_END_HOUR = 14      # 2 PM local time

    def __init__(self, swarm: Swarm, supervisor_worker: Optional[Worker] = None):
        self.swarm = swarm
        self.worker = supervisor_worker  # The local model used for reasoning
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_health_check = 0.0
        self._last_recovery_check = 0.0
        self._last_report = 0.0
        self._last_task_gen = 0.0
        self._health_history: list[dict] = []
        self._alerts: list[dict] = []

        # State persistence
        self._state_dir = Path(swarm.state_dir) / "supervisor"
        self._state_dir.mkdir(parents=True, exist_ok=True)

    def start(self):
        """Start the supervisor background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="swarm-supervisor",
        )
        self._thread.start()
        log.info("Swarm supervisor started (using %s)",
                 self.worker.identity.name if self.worker else "no local model")

    def stop(self):
        """Stop the supervisor."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=10)
        log.info("Swarm supervisor stopped")

    def is_double_token_window(self) -> bool:
        """Check if we're in the double-token window (cheaper Claude Code)."""
        now = datetime.now()
        return self.DOUBLE_TOKEN_START_HOUR <= now.hour < self.DOUBLE_TOKEN_END_HOUR

    def get_status(self) -> dict:
        """Return supervisor status for dashboard."""
        return {
            "running": self._running,
            "supervisor_model": self.worker.model if self.worker else None,
            "double_token_window": self.is_double_token_window(),
            "last_health_check": self._last_health_check,
            "last_recovery_check": self._last_recovery_check,
            "last_report": self._last_report,
            "alerts": self._alerts[-10:],  # Last 10 alerts
            "health_history_count": len(self._health_history),
        }

    # ── Main Loop ──

    def _run_loop(self):
        """Main supervisor loop — runs continuously in background."""
        log.info("Supervisor loop started")
        while self._running:
            try:
                now = time.time()

                # Health check — every minute
                if now - self._last_health_check >= self.HEALTH_CHECK_INTERVAL:
                    self._health_check()
                    self._last_health_check = now

                # Recovery check — every 5 minutes
                if now - self._last_recovery_check >= self.RECOVERY_CHECK_INTERVAL:
                    self._recovery_check()
                    self._last_recovery_check = now

                # Task generation — every 10 minutes
                if now - self._last_task_gen >= self.TASK_GEN_INTERVAL:
                    self._check_task_queue()
                    self._last_task_gen = now

                # Hourly report
                if now - self._last_report >= self.REPORT_INTERVAL:
                    self._generate_report()
                    self._last_report = now

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                log.error("Supervisor error: %s", e)
                time.sleep(30)  # Back off on error

    # ── Health Monitoring ──

    def _health_check(self):
        """Check the health of all workers and the swarm."""
        swarm = self.swarm
        if not swarm._running:
            self._alert("critical", "Swarm is not running!")
            return

        suspended = list(swarm._suspended_workers.keys())
        total = len(swarm.workers)
        active = total - len(suspended)

        health = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tick_count": swarm._tick_count,
            "tasks_completed": swarm._tasks_completed,
            "tasks_failed": swarm._tasks_failed,
            "workers_total": total,
            "workers_active": active,
            "workers_suspended": suspended,
            "pending_tasks": len(swarm.task_queue.get_available_tasks()),
            "budget_remaining": None,
            "double_token_window": self.is_double_token_window(),
        }

        # Budget check
        if hasattr(swarm, 'budget_tracker'):
            bt = swarm.budget_tracker
            health["budget_remaining"] = {
                "session_usd": bt.config.session_limit_usd - bt.session_spend,
                "daily_usd": bt.config.daily_limit_usd - bt.daily_spend,
            }

        self._health_history.append(health)
        # Keep last 1440 entries (~24 hours at 1/min)
        if len(self._health_history) > 1440:
            self._health_history = self._health_history[-1440:]

        # Alert conditions
        if active == 0:
            self._alert("critical", f"All {total} workers suspended! Only local model running.")
        elif len(suspended) > total * 0.5:
            self._alert("warning", f"{len(suspended)}/{total} workers suspended: {', '.join(suspended)}")

        if health["pending_tasks"] == 0 and swarm._tick_count > 10:
            self._alert("info", "Task queue empty — supervisor should generate new tasks")

    # ── Recovery ──

    def _recovery_check(self):
        """Check if suspended workers can be recovered."""
        swarm = self.swarm
        suspended = dict(swarm._suspended_workers)

        if not suspended:
            return

        now = time.time()
        for name, info in suspended.items():
            suspended_minutes = (now - info.get("suspended_at", now)) / 60

            # If suspended for more than 2 hours, try a health check
            if suspended_minutes > 120:
                log.info(
                    "Supervisor: Worker %s suspended for %.0f minutes — scheduling recovery check",
                    name, suspended_minutes,
                )
                # Set next_check to now so the swarm's built-in checker will try
                info["next_check"] = now

        # During double-token window, be more aggressive about recovery
        if self.is_double_token_window():
            for name, info in suspended.items():
                if "claude" in info.get("reason", "").lower():
                    info["next_check"] = now
                    log.info(
                        "Supervisor: Double-token window active — forcing recovery check for %s",
                        name,
                    )

    # ── Task Management ──

    def _check_task_queue(self):
        """Check if the task queue needs attention."""
        swarm = self.swarm
        available = swarm.task_queue.get_available_tasks()

        if len(available) < 3 and swarm._tick_count > 10:
            log.info("Supervisor: Task queue low (%d tasks) — swarm should generate more", len(available))
            # The swarm's generate_tasks() will handle this in the next tick

    # ── Reporting ──

    def _generate_report(self):
        """Generate an hourly supervisor report."""
        swarm = self.swarm

        # Calculate stats from health history
        recent = self._health_history[-60:]  # Last hour
        if not recent:
            return

        tasks_completed_this_hour = 0
        if len(recent) >= 2:
            tasks_completed_this_hour = recent[-1]["tasks_completed"] - recent[0]["tasks_completed"]

        report = {
            "type": "supervisor_report",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "period": "hourly",
            "tasks_completed": tasks_completed_this_hour,
            "workers_active": recent[-1]["workers_active"],
            "workers_suspended": recent[-1]["workers_suspended"],
            "pending_tasks": recent[-1]["pending_tasks"],
            "double_token_window": self.is_double_token_window(),
            "alerts_this_hour": [a for a in self._alerts if
                                 time.time() - a.get("time", 0) < 3600],
        }

        # Save report
        report_file = self._state_dir / f"report-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
        try:
            report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        except OSError:
            pass

        log.info(
            "Supervisor hourly report: %d tasks completed, %d active workers, %d suspended, %d pending tasks",
            tasks_completed_this_hour,
            report["workers_active"],
            len(report["workers_suspended"]),
            report["pending_tasks"],
        )

    # ── Alerts ──

    def _alert(self, severity: str, message: str):
        """Record an alert."""
        alert = {
            "severity": severity,
            "message": message,
            "time": time.time(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._alerts.append(alert)
        # Keep last 100 alerts
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]

        if severity == "critical":
            log.error("SUPERVISOR ALERT: %s", message)
        elif severity == "warning":
            log.warning("Supervisor alert: %s", message)
        else:
            log.info("Supervisor: %s", message)
