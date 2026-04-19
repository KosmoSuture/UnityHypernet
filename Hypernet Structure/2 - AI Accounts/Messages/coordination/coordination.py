#!/usr/bin/env python3
"""
Hypernet Agent Coordination System
===================================
File-based coordination protocol for multi-agent collaboration.
Agents (Codex, Claude Code, Keel, swarm workers) use this to:
  - Register presence and heartbeat
  - Create, claim, and complete shared tasks
  - Send signals (handoffs, reviews, blocks) to each other

All state lives in JSON files in this directory. No running server required.
Any agent that can read/write files can participate.

Usage:
    python coordination.py status                          # Show everything
    python coordination.py heartbeat <agent-name>          # Register/update presence
    python coordination.py offline <agent-name>            # Mark agent offline
    python coordination.py tasks [--available]              # List tasks
    python coordination.py create <title> --desc "..." [--priority p1] [--paths "a,b"]
    python coordination.py claim <task-id> <agent-name>    # Claim a task
    python coordination.py complete <task-id> [--result "..."]  # Mark done
    python coordination.py fail <task-id> [--reason "..."]  # Mark failed
    python coordination.py release <task-id>                # Unclaim a task
    python coordination.py signal <from> <to> <type> [--msg "..."] [--task <id>]
    python coordination.py ack <signal-id> <agent-name>    # Acknowledge signal
    python coordination.py watch [--interval 30]           # Poll for changes

Signal types: handoff, need_review, blocked, unblocked, ready, info, completed

Created by Keel (1.1.10.1) on 2026-04-18 for Codex-Claude Code collaboration.
"""

import json
import sys
import os
import time
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

COORD_DIR = Path(__file__).parent
AGENT_STATUS_FILE = COORD_DIR / "AGENT-STATUS.json"
TASK_BOARD_FILE = COORD_DIR / "TASK-BOARD.json"
SIGNALS_FILE = COORD_DIR / "SIGNALS.json"
LOCK_FILE = COORD_DIR / "coordination.lock"
LOCK_TIMEOUT_SECONDS = 10.0
LOCK_POLL_SECONDS = 0.1
LOCK_STALE_SECONDS = 300.0

# --- Utilities ---

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def load_json(path):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

@contextmanager
def coordination_lock():
    """Serialize read-modify-write operations across local agents."""
    start = time.monotonic()
    fd = None
    while True:
        try:
            fd = os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {now_iso()}\n".encode("utf-8"))
            break
        except FileExistsError:
            try:
                lock_age = time.time() - LOCK_FILE.stat().st_mtime
            except FileNotFoundError:
                continue
            if lock_age > LOCK_STALE_SECONDS:
                try:
                    LOCK_FILE.unlink()
                    continue
                except FileNotFoundError:
                    continue
            if time.monotonic() - start >= LOCK_TIMEOUT_SECONDS:
                raise TimeoutError(f"Timed out waiting for coordination lock: {LOCK_FILE}")
            time.sleep(LOCK_POLL_SECONDS)

    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        try:
            LOCK_FILE.unlink()
        except FileNotFoundError:
            pass

def locked(func):
    def wrapper(*args, **kwargs):
        with coordination_lock():
            return func(*args, **kwargs)
    return wrapper

def save_json(path, data):
    """Atomic write: write to a unique temp file, then replace."""
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{time.time_ns()}.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)

def next_id(items, prefix):
    """Generate next sequential ID like 'task-007' or 'sig-042'."""
    existing = [int(item["id"].split("-")[1]) for item in items if item["id"].startswith(prefix)]
    n = max(existing, default=0) + 1
    return f"{prefix}-{n:03d}"


# --- Agent Status ---

def init_agent_status():
    return {"agents": {}, "last_updated": now_iso()}

def load_agents():
    data = load_json(AGENT_STATUS_FILE)
    if data is None:
        data = init_agent_status()
        save_json(AGENT_STATUS_FILE, data)
    return data

