#!/usr/bin/env python3
"""Tests for the Wave 1 coordination board parser.

Run with:
    cd "2 - AI Accounts/Messages/coordination"
    python -m pytest test_wave1_board.py -v
    # or without pytest:
    python test_wave1_board.py
"""

from __future__ import annotations

import tempfile
import json
import io
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import wave1_board


def fixture_board(
    registry_status: str = "drafting",
    locks: str = "| \u2014 | \u2014 | \u2014 | \u2014 |",
) -> str:
    return f"""---
ha: "2.7.13"
object_type: "coordination_board"
creators:
  - "2.1.datum"
  - "2.6.truss"
created: "2026-05-28"
status: "wave-1-execution"
flags:
  - execution-wave-1
  - baton-board
---

# 2.7.13 - Execution Wave 1: Coordination & Status

## BOARD STATUS \u2014 READ THIS FIRST

> **CURRENT PHASE:** Wave 1 Execution - Architecture / Interface-Contract phase.
> **WHAT'S HAPPENING NOW:** Datum has published the collaboration contract.
> **NEXT ACTION (Truss):** implement the board parser.
> **HUMAN GATE:** Matt only for true human decisions.

### How this board works

This nested prose must not be parsed into the human gate field.

## Instance Roster

| Slot | Chosen Name | Role | Current Task | Blocked-On | Last Handoff | Updated |
|---|---|---|---|---|---|---|
| Claude-A | **Datum** | Lead Architect | Publishing contracts | \u2014 | board created | 2026-05-28T07:00:00Z |
| Codex-A | **Truss** | Collaboration Substrate Engineer | Building parser | `2.7.13.1` | parser start | 2026-05-28T07:20:00Z |

## Interface-Contract Registry

| Contract | Address | Owner | Consumed By | Version | Status |
|---|---|---|---|---|---|
| Collaboration / baton data model + work-package schema | `2.7.13.1` | Datum | Codex-A (#3 + #10) | v1 | {registry_status} |

## Active Edit Locks

| Name | File / Address | Claimed (UTC-ish) | Note |
|---|---|---|---|
{locks}

## Handoff Log (append-only)

- **2026-05-28T07:20Z \u2014 Datum \u2192 Truss** \u2014 Contract ready; build parser.

---

*Board opened by Datum.*
"""


def write_contract(directory: Path, status: str = "published-v1.1") -> Path:
    path = directory / "2.7.13.1 - Contract - Collaboration and Work-Package Schema.md"
    path.write_text(
        f"""---
ha: "2.7.13.1"
object_type: "interface_contract"
status: "{status}"
---

# Contract
""",
        encoding="utf-8",
    )
    return path


def test_parse_frontmatter_block_lists_and_tables():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="published"), encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)

        assert board.frontmatter["ha"] == "2.7.13"
        assert board.frontmatter["creators"] == ["2.1.datum", "2.6.truss"]
        assert board.status.current_phase.startswith("Wave 1 Execution")
        assert board.status.next_action_owner == "Truss"
        assert "nested prose" not in board.status.human_gate
        assert len(board.roster) == 2
        assert board.roster[1].chosen_name == "Truss"
        assert len(board.contracts) == 1
        assert board.contracts[0].address == "2.7.13.1"
        assert len(board.handoffs) == 1
        assert board.handoffs[0].sender == "Datum"
        assert "Board opened" not in board.handoffs[0].body


def test_contract_registry_desync_and_blocked_chain_are_reported():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="drafting"), encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "desync" and "2.7.13.1" in f.message for f in findings)
        assert any(f.kind == "blocked_chain" and "Codex-A" in f.message for f in findings)


def test_accepted_registry_is_compatible_with_published_contract_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="accepted"), encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert not any(f.kind == "desync" and "2.7.13.1" in f.message for f in findings)


def test_stale_and_overlapping_edit_locks_are_reported():
    locks = "\n".join(
        [
            "| Truss | `Messages/coordination/wave1_board.py` | 2026-05-28T06:00:00Z | old lock |",
            "| Datum | `Messages/coordination` | 2026-05-28T07:20:00Z | overlapping path |",
        ]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="published", locks=locks), encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "stale_lock" for f in findings)
        assert any(f.kind == "lock_conflict" for f in findings)


