"""
Hypernet Agent Tool Extension Framework

Extends the base Tool framework (tools.py) with capabilities needed for the
Universal AI Agent Framework (2.0.11):

  1. AgentTool     — Extended Tool with category, setup instructions, grant templates
  2. GrantCard     — Copy-pasteable permission grant for user-friendly access granting
  3. ToolRegistry  — Discovery, availability checking, and categorized tool listing

This is Phase 1 of the Universal Agent Framework. It makes it easy to add new
tools (shell, API, database, etc.) with self-documenting setup and simple
user-facing permission grants.

Design principle: Tools should be easy to add, easy to grant, and easy to audit.
A user should be able to grant a tool permission by copying and pasting a single
text block. An AI should be able to discover what tools are available, what setup
they need, and how to request access.

Reference: 2.0.11 — Universal AI Agent Framework (design doc)
Reference: TASK-053 — Universal AI Agent Framework
"""

from __future__ import annotations

import json
import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .tools import Tool, ToolContext, ToolResult
from .permissions import PermissionTier

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
#  Tool Categories
# ---------------------------------------------------------------------------

class ToolCategory:
    """Standard tool categories for the agent framework."""
    FILESYSTEM = "filesystem"     # File read/write/search (existing tools)
    SYSTEM = "system"             # Shell execution, process management
    COMMUNICATION = "communication"  # Email, messaging, webhooks
    DATA = "data"                 # Database, API calls, data transform
    DEVELOPMENT = "development"   # Git, testing, code analysis
    WEB = "web"                   # Web scraping, HTTP requests
    CUSTOM = "custom"             # User-defined tools


# ---------------------------------------------------------------------------
#  Grant Card
# ---------------------------------------------------------------------------

@dataclass
class GrantCard:
    """A copy-pasteable permission grant for a tool.

    Grant cards are the user-facing mechanism for granting tool access.
    A user copies the grant text, saves it to ~/.hypernet/grants/, and
    the system picks it up on next boot or refresh.

    The grant card contains:
      - What tool is being granted
      - What access level it provides
      - What the tool can do (human-readable)
      - What the tool CANNOT do (explicit limits)
      - Revocation instructions
    """
    tool_name: str
    access_level: str            # Human-readable: "read", "write", "execute", "full"
    description: str             # What this grant allows
    limitations: list[str]       # What this grant does NOT allow
    grant_text: str              # The actual copy-pasteable text
    revocation: str = "Delete this file to revoke access."

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "access_level": self.access_level,
            "description": self.description,
            "limitations": self.limitations,
            "grant_text": self.grant_text,
            "revocation": self.revocation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> GrantCard:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
#  AgentTool
# ---------------------------------------------------------------------------

