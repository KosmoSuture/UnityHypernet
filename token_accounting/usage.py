"""
Normalized usage + cost models (round-2 design item #3; Codex #3).

Replaces v1.0's two-rate `price(model)->(in_per_1k,out_per_1k)` tuple — which only fit
token-count, two-rate engines — with a CostModel that estimates from a NormalizedUsage and a
PricingContext. This generalizes to per-modality / per-unit billing and to engines that do not
return token counts synchronously.

Backwards compat (R7): the default TokenCostModel reproduces v1.0's math exactly, and the
module-level `estimate_cost_usd(model, in, out)` shim returns identical values, so the 22-check
harness (which imports it via wrapper) passes unchanged.

Standard library only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional, Protocol


# USD per 1,000 tokens (input, output). Estimates; the reconciler corrects drift later.
PRICING: dict[str, tuple[float, float]] = {
    "claude-opus-4-8": (0.015, 0.075),
    "claude-sonnet-4-6": (0.003, 0.015),
    "claude-haiku-4-5": (0.0008, 0.004),
    "codex": (0.010, 0.030),
    "gpt-5.2": (0.010, 0.030),
}
DEFAULT_PRICE: tuple[float, float] = (0.010, 0.030)


@dataclass
class NormalizedUsage:
    """One call's usage, normalized across engines (Codex #3).

    Preserves the common token fields WHEN AVAILABLE, plus arbitrary per-modality dimensions and
    the raw provider response, plus where the numbers came from and the provider/request ids for
    reconciliation.
    """
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    usage_dimensions: dict = field(default_factory=dict)   # e.g. {"image_units": 3, "cached_input_tokens": 200}
    raw_usage: Optional[object] = None                     # provider response verbatim
    estimation_source: str = "provider-response"           # provider-response | externally-estimated | disclosed
    provider: Optional[str] = None
    request_id: Optional[str] = None

    # -- serialization for the ledger (json columns) --
    def dimensions_json(self) -> Optional[str]:
        return json.dumps(self.usage_dimensions, sort_keys=True, separators=(",", ":")) if self.usage_dimensions else None

    def raw_json(self) -> Optional[str]:
        if self.raw_usage is None:
            return None
        try:
            return json.dumps(self.raw_usage, sort_keys=True, separators=(",", ":"), default=str)
        except (TypeError, ValueError):
            return json.dumps(str(self.raw_usage))

    @classmethod
    def from_call_result(cls, result, provider: Optional[str] = None) -> "NormalizedUsage":
        """Map a legacy CallResult into NormalizedUsage (R7 bridge)."""
        return cls(input_tokens=result.input_tokens, output_tokens=result.output_tokens,
                   estimation_source="provider-response", provider=provider,
                   request_id=getattr(result, "request_id", None))


@dataclass(frozen=True)
class PricingContext:
    region: Optional[str] = None
    batch: bool = False
    extra: dict = field(default_factory=dict)


@dataclass(frozen=True)
class CostEstimate:
    cost_usd: float
    basis: str  # how it was computed (for audit/reconciliation)


class CostModel(Protocol):
    def estimate(self, usage: NormalizedUsage, model: str, context: Optional[PricingContext]) -> CostEstimate: ...


class TokenCostModel:
    """Default token-based cost model — reproduces v1.0 math EXACTLY (R7)."""

    def estimate(self, usage: NormalizedUsage, model: str, context: Optional[PricingContext] = None) -> CostEstimate:
        pin, pout = PRICING.get(model, DEFAULT_PRICE)
        it = usage.input_tokens or 0
        ot = usage.output_tokens or 0
        cost = (it / 1000.0) * pin + (ot / 1000.0) * pout
        return CostEstimate(cost_usd=cost, basis=f"token:{model}")


class PerUnitCostModel:
    """Example NON-two-rate, NON-token cost model — proves CostModel generality (AC2).

    Prices arbitrary usage_dimensions by a per-unit rate table (e.g. image units, audio seconds),
    optionally plus a per-request fee. Demonstrates an engine whose billing is not input/output
    token pricing.
    """

    def __init__(self, unit_rates_usd: dict[str, float], per_request_fee_usd: float = 0.0):
        self._rates = dict(unit_rates_usd)
        self._fee = per_request_fee_usd

    def estimate(self, usage: NormalizedUsage, model: str, context: Optional[PricingContext] = None) -> CostEstimate:
        cost = self._fee
        for dim, units in usage.usage_dimensions.items():
            cost += self._rates.get(dim, 0.0) * float(units)
        return CostEstimate(cost_usd=cost, basis=f"per-unit:{model}:{sorted(self._rates)}")


# ----------------------------------------------------------------------------------------------
# Backwards-compat shim (R7): the v1.0 module-level function. Must return identical values.
# ----------------------------------------------------------------------------------------------

_DEFAULT_TOKEN_COST_MODEL = TokenCostModel()


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """v1.0 API preserved — identical results, now delegating to TokenCostModel."""
    return _DEFAULT_TOKEN_COST_MODEL.estimate(
        NormalizedUsage(input_tokens=input_tokens, output_tokens=output_tokens), model, None
    ).cost_usd