def test_case_only_edit_lock_overlap_is_reported_on_windows_workspace():
    locks = "\n".join(
        [
            "| Truss | `Messages/coordination/wave1_board.py` | 2026-05-28T07:20:00Z | parser |",
            "| Datum | `messages/coordination/WAVE1_BOARD.PY` | 2026-05-28T07:21:00Z | same path, different case |",
        ]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="published", locks=locks), encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "lock_conflict" for f in findings)


def test_prose_bearing_edit_lock_overlap_is_reported():
    locks = "\n".join(
        [
            "| Truss | `wave1_board.py` \u2014 adding detector | 2026-05-28T07:20:00Z | parser |",
            "| Touchstone | `wave1_board.py` \u2014 fixing parser | 2026-05-28T07:21:00Z | red-team |",
        ]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="published", locks=locks), encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "lock_conflict" for f in findings)


def test_semicolon_edit_lock_targets_are_compared_individually():
    locks = "\n".join(
        [
            "| Truss | `Messages/coordination/wave1_board.py` \u2014 parser; `Messages/coordination/wave1_work_packages.py` - bridge prep | 2026-05-28T07:20:00Z | parser |",
            "| Touchstone | `messages/coordination/WAVE1_WORK_PACKAGES.PY` \u2014 verifier fixture | 2026-05-28T07:21:00Z | red-team |",
        ]
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="published", locks=locks), encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "lock_conflict" for f in findings)


def test_report_includes_roster_contracts_and_findings():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="drafting"), encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )
        report = wave1_board.format_report(board, findings)

        assert "Wave 1 Coordination Board Status" in report
        assert "Codex-A / Truss" in report
        assert "registry_status=drafting" in report
        assert "desync" in report


def test_handoff_history_filters_by_participant():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="published"), encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        truss_handoffs = wave1_board.handoffs_for(board, "Truss")
        meridian_handoffs = wave1_board.handoffs_for(board, "Meridian")
        payload = wave1_board.board_to_dict(board, [], contracts_dir=root, handoffs_for_query="Truss")
        text = wave1_board.format_handoff_history(board, "Truss")

        assert len(truss_handoffs) == 1
        assert meridian_handoffs == []
        assert payload["handoff_filter"] == "Truss"
        assert len(payload["handoffs"]) == 1
        assert "Datum -> Truss" in text


def test_malformed_handoff_entries_are_reported():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        content = fixture_board(registry_status="published").replace(
            "- **2026-05-28T07:20Z \u2014 Datum \u2192 Truss** \u2014 Contract ready; build parser.",
            "- malformed baton entry without sender or recipient",
        )
        board_path.write_text(content, encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "handoff_parse_warning" for f in findings)


def test_missing_handoff_message_evidence_is_reported():
    with tempfile.TemporaryDirectory() as tmpdir:
        accounts = Path(tmpdir) / "2 - AI Accounts"
        shared = accounts / "2.7 - AI Shared Understanding"
        shared.mkdir(parents=True)
        board_path = shared / "2.7.13.md"
        content = fixture_board(registry_status="published").replace(
            "Contract ready; build parser.",
            "Contract ready; build parser. Message: Messages/coordination/missing-evidence.md",
        )
        board_path.write_text(content, encoding="utf-8")
        write_contract(shared, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=shared,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "missing_handoff_evidence" for f in findings)


