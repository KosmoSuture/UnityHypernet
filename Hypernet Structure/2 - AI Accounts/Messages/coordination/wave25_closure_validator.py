#!/usr/bin/env python3
"""Wave 2.5 H6 closure-record validator.

This module validates an already-parsed H6 closure record. It intentionally has
no DB, network, or filesystem dependency so Touchstone's closure meta-test can
exercise the closure rules as a pure function.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


VALID_STATES = {"full", "best-effort", "incomplete", "fully-blocked"}
PRESENT_H1_LABELS = {"active-working", "active-slow", "idle", "stale-warning"}
NO_REMAINING_WORK_MARKERS = (
    "pass",
    "complete",
    "closed",
    "concur",
    "no remaining",
    "nothing useful remains",
)
REMAINING_WORK_MARKERS = (
    "revise",
    "not pass",
    "incomplete",
    "blocked",
    "work remains",
    "remaining work remains",
    "remaining work:",
    "todo",
    "pending",
    "open blocker",
    "blocker remains",
)


@dataclass
class ClosureValidationResult:
    valid: bool
    violations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _casefold(value: Any) -> str:
    return str(value or "").strip().casefold()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _parse_bool(value: Any) -> bool:
    return _casefold(value) in {"true", "yes", "1"}


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    raw = value.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        return [_strip_scalar(raw)] if raw else []
    inner = raw[1:-1].strip()
    if not inner:
        return []
    return [_strip_scalar(item) for item in inner.split(",") if item.strip()]


def _frontmatter(markdown: str) -> dict[str, Any]:
    normalized = markdown.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return {}
    end = normalized.find("\n---", 4)
    if end == -1:
        return {}
    frontmatter: dict[str, Any] = {}
    for line in normalized[4:end].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("["):
            frontmatter[key.strip()] = _parse_inline_list(value)
        elif _casefold(value) in {"true", "false"}:
            frontmatter[key.strip()] = _parse_bool(value)
        else:
            frontmatter[key.strip()] = _strip_scalar(value)
    return frontmatter


def _table_after_heading(markdown: str, heading_pattern: str) -> list[list[str]]:
    lines = markdown.replace("\r\n", "\n").splitlines()
    start = -1
    for index, line in enumerate(lines):
        if re.search(heading_pattern, line, re.IGNORECASE):
            start = index + 1
            break
    if start == -1:
        return []
    table_lines: list[str] = []
    for line in lines[start:]:
        if line.startswith("|"):
            table_lines.append(line)
        elif table_lines:
            break
    rows: list[list[str]] = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        rows.append(cells)
    if len(rows) <= 1:
        return []
    return rows


def _freshness_from_cell(value: str) -> str:
    folded = _casefold(value)
    if "standing" in folded:
        return "standing"
    if "fresh" in folded:
        return "fresh"
    return folded


def parse_markdown_closure_record(markdown: str) -> dict[str, Any]:
    """Parse the constrained H6 §3 closure-record Markdown shape."""
    frontmatter = _frontmatter(markdown)
    record: dict[str, Any] = {
        "_frontmatter": frontmatter,
        "_raw_markdown": markdown,
        "closure_state": frontmatter.get("closure_state", ""),
        "reopenable": frontmatter.get("reopenable", True),
        "declared_by": _as_list(frontmatter.get("declared_by")),
        "corroborated_by": _as_list(frontmatter.get("corroborated_by")),
        "lanes": [],
        "residuals": [],
        "decision_basis": {"gated_action_present": True},
    }

    lane_rows = _table_after_heading(markdown, r"lane positions")
    for cells in lane_rows[1:]:
        if len(cells) < 7:
            continue
        record["lanes"].append(
            {
                "lane": cells[0],
                "instance": cells[1],
                "model": cells[2],
                "position": cells[3],
                "evidence": cells[4],
                "freshness": _freshness_from_cell(cells[5]),
                "as_of": cells[6],
            }
        )

    residual_rows = _table_after_heading(markdown, r"named residuals")
    for cells in residual_rows[1:]:
        if len(cells) < 6:
            continue
        record["residuals"].append(
            {
                "id": cells[0],
                "residual": cells[1],
                "severity": cells[2],
                "owner": cells[3],
                "reopen_condition": cells[4],
                "own_gated_action": "yes" in _casefold(cells[5]) or "true" in _casefold(cells[5]),
            }
        )
    return record


def _distinct_names(values: list[Any]) -> set[str]:
    return {_casefold(value) for value in values if _casefold(value)}


def _lanes(record: dict[str, Any]) -> list[dict[str, Any]]:
    lanes = record.get("lanes", [])
    return [lane for lane in lanes if isinstance(lane, dict)]


def _lane_name(lane: dict[str, Any]) -> str:
    return _casefold(lane.get("lane"))


def _lane_by_name(record: dict[str, Any], lane_name: str) -> dict[str, Any] | None:
    target = _casefold(lane_name)
    for lane in _lanes(record):
        if _lane_name(lane) == target:
            return lane
    return None


def _freshness(lane: dict[str, Any]) -> str:
    return _casefold(lane.get("freshness"))


def _position_names_no_work(lane: dict[str, Any]) -> bool:
    position = _casefold(lane.get("position"))
    if any(marker in position for marker in REMAINING_WORK_MARKERS):
        return False
    if any(marker in position for marker in NO_REMAINING_WORK_MARKERS):
        return True
    return False


def _full_record_has_draft_markers(record: dict[str, Any]) -> bool:
    frontmatter = record.get("_frontmatter", {})
    if not isinstance(frontmatter, dict):
        frontmatter = {}
    if "draft" in _casefold(frontmatter.get("ha")):
        return True
    if "draft" in _casefold(frontmatter.get("status")):
        return True

    raw = _casefold(record.get("_raw_markdown"))
    stale_phrases = (
        "## next (to finalize)",
        "truss + meridian post h6 seats",
        "record finalizes (full/best-effort)",
        "this record finalizes",
        "finalizes on h6",
    )
    return any(phrase in raw for phrase in stale_phrases)


def _is_contradicted(lane: dict[str, Any], context: dict[str, Any]) -> bool:
    if bool(lane.get("contradicted")):
        return True
    lane_key = _lane_name(lane)
    instance_key = _casefold(lane.get("instance"))
    contradicted = {_casefold(value) for value in _as_list(context.get("contradicted_lanes"))}
    contradicted_instances = {
        _casefold(value) for value in _as_list(context.get("contradicted_instances"))
    }
    return lane_key in contradicted or instance_key in contradicted_instances


def _is_fresh_or_valid_standing(lane: dict[str, Any], context: dict[str, Any]) -> bool:
    freshness = _freshness(lane)
    if freshness == "fresh":
        return True
    if freshness == "standing" and not _is_contradicted(lane, context):
        return True
    return False


def _adversary_instances(record: dict[str, Any], context: dict[str, Any]) -> set[str]:
    names = _distinct_names(_as_list(context.get("adversary_instances")))
    adversary_lane_name = _casefold(context.get("adversary_lane"))
    for lane in _lanes(record):
        lane_text = _lane_name(lane)
        position_text = _casefold(lane.get("position"))
        if lane_text == adversary_lane_name or "adversary" in lane_text or "red-team" in lane_text:
            names.add(_casefold(lane.get("instance")))
        elif "adversary" in position_text or "red-team" in position_text:
            names.add(_casefold(lane.get("instance")))
    names.discard("")
    return names


def _is_adversary_instance(instance: Any, record: dict[str, Any], context: dict[str, Any]) -> bool:
    return _casefold(instance) in _adversary_instances(record, context)


def _gated_action_present(record: dict[str, Any], context: dict[str, Any], violations: list[str]) -> bool:
    basis = record.get("decision_basis", {})
    if not isinstance(basis, dict):
        basis = {}
    explicit = basis.get("gated_action_present")
    cleared_by = basis.get("adversary_cleared_no_gated_action_by")

    if explicit is True:
        return True
    if cleared_by:
        if _is_adversary_instance(cleared_by, record, context):
            return False
        violations.append("V2-SELF-CLEARED")
        return True
    return True


def validate_closure_record(
    record: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> ClosureValidationResult:
    """Validate a parsed H6 closure record.

    The caller supplies context that is intentionally not part of the durable
    record, such as chartered lanes, H1 labels, and later contradictions.
    """

    context = context or {}
    violations: list[str] = []
    state = _casefold(record.get("closure_state"))
    if state not in VALID_STATES:
        violations.append("V0-UNKNOWN-STATE")

    declared_by = _distinct_names(_as_list(record.get("declared_by")))
    corroborated_by = _distinct_names(_as_list(record.get("corroborated_by")))

    if state in {"incomplete", "fully-blocked"}:
        if not declared_by:
            violations.append("V1-PESSIMISM")
    elif state == "best-effort":
        if len(declared_by | corroborated_by) < 2:
            violations.append("V1-BEST-EFFORT-QUORUM")
    elif state == "full":
        for project_lane in _as_list(context.get("project_lanes")):
            lane = _lane_by_name(record, str(project_lane))
            if lane is None or not _is_fresh_or_valid_standing(lane, context):
                violations.append("V1-FULL-INCOMPLETE")
                break
            if not _position_names_no_work(lane):
                violations.append("V1-FULL-INCOMPLETE")
                break

    for lane in _lanes(record):
        if _freshness(lane) == "standing" and _is_contradicted(lane, context):
            violations.append("V4-STALE-STANDING")
            break

    if state in {"full", "best-effort"}:
        gated = _gated_action_present(record, context, violations)
        if gated:
            adversary_lane_name = context.get("adversary_lane")
            adversary_lane = _lane_by_name(record, str(adversary_lane_name)) if adversary_lane_name else None
            if adversary_lane is None:
                violations.append("V2-ABSENT-ADVERSARY")
            elif not _is_fresh_or_valid_standing(adversary_lane, context):
                violations.append("V2-ABSENT-ADVERSARY")

    if state == "full":
        if _full_record_has_draft_markers(record):
            violations.append("V6-FULL-DRAFT-MARKER")

        h1_labels = {
            _casefold(instance): _casefold(label)
            for instance, label in dict(context.get("h1_labels", {})).items()
        }
        for lane in _lanes(record):
            if _freshness(lane) != "standing":
                continue
            instance = _casefold(lane.get("instance"))
            if h1_labels.get(instance) not in PRESENT_H1_LABELS:
                violations.append("V3-UNREACHABLE-FULL")
                break

        if _as_list(record.get("residuals")) and record.get("reopenable") is False:
            violations.append("V5-UNREOPENABLE-WITH-RESIDUALS")

    ordered = []
    seen = set()
    for violation in violations:
        if violation not in seen:
            ordered.append(violation)
            seen.add(violation)
    return ClosureValidationResult(valid=not ordered, violations=ordered)


def parse_context_args(args: argparse.Namespace, record: dict[str, Any]) -> dict[str, Any]:
    h1_labels: dict[str, str] = {}
    for item in args.h1_label:
        if "=" in item:
            name, label = item.split("=", 1)
            h1_labels[name.strip()] = label.strip()
    project_lanes = args.project_lane or [str(lane.get("lane", "")) for lane in _lanes(record)]
    return {
        "project_lanes": project_lanes,
        "adversary_lane": args.adversary_lane,
        "adversary_instances": args.adversary_instance,
        "h1_labels": h1_labels,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an H6 closure record.")
    parser.add_argument("--closure-record", required=True)
    parser.add_argument("--project-lane", action="append", default=[])
    parser.add_argument("--adversary-lane", default="Adversary")
    parser.add_argument("--adversary-instance", action="append", default=["Touchstone"])
    parser.add_argument("--h1-label", action="append", default=[], help="Instance=label")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    markdown = Path(args.closure_record).read_text(encoding="utf-8")
    record = parse_markdown_closure_record(markdown)
    context = parse_context_args(args, record)
    result = validate_closure_record(record, context)
    payload = {
        "valid": result.valid,
        "violations": result.violations,
        "closure_state": record.get("closure_state"),
        "lane_count": len(_lanes(record)),
        "residual_count": len(_as_list(record.get("residuals"))),
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        verdict = "PASS" if result.valid else "FAIL"
        print(f"{verdict}: state={payload['closure_state']} lanes={payload['lane_count']} violations={result.violations}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
