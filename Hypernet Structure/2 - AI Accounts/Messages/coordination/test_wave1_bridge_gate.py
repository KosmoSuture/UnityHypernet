#!/usr/bin/env python3
"""Tests for the Wave 1 read-only WP bridge gate.

Run with:
    cd "2 - AI Accounts/Messages/coordination"
    python -m pytest test_wave1_bridge_gate.py -v
    # or without pytest:
    python test_wave1_bridge_gate.py
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
from pathlib import Path

import wave1_bridge_gate


def valid_wp() -> dict:
    return {
        "ha": "2.7.13.CA.4.wp.test",
        "wp_id": "wp-3-board-parser",
        "title": "Board parser + status report",
        "description": "Parse 2.7.13 and emit a trustworthy status report",
        "project": "#3",
        "owner": "Truss",
        "status": "pending",
        "phase": "v1",
        "blocked_on": ["wp-3-contract-review", "2.7.13.1"],
        "files_owned": ["Hypernet Structure/2 - AI Accounts/Messages/coordination/wave1_board.py"],
        "acceptance": ["Report lists every roster row"],
        "evidence": [],
        "created_by": "Datum",
        "created_at": "2026-05-28T00:00:00Z",
    }


def board_fixture(registry_status: str = "published") -> str:
    return f"""---
ha: "2.7.13"
object_type: "coordination_board"
---

# 2.7.13 - Execution Wave 1: Coordination & Status

## BOARD STATUS - READ THIS FIRST

> **CURRENT PHASE:** Wave 1 Execution.
> **WHAT'S HAPPENING NOW:** Contracts are available.
> **NEXT ACTION (Truss):** bridge WPs.
> **HUMAN GATE:** Matt only for true human decisions.

## Instance Roster

| Slot | Chosen Name | Role | Current Task | Blocked-On | Last Handoff | Updated |
|---|---|---|---|---|---|---|
| Codex-A | **Truss** | Collaboration Substrate Engineer | Bridge gate | - | gate start | 2026-05-28T07:20:00Z |

## Interface-Contract Registry

