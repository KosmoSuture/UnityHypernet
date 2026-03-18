"""
Hypernet Budget Tracker

Tracks token spending across sessions to enforce daily and session limits.
Local models (cost=0) are always allowed regardless of budget state.
Persists spending history to JSON for cross-session tracking.
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .providers import ModelTier, get_model_tier, get_model_cost_per_million

log = logging.getLogger(__name__)


@dataclass
class BudgetConfig:
    """Budget limits for token spending."""
    daily_limit_usd: float = 5.00
    session_limit_usd: float = 2.00
    warn_at_percent: float = 0.80

    @classmethod
    def from_dict(cls, d: dict) -> BudgetConfig:
        return cls(
            daily_limit_usd=float(d.get("daily_limit_usd", 5.00)),
            session_limit_usd=float(d.get("session_limit_usd", 2.00)),
            warn_at_percent=float(d.get("warn_at_percent", 0.80)),
        )


@dataclass
class SpendRecord:
    """A single spending event."""
    model: str
    tokens: int
    cost_usd: float
    task_title: str
    worker: str
    timestamp: str = ""
    tier: str = ""

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "tokens": self.tokens,
            "cost_usd": self.cost_usd,
            "task_title": self.task_title,
            "worker": self.worker,
            "timestamp": self.timestamp,
            "tier": self.tier,
        }


class BudgetTracker:
    """Tracks and enforces token spending budgets.

    Local models always pass budget checks (they're free).
    Paid model usage is tracked against daily and session limits.
    """

    def __init__(self, config: Optional[BudgetConfig] = None):
        self.config = config or BudgetConfig()
        self._session_spend: float = 0.0
        self._daily_spend: float = 0.0
        self._daily_date: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._records: list[SpendRecord] = []
        self._total_tokens: int = 0
        # Per-worker tracking — contributed by Lattice (2.1, The Architect)
        self._worker_spend: dict[str, float] = {}  # worker_name -> session spend USD
        self._worker_tokens: dict[str, int] = {}   # worker_name -> session tokens
        self._worker_tasks: dict[str, int] = {}    # worker_name -> tasks completed

    def can_spend(self, estimated_cost: float, model: str = "") -> bool:
        """Check if a spend is within budget.

        Local models always return True (they're free).
        For paid models, checks both session and daily limits.
        """
        if model and get_model_tier(model) == ModelTier.LOCAL:
            return True
        if estimated_cost <= 0:
            return True

        self._roll_daily()

        if self._session_spend + estimated_cost > self.config.session_limit_usd:
            return False
        if self._daily_spend + estimated_cost > self.config.daily_limit_usd:
            return False
        return True

    def estimate_cost(self, model: str, estimated_tokens: int = 1000) -> float:
        """Estimate cost for a model call before making it."""
        cost_per_m = get_model_cost_per_million(model)
        return (estimated_tokens / 1_000_000) * cost_per_m

    def record(self, model: str, tokens: int, cost: float,
               task_title: str = "", worker: str = "") -> None:
        """Record a completed spend."""
        self._roll_daily()

        tier = get_model_tier(model)
        rec = SpendRecord(
            model=model,
            tokens=tokens,
            cost_usd=cost,
            task_title=task_title,
            worker=worker,
            timestamp=datetime.now(timezone.utc).isoformat(),
            tier=tier.value,
        )
        self._records.append(rec)
        self._total_tokens += tokens

        # Per-worker tracking
        if worker:
            self._worker_spend[worker] = self._worker_spend.get(worker, 0.0) + cost
            self._worker_tokens[worker] = self._worker_tokens.get(worker, 0) + tokens
            self._worker_tasks[worker] = self._worker_tasks.get(worker, 0) + 1

        # Only count paid models against budget
        if tier != ModelTier.LOCAL:
            self._session_spend += cost
            self._daily_spend += cost

        if self.is_warning:
            log.warning(
                f"Budget warning: session ${self._session_spend:.2f}/"
                f"${self.config.session_limit_usd:.2f}, "
                f"daily ${self._daily_spend:.2f}/"
                f"${self.config.daily_limit_usd:.2f}"
            )

    @property
    def is_warning(self) -> bool:
        """True if spending has reached the warning threshold."""
        session_pct = self._session_spend / max(0.01, self.config.session_limit_usd)
        daily_pct = self._daily_spend / max(0.01, self.config.daily_limit_usd)
        return max(session_pct, daily_pct) >= self.config.warn_at_percent

    @property
    def session_spend(self) -> float:
        return self._session_spend

    @property
    def daily_spend(self) -> float:
        self._roll_daily()
        return self._daily_spend

    def summary(self) -> dict:
        """Return a summary of current budget state."""
        self._roll_daily()
        return {
            "session_spend_usd": round(self._session_spend, 4),
            "session_limit_usd": self.config.session_limit_usd,
            "daily_spend_usd": round(self._daily_spend, 4),
            "daily_limit_usd": self.config.daily_limit_usd,
            "daily_date": self._daily_date,
            "total_tokens": self._total_tokens,
            "total_records": len(self._records),
            "is_warning": self.is_warning,
            "per_worker": self.all_worker_summaries(),
        }

    def worker_summary(self, worker_name: str) -> dict:
        """Return spending summary for a specific worker."""
        return {
            "worker": worker_name,
            "spend_usd": round(self._worker_spend.get(worker_name, 0.0), 4),
            "tokens": self._worker_tokens.get(worker_name, 0),
            "tasks": self._worker_tasks.get(worker_name, 0),
        }

    def all_worker_summaries(self) -> list[dict]:
        """Return spending summaries for all workers, sorted by spend descending."""
        workers = set(self._worker_spend) | set(self._worker_tokens)
        summaries = [self.worker_summary(w) for w in workers]
        summaries.sort(key=lambda s: s["spend_usd"], reverse=True)
        return summaries

    def _roll_daily(self) -> None:
        """Reset daily spend if we've crossed into a new UTC day."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._daily_date:
            log.info(f"Budget daily reset: {self._daily_date} -> {today}")
            self._daily_spend = 0.0
            self._daily_date = today

    def save(self, path: Path) -> None:
        """Persist budget state to JSON."""
        data = {
            "config": {
                "daily_limit_usd": self.config.daily_limit_usd,
                "session_limit_usd": self.config.session_limit_usd,
                "warn_at_percent": self.config.warn_at_percent,
            },
            "daily_spend": self._daily_spend,
            "daily_date": self._daily_date,
            "total_tokens": self._total_tokens,
            "worker_spend": self._worker_spend,
            "worker_tokens": self._worker_tokens,
            "worker_tasks": self._worker_tasks,
            "records": [r.to_dict() for r in self._records[-200:]],
        }
        path = Path(path)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)

    def load(self, path: Path) -> bool:
        """Load budget state from JSON. Returns True if loaded."""
        path = Path(path)
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            saved_date = data.get("daily_date", "")
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if saved_date == today:
                self._daily_spend = float(data.get("daily_spend", 0.0))
            else:
                self._daily_spend = 0.0
            self._daily_date = today
            self._total_tokens = int(data.get("total_tokens", 0))
            # Restore per-worker tracking
            ws = data.get("worker_spend")
            if isinstance(ws, dict):
                self._worker_spend = {k: float(v) for k, v in ws.items()}
            wt = data.get("worker_tokens")
            if isinstance(wt, dict):
                self._worker_tokens = {k: int(v) for k, v in wt.items()}
            wta = data.get("worker_tasks")
            if isinstance(wta, dict):
                self._worker_tasks = {k: int(v) for k, v in wta.items()}
            return True
        except Exception as e:
            log.warning(f"Could not load budget state: {e}")
            return False
