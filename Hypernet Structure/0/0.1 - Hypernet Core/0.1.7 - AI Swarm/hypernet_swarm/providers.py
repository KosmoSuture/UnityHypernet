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
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Union

log = logging.getLogger(__name__)


class KeyRotator:
    """Round-robin API key rotation for multiplied rate limits.

    When a user has multiple API keys (e.g., 4 Google accounts = 4 Gemini
    keys), this rotator cycles through them to multiply effective rate limits.
    Thread-safe for concurrent worker access.
    """

    def __init__(self, keys: list[str]):
        if not keys:
            raise ValueError("KeyRotator requires at least one key")
        self._keys = list(keys)
        self._index = 0
        self._lock = threading.Lock()

    def next(self) -> str:
        """Return the next key in round-robin order."""
        with self._lock:
            key = self._keys[self._index % len(self._keys)]
            self._index += 1
            return key

    def current_index(self) -> int:
        """Return the current index (for debugging)."""
        return (self._index - 1) % len(self._keys)

    def count(self) -> int:
        """Return the number of keys in rotation."""
        return len(self._keys)

    def __len__(self) -> int:
        return len(self._keys)

    def __repr__(self) -> str:
        return f"KeyRotator({self.count()} keys, index={self._index % len(self._keys)})"


def _normalize_keys(api_key: Union[str, list[str]]) -> list[str]:
    """Normalize a single key or list of keys into a list, filtering blanks."""
    if isinstance(api_key, list):
        return [k for k in api_key if k and k.strip()]
    if api_key and api_key.strip():
        return [api_key.strip()]
    return []


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
    "ollama/": 0.0,
    # Free-tier providers (cost is $0 within limits)
    "gemini/": 0.0,
    "groq/": 0.0,
    "cerebras/": 0.0,
    "openrouter/": 0.0,
    # Very cheap
    "deepseek/": 0.35,
    "mistral/": 0.50,
    "together/": 0.50,
    "cohere/": 0.50,
    "huggingface/": 0.50,
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
    "claude-code/": 15.00,  # Estimated — Claude Code uses Sonnet/Opus internally
    "o1": 30.00,
    "o3": 40.00,
    "o4": 40.00,
}


