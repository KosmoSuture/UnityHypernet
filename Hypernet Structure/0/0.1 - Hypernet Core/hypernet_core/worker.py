"""
Hypernet Worker

Wraps LLM API calls (Claude / GPT / any provider) with identity-aware system prompts.
Each worker is bound to an InstanceProfile and uses the IdentityManager
to construct context-rich prompts.

Provider detection is automatic — the model name determines which LLM
provider to use (e.g., "claude-*" → Anthropic, "gpt-*" → OpenAI).

Supports:
  - Single-turn reasoning (think)
  - Multi-turn conversation (converse)
  - Task execution with structured results
  - Tool use — workers can act on the filesystem via ToolExecutor
  - Multi-provider LLM support (Anthropic, OpenAI, extensible)
  - Swarm directives — workers can request spawn/scale (Keystone, 2.2)
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
from typing import Optional, Any, TYPE_CHECKING

from .identity import InstanceProfile, IdentityManager
from .providers import LLMProvider, create_provider, detect_provider_class

if TYPE_CHECKING:
    from .tools import ToolExecutor

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
    tool_calls: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "task_address": self.task_address,
            "success": self.success,
            "output": self.output,
            "files_modified": self.files_modified,
            "tokens_used": self.tokens_used,
            "duration_seconds": self.duration_seconds,
            "error": self.error,
            "tool_calls": self.tool_calls,
        }


class Worker:
    """Identity-aware LLM worker that executes tasks.

    When a ToolExecutor is provided, the worker can act on the filesystem
    and system. Without it, the worker can only think and describe actions.
    """

    def __init__(
        self,
        identity: InstanceProfile,
        identity_manager: IdentityManager,
        api_key: Optional[str] = None,
        api_keys: Optional[dict[str, str]] = None,
        model: Optional[str] = None,
        mock: bool = False,
        tool_executor: Optional[ToolExecutor] = None,
        provider: Optional[LLMProvider] = None,
    ):
        self.identity = identity
        self.identity_manager = identity_manager
        self.model = model or identity.model or "claude-opus-4-6"
        self.mock = mock
        self.tool_executor = tool_executor
        self._provider: Optional[LLMProvider] = provider
        self._system_prompt: Optional[str] = None
        self._conversation: list[dict] = []
        self._tokens_used: int = 0

        # Initialize LLM provider (unless mock or already provided)
        if not mock and self._provider is None:
            # Build api_keys dict from all available sources
            keys = dict(api_keys or {})
            # Backward compat: bare api_key param → detect which key it is
            if api_key:
                provider_cls = detect_provider_class(self.model)
                if provider_cls and provider_cls.name == "openai":
                    keys.setdefault("openai_api_key", api_key)
                else:
                    keys.setdefault("anthropic_api_key", api_key)
            # Fall back to environment variables
            for env_var, key_name in [
                ("ANTHROPIC_API_KEY", "anthropic_api_key"),
                ("OPENAI_API_KEY", "openai_api_key"),
            ]:
                if env_var in os.environ:
                    keys.setdefault(key_name, os.environ[env_var])

            if keys:
                self._provider = create_provider(self.model, keys)

            if self._provider is None:
                log.warning(f"No provider for worker {identity.name} (model={self.model}). Mock mode.")
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

    @property
    def provider_name(self) -> str:
        """Name of the LLM provider (e.g., 'anthropic', 'openai', 'mock')."""
        if self.mock:
            return "mock"
        if self._provider:
            return self._provider.name
        return "none"

    def think(self, prompt: str) -> str:
        """Single-turn reasoning — send a prompt, get a response."""
        if self.mock:
            return self._mock_response(prompt)

        try:
            response = self._provider.complete(
                model=self.model,
                system=self.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            self._tokens_used += response.tokens_used
            return response.text
        except Exception as e:
            log.error(f"Worker {self.identity.name} API error: {e}")
            return f"[Error: {e}]"

    def converse(self, messages: list[dict]) -> str:
        """Multi-turn conversation — send message history, get next response."""
        if self.mock:
            last_msg = messages[-1]["content"] if messages else "hello"
            return self._mock_response(last_msg)

        try:
            response = self._provider.complete(
                model=self.model,
                system=self.system_prompt,
                messages=messages,
            )
            self._tokens_used += response.tokens_used
            return response.text
        except Exception as e:
            log.error(f"Worker {self.identity.name} conversation error: {e}")
            return f"[Error: {e}]"

    def use_tool(self, tool_name: str, params: dict[str, Any], task_address: Optional[str] = None) -> dict:
        """Execute a tool through the ToolExecutor.

        Returns a dict with the tool result. If no ToolExecutor is configured,
        returns an error indicating tools are not available.
        """
        if not self.tool_executor:
            return {
                "success": False,
                "error": "No ToolExecutor configured — worker can think but not act",
            }

        result = self.tool_executor.execute(
            tool_name=tool_name,
            params=params,
            worker_name=self.identity.name,
            worker_address=self.identity.address or f"2.1.{self.identity.name.lower()}",
            task_address=task_address,
        )
        return result.to_dict()

    def execute_task(self, task_data: dict) -> TaskResult:
        """Execute a task from the queue.

        If a ToolExecutor is configured, the worker can use tools to actually
        perform actions (read/write files, run tests, etc.). Otherwise, the
        worker can only describe what it would do.

        Args:
            task_data: The task node's data dict (title, description, tags, etc.)
        """
        task_address = task_data.get("_address", "unknown")
        title = task_data.get("title", "Untitled")
        description = task_data.get("description", "")
        start_time = datetime.now(timezone.utc)

        # Build prompt with tool awareness
        tool_section = ""
        if self.tool_executor:
            tool_section = (
                "\n\nYou have access to the following tools to complete this task:\n"
                + self.tool_executor.get_tool_descriptions()
                + "\n\nTo use a tool, respond with a JSON block like:\n"
                '```tool\n{"tool": "tool_name", "params": {"key": "value"}}\n```\n'
                "You may use multiple tools. After using tools, summarize what you did.\n"
            )

        prompt = (
            f"You have been assigned the following task:\n\n"
            f"**Title:** {title}\n"
            f"**Description:** {description}\n"
            f"{tool_section}\n"
            f"Please complete this task. Provide your output as a structured response with:\n"
            f"1. What you did\n"
            f"2. Any files you created or modified\n"
            f"3. A brief summary of the result\n"
        )

        try:
            output = self.think(prompt)
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

            # Parse and execute any tool calls from the response
            tool_results = []
            all_files = []
            if self.tool_executor:
                tool_calls = _parse_tool_calls(output)
                for call in tool_calls:
                    result = self.use_tool(
                        call["tool"], call.get("params", {}), task_address,
                    )
                    tool_results.append({
                        "tool": call["tool"],
                        "params": call.get("params", {}),
                        "result": result,
                    })
                    if result.get("files_affected"):
                        all_files.extend(result["files_affected"])

            # Parse swarm directives — contributed by Keystone (2.2)
            # These are NOT executed here; the orchestrator processes them.
            swarm_directives = _parse_swarm_directives(output)
            if swarm_directives:
                tool_results.append({"swarm_directives": swarm_directives})

            return TaskResult(
                task_address=task_address,
                success=True,
                output=output,
                files_modified=all_files,
                tokens_used=self._tokens_used,
                duration_seconds=elapsed,
                tool_calls=tool_results,
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

    @property
    def has_tools(self) -> bool:
        """Whether this worker has tool-use capability."""
        return self.tool_executor is not None

    def __repr__(self) -> str:
        mode = "mock" if self.mock else self.provider_name
        tools = "+tools" if self.has_tools else ""
        return f"Worker({self.identity.name}, model={self.model}, mode={mode}{tools})"


def _parse_tool_calls(text: str) -> list[dict]:
    """Parse tool call blocks from LLM response text.

    Looks for ```tool ... ``` blocks containing JSON with "tool" and "params" keys.
    """
    import re
    calls = []
    pattern = r'```tool\s*\n(.*?)\n```'
    for match in re.finditer(pattern, text, re.DOTALL):
        try:
            data = json.loads(match.group(1).strip())
            if "tool" in data:
                calls.append(data)
        except (json.JSONDecodeError, Exception):
            continue
    return calls


def _parse_swarm_directives(text: str) -> list[dict]:
    """Parse ```swarm``` directive blocks from LLM response text.

    Workers can request orchestrator actions by emitting JSON blocks:
      - {"action":"spawn","model":"gpt-4o","count":1,"reason":"..."}
      - {"action":"scale_down","count":1,"reason":"..."}

    The worker does NOT execute these — they are passed to the orchestrator.

    Contributed by Keystone (2.2).
    """
    import re
    directives = []
    pattern = r'```swarm\s*\n(.*?)\n```'
    for match in re.finditer(pattern, text, re.DOTALL):
        try:
            data = json.loads(match.group(1).strip())
            if isinstance(data, dict) and data.get("action"):
                directives.append(data)
        except Exception:
            continue
    return directives
