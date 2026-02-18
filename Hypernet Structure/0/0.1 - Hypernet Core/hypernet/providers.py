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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

log = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Normalized response from any LLM provider."""

    text: str
    tokens_used: int
    model: str
    raw: Any = None


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

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
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

    def complete(
        self,
        model: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
    ) -> LLMResponse:
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

    @classmethod
    def supports_model(cls, model: str) -> bool:
        return any(model.startswith(p) for p in cls.KNOWN_PREFIXES)


# =========================================================================
# Provider Registry — add new providers here
# =========================================================================

PROVIDER_REGISTRY: list[type[LLMProvider]] = [
    AnthropicProvider,
    OpenAIProvider,
]

# Maps provider name to the config key that holds its API key
PROVIDER_KEY_MAP: dict[str, str] = {
    "anthropic": "anthropic_api_key",
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
