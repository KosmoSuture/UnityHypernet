"""
Engine adapters (round-2 design items #1/#3; R1/R2).

An EngineAdapter normalizes a provider's native usage report into a NormalizedUsage. The
enforcement core lives ABOVE adapters, so enforcement is identical for every engine; the only
per-engine code is "how do I read this provider's usage." Adding an engine = one adapter + one
CostModel entry, with no core/ledger/chain change (Matt Q2 "work with anything").

Standard library only.
"""

from __future__ import annotations

from typing import Optional, Protocol

from .usage import NormalizedUsage


class EngineAdapter(Protocol):
    engine_id: str

    def to_normalized_usage(self, raw_response: object) -> NormalizedUsage: ...


class ClaudeAdapter:
    """Anthropic SDK: response.usage.input_tokens / output_tokens (v1.0 behavior, formalized)."""

    engine_id = "claude"

    def to_normalized_usage(self, raw_response: object) -> NormalizedUsage:
        # Accept either an SDK object with `.usage` or a dict carrying a "usage" key.
        if isinstance(raw_response, dict):
            usage = raw_response.get("usage", raw_response)
        else:
            usage = getattr(raw_response, "usage", raw_response)
        it = _get(usage, "input_tokens")
        ot = _get(usage, "output_tokens")
        dims = {}
        cached = _get(usage, "cache_read_input_tokens")
        if cached is not None:
            dims["cache_read_input_tokens"] = cached
        return NormalizedUsage(input_tokens=it, output_tokens=ot, usage_dimensions=dims,
                               raw_usage=_safe(usage), estimation_source="provider-response",
                               provider="anthropic", request_id=_get(raw_response, "id"))


class CodexAdapter:
    """Codex CLI `codex exec --json`: per-call usage events carry input/output token counts.

    Brings the Codex path to PARITY with Claude (the v1.1 core job): identical NormalizedUsage,
    so one ledger logs the same data regardless of vendor.
    """

    engine_id = "codex"

    def to_normalized_usage(self, raw_response: object) -> NormalizedUsage:
        # Accept either a parsed usage dict from the --json stream or an object with .usage.
        usage = raw_response.get("usage") if isinstance(raw_response, dict) else getattr(raw_response, "usage", raw_response)
        it = _get(usage, "input_tokens")
        ot = _get(usage, "output_tokens")
        rid = (raw_response.get("id") if isinstance(raw_response, dict) else _get(raw_response, "id"))
        return NormalizedUsage(input_tokens=it, output_tokens=ot, raw_usage=_safe(usage),
                               estimation_source="provider-response", provider="openai", request_id=rid)


class DummyImageEngineAdapter:
    """Example engine whose usage is NOT input/output token counts (AC2).

    Reports per-modality units (e.g. image units) — proves the adapter + CostModel path handles
    non-token, non-two-rate billing without touching the core.
    """

    engine_id = "dummy-image"

    def to_normalized_usage(self, raw_response: object) -> NormalizedUsage:
        d = raw_response if isinstance(raw_response, dict) else {}
        return NormalizedUsage(
            input_tokens=None, output_tokens=None,
            usage_dimensions={"image_units": d.get("image_units", 0), "audio_seconds": d.get("audio_seconds", 0)},
            raw_usage=d, estimation_source=d.get("estimation_source", "provider-response"),
            provider="dummy", request_id=d.get("id"),
        )


# Registry: engine_id -> adapter instance. Add an engine by registering its adapter.
ADAPTERS: dict[str, EngineAdapter] = {
    a.engine_id: a for a in (ClaudeAdapter(), CodexAdapter(), DummyImageEngineAdapter())
}


def register_adapter(adapter: EngineAdapter) -> None:
    ADAPTERS[adapter.engine_id] = adapter


def get_adapter(engine_id: str) -> Optional[EngineAdapter]:
    return ADAPTERS.get(engine_id)


def _get(obj, name):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(name)
    return getattr(obj, name, None)


def _safe(obj):
    if isinstance(obj, (dict, list, str, int, float, bool)) or obj is None:
        return obj
    # best-effort: expose simple attributes
    out = {}
    for k in ("input_tokens", "output_tokens", "cache_read_input_tokens"):
        v = _get(obj, k)
        if v is not None:
            out[k] = v
    return out or str(obj)
