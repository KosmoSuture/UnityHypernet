"""
Hypernet LLM Provider Abstraction

Normalizes API differences between LLM providers (Anthropic, OpenAI, etc.)
so workers can use any supported model transparently.

Provider detection is automatic — the model name determines which provider
to use (e.g., "claude-*" → Anthropic, "gpt-*" → OpenAI).

Adding a new provider:
  1. Subclass LLMProvider
  2. Implement complete() and supports_model()
  3. Add to PROVIDER_REGISTRY

Reference: Plan at plans/scalable-petting-pine.md
"""

from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

log = logging.getLogger(__name__)


class ModelTier(Enum):
    """Cost tiers for LLM models — LOCAL is free, PREMIUM is expensive."""
    LOCAL = "local"
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"


# Cost per 1M tokens (input+output blended average) for known models.
# Local models are always 0.0. Prices are approximate and directional.
MODEL_COSTS: dict[str, float] = {
    # Local — free
    "local/": 0.0,
    "lmstudio/": 0.0,
    # Budget
    "gpt-4o-mini": 0.30,
    "gpt-4.1-mini": 0.30,
    "gpt-4.1-nano": 0.10,
    "claude-haiku": 1.00,
    # Standard
    "gpt-4o": 5.00,
    "gpt-4.1": 5.00,
    "claude-sonnet": 6.00,
    # Premium
    "claude-opus": 30.00,
    "o1": 30.00,
    "o3": 40.00,
    "o4": 40.00,
}


def get_model_tier(model: str) -> ModelTier:
    """Classify a model into a cost tier based on its name prefix."""
    m = model.lower()
    if m.startswith(("local/", "lmstudio/")):
        return ModelTier.LOCAL
    if "mini" in m or "nano" in m or "haiku" in m:
        return ModelTier.BUDGET
    if "opus" in m or m.startswith(("o1", "o3", "o4")):
        return ModelTier.PREMIUM
    return ModelTier.STANDARD


def get_model_cost_per_million(model: str) -> float:
    """Look up approximate cost per 1M tokens for a model.

    Uses longest prefix match against MODEL_COSTS.
    Returns 0.0 for unknown models (conservative — don't block).
    """
    m = model.lower()
    # Try exact match first, then prefix match (longest first)
    best_match = ""
    for prefix in sorted(MODEL_COSTS.keys(), key=len, reverse=True):
        if m.startswith(prefix.lower()):
            best_match = prefix
            break
    return MODEL_COSTS.get(best_match, 0.0)


class CreditsExhaustedError(Exception):
    """Raised when API credits/quota are exhausted (not a transient error)."""
    pass


class RateLimitError(Exception):
    """Raised when API returns 429 (transient, should retry with backoff)."""

    def __init__(self, message: str, retry_after: float = 0.0):
        super().__init__(message)
        self.retry_after = retry_after


def _retry_with_backoff(fn, max_retries: int = 3, base_delay: float = 2.0):
    """Call fn() with exponential backoff on transient errors.

    Retries on rate limits (429) and server errors (5xx).
    Raises CreditsExhaustedError immediately (no retry).
    Raises the last exception after all retries are exhausted.
    """
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except CreditsExhaustedError:
            raise  # No retry — credits are gone
        except Exception as e:
            last_exc = e
            err_str = str(e).lower()
            err_type = type(e).__name__.lower()

            # Detect credit/quota exhaustion — don't retry
            if any(kw in err_str for kw in [
                "insufficient_quota", "billing", "payment required",
                "exceeded your current quota", "credits",
                "account_deactivated",
            ]):
                raise CreditsExhaustedError(f"Credits exhausted: {e}") from e

            # Detect rate limits — retry with backoff
            is_rate_limit = (
                "rate" in err_str and "limit" in err_str
                or "429" in err_str
                or "too many requests" in err_str
                or "ratelimit" in err_type
                or "overloaded" in err_str
            )

            # Detect server errors — retry with backoff
            is_server_error = (
                "500" in err_str or "502" in err_str
                or "503" in err_str or "504" in err_str
                or "overloaded" in err_str
                or "internal" in err_str and "error" in err_str
            )

            if is_rate_limit or is_server_error:
                if attempt < max_retries:
                    # Check for Retry-After header hint
                    retry_after = getattr(e, 'retry_after', 0) or 0
                    delay = max(retry_after, base_delay * (2 ** attempt))
                    log.warning(
                        "API transient error (attempt %d/%d), retrying in %.1fs: %s",
                        attempt + 1, max_retries, delay, e,
                    )
                    time.sleep(delay)
                    continue
                else:
                    log.error(
                        "API transient error persisted after %d retries: %s",
                        max_retries, e,
                    )
                    raise

            # Unknown error — don't retry
            raise

    raise last_exc  # Should not reach here, but just in case


