"""Per-role worker: polls commands/, runs engine call, captures stream.

Invocation:
    python -m session_manager.worker <role>

The worker runs as a background process. It writes its PID to worker.pid,
heartbeats status every HEARTBEAT_SEC, polls commands/ every POLL_SEC, and
exits cleanly when STOP file appears.

★ Hypernet check-in convention (per Matt 2026-06-03): every heartbeat MUST
carry `resume_session_id` (the UID needed to recover this AI from death) plus
the latest conversation checkpoint (`last_assistant_msg_uuid`, `last_result_uuid`)
and the command-cycle fingerprint (`last_command_completed_sha`). This makes
recovery unambiguous: read the most recent status entry → run the
`resume_cmd_hint` → re-queue any commands left in commands/. No guessing.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from . import audit, paths, roster

POLL_SEC = 2.0
HEARTBEAT_SEC = 5.0


def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _list_commands(role: str) -> list[Path]:
    """Returns sorted list of pending command files (oldest first by filename)."""
    cdir = paths.commands_dir(role)
    if not cdir.exists():
        return []
    files = sorted([p for p in cdir.iterdir() if p.is_file() and p.suffix in (".txt", ".md")])
    return files


def _build_claude_cmd(cfg: dict, prompt: str) -> list[str]:
    """Construct claude --resume invocation."""
    cmd = ["claude", "--resume", cfg["session_id"], "-p", prompt,
           "--permission-mode", "bypassPermissions",
           "--strict-mcp-config",
           "--output-format", "stream-json",
           "--verbose",
           "--add-dir", cfg.get("cwd", r"C:\Hypernet")]
    if cfg.get("model"):
        cmd.extend(["--model", cfg["model"]])
    if cfg.get("tools"):
        cmd.extend(["--tools", cfg["tools"]])
    if cfg.get("append_system_prompt"):
        cmd.extend(["--append-system-prompt", cfg["append_system_prompt"]])
    return cmd


def _build_codex_cmd(cfg: dict, prompt: str) -> list[str]:
    """Construct codex exec invocation. Codex reads prompt from stdin via '-'."""
    cmd = ["codex", "exec",
           "--dangerously-bypass-approvals-and-sandbox",
           "--cd", cfg.get("cwd", r"C:\Hypernet"),
           "--json"]
    cmd.append("-")
    return cmd


def _stream_to_log(cmd: list[str], stream_path: Path, prompt_for_stdin: str = None) -> int:
    """Run cmd, stream stdout to stream_path (append), return exit code."""
    with stream_path.open("a", encoding="utf-8") as logf:
        logf.write(f"\n--- CALL START {_now_iso()} ---\n")
        logf.write(f"cmd: {' '.join(cmd)}\n")
        logf.flush()
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if prompt_for_stdin else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        if prompt_for_stdin:
            proc.stdin.write(prompt_for_stdin)
            proc.stdin.close()
        for line in proc.stdout:
            logf.write(line)
            logf.flush()
        rc = proc.wait()
        logf.write(f"--- CALL END {_now_iso()} exit={rc} ---\n")
        logf.flush()
        return rc


def _archive(cmd_path: Path, role: str):
    """Move processed command to processed/<ts>-<orig> (append-only — never delete)."""
    proc_dir = paths.processed_dir(role)
    proc_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    target = proc_dir / f"{ts}-{cmd_path.name}"
    shutil.move(str(cmd_path), str(target))
    return target


def _parse_last_message_uuid(stream_path: Path) -> tuple[str, str]:
    """Read tail of stream.jsonl, return (last_assistant_msg_uuid, last_result_uuid).

    Best-effort: parses last ~500 JSON-lines. Returns ('', '') if nothing
    parseable. `last_result_uuid` marks turn completion; `last_assistant_msg_uuid`
    is the most recent assistant message — both are checkpoints a recoverer
    can use to know how far the conversation actually advanced.
    """
    if not stream_path.exists():
        return "", ""
    try:
        data = stream_path.read_text(encoding="utf-8", errors="replace")
        lines = data.splitlines()[-500:]
    except Exception:
        return "", ""
    last_msg_uuid = ""
    last_result_uuid = ""
    for line in lines:
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            evt = json.loads(line)
        except Exception:
            continue
        t = evt.get("type")
        if t == "assistant":
            u = evt.get("uuid", "")
            if u:
                last_msg_uuid = u
        elif t == "result":
            u = evt.get("uuid", "")
            if u:
                last_result_uuid = u
    return last_msg_uuid, last_result_uuid


def _resume_cmd_hint(cfg: dict) -> str:
    """A copy-pasteable resume command for the recoverer."""
    if cfg["engine"] == "claude":
        parts = ["claude", "--resume", cfg["session_id"], "-p", "'<your-prompt>'"]
        if cfg.get("model"):
            parts.extend(["--model", cfg["model"]])
        if cfg.get("tools"):
            parts.extend(["--tools", cfg["tools"]])
        parts.extend(["--add-dir", cfg.get("cwd", r"C:\Hypernet")])
        parts.extend(["--permission-mode", "bypassPermissions", "--strict-mcp-config"])
        return " ".join(parts)
    elif cfg["engine"] == "codex":
        return (f"codex exec --dangerously-bypass-approvals-and-sandbox "
                f"--cd {cfg.get('cwd','')} --json - "
                f"# session_id={cfg['session_id']} embedded in boot prompt")
    return f"# unknown engine {cfg['engine']}"


def _pending_commands_count(role: str) -> int:
    return len(_list_commands(role))


def _heartbeat_fields(role: str, cfg: dict, state: str, **extra) -> dict:
    """Build the standard heartbeat field set that EVERY status update includes.

    Hypernet check-in convention: `resume_session_id` is the single most important
    field — it's what an outside recoverer uses to resurrect this AI. Plus
    conversation checkpoint UIDs, command-cycle fingerprint, and the
    copy-pasteable resume command.
    """
    last_msg_uuid, last_result_uuid = _parse_last_message_uuid(paths.stream_log(role))
    fields = {
        "state": state,
        "heartbeat": _now_iso(),
        "pid": os.getpid(),
        "engine": cfg["engine"],
        # ★ The recovery key — every heartbeat carries this verbatim
        "resume_session_id": cfg["session_id"],
        "resume_cmd_hint": _resume_cmd_hint(cfg),
        # Conversation-level checkpoints (best-effort from stream.jsonl tail)
        "last_assistant_msg_uuid": last_msg_uuid,
        "last_result_uuid": last_result_uuid,
        # Command-cycle visibility
        "pending_commands": _pending_commands_count(role),
    }
    fields.update(extra)
    return fields


def run(role: str):
    # ★ S.6 — validate role name format up front
    try:
        paths.validate_role_name(role)
    except paths.InvalidRoleName as e:
        print(f"worker: {e}", file=sys.stderr)
        sys.exit(2)
    cfg = roster.get(role)
    if not cfg:
        print(f"worker: role '{role}' not in roster; exiting", file=sys.stderr)
        sys.exit(1)
    # ★ S.5 — NODE-0 marker check at startup (fail-closed)
    ok, msg = audit.check_node0()
    if not ok:
        print(f"worker: {msg}; refusing to start", file=sys.stderr)
        audit.audit("worker_refused_startup_no_node0_marker", role=role, reason=msg)
        sys.exit(3)
    paths.ensure_role(role)
    paths.worker_pid(role).write_text(str(os.getpid()), encoding="utf-8")
    # First heartbeat — recovery-ready from second one
    audit.audit("worker_start", role=role, pid=os.getpid(),
                resume_session_id=cfg["session_id"])
    audit.write_status(role, **_heartbeat_fields(role, cfg, "idle"))
    last_heartbeat = time.time()
    last_command_completed_sha = ""
    last_call_exit_code = None
    last_call_duration_ms = 0
    try:
        while True:
            # ★ S.5 — NODE-0 marker check on every loop (fail-closed)
            ok, msg = audit.check_node0()
            if not ok:
                audit.audit("worker_stop_node0_revoked", role=role, reason=msg,
                            resume_session_id=cfg["session_id"])
                try:
                    audit.write_status(role, **_heartbeat_fields(
                        role, cfg, "stopped",
                        reason=f"NODE-0 marker revoked: {msg}",
                        last_command_completed_sha=last_command_completed_sha,
                    ))
                except Exception:
                    pass
                break
            # Check STOP (fail-closed)
            if paths.stop_file(role).exists():
                audit.audit("worker_stop_via_stop_file", role=role,
                            resume_session_id=cfg["session_id"])
                audit.write_status(role, **_heartbeat_fields(
                    role, cfg, "stopped",
                    reason="STOP file present",
                    last_command_completed_sha=last_command_completed_sha,
                    last_call_exit_code=last_call_exit_code,
                    last_call_duration_ms=last_call_duration_ms,
                ))
                break
            # Heartbeat
            if time.time() - last_heartbeat > HEARTBEAT_SEC:
                audit.write_status(role, **_heartbeat_fields(
                    role, cfg, "idle",
                    last_command_completed_sha=last_command_completed_sha,
                    last_call_exit_code=last_call_exit_code,
                    last_call_duration_ms=last_call_duration_ms,
                ))
                last_heartbeat = time.time()
            # Poll commands
            cmds = _list_commands(role)
            if cmds:
                cmd_file = cmds[0]
                prompt = cmd_file.read_text(encoding="utf-8")
                cmd_sha = hashlib.sha256(cmd_file.read_bytes()).hexdigest()
                audit.audit("command_picked_up", role=role,
                            command_file=str(cmd_file),
                            command_sha=cmd_sha,
                            prompt_chars=len(prompt),
                            resume_session_id=cfg["session_id"])
                audit.write_status(role, **_heartbeat_fields(
                    role, cfg, "running",
                    current_command=str(cmd_file),
                    current_command_sha=cmd_sha,
                    prompt_chars=len(prompt),
                    last_command_completed_sha=last_command_completed_sha,
                ))
                # Build + run
                t0 = time.time()
                if cfg["engine"] == "claude":
                    cmd = _build_claude_cmd(cfg, prompt)
                    rc = _stream_to_log(cmd, paths.stream_log(role))
                elif cfg["engine"] == "codex":
                    cmd = _build_codex_cmd(cfg, prompt)
                    rc = _stream_to_log(cmd, paths.stream_log(role), prompt_for_stdin=prompt)
                else:
                    audit.audit("unknown_engine", role=role, engine=cfg["engine"])
                    rc = -1
                last_call_duration_ms = int((time.time() - t0) * 1000)
                last_call_exit_code = rc
                # Archive
                archived = _archive(cmd_file, role)
                last_command_completed_sha = cmd_sha
                audit.audit("command_completed", role=role, exit_code=rc,
                            archived_to=str(archived),
                            command_sha=cmd_sha,
                            duration_ms=last_call_duration_ms,
                            resume_session_id=cfg["session_id"])
                audit.write_status(role, **_heartbeat_fields(
                    role, cfg, "idle",
                    last_completion=_now_iso(),
                    last_call_exit_code=rc,
                    last_call_duration_ms=last_call_duration_ms,
                    last_command_completed_sha=cmd_sha,
                ))
                last_heartbeat = time.time()
            time.sleep(POLL_SEC)
    except KeyboardInterrupt:
        audit.audit("worker_keyboard_interrupt", role=role,
                    resume_session_id=cfg["session_id"])
        audit.write_status(role, **_heartbeat_fields(
            role, cfg, "stopped",
            reason="KeyboardInterrupt",
            last_command_completed_sha=last_command_completed_sha,
            last_call_exit_code=last_call_exit_code,
            last_call_duration_ms=last_call_duration_ms,
        ))
    finally:
        try:
            paths.worker_pid(role).unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m session_manager.worker <role>", file=sys.stderr)
        sys.exit(2)
    run(sys.argv[1])
