"""sm — Session Manager CLI.

Commands:
    sm list                        — show roster + each role's state/heartbeat
    sm status <role>               — show role's full status
    sm spawn <role> <engine> <session-id> [--model M] [--tools T]
                                  — register + launch worker
    sm send <role> <prompt|@file>  — queue a new command for role
    sm tail <role> [-n N]          — tail role's stream.jsonl
    sm kill <role>                 — drop STOP file (graceful)
    sm rm <role>                   — remove from roster (after kill)
    sm audit [role]                — show audit log entries
    sm verify <role>               — verify status.history.jsonl hash chain
    sm spawn-cmd <role> ...        — print the spawn command (for manual run)
"""
import argparse
import calendar
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional
from . import audit, paths, roster

def _now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _run_text(cmd: list[str], cwd: Optional[str] = None) -> str:
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=8)
    except Exception:
        return ""
    if out.returncode != 0:
        return ""
    return out.stdout.strip()


def _is_worker_alive(role: str) -> bool:
    """Check if worker PID exists and is running."""
    pid_file = paths.worker_pid(role)
    if not pid_file.exists():
        return False
    try:
        pid = int(pid_file.read_text().strip())
    except (ValueError, FileNotFoundError):
        return False
    if sys.platform.startswith("win"):
        try:
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                                 capture_output=True, text=True, timeout=5)
            return str(pid) in out.stdout
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

def cmd_list(args):
    r = roster.load()
    if not r:
        print("(no roles registered)")
        return
    hdr = (f"{'ROLE':<14} {'ENGINE':<7} {'STATE':<8} {'ALIVE':<5} {'PID':<7} "
           f"{'HEARTBEAT':<21} {'PEND':<5} {'RESUME-FROM (UID)':<38} {'LAST-RESULT-UUID':<36}")
    print(hdr)
    print("-" * len(hdr))
    for role, cfg in sorted(r.items()):
        st = audit.read_status(role)
        alive = "yes" if _is_worker_alive(role) else "NO"
        state = st.get("state", "?")
        hb = st.get("heartbeat", "?")
        pid = st.get("pid", "?")
        resume_sid = st.get("resume_session_id", cfg.get("session_id", "?"))
        last_result = (st.get("last_result_uuid", "") or "-")[:36]
        pending = st.get("pending_commands", "?")
        print(f"{role:<14} {cfg['engine']:<7} {state:<8} {alive:<5} {str(pid):<7} "
              f"{hb:<21} {str(pending):<5} {resume_sid:<38} {last_result:<36}")


def _heartbeat_age_sec(heartbeat: str) -> Optional[int]:
    if not heartbeat or heartbeat == "?":
        return None
    try:
        hb_epoch = calendar.timegm(time.strptime(heartbeat, "%Y-%m-%dT%H:%M:%SZ"))
    except ValueError:
        return None
    return max(0, int(time.time() - hb_epoch))


def _continuity_rows(show_all: bool = False, stale_after_sec: int = 0) -> list[dict]:
    rows = []
    for role, cfg in sorted(roster.load().items()):
        st = audit.read_status(role)
        failure = st.get("last_failure_kind", "") or ""
        recommended = bool(st.get("continuity_recommended", False))
        hb = st.get("heartbeat", "?")
        age = _heartbeat_age_sec(hb)
        stale = stale_after_sec > 0 and (age is None or age > stale_after_sec)
        if not show_all and not (recommended or failure or stale):
            continue
        rows.append({
            "role": role,
            "engine": cfg.get("engine", ""),
            "state": st.get("state", "?"),
            "recommended": recommended,
            "failure": failure or "-",
            "retry_after": st.get("retry_after", "") or "-",
            "pending": st.get("pending_commands", "?"),
            "evidence": st.get("exhaustion_evidence_ref", "") or "-",
            "disclosure": st.get("token_disclosure_mode", "") or "-",
            "heartbeat": hb,
            "heartbeat_age_sec": age,
            "stale": stale,
        })
    return rows