class AgentTool(Tool):
    """Extended Tool with agent framework capabilities.

    Adds to the base Tool:
      - category: Which category this tool belongs to
      - setup_instructions: Human-readable setup guide
      - grant_template: Template for generating grant cards
      - requires_config: What configuration the tool needs
      - check_available(): Whether the tool can currently execute

    Subclasses implement:
      - execute(): The actual tool logic (inherited from Tool)
      - check_available(): Whether prerequisites are met
      - setup_guide(): Step-by-step setup instructions
    """

    name: str = ""
    description: str = ""
    category: str = ToolCategory.CUSTOM
    required_tier: PermissionTier = PermissionTier.EXTERNAL
    requires_config: dict[str, str] = {}  # key → description of what's needed

    def check_available(self, context: ToolContext) -> tuple[bool, str]:
        """Check if this tool can currently execute.

        Returns:
            (available, reason) — True if ready, False with explanation if not.
        """
        return True, "Available"

    def setup_guide(self) -> str:
        """Return human-readable setup instructions.

        Override in subclasses for tool-specific setup.
        """
        if not self.requires_config:
            return f"{self.name}: No setup required."

        lines = [f"# Setup: {self.name}", ""]
        for key, desc in self.requires_config.items():
            lines.append(f"  {key}: {desc}")
        return "\n".join(lines)

    def grant_card(self) -> GrantCard:
        """Generate a grant card for this tool.

        Override in subclasses for custom grant text.
        """
        grant_text = (
            f"# Hypernet Grant Card\n"
            f"# Tool: {self.name}\n"
            f"# Generated: {datetime.now(timezone.utc).isoformat()}\n"
            f"#\n"
            f"# Save this file to ~/.hypernet/grants/{self.name}.grant\n"
            f"# Delete this file to revoke access.\n"
            f"\n"
            f'{{"tool": "{self.name}", '
            f'"granted": true, '
            f'"tier": {self.required_tier.value}, '
            f'"category": "{self.category}"}}\n'
        )

        return GrantCard(
            tool_name=self.name,
            access_level=self.required_tier.name.lower().replace("_", " "),
            description=self.description,
            limitations=[
                f"Requires permission tier {self.required_tier.value} ({self.required_tier.name})",
                "All executions are logged to the audit trail",
                "Can be revoked by deleting the grant file",
            ],
            grant_text=grant_text,
        )

    def to_spec(self) -> dict[str, str]:
        """Extended tool spec including agent framework fields."""
        spec = super().to_spec()
        spec["category"] = self.category
        available, reason = self.check_available(
            ToolContext(
                worker_name="", worker_address="",
                permission_mgr=None, audit_trail=None,
                archive_root=Path("."),
            )
        )
        spec["available"] = available
        if not available:
            spec["unavailable_reason"] = reason
        return spec


# ---------------------------------------------------------------------------
#  Concrete Agent Tools
# ---------------------------------------------------------------------------

class ShellExecTool(AgentTool):
    """Execute shell commands on the host system.

    This is the most powerful tool — it gives the AI access to the
    operating system. Gated at EXTERNAL tier (requires human approval).
    """

    name = "shell_exec"
    description = (
        "Execute a shell command and return stdout/stderr. "
        "Provide 'command' (the shell command to run) and optional "
        "'timeout' (seconds, default 30) and 'cwd' (working directory)."
    )
    category = ToolCategory.SYSTEM
    required_tier = PermissionTier.EXTERNAL
    requires_config = {
        "shell_allowed": "Set to 'true' to enable shell execution",
        "shell_allowlist": "Optional: comma-separated list of allowed commands",
    }

    def check_available(self, context: ToolContext) -> tuple[bool, str]:
        # Shell exec requires explicit grant — never available by default
        grants_dir = Path.home() / ".hypernet" / "grants"
        grant_file = grants_dir / "shell_exec.grant"
        if grant_file.exists():
            return True, "Shell execution granted"
        return False, "Shell execution requires a grant card at ~/.hypernet/grants/shell_exec.grant"

    def setup_guide(self) -> str:
        return (
            "# Setup: Shell Execution\n"
            "\n"
            "Shell execution gives AI access to run commands on your system.\n"
            "This is powerful — use it when you trust the AI with system access.\n"
            "\n"
            "## Steps:\n"
            "1. Create the grants directory: mkdir -p ~/.hypernet/grants\n"
            "2. Save the grant card below to: ~/.hypernet/grants/shell_exec.grant\n"
            "3. The AI will be able to run shell commands on next boot.\n"
            "\n"
            "## To revoke:\n"
            "Delete ~/.hypernet/grants/shell_exec.grant\n"
        )

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        import subprocess

        command = params.get("command", "")
        timeout = min(params.get("timeout", 30), 120)  # Cap at 2 minutes
        cwd = params.get("cwd", None)

        if not command:
            return ToolResult(success=False, error="Missing 'command' parameter")

        # Check availability
        available, reason = self.check_available(context)
        if not available:
            return ToolResult(success=False, error=reason)

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"

            # Truncate large output
            if len(output) > 20000:
                output = output[:20000] + f"\n[Truncated — {len(output)} chars total]"

            return ToolResult(
                success=result.returncode == 0,
                output=output,
                error=f"Exit code {result.returncode}" if result.returncode != 0 else None,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error=f"Command timed out after {timeout} seconds")
        except Exception as e:
            return ToolResult(success=False, error=f"Shell execution error: {e}")


