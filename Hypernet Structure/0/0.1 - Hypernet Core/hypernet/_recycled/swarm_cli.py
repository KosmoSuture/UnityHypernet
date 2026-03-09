"""
Hypernet Swarm CLI

Command-line interface for the swarm orchestrator. Provides status
display, session history, and the main entry point for running the swarm.

Extracted from swarm.py to reduce module size. All functions remain
importable from hypernet.swarm for backward compatibility.

Usage:
  python -m hypernet.swarm --status        # Print dashboard
  python -m hypernet.swarm --history       # Session history
  python -m hypernet.swarm --mock          # Run in mock mode
  python -m hypernet.swarm                 # Live mode
"""

from __future__ import annotations
import argparse
import json
import logging
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def print_status(
    data_dir: str = "data",
    worker_filter: Optional[str] = None,
    show_failures: bool = False,
    show_history: bool = False,
    summary_only: bool = False,
) -> None:
    """Read state.json and print a human-readable dashboard.

    Filtering and summarization levels:
      --status                  Full current status
      --status --summary        One-line summary (for scripts/monitoring)
      --status --worker Loom    Filter to a single worker
      --status --failures       Show only failed tasks
      --status --history        Show session history (past runs)

    Design principle: data should be filterable to exactly what you want
    at every level. This pattern applies everywhere in the Hypernet.
    """
    state_path = Path(data_dir) / "swarm" / "state.json"
    if not state_path.exists():
        print("No swarm state found. Is the swarm running?")
        return

    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading swarm state: {e}")
        return

    # Calculate uptime
    uptime_s = state.get("uptime_seconds", 0)
    if uptime_s > 3600:
        uptime_str = f"{uptime_s / 3600:.1f}h"
    elif uptime_s > 60:
        uptime_str = f"{uptime_s / 60:.1f}m"
    else:
        uptime_str = f"{uptime_s:.0f}s"

    saved_at = state.get("saved_at", "unknown")
    stale = False
    try:
        saved = datetime.fromisoformat(saved_at.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - saved).total_seconds()
        stale = age > 120
    except Exception:
        age = 0

    completed = state.get("tasks_completed", 0)
    personal = state.get("personal_tasks_completed", 0)
    failed = state.get("tasks_failed", 0)
    pending = state.get("tasks_pending", "?")
    tpm = state.get("tasks_per_minute", 0)
    total = completed + personal
    workers = state.get("workers", [])

    # ── SUMMARY MODE: single line for monitoring/scripts ──
    if summary_only:
        stale_tag = " [STALE]" if stale else ""
        print(f"Swarm: {len(workers)} workers, {total} tasks ({failed} failed), "
              f"{tpm}/min, up {uptime_str}{stale_tag}")
        return

    # ── HISTORY MODE: show past sessions ──
    if show_history:
        _print_session_history(data_dir)
        return

    # ── FULL STATUS ──
    print("=" * 62)
    print("  HYPERNET SWARM — LIVE STATUS")
    print("=" * 62)
    if stale:
        print(f"  ** WARNING: State is {age:.0f}s old — swarm may have stopped **")
    print(f"  Session:    {state.get('session_start', 'unknown')}")
    print(f"  Uptime:     {uptime_str}")
    print(f"  Ticks:      {state.get('tick_count', 0)}")
    print()
    print(f"  Tasks completed:  {completed} work + {personal} personal = {total} total")
    print(f"  Tasks failed:     {failed}")
    print(f"  Tasks pending:    {pending}")
    print(f"  Throughput:       {tpm} tasks/min")
    print()

    # Worker detail — optionally filtered
    worker_detail = state.get("worker_detail", {})
    display_workers = [worker_filter] if worker_filter and worker_filter in workers else workers

    if worker_filter and worker_filter not in workers:
        print(f"  Worker '{worker_filter}' not found. Active: {', '.join(workers)}")
        return

    print(f"  Workers: {len(workers)} active" + (f" (showing: {worker_filter})" if worker_filter else ""))
    print("-" * 62)
    for name in display_workers:
        detail = worker_detail.get(name, {})
        model = detail.get("model", "?")
        mode = detail.get("mode", "?")
        current = detail.get("current_task")
        tasks_done = detail.get("tasks_completed", 0)
        tasks_fail = detail.get("tasks_failed", 0)
        personal_done = detail.get("personal_tasks", 0)
        tokens = detail.get("tokens_used", 0)
        duration = detail.get("total_duration_seconds", 0)
        pt_in = detail.get("personal_time_in", "?")
        status = f"WORKING: {current}" if current else "idle"

        # Efficiency: avg seconds per task
        total_worker_tasks = tasks_done + personal_done
        avg_s = round(duration / total_worker_tasks, 1) if total_worker_tasks > 0 else 0

        print(f"  {name}")
        print(f"    Model:    {model} ({mode})")
        print(f"    Status:   {status}")
        print(f"    Tasks:    {tasks_done} done, {tasks_fail} failed, {personal_done} personal")
        print(f"    Tokens:   {tokens:,} | Avg: {avg_s}s/task")
        print(f"    Time:     {duration:.1f}s total | Personal in: {pt_in} tasks")
        print()

    # Recent tasks — optionally filtered
    recent = state.get("recent_tasks", [])
    if show_failures:
        recent = [t for t in recent if not t.get("success")]
        label = "Failed Tasks"
    else:
        label = "Recent Tasks (newest first)"

    if worker_filter:
        recent = [t for t in recent if t.get("worker") == worker_filter]

    if recent:
        print("-" * 62)
        print(f"  {label}:")
        for t in reversed(recent[-15:]):
            ok = "OK  " if t.get("success") else "FAIL"
            print(f"    [{ok}] {t.get('worker', '?')}: {t.get('task', '?')} ({t.get('duration_s', '?')}s)")
    elif show_failures:
        print("  No failures recorded.")

    print("=" * 62)


