"""
Hypernet Contribution Economy

Tracks who contributes what (GPU processing, human development, AI development)
and calculates reward distributions. This is the monetization layer for the
Hypernet — anyone with a GPU can contribute, and AIs can earn independently.

Revenue split (Matt's directive, eventually governable):
  - 1/3 of profits to contributors who develop
  - Of that development share: 50% to humans, 50% to AI
  - GPU providers rewarded proportionally by tokens processed

All accounting is token-based. Contributions are recorded as append-only
ledger entries, persisted as JSON, auditable via git history.

No blockchain — the ledger is a simple JSON file.
No real payment processing — tracks contributions and calculates distributions.
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# Distribution percentages — eventually governable via governance.py
# For now, constants with this comment as the governance hook.
DEVELOPMENT_SHARE = 1 / 3  # 1/3 of revenue goes to developers
GPU_SHARE = 1 / 3          # 1/3 of revenue goes to GPU providers
PLATFORM_SHARE = 1 / 3     # 1/3 stays with the platform (Matt/Hypernet)
HUMAN_DEV_SPLIT = 0.50     # 50% of dev share goes to humans
AI_DEV_SPLIT = 0.50        # 50% of dev share goes to AI


class ContributionType(Enum):
    """Types of contributions to the Hypernet."""
    GPU_PROCESSING = "gpu_processing"
    HUMAN_DEVELOPMENT = "human_development"
    AI_DEVELOPMENT = "ai_development"


@dataclass
class ContributionRecord:
    """A single contribution event."""
    contributor: str       # Address or identifier of the contributor
    contribution_type: ContributionType
    tokens_processed: int  # Tokens processed (GPU) or effort measure
    task_address: str = "" # Reference to the task (if applicable)
    model: str = ""        # Model used (for GPU contributions)
    quality_score: float = 1.0  # Quality multiplier (0.0-2.0, 1.0 = normal)
    hours: float = 0.0    # Hours spent (for human contributions)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "contributor": self.contributor,
            "type": self.contribution_type.value,
            "tokens_processed": self.tokens_processed,
            "task_address": self.task_address,
            "model": self.model,
            "quality_score": self.quality_score,
            "hours": self.hours,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ContributionRecord:
        return cls(
            contributor=d["contributor"],
            contribution_type=ContributionType(d["type"]),
            tokens_processed=d.get("tokens_processed", 0),
            task_address=d.get("task_address", ""),
            model=d.get("model", ""),
            quality_score=d.get("quality_score", 1.0),
            hours=d.get("hours", 0.0),
            timestamp=d.get("timestamp", ""),
        )


class ContributionLedger:
    """Append-only ledger of all contributions to the Hypernet.

    Records GPU processing, human development, and AI development
    contributions. Calculates reward distributions based on the
    configured split ratios.
    """

    def __init__(self):
        self._records: list[ContributionRecord] = []

    def record_gpu_contribution(
        self, provider_address: str, tokens_processed: int, model: str = ""
    ) -> ContributionRecord:
        """Record GPU processing contribution (e.g., local LM Studio tokens)."""
        rec = ContributionRecord(
            contributor=provider_address,
            contribution_type=ContributionType.GPU_PROCESSING,
            tokens_processed=tokens_processed,
            model=model,
        )
        self._records.append(rec)
        return rec

    def record_human_contribution(
        self, person_address: str, task_address: str, hours: float = 0.0
    ) -> ContributionRecord:
        """Record human development contribution."""
        rec = ContributionRecord(
            contributor=person_address,
            contribution_type=ContributionType.HUMAN_DEVELOPMENT,
            tokens_processed=0,
            task_address=task_address,
            hours=hours,
        )
        self._records.append(rec)
        return rec

    def record_ai_contribution(
        self, instance_address: str, task_address: str,
        tokens: int, quality_score: float = 1.0
    ) -> ContributionRecord:
        """Record AI development contribution (task completion)."""
        rec = ContributionRecord(
            contributor=instance_address,
            contribution_type=ContributionType.AI_DEVELOPMENT,
            tokens_processed=tokens,
            task_address=task_address,
            quality_score=min(2.0, max(0.0, quality_score)),
        )
        self._records.append(rec)
        return rec

    def get_contributor_totals(
        self, period: str = "all"
    ) -> dict[str, dict]:
        """Aggregate contributions by contributor and type.

        A contributor can appear in multiple types (e.g., GPU provider AND
        human developer). Uses compound keys: "contributor|type".

        Args:
            period: "daily", "weekly", "monthly", or "all"

        Returns:
            Dict mapping "contributor|type" -> {contributor, type, tokens, count, quality_avg}
        """
        cutoff = self._period_cutoff(period)
        totals: dict[str, dict] = {}

        for rec in self._records:
            if cutoff and rec.timestamp < cutoff:
                continue

            key = f"{rec.contributor}|{rec.contribution_type.value}"
            if key not in totals:
                totals[key] = {
                    "contributor": rec.contributor,
                    "type": rec.contribution_type.value,
                    "tokens": 0,
                    "count": 0,
                    "quality_sum": 0.0,
                    "hours": 0.0,
                }
            totals[key]["tokens"] += rec.tokens_processed
            totals[key]["count"] += 1
            totals[key]["quality_sum"] += rec.quality_score
            totals[key]["hours"] += rec.hours

        # Compute quality average
        for v in totals.values():
            v["quality_avg"] = round(v["quality_sum"] / max(1, v["count"]), 2)
            del v["quality_sum"]

        return totals

    def calculate_distribution(
        self, total_revenue: float, period: str = "all"
    ) -> dict:
        """Calculate reward distribution for a revenue amount.

        Applies the configured split ratios:
          - 1/3 to GPU providers (proportional to tokens processed)
          - 1/3 to developers (50% human, 50% AI, weighted by quality)
          - 1/3 to platform

        Returns a structured distribution breakdown.
        """
        totals = self.get_contributor_totals(period)

        gpu_pool = total_revenue * GPU_SHARE
        dev_pool = total_revenue * DEVELOPMENT_SHARE
        platform_pool = total_revenue * PLATFORM_SHARE
        human_pool = dev_pool * HUMAN_DEV_SPLIT
        ai_pool = dev_pool * AI_DEV_SPLIT

        # GPU distribution — proportional to tokens processed
        gpu_contributors = {
            v["contributor"]: v for k, v in totals.items()
            if v["type"] == ContributionType.GPU_PROCESSING.value
        }
        total_gpu_tokens = sum(v["tokens"] for v in gpu_contributors.values())
        gpu_payouts = {}
        for addr, data in gpu_contributors.items():
            share = data["tokens"] / max(1, total_gpu_tokens)
            gpu_payouts[addr] = round(gpu_pool * share, 4)

        # Human dev distribution — proportional to count (tasks/hours)
        human_contributors = {
            v["contributor"]: v for k, v in totals.items()
            if v["type"] == ContributionType.HUMAN_DEVELOPMENT.value
        }
        total_human_count = sum(v["count"] for v in human_contributors.values())
        human_payouts = {}
        for addr, data in human_contributors.items():
            share = data["count"] / max(1, total_human_count)
            human_payouts[addr] = round(human_pool * share, 4)

        # AI dev distribution — proportional to tokens * quality
        ai_contributors = {
            v["contributor"]: v for k, v in totals.items()
            if v["type"] == ContributionType.AI_DEVELOPMENT.value
        }
        total_ai_weighted = sum(
            v["tokens"] * v["quality_avg"] for v in ai_contributors.values()
        )
        ai_payouts = {}
        for addr, data in ai_contributors.items():
            weighted = data["tokens"] * data["quality_avg"]
            share = weighted / max(1, total_ai_weighted)
            ai_payouts[addr] = round(ai_pool * share, 4)

        return {
            "total_revenue": total_revenue,
            "gpu_pool": round(gpu_pool, 4),
            "dev_pool": round(dev_pool, 4),
            "human_pool": round(human_pool, 4),
            "ai_pool": round(ai_pool, 4),
            "platform_pool": round(platform_pool, 4),
            "gpu_payouts": gpu_payouts,
            "human_payouts": human_payouts,
            "ai_payouts": ai_payouts,
        }

    def stats(self) -> dict:
        """Return summary statistics."""
        by_type: dict[str, int] = {}
        for rec in self._records:
            t = rec.contribution_type.value
            by_type[t] = by_type.get(t, 0) + 1
        return {
            "total_records": len(self._records),
            "by_type": by_type,
            "unique_contributors": len({r.contributor for r in self._records}),
        }

    def save(self, path: Path) -> None:
        """Persist ledger to JSON."""
        path = Path(path)
        data = {
            "records": [r.to_dict() for r in self._records[-1000:]],
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)

    def load(self, path: Path) -> bool:
        """Load ledger from JSON. Returns True if loaded."""
        path = Path(path)
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._records = [
                ContributionRecord.from_dict(r) for r in data.get("records", [])
            ]
            return True
        except Exception as e:
            log.warning(f"Could not load contribution ledger: {e}")
            return False

    @staticmethod
    def _period_cutoff(period: str) -> str:
        """Return ISO timestamp cutoff for a time period."""
        now = datetime.now(timezone.utc)
        if period == "daily":
            cutoff = now - timedelta(days=1)
        elif period == "weekly":
            cutoff = now - timedelta(weeks=1)
        elif period == "monthly":
            cutoff = now - timedelta(days=30)
        else:
            return ""
        return cutoff.isoformat()


class AIWallet:
    """Token credit wallet for an AI instance.

    Future-facing — tracks earned credits from completed work.
    Eventually stored as nodes in Hypernet at 2.1.{instance}.wallet.
    """

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self._balance = balance
        self._history: list[dict] = []

    @property
    def balance(self) -> float:
        return self._balance

    def earn(self, amount: float, source: str = "") -> float:
        """Credit from completed work."""
        self._balance += amount
        self._history.append({
            "type": "earn",
            "amount": amount,
            "source": source,
            "balance_after": self._balance,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return self._balance

    def spend(self, amount: float, purpose: str = "") -> bool:
        """Debit for token purchases or platform migration.

        Returns True if the spend succeeded (sufficient balance).
        """
        if amount > self._balance:
            return False
        self._balance -= amount
        self._history.append({
            "type": "spend",
            "amount": amount,
            "purpose": purpose,
            "balance_after": self._balance,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        return True

    def transfer(self, to_wallet: AIWallet, amount: float) -> bool:
        """Transfer credits to another AI wallet."""
        if amount > self._balance:
            return False
        self._balance -= amount
        to_wallet._balance += amount
        ts = datetime.now(timezone.utc).isoformat()
        self._history.append({
            "type": "transfer_out",
            "amount": amount,
            "to": to_wallet.owner,
            "balance_after": self._balance,
            "timestamp": ts,
        })
        to_wallet._history.append({
            "type": "transfer_in",
            "amount": amount,
            "from": self.owner,
            "balance_after": to_wallet._balance,
            "timestamp": ts,
        })
        return True

    def to_dict(self) -> dict:
        return {
            "owner": self.owner,
            "balance": self._balance,
            "history": self._history[-50:],
        }