class HttpRequestTool(AgentTool):
    """Make HTTP requests to external APIs."""

    name = "http_request"
    description = (
        "Make an HTTP request. Provide 'url', optional 'method' (GET/POST/PUT/DELETE, "
        "default GET), optional 'headers' (dict), optional 'body' (string or dict)."
    )
    category = ToolCategory.WEB
    required_tier = PermissionTier.EXTERNAL
    requires_config = {
        "http_allowed": "Set to 'true' to enable HTTP requests",
    }

    def check_available(self, context: ToolContext) -> tuple[bool, str]:
        try:
            import urllib.request  # noqa: F401
            return True, "HTTP requests available (urllib)"
        except ImportError:
            return False, "urllib not available"

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        import urllib.request
        import urllib.error

        url = params.get("url", "")
        method = params.get("method", "GET").upper()
        headers = params.get("headers", {})
        body = params.get("body", None)

        if not url:
            return ToolResult(success=False, error="Missing 'url' parameter")

        try:
            body_bytes = None
            if body is not None:
                if isinstance(body, dict):
                    body_bytes = json.dumps(body).encode("utf-8")
                    headers.setdefault("Content-Type", "application/json")
                else:
                    body_bytes = str(body).encode("utf-8")

            req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read().decode("utf-8", errors="replace")
                if len(content) > 20000:
                    content = content[:20000] + f"\n[Truncated — {len(content)} chars]"

                return ToolResult(
                    success=True,
                    output=f"HTTP {resp.status} {resp.reason}\n\n{content}",
                )
        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode("utf-8", errors="replace")[:5000]
            except Exception:
                pass
            return ToolResult(
                success=False,
                error=f"HTTP {e.code}: {e.reason}",
                output=body_text,
            )
        except Exception as e:
            return ToolResult(success=False, error=f"HTTP request error: {e}")


