#!/usr/bin/env python3
"""Validate Wave 1 work-packages and map them to coordination.py task inputs.

This module is the first `2.7.13.CA.4` bridge slice. It is intentionally pure:
it does not write TASK-BOARD.json or acquire live task claims. The goal is to make
Datum's work-package schema mechanically checkable before any state-writing bridge
exists.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


TASK_STATUSES = {"pending", "claimed", "in_progress", "completed", "failed", "blocked"}
WAVE1_PROJECTS = {"#1", "#2", "#3", "#6"}
REQUIRED_FIELDS = {
    "wp_id",
    "title",
    "description",
    "project",
    "owner",
    "status",
    "phase",
    "blocked_on",
    "files_owned",
    "acceptance",
    "evidence",
    "created_by",
    "created_at",
}
LIST_FIELDS = {"blocked_on", "files_owned", "acceptance", "evidence"}


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


@dataclass
class ValidationIssue:
    severity: str
    field: str
    message: str


def is_isoish_timestamp(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_work_package(data: Any) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    if not isinstance(data, dict):
        return [ValidationIssue("error", "package", "Work package must be a JSON object.")]

    for field in sorted(REQUIRED_FIELDS):
        if field not in data:
            issues.append(ValidationIssue("error", field, f"Missing required field '{field}'."))

    for field in LIST_FIELDS:
        if field in data and not isinstance(data[field], list):
            issues.append(ValidationIssue("error", field, f"Field '{field}' must be a list."))
        elif field in data and any(not isinstance(item, str) for item in data[field]):
            issues.append(ValidationIssue("error", field, f"Field '{field}' must contain only strings."))

    for field in ("wp_id", "title", "description", "project", "owner", "status", "phase", "created_by", "created_at"):
        if field in data and not isinstance(data[field], str):
            issues.append(ValidationIssue("error", field, f"Field '{field}' must be a string."))

    for field in ("wp_id", "title", "description", "project", "status", "phase", "created_by", "created_at"):
        if field in data and isinstance(data[field], str) and not data[field].strip():
            issues.append(ValidationIssue("error", field, f"Field '{field}' must not be blank."))

    wp_id = data.get("wp_id")
    if isinstance(wp_id, str) and not wp_id.startswith("wp-"):
        issues.append(ValidationIssue("error", "wp_id", "Field 'wp_id' must start with 'wp-'."))

    project = data.get("project")
    if isinstance(project, str) and project not in WAVE1_PROJECTS:
        issues.append(ValidationIssue("error", "project", f"Project '{project}' is not a Wave 1 project."))

    status = data.get("status")
    if isinstance(status, str) and status not in TASK_STATUSES:
        issues.append(ValidationIssue("error", "status", f"Status '{status}' is not a valid TaskStatus value."))

    acceptance = data.get("acceptance")
    if isinstance(acceptance, list) and not acceptance:
        issues.append(ValidationIssue("error", "acceptance", "Acceptance criteria are required before a WP can be real work."))
    elif isinstance(acceptance, list) and any(isinstance(item, str) and not item.strip() for item in acceptance):
        issues.append(ValidationIssue("error", "acceptance", "Acceptance criteria must not be blank."))

    created_at = data.get("created_at")
    if isinstance(created_at, str) and created_at.strip() and not is_isoish_timestamp(created_at):
        issues.append(ValidationIssue("error", "created_at", "Field 'created_at' must be an ISO-ish timestamp."))

    evidence = data.get("evidence")
    if status == "completed" and isinstance(evidence, list) and not evidence:
        issues.append(ValidationIssue("error", "evidence", "Completed WPs must include evidence links or paths."))

    return issues


def split_blockers(blocked_on: list[str]) -> tuple[list[str], list[str]]:
    """Return (coordination_dependencies, external_blockers).

    `coordination.py` task dependencies are task-like IDs. Contract addresses and
    instance names stay external so the bridge does not pretend the active task
    board can satisfy them.
    """
    coordination_deps: list[str] = []
    external: list[str] = []
    for item in blocked_on:
        if item.startswith("wp-") or item.startswith("task-"):
            coordination_deps.append(item)
        else:
            external.append(item)
    return coordination_deps, external


def overlaps_path(left: str, right: str) -> bool:
    left = left.replace("\\", "/").rstrip("/").casefold()
    right = right.replace("\\", "/").rstrip("/").casefold()
    if not left or not right:
        return False
    if left == right:
        return True
    return left.startswith(f"{right}/") or right.startswith(f"{left}/")


def detect_work_package_conflicts(packages: list[Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen_ids: dict[str, int] = {}
    file_claims: list[tuple[str, str, int]] = []
    package_ids: set[str] = set()
    dependency_graph: dict[str, list[str]] = {}

    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            continue
        wp_id = package.get("wp_id", f"(index {index})")
        if isinstance(wp_id, str):
            if wp_id in seen_ids:
                issues.append(
                    ValidationIssue(
                        "error",
                        "wp_id",
                        f"Duplicate wp_id '{wp_id}' in packages {seen_ids[wp_id]} and {index}.",
                    )
                )
            else:
                seen_ids[wp_id] = index
                package_ids.add(wp_id)

        files_owned = package.get("files_owned", [])
        if not isinstance(files_owned, list):
            continue
        for path in files_owned:
            if not isinstance(path, str):
                continue
            for existing_path, existing_wp_id, existing_index in file_claims:
                if overlaps_path(path, existing_path):
                    issues.append(
                        ValidationIssue(
                            "error",
                            "files_owned",
                            f"WP '{wp_id}' (index {index}) overlaps owned path '{path}' with WP '{existing_wp_id}' (index {existing_index}) path '{existing_path}'.",
                        )
                    )
            file_claims.append((path, str(wp_id), index))

    for package in packages:
        if not isinstance(package, dict):
            continue
        wp_id = package.get("wp_id")
        blocked_on = package.get("blocked_on", [])
        if not isinstance(wp_id, str) or not isinstance(blocked_on, list):
            continue
        dependency_graph[wp_id] = [
            dep for dep in blocked_on if isinstance(dep, str) and dep.startswith("wp-") and dep in package_ids
        ]

    for cycle in dependency_cycles(dependency_graph):
        issues.append(
            ValidationIssue(
                "error",
                "blocked_on",
                f"Dependency cycle: {' -> '.join(cycle)}.",
            )
        )

    return issues


def dependency_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    seen_cycle_keys: set[tuple[str, ...]] = set()
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def cycle_key(cycle: list[str]) -> tuple[str, ...]:
        body = cycle[:-1]
        rotations = [tuple(body[idx:] + body[:idx]) for idx in range(len(body))]
        return min(rotations)

    def visit(node: str) -> None:
        if node in visiting:
            start = stack.index(node)
            cycle = stack[start:] + [node]
            key = cycle_key(cycle)
            if key not in seen_cycle_keys:
                seen_cycle_keys.add(key)
                cycles.append(cycle)
            return
        if node in visited:
            return

        visiting.add(node)
        stack.append(node)
        for dep in graph.get(node, []):
            visit(dep)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    return cycles


def increment_count(counts: dict[str, int], value: Any, fallback: str = "(missing)") -> None:
    key = value.strip() if isinstance(value, str) and value.strip() else fallback
    counts[key] = counts.get(key, 0) + 1


def package_set_summary(packages: list[Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "count": len(packages),
        "by_project": {},
        "by_owner": {},
        "by_status": {},
        "files_owned": [],
        "coordination_dependencies": [],
        "external_blockers": [],
        "invalid_members": [],
    }
    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            summary["invalid_members"].append(index)
            continue

        wp_id = package.get("wp_id") if isinstance(package.get("wp_id"), str) else f"(index {index})"
        increment_count(summary["by_project"], package.get("project"))
        increment_count(summary["by_owner"], package.get("owner"), fallback="(unclaimed)")
        increment_count(summary["by_status"], package.get("status"))

        files_owned = package.get("files_owned", [])
        if isinstance(files_owned, list):
            for path in files_owned:
                if isinstance(path, str):
                    summary["files_owned"].append({"wp_id": wp_id, "path": path})

        blocked_on = package.get("blocked_on", [])
        if isinstance(blocked_on, list):
            coordination_deps, external_blockers = split_blockers(
                [item for item in blocked_on if isinstance(item, str)]
            )
            for dep in coordination_deps:
                summary["coordination_dependencies"].append({"wp_id": wp_id, "depends_on": dep})
            for blocker in external_blockers:
                summary["external_blockers"].append({"wp_id": wp_id, "blocked_on": blocker})

    return summary


def build_description(data: dict[str, Any], external_blockers: list[str]) -> str:
    lines = [
        data["description"],
        "",
        f"WP: {data['wp_id']}",
        f"Project: {data['project']}",
        f"Phase: {data['phase']}",
    ]
    durable_address = data.get("ha")
    if isinstance(durable_address, str) and durable_address.strip():
        lines.append(f"Durable source: {durable_address.strip()}")
    if external_blockers:
        lines.append(f"External blockers: {', '.join(external_blockers)}")
    return "\n".join(lines)


def to_coordination_create_args(data: dict[str, Any]) -> dict[str, Any]:
    issues = validate_work_package(data)
    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        messages = "; ".join(f"{issue.field}: {issue.message}" for issue in errors)
        raise ValueError(f"Invalid work package: {messages}")

    coordination_deps, external_blockers = split_blockers(data.get("blocked_on", []))
    return {
        "title": f"{data['wp_id']}: {data['title']}",
        "description": build_description(data, external_blockers),
        "priority": "p1",
        "owned_paths": list(data.get("files_owned", [])),
        "depends_on": coordination_deps,
        "created_by": data.get("owner") or data.get("created_by") or "unknown",
        "acceptance_criteria": list(data.get("acceptance", [])),
        "external_blockers": external_blockers,
    }


def bridge_preview(data: Any) -> dict[str, Any]:
    issues = validate_work_package(data)
    if issues or not isinstance(data, dict):
        return {
            "wp_id": data.get("wp_id", "") if isinstance(data, dict) else "",
            "validation_issues": [asdict(issue) for issue in issues],
            "coordination_create_args": None,
        }
    return {
        "wp_id": data.get("wp_id", ""),
        "validation_issues": [],
        "coordination_create_args": to_coordination_create_args(data),
    }


def package_set_preview(packages: list[Any]) -> dict[str, Any]:
    return {
        "count": len(packages),
        "summary": package_set_summary(packages),
        "packages": [bridge_preview(package) for package in packages],
        "set_conflicts": [asdict(issue) for issue in detect_work_package_conflicts(packages)],
    }


def format_text_preview(data: Any) -> str:
    issues = validate_work_package(data)
    lines = [f"Work Package: {data.get('wp_id', '(missing)') if isinstance(data, dict) else '(invalid)'}"]
    if issues:
        lines.append("Validation issues:")
        for issue in issues:
            lines.append(f"- [{issue.severity}] {issue.field}: {issue.message}")
        return "\n".join(lines)

    args = to_coordination_create_args(data)
    lines.extend(
        [
            "Validation issues: none",
            "coordination.py create_task preview:",
            f"- title: {args['title']}",
            f"- owned_paths: {', '.join(args['owned_paths']) or '(none)'}",
            f"- depends_on: {', '.join(args['depends_on']) or '(none)'}",
            f"- external_blockers: {', '.join(args['external_blockers']) or '(none)'}",
            f"- acceptance_criteria: {len(args['acceptance_criteria'])}",
        ]
    )
    return "\n".join(lines)


def format_text_package_set(packages: list[Any]) -> str:
    conflicts = detect_work_package_conflicts(packages)
    summary = package_set_summary(packages)
    lines = [f"Work Package Set: {len(packages)} package(s)"]
    lines.extend(
        [
            "Summary:",
            f"- by_project: {json.dumps(summary['by_project'], ensure_ascii=False, sort_keys=True)}",
            f"- by_owner: {json.dumps(summary['by_owner'], ensure_ascii=False, sort_keys=True)}",
            f"- by_status: {json.dumps(summary['by_status'], ensure_ascii=False, sort_keys=True)}",
            f"- files_owned: {len(summary['files_owned'])}",
            f"- coordination_dependencies: {len(summary['coordination_dependencies'])}",
            f"- external_blockers: {len(summary['external_blockers'])}",
        ]
    )
    for package in packages:
        lines.append("")
        lines.append(format_text_preview(package))
    lines.append("")
    lines.append("Set conflicts:")
    if conflicts:
        for issue in conflicts:
            lines.append(f"- [{issue.severity}] {issue.field}: {issue.message}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Wave 1 work-package JSON.")
    parser.add_argument("path", help="Path to a JSON file containing one work-package object or a list of work-packages")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    packages = data if isinstance(data, list) else [data]
    issues = []
    for package in packages:
        issues.extend(validate_work_package(package))
    issues.extend(detect_work_package_conflicts(packages))

    if args.format == "json":
        payload = package_set_preview(packages) if isinstance(data, list) else bridge_preview(data)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(format_text_package_set(packages) if isinstance(data, list) else format_text_preview(data))
    return 1 if any(issue.severity == "error" for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
