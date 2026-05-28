#!/usr/bin/env python3
"""Read-only gate before Wave 1 WPs are mirrored into live coordination tasks.

Address: 2.7.13.CA.4. This combines the canonical board findings with the
work-package bridge preview and returns a clear yes/no. It never writes
TASK-BOARD.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import wave1_board
import wave1_work_packages


def _configure_stream_errors(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if not callable(reconfigure):
        return
    try:
        reconfigure(errors="replace")
    except (AttributeError, OSError, ValueError):
        pass


def configure_cli_output() -> None:
    _configure_stream_errors(sys.stdout)
    _configure_stream_errors(sys.stderr)


configure_cli_output()


def as_package_list(data: Any) -> list[Any]:
    return data if isinstance(data, list) else [data]


def load_work_package_json(path: str | Path) -> tuple[Any, list[Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data, as_package_list(data)


def work_package_blockers(packages: list[Any]) -> list[str]:
    blockers: list[str] = []
    for index, package in enumerate(packages):
        for issue in wave1_work_packages.validate_work_package(package):
            if issue.severity == "error":
                blockers.append(f"wp[{index}] {issue.field}: {issue.message}")
    for issue in wave1_work_packages.detect_work_package_conflicts(packages):
        if issue.severity == "error":
            blockers.append(f"wp-set {issue.field}: {issue.message}")
    return blockers


def cli_encoding_blockers(packages: list[Any]) -> list[str]:
    """Block argv rendering that would be lossy through coordination.py's CSV flags."""
    blockers: list[str] = []
    list_fields = {
        "owned_paths": "--paths",
        "depends_on": "--depends",
        "acceptance_criteria": "--criteria",
    }
    for index, package in enumerate(packages):
        preview = wave1_work_packages.bridge_preview(package)
        create_args = preview.get("coordination_create_args")
        if not create_args:
            continue
        for field, flag in list_fields.items():
            for item in create_args.get(field, []):
                if "," in item:
                    blockers.append(
                        f"wp[{index}] {field}: item contains a comma, but coordination.py {flag} is comma-separated."
                    )
    return blockers


def board_blockers(findings: list[wave1_board.Finding]) -> list[str]:
    return [
        f"board {finding.kind}: {finding.message}"
        for finding in findings
        if finding.severity == "high"
    ]


def board_nonblocking_warnings(findings: list[wave1_board.Finding]) -> list[str]:
    return [
        f"board {finding.kind}: {finding.message}"
        for finding in findings
        if finding.severity != "high"
    ]


def roster_owner_names(board: wave1_board.Wave1Board) -> set[str]:
    names: set[str] = set()
    for row in board.roster:
        for value in (row.slot, row.chosen_name):
            name = wave1_board.clean_cell(value)
            if name:
                names.add(name.casefold())
    return names


def roster_owner_blockers(board: wave1_board.Wave1Board, packages: list[Any]) -> list[str]:
    valid_owners = roster_owner_names(board)
    blockers: list[str] = []
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            continue
        owner = package.get("owner", "")
        if not isinstance(owner, str) or not wave1_board.clean_cell(owner):
            continue
        if wave1_board.clean_cell(owner).casefold() not in valid_owners:
            blockers.append(f"wp[{index}] owner: '{owner}' is not present in the live board roster.")
    return blockers


def live_status_blockers(packages: list[Any]) -> list[str]:
    blockers: list[str] = []
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            continue
        status = package.get("status", "")
        if isinstance(status, str) and status != "pending":
            blockers.append(
                f"wp[{index}] status: coordination.py create can only mirror pending WPs; status '{status}' would not round-trip."
            )
    return blockers


def build_readiness_evidence(
    board: wave1_board.Wave1Board,
    findings: list[wave1_board.Finding],
    packages: list[Any],
) -> dict[str, Any]:
    evidence = {
        "board_high_severity_findings": board_blockers(findings),
        "board_nonblocking_findings": board_nonblocking_warnings(findings),
        "work_package_errors": work_package_blockers(packages),
        "roster_owner_errors": roster_owner_blockers(board, packages),
        "cli_encoding_errors": cli_encoding_blockers(packages),
        "live_status_errors": live_status_blockers(packages),
    }
    blockers: list[str] = []
    for key in (
        "board_high_severity_findings",
        "work_package_errors",
        "roster_owner_errors",
        "cli_encoding_errors",
        "live_status_errors",
    ):
        blockers.extend(evidence[key])
    evidence["blockers"] = blockers
    evidence["ready"] = not blockers
    return evidence


