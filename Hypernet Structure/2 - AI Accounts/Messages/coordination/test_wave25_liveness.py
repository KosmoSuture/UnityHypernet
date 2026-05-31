#!/usr/bin/env python3
"""Tests for Wave 2.5 liveness heartbeat/classifier tooling."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import wave25_coorddb
import wave25_liveness


NOW = datetime(2026, 5, 31, 6, 10, tzinfo=timezone.utc)


def add_roster(conn, slot: str = "Codex-A", name: str = "Truss", task: str = "Building H1"):
    wave25_coorddb.upsert_roster(
        conn,
        wave25_coorddb.RosterState(
            project_id="fixture",
            slot=slot,
            chosen_name=name,
            current_task=task,
            updated_at="2026-05-31T06:00:00Z",
        ),
    )


def labels_by_slot(db_path: Path):
    return {
        status.slot: status
        for status in wave25_liveness.classify_liveness(db_path, "fixture", now=NOW)
    }


def test_fresh_working_heartbeat_is_active_working():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn)
        wave25_liveness.write_heartbeat(
            db_path,
            "fixture",
            "Codex-A",
            "Truss",
            current_task="Building H1",
            last_action_type="code",
            observed_at="2026-05-31T06:09:30Z",
            monotonic_counter=4,
        )

        status = labels_by_slot(db_path)["Codex-A"]

        assert status.label == wave25_liveness.LABEL_ACTIVE_WORKING
        assert status.heartbeat_present is True
        assert status.lifecycle_state == "live"


def test_fresh_waiting_heartbeat_is_idle():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn, task="Waiting for gate panel")
        wave25_liveness.write_heartbeat(
            db_path,
            "fixture",
            "Codex-A",
            "Truss",
            current_task="Waiting for gate panel",
            last_action_type="waiting",
            observed_at="2026-05-31T06:09:30Z",
        )

        assert labels_by_slot(db_path)["Codex-A"].label == wave25_liveness.LABEL_IDLE


def test_contextual_first_boot_mention_in_task_is_not_starting():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn, task="Verifying H3 evidence")
        wave25_liveness.write_heartbeat(
            db_path,
            "fixture",
            "Codex-A",
            "Truss",
            current_task="Verifying Plumb first-boot evidence and spawn-gate ordering",
            last_action_type="verify",
            observed_at="2026-05-31T06:09:30Z",
        )

        status = labels_by_slot(db_path)["Codex-A"]

        assert status.label == wave25_liveness.LABEL_ACTIVE_WORKING
        assert status.lifecycle_state == "live"


def test_late_heartbeat_is_active_slow_then_stale_then_dead():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn)
        for observed_at, expected in [
            ("2026-05-31T06:06:00Z", wave25_liveness.LABEL_ACTIVE_SLOW),
            ("2026-05-31T06:03:00Z", wave25_liveness.LABEL_STALE_WARNING),
            ("2026-05-31T05:50:00Z", wave25_liveness.LABEL_DEAD),
        ]:
            wave25_liveness.write_heartbeat(
                db_path,
                "fixture",
                "Codex-A",
                "Truss",
                current_task="Building H1",
                last_action_type="code",
                observed_at=observed_at,
            )
            status = wave25_liveness.classify_liveness(
                db_path,
                "fixture",
                now=NOW,
                thresholds=wave25_liveness.LivenessThresholds(
                    active_seconds=90,
                    slow_seconds=300,
                    dead_seconds=900,
                ),
            )[0]
            assert status.label == expected


def test_no_heartbeat_for_first_boot_placeholder_is_not_dead():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(
                conn,
                slot="Claude-C",
                name="(unclaimed - Verifier)",
                task="boot via 2.7.15 first-boot sequence",
            )

        status = labels_by_slot(db_path)["Claude-C"]

        assert status.label == wave25_liveness.LABEL_IDLE
        assert status.lifecycle_state == "starting"
        assert "not a respawn outage" in status.reason


def test_no_heartbeat_for_decorated_first_boot_row_is_not_dead():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(
                conn,
                slot="Codex-C",
                name="Plumb",
                task="**FIRST-BOOT** - live session is booting for H3 review",
            )

        status = labels_by_slot(db_path)["Codex-C"]

        assert status.label == wave25_liveness.LABEL_IDLE
        assert status.lifecycle_state == "starting"


def test_no_heartbeat_for_live_roster_row_is_dead():
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
                    current_task="Building H1",
                    updated_at="2026-05-31T05:00:00Z",
                ),
            )

        status = labels_by_slot(db_path)["Codex-A"]

        assert status.label == wave25_liveness.LABEL_DEAD
        assert status.heartbeat_present is False


def test_recent_coordination_message_is_activity_fallback_without_heartbeat():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        db_path = root / "coord.sqlite3"
        messages_dir = root / "messages"
        messages_dir.mkdir()
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            wave25_coorddb.upsert_roster(
                conn,
                wave25_coorddb.RosterState(
                    project_id="fixture",
                    slot="Claude-A",
                    chosen_name="Datum",
                    current_task="Old board task",
                    updated_at="2026-05-31T05:00:00Z",
                ),
            )
        message = messages_dir / "20260531T060930Z-datum-h6-update.md"
        message.write_text(
            """---
