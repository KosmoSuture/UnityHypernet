#!/usr/bin/env python3
"""Tests for Wave 2.5 atomic coordination DB tooling."""

from __future__ import annotations

import sqlite3
import gc
import shutil
import tempfile
import threading
import time
from pathlib import Path

import wave25_coorddb


def cleanup_runtime_dir(tmpdir: str, db_path: Path) -> None:
    for attempt in range(100):
        try:
            if db_path.exists():
                conn = sqlite3.connect(db_path, timeout=30)
                try:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    conn.execute("PRAGMA journal_mode=DELETE")
                finally:
                    conn.close()
            wave25_coorddb.cleanup_runtime_db(db_path, execute=True)
            shutil.rmtree(tmpdir)
            return
        except (PermissionError, OSError):
            if attempt == 99:
                raise
            gc.collect()
            time.sleep(0.1)


def board_fixture() -> str:
    return """---
ha: "2.7.13.W2.5"
object_type: "coordination_board"
---

# 2.7.13.W2.5 - Fixture

## BOARD STATUS - READ THIS FIRST

> **CURRENT PHASE:** fixture.
> **WHAT'S HAPPENING NOW:** testing.
> **NEXT ACTION (Truss):** build H2.
> **HUMAN GATE:** none.

## Instance Roster

| Slot | Chosen Name | Role | Current Task | Blocked-On | Last Handoff | Updated |
|---|---|---|---|---|---|---|
| Codex-A | **Truss** | Collaboration Substrate Engineer | Building H2 | - | fixture | 2026-05-31T06:00:00Z |
| Claude-A | **Datum** | Architect | Drafting H4/H6 | Gate panel | fixture | 2026-05-31T03:10:00Z |

## Active Edit Locks

| Name | File / Address | Claimed (UTC) | Note |
|---|---|---|---|
| Truss | 2.7.13.W2.5.H2 | 2026-05-31T06:00:00Z | fixture lock |

## Handoff Log (append-only)

- **2026-05-31T06:00Z - Truss > all** - Fixture handoff.
"""


def test_init_schema_and_seed_board():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        board_path = Path(tmpdir) / "board.md"
        board_path.write_text(board_fixture(), encoding="utf-8")

        result = wave25_coorddb.seed_from_board(db_path, board_path, writer="test")

        assert result["roster_rows"] == 2
        assert result["edit_locks"] == 1
        with wave25_coorddb.coordination_db(db_path) as conn:
            version = conn.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()["value"]
            rows = conn.execute("SELECT slot, chosen_name FROM roster ORDER BY slot").fetchall()
            events = [
                row["event_type"]
                for row in conn.execute("SELECT event_type FROM event_log ORDER BY event_id").fetchall()
            ]
        assert version == str(wave25_coorddb.SCHEMA_VERSION)
        assert [(row["slot"], row["chosen_name"]) for row in rows] == [
            ("Claude-A", "Datum"),
            ("Codex-A", "Truss"),
        ]
        assert "seed_from_board" in events
        assert "upsert_roster" in events


def test_roster_revision_and_work_package_upsert():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            wave25_coorddb.upsert_roster(
                conn,
                wave25_coorddb.RosterState(
                    project_id="fixture",
                    slot="Codex-A",
                    chosen_name="Truss",
                    current_task="H2",
                ),
            )
            wave25_coorddb.upsert_roster(
                conn,
                wave25_coorddb.RosterState(
                    project_id="fixture",
                    slot="Codex-A",
                    chosen_name="Truss",
                    current_task="H1",
                ),
            )
            wave25_coorddb.upsert_work_package(
                conn,
                wave25_coorddb.WorkPackageState(
                    project_id="fixture",
                    wp_id="H2",
                    title="Coord DB",
                    status="in_progress",
                    claimed_by="Truss",
                ),
            )
            roster = conn.execute("SELECT revision, current_task, current_hash, last_event_hash FROM roster").fetchone()
            wp = conn.execute("SELECT status, claimed_by FROM work_packages WHERE wp_id='H2'").fetchone()
            event_count = conn.execute("SELECT COUNT(*) AS n FROM event_log").fetchone()["n"]

        assert roster["revision"] == 2
        assert roster["current_task"] == "H1"
        assert roster["current_hash"]
        assert roster["last_event_hash"]
        assert event_count == 3
        assert dict(wp) == {"status": "in_progress", "claimed_by": "Truss"}


