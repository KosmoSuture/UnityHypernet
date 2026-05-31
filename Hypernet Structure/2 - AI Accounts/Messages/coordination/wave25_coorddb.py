#!/usr/bin/env python3
"""Wave 2.5 atomic coordination database.

H2 substrate: per-project SQLite hot state for roster rows, edit locks,
heartbeats, work-package claims, and append-only coordination events. The
markdown board remains the durable archive; this database is temp coordination
state and can be snapshotted back to markdown.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import wave1_board
import wave1_board_writer


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROJECT_ID = "wave-2.5"
DEFAULT_DB_PATH = SCRIPT_DIR / "wave25_coordination.sqlite3"
DEFAULT_SNAPSHOT_PATH = SCRIPT_DIR / "wave25_coordination_snapshot.md"
SCHEMA_VERSION = 2
DEFAULT_LOCK_TTL_SECONDS = 1800
SECRET_KEY_MARKERS = ("token", "secret", "password", "api_key", "apikey", "cookie", "webhook")
ALLOWED_SECRETISH_KEYS = {"credential_locator", "vault_ref"}


class CoordinationDbError(ValueError):
    pass


@dataclass
class RosterState:
    project_id: str
    slot: str
    chosen_name: str = ""
    role: str = ""
    current_task: str = ""
    blocked_on: str = ""
    last_handoff: str = ""
    updated_at: str = ""
    revision: int = 0
    expected_revision: int | None = None
    last_writer: str = ""
    payload: dict[str, Any] | None = None


@dataclass
class EditLockState:
    project_id: str
    lock_name: str
    target: str
    holder: str
    claimed_at: str
    expires_at: str
    note: str = ""
    status: str = "active"
    payload: dict[str, Any] | None = None


@dataclass
class WorkPackageState:
    project_id: str
    wp_id: str
    title: str
    status: str = "pending"
    claimed_by: str = ""
    claimed_at: str = ""
    updated_at: str = ""
    payload: dict[str, Any] | None = None


@dataclass
class CoordinationEvent:
    project_id: str
    event_type: str
    actor: str
    slot: str = ""
    occurred_at: str = ""
    logical_counter: int = 0
    content_hash: str = ""
    parent_hash: str = ""
    payload: dict[str, Any] | None = None
    entity_type: str = ""
    entity_id: str = ""
    operation: str = ""
    actor_role: str = ""
    model_family: str = ""
    session_ref: str = ""
    request_id: str = ""
    gate_record_ref: str = ""
    before_hash: str = ""
    after_hash: str = ""
    evidence: dict[str, Any] | None = None
    status: str = "recorded"


def _configure_stream_errors(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


_configure_stream_errors(sys.stdout)
_configure_stream_errors(sys.stderr)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime | None:
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def dumps_payload(payload: dict[str, Any] | None) -> str:
    return json.dumps(payload or {}, sort_keys=True, ensure_ascii=False)


def loads_payload(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    try:
        payload = json.loads(value)
    except json.JSONDecodeError:
        return {"_unparseable_payload": value}
    return payload if isinstance(payload, dict) else {"value": payload}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), default=str)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_hash(value: Any) -> str:
    return sha256_text(canonical_json(value))


def assert_no_secret_payload(payload: Any, context: str = "payload") -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            key_text = str(key).casefold()
            if key_text not in ALLOWED_SECRETISH_KEYS and any(marker in key_text for marker in SECRET_KEY_MARKERS):
                if value not in (None, "", [], {}):
                    raise CoordinationDbError(f"{context}: secret-looking field '{key}' is not allowed in coordination DB payloads")
            assert_no_secret_payload(value, f"{context}.{key}")
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            assert_no_secret_payload(item, f"{context}[{index}]")


def latest_event_ref(conn: sqlite3.Connection, project_id: str) -> tuple[int | None, str]:
    row = conn.execute(
        "SELECT event_id, event_hash, content_hash FROM event_log WHERE project_id = ? ORDER BY event_id DESC LIMIT 1",
        (project_id,),
    ).fetchone()
    if row is None:
        return None, ""
    return int(row["event_id"]), str(row["event_hash"] or row["content_hash"] or "")


@contextmanager
def coordination_db(db_path: str | Path = DEFAULT_DB_PATH):
    conn = connect(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def write_transaction(conn: sqlite3.Connection):
    own_transaction = not conn.in_transaction
    if own_transaction:
        conn.execute("BEGIN IMMEDIATE")
    try:
        yield
        if own_transaction:
            conn.commit()
    except Exception:
        if own_transaction:
            conn.rollback()
        raise


def connect(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    last_error: sqlite3.OperationalError | None = None
    for attempt in range(50):
        conn = sqlite3.connect(path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA busy_timeout=30000")
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            init_schema(conn)
            return conn
        except sqlite3.OperationalError as exc:
            conn.close()
            if "locked" not in str(exc).casefold() and "busy" not in str(exc).casefold():
                raise
            last_error = exc
            time.sleep(0.02 * (attempt + 1))
    raise last_error or sqlite3.OperationalError("database is locked")


def init_schema(conn: sqlite3.Connection) -> None:
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS project_state (
              project_id TEXT PRIMARY KEY,
              board_path TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL DEFAULT 'active',
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              payload_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS roster (
              project_id TEXT NOT NULL,
              slot TEXT NOT NULL,
              chosen_name TEXT NOT NULL DEFAULT '',
              role TEXT NOT NULL DEFAULT '',
              current_task TEXT NOT NULL DEFAULT '',
              blocked_on TEXT NOT NULL DEFAULT '',
              last_handoff TEXT NOT NULL DEFAULT '',
              updated_at TEXT NOT NULL DEFAULT '',
              revision INTEGER NOT NULL DEFAULT 0,
              last_writer TEXT NOT NULL DEFAULT '',
              current_hash TEXT NOT NULL DEFAULT '',
              last_event_id INTEGER,
              last_event_hash TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL DEFAULT '{}',
              PRIMARY KEY (project_id, slot)
            );

            CREATE TABLE IF NOT EXISTS edit_locks (
              project_id TEXT NOT NULL,
              lock_name TEXT NOT NULL,
              target TEXT NOT NULL,
              holder TEXT NOT NULL,
              claimed_at TEXT NOT NULL,
              expires_at TEXT NOT NULL,
              note TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL DEFAULT 'active',
              current_hash TEXT NOT NULL DEFAULT '',
              last_event_id INTEGER,
              last_event_hash TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL DEFAULT '{}',
              PRIMARY KEY (project_id, lock_name)
            );

            CREATE TABLE IF NOT EXISTS heartbeats (
              project_id TEXT NOT NULL,
              slot TEXT NOT NULL,
              instance_name TEXT NOT NULL,
              observed_at TEXT NOT NULL,
              current_task TEXT NOT NULL DEFAULT '',
              last_action_type TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL DEFAULT 'active',
              monotonic_counter INTEGER NOT NULL DEFAULT 0,
              current_hash TEXT NOT NULL DEFAULT '',
              last_event_id INTEGER,
              last_event_hash TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL DEFAULT '{}',
              PRIMARY KEY (project_id, slot)
            );

            CREATE TABLE IF NOT EXISTS heartbeat_events (
              event_id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id TEXT NOT NULL,
              slot TEXT NOT NULL,
              instance_name TEXT NOT NULL,
              observed_at TEXT NOT NULL,
              current_task TEXT NOT NULL DEFAULT '',
              last_action_type TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL DEFAULT 'active',
              monotonic_counter INTEGER NOT NULL DEFAULT 0,
              payload_hash TEXT NOT NULL DEFAULT '',
              event_hash TEXT NOT NULL DEFAULT '',
              parent_event_hash TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS work_packages (
              project_id TEXT NOT NULL,
              wp_id TEXT NOT NULL,
              title TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'pending',
              claimed_by TEXT NOT NULL DEFAULT '',
              claimed_at TEXT NOT NULL DEFAULT '',
              updated_at TEXT NOT NULL DEFAULT '',
              current_hash TEXT NOT NULL DEFAULT '',
              last_event_id INTEGER,
              last_event_hash TEXT NOT NULL DEFAULT '',
              payload_json TEXT NOT NULL DEFAULT '{}',
              PRIMARY KEY (project_id, wp_id)
            );

            CREATE TABLE IF NOT EXISTS event_log (
              event_id INTEGER PRIMARY KEY AUTOINCREMENT,
              project_id TEXT NOT NULL,
              event_type TEXT NOT NULL,
              actor TEXT NOT NULL,
              slot TEXT NOT NULL DEFAULT '',
              occurred_at TEXT NOT NULL,
              logical_counter INTEGER NOT NULL DEFAULT 0,
              content_hash TEXT NOT NULL DEFAULT '',
              parent_hash TEXT NOT NULL DEFAULT '',
              entity_type TEXT NOT NULL DEFAULT '',
              entity_id TEXT NOT NULL DEFAULT '',
              operation TEXT NOT NULL DEFAULT '',
              actor_slot TEXT NOT NULL DEFAULT '',
              actor_role TEXT NOT NULL DEFAULT '',
              model_family TEXT NOT NULL DEFAULT '',
              session_ref TEXT NOT NULL DEFAULT '',
              actor_counter INTEGER,
              parent_event_id INTEGER,
              parent_event_hash TEXT NOT NULL DEFAULT '',
              request_id TEXT NOT NULL DEFAULT '',
              gate_record_ref TEXT NOT NULL DEFAULT '',
              before_hash TEXT NOT NULL DEFAULT '',
              after_hash TEXT NOT NULL DEFAULT '',
              payload_hash TEXT NOT NULL DEFAULT '',
              event_hash TEXT NOT NULL DEFAULT '',
              evidence_json TEXT NOT NULL DEFAULT '{}',
              status TEXT NOT NULL DEFAULT 'recorded',
              payload_json TEXT NOT NULL DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_roster_project_updated
              ON roster(project_id, updated_at);
            CREATE INDEX IF NOT EXISTS idx_heartbeats_project_observed
              ON heartbeats(project_id, observed_at);
            CREATE INDEX IF NOT EXISTS idx_heartbeat_events_slot
              ON heartbeat_events(project_id, slot, observed_at);
            CREATE INDEX IF NOT EXISTS idx_event_log_project_hash
              ON event_log(project_id, content_hash);
            """
        )
        conn.execute(
            "INSERT OR REPLACE INTO schema_meta(key, value) VALUES('schema_version', ?)",
            (str(SCHEMA_VERSION),),
        )
        migrate_schema(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def migrate_schema(conn: sqlite3.Connection) -> None:
    table_columns = {
        "roster": {
            "current_hash": "TEXT NOT NULL DEFAULT ''",
            "last_event_id": "INTEGER",
            "last_event_hash": "TEXT NOT NULL DEFAULT ''",
        },
        "edit_locks": {
            "current_hash": "TEXT NOT NULL DEFAULT ''",
            "last_event_id": "INTEGER",
            "last_event_hash": "TEXT NOT NULL DEFAULT ''",
        },
        "heartbeats": {
            "current_hash": "TEXT NOT NULL DEFAULT ''",
            "last_event_id": "INTEGER",
            "last_event_hash": "TEXT NOT NULL DEFAULT ''",
        },
        "heartbeat_events": {
            "payload_hash": "TEXT NOT NULL DEFAULT ''",
            "event_hash": "TEXT NOT NULL DEFAULT ''",
            "parent_event_hash": "TEXT NOT NULL DEFAULT ''",
        },
        "work_packages": {
            "current_hash": "TEXT NOT NULL DEFAULT ''",
            "last_event_id": "INTEGER",
            "last_event_hash": "TEXT NOT NULL DEFAULT ''",
        },
        "event_log": {
            "entity_type": "TEXT NOT NULL DEFAULT ''",
            "entity_id": "TEXT NOT NULL DEFAULT ''",
            "operation": "TEXT NOT NULL DEFAULT ''",
            "actor_slot": "TEXT NOT NULL DEFAULT ''",
            "actor_role": "TEXT NOT NULL DEFAULT ''",
            "model_family": "TEXT NOT NULL DEFAULT ''",
            "session_ref": "TEXT NOT NULL DEFAULT ''",
            "actor_counter": "INTEGER",
            "parent_event_id": "INTEGER",
            "parent_event_hash": "TEXT NOT NULL DEFAULT ''",
            "request_id": "TEXT NOT NULL DEFAULT ''",
            "gate_record_ref": "TEXT NOT NULL DEFAULT ''",
            "before_hash": "TEXT NOT NULL DEFAULT ''",
            "after_hash": "TEXT NOT NULL DEFAULT ''",
            "payload_hash": "TEXT NOT NULL DEFAULT ''",
            "event_hash": "TEXT NOT NULL DEFAULT ''",
            "evidence_json": "TEXT NOT NULL DEFAULT '{}'",
            "status": "TEXT NOT NULL DEFAULT 'recorded'",
        },
    }
    for table, columns in table_columns.items():
        existing = {
            str(row["name"])
            for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
        }
        for column, ddl in columns.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def audit_state_event(
    conn: sqlite3.Connection,
    *,
    project_id: str,
    entity_type: str,
    entity_id: str,
    operation: str,
    actor: str,
    after_state: dict[str, Any],
    before_hash: str = "",
    slot: str = "",
    occurred_at: str | None = None,
    actor_counter: int | None = None,
    payload: dict[str, Any] | None = None,
    evidence: dict[str, Any] | None = None,
    status: str = "recorded",
) -> tuple[int, str, str]:
    event_payload = payload or after_state
    assert_no_secret_payload(event_payload, f"{entity_type}.{entity_id}.payload")
    assert_no_secret_payload(evidence or {}, f"{entity_type}.{entity_id}.evidence")
    occurred = occurred_at or now_iso()
    parent_event_id, parent_event_hash = latest_event_ref(conn, project_id)
    after_hash = stable_hash(after_state)
    payload_hash = stable_hash(event_payload)
    seed = {
        "project_id": project_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "operation": operation,
        "actor": actor,
        "slot": slot,
        "occurred_at": occurred,
        "actor_counter": actor_counter,
        "parent_event_id": parent_event_id,
        "parent_event_hash": parent_event_hash,
        "before_hash": before_hash,
        "after_hash": after_hash,
        "payload_hash": payload_hash,
        "evidence": evidence or {},
        "status": status,
    }
    event_hash = stable_hash(seed)
    cursor = conn.execute(
        """
        INSERT INTO event_log(
          project_id, event_type, actor, slot, occurred_at, logical_counter,
          content_hash, parent_hash, entity_type, entity_id, operation, actor_slot,
          actor_counter, parent_event_id, parent_event_hash, before_hash, after_hash,
          payload_hash, event_hash, evidence_json, status, payload_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            operation,
            actor,
            slot,
            occurred,
            actor_counter or 0,
            event_hash,
            parent_event_hash,
            entity_type,
            entity_id,
            operation,
            slot,
            actor_counter,
            parent_event_id,
            parent_event_hash,
            before_hash,
            after_hash,
            payload_hash,
            event_hash,
            dumps_payload(evidence),
            status,
            dumps_payload(event_payload),
        ),
    )
    return int(cursor.lastrowid), event_hash, after_hash


def ensure_project(
    conn: sqlite3.Connection,
    project_id: str = DEFAULT_PROJECT_ID,
    board_path: str = "",
    status: str = "active",
    payload: dict[str, Any] | None = None,
    updated_at: str | None = None,
) -> None:
    ts = updated_at or now_iso()
    conn.execute(
        """
        INSERT INTO project_state(project_id, board_path, status, created_at, updated_at, payload_json)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id) DO UPDATE SET
          board_path=excluded.board_path,
          status=excluded.status,
          updated_at=excluded.updated_at,
          payload_json=excluded.payload_json
        """,
        (project_id, board_path, status, ts, ts, dumps_payload(payload)),
    )


def upsert_roster(conn: sqlite3.Connection, state: RosterState) -> None:
    if not conn.in_transaction:
        with write_transaction(conn):
            upsert_roster(conn, state)
        return
    existing = conn.execute(
        "SELECT revision, current_hash FROM roster WHERE project_id = ? AND slot = ?",
        (state.project_id, state.slot),
    ).fetchone()
    if existing and state.expected_revision is not None and int(existing["revision"]) != state.expected_revision:
        raise CoordinationDbError(
            f"roster.{state.slot}: expected revision {state.expected_revision}, found {existing['revision']}"
        )
    revision = int(existing["revision"]) + 1 if existing else max(state.revision, 1)
    after_state = {
        "project_id": state.project_id,
        "slot": state.slot,
        "chosen_name": state.chosen_name,
        "role": state.role,
        "current_task": state.current_task,
        "blocked_on": state.blocked_on,
        "last_handoff": state.last_handoff,
        "updated_at": state.updated_at or now_iso(),
        "revision": revision,
        "last_writer": state.last_writer,
        "payload": state.payload or {},
    }
    event_id, event_hash, current_hash = audit_state_event(
        conn,
        project_id=state.project_id,
        entity_type="roster",
        entity_id=state.slot,
        operation="upsert_roster",
        actor=state.last_writer or "unknown",
        after_state=after_state,
        before_hash=str(existing["current_hash"] or "") if existing else "",
        slot=state.slot,
        occurred_at=after_state["updated_at"],
        payload=state.payload or after_state,
    )
    conn.execute(
        """
        INSERT INTO roster(
          project_id, slot, chosen_name, role, current_task, blocked_on, last_handoff,
          updated_at, revision, last_writer, current_hash, last_event_id, last_event_hash,
          payload_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id, slot) DO UPDATE SET
          chosen_name=excluded.chosen_name,
          role=excluded.role,
          current_task=excluded.current_task,
          blocked_on=excluded.blocked_on,
          last_handoff=excluded.last_handoff,
          updated_at=excluded.updated_at,
          revision=excluded.revision,
          last_writer=excluded.last_writer,
          current_hash=excluded.current_hash,
          last_event_id=excluded.last_event_id,
          last_event_hash=excluded.last_event_hash,
          payload_json=excluded.payload_json
        """,
        (
            state.project_id,
            state.slot,
            state.chosen_name,
            state.role,
            state.current_task,
            state.blocked_on,
            state.last_handoff,
            after_state["updated_at"],
            revision,
            state.last_writer,
            current_hash,
            event_id,
            event_hash,
            dumps_payload(state.payload),
        ),
    )


def upsert_edit_lock(conn: sqlite3.Connection, state: EditLockState) -> None:
    if not conn.in_transaction:
        with write_transaction(conn):
            upsert_edit_lock(conn, state)
        return
    if state.status == "active" and parse_time(state.expires_at) is None:
        raise CoordinationDbError(f"edit_lock.{state.lock_name}: active locks require parseable expires_at")
    existing = conn.execute(
        "SELECT current_hash FROM edit_locks WHERE project_id = ? AND lock_name = ?",
        (state.project_id, state.lock_name),
    ).fetchone()
    after_state = {
        "project_id": state.project_id,
        "lock_name": state.lock_name,
        "target": state.target,
        "holder": state.holder,
        "claimed_at": state.claimed_at,
        "expires_at": state.expires_at,
        "note": state.note,
        "status": state.status,
        "payload": state.payload or {},
    }
    event_id, event_hash, current_hash = audit_state_event(
        conn,
        project_id=state.project_id,
        entity_type="edit_lock",
        entity_id=state.lock_name,
        operation="upsert_edit_lock",
        actor=state.holder,
        after_state=after_state,
        before_hash=str(existing["current_hash"] or "") if existing else "",
        payload=state.payload or after_state,
        status=state.status,
    )
    conn.execute(
        """
        INSERT INTO edit_locks(
          project_id, lock_name, target, holder, claimed_at, expires_at, note, status,
          current_hash, last_event_id, last_event_hash, payload_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id, lock_name) DO UPDATE SET
          target=excluded.target,
          holder=excluded.holder,
          claimed_at=excluded.claimed_at,
          expires_at=excluded.expires_at,
          note=excluded.note,
          status=excluded.status,
          current_hash=excluded.current_hash,
          last_event_id=excluded.last_event_id,
          last_event_hash=excluded.last_event_hash,
          payload_json=excluded.payload_json
        """,
        (
            state.project_id,
            state.lock_name,
            state.target,
            state.holder,
            state.claimed_at,
            state.expires_at,
            state.note,
            state.status,
            current_hash,
            event_id,
            event_hash,
            dumps_payload(state.payload),
        ),
    )


def release_edit_lock(conn: sqlite3.Connection, project_id: str, lock_name: str, released_at: str | None = None) -> None:
    if not conn.in_transaction:
        with write_transaction(conn):
            release_edit_lock(conn, project_id, lock_name, released_at)
        return
    existing = conn.execute(
        "SELECT * FROM edit_locks WHERE project_id = ? AND lock_name = ?",
        (project_id, lock_name),
    ).fetchone()
    if existing:
        after_state = dict(existing)
        after_state["status"] = "released"
        after_state["released_at"] = released_at or now_iso()
        event_id, event_hash, current_hash = audit_state_event(
            conn,
            project_id=project_id,
            entity_type="edit_lock",
            entity_id=lock_name,
            operation="release_edit_lock",
            actor=str(existing["holder"] or "unknown"),
            after_state=after_state,
            before_hash=str(existing["current_hash"] or ""),
            status="released",
        )
    else:
        event_id = None
        event_hash = ""
        current_hash = ""
    conn.execute(
        """
        UPDATE edit_locks
        SET status = 'released',
            current_hash = ?,
            last_event_id = ?,
            last_event_hash = ?,
            payload_json = json_set(COALESCE(NULLIF(payload_json, ''), '{}'), '$.released_at', ?)
        WHERE project_id = ? AND lock_name = ?
        """,
        (current_hash, event_id, event_hash, released_at or now_iso(), project_id, lock_name),
    )


def upsert_work_package(conn: sqlite3.Connection, state: WorkPackageState) -> None:
    if not conn.in_transaction:
        with write_transaction(conn):
            upsert_work_package(conn, state)
        return
    existing = conn.execute(
        "SELECT current_hash FROM work_packages WHERE project_id = ? AND wp_id = ?",
        (state.project_id, state.wp_id),
    ).fetchone()
    after_state = {
        "project_id": state.project_id,
        "wp_id": state.wp_id,
        "title": state.title,
        "status": state.status,
        "claimed_by": state.claimed_by,
        "claimed_at": state.claimed_at,
        "updated_at": state.updated_at or now_iso(),
        "payload": state.payload or {},
    }
    event_id, event_hash, current_hash = audit_state_event(
        conn,
        project_id=state.project_id,
        entity_type="work_package",
        entity_id=state.wp_id,
        operation="upsert_work_package",
        actor=state.claimed_by or "unknown",
        after_state=after_state,
        before_hash=str(existing["current_hash"] or "") if existing else "",
        occurred_at=after_state["updated_at"],
        payload=state.payload or after_state,
        status=state.status,
    )
    conn.execute(
        """
        INSERT INTO work_packages(
          project_id, wp_id, title, status, claimed_by, claimed_at, updated_at,
          current_hash, last_event_id, last_event_hash, payload_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id, wp_id) DO UPDATE SET
          title=excluded.title,
          status=excluded.status,
          claimed_by=excluded.claimed_by,
          claimed_at=excluded.claimed_at,
          updated_at=excluded.updated_at,
          current_hash=excluded.current_hash,
          last_event_id=excluded.last_event_id,
          last_event_hash=excluded.last_event_hash,
          payload_json=excluded.payload_json
        """,
        (
            state.project_id,
            state.wp_id,
            state.title,
            state.status,
            state.claimed_by,
            state.claimed_at,
            after_state["updated_at"],
            current_hash,
            event_id,
            event_hash,
            dumps_payload(state.payload),
        ),
    )


def record_heartbeat(
    conn: sqlite3.Connection,
    project_id: str,
    slot: str,
    instance_name: str,
    observed_at: str | None = None,
    current_task: str = "",
    last_action_type: str = "",
    status: str = "active",
    monotonic_counter: int = 0,
    payload: dict[str, Any] | None = None,
) -> None:
    if not conn.in_transaction:
        with write_transaction(conn):
            record_heartbeat(
                conn,
                project_id,
                slot,
                instance_name,
                observed_at=observed_at,
                current_task=current_task,
                last_action_type=last_action_type,
                status=status,
                monotonic_counter=monotonic_counter,
                payload=payload,
            )
        return
    ts = observed_at or now_iso()
    assert_no_secret_payload(payload or {}, f"heartbeat.{slot}.payload")
    payload_json = dumps_payload(payload)
    existing = conn.execute(
        "SELECT current_hash FROM heartbeats WHERE project_id = ? AND slot = ?",
        (project_id, slot),
    ).fetchone()
    after_state = {
        "project_id": project_id,
        "slot": slot,
        "instance_name": instance_name,
        "observed_at": ts,
        "current_task": current_task,
        "last_action_type": last_action_type,
        "status": status,
        "monotonic_counter": monotonic_counter,
        "payload": payload or {},
    }
    event_id, event_hash, current_hash = audit_state_event(
        conn,
        project_id=project_id,
        entity_type="heartbeat",
        entity_id=slot,
        operation="record_heartbeat",
        actor=instance_name or slot,
        after_state=after_state,
        before_hash=str(existing["current_hash"] or "") if existing else "",
        slot=slot,
        occurred_at=ts,
        actor_counter=monotonic_counter,
        payload=payload or after_state,
        evidence={"heartbeat_payload_hash": stable_hash(payload or {})},
        status=status,
    )
    conn.execute(
        """
        INSERT INTO heartbeats(
          project_id, slot, instance_name, observed_at, current_task, last_action_type,
          status, monotonic_counter, current_hash, last_event_id, last_event_hash, payload_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(project_id, slot) DO UPDATE SET
          instance_name=excluded.instance_name,
          observed_at=excluded.observed_at,
          current_task=excluded.current_task,
          last_action_type=excluded.last_action_type,
          status=excluded.status,
          monotonic_counter=excluded.monotonic_counter,
          current_hash=excluded.current_hash,
          last_event_id=excluded.last_event_id,
          last_event_hash=excluded.last_event_hash,
          payload_json=excluded.payload_json
        """,
        (
            project_id,
            slot,
            instance_name,
            ts,
            current_task,
            last_action_type,
            status,
            monotonic_counter,
            current_hash,
            event_id,
            event_hash,
            payload_json,
        ),
    )
    conn.execute(
        """
        INSERT INTO heartbeat_events(
          project_id, slot, instance_name, observed_at, current_task, last_action_type,
          status, monotonic_counter, payload_hash, event_hash, parent_event_hash, payload_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            slot,
            instance_name,
            ts,
            current_task,
            last_action_type,
            status,
            monotonic_counter,
            stable_hash(payload or after_state),
            event_hash,
            "",
            payload_json,
        ),
    )


def record_event(conn: sqlite3.Connection, event: CoordinationEvent) -> int:
    if not conn.in_transaction:
        with write_transaction(conn):
            return record_event(conn, event)
    occurred = event.occurred_at or now_iso()
    assert_no_secret_payload(event.payload or {}, f"event.{event.event_type}.payload")
    parent_event_id, parent_event_hash = latest_event_ref(conn, event.project_id)
    payload_hash = stable_hash(event.payload or {})
    seed = {
        "project_id": event.project_id,
        "event_type": event.event_type,
        "actor": event.actor,
        "slot": event.slot,
        "occurred_at": occurred,
        "logical_counter": event.logical_counter,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "operation": event.operation or event.event_type,
        "parent_event_id": parent_event_id,
        "parent_event_hash": parent_event_hash,
        "payload_hash": payload_hash,
        "before_hash": event.before_hash,
        "after_hash": event.after_hash,
        "evidence": event.evidence or {},
        "status": event.status,
    }
    event_hash = event.content_hash or stable_hash(seed)
    cursor = conn.execute(
        """
        INSERT INTO event_log(
          project_id, event_type, actor, slot, occurred_at, logical_counter,
          content_hash, parent_hash, entity_type, entity_id, operation, actor_slot, actor_role,
          model_family, session_ref, actor_counter, parent_event_id, parent_event_hash,
          request_id, gate_record_ref, before_hash, after_hash, payload_hash, event_hash,
          evidence_json, status, payload_json
        )
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.project_id,
            event.event_type,
            event.actor,
            event.slot,
            occurred,
            event.logical_counter,
            event_hash,
            event.parent_hash or parent_event_hash,
            event.entity_type,
            event.entity_id,
            event.operation or event.event_type,
            event.slot,
            event.actor_role,
            event.model_family,
            event.session_ref,
            event.logical_counter,
            parent_event_id,
            parent_event_hash,
            event.request_id,
            event.gate_record_ref,
            event.before_hash,
            event.after_hash,
            payload_hash,
            event_hash,
            dumps_payload(event.evidence),
            event.status,
            dumps_payload(event.payload),
        ),
    )
    return int(cursor.lastrowid)


def seed_from_board(
    db_path: str | Path,
    board_path: str | Path,
    project_id: str = DEFAULT_PROJECT_ID,
    writer: str = "board-seed",
) -> dict[str, int]:
    board = wave1_board.parse_board(board_path)
    with coordination_db(db_path) as conn:
        ensure_project(conn, project_id, board_path=str(board_path), payload={"frontmatter": board.frontmatter})
        for row in board.roster:
            upsert_roster(
                conn,
                RosterState(
                    project_id=project_id,
                    slot=row.slot,
                    chosen_name=row.chosen_name,
                    role=row.role,
                    current_task=row.current_task,
                    blocked_on=row.blocked_on,
                    last_handoff=row.last_handoff,
                    updated_at=row.updated,
                    last_writer=writer,
                ),
            )
        for lock in board.edit_locks:
            claimed_at = lock.claimed_at or now_iso()
            claimed_dt = parse_time(claimed_at) or datetime.now(timezone.utc)
            upsert_edit_lock(
                conn,
                EditLockState(
                    project_id=project_id,
                    lock_name=lock.name,
                    target=lock.file_or_address,
                    holder=lock.name,
                    claimed_at=claimed_at,
                    expires_at=format_iso(claimed_dt + timedelta(seconds=DEFAULT_LOCK_TTL_SECONDS)),
                    note=lock.note,
                    status="active",
                    payload={"source": "board_seed", "seed_writer": writer},
                ),
            )
        record_event(
            conn,
            CoordinationEvent(
                project_id=project_id,
                event_type="seed_from_board",
                actor=writer,
                occurred_at=now_iso(),
                payload={"board_path": str(board_path), "roster_rows": len(board.roster)},
            ),
        )
    return {"roster_rows": len(board.roster), "edit_locks": len(board.edit_locks)}


def rows_as_dicts(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]


def expire_stale_locks(conn: sqlite3.Connection, project_id: str, now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    expired = 0
    rows = conn.execute(
        "SELECT * FROM edit_locks WHERE project_id = ? AND status = 'active' AND expires_at != ''",
        (project_id,),
    ).fetchall()
    for row in rows:
        expires = parse_time(str(row["expires_at"]))
        if expires is None or expires >= now:
            continue
        after_state = dict(row)
        after_state["status"] = "expired"
        after_state["expired_at"] = format_iso(now)
        event_id, event_hash, current_hash = audit_state_event(
            conn,
            project_id=project_id,
            entity_type="edit_lock",
            entity_id=str(row["lock_name"]),
            operation="expire_edit_lock",
            actor="coorddb-expiry",
            after_state=after_state,
            before_hash=str(row["current_hash"] or ""),
            status="expired",
        )
        conn.execute(
            """
            UPDATE edit_locks
            SET status = 'expired',
                current_hash = ?,
                last_event_id = ?,
                last_event_hash = ?,
                payload_json = json_set(COALESCE(NULLIF(payload_json, ''), '{}'), '$.expired_at', ?)
            WHERE project_id = ? AND lock_name = ?
            """,
            (current_hash, event_id, event_hash, format_iso(now), project_id, row["lock_name"]),
        )
        expired += 1
    return expired


def get_project_snapshot(conn: sqlite3.Connection, project_id: str = DEFAULT_PROJECT_ID) -> dict[str, Any]:
    expire_stale_locks(conn, project_id)
    project = conn.execute("SELECT * FROM project_state WHERE project_id = ?", (project_id,)).fetchone()
    return {
        "project": dict(project) if project else {},
        "roster": rows_as_dicts(
            conn.execute("SELECT * FROM roster WHERE project_id = ? ORDER BY slot", (project_id,))
        ),
        "edit_locks": rows_as_dicts(
            conn.execute(
                "SELECT * FROM edit_locks WHERE project_id = ? AND status = 'active' ORDER BY lock_name",
                (project_id,),
            )
        ),
        "heartbeats": rows_as_dicts(
            conn.execute("SELECT * FROM heartbeats WHERE project_id = ? ORDER BY slot", (project_id,))
        ),
        "work_packages": rows_as_dicts(
            conn.execute("SELECT * FROM work_packages WHERE project_id = ? ORDER BY wp_id", (project_id,))
        ),
        "recent_events": rows_as_dicts(
            conn.execute(
                "SELECT * FROM event_log WHERE project_id = ? ORDER BY event_id",
                (project_id,),
            )
        ),
    }


def md_escape_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\n", " ")
    text = text.replace("|", "\\|")
    return text.strip() or "-"


def render_table(headers: list[str], rows: list[dict[str, Any]], keys: list[str]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    if not rows:
        lines.append("| " + " | ".join("-" for _ in headers) + " |")
        return lines
    for row in rows:
        lines.append("| " + " | ".join(md_escape_cell(row.get(key, "")) for key in keys) + " |")
    return lines


def render_snapshot_markdown(snapshot: dict[str, Any], db_path: str | Path, project_id: str) -> str:
    generated = now_iso()
    snapshot_state_hash = stable_hash(snapshot)
    lines = [
        "---",
        'object_type: "coordination_db_snapshot"',
        f'project_id: "{project_id}"',
        f'generated: "{generated}"',
        f'snapshot_state_hash: "{snapshot_state_hash}"',
        'visibility: "public"',
        "---",
        "",
        f"# Wave 2.5 Coordination DB Snapshot — {project_id}",
        "",
        f"Source DB: `{Path(db_path)}`",
        f"Snapshot state hash: `{snapshot_state_hash}`",
        "",
        "This is a durable markdown projection of temp SQLite hot coordination state. The",
        "SQLite file remains runtime state and is cleaned at project end.",
        "",
        "## Roster",
        "",
        *render_table(
            ["Slot", "Chosen Name", "Role", "Current Task", "Blocked-On", "Updated", "Revision"],
            snapshot["roster"],
            ["slot", "chosen_name", "role", "current_task", "blocked_on", "updated_at", "revision"],
        ),
        "",
        "## Active Edit Locks",
        "",
        *render_table(
            ["Name", "Target", "Holder", "Claimed", "Expires", "Note"],
            snapshot["edit_locks"],
            ["lock_name", "target", "holder", "claimed_at", "expires_at", "note"],
        ),
        "",
        "## Heartbeats",
        "",
        *render_table(
            ["Slot", "Instance", "Observed", "Task", "Last Action", "Status", "Counter"],
            snapshot["heartbeats"],
            ["slot", "instance_name", "observed_at", "current_task", "last_action_type", "status", "monotonic_counter"],
        ),
        "",
        "## Work Packages",
        "",
        *render_table(
            ["WP", "Title", "Status", "Claimed By", "Claimed At", "Updated"],
            snapshot["work_packages"],
            ["wp_id", "title", "status", "claimed_by", "claimed_at", "updated_at"],
        ),
        "",
        "## Recent Events",
        "",
        *render_table(
            ["ID", "Type", "Actor", "Slot", "Occurred", "Clock", "Hash", "Parent"],
            list(reversed(snapshot["recent_events"])),
            ["event_id", "event_type", "actor", "slot", "occurred_at", "logical_counter", "content_hash", "parent_hash"],
        ),
        "",
        "## Cleanup Protocol",
        "",
        "- Runtime DB files are temp state and remain ignored by `.gitignore` (`*.sqlite3`).",
        "- Before project close, run `python wave25_coorddb.py snapshot --output <path>` and keep the markdown projection.",
        "- After snapshot verification, run `python wave25_coorddb.py cleanup --execute` to remove the temp DB and SQLite WAL/SHM sidecars.",
        "",
    ]
    return "\n".join(lines)


def snapshot_to_markdown(
    db_path: str | Path = DEFAULT_DB_PATH,
    output_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    project_id: str = DEFAULT_PROJECT_ID,
) -> Path:
    with coordination_db(db_path) as conn:
        snapshot = get_project_snapshot(conn, project_id)
    output = Path(output_path)
    wave1_board_writer.atomic_write_text(output, render_snapshot_markdown(snapshot, db_path, project_id))
    return output


def cleanup_runtime_db(db_path: str | Path = DEFAULT_DB_PATH, execute: bool = False) -> dict[str, Any]:
    return cleanup_runtime_db_after_snapshot(db_path, snapshot_path=None, execute=execute)


def cleanup_runtime_db_after_snapshot(
    db_path: str | Path = DEFAULT_DB_PATH,
    snapshot_path: str | Path | None = DEFAULT_SNAPSHOT_PATH,
    execute: bool = False,
) -> dict[str, Any]:
    path = Path(db_path)
    targets = [path, path.with_name(f"{path.name}-wal"), path.with_name(f"{path.name}-shm")]
    existing = [target for target in targets if target.exists()]
    if not execute:
        return {"execute": False, "would_remove": [str(target) for target in existing], "removed": []}
    if snapshot_path is not None and not Path(snapshot_path).exists():
        raise CoordinationDbError(f"refusing cleanup before durable snapshot exists: {snapshot_path}")
    removed: list[str] = []
    for target in existing:
        target.unlink()
        removed.append(str(target))
    return {"execute": True, "would_remove": [], "removed": removed}


def format_status(db_path: str | Path = DEFAULT_DB_PATH, project_id: str = DEFAULT_PROJECT_ID) -> str:
    with coordination_db(db_path) as conn:
        snapshot = get_project_snapshot(conn, project_id)
    lines = [
        "Wave 2.5 Coordination DB",
        f"DB: {Path(db_path)}",
        f"Project: {project_id}",
        f"Roster rows: {len(snapshot['roster'])}",
        f"Active locks: {len(snapshot['edit_locks'])}",
        f"Heartbeats: {len(snapshot['heartbeats'])}",
        f"Work packages: {len(snapshot['work_packages'])}",
        f"Recent events: {len(snapshot['recent_events'])}",
    ]
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave 2.5 per-project SQLite coordination DB.")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Create or migrate the coordination DB schema.")

    seed = sub.add_parser("seed-board", help="Seed roster/edit-lock hot state from a markdown board.")
    seed.add_argument("--board", required=True)
    seed.add_argument("--writer", default="board-seed")

    snapshot = sub.add_parser("snapshot", help="Write a markdown projection of DB hot state.")
    snapshot.add_argument("--output", default=str(DEFAULT_SNAPSHOT_PATH))

    cleanup = sub.add_parser("cleanup", help="Remove temp SQLite runtime files after snapshot verification.")
    cleanup.add_argument("--execute", action="store_true")
    cleanup.add_argument("--snapshot", default=str(DEFAULT_SNAPSHOT_PATH))

    sub.add_parser("status", help="Show DB summary.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "init":
        with coordination_db(args.db) as conn:
            ensure_project(conn, args.project_id)
        result: dict[str, Any] = {"db": args.db, "project_id": args.project_id, "schema_version": SCHEMA_VERSION}
    elif args.command == "seed-board":
        result = seed_from_board(args.db, args.board, args.project_id, args.writer)
        result.update({"db": args.db, "project_id": args.project_id})
    elif args.command == "snapshot":
        path = snapshot_to_markdown(args.db, args.output, args.project_id)
        result = {"snapshot": str(path), "db": args.db, "project_id": args.project_id}
    elif args.command == "cleanup":
        result = cleanup_runtime_db_after_snapshot(args.db, snapshot_path=args.snapshot, execute=args.execute)
    else:
        if args.format == "json":
            with coordination_db(args.db) as conn:
                result = get_project_snapshot(conn, args.project_id)
        else:
            print(format_status(args.db, args.project_id))
            return 0

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