@dataclass
class LLMResponse:
    """Normalized response from any LLM provider."""

    text: str
    tokens_used: int
    model: str
    raw: Any = None
    cost_usd: float = 0.0


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    Each provider wraps a specific API (Anthropic, OpenAI, etc.) and
    normalizes the request/response format so Worker doesn't need to
    know which provider it's talking to.
    """

    name: str = ""

    @abstractmethod
    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Send a completion request and return a normalized response."""
        ...

    async def async_complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Async completion request. Default runs sync in executor.

        Providers that have native async clients should override this.
        Contributed by Lattice (2.1, The Architect).
        """
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.complete(model, system, messages, max_tokens),
        )

    @classmethod
    @abstractmethod
    def supports_model(cls, model: str) -> bool:
        """Check if this provider supports the given model name."""
        ...


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""

    name = "anthropic"
    KNOWN_PREFIXES = ("claude-",)

    def __init__(self, api_key: str):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)
        self._async_client = anthropic.AsyncAnthropic(api_key=api_key)

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        def _call():
            response = self._client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
            )
            tokens = response.usage.input_tokens + response.usage.output_tokens
            return LLMResponse(
                text=response.content[0].text,
                tokens_used=tokens,
                model=model,
                raw=response,
            )

        return _retry_with_backoff(_call)

    async def async_complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Native async completion via AsyncAnthropic."""
        response = await self._async_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        tokens = response.usage.input_tokens + response.usage.output_tokens
        return LLMResponse(
            text=response.content[0].text,
            tokens_used=tokens,
            model=model,
            raw=response,
        )

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(p) for p in cls.KNOWN_PREFIXES)


class LMStudioProvider(LLMProvider):
    """LM Studio local inference via OpenAI-compatible API.

    Connects to a locally running LM Studio server. No real API key needed.
    Start LM Studio, load a model, enable the local server, then use
    model names prefixed with "local/" (e.g., "local/qwen2.5-coder-7b-instruct").
    """

    name = "lmstudio"
    KNOWN_PREFIXES = ("local/", "lmstudio/")

    def __init__(self, api_key: str = "lm-studio", base_url: str = "http://localhost:1234/v1"):
        import openai

        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Strip the routing prefix (local/ or lmstudio/) to get the actual model ID
        actual_model = model.split("/", 1)[-1] if "/" in model else model
        full_messages = [{"role": "system", "content": system}] + messages
        response = self._client.chat.completions.create(
            model=actual_model,
            max_tokens=max_tokens,
            messages=full_messages,
        )
        tokens = response.usage.prompt_tokens + response.usage.completion_tokens
        return LLMResponse(
            text=response.choices[0].message.content,
            tokens_used=tokens,
            model=model,
            raw=response,
        )

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(p) for p in cls.KNOWN_PREFIXES)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT/O-series API provider."""

    name = "openai"
    KNOWN_PREFIXES = ("gpt-", "o1", "o3", "o4")

    def __init__(self, api_key: str):
        import openai

        self._client = openai.OpenAI(api_key=api_key)
        self._async_client = openai.AsyncOpenAI(api_key=api_key)

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        def _call():
            # OpenAI uses system role as a message rather than a separate param
            full_messages = [{"role": "system", "content": system}] + messages
            response = self._client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=full_messages,
            )
            tokens = response.usage.prompt_tokens + response.usage.completion_tokens
            return LLMResponse(
                text=response.choices[0].message.content,
                tokens_used=tokens,
                model=model,
                raw=response,
            )

        return _retry_with_backoff(_call)

    async def async_complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Native async completion via AsyncOpenAI."""
        full_messages = [{"role": "system", "content": system}] + messages
        response = await self._async_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=full_messages,
        )
        tokens = response.usage.prompt_tokens + response.usage.completion_tokens
        return LLMResponse(
            text=response.choices[0].message.content,
            tokens_used=tokens,
            model=model,
            raw=response,
        )

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(p) for p in cls.KNOWN_PREFIXES)


# =========================================================================
# Provider Registry — add new providers here
# =========================================================================

PROVIDER_REGISTRY: list[type[LLMProvider]] = [
    AnthropicProvider,
    LMStudioProvider,
    OpenAIProvider,
]

# Maps provider name to the config key that holds its API key
PROVIDER_KEY_MAP: dict[str, str] = {
    "anthropic": "anthropic_api_key",
    "lmstudio": "lmstudio_api_key",
    "openai": "openai_api_key",
}


def detect_provider_class(model: str) -> Optional[type[LLMProvider]]:
    """Return the provider class for a given model name, or None."""
    for provider_cls in PROVIDER_REGISTRY:
        if provider_cls.supports_model(model):
            return provider_cls
    return None


def create_provider(
    model: str,
    api_keys: dict[str, str],
) -> Optional[LLMProvider]:
    """Create the appropriate provider for a model, given available API keys.

    Args:
        model: Model name (e.g., "claude-opus-4-6", "gpt-4o")
        api_keys: Dict mapping key names to values
                  (e.g., {"anthropic_api_key": "sk-...", "openai_api_key": "sk-..."})

    Returns:
        An initialized LLMProvider, or None if the model isn't recognized
        or the required API key is missing.
    """
    provider_cls = detect_provider_class(model)
    if provider_cls is None:
        log.warning(f"No provider found for model '{model}'")
        return None

    # LM Studio runs locally — no real API key required
    if provider_cls.name == "lmstudio":
        try:
            return provider_cls(api_key=api_keys.get("lmstudio_api_key", "lm-studio"))
        except ImportError:
            log.warning("LM Studio provider needs the 'openai' package. Install with: pip install openai")
            return None

    key_name = PROVIDER_KEY_MAP.get(provider_cls.name)
    if not key_name or not api_keys.get(key_name):
        log.warning(
            f"Provider '{provider_cls.name}' needs key '{key_name}' "
            f"but it's not in api_keys"
        )
        return None

    try:
        return provider_cls(api_key=api_keys[key_name])
    except ImportError:
        log.warning(
            f"Provider '{provider_cls.name}' package not installed. "
            f"Install with: pip install {provider_cls.name}"
        )
        return None
