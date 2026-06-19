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
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
from . import audit, paths, roster

POLL_SEC = 2.0
HEARTBEAT_SEC = 5.0

_FAILURE_TAIL_LINES = 800

_QUOTA_PATTERNS = (
    "insufficient_quota",
    "quota exceeded",
    "usage limit",
    "credit balance",
    "billing",
    "out of credits",
)
_RATE_LIMIT_PATTERNS = (
    "rate limit",
    "rate_limit",
    "too many requests",
    " 429",
    "status 429",
    "http 429",
)
_CONTEXT_LIMIT_PATTERNS = (
    "context length",
    "context window",
    "maximum context",
    "prompt is too long",
    "input is too long",
    "token limit",
    "tokens exceeded",
)


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
            # ★ task #66 ROOT-CAUSE FIX (2026-06-06): without an explicit encoding, Python decodes the
            # subprocess stream with the Windows locale codec (cp1252), which raises UnicodeDecodeError on
            # any non-cp1252 byte (e.g. 0x90) in claude/codex JSON output — that exception propagated out
            # of run() and KILLED THE WORKER. Decode as UTF-8, replacing undecodable bytes, so the stream
            # reader never crashes the worker on output bytes.
            encoding="utf-8",
            errors="replace",
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


def _walk_json_scalars(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield str(k), v
            yield from _walk_json_scalars(v)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_json_scalars(item)


def _extract_retry_after_from_event(evt: dict) -> str:
    for key, value in _walk_json_scalars(evt):
        lk = key.lower()
        if lk in {"retry_after", "retry_after_s", "retry_after_seconds"}:
            return str(value)
        if lk in {"retry_after_ms", "retry_ms", "wait_ms"}:
            try:
                return f"{int(value) / 1000:.0f}s"
            except (TypeError, ValueError):
                return str(value)
        if lk in {"reset_at", "resets_at", "reset_time", "rate_limit_reset"}:
            return str(value)
    return ""


def _extract_retry_after_from_text(text: str) -> str:
    patterns = (
        r"retry[-_ ]after[:= ]+([A-Za-z0-9:._+-]+)",
        r"retry after ([0-9]+)\s*(seconds?|secs?|s)?",
        r"try again in ([0-9]+)\s*(seconds?|minutes?|hours?|secs?|mins?|hrs?|s|m|h)?",
        r"reset(?:s)? (?:at|in) ([A-Za-z0-9:._+-]+)",
    )
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if not m:
            continue
        value = m.group(1)
        unit = m.group(2) if len(m.groups()) > 1 else ""
        return f"{value}{unit or ''}"
    return ""


def _line_evidence_ref(stream_path: Path, line_no: int, line: str) -> str:
    digest = hashlib.sha256(line.encode("utf-8", errors="replace")).hexdigest()[:16]
    return f"{stream_path.name}:line={line_no}:sha256={digest}"


def _latest_call_lines(all_lines: list[str]) -> tuple[int, list[str]]:
    start_index = 0
    for i in range(len(all_lines) - 1, -1, -1):
        if all_lines[i].startswith("--- CALL START "):
            start_index = i
            break
    return start_index + 1, all_lines[start_index:]


def _is_classifier_candidate_line(raw: str) -> bool:
    if not raw:
        return False
    if raw.startswith("--- CALL START ") or raw.startswith("--- CALL END "):
        return False
    if raw.startswith("cmd: "):
        return False
    return True


def _classify_call_failure(stream_path: Path, exit_code: int, engine: str) -> dict:
    """Classify provider failure from stream metadata without copying raw stream text.

    The status fields are intentionally metadata-only. Raw stream tails can contain
    prompts, tool output, or secrets, so the evidence pointer is a line number plus
    line hash instead of the matching text.
    """
    cleared = {
        "last_failure_kind": "",
        "retry_after": "",
        "exhaustion_evidence_ref": "",
        "continuity_recommended": False,
    }
    if exit_code == 0:
        return cleared
    if not stream_path.exists():
        return {
            **cleared,
            "last_failure_kind": "nonzero_exit",
            "exhaustion_evidence_ref": f"{stream_path.name}:missing",
        }

    try:
        all_lines = stream_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return {
            **cleared,
            "last_failure_kind": "nonzero_exit",
            "exhaustion_evidence_ref": f"{stream_path.name}:unreadable",
        }

    call_start_line_no, call_lines = _latest_call_lines(all_lines)
    start_line_no = max(call_start_line_no, call_start_line_no + len(call_lines) - _FAILURE_TAIL_LINES)
    lines = call_lines[-_FAILURE_TAIL_LINES:]
    best = {
        **cleared,
        "last_failure_kind": "nonzero_exit",
        "exhaustion_evidence_ref": f"{stream_path.name}:tail",
    }

    def set_best(kind: str, line_no: int, line: str, retry_after: str = "") -> dict:
        return {
            "last_failure_kind": kind,
            "retry_after": retry_after,
            "exhaustion_evidence_ref": _line_evidence_ref(stream_path, line_no, line),
            "continuity_recommended": (
                engine == "claude"
                and kind in {"provider_quota_exhausted", "provider_rate_limited", "context_limit"}
            ),
        }

    for offset, line in enumerate(lines):
        line_no = start_line_no + offset
        raw = line.strip()
        if not _is_classifier_candidate_line(raw):
            continue
        lower = raw.lower()
        evt = None
        if raw.startswith("{"):
            try:
                evt = json.loads(raw)
            except Exception:
                evt = None
        retry_after = _extract_retry_after_from_event(evt) if isinstance(evt, dict) else ""
        retry_after = retry_after or _extract_retry_after_from_text(raw)

        if isinstance(evt, dict) and evt.get("type") == "rate_limit_event":
            best = set_best("provider_rate_limited", line_no, raw, retry_after)
            continue
        if any(p in lower for p in _QUOTA_PATTERNS):
            best = set_best("provider_quota_exhausted", line_no, raw, retry_after)
            continue
        if any(p in lower for p in _RATE_LIMIT_PATTERNS):
            best = set_best("provider_rate_limited", line_no, raw, retry_after)
            continue
        if any(p in lower for p in _CONTEXT_LIMIT_PATTERNS):
            best = set_best("context_limit", line_no, raw, retry_after)
            continue
        if isinstance(evt, dict) and evt.get("type") == "result" and evt.get("is_error") is True:
            best = set_best("model_error", line_no, raw, retry_after)

    return best


def _token_ledger_db(cfg: dict) -> str:
    return (
        cfg.get("token_ledger_db", "")
        or os.environ.get("SESSION_MANAGER_TOKEN_LEDGER_DB", "")
        or os.environ.get("SM_TOKEN_LEDGER_DB", "")
    )


def _record_unmetered_disclosure(role: str, cfg: dict, command_sha: str,
                                 exit_code: int, duration_ms: int) -> dict:
    """Record a structured disclosure for CLI calls that are not wrapper-metered.

    This is intentionally disclosure-only. It does not claim per-call budget enforcement and
    it never blocks the worker when the optional accounting DB is unavailable.
    """
    cleared = {
        "token_disclosure_mode": "not_configured",
        "token_disclosure_id": "",
        "token_disclosure_error": "",
    }
    db_path = _token_ledger_db(cfg)
    if not db_path:
        return cleared
    completed = _now_iso()
    base = f"sm:{role}:{cfg.get('session_id','')}:{command_sha}:{completed}"
    disclosure_id = "sm-disc-" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:24]
    try:
        from token_accounting.ledger import TokenLedger
        from token_accounting.reconciler import Reconciler

        ledger = TokenLedger(db_path)
        try:
            raw = {
                "disclosure_id": disclosure_id,
                "instance_name": role,
                "account": cfg.get("account") or "unknown",
                "role": role,
                "engine": cfg.get("engine", "unknown"),
                "model": cfg.get("model") or cfg.get("engine", "unknown"),
                "reason_code": "wrapper-unavailable",
                "timestamp_utc": completed,
                "disclosed_by": "session_manager.worker",
                "billing_reconstruct_pointer": (
                    f"session_manager:{role}:stream.jsonl:"
                    f"command_sha={command_sha}:exit={exit_code}:duration_ms={duration_ms}"
                ),
            }
            rec = Reconciler(ledger.connection()).ingest_disclosure(raw, disclosure_id=disclosure_id)
        finally:
            ledger.close()
        if not rec.valid:
            return {
                "token_disclosure_mode": "invalid",
                "token_disclosure_id": disclosure_id,
                "token_disclosure_error": rec.malformed_reason or "invalid disclosure",
            }
        return {
            "token_disclosure_mode": "recorded",
            "token_disclosure_id": disclosure_id,
            "token_disclosure_error": "",
        }
    except Exception as exc:
        return {
            "token_disclosure_mode": "record_failed",
            "token_disclosure_id": disclosure_id,
            "token_disclosure_error": f"{type(exc).__name__}: {exc}",
        }


