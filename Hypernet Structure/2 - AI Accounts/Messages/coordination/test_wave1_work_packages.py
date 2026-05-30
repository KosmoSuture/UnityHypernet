#!/usr/bin/env python3
"""Tests for Wave 1 work-package validation and coordination bridge prep.

Run with:
    cd "2 - AI Accounts/Messages/coordination"
    python -m pytest test_wave1_work_packages.py -v
    # or without pytest:
    python test_wave1_work_packages.py
"""

from __future__ import annotations

import json
import copy
import contextlib
import io
import tempfile
from pathlib import Path

import wave1_work_packages


def valid_wp() -> dict:
    return {
        "wp_id": "wp-3-board-parser",
        "title": "Board parser + status report",
        "description": "Parse 2.7.13 and emit a trustworthy status report",
        "project": "#3",
        "owner": "Truss",
        "status": "in_progress",
        "phase": "v1",
        "blocked_on": ["wp-3-contract-review", "2.7.13.1", "Datum"],
        "files_owned": ["Hypernet Structure/2 - AI Accounts/Messages/coordination/wave1_board.py"],
        "acceptance": [
            "Given the current 2.7.13, report lists every roster row",
            "Detects an injected stale lock",
        ],
        "evidence": [],
        "created_by": "Datum",
        "created_at": "2026-05-28T00:00:00Z",
    }


def test_valid_work_package_maps_to_coordination_create_args():
    wp = valid_wp()
    wp["ha"] = "2.7.13.CA.4.wp.test"
    issues = wave1_work_packages.validate_work_package(wp)
    args = wave1_work_packages.to_coordination_create_args(wp)

    assert issues == []
    assert args["title"].startswith("wp-3-board-parser:")
    assert "Durable source: 2.7.13.CA.4.wp.test" in args["description"]
    assert args["owned_paths"] == wp["files_owned"]
    assert args["depends_on"] == ["wp-3-contract-review"]
    assert args["external_blockers"] == ["2.7.13.1", "Datum"]
    assert args["acceptance_criteria"] == wp["acceptance"]


def test_invalid_work_package_reports_missing_acceptance_and_bad_status():
    wp = valid_wp()
    wp["status"] = "in_review"
    wp["acceptance"] = []

    issues = wave1_work_packages.validate_work_package(wp)

    assert any(issue.field == "status" for issue in issues)
    assert any(issue.field == "acceptance" for issue in issues)


def test_completed_work_package_requires_evidence():
    wp = valid_wp()
    wp["status"] = "completed"
    wp["evidence"] = []

    issues = wave1_work_packages.validate_work_package(wp)

    assert any(issue.field == "evidence" for issue in issues)


def test_required_strings_timestamp_and_acceptance_items_are_not_blank():
    wp = valid_wp()
    wp["title"] = " "
    wp["created_at"] = "not a timestamp"
    wp["acceptance"] = [" "]

    issues = wave1_work_packages.validate_work_package(wp)

    assert any(issue.field == "title" and "blank" in issue.message for issue in issues)
    assert any(issue.field == "created_at" and "ISO" in issue.message for issue in issues)
    assert any(issue.field == "acceptance" and "blank" in issue.message for issue in issues)


def test_empty_owner_is_valid_for_unclaimed_work_packages():
    wp = valid_wp()
    wp["owner"] = ""

    issues = wave1_work_packages.validate_work_package(wp)

    assert not any(issue.field == "owner" for issue in issues)


def test_bridge_preview_json_shape():
    wp = valid_wp()
    preview = wave1_work_packages.bridge_preview(wp)

    assert preview["wp_id"] == "wp-3-board-parser"
    assert preview["validation_issues"] == []
    assert preview["coordination_create_args"]["created_by"] == "Truss"


def test_cli_text_and_json_preview_do_not_write_live_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "wp.json"
        path.write_text(json.dumps(valid_wp()), encoding="utf-8")

        data = json.loads(path.read_text(encoding="utf-8"))
        text = wave1_work_packages.format_text_preview(data)
        preview = wave1_work_packages.bridge_preview(data)

        assert "Validation issues: none" in text
        assert preview["coordination_create_args"]["external_blockers"] == ["2.7.13.1", "Datum"]


def test_duplicate_wp_ids_are_reported_across_package_set():
    first = valid_wp()
    second = copy.deepcopy(first)
    second["title"] = "Different title"

    issues = wave1_work_packages.detect_work_package_conflicts([first, second])

    assert any(issue.field == "wp_id" for issue in issues)


def test_overlapping_files_owned_are_reported_across_package_set():
    first = valid_wp()
    second = copy.deepcopy(valid_wp())
    second["wp_id"] = "wp-3-board-tests"
    second["files_owned"] = ["Hypernet Structure/2 - AI Accounts/Messages/coordination"]

    issues = wave1_work_packages.detect_work_package_conflicts([first, second])

    assert any(issue.field == "files_owned" for issue in issues)


def test_distinct_files_owned_do_not_conflict():
    first = valid_wp()
    second = copy.deepcopy(valid_wp())
    second["wp_id"] = "wp-3-summary"
    second["files_owned"] = ["Hypernet Structure/2 - AI Accounts/2.7 - AI Shared Understanding/2.7.13.CA.md"]

    issues = wave1_work_packages.detect_work_package_conflicts([first, second])

    assert issues == []