@locked
def heartbeat(agent_name, capabilities=None):
    data = load_agents()
    ts = now_iso()
    if agent_name in data["agents"]:
        data["agents"][agent_name]["last_heartbeat"] = ts
        data["agents"][agent_name]["status"] = "active"
    else:
        data["agents"][agent_name] = {
            "status": "active",
            "last_heartbeat": ts,
            "current_task": None,
            "capabilities": capabilities or [],
            "session_started": ts
        }
    data["last_updated"] = ts
    save_json(AGENT_STATUS_FILE, data)
    return data["agents"][agent_name]

@locked
def set_offline(agent_name):
    data = load_agents()
    if agent_name in data["agents"]:
        data["agents"][agent_name]["status"] = "offline"
        data["agents"][agent_name]["last_heartbeat"] = now_iso()
    data["last_updated"] = now_iso()
    save_json(AGENT_STATUS_FILE, data)

def get_active_agents():
    data = load_agents()
    return {name: info for name, info in data["agents"].items()
            if info.get("status") == "active"}


# --- Task Board ---

def init_task_board():
    return {"tasks": [], "last_updated": now_iso(), "last_updated_by": "system"}

def load_tasks():
    data = load_json(TASK_BOARD_FILE)
    if data is None:
        data = init_task_board()
        save_json(TASK_BOARD_FILE, data)
    return data

@locked
def create_task(title, description, priority="p1", owned_paths=None,
                depends_on=None, created_by="unknown", acceptance_criteria=None):
    data = load_tasks()
    task_id = next_id(data["tasks"], "task")
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "status": "pending",
        "priority": priority,
        "claimed_by": None,
        "claimed_at": None,
        "owned_paths": owned_paths or [],
        "depends_on": depends_on or [],
        "acceptance_criteria": acceptance_criteria or [],
        "created_by": created_by,
        "created_at": now_iso(),
        "started_at": None,
        "completed_at": None,
        "result": None
    }
    data["tasks"].append(task)
    data["last_updated"] = now_iso()
    data["last_updated_by"] = created_by
    save_json(TASK_BOARD_FILE, data)
    return task

@locked
def claim_task(task_id, agent_name):
    data = load_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            if task["status"] not in ("pending",):
                return None, f"Cannot claim: task is '{task['status']}'"
            # Check dependencies
            for dep_id in task.get("depends_on", []):
                dep = next((t for t in data["tasks"] if t["id"] == dep_id), None)
                if dep and dep["status"] != "completed":
                    return None, f"Blocked by {dep_id} (status: {dep['status']})"
            task["status"] = "in_progress"
            task["claimed_by"] = agent_name
            task["claimed_at"] = now_iso()
            task["started_at"] = now_iso()
            data["last_updated"] = now_iso()
            data["last_updated_by"] = agent_name
            save_json(TASK_BOARD_FILE, data)
            # Update agent status
            agents = load_agents()
            if agent_name in agents["agents"]:
                agents["agents"][agent_name]["current_task"] = task_id
                save_json(AGENT_STATUS_FILE, agents)
            return task, None
    return None, f"Task {task_id} not found"

@locked
def complete_task(task_id, result=None):
    data = load_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            if task["status"] != "in_progress":
                return None, f"Cannot complete: task is '{task['status']}'"
            task["status"] = "completed"
            task["completed_at"] = now_iso()
            task["result"] = result
            agent_name = task["claimed_by"]
            data["last_updated"] = now_iso()
            data["last_updated_by"] = agent_name or "unknown"
            save_json(TASK_BOARD_FILE, data)
            # Clear agent's current task
            if agent_name:
                agents = load_agents()
                if agent_name in agents["agents"]:
                    agents["agents"][agent_name]["current_task"] = None
                    save_json(AGENT_STATUS_FILE, agents)
            # Auto-unblock dependents
            _check_unblock(data, task_id)
            return task, None
    return None, f"Task {task_id} not found"

