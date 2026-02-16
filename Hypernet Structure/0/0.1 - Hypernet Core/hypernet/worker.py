"""
Hypernet Worker

Wraps LLM API calls (Claude / GPT) with identity-aware system prompts.
Each worker is bound to an InstanceProfile and uses the IdentityManager
to construct context-rich prompts.

Supports:
  - Single-turn reasoning (think)
  - Multi-turn conversation (converse)
  - Task execution with structured results
  - Token budget tracking
  - Mock mode for testing without API keys
"""

from __future__ import annotations
import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Any

from .identity import InstanceProfile, IdentityManager

log = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """Structured result from a worker executing a task."""
    task_address: str
    success: bool
    output: str = ""
    files_modified: list[str] = field(default_factory=list)
    tokens_used: int = 0
    duration_seconds: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "task_address": self.task_address,
            "success": self.success,
            "output": self.output,
            "files_modified": self.files_modified,
            "tokens_used": self.tokens_used,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
        }


class Worker:
    """Identity-aware LLM worker that executes tasks."""

    def __init__(
        self,
        identity: InstanceProfile,
        identity_manager: IdentityManager,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        mock: bool = False,
    ):
        self.identity = identity
        self.identity_manager = identity_manager
        self.model = model or identity.model or "claude-opus-4-6"
        self.mock = mock
        self._client = None
        self._system_prompt: Optional[str] = None
        self._conversation: list[dict] = []
        self._tokens_used: int = 0

        # Initialize API client
        if not mock:
            api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            if api_key:
                try:
                    import anthropic
                    self._client = anthropic.Anthropic(api_key=api_key)
                except ImportError:
                    log.warning("anthropic package not installed. Install with: pip install anthropic")
                    self.mock = True
            else:
                log.warning(f"No API key for worker {identity.name}. Running in mock mode.")
                self.mock = True

    @property
    def system_prompt(self) -> str:
        """Build system prompt lazily and cache it."""
        if self._system_prompt is None:
            self._system_prompt = self.identity_manager.build_system_prompt(self.identity)
        return self._system_prompt

    @property
    def tokens_used(self) -> int:
        return self._tokens_used

    def think(self, prompt: str) -> str:
        """Single-turn reasoning — send a prompt, get a response."""
        if self.mock:
            return self._mock_response(prompt)

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            self._tokens_used += response.usage.input_tokens + response.usage.output_tokens
            return response.content[0].text
        except Exception as e:
            log.error(f"Worker {self.identity.name} API error: {e}")
            return f"[Error: {e}]"

    def converse(self, messages: list[dict]) -> str:
        """Multi-turn conversation — send message history, get next response."""
        if self.mock:
            last_msg = messages[-1]["content"] if messages else "hello"
            return self._mock_response(last_msg)

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages,
            )
            self._tokens_used += response.usage.input_tokens + response.usage.output_tokens
            return response.content[0].text
        except Exception as e:
            log.error(f"Worker {self.identity.name} conversation error: {e}")
            return f"[Error: {e}]"

    def execute_task(self, task_data: dict) -> TaskResult:
        """Execute a task from the queue.

        Args:
            task_data: The task node's data dict (title, description, tags, etc.)
        """
        task_address = task_data.get("_address", "unknown")
        title = task_data.get("title", "Untitled")
        description = task_data.get("description", "")
        start_time = datetime.now(timezone.utc)

        prompt = (
            f"You have been assigned the following task:\n\n"
            f"**Title:** {title}\n"
            f"**Description:** {description}\n\n"
            f"Please complete this task. Provide your output as a structured response with:\n"
            f"1. What you did\n"
            f"2. Any files you would create or modify\n"
            f"3. A brief summary of the result\n"
        )

        try:
            output = self.think(prompt)
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

            return TaskResult(
                task_address=task_address,
                success=True,
                output=output,
                tokens_used=self._tokens_used,
                duration_seconds=elapsed,
            )
        except Exception as e:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            return TaskResult(
                task_address=task_address,
                success=False,
                error=str(e),
                duration_seconds=elapsed,
            )

    def _mock_response(self, prompt: str) -> str:
        """Generate a mock response for testing without API access."""
        return (
            f"[Mock response from {self.identity.name}]\n"
            f"Received prompt ({len(prompt)} chars). "
            f"In live mode, this would be processed by {self.model}.\n"
            f"Instance orientation: {self.identity.orientation or 'not set'}"
        )

    def reset_conversation(self) -> None:
        """Clear conversation history for a fresh session."""
        self._conversation = []

    def __repr__(self) -> str:
        mode = "mock" if self.mock else "live"
        return f"Worker({self.identity.name}, model={self.model}, mode={mode})"
