"""
Hypernet Tool Framework

Tools let AI workers ACT on the filesystem and system, not just think.
Every tool execution is gated by the permission system and logged to
the audit trail.

Execution flow:
  1. Worker requests tool use with params
  2. ToolExecutor checks permission tier
  3. If allowed: execute tool, create audit entry, return result
  4. If denied: create denied audit entry, return error

Built-in tools:
  - read_file (Tier 0)   — Read any file in the archive
  - list_files (Tier 0)  — List files in a directory
  - write_file (Tier 1)  — Write to permitted paths
  - append_file (Tier 1) — Append to permitted paths
  - run_tests (Tier 1)   — Run the test suite
  - search_files (Tier 0) — Search for content in files

Reference: Plan at plans/scalable-petting-pine.md
"""

from __future__ import annotations
import glob as glob_module
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .permissions import PermissionManager, PermissionTier
from .audit import AuditTrail, AuditEntry

log = logging.getLogger(__name__)


@dataclass
class ToolContext:
    """Execution context passed to every tool call."""

    worker_name: str
    worker_address: str
    permission_mgr: PermissionManager
    audit_trail: AuditTrail
    archive_root: Path
    task_address: Optional[str] = None  # Task that triggered this tool use


@dataclass
class ToolResult:
    """Result from a tool execution."""

    success: bool
    output: str = ""
    error: Optional[str] = None
    files_affected: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "files_affected": self.files_affected,
        }


class Tool(ABC):
    """Base class for all tools. Subclasses implement execute()."""

    name: str = ""
    description: str = ""
    required_tier: PermissionTier = PermissionTier.READ_ONLY

    @abstractmethod
    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        """Execute the tool with given parameters and context."""
        ...

    def to_spec(self) -> dict[str, str]:
        """Return tool specification for LLM tool-use."""
        return {
            "name": self.name,
            "description": self.description,
            "required_tier": self.required_tier.name,
        }


class ReadFileTool(Tool):
    """Read a file from the archive."""

    name = "read_file"
    description = "Read the contents of a file. Provide 'path' (relative to archive root)."
    required_tier = PermissionTier.READ_ONLY

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        rel_path = params.get("path", "")
        if not rel_path:
            return ToolResult(success=False, error="Missing 'path' parameter")

        full_path = (context.archive_root / rel_path).resolve()

        # Security: ensure path is within archive
        if not _is_safe_path(full_path, context.archive_root):
            return ToolResult(
                success=False,
                error=f"Path '{rel_path}' is outside the archive",
            )

        if not full_path.exists():
            return ToolResult(success=False, error=f"File not found: {rel_path}")

        if not full_path.is_file():
            return ToolResult(success=False, error=f"Not a file: {rel_path}")

        try:
            content = full_path.read_text(encoding="utf-8")
            # Truncate very large files
            if len(content) > 50000:
                content = content[:50000] + f"\n\n[Truncated — file is {len(content)} chars]"

            return ToolResult(
                success=True,
                output=content,
                files_affected=[rel_path],
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Error reading file: {e}")


class ListFilesTool(Tool):
    """List files in a directory."""

    name = "list_files"
    description = "List files in a directory. Provide 'path' (relative to archive root) and optional 'pattern' (glob)."
    required_tier = PermissionTier.READ_ONLY

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        rel_path = params.get("path", ".")
        pattern = params.get("pattern", "*")

        full_path = (context.archive_root / rel_path).resolve()

        if not _is_safe_path(full_path, context.archive_root):
            return ToolResult(
                success=False,
                error=f"Path '{rel_path}' is outside the archive",
            )

        if not full_path.exists():
            return ToolResult(success=False, error=f"Directory not found: {rel_path}")

        if not full_path.is_dir():
            return ToolResult(success=False, error=f"Not a directory: {rel_path}")

        try:
            entries = sorted(full_path.glob(pattern))
            lines = []
            for entry in entries[:200]:  # Cap at 200 entries
                rel = entry.relative_to(context.archive_root)
                marker = "/" if entry.is_dir() else ""
                lines.append(f"{rel}{marker}")

            output = "\n".join(lines)
            if len(entries) > 200:
                output += f"\n\n[Showing 200 of {len(entries)} entries]"

            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, error=f"Error listing files: {e}")