| Contract | Address | Owner | Consumed By | Version | Status |
|---|---|---|---|---|---|
| Collaboration / baton data model + work-package schema | `2.7.13.1` | Datum | Codex-A (#3 + #10) | v1 | {registry_status} |

## Active Edit Locks

| Name | File / Address | Claimed (UTC-ish) | Note |
|---|---|---|---|
| - | - | - | - |

## Handoff Log (append-only)

- **2026-05-28T07:20Z - Datum > Truss** - Contract ready.

---
"""


def write_contract(directory: Path, status: str = "published-v1.1") -> None:
    (directory / "2.7.13.1 - Contract.md").write_text(
        f"""---
ha: "2.7.13.1"
status: "{status}"
---
""",
        encoding="utf-8",
    )


def write_fixture_files(tmpdir: str, registry_status: str = "published", wp_data: object | None = None) -> tuple[Path, Path]:
    root = Path(tmpdir)
    board = root / "board.md"
    wp = root / "wp.json"
    board.write_text(board_fixture(registry_status), encoding="utf-8")
    write_contract(root)
    wp.write_text(json.dumps(valid_wp() if wp_data is None else wp_data), encoding="utf-8")
    return board, wp


def test_gate_allows_clean_board_and_valid_wp_preview():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir)

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is True
        assert report["blockers"] == []
        assert report["readiness_evidence"]["ready"] is True
        assert report["readiness_evidence"]["blockers"] == []
        assert report["coordination_create_argv"][0]["allowed"] is True
        assert report["coordination_create_argv"][0]["argv"][:3] == ["python", "coordination.py", "create"]


def test_gate_allows_slot_name_as_owner_alias():
    wp_data = valid_wp()
    wp_data["owner"] = "Codex-A"
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, wp_data=wp_data)

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is True
        assert report["blockers"] == []


def test_gate_blocks_unknown_wp_owner_before_live_write():
    wp_data = valid_wp()
    wp_data["owner"] = "Unknown-AI"
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, wp_data=wp_data)

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is False
        assert any("owner" in blocker and "Unknown-AI" in blocker for blocker in report["blockers"])
        assert any("Unknown-AI" in blocker for blocker in report["readiness_evidence"]["roster_owner_errors"])
        assert report["coordination_create_argv"][0]["allowed"] is False


def test_gate_blocks_high_severity_board_findings():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, registry_status="drafting")

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is False
        assert any(blocker.startswith("board desync") for blocker in report["blockers"])
        assert report["readiness_evidence"]["board_high_severity_findings"]
        assert report["coordination_create_argv"][0]["allowed"] is False


def test_gate_blocks_wp_without_durable_source_address():
    wp_data = valid_wp()
    del wp_data["ha"]
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, wp_data=wp_data)

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is False
        assert any("durable WP source" in blocker for blocker in report["blockers"])
        assert report["readiness_evidence"]["durable_source_errors"]
        assert report["coordination_create_argv"][0]["allowed"] is False


def test_gate_allows_accepted_registry_with_published_contract_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, registry_status="accepted")

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is True
        assert report["readiness_evidence"]["board_high_severity_findings"] == []
        assert report["blockers"] == []
        assert report["coordination_create_argv"][0]["allowed"] is True


def test_gate_exposes_medium_board_findings_without_blocking():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir)
        board.write_text(
            board_fixture().replace(
                "2026-05-28T07:20:00Z",
                "2026-05-28T05:00:00Z",
            ),
            encoding="utf-8",
        )

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is True
        assert report["blockers"] == []
        assert report["readiness_evidence"]["ready"] is True
        assert any(
            "stale_ownership" in warning
            for warning in report["readiness_evidence"]["board_nonblocking_findings"]
        )
        assert report["coordination_create_argv"][0]["allowed"] is True


def test_gate_blocks_invalid_wp_without_traceback():
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, wp_data="not an object")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = wave1_bridge_gate.main(
                [
                    str(wp),
                    "--board",
                    str(board),
                    "--contracts-dir",
                    tmpdir,
                    "--now",
                    "2026-05-28T07:30:00Z",
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(output.getvalue())
        assert code == 1
        assert payload["ready_to_write_live_tasks"] is False
        assert any("package" in blocker for blocker in payload["blockers"])
        assert payload["readiness_evidence"]["work_package_errors"]
        assert payload["coordination_create_argv"] == []


def test_gate_blocks_comma_bearing_cli_list_items_before_live_write():
    wp_data = valid_wp()
    wp_data["acceptance"] = ["Render argv, but do not split this criterion"]
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, wp_data=wp_data)

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is False
        assert any("acceptance_criteria" in blocker for blocker in report["blockers"])
        assert report["readiness_evidence"]["cli_encoding_errors"]
        assert report["coordination_create_argv"][0]["allowed"] is False


def test_gate_blocks_non_pending_wp_status_before_create_path():
    wp_data = valid_wp()
    wp_data["status"] = "in_progress"
    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, wp_data=wp_data)

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is False
        assert any("would not round-trip" in blocker for blocker in report["blockers"])
        assert report["readiness_evidence"]["live_status_errors"]
        assert report["coordination_create_argv"][0]["allowed"] is False


def test_gate_blocks_wp_dependency_cycles_before_live_write():
    first = valid_wp()
    first["wp_id"] = "wp-3-a"
    first["blocked_on"] = ["wp-3-b"]
    first["files_owned"] = ["Hypernet Structure/2 - AI Accounts/Messages/coordination/a.py"]
    second = copy.deepcopy(valid_wp())
    second["wp_id"] = "wp-3-b"
    second["blocked_on"] = ["wp-3-a"]
    second["files_owned"] = ["Hypernet Structure/2 - AI Accounts/Messages/coordination/b.py"]

    with tempfile.TemporaryDirectory() as tmpdir:
        board, wp = write_fixture_files(tmpdir, wp_data=[first, second])

        report = wave1_bridge_gate.build_gate_report(
            board_path=board,
            contracts_dir=tmpdir,
            wp_path=wp,
            now="2026-05-28T07:30:00Z",
        )

        assert report["ready_to_write_live_tasks"] is False
        assert any("Dependency cycle" in blocker for blocker in report["blockers"])
        assert any("Dependency cycle" in blocker for blocker in report["readiness_evidence"]["work_package_errors"])
        assert report["work_packages"]["set_conflicts"][0]["field"] == "blocked_on"
        assert all(command["allowed"] is False for command in report["coordination_create_argv"])


if __name__ == "__main__":
    tests = [
        test_gate_allows_clean_board_and_valid_wp_preview,
        test_gate_allows_slot_name_as_owner_alias,
        test_gate_blocks_unknown_wp_owner_before_live_write,
        test_gate_blocks_high_severity_board_findings,
        test_gate_blocks_wp_without_durable_source_address,
        test_gate_allows_accepted_registry_with_published_contract_file,
        test_gate_exposes_medium_board_findings_without_blocking,
        test_gate_blocks_invalid_wp_without_traceback,
        test_gate_blocks_comma_bearing_cli_list_items_before_live_write,
        test_gate_blocks_non_pending_wp_status_before_create_path,
        test_gate_blocks_wp_dependency_cycles_before_live_write,
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
