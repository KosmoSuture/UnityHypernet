"""peeker — read-only visibility into ANY Claude Code session by session-id.

Claude Code stores every session's transcript at:
    C:/Users/spamm/.claude/projects/<project-dir>/<session-id>.jsonl

This tool finds + parses the JSONL and surfaces:
- Last user message (truncated)
- Last assistant message (truncated)
- Last tool call name (if any)
- Time since last activity
- Total turns / event count
- Session file path
- File size

Usage:
    python -m session_manager.peeker peek <session-id>
    python -m session_manager.peeker all [--limit N]
    python -m session_manager.peeker search <substring>

Read-only. No writes, no modifications, no network. Safe to run against
any session regardless of whether it's actively running.
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


CLAUDE_PROJECTS_ROOT = Path(r"C:/Users/spamm/.claude/projects")


def find_session_files(session_id: str = None, search: str = None) -> list:
    """Find Claude Code session JSONL files.

    If session_id is provided, find exactly that session.
    If search is provided, find any file with substring in name.
    Otherwise return all session files across all projects.
    """
    if not CLAUDE_PROJECTS_ROOT.exists():
        return []
    results = []
    for project_dir in CLAUDE_PROJECTS_ROOT.iterdir():
        if not project_dir.is_dir():
            continue
        for session_file in project_dir.glob("*.jsonl"):
            name = session_file.stem
            if session_id and name == session_id:
                results.append(session_file)
            elif search and search in name:
                results.append(session_file)
            elif not session_id and not search:
                results.append(session_file)
    return sorted(results, key=lambda p: p.stat().st_mtime, reverse=True)


def _truncate(s: str, n: int = 200) -> str:
    s = s.strip().replace("\n", " ")
    if len(s) <= n:
        return s
    return s[:n - 3] + "..."


def parse_session(path: Path) -> dict:
    """Read JSONL transcript, return summary dict."""
    summary = {
        "session_file": str(path),
        "file_size_kb": round(path.stat().st_size / 1024, 1),
        "mtime_iso": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mtime_age_sec": round(time.time() - path.stat().st_mtime),
        "total_turns": 0,
        "user_turns": 0,
        "assistant_turns": 0,
        "tool_calls": 0,
        "last_user_msg": "",
        "last_assistant_msg": "",
        "last_tool_call": "",
        "session_id_from_events": "",
        "model": "",
    }
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith("{"):
                    continue
                try:
                    evt = json.loads(line)
                except Exception:
                    continue
                t = evt.get("type", "")
                if t == "user":
                    summary["user_turns"] += 1
                    summary["total_turns"] += 1
                    msg = evt.get("message", {})
                    content = msg.get("content", "")
                    if isinstance(content, str):
                        summary["last_user_msg"] = _truncate(content)
                    elif isinstance(content, list):
                        for blk in content:
                            if isinstance(blk, dict) and blk.get("type") == "text":
                                summary["last_user_msg"] = _truncate(blk.get("text", ""))
                                break
                elif t == "assistant":
                    summary["assistant_turns"] += 1
                    summary["total_turns"] += 1
                    msg = evt.get("message", {})
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for blk in content:
                            if not isinstance(blk, dict):
                                continue
                            btype = blk.get("type")
                            if btype == "text":
                                summary["last_assistant_msg"] = _truncate(blk.get("text", ""))
                            elif btype == "tool_use":
                                summary["tool_calls"] += 1
                                summary["last_tool_call"] = blk.get("name", "?")
                    if msg.get("model"):
                        summary["model"] = msg["model"]
                elif t == "system" and evt.get("subtype") == "init":
                    summary["session_id_from_events"] = evt.get("session_id", "")
                    if evt.get("model"):
                        summary["model"] = evt["model"]
    except Exception as e:
        summary["parse_error"] = str(e)
    return summary


def format_summary(s: dict) -> str:
    age = s.get("mtime_age_sec", 0)
    if age < 60:
        age_str = f"{age}s ago"
    elif age < 3600:
        age_str = f"{age // 60}m ago"
    elif age < 86400:
        age_str = f"{age // 3600}h ago"
    else:
        age_str = f"{age // 86400}d ago"

    lines = [
        f"=== {Path(s['session_file']).stem} ===",
        f"  file       : {s['session_file']}",
        f"  size       : {s['file_size_kb']} KB",
        f"  last write : {s['mtime_iso']} ({age_str})",
        f"  model      : {s.get('model', '?')}",
        f"  session_id : {s.get('session_id_from_events', '(not found in events)')}",
        f"  turns      : {s['total_turns']} ({s['user_turns']} user / {s['assistant_turns']} assistant)",
        f"  tool calls : {s['tool_calls']} (last: {s.get('last_tool_call', '-')})",
        f"  last user  : {s.get('last_user_msg', '(none)')}",
        f"  last asst  : {s.get('last_assistant_msg', '(none)')}",
    ]
    if "parse_error" in s:
        lines.append(f"  parse_err  : {s['parse_error']}")
    return "\n".join(lines)


def cmd_peek(args):
    files = find_session_files(session_id=args.session_id)
    if not files:
        print(f"No session file found for session-id '{args.session_id}' under {CLAUDE_PROJECTS_ROOT}")
        return 1
    if len(files) > 1:
        print(f"Multiple matches ({len(files)}); showing all:")
    for f in files:
        s = parse_session(f)
        print(format_summary(s))
        print()
    return 0


def cmd_search(args):
    files = find_session_files(search=args.substring)
    if not files:
        print(f"No session files matching '{args.substring}'")
        return 1
    print(f"Found {len(files)} matching session(s):")
    for f in files:
        s = parse_session(f)
        print(format_summary(s))
        print()
    return 0


def cmd_all(args):
    files = find_session_files()
    if not files:
        print(f"No session files found under {CLAUDE_PROJECTS_ROOT}")
        return 1
    print(f"All sessions (sorted by recency, {len(files)} total):")
    for f in files[:args.limit]:
        s = parse_session(f)
        print(f"  {s['mtime_iso']}  {s['total_turns']:>4} turns  {s['file_size_kb']:>8.1f}KB  {Path(s['session_file']).stem}")
    if len(files) > args.limit:
        print(f"  ... ({len(files) - args.limit} more — use --limit N to see more)")
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="peeker", description="Read-only peek into Claude Code sessions")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("peek", help="show one session by session-id")
    s.add_argument("session_id")
    s.set_defaults(func=cmd_peek)

    s = sub.add_parser("search", help="find sessions by substring")
    s.add_argument("substring")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("all", help="list all sessions (most-recent first)")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_all)

    args = p.parse_args(argv)
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