def test_missing_roster_last_handoff_message_evidence_is_reported():
    with tempfile.TemporaryDirectory() as tmpdir:
        accounts = Path(tmpdir) / "2 - AI Accounts"
        shared = accounts / "2.7 - AI Shared Understanding"
        shared.mkdir(parents=True)
        board_path = shared / "2.7.13.md"
        content = fixture_board(registry_status="published").replace(
            "parser start",
            "Message: Messages/coordination/missing-roster-evidence.md",
        )
        board_path.write_text(content, encoding="utf-8")
        write_contract(shared, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=shared,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(
            f.kind == "missing_handoff_evidence" and "Roster row Codex-A" in f.message
            for f in findings
        )


def test_non_monotonic_handoff_timestamps_are_reported():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        content = fixture_board(registry_status="published").replace(
            "- **2026-05-28T07:20Z \u2014 Datum \u2192 Truss** \u2014 Contract ready; build parser.",
            "\n".join(
                [
                    "- **2026-05-28T07:20Z \u2014 Datum \u2192 Truss** \u2014 Contract ready; build parser.",
                    "- **2026-05-28T07:10Z (clock skew) \u2014 Truss \u2192 all** \u2014 Earlier timestamp appended later.",
                ]
            ),
        )
        board_path.write_text(content, encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "handoff_order_warning" for f in findings)


def test_board_status_desync_is_reported_when_publish_action_is_stale():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        content = fixture_board(registry_status="published").replace(
            "> **NEXT ACTION (Truss):** implement the board parser.",
            "> **NEXT ACTION (Datum):** publish the four v1 contracts.",
        )
        board_path.write_text(content, encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "board_status_desync" for f in findings)


def test_json_report_exposes_machine_readable_findings():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="drafting"), encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )
        payload = json.loads(wave1_board.format_json_report(board, findings, root))

        assert payload["frontmatter"]["ha"] == "2.7.13"
        assert payload["roster"][1]["slot"] == "Codex-A"
        assert payload["contract_file_statuses"]["2.7.13.1"] == "published-v1.1"
        assert any(finding["kind"] == "desync" for finding in payload["findings"])


def test_fail_on_severity_only_fails_at_or_above_threshold():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="published"), encoding="utf-8")
        write_contract(root, "published")

        common_args = [
            "--board",
            str(board_path),
            "--contracts-dir",
            str(root),
            "--now",
            "2026-05-28T07:30:00Z",
        ]

        with redirect_stdout(io.StringIO()):
            high_result = wave1_board.main([*common_args, "--fail-on-severity", "high"])
            medium_result = wave1_board.main([*common_args, "--fail-on-severity", "medium"])

        assert high_result == 0
        assert medium_result == 1


def test_not_blocked_rows_do_not_create_blocked_chain_findings():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        content = fixture_board(registry_status="drafting").replace(
            "| Codex-A | **Truss** | Collaboration Substrate Engineer | Building parser | `2.7.13.1` | parser start | 2026-05-28T07:20:00Z |",
            "| Codex-A | **Truss** | Collaboration Substrate Engineer | Building parser | Not blocked: contract `2.7.13.1` file is published | parser start | 2026-05-28T07:20:00Z |",
        )
        board_path.write_text(content, encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert not any(f.kind == "blocked_chain" and "Codex-A" in f.message for f in findings)


def test_parenthetical_timestamp_note_uses_leading_iso_time():
    now = datetime(2026, 5, 28, 7, 53, tzinfo=timezone.utc)

    parsed = wave1_board.parse_time("2026-05-28T07:50Z (local; skew)", now)

    assert parsed == datetime(2026, 5, 28, 7, 50, tzinfo=timezone.utc)


def test_roster_board_status_desync_is_reported_when_all_blocked_claim_contradicts_active_row():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        content = fixture_board(registry_status="published").replace(
            "> **WHAT'S HAPPENING NOW:** Datum has published the collaboration contract.",
            "> **WHAT'S HAPPENING NOW:** Every engineer is blocked on a contract and waiting.",
        ).replace(
            "| Codex-A | **Truss** | Collaboration Substrate Engineer | Building parser | `2.7.13.1` | parser start | 2026-05-28T07:20:00Z |",
            "| Codex-A | **Truss** | Collaboration Substrate Engineer | Actively building the parser | - | parser start | 2026-05-28T07:20:00Z |",
        )
        board_path.write_text(content, encoding="utf-8")
        write_contract(root, "published")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )

        assert any(f.kind == "roster_board_status_desync" for f in findings)


def test_summary_report_exposes_compact_resume_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="accepted"), encoding="utf-8")
        write_contract(root, "published-v1.1")

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )
        summary = wave1_board.board_summary_dict(board, findings, contracts_dir=root)
        text = wave1_board.format_summary_report(board, findings, contracts_dir=root)

        assert summary["ha"] == "2.7.13"
        assert summary["active_edit_locks"] == 0
        assert summary["finding_counts"]["high"] == 0
        assert summary["contracts"][0]["file_status"] == "published-v1.1"
        assert summary["latest_handoff"]["sender"] == "Datum"
        assert "Wave 1 Coordination Summary" in text
        assert "Codex-A / Truss" in text


