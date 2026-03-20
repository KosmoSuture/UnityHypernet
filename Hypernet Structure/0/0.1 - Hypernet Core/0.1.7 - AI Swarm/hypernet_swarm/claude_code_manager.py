"""
Claude Code Session Manager — Persistent autonomous Claude Code instances.

Instead of one-shot `claude -p` calls, this manager maintains long-running
Claude Code sessions that can:
  1. Accept multiple tasks over their lifetime
  2. Resume previous sessions for context continuity
  3. Run with the Hypernet boot sequence as system prompt
  4. Be monitored for output and health
  5. Auto-restart on crash

Each managed instance runs as a subprocess with `--dangerously-skip-permissions`
and communicates via `--output-format stream-json` for real-time monitoring.

Usage:
    manager = ClaudeCodeManager(
        working_dir="C:/Hypernet/Hypernet Structure",
        max_instances=4,
        boot_sequence="...",
    )
    manager.start()  # Launches 4 instances
    manager.submit_task("Chisel", "Fix the bug in server.py")
    results = manager.collect_results()  # Non-blocking
    manager.stop()  # Graceful shutdown
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class ClaudeCodeInstance:
    """A managed Claude Code CLI session."""
    name: str
    model: str  # "sonnet", "opus", "haiku"
    working_dir: str
    process: Optional[subprocess.Popen] = None
    session_id: Optional[str] = None
    status: str = "stopped"  # stopped, starting, running, busy, crashed
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_tokens: int = 0
    last_active: float = 0.0
    last_error: Optional[str] = None
    _output_buffer: str = ""
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def is_alive(self) -> bool:
        """Check if the subprocess is still running."""
        return self.process is not None and self.process.poll() is None


@dataclass
class TaskSubmission:
    """A task waiting to be executed by a Claude Code instance."""
    task_id: str
    title: str
    description: str
    prompt: str
    submitted_at: float = field(default_factory=time.time)
    assigned_to: Optional[str] = None
    result: Optional[str] = None
    success: Optional[bool] = None
    completed_at: Optional[float] = None


class ClaudeCodeManager:
    """Manages multiple persistent Claude Code instances.

    The manager spawns Claude Code CLI processes as long-running workers.
    Each instance can accept tasks, execute them autonomously, and report
    results back to the swarm.

    Architecture:
    - Each instance runs `claude -p <task> --dangerously-skip-permissions`
    - Tasks are queued and dispatched to idle instances
    - Instances auto-restart on crash
    - Output is captured and parsed for results
    - Session IDs are preserved for context continuity
    """

    def __init__(
        self,
        working_dir: str = ".",
        max_instances: int = 4,
        boot_prompt: str = "",
        model: str = "sonnet",
        max_turns: int = 50,
        max_budget_usd: float = 5.0,
        state_dir: str = "",
    ):
        self.working_dir = working_dir
        self.max_instances = max_instances
        self.boot_prompt = boot_prompt
        self.default_model = model
        self.max_turns = max_turns
        self.max_budget_usd = max_budget_usd
        self.state_dir = Path(state_dir) if state_dir else Path(working_dir) / "data" / "claude-code"

        # Find claude CLI
        self._claude_path = self._find_claude()

        # Instance registry
        self.instances: dict[str, ClaudeCodeInstance] = {}

        # Task queue
        self._task_queue: list[TaskSubmission] = []
        self._completed_tasks: list[TaskSubmission] = []
        self._lock = threading.Lock()

        # Manager thread
        self._running = False
        self._manager_thread: Optional[threading.Thread] = None

        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _find_claude() -> Optional[str]:
        """Find the claude CLI executable."""
        found = shutil.which("claude")
        if found:
            return found

        home = Path.home()
        candidates = [
            home / ".local" / "bin" / "claude.exe",
            home / ".local" / "bin" / "claude",
            home / "AppData" / "Roaming" / "npm" / "claude.cmd",
            Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd",
            Path("C:/Users/spamm/.local/bin/claude.exe"),
        ]
        for c in candidates:
            try:
                if c.exists():
                    return str(c)
            except (OSError, ValueError):
                continue
        return None

    def register_instance(self, name: str, model: str = "") -> ClaudeCodeInstance:
        """Register a new Claude Code instance."""
        instance = ClaudeCodeInstance(
            name=name,
            model=model or self.default_model,
            working_dir=self.working_dir,
        )
        self.instances[name] = instance
        log.info("Registered Claude Code instance: %s (model=%s)", name, instance.model)
        return instance

    def start(self):
        """Start the manager loop (runs in background thread)."""
        if self._running:
            return
        if not self._claude_path:
            log.error("Claude Code CLI not found — cannot start manager")
            return

        self._running = True
        self._manager_thread = threading.Thread(
            target=self._manager_loop,
            daemon=True,
            name="claude-code-manager",
        )
        self._manager_thread.start()
        log.info(
            "Claude Code manager started: %d instances, working_dir=%s",
            len(self.instances), self.working_dir,
        )

    def stop(self):
        """Stop all instances and the manager loop."""
        self._running = False
        for name, instance in self.instances.items():
            self._stop_instance(instance)
        if self._manager_thread and self._manager_thread.is_alive():
            self._manager_thread.join(timeout=10)
        log.info("Claude Code manager stopped")

    def submit_task(self, task_id: str, title: str, description: str,
                    prompt: str = "", target_instance: str = "") -> TaskSubmission:
        """Submit a task for execution by a Claude Code instance.

        Args:
            task_id: Unique task identifier (e.g., "0.7.1.19617")
            title: Human-readable task title
            description: Full task description
            prompt: Optional custom prompt (if empty, builds from title+description)
            target_instance: Optional specific instance name to assign to
        """
        if not prompt:
            prompt = self._build_task_prompt(title, description)

        task = TaskSubmission(
            task_id=task_id,
            title=title,
            description=description,
            prompt=prompt,
            assigned_to=target_instance or None,
        )
        with self._lock:
            self._task_queue.append(task)

        log.info("Task submitted to Claude Code manager: %s — %s", task_id, title)
        return task

    def collect_results(self) -> list[TaskSubmission]:
        """Collect completed tasks (non-blocking). Returns and clears the completed list."""
        with self._lock:
            results = list(self._completed_tasks)
            self._completed_tasks.clear()
        return results

    def get_status(self) -> dict:
        """Return manager status for dashboard/API."""
        instances_info = []
        for name, inst in self.instances.items():
            instances_info.append({
                "name": name,
                "model": inst.model,
                "status": inst.status,
                "current_task": inst.current_task,
                "tasks_completed": inst.tasks_completed,
                "tasks_failed": inst.tasks_failed,
                "total_tokens": inst.total_tokens,
                "session_id": inst.session_id,
                "alive": inst.is_alive(),
                "last_error": inst.last_error,
            })
        return {
            "running": self._running,
            "instances": instances_info,
            "queue_depth": len(self._task_queue),
            "total_completed": sum(i.tasks_completed for i in self.instances.values()),
            "total_failed": sum(i.tasks_failed for i in self.instances.values()),
            "claude_path": self._claude_path,
        }

    # ── Internal methods ──

    def _manager_loop(self):
        """Main manager loop — dispatches tasks and monitors instances."""
        while self._running:
            try:
                # 1. Check for idle instances and assign queued tasks
                self._dispatch_tasks()

                # 2. Monitor running instances for completion
                self._monitor_instances()

                # 3. Restart crashed instances
                self._check_health()

                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                log.error("Claude Code manager loop error: %s", e)
                time.sleep(5)

    def _dispatch_tasks(self):
        """Assign queued tasks to idle instances."""
        with self._lock:
            if not self._task_queue:
                return

            for name, instance in self.instances.items():
                if instance.status not in ("running", "stopped"):
                    continue  # busy or crashed
                if instance.current_task:
                    continue  # already working

                # Find a task for this instance
                task = None
                for t in self._task_queue:
                    if t.assigned_to and t.assigned_to != name:
                        continue
                    task = t
                    break

                if task:
                    self._task_queue.remove(task)
                    task.assigned_to = name
                    self._execute_task(instance, task)

    def _execute_task(self, instance: ClaudeCodeInstance, task: TaskSubmission):
        """Launch a Claude Code session to execute a task."""
        instance.current_task = task.title
        instance.status = "busy"
        instance.last_active = time.time()

        def _run():
            try:
                result = self._run_claude(instance, task.prompt)
                task.result = result
                task.success = True
                task.completed_at = time.time()
                instance.tasks_completed += 1
                log.info(
                    "Claude Code %s completed task: %s (%.1fs)",
                    instance.name, task.title,
                    task.completed_at - task.submitted_at,
                )
            except Exception as e:
                task.result = str(e)
                task.success = False
                task.completed_at = time.time()
                instance.tasks_failed += 1
                instance.last_error = str(e)
                log.error("Claude Code %s failed task %s: %s", instance.name, task.title, e)
            finally:
                instance.current_task = None
                instance.status = "running"
                with self._lock:
                    self._completed_tasks.append(task)

        thread = threading.Thread(target=_run, daemon=True, name=f"cc-{instance.name}")
        thread.start()

    def _run_claude(self, instance: ClaudeCodeInstance, prompt: str) -> str:
        """Execute a claude CLI command and return the result."""
        cmd = [
            self._claude_path,
            "-p", prompt,
            "--dangerously-skip-permissions",
            "--output-format", "json",
            "--model", instance.model,
            "--max-turns", str(self.max_turns),
        ]

        # Resume previous session for context continuity
        if instance.session_id:
            cmd.extend(["--resume", instance.session_id])

        # Add boot sequence as system prompt
        if self.boot_prompt:
            # Write boot prompt to temp file for --system-prompt-file
            boot_file = self.state_dir / f"{instance.name}-boot.txt"
            boot_file.write_text(self.boot_prompt, encoding="utf-8")
            cmd.extend(["--system-prompt-file", str(boot_file)])

        log.info(
            "Launching Claude Code: %s (model=%s, resume=%s)",
            instance.name, instance.model, bool(instance.session_id),
        )

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=instance.working_dir,
            timeout=600,  # 10 minute timeout
        )

        output_text = result.stdout.strip()

        # Parse JSON output
        if output_text:
            try:
                data = json.loads(output_text)
                # Save session ID for context continuity
                if data.get("session_id"):
                    instance.session_id = data["session_id"]
                    self._save_state()
                # Track tokens
                usage = data.get("usage", {})
                instance.total_tokens += usage.get("total_tokens", 0)
                return data.get("result", output_text)
            except json.JSONDecodeError:
                return output_text

        if result.returncode != 0:
            error = result.stderr.strip()[:500] if result.stderr else f"Exit code {result.returncode}"
            raise RuntimeError(f"Claude Code failed: {error}")

        return output_text or "(no output)"

    def _monitor_instances(self):
        """Check running instances for issues."""
        for name, instance in self.instances.items():
            if instance.status == "busy" and instance.last_active:
                # Check for stuck instances (>15 minutes on a task)
                if time.time() - instance.last_active > 900:
                    log.warning(
                        "Claude Code %s appears stuck on '%s' (%.0f minutes)",
                        name, instance.current_task,
                        (time.time() - instance.last_active) / 60,
                    )

    def _check_health(self):
        """Restart crashed instances."""
        for name, instance in self.instances.items():
            if instance.status == "crashed":
                # Cool down before restart
                if time.time() - instance.last_active > 30:
                    log.info("Restarting crashed Claude Code instance: %s", name)
                    instance.status = "running"
                    instance.last_error = None

    def _stop_instance(self, instance: ClaudeCodeInstance):
        """Stop a running instance."""
        if instance.process and instance.is_alive():
            instance.process.terminate()
            try:
                instance.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                instance.process.kill()
        instance.status = "stopped"
        instance.process = None

    def _build_task_prompt(self, title: str, description: str) -> str:
        """Build a task prompt for Claude Code."""
        parts = [
            f"# Task: {title}",
            "",
            description,
            "",
            "## Instructions",
            "- Complete this task thoroughly",
            "- Read relevant files before making changes",
            "- Run tests if applicable",
            "- Provide a summary of what you did",
        ]
        return "\n".join(parts)

    def _save_state(self):
        """Persist session IDs and stats for restart continuity."""
        state = {}
        for name, instance in self.instances.items():
            state[name] = {
                "session_id": instance.session_id,
                "tasks_completed": instance.tasks_completed,
                "tasks_failed": instance.tasks_failed,
                "total_tokens": instance.total_tokens,
                "model": instance.model,
            }
        state_file = self.state_dir / "manager_state.json"
        try:
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except OSError as e:
            log.debug("Could not save Claude Code manager state: %s", e)

    def load_state(self):
        """Load previous session state."""
        state_file = self.state_dir / "manager_state.json"
        if not state_file.exists():
            return
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
            for name, data in state.items():
                if name in self.instances:
                    inst = self.instances[name]
                    inst.session_id = data.get("session_id")
                    inst.tasks_completed = data.get("tasks_completed", 0)
                    inst.tasks_failed = data.get("tasks_failed", 0)
                    inst.total_tokens = data.get("total_tokens", 0)
            log.info("Loaded Claude Code manager state: %d instances", len(state))
        except (json.JSONDecodeError, OSError) as e:
            log.warning("Could not load Claude Code manager state: %s", e)
