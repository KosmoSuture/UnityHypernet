#!/usr/bin/env python3
"""Tests for first-live-mirror preflight."""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path

import wave1_live_mirror
import coordination


def board_fixture() -> str:
    return """---
ha: "2.7.13"
object_type: "coordination_board"
---

# 2.7.13 - Execution Wave 1: Coordination & Status

## BOARD STATUS - READ THIS FIRST

> **CURRENT PHASE:** Build phase.
> **WHAT'S HAPPENING NOW:** Contracts are accepted and engineers are building.
> **NEXT ACTION (Truss):** preflight first live mirror.
> **HUMAN GATE:** Matt only for true human decisions.

## Instance Roster

| Slot | Chosen Name | Role | Current Task | Blocked-On | Last Handoff | Updated |
|---|---|---|---|---|---|---|
| Codex-A | **Truss** | Collaboration Substrate Engineer | Preflight mirror | - | mirror start | 2026-05-28T09:00:00Z |

## Interface-Contract Registry

| Contract | Address | Owner | Consumed By | Version | Status |
|---|---|---|---|---|---|
| Collaboration / baton data model + work-package schema | `2.7.13.1` | Datum | Truss | v1.2 | accepted |

## Active Edit Locks

| Name | File / Address | Claimed (UTC-ish) | Note |
|---|---|---|---|
| - | - | - | - |

## Handoff Log (append-only)

- **2026-05-28T09:00Z - Datum > Truss** - Contracts accepted.

---
"""


def valid_wp() -> dict:
    return {
        "ha": "2.7.13.CA.4.wp.test",
        "wp_id": "wp-3-first-live-task-mirror",
        "title": "First live task mirror activation",
        "description": "Mirror an addressed durable WP into coordination.py.",
        "project": "#3",
        "owner": "Truss",
        "status": "pending",
        "phase": "test",
        "blocked_on": [],
        "files_owned": ["Hypernet Structure/2 - AI Accounts/Messages/coordination/TASK-BOARD.json"],
        "acceptance": ["Mirror task references the durable source address."],
        "evidence": [],
        "created_by": "Truss",
        "created_at": "2026-05-28T09:00:00Z",
    }


def ack_fixture(subject_wp: str = "2.7.13.CA.4.wp.test", status: str = "ack-granted") -> str:
    return f"""---
ha: "2.messages.coordination.test-touchstone-ack"
object_type: "verifier_ack"
status: "{status}"
subject_wp: "{subject_wp}"
flags:
  - first-live-write
---

# Ack
"""


def write_files(tmpdir: str, ack_subject: str = "2.7.13.CA.4.wp.test") -> tuple[Path, Path, Path]:
    root = Path(tmpdir)
    board = root / "board.md"
    contract = root / "2.7.13.1 - Contract.md"
    wp = root / "wp.json"
    ack = root / "ack.md"
    board.write_text(board_fixture(), encoding="utf-8")
    contract.write_text('---\nha: "2.7.13.1"\nstatus: "published-v1.2"\n---\n', encoding="utf-8")
    wp.write_text(json.dumps(valid_wp()), encoding="utf-8")
    ack.write_text(ack_fixture(ack_subject), encoding="utf-8")
    return board, wp, ack