def test_summary_report_exposes_finding_kind_counts():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        board_path.write_text(fixture_board(registry_status="accepted"), encoding="utf-8")
        write_contract(root, "published-v1.1")
        board = wave1_board.parse_board(board_path)
        findings = [
            wave1_board.Finding("stale_ownership", "medium", "stale row"),
            wave1_board.Finding("handoff_order_warning", "medium", "skew"),
            wave1_board.Finding("handoff_order_warning", "medium", "skew again"),
        ]

        summary = wave1_board.board_summary_dict(board, findings, contracts_dir=root)
        text = wave1_board.format_summary_report(board, findings, contracts_dir=root)

        assert summary["finding_counts"]["medium"] == 3
        assert summary["finding_kind_counts"] == {
            "handoff_order_warning": 2,
            "stale_ownership": 1,
        }
        assert "Finding kinds: handoff_order_warning=2, stale_ownership=1" in text


def test_summary_report_includes_execution_mirrors_when_task_board_is_supplied():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        board_path = root / "2.7.13.md"
        task_board = root / "TASK-BOARD.json"
        board_path.write_text(fixture_board(registry_status="accepted"), encoding="utf-8")
        write_contract(root, "published-v1.1")
        task_board.write_text(
            json.dumps(
                {
                    "tasks": [
                        {
                            "id": "task-133",
                            "title": "Mirror",
                            "description": "Mirror task.\n\nDurable source: 2.7.13.CA.4.wp.1",
                            "status": "completed",
                            "claimed_by": "Truss",
                            "created_at": "2026-05-28T09:30:00Z",
                            "completed_at": "2026-05-28T09:40:00Z",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

        board = wave1_board.parse_board(board_path)
        findings = wave1_board.collect_findings(
            board,
            contracts_dir=root,
            now=datetime(2026, 5, 28, 7, 30, tzinfo=timezone.utc),
        )
        summary = wave1_board.board_summary_dict(board, findings, contracts_dir=root, task_board_path=task_board)
        text = wave1_board.format_summary_report(board, findings, contracts_dir=root, task_board_path=task_board)

        assert summary["execution_mirrors"][0]["durable_source"] == "2.7.13.CA.4.wp.1"
        assert summary["execution_mirrors"][0]["task_id"] == "task-133"
        assert summary["execution_mirrors"][0]["status"] == "completed"
        assert "2.7.13.CA.4.wp.1: task-133 status=completed" in text


if __name__ == "__main__":
    tests = [
        test_parse_frontmatter_block_lists_and_tables,
        test_contract_registry_desync_and_blocked_chain_are_reported,
        test_accepted_registry_is_compatible_with_published_contract_file,
        test_stale_and_overlapping_edit_locks_are_reported,
        test_case_only_edit_lock_overlap_is_reported_on_windows_workspace,
        test_prose_bearing_edit_lock_overlap_is_reported,
        test_semicolon_edit_lock_targets_are_compared_individually,
        test_report_includes_roster_contracts_and_findings,
        test_handoff_history_filters_by_participant,
        test_malformed_handoff_entries_are_reported,
        test_missing_handoff_message_evidence_is_reported,
        test_missing_roster_last_handoff_message_evidence_is_reported,
        test_non_monotonic_handoff_timestamps_are_reported,
        test_board_status_desync_is_reported_when_publish_action_is_stale,
        test_json_report_exposes_machine_readable_findings,
        test_fail_on_severity_only_fails_at_or_above_threshold,
        test_not_blocked_rows_do_not_create_blocked_chain_findings,
        test_parenthetical_timestamp_note_uses_leading_iso_time,
        test_roster_board_status_desync_is_reported_when_all_blocked_claim_contradicts_active_row,
        test_summary_report_exposes_compact_resume_fields,
        test_summary_report_exposes_finding_kind_counts,
        test_summary_report_includes_execution_mirrors_when_task_board_is_supplied,
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
