#!/usr/bin/env python3
"""Preflight the first Wave 1 live task mirror write.

Address: 2.7.13.CA.4. This intentionally does not write TASK-BOARD.json.
It verifies the three gates Datum required for the first live mirror activation:
durable addressed WP source, green bridge gate, and Touchstone ack.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import wave1_board
import wave1_bridge_gate


DEFAULT_ACK_PATH = (
    wave1_board.HYPERNET_ROOT
    / "Hypernet Structure"
    / "2 - AI Accounts"
    / "Messages"
    / "coordination"
    / "2.messages.coordination.2026-05-28-touchstone-verifier-ack-first-live-task-mirror.md"
)


def load_wp(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("First live mirror preflight requires a single WP object.")
    return data


def load_ack_frontmatter(path: str | Path) -> dict[str, Any]:
    ack_path = Path(path)
    frontmatter, _ = wave1_board.parse_frontmatter(ack_path.read_text(encoding="utf-8"))
    return frontmatter


def ack_blockers(wp: dict[str, Any], ack_frontmatter: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    wp_ha = wave1_board.clean_cell(str(wp.get("ha", "")))
    if not wp_ha:
        blockers.append("wp ha: durable WP address is required before checking ack.")
    status = wave1_board.clean_cell(str(ack_frontmatter.get("status", "")))
    if status != "ack-granted":
        blockers.append(f"ack status: expected 'ack-granted', got '{status or '(missing)'}'.")
    subject_wp = wave1_board.clean_cell(str(ack_frontmatter.get("subject_wp", "")))
    if not subject_wp:
        blockers.append("ack subject_wp: missing subject WP address.")
    elif wp_ha and subject_wp != wp_ha:
        blockers.append(f"ack subject_wp: expected '{wp_ha}', got '{subject_wp}'.")
    flags = ack_frontmatter.get("flags", [])
    if isinstance(flags, list) and "first-live-write" not in flags:
        blockers.append("ack flags: missing 'first-live-write'.")
    return blockers


def mirror_status_for_wp(wp: dict[str, Any], task_board_path: str | Path | None = None) -> dict[str, Any]:
    import coordination

    durable_address = wave1_board.clean_cell(str(wp.get("ha", "")))
    path = Path(task_board_path) if task_board_path is not None else coordination.TASK_BOARD_FILE
    data = coordination.load_json(path)
    tasks = data.get("tasks", []) if isinstance(data, dict) else []
    matches = []
    if durable_address:
        for task in tasks:
            description = str(task.get("description", ""))
            if durable_address in description:
                matches.append(
                    {
                        "id": task.get("id", ""),
                        "title": task.get("title", ""),
                        "status": task.get("status", ""),
                        "claimed_by": task.get("claimed_by"),
                        "created_at": task.get("created_at"),
                        "completed_at": task.get("completed_at"),
                    }
                )
    return {
        "task_board_path": str(path),
        "durable_address": durable_address,
        "count": len(matches),
        "matches": matches,
    }


def existing_mirror_blockers(mirror_status: dict[str, Any]) -> list[str]:
    count = int(mirror_status.get("count", 0))
    if count == 0:
        return []
    ids = ", ".join(str(item.get("id", "")) for item in mirror_status.get("matches", []))
    return [
        f"TASK-BOARD already contains {count} task(s) referencing {mirror_status.get('durable_address', '')}: {ids}."
    ]


def build_preflight_report(
    wp_path: str | Path,
    ack_path: str | Path = DEFAULT_ACK_PATH,
    board_path: str | Path = wave1_board.DEFAULT_BOARD_PATH,
    contracts_dir: str | Path = wave1_board.DEFAULT_CONTRACTS_DIR,
    task_board_path: str | Path | None = None,
    now: str = "",
) -> dict[str, Any]:
    wp = load_wp(wp_path)
    ack_frontmatter = load_ack_frontmatter(ack_path)
    gate_report = wave1_bridge_gate.build_gate_report(
        board_path=board_path,
        contracts_dir=contracts_dir,
        wp_path=wp_path,
        now=now,
    )
    ack_errors = ack_blockers(wp, ack_frontmatter)
    mirror_status = mirror_status_for_wp(wp, task_board_path)
    mirror_errors = existing_mirror_blockers(mirror_status)
    blockers = list(gate_report["blockers"]) + ack_errors + mirror_errors
    return {
        "ready_to_execute_first_live_mirror": not blockers,
        "blockers": blockers,
        "wp": {
            "path": str(wp_path),
            "ha": wp.get("ha", ""),
            "wp_id": wp.get("wp_id", ""),
        },
        "ack": {
            "path": str(ack_path),
            "status": ack_frontmatter.get("status", ""),
            "subject_wp": ack_frontmatter.get("subject_wp", ""),
            "blockers": ack_errors,
        },
        "existing_mirrors": mirror_status,
        "gate": gate_report,
        "coordination_create_argv": gate_report.get("coordination_create_argv", []),
        "executed": False,
        "created_task": None,
    }


def execute_first_live_mirror(report: dict[str, Any]) -> dict[str, Any]:
    if not report.get("ready_to_execute_first_live_mirror"):
        blockers = "; ".join(report.get("blockers", [])) or "preflight not ready"
        raise ValueError(f"Cannot execute first live mirror: {blockers}")
    create_args = report["gate"]["work_packages"].get("coordination_create_args")
    if not create_args:
        raise ValueError("Cannot execute first live mirror: missing coordination create args.")

    import coordination

    durable_address = str(report["wp"].get("ha", ""))
    current_board = coordination.load_json(coordination.TASK_BOARD_FILE) or {"tasks": []}
    for task in current_board.get("tasks", []):
        description = str(task.get("description", ""))
        if durable_address and durable_address in description:
            raise ValueError(
                f"Cannot execute first live mirror: TASK-BOARD already contains a task referencing {durable_address}."
            )

    task = coordination.create_task(
        create_args["title"],
        create_args["description"],
        create_args.get("priority", "p1"),
        create_args.get("owned_paths", []),
        create_args.get("depends_on", []),
        create_args.get("created_by", "unknown"),
        create_args.get("acceptance_criteria", []),
    )
    report["executed"] = True
    report["created_task"] = task
    return task


def format_text_report(report: dict[str, Any]) -> str:
    lines = [
        "Wave 1 First Live Mirror Preflight",
        f"ready_to_execute_first_live_mirror: {str(report['ready_to_execute_first_live_mirror']).lower()}",
        f"executed: {str(report.get('executed', False)).lower()}",
        f"wp: {report['wp']['ha']} ({report['wp']['wp_id']})",
        f"ack: {report['ack']['status']} for {report['ack']['subject_wp']}",
        f"existing_mirrors: {report.get('existing_mirrors', {}).get('count', 0)}",
        "",
        "Blockers:",
    ]
    if report["blockers"]:
        for blocker in report["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")
    lines.extend(["", "coordination.py dry-run argv:"])
    commands = report.get("coordination_create_argv", [])
    if commands:
        lines.append(" ".join(commands[0]["argv"]))
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight the first Wave 1 live task mirror write.")
    parser.add_argument("wp_path", help="Path to the addressed durable WP JSON artifact.")
    parser.add_argument("--ack", default=str(DEFAULT_ACK_PATH), help="Path to Touchstone's ack message.")
    parser.add_argument("--board", default=str(wave1_board.DEFAULT_BOARD_PATH))
    parser.add_argument("--contracts-dir", default=str(wave1_board.DEFAULT_CONTRACTS_DIR))
    parser.add_argument("--task-board", default="", help="Optional TASK-BOARD.json path for existing-mirror checks.")
    parser.add_argument("--now", default="")
    parser.add_argument("--format", choices={"text", "json"}, default="text")
    parser.add_argument("--execute", action="store_true", help="Execute the live coordination.py create after preflight passes.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = build_preflight_report(
        wp_path=args.wp_path,
        ack_path=args.ack,
        board_path=args.board,
        contracts_dir=args.contracts_dir,
        task_board_path=args.task_board or None,
        now=args.now,
    )
    if args.execute:
        try:
            execute_first_live_mirror(report)
        except ValueError as exc:
            report["blockers"].append(str(exc))
            report["ready_to_execute_first_live_mirror"] = False
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(format_text_report(report))
    return 0 if report["ready_to_execute_first_live_mirror"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
