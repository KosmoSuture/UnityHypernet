"""Append-only audit log + status writers (revision-transparent — no silent edits).

Status updates write the current state to status.json AND append a hash-chained
entry to status.history.jsonl. The history is the audit substrate; status.json
is a convenience view that always matches the latest history entry.

★ S.4 (Codex 2026-06-03): write_status now validates `resume_session_id` against
the roster — a forged UID in a status write is rejected at the boundary.

★ S.5 (Codex 2026-06-03): check_node0() helper added. Workers and sm CLI commands
fail-closed when the NODE-0 marker is absent.

★ S.3 / "recompute-and-propagate attack" is still a known gap (deferred to a
proper design pass with key-storage decisions). Current chain catches honest
mistakes; not authenticated against a determined local writer.
"""
import hashlib
import json
import os
import time
from pathlib import Path
from . import paths


def check_node0() -> tuple[bool, str]:
    """★ S.5 — Returns (ok, msg). False if NODE-0 marker absent → fail-closed."""
    if not paths.NODE_0_MARKER.exists():
        return False, (
            f"NODE-0 marker absent at {paths.NODE_0_MARKER} — fail-closed "
            f"(founder deletion = revoke authorization for entire sm stack)"
        )
    return True, "NODE-0 marker present"


def require_node0():
    """Helper: raise on missing NODE-0 marker. Use at command boundaries."""
    ok, msg = check_node0()
    if not ok:
        raise PermissionError(msg)

def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _sha256_of(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def _last_history_hash(history_path: Path) -> str:
    if not history_path.exists():
        return "GENESIS"
    last_line = ""
    with history_path.open("rb") as f:
        for line in f:
            if line.strip():
                last_line = line.decode("utf-8")
    if not last_line:
        return "GENESIS"
    return json.loads(last_line)["hash"]

def write_status(role: str, **fields):
    """Atomic-ish status update: write status.json + append to status.history.jsonl.

    ★ S.4 — If `resume_session_id` is present in fields, it MUST equal
    roster[role].session_id. Mismatch raises InvalidResumeSessionID — fail-closed
    on UID forgery attempts.
    """
    # ★ S.4: validate resume_session_id against roster if claimed
    if "resume_session_id" in fields:
        # Import lazily to avoid circular import
        from . import roster as _roster
        cfg = _roster.get(role)
        if cfg is None:
            raise InvalidResumeSessionID(
                f"write_status: role {role!r} not in roster; cannot validate "
                f"resume_session_id claim {fields['resume_session_id']!r}"
            )
        if fields["resume_session_id"] != cfg.get("session_id"):
            raise InvalidResumeSessionID(
                f"write_status: claimed resume_session_id "
                f"{fields['resume_session_id']!r} does not match "
                f"roster[{role}].session_id={cfg.get('session_id')!r} — fail-closed "
                f"(prevents UID forgery / status injection)"
            )
    status_p = paths.status_path(role)
    history_p = paths.status_history(role)
    paths.ensure_role(role)
    prev_hash = _last_history_hash(history_p)
    entry = {
        "role": role,
        "ts": _now_iso(),
        "prev_hash": prev_hash,
        **fields,
    }
    canon = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")
    entry["hash"] = _sha256_of((prev_hash + ":" + canon.decode("utf-8")).encode("utf-8"))
    # Append to history (append-only)
    with history_p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    # Overwrite status.json (always reflects latest)
    status_p.write_text(json.dumps(entry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return entry


class InvalidResumeSessionID(ValueError):
    """★ S.4 — Raised when a status write claims a resume_session_id that
    doesn't match the role's roster entry. Fail-closed to prevent UID forgery."""

def read_status(role: str) -> dict:
    p = paths.status_path(role)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))

def audit(action: str, actor: str = "sm", **fields):
    """Global sm-action audit (commands queued, kills issued, spawns started)."""
    prev_hash = _last_history_hash(paths.AUDIT_LOG)
    entry = {
        "ts": _now_iso(),
        "actor": actor,
        "action": action,
        "prev_hash": prev_hash,
        **fields,
    }
    canon = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")
    entry["hash"] = _sha256_of((prev_hash + ":" + canon.decode("utf-8")).encode("utf-8"))
    with paths.AUDIT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry

def verify_chain(history_path: Path) -> tuple[bool, str]:
    """Verify the hash chain of an append-only log. Returns (ok, message)."""
    if not history_path.exists():
        return True, "no entries"
    prev = "GENESIS"
    n = 0
    with history_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            entry = json.loads(line)
            n += 1
            if entry.get("prev_hash") != prev:
                return False, f"break at entry {n}: prev_hash {entry.get('prev_hash')[:8]} != expected {prev[:8]}"
            # Recompute hash
            claimed = entry.pop("hash")
            canon = json.dumps(entry, sort_keys=True, separators=(",", ":")).encode("utf-8")
            expected = _sha256_of((prev + ":" + canon.decode("utf-8")).encode("utf-8"))
            if claimed != expected:
                return False, f"hash mismatch at entry {n}: {claimed[:8]} != {expected[:8]}"
            prev = claimed
    return True, f"{n} entries verified"