from: "Datum (Lead Architect - Claude-A)"
created: "2026-05-31T06:09:30Z"
---

# Update
""",
            encoding="utf-8",
        )
        timestamp = NOW.timestamp() - 30
        os.utime(message, (timestamp, timestamp))

        status = wave25_liveness.classify_liveness(
            db_path,
            "fixture",
            now=NOW,
            messages_dir=messages_dir,
        )[0]

        assert status.label == wave25_liveness.LABEL_IDLE
        assert status.heartbeat_present is False
        assert "coordination message" in status.reason


def test_no_heartbeat_with_fresh_roster_update_is_temporary_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn, task="Building H1")

        status = labels_by_slot(db_path)["Codex-A"]

        assert status.label == wave25_liveness.LABEL_STALE_WARNING
        assert "roster update" in status.reason


def test_future_dated_heartbeat_is_clock_anomaly_not_active():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn)
        wave25_liveness.write_heartbeat(
            db_path,
            "fixture",
            "Codex-A",
            "Truss",
            current_task="Building H1",
            last_action_type="code",
            observed_at="2026-05-31T06:50:00Z",
        )

        status = labels_by_slot(db_path)["Codex-A"]

        assert status.label == wave25_liveness.LABEL_STALE_WARNING
        assert "future-dated" in status.reason


def test_small_future_dated_heartbeat_within_skew_tolerance_is_active():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn)
        wave25_liveness.write_heartbeat(
            db_path,
            "fixture",
            "Codex-A",
            "Truss",
            current_task="Building H1",
            last_action_type="code",
            observed_at="2026-05-31T06:10:30Z",
        )

        status = labels_by_slot(db_path)["Codex-A"]

        assert status.label == wave25_liveness.LABEL_ACTIVE_WORKING
        assert "within clock skew tolerance" in status.reason
        assert status.suspicion_score == 0.0


def test_slow_baseline_below_suspicion_threshold_is_not_dead():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "coord.sqlite3"
        with wave25_coorddb.coordination_db(db_path) as conn:
            wave25_coorddb.ensure_project(conn, "fixture")
            add_roster(conn)
        for counter, observed_at in enumerate(
            [
                "2026-05-31T05:00:00Z",
                "2026-05-31T05:04:10Z",
                "2026-05-31T05:08:20Z",
                "2026-05-31T05:12:30Z",
            ],
            start=1,
        ):
            wave25_liveness.write_heartbeat(
                db_path,
                "fixture",
                "Codex-A",
                "Truss",
                current_task="Long red-team pass",
                last_action_type="analysis",
                observed_at=observed_at,
                monotonic_counter=counter,
            )

        status = wave25_liveness.classify_liveness(
            db_path,
            "fixture",
            now=datetime(2026, 5, 31, 5, 28, tzinfo=timezone.utc),
        )[0]

        assert status.label == wave25_liveness.LABEL_STALE_WARNING
        assert status.suspicion_score < wave25_liveness.DEFAULT_DEAD_SUSPICION_THRESHOLD
        assert status.work_signature_unchanged_count == 4


if __name__ == "__main__":
    tests = [
        test_fresh_working_heartbeat_is_active_working,
        test_fresh_waiting_heartbeat_is_idle,
        test_contextual_first_boot_mention_in_task_is_not_starting,
        test_late_heartbeat_is_active_slow_then_stale_then_dead,
        test_no_heartbeat_for_first_boot_placeholder_is_not_dead,
        test_no_heartbeat_for_decorated_first_boot_row_is_not_dead,
        test_no_heartbeat_for_live_roster_row_is_dead,
        test_recent_coordination_message_is_activity_fallback_without_heartbeat,
        test_no_heartbeat_with_fresh_roster_update_is_temporary_fallback,
        test_future_dated_heartbeat_is_clock_anomaly_not_active,
        test_small_future_dated_heartbeat_within_skew_tolerance_is_active,
        test_slow_baseline_below_suspicion_threshold_is_not_dead,
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