def cmd_continuity(args):
    rows = _continuity_rows(show_all=args.all, stale_after_sec=args.stale_after)
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return 0
    if not rows:
        print("(no continuity-relevant failures recorded)")
        return 0
    hdr = (f"{'ROLE':<14} {'ENG':<7} {'STATE':<8} {'HANDOFF':<7} "
           f"{'STALE':<6} {'AGE':<7} {'FAILURE':<26} {'RETRY':<12} {'PEND':<5} "
           f"{'DISCLOSURE':<14} {'EVIDENCE'}")
    print(hdr)
    print("-" * len(hdr))
    for row in rows:
        handoff = "YES" if row["recommended"] else "-"
        stale = "YES" if row["stale"] else "-"
        age = "-" if row["heartbeat_age_sec"] is None else str(row["heartbeat_age_sec"])
        print(f"{row['role']:<14} {row['engine']:<7} {row['state']:<8} {handoff:<7} "
              f"{stale:<6} {age:<7} {row['failure']:<26} {row['retry_after']:<12} "
              f"{str(row['pending']):<5} {row['disclosure']:<14} {row['evidence']}")
    return 0


def _default_coordination_dir() -> Path:
    return (paths.ROOT.parent / "Hypernet Structure" / "2 - AI Accounts" /
            "Messages" / "coordination")


def _git_head(cwd: str) -> str:
    return _run_text(["git", "-C", cwd, "rev-parse", "--short", "HEAD"])


def _git_status_lines(cwd: str) -> list[str]:
    out = _run_text(["git", "-C", cwd, "status", "--short"])
    return [line for line in out.splitlines() if line.strip()]


def _recent_coordination_notes(coordination_dir: Path, limit: int = 8) -> list[dict]:
    if not coordination_dir.exists():
        return []
    files = [p for p in coordination_dir.iterdir() if p.is_file() and p.suffix.lower() == ".md"]
    files.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    notes = []
    for p in files[:max(0, limit)]:
        st = p.stat()
        notes.append({
            "name": p.name,
            "path": str(p),
            "modified_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
        })
    return notes


def _build_reentry_packet(cwd: str, coordination_dir: Path,
                          notes_limit: int = 8, stale_after_sec: int = 900) -> dict:
    return {
        "object_type": "codex_to_tally_reentry",
        "generated_at": _now_iso(),
        "current_head": _git_head(cwd),
        "dirty_files": _git_status_lines(cwd),
        "continuity_rows": _continuity_rows(show_all=True, stale_after_sec=stale_after_sec),
        "recent_coordination_notes": _recent_coordination_notes(coordination_dir, notes_limit),
        "completed_by_codex": [],
        "tests_run": [],
        "open_decisions_for_tally": [
            "Review Codex continuity deltas and decide whether Packet 04 should be adopted, revised, or discarded.",
        ],
        "held_for_gate_or_matt": [
            "Durable always-up launch, watchdog restart, pushes, grants, and final gate actions remain held.",
        ],
        "recommended_first_tally_action": [
            "Read the newest Codex continuity handoff/update note, then review only the changed files and open decisions.",
        ],
    }


def _print_reentry_markdown(packet: dict) -> None:
    print("codex_to_tally_reentry:")
    print(f"  generated_at: \"{packet['generated_at']}\"")
    print(f"  current_head: \"{packet['current_head']}\"")
    print("  dirty_files:")
    if packet["dirty_files"]:
        for item in packet["dirty_files"]:
            print(f"    - \"{item}\"")
    else:
        print("    - \"\"")
    print("  continuity_rows:")
    if packet["continuity_rows"]:
        for row in packet["continuity_rows"]:
            print(f"    - role: \"{row['role']}\"")
            print(f"      engine: \"{row['engine']}\"")
            print(f"      state: \"{row['state']}\"")
            print(f"      continuity_recommended: {str(row['recommended']).lower()}")
            print(f"      stale: {str(row['stale']).lower()}")
            print(f"      failure: \"{row['failure']}\"")
    else:
        print("    - {}")
    print("  recent_coordination_notes:")
    for note in packet["recent_coordination_notes"]:
        print(f"    - \"{note['name']}\"")
    print("  open_decisions_for_tally:")
    for item in packet["open_decisions_for_tally"]:
        print(f"    - \"{item}\"")
    print("  held_for_gate_or_matt:")
    for item in packet["held_for_gate_or_matt"]:
        print(f"    - \"{item}\"")
    print("  recommended_first_tally_action:")
    for item in packet["recommended_first_tally_action"]:
        print(f"    - \"{item}\"")