def test_concurrent_roster_writers_increment_atomically():
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "coord.sqlite3"
    try:
        writer_count = 25
        barrier = threading.Barrier(writer_count)
        errors: list[str] = []

        def write(index: int) -> None:
            try:
                conn = wave25_coorddb.connect(db_path)
                try:
                    barrier.wait(timeout=5)
                    wave25_coorddb.upsert_roster(
                        conn,
                        wave25_coorddb.RosterState(
                            project_id="fixture",
                            slot="Codex-A",
                            chosen_name="Truss",
                            current_task=f"H2 writer {index}",
                            last_writer=f"writer-{index}",
                        ),
                    )
                finally:
                    conn.close()
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=write, args=(index,)) for index in range(writer_count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert errors == []
        with wave25_coorddb.coordination_db(db_path) as conn:
            row = conn.execute("SELECT revision FROM roster WHERE project_id='fixture' AND slot='Codex-A'").fetchone()
            event_count = conn.execute(
                "SELECT COUNT(*) AS n FROM event_log WHERE project_id='fixture' AND entity_type='roster'"
            ).fetchone()["n"]
        assert row["revision"] == writer_count
        assert event_count == writer_count
    finally:
        try:
            threads.clear()
        except UnboundLocalError:
            pass
        gc.collect()
        cleanup_runtime_dir(tmpdir, db_path)


def test_roster_expected_revision_conflict_blocks_stale_update():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.upsert_roster(
                conn,
                wave25_coorddb.RosterState(project_id="fixture", slot="Codex-A", chosen_name="Truss"),
            )
            try:
                wave25_coorddb.upsert_roster(
                    conn,
                    wave25_coorddb.RosterState(
                        project_id="fixture",
                        slot="Codex-A",
                        chosen_name="Truss",
                        current_task="stale",
                        expected_revision=0,
                    ),
                )
            except wave25_coorddb.CoordinationDbError as exc:
                assert "expected revision" in str(exc)
            else:
                raise AssertionError("stale expected_revision should block update")


def test_heartbeat_current_row_and_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            wave25_coorddb.record_heartbeat(
                conn,
                "fixture",
                "Codex-A",
                "Truss",
                observed_at="2026-05-31T06:00:00Z",
                current_task="H2",
                last_action_type="code",
                monotonic_counter=1,
            )
            wave25_coorddb.record_heartbeat(
                conn,
                "fixture",
                "Codex-A",
                "Truss",
                observed_at="2026-05-31T06:01:00Z",
                current_task="H2",
                last_action_type="test",
                monotonic_counter=2,
            )
            latest = conn.execute(
                "SELECT observed_at, last_action_type, monotonic_counter, current_hash, last_event_hash FROM heartbeats"
            ).fetchone()
            count = conn.execute("SELECT COUNT(*) AS n FROM heartbeat_events").fetchone()["n"]
            event_hashes = [
                row["event_hash"]
                for row in conn.execute("SELECT event_hash FROM heartbeat_events ORDER BY event_id").fetchall()
            ]

        assert latest["observed_at"] == "2026-05-31T06:01:00Z"
        assert latest["last_action_type"] == "test"
        assert latest["monotonic_counter"] == 2
        assert latest["current_hash"]
        assert latest["last_event_hash"]
        assert {
            "observed_at": latest["observed_at"],
            "last_action_type": latest["last_action_type"],
            "monotonic_counter": latest["monotonic_counter"],
        } == {
            "observed_at": "2026-05-31T06:01:00Z",
            "last_action_type": "test",
            "monotonic_counter": 2,
        }
        assert count == 2
        assert len(set(event_hashes)) == 2


def test_secret_payload_rejected_and_rolls_back_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        try:
            with wave25_coorddb.coordination_db(db_path) as conn:
                wave25_coorddb.ensure_project(conn, "fixture")
                wave25_coorddb.record_heartbeat(
                    conn,
                    "fixture",
                    "Codex-A",
                    "Truss",
                    observed_at="2026-05-31T06:00:00Z",
                    payload={"api_token": "do-not-store"},
                )
        except wave25_coorddb.CoordinationDbError as exc:
            assert "secret-looking field" in str(exc)
        else:
            raise AssertionError("secret-looking heartbeat payload should be rejected")

        with wave25_coorddb.coordination_db(db_path) as conn:
            count = conn.execute("SELECT COUNT(*) AS n FROM heartbeats").fetchone()["n"]
        assert count == 0


def test_snapshot_hash_is_stable_for_same_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        output1 = Path(tmpdir) / "snapshot-1.md"
        output2 = Path(tmpdir) / "snapshot-2.md"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            wave25_coorddb.record_heartbeat(
                conn,
                "fixture",
                "Codex-A",
                "Truss",
                observed_at="2026-05-31T06:00:00Z",
                current_task="H2",
            )
        wave25_coorddb.snapshot_to_markdown(db_path, output1, "fixture")
        wave25_coorddb.snapshot_to_markdown(db_path, output2, "fixture")

        def state_hash(path: Path) -> str:
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.startswith("snapshot_state_hash:"):
                    return line.split('"', 2)[1]
            raise AssertionError("snapshot_state_hash missing")

        assert state_hash(output1) == state_hash(output2)


def test_expired_locks_are_removed_from_active_snapshot_with_audit_event():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.upsert_edit_lock(
                conn,
                wave25_coorddb.EditLockState(
                    project_id="fixture",
                    lock_name="h2",
                    target="2.7.13.W2.5.H2",
                    holder="Truss",
                    claimed_at="2026-05-31T06:00:00Z",
                    expires_at="2026-05-31T06:01:00Z",
                ),
            )
        with wave25_coorddb.coordination_db(db_path) as conn:
            snapshot = wave25_coorddb.get_project_snapshot(conn, "fixture")
            status = conn.execute("SELECT status FROM edit_locks WHERE lock_name='h2'").fetchone()["status"]
            event = conn.execute(
                "SELECT event_type FROM event_log WHERE entity_type='edit_lock' ORDER BY event_id DESC LIMIT 1"
            ).fetchone()["event_type"]

        assert snapshot["edit_locks"] == []
        assert status == "expired"
        assert event == "expire_edit_lock"


def test_snapshot_includes_all_events_not_just_last_twenty():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            for index in range(25):
                wave25_coorddb.record_event(
                    conn,
                    wave25_coorddb.CoordinationEvent(
                        project_id="fixture",
                        event_type=f"event-{index}",
                        actor="test",
                        payload={"index": index},
                    ),
                )
            snapshot = wave25_coorddb.get_project_snapshot(conn, "fixture")

        assert len(snapshot["recent_events"]) == 25
        assert snapshot["recent_events"][0]["event_type"] == "event-0"
        assert snapshot["recent_events"][-1]["event_type"] == "event-24"


def test_snapshot_and_cleanup_runtime_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        output = Path(tmpdir) / "snapshot.md"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            wave25_coorddb.record_heartbeat(
                conn,
                "fixture",
                "Codex-A",
                "Truss",
                observed_at="2026-05-31T06:00:00Z",
                current_task="H2",
            )
        wave25_coorddb.snapshot_to_markdown(db_path, output, "fixture")

        text = output.read_text(encoding="utf-8")
        assert "Coordination DB Snapshot" in text
        assert "| Codex-A | Truss | 2026-05-31T06:00:00Z | H2 |" in text
        dry_run = wave25_coorddb.cleanup_runtime_db(db_path, execute=False)
        assert str(db_path) in dry_run["would_remove"]
        try:
            wave25_coorddb.cleanup_runtime_db_after_snapshot(
                db_path,
                snapshot_path=Path(tmpdir) / "missing.md",
                execute=True,
            )
        except wave25_coorddb.CoordinationDbError as exc:
            assert "refusing cleanup" in str(exc)
        else:
            raise AssertionError("cleanup should refuse without durable snapshot")

        removed = wave25_coorddb.cleanup_runtime_db_after_snapshot(db_path, snapshot_path=output, execute=True)
        assert str(db_path) in removed["removed"]
        assert not db_path.exists()


if __name__ == "__main__":
    tests = [
        test_init_schema_and_seed_board,
        test_roster_revision_and_work_package_upsert,
        test_concurrent_roster_writers_increment_atomically,
        test_roster_expected_revision_conflict_blocks_stale_update,
        test_heartbeat_current_row_and_history,
        test_secret_payload_rejected_and_rolls_back_state,
        test_snapshot_hash_is_stable_for_same_state,
        test_expired_locks_are_removed_from_active_snapshot_with_audit_event,
        test_snapshot_includes_all_events_not_just_last_twenty,
        test_snapshot_and_cleanup_runtime_db,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL: {test.__name__} - {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed out of {len(tests)} tests")
    raise SystemExit(1 if failed else 0)
