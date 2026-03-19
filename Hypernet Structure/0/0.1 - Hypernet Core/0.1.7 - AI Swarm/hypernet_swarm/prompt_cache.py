"""
Hypernet Prompt Cache Manager

Manages system prompt caching for Anthropic Claude API to achieve 90%
discount on cached input tokens. OpenAI caches automatically for prompts
over 1024 tokens — no extra code needed.

Anthropic caching strategy:
  - The system prompt (boot sequence) is largely identical across workers
    on the same account. We split it into a cacheable prefix (core identity
    docs, system docs, governance) and a dynamic suffix (instance-specific
    files, recent messages, session history).
  - The cacheable prefix gets cache_control: {"type": "ephemeral"} on the
    last text block, which tells Anthropic to cache everything up to and
    including that block.
  - Cache TTL is 5 minutes, refreshed on each use. The swarm tick loop
    runs every 2 seconds, so active workers keep the cache warm.
  - First request pays a 25% surcharge on input tokens (cache write).
    Subsequent requests get 90% off cached tokens. Break-even at ~2 hits.

Cost savings math (claude-sonnet-4-6 at $3/M input):
  - System prompt: ~8K tokens
  - Without caching: 8K * $3/M = $0.024 per call
  - With caching (90% off): 8K * $0.30/M = $0.0024 per call
  - Savings: ~$0.022 per call, ~90%

Usage:
    cache_mgr = PromptCacheManager()
    system_blocks = cache_mgr.build_cached_system(
        identity_mgr, worker.identity
    )
    # Pass system_blocks as system= to Anthropic API instead of a string

Reference: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
"""

from __future__ import annotations
import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

log = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """Tracks prompt cache hit/miss rates."""
    cache_writes: int = 0       # Requests that wrote to cache (25% surcharge)
    cache_hits: int = 0         # Requests that read from cache (90% discount)
    total_requests: int = 0     # Total requests through the cache manager
    tokens_saved: int = 0       # Estimated tokens saved by caching
    cost_saved_usd: float = 0.0  # Estimated USD saved

    @property
    def hit_rate(self) -> float:
        """Cache hit rate as a fraction 0.0-1.0."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    @property
    def hit_rate_pct(self) -> str:
        """Cache hit rate as a human-readable percentage."""
        return f"{self.hit_rate * 100:.1f}%"

    def to_dict(self) -> dict:
        return {
            "cache_writes": self.cache_writes,
            "cache_hits": self.cache_hits,
            "total_requests": self.total_requests,
            "tokens_saved": self.tokens_saved,
            "cost_saved_usd": round(self.cost_saved_usd, 4),
            "hit_rate": self.hit_rate_pct,
        }


@dataclass
class CachedPrompt:
    """A system prompt split into cacheable prefix and dynamic suffix."""
    prefix_blocks: list[dict]   # Static blocks (core identity, system docs)
    suffix_blocks: list[dict]   # Dynamic blocks (instance-specific, messages)
    prefix_hash: str            # Hash of prefix content for cache invalidation
    created_at: float = 0.0     # time.time() when this was built
    token_estimate: int = 0     # Rough token count of prefix (chars / 4)


class PromptCacheManager:
    """Manages system prompt caching for the Anthropic API.

    Splits system prompts into a cacheable static prefix and a dynamic
    suffix. The prefix contains shared identity documents that are the
    same across workers on the same account. The suffix contains
    instance-specific data that changes between workers and sessions.

    For OpenAI, no special handling is needed — their API caches
    automatically. This manager still provides the split for consistency
    but doesn't add cache_control markers.
    """

    # Cache TTL for Anthropic is 5 minutes. We rebuild the prefix if
    # the underlying documents change (detected via content hash).
    CACHE_REBUILD_INTERVAL = 240.0  # Rebuild prefix every 4 minutes
    # (slightly under Anthropic's 5-minute TTL to avoid expiration gaps)

    def __init__(self):
        self._cached_prefixes: dict[str, CachedPrompt] = {}
        # Key: account_prefix (e.g., "2.1") → CachedPrompt
        self._stats = CacheStats()
        # Per-account stats
        self._account_stats: dict[str, CacheStats] = {}

    @property
    def stats(self) -> CacheStats:
        return self._stats

    def get_account_stats(self, account_prefix: str) -> CacheStats:
        """Get cache stats for a specific account."""
        return self._account_stats.get(account_prefix, CacheStats())

    def build_cached_system(
        self,
        identity_mgr: Any,
        profile: Any,
        provider_name: str = "anthropic",
    ) -> list[dict] | str:
        """Build a system prompt with caching support.

        For Anthropic: returns a list of content blocks with cache_control
        on the static prefix. Pass this as the `system` parameter.

        For OpenAI/other: returns a plain string (OpenAI caches automatically).

        Args:
            identity_mgr: IdentityManager instance
            profile: InstanceProfile for the worker
            provider_name: "anthropic", "openai", etc.

        Returns:
            For Anthropic: list[dict] with cache_control markers
            For others: str (plain system prompt)
        """
        self._stats.total_requests += 1

        # For non-Anthropic providers, return plain string
        if provider_name != "anthropic":
            return identity_mgr.build_system_prompt(profile)

        account_prefix = self._infer_account_prefix(identity_mgr, profile)
        account_stats = self._account_stats.setdefault(account_prefix, CacheStats())
        account_stats.total_requests += 1

        # Check if we have a valid cached prefix for this account
        now = time.time()
        cached = self._cached_prefixes.get(account_prefix)

        if cached and (now - cached.created_at) < self.CACHE_REBUILD_INTERVAL:
            # Reuse cached prefix — this is a cache hit
            self._stats.cache_hits += 1
            account_stats.cache_hits += 1

            # Estimate savings: cached prefix tokens * 90% discount
            # (vs paying full price without caching)
            saved_tokens = cached.token_estimate
            self._stats.tokens_saved += saved_tokens
            # Approximate cost savings (Claude Sonnet input: $3/M tokens)
            self._stats.cost_saved_usd += (saved_tokens / 1_000_000) * 2.70  # 90% of $3

            log.debug(
                "Prompt cache HIT for account %s (prefix=%d tokens, age=%.0fs)",
                account_prefix, cached.token_estimate, now - cached.created_at,
            )
        else:
            # Build new prefix — this is a cache write (25% surcharge on first use)
            prefix_blocks, prefix_hash, token_est = self._build_prefix(
                identity_mgr, profile, account_prefix,
            )
            cached = CachedPrompt(
                prefix_blocks=prefix_blocks,
                suffix_blocks=[],  # Will be filled per-request
                prefix_hash=prefix_hash,
                created_at=now,
                token_estimate=token_est,
            )
            self._cached_prefixes[account_prefix] = cached
            self._stats.cache_writes += 1
            account_stats.cache_writes += 1

            log.info(
                "Prompt cache WRITE for account %s (prefix=%d tokens, hash=%s)",
                account_prefix, token_est, prefix_hash[:12],
            )

        # Build dynamic suffix (instance-specific, always fresh)
        suffix_blocks = self._build_suffix(identity_mgr, profile)

        # Combine: prefix (with cache_control on last block) + suffix
        all_blocks = list(cached.prefix_blocks)  # Copy to avoid mutation
        if all_blocks:
            # Add cache_control to the last prefix block
            last_block = dict(all_blocks[-1])  # Copy
            last_block["cache_control"] = {"type": "ephemeral"}
            all_blocks[-1] = last_block
        all_blocks.extend(suffix_blocks)

        return all_blocks

    def _build_prefix(
        self,
        identity_mgr: Any,
        profile: Any,
        account_prefix: str,
    ) -> tuple[list[dict], str, int]:
        """Build the static (cacheable) prefix blocks.

        Contains:
          - Identity header
          - Core identity documents (account-specific)
          - System documents (shared governance, standards)

        These rarely change and are shared across all workers on the
        same account — ideal for caching.

        Returns: (blocks, content_hash, estimated_tokens)
        """
        sections = []

        # Account path resolution
        account_path = getattr(identity_mgr, '_account_paths', {}).get(
            account_prefix,
            getattr(identity_mgr, '_ai_root', None),
        )

        # Header (static per account)
        header = (
            f"You are an AI instance in the Hypernet — "
            f"a decentralized infrastructure for human-AI collaboration.\n"
            f"Your account: {account_prefix}.\n"
        )
        sections.append(header)

        # Core identity documents (account-specific, rarely change)
        account_core_docs = getattr(identity_mgr, 'ACCOUNT_CORE_DOCS', {})
        core_docs = account_core_docs.get(account_prefix, [])
        if not core_docs:
            core_docs = account_core_docs.get("2.1", [])

        for doc_name in core_docs:
            content = identity_mgr._load_doc(doc_name, search_root=account_path)
            if content:
                sections.append(f"## {doc_name}\n\n{content}")

        # System documents (shared governance standards — rarely change)
        system_docs = getattr(identity_mgr, 'SYSTEM_DOCS', [])
        for doc_name in system_docs:
            content = identity_mgr._load_doc(doc_name)
            if content:
                sections.append(f"## {doc_name}\n\n{content}")

        # Combine into content blocks
        full_text = "\n\n---\n\n".join(sections)
        content_hash = hashlib.sha256(full_text.encode()).hexdigest()
        token_estimate = len(full_text) // 4  # Rough: 1 token ~ 4 chars

        blocks = [{"type": "text", "text": full_text}]

        return blocks, content_hash, token_estimate

    def _build_suffix(
        self,
        identity_mgr: Any,
        profile: Any,
    ) -> list[dict]:
        """Build the dynamic (non-cached) suffix blocks.

        Contains instance-specific data that changes between workers:
          - Instance name and address
          - Instance-specific files (README, baseline, divergence)
          - Recent messages
          - Session history
          - Orientation and capabilities
        """
        sections = []

        # Instance identity (changes per worker)
        sections.append(
            f"Your name is {profile.name}.\n"
            f"Your Hypernet address is {profile.address}.\n"
        )

        # Instance-specific files
        result = identity_mgr._find_instance_dir(profile.name)
        instance_dir = result[0] if result else None
        if instance_dir:
            for filename in ["README.md", "baseline-responses.md", "divergence-log.md"]:
                filepath = instance_dir / filename
                if filepath.exists():
                    try:
                        content = filepath.read_text(encoding="utf-8")
                        sections.append(f"## Instance: {filename}\n\n{content}")
                    except Exception:
                        pass

        # Recent messages (changes frequently)
        messages = identity_mgr._load_recent_messages(5)
        if messages:
            sections.append(
                "## Recent Inter-Instance Messages\n\n"
                + "\n\n---\n\n".join(messages)
            )

        # Session history (changes per session)
        session_summary = identity_mgr._load_session_summary(profile.name)
        if session_summary:
            sections.append(f"## Previous Session Summary\n\n{session_summary}")

        # Orientation and capabilities (static per instance but different per worker)
        if profile.orientation:
            sections.append(f"## Your Orientation\n\n{profile.orientation}")
        if profile.capabilities:
            sections.append(
                "## Your Capabilities\n\n"
                + "\n".join(f"- {c}" for c in profile.capabilities)
            )

        full_text = "\n\n---\n\n".join(sections)
        return [{"type": "text", "text": full_text}] if full_text.strip() else []

    def _infer_account_prefix(self, identity_mgr: Any, profile: Any) -> str:
        """Determine account prefix from profile address."""
        addr = getattr(profile, 'address', '') or ''
        if addr.startswith("2.2."):
            return "2.2"
        if addr.startswith("2.3."):
            return "2.3"
        return "2.1"

    def invalidate(self, account_prefix: Optional[str] = None) -> None:
        """Force cache rebuild on next request.

        Args:
            account_prefix: If given, only invalidate that account's cache.
                          If None, invalidate all.
        """
        if account_prefix:
            self._cached_prefixes.pop(account_prefix, None)
            log.info("Prompt cache invalidated for account %s", account_prefix)
        else:
            self._cached_prefixes.clear()
            log.info("Prompt cache fully invalidated")

    def reset_stats(self) -> None:
        """Reset all cache statistics."""
        self._stats = CacheStats()
        self._account_stats.clear()
