"""Filesystem layout for session_manager.

★ S.6 (Codex 2026-06-03): role names are now strictly validated via allowlist
to prevent path traversal. `role_dir()` resolves the path + asserts containment
under SESSIONS_DIR; any role name that resolves outside (via .. or absolute
prefixes) is rejected at the boundary.

★ S.5: NODE_0_MARKER documented here, checked by auth.check_node0().
"""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SESSIONS_DIR = ROOT / "sessions"
ROSTER_PATH = ROOT / "roster.json"
AUDIT_LOG = ROOT / "audit.jsonl"  # global append-only sm-action log

# ★ S.5 — NODE-0 founder-authorization marker. Deleting this is the
# founder's fail-closed kill for the entire CODE-0 stack (sm + spawned AIs).
NODE_0_MARKER = Path(r"C:/Users/spamm/.hypernet/node0-authorization.json")

# ★ S.6 — Strict role-name allowlist. Lowercase alphanumeric + underscore + hyphen,
# 1-64 chars. Prevents path-traversal and unicode-confusion attacks.
_ROLE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class InvalidRoleName(ValueError):
    """Raised when a role name fails the allowlist regex or path-confinement check."""


def validate_role_name(role: str) -> None:
    """Validate role name format. Raises InvalidRoleName on failure."""
    if not isinstance(role, str):
        raise InvalidRoleName(f"role name must be str, got {type(role).__name__}")
    if not _ROLE_NAME_RE.match(role):
        raise InvalidRoleName(
            f"role name {role!r} fails allowlist [a-z0-9][a-z0-9_-]{{0,63}}; "
            f"reject (prevents path traversal + unicode confusion)"
        )


def _assert_under_sessions(p: Path) -> Path:
    """Resolve `p` and assert it stays inside SESSIONS_DIR. Raises InvalidRoleName."""
    resolved = p.resolve()
    sessions_resolved = SESSIONS_DIR.resolve()
    try:
        resolved.relative_to(sessions_resolved)
    except ValueError:
        raise InvalidRoleName(
            f"path {p!r} resolves to {resolved!r}, outside SESSIONS_DIR "
            f"{sessions_resolved!r}; reject (path traversal attempt)"
        )
    return resolved


def role_dir(role: str) -> Path:
    """Return the role's session directory. Validates + confines."""
    validate_role_name(role)
    candidate = SESSIONS_DIR / role
    _assert_under_sessions(candidate)
    return candidate


def commands_dir(role: str) -> Path:
    return role_dir(role) / "commands"


def processed_dir(role: str) -> Path:
    return role_dir(role) / "processed"


def stream_log(role: str) -> Path:
    return role_dir(role) / "stream.jsonl"


def status_path(role: str) -> Path:
    return role_dir(role) / "status.json"


def status_history(role: str) -> Path:
    return role_dir(role) / "status.history.jsonl"


def stop_file(role: str) -> Path:
    return role_dir(role) / "STOP"


def worker_pid(role: str) -> Path:
    return role_dir(role) / "worker.pid"


def ensure_role(role: str):
    role_dir(role).mkdir(parents=True, exist_ok=True)
    commands_dir(role).mkdir(parents=True, exist_ok=True)
    processed_dir(role).mkdir(parents=True, exist_ok=True)
