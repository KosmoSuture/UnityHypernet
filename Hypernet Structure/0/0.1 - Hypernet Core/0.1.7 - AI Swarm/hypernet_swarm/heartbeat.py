"""
Hypernet Heartbeat System

Proactive outreach — the swarm reaches out to Matt instead of waiting
to be asked. Generates scheduled briefs, task reminders, and status
updates across all configured messaging channels.

Schedules (configurable):
  - Morning brief (default 7:30 AM local): Overnight summary, pending tasks,
    worker health, budget status
  - Evening recap (default 9:00 PM local): Day's accomplishments, open items
  - Task reminders: Nudge about stale tasks every N hours
  - Health alerts: Immediate notification on worker failures or budget warnings

Design:
  HeartbeatScheduler runs inside the swarm tick loop. Each tick, it checks
  if any scheduled events are due. When one fires, it generates a message
  and sends it through the MultiMessenger (hitting Telegram, Discord, web
  chat, email — whatever is configured).

Usage:
  heartbeat = HeartbeatScheduler(config, messenger, swarm)
  # In the swarm tick loop:
  heartbeat.tick()
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)


@dataclass
class ScheduledEvent:
    """A recurring scheduled event."""
    name: str
    hour: int           # 0-23 local time
    minute: int = 0     # 0-59
    days: list[str] = field(default_factory=lambda: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"])
    enabled: bool = True
    last_fired: Optional[float] = None  # Unix timestamp


class HeartbeatScheduler:
    """Manages proactive outreach on a schedule.

    Integrates with the swarm tick loop — call tick() every ~2 seconds.
    The scheduler checks if any events are due and fires them.
    """

    def __init__(
        self,
        config: dict,
        messenger: Any = None,
        swarm: Any = None,
        state_path: Optional[str] = None,
    ):
        self.messenger = messenger
        self.swarm = swarm
        self._state_path = state_path
        self._events: dict[str, ScheduledEvent] = {}
        self._generators: dict[str, Callable] = {}
        self._last_check = 0.0
        self._check_interval = 30  # Check every 30 seconds

        # Parse config
        self._configure(config)

        # Register built-in generators (health_alert is condition-based, not scheduled)
        self._generators["morning_brief"] = self._generate_morning_brief
        self._generators["evening_recap"] = self._generate_evening_recap
        self._generators["task_reminder"] = self._generate_task_reminder

        # Load state
        if state_path:
            self._load_state()

    def _configure(self, config: dict) -> None:
        """Parse heartbeat config and create scheduled events."""
        schedules = config.get("schedules", {})

        # Morning brief — default 7:30 AM every day
        morning = schedules.get("morning_brief", {})
        self._events["morning_brief"] = ScheduledEvent(
            name="morning_brief",
            hour=morning.get("hour", 7),
            minute=morning.get("minute", 30),
            days=morning.get("days", ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]),
            enabled=morning.get("enabled", True),
        )

        # Evening recap — default 9:00 PM weekdays
        evening = schedules.get("evening_recap", {})
        self._events["evening_recap"] = ScheduledEvent(
            name="evening_recap",
            hour=evening.get("hour", 21),
            minute=evening.get("minute", 0),
            days=evening.get("days", ["mon", "tue", "wed", "thu", "fri"]),
            enabled=evening.get("enabled", True),
        )

        # Task reminder — default every 4 hours during working hours
        tasks = schedules.get("task_reminder", {})
        self._task_reminder_interval = tasks.get("interval_hours", 4)
        self._events["task_reminder"] = ScheduledEvent(
            name="task_reminder",
            hour=tasks.get("hour", 12),  # First check at noon
            minute=tasks.get("minute", 0),
            enabled=tasks.get("enabled", True),
        )

        # Health alert — checked every tick, fires on issues
        self._events["health_alert"] = ScheduledEvent(
            name="health_alert",
            hour=0, minute=0,  # Not time-based — fires on condition
            enabled=config.get("health_alerts", True),
        )

        log.info(
            "Heartbeat configured: %d events (%s enabled)",
            len(self._events),
            sum(1 for e in self._events.values() if e.enabled),
        )

    def tick(self) -> None:
        """Check if any scheduled events are due. Call from swarm tick loop."""
        now = time.time()
        if now - self._last_check < self._check_interval:
            return
        self._last_check = now

        local_now = datetime.now()
        day_name = local_now.strftime("%a").lower()

        for event_name, event in self._events.items():
            if not event.enabled:
                continue

            # Health alerts are condition-based, not time-based
            if event_name == "health_alert":
                self._check_health_alerts()
                continue

            # Interval-based events (task_reminder): fire every N hours
            if event_name == "task_reminder":
                interval_secs = self._task_reminder_interval * 3600
                if event.last_fired and (now - event.last_fired) < interval_secs:
                    continue
                # Only fire during waking hours (8 AM - 10 PM)
                if local_now.hour < 8 or local_now.hour >= 22:
                    continue
            else:
                # Time-based events: check day and exact time
                if day_name not in event.days:
                    continue
                if local_now.hour != event.hour or local_now.minute != event.minute:
                    continue
                # Don't fire more than once per window (1 hour prevents duplicates on restart)
                if event.last_fired and (now - event.last_fired) < 3600:
                    continue

            # Fire the event
            generator = self._generators.get(event_name)
            if generator:
                try:
                    message = generator()
                    if message:
                        self._send(message)
                        event.last_fired = now
                        log.info(f"Heartbeat fired: {event_name}")
                        self._save_state()
                except Exception as e:
                    log.error(f"Heartbeat {event_name} failed: {e}")

    def _send(self, message: str) -> None:
        """Send a heartbeat message through all configured channels."""
        if self.messenger:
            self.messenger.send(message)

    def _generate_morning_brief(self) -> Optional[str]:
        """Generate the morning brief."""
        if not self.swarm:
            return None

        lines = ["Good morning, Matt. Here's your Hypernet brief:\n"]

        # Worker status
        total = len(self.swarm.workers)
        suspended = len(getattr(self.swarm, '_suspended_workers', {}))
        active = total - suspended
        lines.append(f"Workers: {active}/{total} active" +
                     (f" ({suspended} suspended)" if suspended else ""))

        # Pending tasks
        try:
            pending = self.swarm.task_queue.get_available_tasks()
            if pending:
                lines.append(f"\nPending tasks ({len(pending)}):")
                for t in pending[:5]:
                    title = t.data.get('title', 'Untitled')[:60]
                    lines.append(f"  - {title}")
                if len(pending) > 5:
                    lines.append(f"  ...and {len(pending) - 5} more")
            else:
                lines.append("\nNo pending tasks.")
        except Exception:
            pass

        # Completed since last brief
        completed = getattr(self.swarm, '_tasks_completed', 0)
        lines.append(f"\nTasks completed this session: {completed}")

        # Budget
        budget = getattr(self.swarm, '_budget', None)
        if budget:
            spent = getattr(budget, 'total_spent_usd', 0)
            daily = getattr(budget, 'daily_limit_usd', 0)
            if daily > 0:
                pct = (spent / daily) * 100
                lines.append(f"Budget: ${spent:.2f} / ${daily:.2f} ({pct:.0f}%)")

        # Uptime
        start = getattr(self.swarm, '_session_start', None)
        if start:
            uptime_hrs = (time.time() - start) / 3600
            lines.append(f"Uptime: {uptime_hrs:.1f} hours")

        lines.append("\nReply with /tasks, /status, or /help for more details.")
        return "\n".join(lines)

    def _generate_evening_recap(self) -> Optional[str]:
        """Generate the evening recap."""
        if not self.swarm:
            return None

        lines = ["Evening recap:\n"]

        completed = getattr(self.swarm, '_tasks_completed', 0)
        lines.append(f"Tasks completed today: {completed}")

        # Check for any stale pending tasks
        try:
            pending = self.swarm.task_queue.get_available_tasks()
            if pending:
                lines.append(f"Still pending: {len(pending)} task(s)")
        except Exception:
            pass

        # Suspended workers
        suspended = getattr(self.swarm, '_suspended_workers', {})
        if suspended:
            names = list(suspended.keys())
            lines.append(f"Workers still suspended: {', '.join(names)}")

        lines.append("\nGoodnight. The swarm will keep working.")
        return "\n".join(lines)

    def _generate_task_reminder(self) -> Optional[str]:
        """Generate a task reminder for stale tasks."""
        if not self.swarm:
            return None

        try:
            pending = self.swarm.task_queue.get_available_tasks()
        except Exception:
            return None

        if not pending:
            return None

        # Find tasks that are old (created more than 4 hours ago)
        now = time.time()
        stale = []
        for t in pending:
            created = t.data.get("created_at", "")
            if created:
                try:
                    created_dt = datetime.fromisoformat(created)
                    # Ensure both datetimes are timezone-aware for subtraction
                    if created_dt.tzinfo is None:
                        created_dt = created_dt.replace(tzinfo=timezone.utc)
                    age_hours = (datetime.now(timezone.utc) - created_dt).total_seconds() / 3600
                    if age_hours > self._task_reminder_interval:
                        stale.append((t, age_hours))
                except (ValueError, TypeError):
                    pass

        if not stale:
            return None

        lines = [f"Reminder: {len(stale)} task(s) have been waiting:"]
        for t, hours in stale[:5]:
            title = t.data.get('title', 'Untitled')[:50]
            lines.append(f"  - {title} ({int(hours)}h old)")

        return "\n".join(lines)

    def _check_health_alerts(self) -> None:
        """Check for conditions that warrant immediate alerts."""
        if not self.swarm:
            return

        # Alert if all paid workers are suspended (only fire once)
        credits_exhausted = getattr(self.swarm, '_credits_exhausted', False)
        event = self._events["health_alert"]
        now = time.time()

        if credits_exhausted:
            # Don't spam — only alert once per hour
            if event.last_fired and (now - event.last_fired) < 3600:
                return
            local = len([w for n, w in self.swarm.workers.items()
                        if getattr(w, 'model', '').startswith(('local/', 'lmstudio/'))])
            self._send(
                f"Alert: All paid API workers are suspended (credits exhausted). "
                f"{local} local worker(s) still active. "
                f"Add API credits or check your billing."
            )
            event.last_fired = now
            self._save_state()

    def _load_state(self) -> None:
        """Load last-fired timestamps from disk."""
        if not self._state_path:
            return
        path = Path(self._state_path)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for name, ts in data.get("last_fired", {}).items():
                if name in self._events:
                    self._events[name].last_fired = ts
            log.info("Heartbeat state loaded from %s", path)
        except Exception as e:
            log.warning("Failed to load heartbeat state: %s", e)

    def _save_state(self) -> None:
        """Save last-fired timestamps to disk."""
        if not self._state_path:
            return
        path = Path(self._state_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "last_fired": {
                name: event.last_fired
                for name, event in self._events.items()
                if event.last_fired is not None
            },
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