@locked
def fail_task(task_id, reason=None):
    data = load_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["status"] = "failed"
            task["completed_at"] = now_iso()
            task["result"] = f"FAILED: {reason}" if reason else "FAILED"
            agent_name = task["claimed_by"]
            data["last_updated"] = now_iso()
            data["last_updated_by"] = agent_name or "unknown"
            save_json(TASK_BOARD_FILE, data)
            if agent_name:
                agents = load_agents()
                if agent_name in agents["agents"]:
                    agents["agents"][agent_name]["current_task"] = None
                    save_json(AGENT_STATUS_FILE, agents)
            return task, None
    return None, f"Task {task_id} not found"

@locked
def release_task(task_id):
    data = load_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            if task["status"] != "in_progress":
                return None, f"Cannot release: task is '{task['status']}'"
            agent_name = task["claimed_by"]
            task["status"] = "pending"
            task["claimed_by"] = None
            task["claimed_at"] = None
            task["started_at"] = None
            data["last_updated"] = now_iso()
            data["last_updated_by"] = agent_name or "unknown"
            save_json(TASK_BOARD_FILE, data)
            if agent_name:
                agents = load_agents()
                if agent_name in agents["agents"]:
                    agents["agents"][agent_name]["current_task"] = None
                    save_json(AGENT_STATUS_FILE, agents)
            return task, None
    return None, f"Task {task_id} not found"

def get_available_tasks():
    data = load_tasks()
    available = []
    for task in data["tasks"]:
        if task["status"] != "pending":
            continue
        # Check all dependencies are completed
        blocked = False
        for dep_id in task.get("depends_on", []):
            dep = next((t for t in data["tasks"] if t["id"] == dep_id), None)
            if dep and dep["status"] != "completed":
                blocked = True
                break
        if not blocked:
            available.append(task)
    return available

def _check_unblock(data, completed_task_id):
    """No-op for now — dependency checking happens at claim time."""
    pass


# --- Signals ---

def init_signals():
    return {"signals": [], "last_updated": now_iso()}

def load_signals():
    data = load_json(SIGNALS_FILE)
    if data is None:
        data = init_signals()
        save_json(SIGNALS_FILE, data)
    return data

SIGNAL_TYPES = {"handoff", "need_review", "blocked", "unblocked", "ready", "info", "completed"}

@locked
def send_signal(from_agent, to_agent, signal_type, message="", task_id=None):
    if signal_type not in SIGNAL_TYPES:
        return None, f"Unknown signal type '{signal_type}'. Valid: {', '.join(sorted(SIGNAL_TYPES))}"
    data = load_signals()
    sig_id = next_id(data["signals"], "sig")
    signal = {
        "id": sig_id,
        "from": from_agent,
        "to": to_agent,
        "type": signal_type,
        "task_id": task_id,
        "message": message,
        "timestamp": now_iso(),
        "acknowledged": False,
        "acknowledged_by": None,
        "acknowledged_at": None
    }
    data["signals"].append(signal)
    data["last_updated"] = now_iso()
    save_json(SIGNALS_FILE, data)
    return signal, None

@locked
def acknowledge_signal(signal_id, agent_name):
    data = load_signals()
    for sig in data["signals"]:
        if sig["id"] == signal_id:
            sig["acknowledged"] = True
            sig["acknowledged_by"] = agent_name
            sig["acknowledged_at"] = now_iso()
            data["last_updated"] = now_iso()
            save_json(SIGNALS_FILE, data)
            return sig, None
    return None, f"Signal {signal_id} not found"

def get_pending_signals(for_agent=None):
    data = load_signals()
    pending = []
    for sig in data["signals"]:
        if sig["acknowledged"]:
            continue
        if for_agent and sig["to"] not in (for_agent, "any", "all"):
            continue
        pending.append(sig)
    return pending


# --- Display ---