def cmd_reentry(args):
    cwd = args.cwd or str(paths.ROOT.parent)
    coord = Path(args.coordination_dir) if args.coordination_dir else _default_coordination_dir()
    packet = _build_reentry_packet(cwd, coord, notes_limit=args.notes,
                                   stale_after_sec=args.stale_after)
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        _print_reentry_markdown(packet)
    return 0


def cmd_status(args):
    st = audit.read_status(args.role)
    if not st:
        print(f"no status for role '{args.role}'")
        return
    print(json.dumps(st, indent=2, sort_keys=True))

def _spawn_worker_detached(role: str) -> int:
    """Launch worker.py as a detached background process. Returns PID or 0 on failure."""
    cmd = [sys.executable, "-m", "session_manager.worker", role]
    if sys.platform.startswith("win"):
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        proc = subprocess.Popen(
            cmd,
            cwd=str(paths.ROOT.parent),  # so 'session_manager' is importable
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        )
    else:
        proc = subprocess.Popen(
            cmd, cwd=str(paths.ROOT.parent),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    return proc.pid

def cmd_spawn(args):
    """Register + launch worker."""
    # ★ S.5 — NODE-0 fail-closed on action commands
    ok, msg = audit.check_node0()
    if not ok:
        print(f"sm spawn refused: {msg}")
        return 3
    # ★ S.6 — validate role name
    try:
        paths.validate_role_name(args.role)
    except paths.InvalidRoleName as e:
        print(f"sm spawn refused: {e}")
        return 4
    existing = roster.get(args.role)
    if existing:
        print(f"role '{args.role}' already in roster; remove first with: sm rm {args.role}")
        return 1
    if args.engine not in ("claude", "codex"):
        print(f"engine must be 'claude' or 'codex', got '{args.engine}'")
        return 1
    cfg = roster.add(
        role=args.role,
        engine=args.engine,
        session_id=args.session_id,
        model=args.model or "",
        cwd=args.cwd or r"C:\Hypernet",
        append_system_prompt=args.append_system_prompt or "",
        tools=args.tools or "",
        notes=args.notes or "",
        account=args.account or "",
        token_ledger_db=args.token_ledger_db or "",
    )
    # Clear any stale STOP file
    sf = paths.stop_file(args.role)
    if sf.exists():
        sf.unlink()
    audit.audit("spawn_requested", role=args.role, engine=args.engine,
                session_id=args.session_id)
    pid = _spawn_worker_detached(args.role)
    audit.audit("worker_detached", role=args.role, pid=pid)
    print(f"spawned worker for role '{args.role}', pid={pid}")
    print(f"  engine={args.engine} session_id={args.session_id}")
    print(f"  use 'sm send {args.role} <prompt>' to queue work")
    return 0

def cmd_send(args):
    """Queue a command for a role. Prompt is text or @path-to-file."""
    # ★ S.5 — NODE-0 fail-closed on action commands
    ok, msg = audit.check_node0()
    if not ok:
        print(f"sm send refused: {msg}")
        return 3
    # ★ S.6 — validate role name
    try:
        paths.validate_role_name(args.role)
    except paths.InvalidRoleName as e:
        print(f"sm send refused: {e}")
        return 4
    if args.role not in roster.load():
        print(f"role '{args.role}' not in roster")
        return 1
    paths.ensure_role(args.role)
    if args.prompt.startswith("@"):
        prompt = Path(args.prompt[1:]).read_text(encoding="utf-8")
        source = args.prompt
    else:
        prompt = args.prompt
        source = "inline"
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    # Sanitize the tag to filename-safe chars. Windows forbids : * ? " < > | / \
    # in filenames; a ':' in a tag previously produced an NTFS alternate-data-stream
    # and a suffix-less file that _list_commands (.txt/.md only) silently skipped —
    # so the command was queued, counted as 0 pending, and never executed. Replace
    # anything unsafe with '-' so every queued command is a real, discoverable file.
    raw_tag = args.tag or "cmd"
    safe_tag = "".join(c if (c.isalnum() or c in "._-") else "-" for c in raw_tag)[:60] or "cmd"
    if safe_tag != raw_tag:
        print(f"note: tag sanitized to '{safe_tag}' (filename-safe)")
    cmd_file = paths.commands_dir(args.role) / f"{ts}-{safe_tag}.txt"
    cmd_file.write_text(prompt, encoding="utf-8")
    audit.audit("command_queued", role=args.role, command_file=str(cmd_file),
                source=source, prompt_chars=len(prompt))
    print(f"queued: {cmd_file}")
    return 0

def cmd_tail(args):
    sp = paths.stream_log(args.role)
    if not sp.exists():
        print(f"no stream log for '{args.role}'")
        return 1
    n = args.n or 50
    lines = sp.read_text(encoding="utf-8", errors="replace").splitlines()
    for line in lines[-n:]:
        print(line)
    return 0

def cmd_kill(args):
    # ★ S.6 — validate role name (no NODE-0 check on kill; founder kill must always work)
    try:
        paths.validate_role_name(args.role)
    except paths.InvalidRoleName as e:
        print(f"sm kill refused: {e}")
        return 4
    sf = paths.stop_file(args.role)
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(f"STOP issued at {_now_iso()} by sm kill\n", encoding="utf-8")
    audit.audit("stop_issued", role=args.role, mechanism="STOP_file")
    print(f"STOP file written for '{args.role}' at {sf}")
    print("worker should exit on next poll cycle (~2s)")
    return 0

def cmd_rm(args):
    if _is_worker_alive(args.role):
        print(f"worker for '{args.role}' is still alive; sm kill {args.role} first")
        return 1
    roster.remove(args.role)
    audit.audit("role_removed", role=args.role)
    print(f"removed '{args.role}' from roster")
    return 0

def cmd_audit(args):
    if not paths.AUDIT_LOG.exists():
        print("(audit log empty)")
        return 0
    n = args.n or 30
    lines = paths.AUDIT_LOG.read_text(encoding="utf-8").splitlines()
    for line in lines[-n:]:
        e = json.loads(line)
        if args.role and e.get("role") != args.role:
            continue
        print(f"{e['ts']} {e['actor']:<6} {e['action']:<30} {json.dumps({k: v for k, v in e.items() if k not in ('ts', 'actor', 'action', 'hash', 'prev_hash')})}")
    return 0

def cmd_verify(args):
    if args.role:
        hp = paths.status_history(args.role)
        ok, msg = audit.verify_chain(hp)
        print(f"{args.role}/status.history.jsonl: {'OK' if ok else 'FAIL'} - {msg}")
        return 0 if ok else 1
    else:
        ok, msg = audit.verify_chain(paths.AUDIT_LOG)
        print(f"audit.jsonl: {'OK' if ok else 'FAIL'} - {msg}")
        return 0 if ok else 1

def cmd_spawn_cmd(args):
    """Print the command to manually launch a worker (for debugging)."""
    cmd = [sys.executable, "-m", "session_manager.worker", args.role]
    print(" ".join(shlex.quote(c) for c in cmd))
    return 0


def cmd_recover(args):
    """Print recovery instructions from the role's latest status.

    The point of the Hypernet check-in convention: every heartbeat carries
    resume_session_id + resume_cmd_hint + pending count, so an outside
    recoverer can resurrect the AI from death without guessing.
    """
    cfg = roster.get(args.role)
    if not cfg:
        print(f"role '{args.role}' not in roster — nothing to recover")
        return 1
    st = audit.read_status(args.role)
    alive = _is_worker_alive(args.role)
    print(f"=== RECOVERY for {args.role} ===")
    print(f"engine             : {cfg['engine']}")
    print(f"worker alive       : {'YES (no recovery needed)' if alive else 'NO (recovery applicable)'}")
    print(f"last heartbeat     : {st.get('heartbeat', '(none)')}")
    print(f"last state         : {st.get('state', '?')}")
    print(f"resume_session_id  : {st.get('resume_session_id', cfg.get('session_id', '?'))}")
    print(f"last_assistant_uuid: {st.get('last_assistant_msg_uuid', '(none)') or '(none)'}")
    print(f"last_result_uuid   : {st.get('last_result_uuid', '(none)') or '(none)'}")
    print(f"last_command_sha   : {st.get('last_command_completed_sha', '(none)') or '(none)'}")
    print(f"last_call_exit_code: {st.get('last_call_exit_code', '(none)')}")
    print(f"last_call_dur_ms   : {st.get('last_call_duration_ms', '(none)')}")
    print(f"last_failure_kind  : {st.get('last_failure_kind', '(none)') or '(none)'}")
    print(f"retry_after        : {st.get('retry_after', '(none)') or '(none)'}")
    print(f"continuity_rec     : {st.get('continuity_recommended', False)}")
    print(f"evidence_ref       : {st.get('exhaustion_evidence_ref', '(none)') or '(none)'}")
    print(f"token_disclosure   : {st.get('token_disclosure_mode', '(none)') or '(none)'}")
    print(f"token_disclosure_id: {st.get('token_disclosure_id', '(none)') or '(none)'}")
    print(f"token_disc_error   : {st.get('token_disclosure_error', '(none)') or '(none)'}")
    print(f"pending commands   : {st.get('pending_commands', '?')}")
    print()
    print(f"--- RESUME COMMAND HINT ---")
    print(f"{st.get('resume_cmd_hint', '(none — re-check status)')}")
    print()
    if not alive:
        print(f"--- TO RESTART WORKER (auto-managed) ---")
        manual_cmd = f"python -m session_manager.worker {args.role}"
        print(f"  {manual_cmd}")
        print(f"  (relaunches the worker; roster entry preserved; will pick up any pending commands)")
    return 0

def build_parser():
    p = argparse.ArgumentParser(prog="sm", description="Session Manager")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list").set_defaults(func=cmd_list)

    s = sub.add_parser("continuity", help="show metadata-only provider failures and Codex handoff recommendations")
    s.add_argument("--all", action="store_true", help="include roles without current failures")
    s.add_argument("--json", action="store_true", help="emit JSON rows")
    s.add_argument("--stale-after", type=int, default=0, metavar="SEC",
                   help="also include roles whose heartbeat is older than SEC seconds; 0 disables stale checks")
    s.set_defaults(func=cmd_continuity)

    s = sub.add_parser("reentry", help="emit a read-only Codex-to-Tally re-entry packet")
    s.add_argument("--cwd", default=str(paths.ROOT.parent), help="repository/workspace root to inspect")
    s.add_argument("--coordination-dir", default="", help="coordination notes directory")
    s.add_argument("-n", "--notes", type=int, default=8, help="number of recent coordination notes to list")
    s.add_argument("--stale-after", type=int, default=900, metavar="SEC",
                   help="mark continuity rows stale when heartbeat age exceeds SEC")
    s.add_argument("--json", action="store_true", help="emit JSON packet")
    s.set_defaults(func=cmd_reentry)

    s = sub.add_parser("status")
    s.add_argument("role")
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("spawn")
    s.add_argument("role")
    s.add_argument("engine", choices=["claude", "codex"])
    s.add_argument("session_id")
    s.add_argument("--model", default="")
    s.add_argument("--cwd", default="")
    s.add_argument("--append-system-prompt", default="")
    s.add_argument("--tools", default="")
    s.add_argument("--notes", default="")
    s.add_argument("--account", default="", help="account label for token disclosures, e.g. 2.6")
    s.add_argument("--token-ledger-db", default="", help="optional token_accounting SQLite DB for unmetered disclosures")
    s.set_defaults(func=cmd_spawn)

    s = sub.add_parser("send")
    s.add_argument("role")
    s.add_argument("prompt", help="prompt text, or @path/to/file")
    s.add_argument("--tag", default="")
    s.set_defaults(func=cmd_send)

    s = sub.add_parser("tail")
    s.add_argument("role")
    s.add_argument("-n", type=int, default=50)
    s.set_defaults(func=cmd_tail)

    s = sub.add_parser("kill")
    s.add_argument("role")
    s.set_defaults(func=cmd_kill)

    s = sub.add_parser("rm")
    s.add_argument("role")
    s.set_defaults(func=cmd_rm)

    s = sub.add_parser("audit")
    s.add_argument("--role", default="")
    s.add_argument("-n", type=int, default=30)
    s.set_defaults(func=cmd_audit)

    s = sub.add_parser("verify")
    s.add_argument("--role", default="")
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("spawn-cmd")
    s.add_argument("role")
    s.set_defaults(func=cmd_spawn_cmd)

    s = sub.add_parser("recover", help="print recovery instructions for a role")
    s.add_argument("role")
    s.set_defaults(func=cmd_recover)

    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    rc = args.func(args)
    sys.exit(rc or 0)

if __name__ == "__main__":
    main()