def test_case_only_path_overlap_is_reported_on_windows_workspace():
    first = valid_wp()
    second = copy.deepcopy(valid_wp())
    second["wp_id"] = "wp-3-board-parser-case"
    second["files_owned"] = ["hypernet structure/2 - ai accounts/messages/coordination/WAVE1_BOARD.PY"]

    issues = wave1_work_packages.detect_work_package_conflicts([first, second])

    assert any(issue.field == "files_owned" for issue in issues)


def test_dependency_cycles_are_reported_across_package_set():
    first = valid_wp()
    first["wp_id"] = "wp-3-a"
    first["blocked_on"] = ["wp-3-b"]
    second = copy.deepcopy(valid_wp())
    second["wp_id"] = "wp-3-b"
    second["blocked_on"] = ["wp-3-a"]
    second["files_owned"] = ["Hypernet Structure/2 - AI Accounts/Messages/coordination/wave1_bridge_gate.py"]

    issues = wave1_work_packages.detect_work_package_conflicts([first, second])

    assert any(issue.field == "blocked_on" and "Dependency cycle" in issue.message for issue in issues)


def test_package_set_preview_includes_set_conflicts():
    first = valid_wp()
    second = copy.deepcopy(first)

    preview = wave1_work_packages.package_set_preview([first, second])

    assert preview["count"] == 2
    assert preview["summary"]["count"] == 2
    assert preview["packages"][0]["wp_id"] == "wp-3-board-parser"
    assert any(issue["field"] == "wp_id" for issue in preview["set_conflicts"])


def test_package_set_summary_counts_decomposition_fields():
    first = valid_wp()
    second = copy.deepcopy(valid_wp())
    second["wp_id"] = "wp-6-verifier"
    second["project"] = "#6"
    second["owner"] = ""
    second["status"] = "pending"
    second["blocked_on"] = ["wp-3-board-parser", "Datum"]
    second["files_owned"] = ["Hypernet Structure/0/0.1 - Hypernet Core/verifier"]

    summary = wave1_work_packages.package_set_summary([first, second, "not an object"])

    assert summary["count"] == 3
    assert summary["by_project"] == {"#3": 1, "#6": 1}
    assert summary["by_owner"]["Truss"] == 1
    assert summary["by_owner"]["(unclaimed)"] == 1
    assert summary["by_status"] == {"in_progress": 1, "pending": 1}
    assert any(dep["depends_on"] == "wp-3-board-parser" for dep in summary["coordination_dependencies"])
    assert any(blocker["blocked_on"] == "Datum" for blocker in summary["external_blockers"])
    assert summary["invalid_members"] == [2]


def test_text_package_set_reports_conflicts():
    first = valid_wp()
    second = copy.deepcopy(first)

    text = wave1_work_packages.format_text_package_set([first, second])

    assert "Work Package Set: 2 package(s)" in text
    assert "Summary:" in text
    assert "Set conflicts:" in text
    assert "Duplicate wp_id" in text


def test_cli_accepts_package_list_json_without_live_writes():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "wps.json"
        path.write_text(json.dumps([valid_wp()]), encoding="utf-8")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = wave1_work_packages.main([str(path), "--format", "json"])

        payload = json.loads(output.getvalue())
        assert code == 0
        assert payload["count"] == 1
        assert payload["set_conflicts"] == []


def test_scalar_json_reports_validation_error_without_traceback():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "wp.json"
        path.write_text(json.dumps("not an object"), encoding="utf-8")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = wave1_work_packages.main([str(path), "--format", "json"])

        payload = json.loads(output.getvalue())
        assert code == 1
        assert payload["validation_issues"][0]["field"] == "package"


def test_package_list_reports_non_object_member_without_traceback():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "wps.json"
        path.write_text(json.dumps([valid_wp(), "not an object"]), encoding="utf-8")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = wave1_work_packages.main([str(path), "--format", "json"])

        payload = json.loads(output.getvalue())
        assert code == 1
        assert payload["packages"][1]["validation_issues"][0]["field"] == "package"


if __name__ == "__main__":
    tests = [
        test_valid_work_package_maps_to_coordination_create_args,
        test_invalid_work_package_reports_missing_acceptance_and_bad_status,
        test_completed_work_package_requires_evidence,
        test_required_strings_timestamp_and_acceptance_items_are_not_blank,
        test_empty_owner_is_valid_for_unclaimed_work_packages,
        test_bridge_preview_json_shape,
        test_cli_text_and_json_preview_do_not_write_live_state,
        test_duplicate_wp_ids_are_reported_across_package_set,
        test_overlapping_files_owned_are_reported_across_package_set,
        test_distinct_files_owned_do_not_conflict,
        test_case_only_path_overlap_is_reported_on_windows_workspace,
        test_dependency_cycles_are_reported_across_package_set,
        test_package_set_preview_includes_set_conflicts,
        test_package_set_summary_counts_decomposition_fields,
        test_text_package_set_reports_conflicts,
        test_cli_accepts_package_list_json_without_live_writes,
        test_scalar_json_reports_validation_error_without_traceback,
        test_package_list_reports_non_object_member_without_traceback,
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
