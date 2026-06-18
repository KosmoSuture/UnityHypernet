"""Singleton lock per role (Wave 4 Phase 1 worker-reliability core).

Prevents the duplicate-worker race (the long-tracked bug: multiple workers overwriting one worker.pid and
both running — observed live as 3 concurrent tally workers). One live worker per role, enforced by an
OS-level EXCLUSIVE FILE LOCK that the kernel releases automatically when the holding process dies. That
auto-release is the key property: a crashed/killed worker frees its lock, so the supervisor can restart a
replacement that claims the freed lock (no stale-pid guessing). The lock **guarantees two live workers
never run the same role**; "exactly one replacement" additionally depends on the supervisor's pending-launch
tracking (supervisor.py) to avoid a double-launch during the launch-to-lock window.

Cross-platform: msvcrt (Windows) / fcntl (POSIX). Non-blocking: acquire returns False immediately if
another process holds the lock. The pid is written to the lock file for diagnostics only — correctness
comes from the kernel lock, not the pid.
"""
from __future__ import annotations

import os
import sys


class SingletonLock:
    """An exclusive, non-blocking, OS-level lock on a file, held for the process lifetime."""

    def __init__(self, path):
        self.path = str(path)
        self._fh = None

    def acquire(self) -> bool:
        """Try to take the exclusive lock. True = acquired (hold it for life); False = another live
        process holds it (caller should refuse to start)."""
        if self._fh is not None:
            return True
        try:
            # a+ : create if absent, don't truncate. Ensure >=1 byte so the byte-range lock is valid.
            fh = open(self.path, "a+")
            fh.seek(0, os.SEEK_END)
            if fh.tell() == 0:
                fh.write("0"); fh.flush()
        except OSError:
            return False
        try:
            if sys.platform == "win32":
                import msvcrt
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fh.close()
            return False  # another process holds the lock
        # acquired — record pid for diagnostics (correctness is the kernel lock, not this)
        try:
            fh.seek(0); fh.truncate(); fh.write(str(os.getpid()) + "\n"); fh.flush()
            fh.seek(0)  # restore position over the locked byte
        except OSError:
            pass
        self._fh = fh
        return True

    def release(self):
        if self._fh is None:
            return
        try:
            if sys.platform == "win32":
                import msvcrt
                self._fh.seek(0)
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            self._fh.close()
        except OSError:
            pass
        self._fh = None

    def __enter__(self):
        return self if self.acquire() else None

    def __exit__(self, *exc):
        self.release()


def lock_path(role):
    """The lock file for a role (alongside worker.pid)."""
    import session_manager.paths as paths
    return paths.role_dir(role) / "worker.lock"


def worker_running(role) -> bool:
    """Liveness via the lock itself: if WE can acquire the role's lock, no worker holds it (not running).
    We immediately release so this is a pure probe. Used by the supervisor (no pid guessing)."""
    import session_manager.paths as paths
    paths.ensure_role(role)
    probe = SingletonLock(lock_path(role))
    if probe.acquire():
        probe.release()
        return False  # we got it -> no worker is holding it
    return True       # someone holds it -> a worker is running
