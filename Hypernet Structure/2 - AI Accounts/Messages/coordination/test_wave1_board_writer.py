#!/usr/bin/env python3
"""Tests for the Wave 1 atomic board writer."""

from __future__ import annotations

import os
import tempfile
import time
from pathlib import Path

import wave1_board
import wave1_board_writer


def board_fixture() -> str:
    return """---
ha: "2.7.13"
object_type: "coordination_board"
---

# 2.7.13 - Execution Wave 1: Coordination & Status

## BOARD STATUS - READ THIS FIRST

> **CURRENT PHASE:** Build phase.
> **WHAT'S HAPPENING NOW:** Testing writer.
> **NEXT ACTION (Truss):** keep testing.
> **HUMAN GATE:** None.

## Instance Roster

| Slot | Chosen Name | Role | Current Task | Blocked-On | Last Handoff | Updated |
|---|---|---|---|---|---|---|
| Codex-A | **Truss** | Collaboration Substrate Engineer | Old task | - | old handoff | 2026-05-28T09:00Z |
| Claude-C | **Touchstone** | Verifier | Verify | - | verify | 2026-05-28T09:00Z |

## Active Edit Locks

| Name | File / Address | Claimed (UTC-ish) | Note |
|---|---|---|---|
| - | - | - | - |

## Handoff Log (append-only)

- **2026-05-28T09:00Z - Datum > all** - Existing handoff.

---

*Footer.*
"""


def update_fixture() -> wave1_board_writer.BoardUpdate:
    return wave1_board_writer.BoardUpdate(
        slot="Codex-A",
        current_task="New task",
        blocked_on="No blocker",
        last_handoff="(09:10Z -> all: writer test)",
        updated="2026-05-28T09:10Z",
        handoff_timestamp="2026-05-28T09:10Z",
        handoff_from="Truss (Codex-A)",
        handoff_to="all",
        handoff_body="Writer updated roster and handoff together.",
    )


def board_fixture_with_truss_lock() -> str:
    return board_fixture().replace(
        "| - | - | - | - |",
        "| Truss | `Messages/coordination/wave1_board_writer.py` | 2026-05-28T09:44Z | test lock |\n| - | - | - | - |",
    )


def test_apply_board_update_updates_roster_and_appends_handoff():
    updated = wave1_board_writer.apply_board_update_text(board_fixture(), update_fixture())
    board_path = Path("unused.md")
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        board_path.write_text(updated, encoding="utf-8")
        parsed = wave1_board.parse_board(board_path)

    truss = next(row for row in parsed.roster if row.slot == "Codex-A")
    assert truss.current_task == "New task"
    assert truss.blocked_on == "No blocker"
    assert truss.updated == "2026-05-28T09:10Z"
    assert parsed.handoffs[-1].sender == "Truss (Codex-A)"
    assert parsed.handoffs[-1].recipient == "all"
    assert "Writer updated roster" in parsed.handoffs[-1].body


def test_write_board_update_execute_uses_lock_and_removes_it():
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        board_path.write_text(board_fixture(), encoding="utf-8")

        report = wave1_board_writer.write_board_update(board_path, update_fixture(), execute=True)

        assert report["changed"] is True
        assert not wave1_board_writer.lock_path_for(board_path).exists()
        assert "New task" in board_path.read_text(encoding="utf-8")
        assert not list(Path(tmpdir).glob("*.tmp"))


def test_stale_lock_is_removed_before_execute():
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        board_path.write_text(board_fixture(), encoding="utf-8")
        lock_path = wave1_board_writer.lock_path_for(board_path)
        lock_path.write_text("stale\n", encoding="utf-8")
        old = time.time() - 120
        os.utime(lock_path, (old, old))

        report = wave1_board_writer.write_board_update(
            board_path,
            update_fixture(),
            execute=True,
            stale_seconds=1,
        )

        assert report["changed"] is True
        assert not lock_path.exists()


def test_execute_can_clear_active_edit_lock_in_same_write():
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        board_path.write_text(board_fixture_with_truss_lock(), encoding="utf-8")
        update = update_fixture()
        update.clear_lock_name = "Truss"

        wave1_board_writer.write_board_update(board_path, update, execute=True)
        parsed = wave1_board.parse_board(board_path)

        assert parsed.edit_locks == []


def test_apply_board_update_can_rewrite_board_status_block():
    update = update_fixture()
    update.board_status = {
        "current_phase": "Build phase with writer.",
        "whats_happening_now": "Writer is under fixture test.",
        "next_action_owner": "Truss",
        "next_action": "Continue hardening.",
        "human_gate": "None for fixture.",
    }

    updated = wave1_board_writer.apply_board_update_text(board_fixture(), update)
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        board_path.write_text(updated, encoding="utf-8")
        parsed = wave1_board.parse_board(board_path)

    assert parsed.status.current_phase == "Build phase with writer."
    assert parsed.status.whats_happening_now == "Writer is under fixture test."
    assert parsed.status.next_action_owner == "Truss"
    assert parsed.status.next_action == "Continue hardening."
    assert parsed.status.human_gate == "None for fixture."


def test_fresh_lock_blocks_execute():
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        board_path.write_text(board_fixture(), encoding="utf-8")
        lock_path = wave1_board_writer.lock_path_for(board_path)
        lock_path.write_text("fresh\n", encoding="utf-8")

        try:
            wave1_board_writer.write_board_update(
                board_path,
                update_fixture(),
                execute=True,
                lock_timeout_seconds=0,
                stale_seconds=60,
            )
        except TimeoutError as exc:
            assert "Timed out waiting for board lock" in str(exc)
        else:
            raise AssertionError("fresh board lock should block execute")


def test_missing_roster_row_fails_without_changing_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        original = board_fixture()
        board_path.write_text(original, encoding="utf-8")
        update = update_fixture()
        update.slot = "Codex-B"

        try:
            wave1_board_writer.write_board_update(board_path, update, execute=True)
        except wave1_board_writer.BoardWriteError as exc:
            assert "Instance Roster row not found" in str(exc)
        else:
            raise AssertionError("missing roster row should fail")
        assert board_path.read_text(encoding="utf-8") == original


if __name__ == "__main__":
    tests = [
        test_apply_board_update_updates_roster_and_appends_handoff,
        test_write_board_update_execute_uses_lock_and_removes_it,
        test_stale_lock_is_removed_before_execute,
        test_execute_can_clear_active_edit_lock_in_same_write,
        test_apply_board_update_can_rewrite_board_status_block,
        test_fresh_lock_blocks_execute,
        test_missing_roster_row_fails_without_changing_file,
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