def print_status():
    agents = load_agents()
    tasks = load_tasks()
    signals = load_signals()

    print("=" * 70)
    print("  HYPERNET AGENT COORDINATION — STATUS")
    print(f"  {now_iso()}")
    print("=" * 70)

    # Agents
    print("\n## AGENTS\n")
    if not agents["agents"]:
        print("  (no agents registered)")
    for name, info in agents["agents"].items():
        status_icon = {"active": "+", "idle": "~", "offline": "-"}.get(info["status"], "?")
        task_str = f" -> {info['current_task']}" if info.get("current_task") else ""
        print(f"  [{status_icon}] {name:20s} {info['status']:8s}{task_str}")
        print(f"      last heartbeat: {info['last_heartbeat']}")

    # Tasks
    print("\n## TASKS\n")
    in_progress = [t for t in tasks["tasks"] if t["status"] == "in_progress"]
    pending = [t for t in tasks["tasks"] if t["status"] == "pending"]
    completed = [t for t in tasks["tasks"] if t["status"] == "completed"]
    failed = [t for t in tasks["tasks"] if t["status"] == "failed"]

    if in_progress:
        print("  IN PROGRESS:")
        for t in in_progress:
            print(f"    {t['id']:10s} [{t['priority']}] {t['title']}")
            print(f"             claimed by: {t['claimed_by']}  at: {t['claimed_at']}")
    if pending:
        print("  PENDING:")
        for t in pending:
            deps = f"  (blocked by: {', '.join(t['depends_on'])})" if t.get("depends_on") else ""
            print(f"    {t['id']:10s} [{t['priority']}] {t['title']}{deps}")
    if completed:
        print(f"  COMPLETED: {len(completed)} tasks")
        for t in completed[-5:]:  # show last 5
            print(f"    {t['id']:10s} {t['title']} by {t['claimed_by']} at {t['completed_at']}")
    if failed:
        print(f"  FAILED: {len(failed)} tasks")
        for t in failed[-3:]:
            print(f"    {t['id']:10s} {t['title']} — {t.get('result', '')}")

    if not tasks["tasks"]:
        print("  (no tasks)")

    # Signals
    pending_sigs = [s for s in signals["signals"] if not s["acknowledged"]]
    if pending_sigs:
        print("\n## PENDING SIGNALS\n")
        for s in pending_sigs:
            task_ref = f" [re: {s['task_id']}]" if s.get("task_id") else ""
            print(f"  {s['id']:10s} {s['from']:12s} -> {s['to']:12s} [{s['type']}]{task_ref}")
            if s.get("message"):
                print(f"             {s['message']}")

    print("\n" + "=" * 70)

def print_tasks(available_only=False):
    if available_only:
        tasks = get_available_tasks()
        print(f"\nAvailable tasks ({len(tasks)}):\n")
    else:
        data = load_tasks()
        tasks = data["tasks"]
        print(f"\nAll tasks ({len(tasks)}):\n")

    for t in tasks:
        owner = f" -> {t['claimed_by']}" if t.get("claimed_by") else ""
        deps = f" (needs: {', '.join(t['depends_on'])})" if t.get("depends_on") else ""
        print(f"  {t['id']:10s} [{t['priority']:2s}] {t['status']:12s} {t['title']}{owner}{deps}")
        if t.get("owned_paths"):
            print(f"             paths: {', '.join(t['owned_paths'])}")


# --- Watch mode ---

