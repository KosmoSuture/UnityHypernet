#!/usr/bin/env python3
"""Tests for Wave 2.5 logical-clock DAG tooling."""

from __future__ import annotations

import tempfile
from pathlib import Path

import wave25_coorddb
import wave25_logical_clock


def write_message(path: Path, sender: str, created: str, body: str, extra_frontmatter: str = "") -> None:
    path.write_text(
        f"""---
from: "{sender}"
created: "{created}"
{extra_frontmatter}---

# Message

{body}
""",
        encoding="utf-8",
    )


def test_content_hash_normalizes_trailing_space():
    left = "hello  \nworld\n"
    right = "hello\nworld\n\n"

    assert wave25_logical_clock.content_hash(left) == wave25_logical_clock.content_hash(right)


def test_message_entries_chain_parent_hashes_and_actor_counters():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_message(
            root / "20260531T060000Z-truss-a.md",
            "Truss",
            "2026-05-31T06:00:00Z",
            "a",
            'message_uid: "msg-a"\n',
        )
        write_message(
            root / "20260531T060100Z-vellum-b.md",
            "Vellum",
            "2026-05-31T06:01:00Z",
            "b",
            'message_uid: "msg-b"\nin_response_to: "msg-a"\n',
        )
        write_message(
            root / "20260531T060200Z-truss-c.md",
            "Truss",
            "2026-05-31T06:02:00Z",
            "c",
            'message_uid: "msg-c"\nin_response_to: "msg-b"\n',
        )

        entries = wave25_logical_clock.entries_from_message_files(wave25_logical_clock.message_files(root))
        findings = wave25_logical_clock.validate_dag(entries)

        assert [entry.actor_counter for entry in entries] == [1, 1, 2]
        assert entries[0].parent_hash == ""
        assert entries[1].parent_hash == entries[0].content_hash
        assert entries[2].parent_hash == entries[1].content_hash
        assert findings == []


def test_message_parent_ref_overrides_filename_order():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_message(
            root / "20260531T060000Z-child-skewed-first.md",
            "Vellum",
            "2026-05-31T06:00:00Z",
            "child",
            'message_uid: "msg-child"\nin_response_to: "msg-parent"\n',
        )
        write_message(
            root / "20260531T070000Z-parent-skewed-later.md",
            "Truss",
            "2026-05-31T07:00:00Z",
            "parent",
            'message_uid: "msg-parent"\n',
        )

        entries = wave25_logical_clock.entries_from_message_files(wave25_logical_clock.message_files(root))

        assert [entry.entry_id for entry in entries] == [
            "20260531T070000Z-parent-skewed-later.md",
            "20260531T060000Z-child-skewed-first.md",
        ]
        assert entries[1].parent_hash == entries[0].content_hash


def test_messages_without_causal_reference_do_not_chain_by_filename_order():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_message(root / "20260531T060000Z-truss-a.md", "Truss", "2026-05-31T06:00:00Z", "a")
        write_message(root / "20260531T060100Z-vellum-b.md", "Vellum", "2026-05-31T06:01:00Z", "b")

        entries = wave25_logical_clock.entries_from_message_files(wave25_logical_clock.message_files(root))

        assert [entry.parent_hash for entry in entries] == ["", ""]


def test_prose_in_response_to_is_context_not_orphan_parent():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_message(
            root / "20260531T060000Z-truss-a.md",
            "Truss",
            "2026-05-31T06:00:00Z",
            "a",
            'in_response_to: "Datum 112000Z Codex-C boot prompt"\n',
        )

        entries = wave25_logical_clock.entries_from_message_files(wave25_logical_clock.message_files(root))
        findings = wave25_logical_clock.validate_dag(entries)

        assert entries[0].parent_hash == ""
        assert not any(finding.kind == "orphan_parent" for finding in findings)