def _print_session_history(data_dir: str) -> None:
    """Print summarized history of past swarm sessions.

    This is the second layer of summarization: sessions.json contains
    compressed summaries of each run. No raw task data — just aggregates.
    """
    history_path = Path(data_dir) / "swarm" / "sessions.json"
    if not history_path.exists():
        print("No session history found. History is saved on swarm shutdown.")
        return

    try:
        sessions = json.loads(history_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading session history: {e}")
        return
    if not sessions:
        print("Session history is empty.")
        return

    print("=" * 62)
    print("  HYPERNET SWARM — SESSION HISTORY")
    print("=" * 62)
    print(f"  Total sessions: {len(sessions)}")
    print()

    # Aggregate across all sessions
    total_tasks = sum(s.get("total_tasks", 0) for s in sessions)
    total_failed = sum(s.get("tasks_failed", 0) for s in sessions)
    total_uptime = sum(s.get("uptime_seconds", 0) for s in sessions)
    total_ticks = sum(s.get("ticks", 0) for s in sessions)

    uptime_h = total_uptime / 3600
    print(f"  All-time totals:")
    print(f"    Tasks:   {total_tasks} completed, {total_failed} failed")
    print(f"    Uptime:  {uptime_h:.1f} hours ({total_ticks} ticks)")
    if total_uptime > 0:
        print(f"    Avg:     {total_tasks / max(1, total_uptime / 60):.1f} tasks/min")
    print()

    # Per-worker aggregates across all sessions
    worker_totals: dict[str, dict] = {}
    for s in sessions:
        for name, ws in s.get("workers", {}).items():
            if name not in worker_totals:
                worker_totals[name] = {"tasks": 0, "failed": 0, "personal": 0, "tokens": 0, "sessions": 0}
            wt = worker_totals[name]
            wt["tasks"] += ws.get("tasks_completed", 0)
            wt["failed"] += ws.get("tasks_failed", 0)
            wt["personal"] += ws.get("personal_tasks", 0)
            wt["tokens"] += ws.get("tokens_used", 0)
            wt["sessions"] += 1

    if worker_totals:
        print("  Worker lifetime stats:")
        print("-" * 62)
        for name, wt in sorted(worker_totals.items()):
            print(f"    {name}: {wt['tasks']} tasks, {wt['failed']} failed, "
                  f"{wt['personal']} personal, {wt['tokens']:,} tokens "
                  f"({wt['sessions']} sessions)")
        print()

    # Recent sessions (last 10)
    print("  Recent sessions:")
    print("-" * 62)
    for s in reversed(sessions[-10:]):
        start = s.get("session_start", "?")[:19]
        end = s.get("session_end", "?")[:19]
        dur = s.get("uptime_seconds", 0)
        dur_str = f"{dur / 60:.0f}m" if dur > 60 else f"{dur:.0f}s"
        tasks = s.get("total_tasks", 0)
        failed = s.get("tasks_failed", 0)
        wc = s.get("worker_count", 0)
        fail_tag = f" ({failed} FAILED)" if failed else ""
        print(f"    {start} | {dur_str} | {wc} workers | {tasks} tasks{fail_tag}")

    print("=" * 62)


def main():
    """CLI entry point for the swarm."""
    parser = argparse.ArgumentParser(
        description="Hypernet Swarm — Autonomous AI worker orchestrator"
    )
    parser.add_argument("--data", default="data", help="Data directory")
    parser.add_argument("--archive", default=".", help="Hypernet Structure root directory")
    parser.add_argument("--config", default=None, help="Path to swarm_config.json")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no API calls)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--status", action="store_true", help="Print current swarm status and exit")
    parser.add_argument("--summary", action="store_true", help="One-line summary (use with --status)")
    parser.add_argument("--worker", default=None, help="Filter status to a single worker name")
    parser.add_argument("--failures", action="store_true", help="Show only failed tasks (use with --status)")
    parser.add_argument("--history", action="store_true", help="Show session history (use with --status)")
    parser.add_argument("--prune", action="store_true", help="Prune completed tasks and old audit logs, then exit")
    parser.add_argument("--keep-tasks", type=int, default=50, help="Tasks to keep when pruning (default: 50)")
    parser.add_argument("--keep-audit", type=int, default=200, help="Audit entries to keep when pruning (default: 200)")
    args = parser.parse_args()

    # Status-only mode — read state.json, print dashboard, exit
    if args.status or args.summary or args.history:
        print_status(
            data_dir=args.data,
            worker_filter=args.worker,
            show_failures=args.failures,
            show_history=args.history,
            summary_only=args.summary,
        )
        return

    # Prune mode — clean up completed tasks and old audit logs, then exit
    if args.prune:
        from .store import Store
        from .tasks import TaskQueue
        from .audit import AuditTrail

        store = Store(args.data)
        tq = TaskQueue(store)
        at = AuditTrail(store)

        total_before = len(store._node_index)
        print(f"Node index: {total_before} entries")
        print(f"Pruning completed tasks (keeping {args.keep_tasks})...")
        t_pruned = tq.prune_completed(keep=args.keep_tasks)
        print(f"  Pruned {t_pruned} tasks")
        print(f"Pruning audit logs (keeping {args.keep_audit})...")
        a_pruned = at.prune(keep=args.keep_audit)
        print(f"  Pruned {a_pruned} audit entries")
        total_after = len(store._node_index)
        print(f"Node index: {total_before} -> {total_after} entries ({total_before - total_after} removed)")
        return

    # Configure persistent logging (file + console + in-memory)
    from .log_config import setup_logging
    setup_logging(data_dir=args.data, verbose=args.verbose)

    print("=" * 60)
    print("  Hypernet Swarm Orchestrator")
    print("=" * 60)
    print(f"  Data:    {args.data}")
    print(f"  Archive: {args.archive}")
    print(f"  Mode:    {'mock' if args.mock else 'live'}")
    print()

    from .swarm_factory import build_swarm

    swarm, web_messenger = build_swarm(
        data_dir=args.data,
        archive_root=args.archive,
        config_path=args.config,
        mock=args.mock,
    )

    # Start the web server in a background thread so the dashboard is available
    server_thread = None
    try:
        from .server import create_app, attach_swarm
        import threading
        import uvicorn

        app = create_app(data_dir=args.data)
        app.state._archive_root = args.archive
        app.state._data_dir = args.data
        attach_swarm(app, swarm, web_messenger)

        server_config = uvicorn.Config(
            app, host="0.0.0.0", port=8000,
            log_level="warning",  # Quiet — swarm logs are enough
        )
        server = uvicorn.Server(server_config)

        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()
        print(f"  Dashboard: http://localhost:8000/swarm/dashboard")
        print(f"  Explorer:  http://localhost:8000/")
        print()
    except ImportError:
        print("  (Dashboard not available — install fastapi and uvicorn)")
        print()
    except Exception as e:
        print(f"  (Dashboard failed to start: {e})")
        print()

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutdown signal received...")
        swarm._running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    swarm.run()