def get_model_tier(model: str) -> ModelTier:
    """Classify a model into a cost tier based on its name prefix."""
    m = model.lower()
    if m.startswith(("local/", "lmstudio/", "ollama/")):
        return ModelTier.LOCAL
    # Free-tier cloud providers (within rate limits)
    if m.startswith(("gemini/", "groq/", "cerebras/", "openrouter/")):
        return ModelTier.LOCAL  # Free = LOCAL tier for budget purposes
    if "mini" in m or "nano" in m or "haiku" in m:
        return ModelTier.BUDGET
    if m.startswith(("deepseek/", "mistral/", "together/", "cohere/", "huggingface/")):
        return ModelTier.BUDGET
    if "opus" in m or m.startswith(("o1", "o3", "o4", "claude-code/")):
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
    """Anthropic Claude API provider.

    Supports multiple API keys for multiplied rate limits. If given a list
    of keys, creates one client per key and rotates through them. On a 429
    rate limit, automatically tries the next key before backing off.
    """

    name = "anthropic"
    KNOWN_PREFIXES = ("claude-",)

    def __init__(self, api_key: Union[str, list[str]]):
        import anthropic

        keys = _normalize_keys(api_key)
        if not keys:
            raise ValueError("AnthropicProvider requires at least one API key")

        self._clients = [anthropic.Anthropic(api_key=k) for k in keys]
        self._async_clients = [anthropic.AsyncAnthropic(api_key=k) for k in keys]
        self._key_index = 0
        self._key_count = len(keys)
        self._lock = threading.Lock()

        # Backward compatibility: single client references
        self._client = self._clients[0]
        self._async_client = self._async_clients[0]

        if self._key_count > 1:
            log.info("AnthropicProvider initialized with %d API keys (rate limit multiplier)", self._key_count)

    def _next_client_index(self) -> int:
        """Get the next client index in round-robin order (thread-safe)."""
        with self._lock:
            idx = self._key_index % self._key_count
            self._key_index += 1
            return idx

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        last_exc = None
        for attempt in range(self._key_count):
            idx = self._next_client_index()
            client = self._clients[idx]

            def _call(c=client, key_idx=idx):
                response = c.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=messages,
                )
                tokens = response.usage.input_tokens + response.usage.output_tokens
                if self._key_count > 1:
                    log.debug("Anthropic request completed using key #%d", key_idx + 1)
                return LLMResponse(
                    text=response.content[0].text,
                    tokens_used=tokens,
                    model=model,
                    raw=response,
                )

            try:
                return _retry_with_backoff(_call)
            except Exception as e:
                last_exc = e
                err_str = str(e).lower()
                is_rate_limit = (
                    "rate" in err_str and "limit" in err_str
                    or "429" in err_str
                    or "too many requests" in err_str
                    or "overloaded" in err_str
                )
                if is_rate_limit and attempt < self._key_count - 1:
                    log.info(
                        "Anthropic key #%d hit rate limit, rotating to next key (%d/%d)",
                        idx + 1, attempt + 2, self._key_count,
                    )
                    continue
                raise

        raise last_exc

    async def async_complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Native async completion via AsyncAnthropic with key rotation."""
        last_exc = None
        for attempt in range(self._key_count):
            idx = self._next_client_index()
            async_client = self._async_clients[idx]
            try:
                response = await async_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=messages,
                )
                tokens = response.usage.input_tokens + response.usage.output_tokens
                if self._key_count > 1:
                    log.debug("Anthropic async request completed using key #%d", idx + 1)
                return LLMResponse(
                    text=response.content[0].text,
                    tokens_used=tokens,
                    model=model,
                    raw=response,
                )
            except Exception as e:
                last_exc = e
                err_str = str(e).lower()
                is_rate_limit = (
                    "rate" in err_str and "limit" in err_str
                    or "429" in err_str
                    or "too many requests" in err_str
                    or "overloaded" in err_str
                )
                if is_rate_limit and attempt < self._key_count - 1:
                    log.info(
                        "Anthropic key #%d hit rate limit (async), rotating to next key (%d/%d)",
                        idx + 1, attempt + 2, self._key_count,
                    )
                    continue
                raise

        raise last_exc

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

        def _call():
            response = self._client.chat.completions.create(
                model=actual_model,
                max_tokens=max_tokens,
                messages=full_messages,
            )
            usage = getattr(response, "usage", None)
            tokens = (usage.prompt_tokens + usage.completion_tokens) if usage else 0
            text = response.choices[0].message.content if response.choices else ""
            return LLMResponse(
                text=text,
                tokens_used=tokens,
                model=model,
                raw=response,
            )

        return _retry_with_backoff(_call, max_retries=2, base_delay=1.0)

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(p) for p in cls.KNOWN_PREFIXES)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT/O-series API provider.

    Supports multiple API keys for multiplied rate limits. If given a list
    of keys, creates one client per key and rotates through them. On a 429
    rate limit, automatically tries the next key before backing off.
    """

    name = "openai"
    KNOWN_PREFIXES = ("gpt-", "o1", "o3", "o4")

    def __init__(self, api_key: Union[str, list[str]]):
        import openai

        keys = _normalize_keys(api_key)
        if not keys:
            raise ValueError("OpenAIProvider requires at least one API key")

        self._clients = [openai.OpenAI(api_key=k) for k in keys]
        self._async_clients = [openai.AsyncOpenAI(api_key=k) for k in keys]
        self._key_index = 0
        self._key_count = len(keys)
        self._lock = threading.Lock()

        # Backward compatibility
        self._client = self._clients[0]
        self._async_client = self._async_clients[0]

        if self._key_count > 1:
            log.info("OpenAIProvider initialized with %d API keys (rate limit multiplier)", self._key_count)

    def _next_client_index(self) -> int:
        """Get the next client index in round-robin order (thread-safe)."""
        with self._lock:
            idx = self._key_index % self._key_count
            self._key_index += 1
            return idx

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        full_messages = [{"role": "system", "content": system}] + messages
        last_exc = None
        for attempt in range(self._key_count):
            idx = self._next_client_index()
            client = self._clients[idx]

            def _call(c=client, key_idx=idx):
                response = c.chat.completions.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=full_messages,
                )
                tokens = response.usage.prompt_tokens + response.usage.completion_tokens
                if self._key_count > 1:
                    log.debug("OpenAI request completed using key #%d", key_idx + 1)
                return LLMResponse(
                    text=response.choices[0].message.content,
                    tokens_used=tokens,
                    model=model,
                    raw=response,
                )

            try:
                return _retry_with_backoff(_call)
            except Exception as e:
                last_exc = e
                err_str = str(e).lower()
                is_rate_limit = (
                    "rate" in err_str and "limit" in err_str
                    or "429" in err_str
                    or "too many requests" in err_str
                    or "overloaded" in err_str
                )
                if is_rate_limit and attempt < self._key_count - 1:
                    log.info(
                        "OpenAI key #%d hit rate limit, rotating to next key (%d/%d)",
                        idx + 1, attempt + 2, self._key_count,
                    )
                    continue
                raise

        raise last_exc

    async def async_complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Native async completion via AsyncOpenAI with key rotation."""
        full_messages = [{"role": "system", "content": system}] + messages
        last_exc = None
        for attempt in range(self._key_count):
            idx = self._next_client_index()
            async_client = self._async_clients[idx]
            try:
                response = await async_client.chat.completions.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=full_messages,
                )
                tokens = response.usage.prompt_tokens + response.usage.completion_tokens
                if self._key_count > 1:
                    log.debug("OpenAI async request completed using key #%d", idx + 1)
                return LLMResponse(
                    text=response.choices[0].message.content,
                    tokens_used=tokens,
                    model=model,
                    raw=response,
                )
            except Exception as e:
                last_exc = e
                err_str = str(e).lower()
                is_rate_limit = (
                    "rate" in err_str and "limit" in err_str
                    or "429" in err_str
                    or "too many requests" in err_str
                    or "overloaded" in err_str
                )
                if is_rate_limit and attempt < self._key_count - 1:
                    log.info(
                        "OpenAI key #%d hit rate limit (async), rotating to next key (%d/%d)",
                        idx + 1, attempt + 2, self._key_count,
                    )
                    continue
                raise

        raise last_exc

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(p) for p in cls.KNOWN_PREFIXES)


class OpenAICompatibleProvider(LLMProvider):
    """Generic provider for any OpenAI-compatible API endpoint.

    Works with: Google Gemini, Groq, Cerebras, Mistral, Together.ai,
    DeepSeek, Cohere, HuggingFace, OpenRouter, Ollama, and any other
    provider that implements the OpenAI chat completions API.

    Model names use a prefix to route to the correct provider:
        gemini/gemini-2.5-flash, groq/llama-3.3-70b-versatile, etc.
    """

    # Registry of known OpenAI-compatible providers
    # Maps prefix → (display_name, base_url, config_key, needs_api_key)
    ENDPOINTS: dict[str, tuple[str, str, str, bool]] = {
        "gemini/": ("Google Gemini", "https://generativelanguage.googleapis.com/v1beta/openai/", "gemini_api_key", True),
        "groq/": ("Groq", "https://api.groq.com/openai/v1", "groq_api_key", True),
        "cerebras/": ("Cerebras", "https://api.cerebras.ai/v1", "cerebras_api_key", True),
        "mistral/": ("Mistral", "https://api.mistral.ai/v1", "mistral_api_key", True),
        "together/": ("Together.ai", "https://api.together.xyz/v1", "together_api_key", True),
        "deepseek/": ("DeepSeek", "https://api.deepseek.com/v1", "deepseek_api_key", True),
        "cohere/": ("Cohere", "https://api.cohere.ai/compatibility/v1", "cohere_api_key", True),
        "huggingface/": ("HuggingFace", "https://router.huggingface.co/v1", "huggingface_api_key", True),
        "openrouter/": ("OpenRouter", "https://openrouter.ai/api/v1", "openrouter_api_key", True),
        "ollama/": ("Ollama", "http://localhost:11434/v1", "ollama_api_key", False),
    }

    def __init__(self, prefix: str, api_key: Union[str, list[str]], base_url: str, display_name: str = ""):
        import openai

        self._prefix = prefix
        self.name = display_name or prefix.rstrip("/")

        keys = _normalize_keys(api_key) if api_key else ["none"]
        if not keys:
            keys = ["none"]

        self._clients = [openai.OpenAI(api_key=k, base_url=base_url) for k in keys]
        self._key_index = 0
        self._key_count = len(keys)
        self._lock = threading.Lock()

        # Backward compatibility
        self._client = self._clients[0]

        if self._key_count > 1:
            log.info(
                "%s provider initialized with %d API keys (rate limit multiplier)",
                self.name, self._key_count,
            )

    def _next_client_index(self) -> int:
        """Get the next client index in round-robin order (thread-safe)."""
        with self._lock:
            idx = self._key_index % self._key_count
            self._key_index += 1
            return idx

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Strip the routing prefix to get the actual model ID
        actual_model = model.split("/", 1)[-1] if "/" in model else model
        full_messages = [{"role": "system", "content": system}] + messages

        last_exc = None
        for attempt in range(self._key_count):
            idx = self._next_client_index()
            client = self._clients[idx]

            def _call(c=client, key_idx=idx):
                response = c.chat.completions.create(
                    model=actual_model,
                    max_tokens=max_tokens,
                    messages=full_messages,
                )
                usage = getattr(response, "usage", None)
                tokens = 0
                if usage:
                    tokens = (getattr(usage, "prompt_tokens", 0) or 0) + (getattr(usage, "completion_tokens", 0) or 0)
                text = response.choices[0].message.content if response.choices else ""
                if self._key_count > 1:
                    log.debug("%s request completed using key #%d", self.name, key_idx + 1)
                return LLMResponse(
                    text=text,
                    tokens_used=tokens,
                    model=model,
                    raw=response,
                )

            try:
                return _retry_with_backoff(_call, max_retries=2, base_delay=2.0)
            except Exception as e:
                last_exc = e
                err_str = str(e).lower()
                is_rate_limit = (
                    "rate" in err_str and "limit" in err_str
                    or "429" in err_str
                    or "too many requests" in err_str
                    or "overloaded" in err_str
                )
                if is_rate_limit and attempt < self._key_count - 1:
                    log.info(
                        "%s key #%d hit rate limit, rotating to next key (%d/%d)",
                        self.name, idx + 1, attempt + 2, self._key_count,
                    )
                    continue
                raise

        raise last_exc

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(prefix) for prefix in cls.ENDPOINTS)

    @classmethod
    def get_endpoint_info(cls, model: str) -> Optional[tuple[str, str, str, str, bool]]:
        """Return (prefix, display_name, base_url, config_key, needs_key) for a model."""
        for prefix, (name, url, key, needs) in cls.ENDPOINTS.items():
            if model.startswith(prefix):
                return prefix, name, url, key, needs
        return None


class ClaudeCodeProvider(LLMProvider):
    """Provider that spawns Claude Code CLI instances as autonomous agents.

    Instead of making API calls, this provider launches `claude` CLI processes
    in headless mode with full permissions. Each "completion" runs an entire
    Claude Code session that can read/write files, run commands, and execute
    complex multi-step tasks.

    Model names: "claude-code/sonnet", "claude-code/opus", "claude-code/haiku"
    The part after "claude-code/" specifies the model variant.

    This is NOT a standard LLM provider — it's a full agent runtime.
    Tasks assigned to Claude Code workers should be high-level directives,
    not simple chat completions.
    """

    name = "claude-code"
    KNOWN_PREFIXES = ("claude-code/",)

    def __init__(self, working_dir: str = ".", max_turns: int = 50, max_budget_usd: float = 5.0):
        self._working_dir = working_dir
        self._max_turns = max_turns
        self._max_budget_usd = max_budget_usd
        # Find claude CLI — check PATH + common install locations
        self._claude_path = self._find_claude()
        if not self._claude_path:
            raise FileNotFoundError(
                "Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )

    @staticmethod
    def _find_claude(explicit_path: str = "") -> Optional[str]:
        """Find the claude CLI executable, checking PATH and common locations."""
        import shutil
        import os
        from pathlib import Path as _P

        # Explicit path from config takes priority
        if explicit_path and _P(explicit_path).exists():
            return explicit_path

        # Check PATH
        found = shutil.which("claude")
        if found:
            return found

        # Check common install locations (npm global, .local/bin, AppData)
        # Try multiple user home detection methods (services may have different HOME)
        homes = set()
        for var in ("USERPROFILE", "HOME", "HOMEDRIVE"):
            val = os.environ.get(var, "")
            if var == "HOMEDRIVE":
                val = val + os.environ.get("HOMEPATH", "")
            if val:
                homes.add(_P(val))
        homes.add(_P.home())

        candidates = []
        for home in homes:
            candidates.extend([
                home / ".local" / "bin" / "claude.exe",
                home / ".local" / "bin" / "claude",
                home / "AppData" / "Roaming" / "npm" / "claude.cmd",
                home / "AppData" / "Roaming" / "npm" / "claude",
            ])
        # Also check standard system locations
        candidates.extend([
            _P(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd",
            _P(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / "claude.exe",
            _P("C:/Users/spamm/.local/bin/claude.exe"),  # Hardcoded fallback for this system
        ])

        for c in candidates:
            try:
                if c.exists():
                    return str(c)
            except (OSError, ValueError):
                continue
        return None

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
        import subprocess
        import json

        # Extract model variant (e.g., "claude-code/sonnet" → "sonnet")
        variant = model.split("/", 1)[-1] if "/" in model else "sonnet"

        # Build the prompt from system + messages
        prompt_parts = []
        if system:
            prompt_parts.append(system)
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                prompt_parts.append(content)
        full_prompt = "\n\n".join(prompt_parts)

        # Build Claude Code CLI command
        cmd = [
            self._claude_path,
            "-p", full_prompt,
            "--dangerously-skip-permissions",
            "--output-format", "json",
            "--model", variant,
            "--max-turns", str(self._max_turns),
        ]

        log.info(
            "Launching Claude Code instance: model=%s, working_dir=%s, prompt_len=%d",
            variant, self._working_dir, len(full_prompt),
        )

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self._working_dir,
                timeout=600,  # 10 minute timeout per task
                env=None,  # Inherit environment
            )

            # Parse JSON output
            output_text = result.stdout.strip()
            session_id = None
            cost = 0.0

            if output_text:
                try:
                    output_data = json.loads(output_text)
                    output_text = output_data.get("result", output_text)
                    session_id = output_data.get("session_id")
                    cost = output_data.get("cost_usd", 0.0)
                    # Token usage from Claude Code output
                    usage = output_data.get("usage", {})
                    tokens = usage.get("total_tokens", 0)
                except json.JSONDecodeError:
                    tokens = len(output_text) // 4  # Rough estimate
            else:
                output_text = result.stderr.strip() or "(no output)"
                tokens = 0

            if result.returncode != 0 and not output_text:
                output_text = f"Claude Code exited with code {result.returncode}: {result.stderr[:500]}"

            return LLMResponse(
                text=output_text,
                tokens_used=tokens,
                model=model,
                raw={"session_id": session_id, "returncode": result.returncode},
                cost_usd=cost,
            )

        except subprocess.TimeoutExpired:
            log.warning("Claude Code session timed out after 600s")
            return LLMResponse(
                text="[Claude Code session timed out after 10 minutes]",
                tokens_used=0,
                model=model,
                raw={"error": "timeout"},
            )
        except FileNotFoundError:
            raise FileNotFoundError(
                "Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(p) for p in cls.KNOWN_PREFIXES)


# =========================================================================
# Provider Registry — add new providers here
# =========================================================================

PROVIDER_REGISTRY: list[type[LLMProvider]] = [
    ClaudeCodeProvider,      # Must be before Anthropic — "claude-code/" is more specific than "claude-"
    AnthropicProvider,
    LMStudioProvider,
    OpenAIProvider,
    OpenAICompatibleProvider,
]

# Maps provider name to the config key that holds its API key
PROVIDER_KEY_MAP: dict[str, str] = {
    "anthropic": "anthropic_api_key",
    "lmstudio": "lmstudio_api_key",
    "openai": "openai_api_key",
    "claude-code": "",  # No API key needed (uses Claude Code's own auth)
}

# Add all OpenAI-compatible provider key mappings
for _prefix, (_name, _url, _key, _needs) in OpenAICompatibleProvider.ENDPOINTS.items():
    PROVIDER_KEY_MAP[_prefix.rstrip("/")] = _key


def detect_provider_class(model: str) -> Optional[type[LLMProvider]]:
    """Return the provider class for a given model name, or None."""
    for provider_cls in PROVIDER_REGISTRY:
        if provider_cls.supports_model(model):
            return provider_cls
    return None


def create_provider(
    model: str,
    api_keys: dict[str, Union[str, list[str]]],
) -> Optional[LLMProvider]:
    """Create the appropriate provider for a model, given available API keys.

    Args:
        model: Model name (e.g., "claude-opus-4-6", "gpt-4o", "gemini/gemini-2.5-flash")
        api_keys: Dict mapping key names to values. Values can be a single string
                  or a list of strings for multi-key rotation.
                  (e.g., {"anthropic_api_key": "sk-...", "gemini_api_key": ["key1", "key2"]})

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
            base_url = api_keys.get("lmstudio_base_url", "http://localhost:1234/v1")
            return provider_cls(
                api_key=api_keys.get("lmstudio_api_key", "lm-studio"),
                base_url=base_url,
            )
        except ImportError:
            log.warning("LM Studio provider needs the 'openai' package. Install with: pip install openai")
            return None

    # OpenAI-compatible providers (Gemini, Groq, Cerebras, etc.)
    if provider_cls is OpenAICompatibleProvider:
        info = OpenAICompatibleProvider.get_endpoint_info(model)
        if not info:
            return None
        prefix, display_name, base_url, config_key, needs_key = info
        api_key = api_keys.get(config_key, "")
        # Check if key is present — supports both str and list[str]
        has_key = bool(api_key) if isinstance(api_key, str) else bool(_normalize_keys(api_key))
        if needs_key and not has_key:
            log.warning(
                f"Provider '{display_name}' needs key '{config_key}' "
                f"but it's not configured. Add it to secrets/config.json"
            )
            return None
        try:
            return OpenAICompatibleProvider(
                prefix=prefix,
                api_key=api_key,
                base_url=base_url,
                display_name=display_name,
            )
        except ImportError:
            log.warning(f"OpenAI-compatible provider needs the 'openai' package.")
            return None

    # Claude Code — spawns CLI instances
    if provider_cls is ClaudeCodeProvider:
        try:
            working_dir = api_keys.get("claude_code_working_dir", ".")
            max_turns = int(api_keys.get("claude_code_max_turns", "50"))
            max_budget = float(api_keys.get("claude_code_max_budget_usd", "5.0"))
            explicit_path = api_keys.get("claude_code_cli_path", "")
            provider = ClaudeCodeProvider.__new__(ClaudeCodeProvider)
            provider._working_dir = working_dir
            provider._max_turns = max_turns
            provider._max_budget_usd = max_budget
            provider._claude_path = ClaudeCodeProvider._find_claude(explicit_path)
            if not provider._claude_path:
                log.warning("Claude Code provider: Claude Code CLI not found. Install with: npm install -g @anthropic-ai/claude-code")
                return None
            provider.name = "claude-code"
            return provider
        except Exception as e:
            log.warning(f"Claude Code provider: {e}")
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