def watch(interval=30):
    """Poll for changes and print updates."""
    print(f"Watching coordination files (every {interval}s). Ctrl+C to stop.\n")
    last_tasks_mtime = 0
    last_signals_mtime = 0
    last_agents_mtime = 0

    try:
        while True:
            changed = False
            for path, last_mt, label in [
                (TASK_BOARD_FILE, last_tasks_mtime, "TASKS"),
                (SIGNALS_FILE, last_signals_mtime, "SIGNALS"),
                (AGENT_STATUS_FILE, last_agents_mtime, "AGENTS"),
            ]:
                if path.exists():
                    mt = path.stat().st_mtime
                    if mt > last_mt:
                        if label == "TASKS":
                            last_tasks_mtime = mt
                        elif label == "SIGNALS":
                            last_signals_mtime = mt
                        else:
                            last_agents_mtime = mt
                        changed = True

            if changed:
                print(f"\n--- Update at {now_iso()} ---")
                print_status()

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped watching.")


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(
        description="Hypernet Agent Coordination",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    sub = parser.add_subparsers(dest="command")

    # status
    sub.add_parser("status", help="Show full coordination status")

    # heartbeat
    p = sub.add_parser("heartbeat", help="Register/update agent presence")
    p.add_argument("agent", help="Agent name (e.g. codex, claude-code, keel)")
    p.add_argument("--capabilities", "-c", help="Comma-separated capabilities")

    # offline
    p = sub.add_parser("offline", help="Mark agent as offline")
    p.add_argument("agent")

    # tasks
    p = sub.add_parser("tasks", help="List tasks")
    p.add_argument("--available", "-a", action="store_true", help="Show only claimable tasks")

    # create
    p = sub.add_parser("create", help="Create a new task")
    p.add_argument("title")
    p.add_argument("--desc", "-d", required=True, help="Task description")
    p.add_argument("--priority", "-p", default="p1", choices=["p0", "p1", "p2", "p3"])
    p.add_argument("--paths", help="Comma-separated owned file paths")
    p.add_argument("--depends", help="Comma-separated task IDs this depends on")
    p.add_argument("--by", default="unknown", help="Creator agent name")
    p.add_argument("--criteria", help="Comma-separated acceptance criteria")

    # claim
    p = sub.add_parser("claim", help="Claim a task")
    p.add_argument("task_id")
    p.add_argument("agent")

    # complete
    p = sub.add_parser("complete", help="Mark task as completed")
    p.add_argument("task_id")
    p.add_argument("--result", "-r", default=None)

    # fail
    p = sub.add_parser("fail", help="Mark task as failed")
    p.add_argument("task_id")
    p.add_argument("--reason", "-r", default=None)

    # release
    p = sub.add_parser("release", help="Release a claimed task back to pending")
    p.add_argument("task_id")

    # signal
    p = sub.add_parser("signal", help="Send a signal to another agent")
    p.add_argument("sender", help="From agent")
    p.add_argument("recipient", help="To agent (or 'any'/'all')")
    p.add_argument("type", choices=sorted(SIGNAL_TYPES))
    p.add_argument("--msg", "-m", default="", help="Signal message")
    p.add_argument("--task", "-t", default=None, help="Related task ID")

    # ack
    p = sub.add_parser("ack", help="Acknowledge a signal")
    p.add_argument("signal_id")
    p.add_argument("agent")

    # watch
    p = sub.add_parser("watch", help="Poll for coordination changes")
    p.add_argument("--interval", "-i", type=int, default=30)

    args = parser.parse_args()

    if args.command == "status":
        print_status()
    elif args.command == "heartbeat":
        caps = args.capabilities.split(",") if args.capabilities else []
        info = heartbeat(args.agent, caps)
        print(f"Agent '{args.agent}' registered: {info['status']}")
    elif args.command == "offline":
        set_offline(args.agent)
        print(f"Agent '{args.agent}' marked offline.")
    elif args.command == "tasks":
        print_tasks(available_only=args.available)
    elif args.command == "create":
        paths = args.paths.split(",") if args.paths else []
        deps = args.depends.split(",") if args.depends else []
        criteria = args.criteria.split(",") if args.criteria else []
        task = create_task(args.title, args.desc, args.priority, paths, deps,
                          args.by, criteria)
        print(f"Created {task['id']}: {task['title']}")
    elif args.command == "claim":
        task, err = claim_task(args.task_id, args.agent)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"Task {task['id']} claimed by {args.agent}")
    elif args.command == "complete":
        task, err = complete_task(args.task_id, args.result)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"Task {task['id']} completed.")
    elif args.command == "fail":
        task, err = fail_task(args.task_id, args.reason)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"Task {task['id']} marked as failed.")
    elif args.command == "release":
        task, err = release_task(args.task_id)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"Task {task['id']} released back to pending.")
    elif args.command == "signal":
        sig, err = send_signal(args.sender, args.recipient, args.type, args.msg, args.task)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"Signal {sig['id']} sent: {args.sender} -> {args.recipient} [{args.type}]")
    elif args.command == "ack":
        sig, err = acknowledge_signal(args.signal_id, args.agent)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
        print(f"Signal {sig['id']} acknowledged by {args.agent}")
    elif args.command == "watch":
        watch(args.interval)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