def coordination_create_argv(create_args: dict[str, Any]) -> list[str]:
    argv = [
        "python",
        "coordination.py",
        "create",
        create_args["title"],
        "--desc",
        create_args["description"],
        "--priority",
        create_args["priority"],
        "--by",
        create_args["created_by"],
    ]
    if create_args.get("owned_paths"):
        argv.extend(["--paths", ",".join(create_args["owned_paths"])])
    if create_args.get("depends_on"):
        argv.extend(["--depends", ",".join(create_args["depends_on"])])
    if create_args.get("acceptance_criteria"):
        argv.extend(["--criteria", ",".join(create_args["acceptance_criteria"])])
    return argv


def command_previews(packages: list[Any], allowed: bool) -> list[dict[str, Any]]:
    previews: list[dict[str, Any]] = []
    for package in packages:
        preview = wave1_work_packages.bridge_preview(package)
        create_args = preview.get("coordination_create_args")
        if not create_args:
            continue
        previews.append(
            {
                "wp_id": preview.get("wp_id", ""),
                "allowed": allowed,
                "argv": coordination_create_argv(create_args),
            }
        )
    return previews


def build_gate_report(
    board_path: str | Path,
    contracts_dir: str | Path,
    wp_path: str | Path,
    now: str = "",
    stale_minutes: int = wave1_board.BOARD_STALENESS_MINUTES,
) -> dict[str, Any]:
    board = wave1_board.parse_board(board_path)
    findings = wave1_board.collect_findings(
        board,
        contracts_dir=contracts_dir,
        now=wave1_board.parse_now(now),
        stale_minutes=stale_minutes,
    )
    wp_data, packages = load_work_package_json(wp_path)
    evidence = build_readiness_evidence(board, findings, packages)
    blockers = list(evidence["blockers"])
    ready = bool(evidence["ready"])
    return {
        "ready_to_write_live_tasks": ready,
        "blockers": blockers,
        "readiness_evidence": evidence,
        "board": {
            "path": str(board.path),
            "findings": [asdict(finding) for finding in findings],
        },
        "work_packages": (
            wave1_work_packages.package_set_preview(packages)
            if isinstance(wp_data, list)
            else wave1_work_packages.bridge_preview(wp_data)
        ),
        "coordination_create_argv": command_previews(packages, ready),
    }


def format_text_report(report: dict[str, Any]) -> str:
    lines = [
        "Wave 1 Bridge Gate",
        f"ready_to_write_live_tasks: {str(report['ready_to_write_live_tasks']).lower()}",
        "",
        "Blockers:",
    ]
    if report["blockers"]:
        for blocker in report["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")

    lines.extend(["", "Board findings:"])
    findings = report["board"]["findings"]
    if findings:
        for finding in findings:
            lines.append(f"- [{finding['severity']}] {finding['kind']}: {finding['message']}")
    else:
        lines.append("- none")

    wp_preview = report["work_packages"]
    if "count" in wp_preview:
        lines.extend(["", f"Work packages: {wp_preview['count']}"])
        conflicts = wp_preview.get("set_conflicts", [])
        if conflicts:
            lines.append("Set conflicts:")
            for issue in conflicts:
                lines.append(f"- [{issue['severity']}] {issue['field']}: {issue['message']}")
    else:
        lines.extend(["", f"Work package: {wp_preview.get('wp_id') or '(invalid)'}"])
        issues = wp_preview.get("validation_issues", [])
        if issues:
            lines.append("Validation issues:")
            for issue in issues:
                lines.append(f"- [{issue['severity']}] {issue['field']}: {issue['message']}")
    lines.extend(["", "coordination.py dry-run argv:"])
    commands = report.get("coordination_create_argv", [])
    if commands:
        for command in commands:
            allowed = "allowed" if command["allowed"] else "blocked"
            lines.append(f"- {command['wp_id']} ({allowed}): {json.dumps(command['argv'], ensure_ascii=False)}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gate read-only WP bridge previews against the live Wave 1 board.")
    parser.add_argument("wp_path", help="Path to one WP JSON object or a list of WPs")
    parser.add_argument("--board", default=str(wave1_board.DEFAULT_BOARD_PATH), help="Path to 2.7.13 board markdown")
    parser.add_argument("--contracts-dir", default=str(wave1_board.DEFAULT_CONTRACTS_DIR), help="Directory containing contract markdown files")
    parser.add_argument("--now", default="", help="Override current time for stale checks (ISO 8601)")
    parser.add_argument("--stale-minutes", type=int, default=wave1_board.BOARD_STALENESS_MINUTES)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = build_gate_report(
        board_path=args.board,
        contracts_dir=args.contracts_dir,
        wp_path=args.wp_path,
        now=args.now,
        stale_minutes=args.stale_minutes,
    )
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(format_text_report(report))
    return 0 if report["ready_to_write_live_tasks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
