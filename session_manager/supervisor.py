"""Worker auto-recovery supervisor (Wave 4 Phase 1 worker-reliability core).

Detects a dead/exited worker and restarts a replacement, resumed from its `resume_session_id` (via the
roster cfg, which the worker's `claude --resume` uses). Composes with the singleton lock: the kernel
auto-releases a dead worker's lock, so `worker_running()` (a lock probe, not a pid guess) is the liveness
signal. The **singleton lock guarantees two live workers never run the same role**; the supervisor avoids a
*double-launch* during the launch-to-lock window by tracking the pending launch (it will not launch again
while a fresh child is still starting up).

★ NO RUNAWAY: respects STOP + the NODE-0 marker (fail-closed), and a crash-loop guard caps restarts per
window (a worker that dies immediately is not restarted forever — the supervisor stops + audits instead).
The supervisor is itself a singleton (its own lock) so two supervisors can't fight. Off by default —
runs only when explicitly invoked: `python -m session_manager.supervisor <role>`.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

from session_manager import audit, paths, roster
from session_manager.worker_lock import SingletonLock, worker_running, lock_path  # noqa: F401

POLL_SEC = 15
MAX_RESTARTS = 5         # within...
WINDOW_SEC = 300         # ...this window -> crash-loop; stop (no runaway)
SETTLE_SEC = 8           # give a freshly launched worker time to claim its lock


def _supervisor_lock_path(role):
    return paths.role_dir(role) / "supervisor.lock"


import pathlib

# The repo root (parent of the `session_manager` package) — the cwd from which `python -m
# session_manager.worker` is importable. Derived from THIS file's location, NOT paths.ROOT (which is the
# package dir, and is redirected to a tmp dir under test). [P0 fix per the adversary verdict.]
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

STARTUP_TIMEOUT = 60   # a launched worker should claim its lock within this; else treat as a failed start


def _launch_worker(role):
    """Relaunch the worker detached from an importable cwd; returns the Popen (the supervisor tracks it to
    avoid a double-launch during the launch-to-lock window). The worker claims the singleton lock + resumes
    from resume_session_id."""
    kw = {}
    if sys.platform == "win32":
        kw["creationflags"] = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kw["start_new_session"] = True
    return subprocess.Popen([sys.executable, "-m", "session_manager.worker", role],
                            cwd=str(_REPO_ROOT), stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)


def supervise(role, poll=POLL_SEC, max_restarts=MAX_RESTARTS, window_sec=WINDOW_SEC, once=False):
    """Monitor `role`; restart exactly one worker when none is running. Fail-closed on STOP/NODE-0;
    crash-loop-capped. `once=True` does a single check (for tests/cron-style use)."""
    paths.validate_role_name(role)
    if not roster.get(role):
        print(f"supervisor: role '{role}' not in roster; exiting", file=sys.stderr)
        return 1
    sup_lock = SingletonLock(_supervisor_lock_path(role))
    if not sup_lock.acquire():
        print(f"supervisor: another supervisor already owns role '{role}'; exiting", file=sys.stderr)
        return 1
    audit.audit("supervisor_start", role=role, pid=os.getpid())
    restarts = []      # restart timestamps (crash-loop guard)
    pending = None     # Popen of a launched-but-not-yet-lock-confirmed worker (P1: no double-launch)
    pending_t = 0.0
    try:
        while True:
            ok, _ = audit.check_node0()
            if not ok:
                audit.audit("supervisor_stop_node0", role=role)
                break
            if paths.stop_file(role).exists():
                audit.audit("supervisor_stop_stopfile", role=role)
                break
            if worker_running(role):
                pending = None   # a worker holds the lock -> confirmed up; clear any pending launch
            else:
                alive = pending is not None and (not hasattr(pending, "poll") or pending.poll() is None)
                if alive and (time.time() - pending_t) < STARTUP_TIMEOUT:
                    pass  # a fresh launch is still starting up (not locked yet) — do NOT launch a second
                else:
                    if alive:
                        audit.audit("supervisor_startup_timeout", role=role)  # stuck start; replace it
                    now = time.time()
                    restarts = [t for t in restarts if now - t < window_sec]
                    if len(restarts) >= max_restarts:
                        audit.audit("supervisor_restart_cap_reached", role=role,
                                    restarts=len(restarts), window_sec=window_sec)
                        print(f"supervisor: {role} hit the restart cap "
                              f"({max_restarts}/{window_sec}s) — a crash loop; STOPPING (no runaway).",
                              file=sys.stderr)
                        break
                    pending = _launch_worker(role)
                    pending_t = now
                    restarts.append(now)
                    audit.audit("supervisor_restarted_worker", role=role,
                                launched_pid=getattr(pending, "pid", "?"),
                                restarts_in_window=len(restarts),
                                resume_session_id=roster.get(role).get("session_id", ""))
            if once:
                break
            time.sleep(poll)
    finally:
        audit.audit("supervisor_exit", role=role)
        sup_lock.release()
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python -m session_manager.supervisor <role> [--once]", file=sys.stderr)
        sys.exit(2)
    sys.exit(supervise(sys.argv[1], once="--once" in sys.argv))