class WriteFileTool(Tool):
    """Write content to a file (permission-gated by path)."""

    name = "write_file"
    description = "Write content to a file. Provide 'path' (relative to archive root) and 'content'."
    required_tier = PermissionTier.WRITE_OWN

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        rel_path = params.get("path", "")
        content = params.get("content", "")

        if not rel_path:
            return ToolResult(success=False, error="Missing 'path' parameter")

        full_path = (context.archive_root / rel_path).resolve()

        if not _is_safe_path(full_path, context.archive_root):
            return ToolResult(
                success=False,
                error=f"Path '{rel_path}' is outside the archive",
            )

        # Permission check: can this worker write to this path?
        perm = context.permission_mgr.check_write(
            context.worker_address, context.worker_name, full_path,
        )
        if not perm:
            return ToolResult(
                success=False,
                error=f"Permission denied: worker '{context.worker_name}' "
                       f"cannot write to '{rel_path}'",
            )

        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            return ToolResult(
                success=True,
                output=f"Wrote {len(content)} chars to {rel_path}",
                files_affected=[rel_path],
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Error writing file: {e}")


class AppendFileTool(Tool):
    """Append content to a file (permission-gated by path)."""

    name = "append_file"
    description = "Append content to an existing file. Provide 'path' and 'content'."
    required_tier = PermissionTier.WRITE_OWN

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        rel_path = params.get("path", "")
        content = params.get("content", "")

        if not rel_path:
            return ToolResult(success=False, error="Missing 'path' parameter")

        full_path = (context.archive_root / rel_path).resolve()

        if not _is_safe_path(full_path, context.archive_root):
            return ToolResult(
                success=False,
                error=f"Path '{rel_path}' is outside the archive",
            )

        perm = context.permission_mgr.check_write(
            context.worker_address, context.worker_name, full_path,
        )
        if not perm:
            return ToolResult(
                success=False,
                error=f"Permission denied: cannot append to '{rel_path}'",
            )

        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "a", encoding="utf-8") as f:
                f.write(content)
            return ToolResult(
                success=True,
                output=f"Appended {len(content)} chars to {rel_path}",
                files_affected=[rel_path],
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Error appending to file: {e}")


class SearchFilesTool(Tool):
    """Search for content across files."""

    name = "search_files"
    description = "Search for a text pattern in files. Provide 'query' and optional 'path' (directory to search)."
    required_tier = PermissionTier.READ_ONLY

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        query = params.get("query", "")
        rel_path = params.get("path", ".")

        if not query:
            return ToolResult(success=False, error="Missing 'query' parameter")

        full_path = (context.archive_root / rel_path).resolve()

        if not _is_safe_path(full_path, context.archive_root):
            return ToolResult(
                success=False,
                error=f"Path '{rel_path}' is outside the archive",
            )

        try:
            matches = []
            search_dir = full_path if full_path.is_dir() else full_path.parent
            for root, dirs, files in os.walk(search_dir):
                # Skip hidden dirs, data dirs, __pycache__
                dirs[:] = [
                    d for d in dirs
                    if not d.startswith(".") and d not in ("data", "__pycache__", "node_modules")
                ]
                for fname in files:
                    if not fname.endswith((".md", ".py", ".json", ".txt", ".yaml", ".yml")):
                        continue
                    fpath = Path(root) / fname
                    try:
                        text = fpath.read_text(encoding="utf-8", errors="ignore")
                        if query.lower() in text.lower():
                            rel = fpath.relative_to(context.archive_root)
                            # Find matching lines
                            for i, line in enumerate(text.splitlines(), 1):
                                if query.lower() in line.lower():
                                    matches.append(f"{rel}:{i}: {line.strip()[:120]}")
                                    if len(matches) >= 50:
                                        break
                    except Exception:
                        continue
                    if len(matches) >= 50:
                        break
                if len(matches) >= 50:
                    break

            if not matches:
                return ToolResult(success=True, output=f"No matches found for '{query}'")

            output = "\n".join(matches)
            if len(matches) >= 50:
                output += "\n\n[Results truncated at 50 matches]"
            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, error=f"Error searching: {e}")