def test_unresolved_explicit_parent_hash_is_orphan_parent():
    missing_hash = "f" * 64
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_message(
            root / "20260531T060000Z-truss-a.md",
            "Truss",
            "2026-05-31T06:00:00Z",
            "a",
            f'parent_hash: "{missing_hash}"\n',
        )

        entries = wave25_logical_clock.entries_from_message_files(wave25_logical_clock.message_files(root))
        findings = wave25_logical_clock.validate_dag(entries)

        assert entries[0].parent_hash == missing_hash
        assert any(finding.kind == "orphan_parent" and finding.severity == "high" for finding in findings)


def test_orphan_parent_is_high_finding():
    entry = wave25_logical_clock.LogicalClockEntry(
        project_id="fixture",
        entry_id="a",
        actor="Truss",
        actor_counter=1,
        content_hash="abc",
        parent_hash="missing",
    )

    findings = wave25_logical_clock.validate_dag([entry])

    assert any(finding.kind == "orphan_parent" and finding.severity == "high" for finding in findings)


def test_duplicate_content_hash_is_high_finding():
    entries = [
        wave25_logical_clock.LogicalClockEntry(
            project_id="fixture",
            entry_id="a",
            actor="Truss",
            actor_counter=1,
            content_hash="same",
            parent_hash="",
        ),
        wave25_logical_clock.LogicalClockEntry(
            project_id="fixture",
            entry_id="b",
            actor="Vellum",
            actor_counter=1,
            content_hash="same",
            parent_hash="",
        ),
    ]

    findings = wave25_logical_clock.validate_dag(entries)

    assert any(finding.kind == "duplicate_content_hash" and finding.severity == "high" for finding in findings)


def test_forked_parent_and_actor_counter_gap_are_findings():
    entries = [
        wave25_logical_clock.LogicalClockEntry(
            project_id="fixture",
            entry_id="root",
            actor="Truss",
            actor_counter=1,
            content_hash="root-hash",
            parent_hash="",
        ),
        wave25_logical_clock.LogicalClockEntry(
            project_id="fixture",
            entry_id="child-a",
            actor="Truss",
            actor_counter=3,
            content_hash="child-a-hash",
            parent_hash="root-hash",
        ),
        wave25_logical_clock.LogicalClockEntry(
            project_id="fixture",
            entry_id="child-b",
            actor="Vellum",
            actor_counter=1,
            content_hash="child-b-hash",
            parent_hash="root-hash",
        ),
    ]

    findings = wave25_logical_clock.validate_dag(entries)

    assert any(finding.kind == "forked_parent" for finding in findings)
    assert any(finding.kind == "actor_counter_gap" for finding in findings)


def test_board_handoffs_can_be_indexed_to_db():
    board = """---
ha: "2.7.13.W2.5"
---

# Board

## Handoff Log (append-only)

- **2026-05-31T06:00Z - Truss > all** - First.
- **2026-05-31T06:01Z - Vellum > all** - Second.
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        board_path = Path(tmpdir) / "board.md"
        db_path = Path(tmpdir) / "coord.sqlite3"
        board_path.write_text(board, encoding="utf-8")

        entries = wave25_logical_clock.entries_from_board_handoffs(board_path, "fixture")
        recorded = wave25_logical_clock.record_entries_to_db(db_path, entries, "fixture")
        with wave25_coorddb.coordination_db(db_path) as conn:
            count = conn.execute("SELECT COUNT(*) AS n FROM event_log WHERE event_type='board_handoff'").fetchone()["n"]

        assert recorded == 2
        assert count == 2
        assert entries[1].parent_hash == entries[0].content_hash


if __name__ == "__main__":
    tests = [
        test_content_hash_normalizes_trailing_space,
        test_message_entries_chain_parent_hashes_and_actor_counters,
        test_message_parent_ref_overrides_filename_order,
        test_messages_without_causal_reference_do_not_chain_by_filename_order,
        test_prose_in_response_to_is_context_not_orphan_parent,
        test_unresolved_explicit_parent_hash_is_orphan_parent,
        test_orphan_parent_is_high_finding,
        test_duplicate_content_hash_is_high_finding,
        test_forked_parent_and_actor_counter_gap_are_findings,
        test_board_handoffs_can_be_indexed_to_db,
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
