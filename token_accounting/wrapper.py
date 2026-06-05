"""
T.4 per-call token-accounting wrapper — v1.1.

v1.1 adds Codex/multi-engine parity (EngineAdapter + CostModel/NormalizedUsage), the reconciler +
disclosure seams, and the S.3 ChainPrimitive seam — over an UNCHANGED enforcement core. This
module is also the backwards-compatibility surface (R7 / Codex #6): it re-exports every v1.0 public
name, so `from token_accounting.wrapper import (...)` and the exact 22-check harness pass unchanged.

Matt design-review-gate picks (2026-06-04T07:35Z, coord 073543Z): §5b = Anchor; §5a = Alt B with a
72h S.3 fast-follow (risk-accepted). This build ships UnkeyedHashChain behind the seam; the
AnchoredChain primitive fast-follows into the same seam with no ledger change.

Standard library only.
"""

from __future__ import annotations

from typing import Callable, Optional

# --- backwards-compat re-exports (v1.0 public API; harness imports these from here) ---
from .core import (  # noqa: F401
    Tier, Thresholds, Budget, BudgetPause, BudgetHardStop, CallResult,
)
from .ledger import TokenLedger  # noqa: F401
from .usage import (  # noqa: F401
    estimate_cost_usd, NormalizedUsage, CostModel, TokenCostModel, CostEstimate, PricingContext,
)
from .engines import EngineAdapter
from .chain import UnkeyedHashChain, SignerChain  # noqa: F401  (seam primitives)


class TokenAccountingWrapper:
    """Wraps model calls: enforce budget BEFORE the call, account AFTER it.

    Legacy (v1.0) usage is unchanged:
        w = TokenAccountingWrapper(ledger, budget, instance_name=..., account=..., provider=..., model=...)
        payload, tier = w.call(lambda: CallResult(input_tokens=.., output_tokens=..), is_personal_time=False)

    v1.1 multi-engine usage:
        w = TokenAccountingWrapper(ledger, budget, instance_name=..., account=..., provider=..., model=...,
                                   adapter=CodexAdapter(), cost_model=TokenCostModel())
        raw, tier = w.call_with_adapter(lambda: provider_raw_response)
    """

    def __init__(self, ledger: TokenLedger, budget: Budget, *, instance_name: str, account: str,
                 provider: str, model: str, wave: Optional[str] = None, project: Optional[str] = None,
                 engine: Optional[str] = None, adapter: Optional[EngineAdapter] = None,
                 cost_model: Optional[CostModel] = None, pricing_context: Optional[PricingContext] = None):
        self.ledger = ledger
        self.budget = budget
        self.instance_name = instance_name
        self.account = account
        self.provider = provider
        self.model = model
        self.wave = wave
        self.project = project
        self.adapter = adapter
        self.cost_model: CostModel = cost_model if cost_model is not None else TokenCostModel()
        self.pricing_context = pricing_context
        self.engine = engine or (adapter.engine_id if adapter is not None else None)
        self._logical_clock = 0

    def current_tier(self) -> Tier:
        return self.budget.thresholds.tier_for(self.budget.fraction(self.ledger.cumulative_usd()))

    def _enforce(self, is_personal_time: bool) -> Tier:
        cumulative = self.ledger.cumulative_usd()
        fraction = self.budget.fraction(cumulative)
        tier = self.budget.thresholds.tier_for(fraction)
        if tier == Tier.HARD_STOP:
            raise BudgetHardStop(tier, fraction)
        if tier == Tier.PAUSE and not is_personal_time:
            raise BudgetPause(tier, fraction)
        return tier

    def _record(self, usage: NormalizedUsage, is_personal_time: bool, request_id: Optional[str]) -> Tier:
        self._logical_clock += 1
        cost = self.cost_model.estimate(usage, self.model, self.pricing_context).cost_usd
        cumulative_after = self.ledger.cumulative_usd() + cost
        tier_after = self.budget.thresholds.tier_for(self.budget.fraction(cumulative_after))
        self.ledger.record(
            instance_name=self.instance_name, account=self.account, provider=self.provider,
            model=self.model, input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
            cost_estimate_usd=cost, cumulative_cost_after=cumulative_after, tier_after=tier_after,
            is_personal_time=is_personal_time, logical_clock=self._logical_clock,
            wave=self.wave, project=self.project, request_id=request_id,
            engine=self.engine, estimation_source=usage.estimation_source,
            usage_dimensions_json=usage.dimensions_json(), raw_usage_json=usage.raw_json(),
        )
        return tier_after

    def call(self, call_fn: Callable[[], CallResult], *, is_personal_time: bool = False,
             request_id: Optional[str] = None) -> tuple[object, Tier]:
        """Legacy v1.0 entry point — call_fn returns a CallResult. Behavior unchanged (R7)."""
        self._enforce(is_personal_time)
        result = call_fn()
        if not isinstance(result, CallResult):
            raise TypeError("wrapped call must return a CallResult (or use call_with_adapter)")
        usage = NormalizedUsage.from_call_result(result, self.provider)
        tier_after = self._record(usage, is_personal_time, request_id or result.request_id)
        return result.payload, tier_after

    def call_with_adapter(self, call_fn: Callable[[], object], *, is_personal_time: bool = False,
                          request_id: Optional[str] = None) -> tuple[object, Tier]:
        """v1.1 multi-engine entry point — call_fn returns a provider raw response; the configured
        EngineAdapter normalizes it. Same enforce-before / account-after discipline."""
        if self.adapter is None:
            raise ValueError("call_with_adapter requires an adapter")
        self._enforce(is_personal_time)
        raw = call_fn()
        usage = self.adapter.to_normalized_usage(raw)
        tier_after = self._record(usage, is_personal_time, request_id or usage.request_id)
        return raw, tier_after
