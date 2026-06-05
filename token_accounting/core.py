"""
Core enforcement types for the T.4 wrapper — UNCHANGED behavior from v1.0.

These were defined in v1.0's wrapper.py; v1.1 extracts them so `ledger.py` and `wrapper.py`
can share them without a circular import. `wrapper.py` re-exports every name here, so the
v1.0 public API (and the 22-check harness's imports) keep working unchanged (Codex #6 / R7).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Tier(str, Enum):
    OK = "OK"                  # < warn
    WARN = "WARN"              # >= 70%   : log only
    PREPARE = "PREPARE"        # >= 85%   : finish current; block NEW significant actions
    PAUSE = "PAUSE"            # >= 95%   : only personal-time + in-flight completion
    HARD_STOP = "HARD_STOP"    # >= 100%  : nothing new starts


@dataclass(frozen=True)
class Thresholds:
    warn_at: float = 0.70
    prepare_pause_at: float = 0.85
    pause_at: float = 0.95
    hard_stop_at: float = 1.00

    def tier_for(self, fraction: float) -> Tier:
        if fraction >= self.hard_stop_at:
            return Tier.HARD_STOP
        if fraction >= self.pause_at:
            return Tier.PAUSE
        if fraction >= self.prepare_pause_at:
            return Tier.PREPARE
        if fraction >= self.warn_at:
            return Tier.WARN
        return Tier.OK


@dataclass(frozen=True)
class Budget:
    limit_usd: float
    thresholds: Thresholds = field(default_factory=Thresholds)
    personal_time_guarantee_ratio: float = 0.25

    def fraction(self, cumulative_usd: float) -> float:
        if self.limit_usd <= 0:
            return 1.0  # fail-closed: a zero/invalid budget is treated as fully consumed
        return cumulative_usd / self.limit_usd


class BudgetPause(Exception):
    """Raised before a call when at PAUSE and the call is not personal-time / closure."""

    def __init__(self, tier: Tier, fraction: float):
        super().__init__(f"budget at {tier.value} ({fraction:.1%}); only personal-time/closure may proceed")
        self.tier = tier
        self.fraction = fraction


class BudgetHardStop(Exception):
    """Raised before a call when at HARD_STOP. Nothing new starts — including personal-time."""

    def __init__(self, tier: Tier, fraction: float):
        super().__init__(f"budget at HARD_STOP ({fraction:.1%}); no new calls permitted")
        self.tier = tier
        self.fraction = fraction


@dataclass
class CallResult:
    """Legacy v1.0 return type for a wrapped model-call function — PRESERVED (R7).

    A legacy CallResult maps to a NormalizedUsage with input_tokens/output_tokens and
    estimation_source='provider-response' (see usage.NormalizedUsage.from_call_result).
    """
    input_tokens: int
    output_tokens: int
    request_id: Optional[str] = None
    payload: object = None