def _t4_metering_enabled(cfg: dict) -> bool:
    """Opt-in gate for REAL T.4 metering + external anchoring (Option C Hybrid). Off by default so
    existing workers/tests keep the disclosure-only behavior; the production tally worker sets it."""
    return bool(cfg.get("t4_metering")
                or str(os.environ.get("SM_T4_METERING", "")).lower() in ("1", "true", "yes"))


def _production_ledger_db(cfg: dict) -> str:
    """The SHARED production T.4 ledger (one chain → one external anchor sequence for the swarm)."""
    return (cfg.get("t4_ledger_db")
            or os.environ.get("SM_T4_LEDGER_DB")
            or os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions", "t4-production-ledger.db"))


def _parse_latest_usage(stream_path: Path, engine: str) -> tuple[Optional[dict], Optional[str]]:
    """Parse the ACTUAL token usage of the latest call from the stream log — HONEST, never fabricated.

    Returns (usage_dict, model) or (None, None) when no usage is present (e.g. a failed call). Takes the
    LAST usage-bearing event in the call (for claude stream-json that is the `result` event = the turn
    total; for codex --json the final token-count event). The meter records ONLY what the provider
    actually reported, so a row cannot claim usage that did not happen (Codex round-3: honest rows)."""
    if not stream_path.exists():
        return None, None
    try:
        all_lines = stream_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None, None
    _, call_lines = _latest_call_lines(all_lines)
    usage: Optional[dict] = None
    model: Optional[str] = None
    for line in call_lines:
        raw = line.strip()
        if not raw.startswith("{"):
            continue
        try:
            evt = json.loads(raw)
        except Exception:
            continue
        if not isinstance(evt, dict):
            continue
        # direct usage on the event (claude `result`, codex token-count)
        u = evt.get("usage")
        if isinstance(u, dict) and (u.get("input_tokens") is not None or u.get("output_tokens") is not None):
            usage = u
        if isinstance(evt.get("model"), str) and evt["model"]:
            model = evt["model"]
        # nested message.usage / message.model (claude assistant events)
        msg = evt.get("message")
        if isinstance(msg, dict):
            mu = msg.get("usage")
            if isinstance(mu, dict) and (mu.get("input_tokens") is not None or mu.get("output_tokens") is not None):
                usage = mu
            if isinstance(msg.get("model"), str) and msg["model"]:
                model = msg["model"]
    return usage, model


def _record_token_accounting(role: str, cfg: dict, command_sha: str,
                             exit_code: int, duration_ms: int) -> dict:
    """Option-C Hybrid: REAL T.4 metering + external AnchoredChain anchor when enabled and the parsed
    usage is present; otherwise the existing disclosure fallback. Fail-closed: if the production sink
    is unavailable (PAT missing / config error) the row/anchor are NOT fabricated — the call is
    disclosed instead, with the error surfaced. Never raises into the worker loop (it must keep running).

    This is the Wave-4 Agent metering-layer PROTOTYPE: the same parse→normalize→record→anchor pattern
    the Wave-4 Agent connector will use (with the Server as the sink instead of the git remote)."""
    disclosure = _record_unmetered_disclosure(role, cfg, command_sha, exit_code, duration_ms)
    if not _t4_metering_enabled(cfg):
        return {**disclosure, "token_metered_mode": "disabled"}
    if exit_code != 0:
        return {**disclosure, "token_metered_mode": "disclosed-call-failed"}
    usage, parsed_model = _parse_latest_usage(paths.stream_log(role), cfg["engine"])
    if not usage:
        return {**disclosure, "token_metered_mode": "disclosed-no-usage"}
    try:
        from token_accounting.production import production_token_ledger
        from token_accounting.engines import get_adapter
        from token_accounting.usage import NormalizedUsage, TokenCostModel

        model = parsed_model or cfg.get("model") or cfg["engine"]
        adapter = get_adapter(cfg["engine"])
        nu = (adapter.to_normalized_usage({"usage": usage, "model": model, "id": usage.get("id")})
              if adapter is not None
              else NormalizedUsage(input_tokens=usage.get("input_tokens"),
                                   output_tokens=usage.get("output_tokens"), raw_usage=usage))
        cost = TokenCostModel().estimate(nu, model).cost_usd
        cfg_path = os.path.join(cfg.get("cwd", r"C:\Hypernet"),
                                "Hypernet Structure", "secrets", "config.json")
        ledger = production_token_ledger(_production_ledger_db(cfg), config_path=cfg_path)  # raises if PAT missing
        try:
            cum = ledger.cumulative_usd() + cost
            row = ledger.record(
                instance_name=role, account=cfg.get("account", "2.4.1"),
                provider=nu.provider or cfg["engine"], model=model,
                input_tokens=nu.input_tokens, output_tokens=nu.output_tokens,
                cost_estimate_usd=cost, cumulative_cost_after=cum, tier_after="NORMAL",
                is_personal_time=False, logical_clock=int(time.time()), engine=cfg["engine"],
                request_id=nu.request_id, usage_dimensions_json=nu.dimensions_json(),
                raw_usage_json=nu.raw_json())
            anchor = ledger.anchor_chain()   # checkpoints head+count to the external public repo
            pending = getattr(getattr(ledger, "_chain", None), "_sink", None)
            provisional = bool(getattr(pending, "pending_push", False))
            mode = ("anchored" if anchor is not None and not provisional
                    else "recorded-anchor-provisional" if anchor is not None
                    else "recorded-no-anchor")
            return {
                **disclosure,
                "token_metered_mode": mode,
                "token_row_seq": row["seq"],
                "token_metered_cost_usd": round(cost, 8),
                "token_input_tokens": nu.input_tokens,
                "token_output_tokens": nu.output_tokens,
                "token_anchor_head": (anchor.head[:16] if anchor is not None else ""),
                "token_anchor_count": (anchor.count if anchor is not None else 0),
            }
        finally:
            ledger.close()
    except Exception as exc:
        # fail-closed: never fabricate a metered/anchored claim; disclose the failure instead.
        return {**disclosure, "token_metered_mode": "metering-failed",
                "token_metered_error": f"{type(exc).__name__}: {exc}"}


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
    # ★ Wave 4 P1 — SINGLETON LOCK: exactly one live worker per role. An OS-level exclusive file lock
    #   (auto-released by the kernel on death) replaces the old blind worker.pid overwrite that allowed the
    #   duplicate-worker race. Refuse to start if another live worker holds the role.
    from session_manager import worker_lock
    _lock = worker_lock.SingletonLock(worker_lock.lock_path(role))
    if not _lock.acquire():
        existing = ""
        try:
            existing = paths.worker_pid(role).read_text(encoding="utf-8").strip()
        except Exception:
            pass
        print(f"worker: another live worker already holds role '{role}' "
              f"(pid {existing or '?'}); refusing to start (singleton lock)", file=sys.stderr)
        audit.audit("worker_refused_startup_singleton_lock_held", role=role, existing_pid=existing)
        sys.exit(4)
    # ★ P1 (adversary fix, reverify R1): the try/finally that releases the singleton lock + cleans
    #   worker.pid begins IMMEDIATELY after a successful acquire — no post-acquire/pre-try gap — so EVERY
    #   post-acquire startup step is covered and a startup exception still releases the lock (no wedge).
    #   The recovery/state vars are the FIRST statements inside the try; they are pure literal assignments
    #   that cannot raise, so the except/finally always have them defined.
    try:
        last_heartbeat = time.time()
        last_command_completed_sha = ""
        last_call_exit_code = None
        last_call_duration_ms = 0
        last_failure = {}
        last_disclosure = {
            "token_disclosure_mode": "not_configured",
            "token_disclosure_id": "",
            "token_disclosure_error": "",
        }
        paths.worker_pid(role).write_text(str(os.getpid()), encoding="utf-8")
        # First heartbeat — recovery-ready from second one
        audit.audit("worker_start", role=role, pid=os.getpid(),
                    resume_session_id=cfg["session_id"])
        audit.write_status(role, **_heartbeat_fields(role, cfg, "idle"))
        last_failure = _classify_call_failure(paths.stream_log(role), 0, cfg["engine"])
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
                    **last_failure,
                    **last_disclosure,
                ))
                break
            # Heartbeat
            if time.time() - last_heartbeat > HEARTBEAT_SEC:
                audit.write_status(role, **_heartbeat_fields(
                    role, cfg, "idle",
                    last_command_completed_sha=last_command_completed_sha,
                    last_call_exit_code=last_call_exit_code,
                    last_call_duration_ms=last_call_duration_ms,
                    **last_failure,
                    **last_disclosure,
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
                last_failure = _classify_call_failure(paths.stream_log(role), rc, cfg["engine"])
                last_disclosure = _record_token_accounting(
                    role, cfg, cmd_sha, rc, last_call_duration_ms)
                # Archive
                archived = _archive(cmd_file, role)
                last_command_completed_sha = cmd_sha
                audit.audit("command_completed", role=role, exit_code=rc,
                            archived_to=str(archived),
                            command_sha=cmd_sha,
                            duration_ms=last_call_duration_ms,
                            token_disclosure_mode=last_disclosure["token_disclosure_mode"],
                            token_disclosure_id=last_disclosure["token_disclosure_id"],
                            resume_session_id=cfg["session_id"])
                audit.write_status(role, **_heartbeat_fields(
                    role, cfg, "idle",
                    last_completion=_now_iso(),
                    last_call_exit_code=rc,
                    last_call_duration_ms=last_call_duration_ms,
                    last_command_completed_sha=cmd_sha,
                    **last_failure,
                    **last_disclosure,
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
            **last_failure,
            **last_disclosure,
        ))
    except Exception as exc:
        # ★ Task #66 band-aid — DIAGNOSE the recurring worker death: log the full traceback so the next
        #   crash has a root cause (the loop previously died silently with no recorded reason).
        import traceback as _tb
        _trace = _tb.format_exc()
        try:
            _crash = paths.worker_pid(role).parent / "worker-crash.log"
            with _crash.open("a", encoding="utf-8") as _fh:
                _fh.write(f"\n--- WORKER CRASH {_now_iso()} pid={os.getpid()} role={role} ---\n{_trace}\n")
        except Exception:
            pass
        try:
            audit.audit("worker_crashed", role=role, exc_type=type(exc).__name__,
                        exc=str(exc)[:300], resume_session_id=cfg.get("session_id", ""))
            audit.write_status(role, **_heartbeat_fields(
                role, cfg, "crashed",
                reason=f"unhandled exception: {type(exc).__name__}: {str(exc)[:200]}",
                last_command_completed_sha=last_command_completed_sha,
                last_call_exit_code=last_call_exit_code,
                last_call_duration_ms=last_call_duration_ms,
            ))
        except Exception:
            pass
        raise   # re-raise so the process exits visibly (a watchdog can restart); the cause is now logged
    finally:
        try:
            paths.worker_pid(role).unlink()
        except FileNotFoundError:
            pass
        try:
            _lock.release()   # release the singleton lock so a supervised restart can claim the role
        except Exception:
            pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python -m session_manager.worker <role>", file=sys.stderr)
        sys.exit(2)
    run(sys.argv[1])