class RunTestsTool(Tool):
    """Run the test suite."""

    name = "run_tests"
    description = "Run the Hypernet test suite. No parameters needed."
    required_tier = PermissionTier.WRITE_OWN

    def execute(self, params: dict[str, Any], context: ToolContext) -> ToolResult:
        test_file = context.archive_root / "0" / "0.1 - Hypernet Core" / "test_hypernet.py"
        if not test_file.exists():
            return ToolResult(success=False, error="Test file not found")

        try:
            result = subprocess.run(
                ["python", str(test_file)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(test_file.parent),
            )
            output = result.stdout + result.stderr
            success = result.returncode == 0
            return ToolResult(
                success=success,
                output=output[:10000],  # Cap output
                error=None if success else f"Tests failed (exit code {result.returncode})",
            )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, error="Tests timed out after 120 seconds")
        except Exception as e:
            return ToolResult(success=False, error=f"Error running tests: {e}")


# =========================================================================
# Tool Executor — orchestrates permission checking, execution, and auditing
# =========================================================================

class ToolExecutor:
    """Executes tools with permission checks and audit logging.

    This is the central gateway: workers never call tools directly.
    Every call goes through ToolExecutor, which:
      1. Checks permissions
      2. Executes the tool
      3. Logs the result to the audit trail
    """

    def __init__(
        self,
        permission_mgr: PermissionManager,
        audit_trail: AuditTrail,
        archive_root: str | Path,
    ):
        self.permission_mgr = permission_mgr
        self.audit_trail = audit_trail
        self.archive_root = Path(archive_root).resolve()
        self._tools: dict[str, Tool] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register all built-in tools."""
        for tool_cls in [
            ReadFileTool, ListFilesTool, WriteFileTool, AppendFileTool,
            SearchFilesTool, RunTestsTool,
        ]:
            tool = tool_cls()
            self._tools[tool.name] = tool

    def register_tool(self, tool: Tool) -> None:
        """Register a custom tool."""
        self._tools[tool.name] = tool

    def available_tools(self, worker_address: str) -> list[dict]:
        """Return tool specs available to a worker at their current tier."""
        tier = self.permission_mgr.get_tier(worker_address)
        return [
            tool.to_spec()
            for tool in self._tools.values()
            if tool.required_tier <= tier
        ]

    def execute(
        self,
        tool_name: str,
        params: dict[str, Any],
        worker_name: str,
        worker_address: str,
        task_address: Optional[str] = None,
    ) -> ToolResult:
        """Execute a tool with full permission checking and audit logging."""
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Unknown tool: '{tool_name}'. "
                      f"Available: {list(self._tools.keys())}",
            )

        # Permission check — resolve relative paths against archive root
        target = params.get("path", params.get("query", ""))
        resolved_target = None
        if params.get("path"):
            resolved_target = str((self.archive_root / params["path"]).resolve())
        perm_check = self.permission_mgr.check_tool(
            worker_address=worker_address,
            worker_name=worker_name,
            tool_name=tool_name,
            required_tier=tool.required_tier,
            target_path=resolved_target,
        )

        if not perm_check:
            # Log denied action
            self.audit_trail.log_denied(
                action=tool_name,
                actor=worker_address,
                actor_name=worker_name,
                target=str(target),
                permission_tier=self.permission_mgr.get_tier(worker_address).value,
                reason=perm_check.reason,
                task_address=task_address,
            )
            return ToolResult(success=False, error=perm_check.reason)

        # Build context and execute
        context = ToolContext(
            worker_name=worker_name,
            worker_address=worker_address,
            permission_mgr=self.permission_mgr,
            audit_trail=self.audit_trail,
            archive_root=self.archive_root,
            task_address=task_address,
        )

        result = tool.execute(params, context)

        # Log to audit trail
        self.audit_trail.log_action(AuditEntry(
            action=tool_name,
            actor=worker_address,
            actor_name=worker_name,
            target=str(target),
            permission_tier=self.permission_mgr.get_tier(worker_address).value,
            result="success" if result.success else f"error: {result.error}",
            task_address=task_address,
            details={"files_affected": result.files_affected} if result.files_affected else {},
        ))

        return result

    def get_tool_descriptions(self) -> str:
        """Generate a human-readable description of all tools for system prompts."""
        lines = ["Available tools:"]
        for tool in sorted(self._tools.values(), key=lambda t: t.required_tier):
            lines.append(
                f"  - {tool.name} (tier {tool.required_tier.value}): {tool.description}"
            )
        return "\n".join(lines)


def _is_safe_path(path: Path, root: Path) -> bool:
    """Ensure a path doesn't escape the archive root."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False