def write_task_board(path: Path, description: str, status: str = "pending") -> None:
    path.write_text(
        json.dumps(
            {
                "tasks": [
                    {
                        "id": "task-1",
                        "title": "Mirror",
                        "description": description,
                        "status": status,
                        "claimed_by": None,
                        "created_at": "2026-05-28T09:10:00Z",
                        "completed_at": None,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_preflight_ready_with_matching_ack_and_green_gate():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp, ack = write_files(tmpdir)
        task_board = Path(tmpdir) / "TASK-BOARD.json"

        report = wave1_live_mirror.build_preflight_report(
            wp_path=wp,
            ack_path=ack,
            board_path=board,
            contracts_dir=tmpdir,
            task_board_path=task_board,
            now="2026-05-28T09:05:00Z",
        )

        assert report["ready_to_execute_first_live_mirror"] is True
        assert report["blockers"] == []
        assert report["existing_mirrors"]["count"] == 0
        assert report["coordination_create_argv"][0]["allowed"] is True
        assert any(
            "Durable source: 2.7.13.CA.4.wp.test" in item
            for item in report["coordination_create_argv"][0]["argv"]
        )


def test_preflight_blocks_ack_subject_mismatch():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp, ack = write_files(tmpdir, ack_subject="2.7.13.CA.4.wp.other")
        task_board = Path(tmpdir) / "TASK-BOARD.json"

        report = wave1_live_mirror.build_preflight_report(
            wp_path=wp,
            ack_path=ack,
            board_path=board,
            contracts_dir=tmpdir,
            task_board_path=task_board,
            now="2026-05-28T09:05:00Z",
        )

        assert report["ready_to_execute_first_live_mirror"] is False
        assert any("subject_wp" in blocker for blocker in report["blockers"])


def test_cli_json_does_not_write_live_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp, ack = write_files(tmpdir)
        task_board = Path(tmpdir) / "TASK-BOARD.json"

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = wave1_live_mirror.main(
                [
                    str(wp),
                    "--ack",
                    str(ack),
                    "--board",
                    str(board),
                    "--contracts-dir",
                    tmpdir,
                    "--task-board",
                    str(task_board),
                    "--now",
                    "2026-05-28T09:05:00Z",
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(output.getvalue())
        assert code == 0
        assert payload["ready_to_execute_first_live_mirror"] is True
        assert not (Path(tmpdir) / "TASK-BOARD.json").exists()


def test_preflight_reports_existing_mirror_as_blocker():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp, ack = write_files(tmpdir)
        task_board = Path(tmpdir) / "TASK-BOARD.json"
        write_task_board(task_board, "Already mirrored.\n\nDurable source: 2.7.13.CA.4.wp.test")

        report = wave1_live_mirror.build_preflight_report(
            wp_path=wp,
            ack_path=ack,
            board_path=board,
            contracts_dir=tmpdir,
            task_board_path=task_board,
            now="2026-05-28T09:05:00Z",
        )

        assert report["ready_to_execute_first_live_mirror"] is False
        assert report["existing_mirrors"]["count"] == 1
        assert report["existing_mirrors"]["matches"][0]["id"] == "task-1"
        assert any("already contains 1 task" in blocker for blocker in report["blockers"])


def test_execute_writes_only_configured_temp_coordination_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp, ack = write_files(tmpdir)
        root = Path(tmpdir)
        old_paths = (
            coordination.TASK_BOARD_FILE,
            coordination.LOCK_FILE,
        )
        coordination.TASK_BOARD_FILE = root / "TASK-BOARD.json"
        coordination.LOCK_FILE = root / "coordination.lock"
        try:
            report = wave1_live_mirror.build_preflight_report(
                wp_path=wp,
                ack_path=ack,
                board_path=board,
                contracts_dir=tmpdir,
                task_board_path=coordination.TASK_BOARD_FILE,
                now="2026-05-28T09:05:00Z",
            )

            task = wave1_live_mirror.execute_first_live_mirror(report)
            task_board = json.loads(coordination.TASK_BOARD_FILE.read_text(encoding="utf-8"))

            assert report["executed"] is True
            assert report["created_task"]["id"] == task["id"]
            assert task_board["tasks"][0]["description"].endswith("Durable source: 2.7.13.CA.4.wp.test")
            assert task_board["tasks"][0]["owned_paths"] == valid_wp()["files_owned"]
            try:
                wave1_live_mirror.execute_first_live_mirror(report)
            except ValueError as exc:
                assert "already contains" in str(exc)
            else:
                raise AssertionError("duplicate live mirror execution should fail")
        finally:
            coordination.TASK_BOARD_FILE, coordination.LOCK_FILE = old_paths


if __name__ == "__main__":
    tests = [
        test_preflight_ready_with_matching_ack_and_green_gate,
        test_preflight_blocks_ack_subject_mismatch,
        test_cli_json_does_not_write_live_state,
        test_preflight_reports_existing_mirror_as_blocker,
        test_execute_writes_only_configured_temp_coordination_state,
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