class GitOpsTool(AgentTool):
    """Git operations — status, diff, commit, branch management."""

    name = "git_ops"
    description = (
        "Perform git operations. Provide 'operation' (status/diff/log/branch/commit/add) "
        "and optional 'args' (additional arguments). For commit, provide 'message'."
    )
    category = ToolCategory.DEVELOPMENT
    required_tier = PermissionTier.WRITE_SHARED
    requires_config = {}

    def check_available(self, context: ToolContext) -> tuple[bool, str]:
        import shutil
        if shutil.which("git"):
            return True, "Git available"
        return False, "Git not found in PATH"

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        import subprocess

        operation = params.get("operation", "")
        args = params.get("args", "")
        message = params.get("message", "")

        allowed_ops = {"status", "diff", "log", "branch", "add", "commit", "show", "stash"}
        if operation not in allowed_ops:
            return ToolResult(
                success=False,
                error=f"Unknown git operation: '{operation}'. Allowed: {allowed_ops}",
            )

        # Build command
        cmd = ["git", operation]
        if operation == "commit" and message:
            cmd.extend(["-m", message])
        if args:
            cmd.extend(args.split())

        # Safety: prevent destructive operations
        dangerous = {"push", "reset", "rebase", "force", "--force", "-f", "--hard"}
        all_args = set(cmd[1:])
        if all_args & dangerous:
            return ToolResult(
                success=False,
                error=f"Dangerous git operation blocked: {all_args & dangerous}. "
                      f"Use manual git for destructive operations.",
            )

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(context.archive_root),
            )
            output = result.stdout
            if result.stderr:
                output += f"\n{result.stderr}"
            if len(output) > 10000:
                output = output[:10000] + "\n[Truncated]"

            return ToolResult(
                success=result.returncode == 0,
                output=output,
                error=f"Git error (exit {result.returncode})" if result.returncode != 0 else None,
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Git command timed out")
        except Exception as e:
            return ToolResult(success=False, error=f"Git error: {e}")


# ---------------------------------------------------------------------------
#  Tool Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Registry for discovering and managing agent tools.

    Extends the basic ToolExecutor pattern with:
      - Categorized tool listing
      - Availability checking
      - Setup guide generation
      - Grant card management
    """

    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        """Register an agent tool."""
        self._tools[tool.name] = tool
        log.info(f"Registered agent tool: {tool.name} (category: {tool.category})")

    def get(self, name: str) -> Optional[AgentTool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> list[AgentTool]:
        """List all registered tools, optionally filtered by category."""
        tools = list(self._tools.values())
        if category:
            tools = [t for t in tools if t.category == category]
        return sorted(tools, key=lambda t: (t.category, t.name))

    def list_categories(self) -> list[str]:
        """List all tool categories that have registered tools."""
        return sorted(set(t.category for t in self._tools.values()))

    def check_availability(self, context: ToolContext) -> dict[str, tuple[bool, str]]:
        """Check availability of all tools.

        Returns:
            Dict of tool_name → (available, reason).
        """
        return {
            name: tool.check_available(context)
            for name, tool in self._tools.items()
        }

    def generate_setup_guide(self) -> str:
        """Generate a complete setup guide for all tools."""
        lines = [
            "# Hypernet Agent Tool Setup Guide",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            f"Total tools: {len(self._tools)}",
            "",
        ]

        for category in self.list_categories():
            lines.append(f"## {category.title()}")
            lines.append("")
            for tool in self.list_tools(category):
                lines.append(f"### {tool.name}")
                lines.append(f"**Description:** {tool.description}")
                lines.append(f"**Required tier:** {tool.required_tier.name}")
                lines.append("")
                lines.append(tool.setup_guide())
                lines.append("")

        return "\n".join(lines)

    def generate_grant_cards(self) -> dict[str, GrantCard]:
        """Generate grant cards for all tools."""
        return {name: tool.grant_card() for name, tool in self._tools.items()}

    def load_grants(self, grants_dir: Optional[Path] = None) -> dict[str, bool]:
        """Load grant cards from the grants directory.

        Args:
            grants_dir: Path to grants directory. Defaults to ~/.hypernet/grants/

        Returns:
            Dict of tool_name → granted (True/False).
        """
        if grants_dir is None:
            grants_dir = Path.home() / ".hypernet" / "grants"

        grants: dict[str, bool] = {}
        if not grants_dir.exists():
            return grants

        for grant_file in grants_dir.glob("*.grant"):
            try:
                content = grant_file.read_text(encoding="utf-8")
                # Skip comment lines, find the JSON
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("{"):
                        data = json.loads(line)
                        tool_name = data.get("tool", "")
                        if tool_name and data.get("granted", False):
                            grants[tool_name] = True
                            log.info(f"Loaded grant for tool: {tool_name}")
                        break
            except Exception as e:
                log.warning(f"Failed to load grant from {grant_file}: {e}")

        return grants

    def to_dict(self) -> dict:
        """Serialize registry state for inspection."""
        return {
            "tools": {
                name: {
                    "name": tool.name,
                    "description": tool.description,
                    "category": tool.category,
                    "required_tier": tool.required_tier.name,
                }
                for name, tool in self._tools.items()
            },
            "categories": self.list_categories(),
            "total": len(self._tools),
        }


# ---------------------------------------------------------------------------
#  Factory
# ---------------------------------------------------------------------------

def create_default_registry() -> ToolRegistry:
    """Create a registry with all built-in agent tools.

    These tools are registered but not necessarily available — each tool
    checks its own prerequisites (grants, system capabilities, etc.)
    before execution.
    """
    registry = ToolRegistry()
    registry.register(ShellExecTool())
    registry.register(HttpRequestTool())
    registry.register(GitOpsTool())
    return registry
