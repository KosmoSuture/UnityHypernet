#!/usr/bin/env python3
"""File-based Significant-Action Gate workflow for Wave 2.

This is tooling, not ratification of the standard itself. It gives the Wave 2
team a shared request/review/decision record that can be used to convene the
required panel and preserve the audit trail before any significant action.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import wave1_board_writer


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_GATE_DIR = SCRIPT_DIR / "wave2_gate_requests"
REQUIRED_REVIEW_LANES = {"quality", "privacy", "security"}
REVIEW_LANES = REQUIRED_REVIEW_LANES | {"red_team"}
REVIEW_VERDICTS = {"approve", "needs_work", "dissent"}
MANDATORY_MIN_ROLES = 3
MANDATORY_MIN_MODEL_FAMILIES = 2
DEFAULT_MIN_ROLES = MANDATORY_MIN_ROLES
DEFAULT_MIN_MODEL_FAMILIES = MANDATORY_MIN_MODEL_FAMILIES


class GateError(ValueError):
    pass


@dataclass
class GateReview:
    reviewer: str
    role: str
    model_family: str
    lane: str
    verdict: str
    notes: str
    reviewed_at: str
    checklist: dict[str, bool] = field(default_factory=dict)


@dataclass
class GateRequest:
    request_id: str
    title: str
    action_type: str
    description: str
    requested_by: str
    created_at: str
    artifacts: list[str] = field(default_factory=list)
    significant_action: bool = True
    status: str = "pending_review"
    min_distinct_roles: int = DEFAULT_MIN_ROLES
    min_model_families: int = DEFAULT_MIN_MODEL_FAMILIES
    requires_red_team: bool = True
    required_lanes: list[str] = field(default_factory=lambda: sorted(REQUIRED_REVIEW_LANES))
    reviews: list[GateReview] = field(default_factory=list)
    audit_log: list[dict[str, str]] = field(default_factory=list)
    decision: dict[str, Any] = field(default_factory=dict)
    gate_record_path: str = ""


def _configure_stream_errors(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


_configure_stream_errors(sys.stdout)
_configure_stream_errors(sys.stderr)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or "gate-request"


def make_request_id(title: str, created_at: str | None = None) -> str:
    timestamp = (created_at or now_iso()).replace("-", "").replace(":", "")
    timestamp = timestamp.replace("+0000", "Z").replace("+00:00", "Z")
    timestamp = re.sub(r"[^0-9TZ]", "", timestamp)
    return f"gate-{timestamp}-{slugify(title)}"


def compact_timestamp(value: str) -> str:
    timestamp = value.replace("-", "").replace(":", "")
    timestamp = timestamp.replace("+0000", "Z").replace("+00:00", "Z")
    return re.sub(r"[^0-9TZ]", "", timestamp)


def audit_event(actor: str, event: str, at: str | None = None) -> dict[str, str]:
    return {"at": at or now_iso(), "actor": actor, "event": event}


def normalize_review(review: GateReview | dict[str, Any]) -> GateReview:
    if isinstance(review, GateReview):
        return review
    return GateReview(
        reviewer=str(review.get("reviewer", "")),
        role=str(review.get("role", "")),
        model_family=str(review.get("model_family", "")),
        lane=str(review.get("lane", "")),
        verdict=str(review.get("verdict", "")),
        notes=str(review.get("notes", "")),
        reviewed_at=str(review.get("reviewed_at", "")),
        checklist={str(k): bool(v) for k, v in dict(review.get("checklist", {})).items()},
    )


def request_to_dict(request: GateRequest) -> dict[str, Any]:
    data = asdict(request)
    data["reviews"] = [asdict(review) for review in request.reviews]
    return data


def request_from_dict(data: dict[str, Any]) -> GateRequest:
    reviews = [normalize_review(review) for review in data.get("reviews", [])]
    return GateRequest(
        request_id=str(data.get("request_id", "")),
        title=str(data.get("title", "")),
        action_type=str(data.get("action_type", "")),
        description=str(data.get("description", "")),
        requested_by=str(data.get("requested_by", "")),
        created_at=str(data.get("created_at", "")),
        artifacts=[str(item) for item in data.get("artifacts", [])],
        significant_action=bool(data.get("significant_action", True)),
        status=str(data.get("status", "pending_review")),
        min_distinct_roles=int(data.get("min_distinct_roles", DEFAULT_MIN_ROLES)),
        min_model_families=int(data.get("min_model_families", DEFAULT_MIN_MODEL_FAMILIES)),
        requires_red_team=bool(data.get("requires_red_team", True)),
        required_lanes=[str(item) for item in data.get("required_lanes", sorted(REQUIRED_REVIEW_LANES))],
        reviews=reviews,
        audit_log=[dict(item) for item in data.get("audit_log", [])],
        decision=dict(data.get("decision", {})),
        gate_record_path=str(data.get("gate_record_path", "")),
    )


def validate_request(request: GateRequest) -> list[str]:
    blockers: list[str] = []
    for field_name in ("request_id", "title", "action_type", "description", "requested_by", "created_at"):
        if not str(getattr(request, field_name)).strip():
            blockers.append(f"request.{field_name}: required")
    for lane in request.required_lanes:
        if lane not in REQUIRED_REVIEW_LANES:
            blockers.append(f"request.required_lanes: unknown lane '{lane}'")
    if request.min_distinct_roles < 1:
        blockers.append("request.min_distinct_roles: must be positive")
    if request.min_model_families < 1:
        blockers.append("request.min_model_families: must be positive")
    return blockers


def validate_review(review: GateReview) -> list[str]:
    blockers: list[str] = []
    for field_name in ("reviewer", "role", "model_family", "lane", "verdict", "reviewed_at"):
        if not str(getattr(review, field_name)).strip():
            blockers.append(f"review.{field_name}: required")
    if review.lane not in REVIEW_LANES:
        blockers.append(f"review.lane: unknown lane '{review.lane}'")
    if review.verdict not in REVIEW_VERDICTS:
        blockers.append(f"review.verdict: unknown verdict '{review.verdict}'")
    return blockers


def approved_reviews(request: GateRequest) -> list[GateReview]:
    return [review for review in request.reviews if review.verdict == "approve"]


def reviewer_key(value: str) -> str:
    return value.strip().casefold()


def lane_coverage(lane: str) -> str:
    return "security" if lane == "red_team" else lane


def is_adversary_role(role: str) -> bool:
    text = role.casefold()
    return "adversary" in text or "2.0.8.2" in text


def effective_min_distinct_roles(request: GateRequest) -> int:
    if request.significant_action:
        return max(MANDATORY_MIN_ROLES, request.min_distinct_roles)
    return request.min_distinct_roles


def effective_min_model_families(request: GateRequest) -> int:
    if request.significant_action:
        return max(MANDATORY_MIN_MODEL_FAMILIES, request.min_model_families)
    return request.min_model_families


def effective_requires_red_team(request: GateRequest) -> bool:
    if request.significant_action:
        return True
    return request.requires_red_team


def effective_required_lanes(request: GateRequest) -> set[str]:
    required = set(request.required_lanes)
    if request.significant_action:
        required |= REQUIRED_REVIEW_LANES
    return required


def evaluate_request(request: GateRequest) -> dict[str, Any]:
    blockers = validate_request(request)
    review_blockers: list[str] = []
    for index, review in enumerate(request.reviews):
        for blocker in validate_review(review):
            review_blockers.append(f"review[{index}] {blocker}")
    blockers.extend(review_blockers)
    min_distinct_roles = effective_min_distinct_roles(request)
    min_model_families = effective_min_model_families(request)
    requires_red_team = effective_requires_red_team(request)
    required_lanes = effective_required_lanes(request)

    reviewer_lanes: dict[str, set[str]] = {}
    reviewer_roles: dict[str, set[str]] = {}
    reviewer_models: dict[str, set[str]] = {}
    reviewer_names: dict[str, str] = {}
    for review in request.reviews:
        key = reviewer_key(review.reviewer)
        if not key:
            continue
        reviewer_names[key] = review.reviewer
        reviewer_lanes.setdefault(key, set()).add(review.lane)
        reviewer_roles.setdefault(key, set()).add(review.role)
        reviewer_models.setdefault(key, set()).add(review.model_family)
    for key, lanes in reviewer_lanes.items():
        if len(lanes) > 1:
            blockers.append(
                f"panel.one_lane_per_reviewer: {reviewer_names[key]} submitted multiple lanes: {', '.join(sorted(lanes))}"
            )
    for key, roles in reviewer_roles.items():
        if len(roles) > 1:
            blockers.append(
                f"panel.reviewer_role_consistency: {reviewer_names[key]} submitted multiple roles: {', '.join(sorted(roles))}"
            )
    for key, models in reviewer_models.items():
        if len(models) > 1:
            blockers.append(
                f"panel.reviewer_model_consistency: {reviewer_names[key]} submitted multiple model families: {', '.join(sorted(models))}"
            )

    approvals = approved_reviews(request)
    dissenting = [review for review in request.reviews if review.verdict in {"needs_work", "dissent"}]
    for review in dissenting:
        blockers.append(
            f"review.{review.reviewer}: verdict '{review.verdict}' must be resolved before approval"
        )

    for review in approvals:
        if reviewer_key(review.reviewer) == reviewer_key(request.requested_by):
            blockers.append(f"panel.independence: author/requester {review.reviewer} cannot approve their own action")

    distinct_reviewers = {reviewer_key(review.reviewer) for review in approvals if review.reviewer.strip()}
    if len(distinct_reviewers) < min_distinct_roles:
        blockers.append(
            f"panel.reviewers: {len(distinct_reviewers)} approving reviewer(s), need {min_distinct_roles}"
        )
    distinct_roles = {review.role.casefold() for review in approvals if review.role.strip()}
    if len(distinct_roles) < min_distinct_roles:
        blockers.append(
            f"panel.roles: {len(distinct_roles)} approval role(s), need {min_distinct_roles}"
        )

    model_families = {review.model_family.casefold() for review in approvals if review.model_family.strip()}
    if len(model_families) < min_model_families:
        blockers.append(
            f"panel.model_families: {len(model_families)} approving model family/families, need {min_model_families}"
        )

    approved_lanes = {lane_coverage(review.lane) for review in approvals}
    missing_lanes = sorted(required_lanes - approved_lanes)
    if missing_lanes:
        blockers.append(f"panel.lanes: missing approval lane(s): {', '.join(missing_lanes)}")

    has_red_team = any(
        lane_coverage(review.lane) == "security" and is_adversary_role(review.role)
        for review in approvals
    )
    if requires_red_team and not has_red_team:
        blockers.append("panel.red_team: security/red-team approval must be from an explicit Adversary")

    ready = not blockers
    return {
        "request_id": request.request_id,
        "status": request.status,
        "ready": ready,
        "blockers": blockers,
        "approval_count": len(approvals),
        "distinct_reviewers": sorted(distinct_reviewers),
        "distinct_roles": sorted(distinct_roles),
        "model_families": sorted(model_families),
        "approved_lanes": sorted(approved_lanes),
        "required_lanes": sorted(required_lanes),
        "min_distinct_roles": min_distinct_roles,
        "min_model_families": min_model_families,
        "requires_red_team": requires_red_team,
    }


def request_path(gate_dir: str | Path, request_id: str) -> Path:
    if not request_id:
        raise GateError("request_id is required")
    return Path(gate_dir) / f"{request_id}.json"


def save_request(gate_dir: str | Path, request: GateRequest) -> Path:
    directory = Path(gate_dir)
    directory.mkdir(parents=True, exist_ok=True)
    if not request.gate_record_path:
        request.gate_record_path = str(default_gate_record_path(directory, request))
    path = request_path(directory, request.request_id)
    wave1_board_writer.atomic_write_text(path, json.dumps(request_to_dict(request), indent=2) + "\n")
    save_markdown_record(request)
    return path


def load_request(gate_dir: str | Path, request_id: str) -> GateRequest:
    path = request_path(gate_dir, request_id)
    if not path.exists():
        raise GateError(f"Gate request not found: {path}")
    return request_from_dict(json.loads(path.read_text(encoding="utf-8")))


def create_request(
    gate_dir: str | Path,
    title: str,
    action_type: str,
    description: str,
    requested_by: str,
    artifacts: list[str] | None = None,
    significant_action: bool = True,
    created_at: str | None = None,
    request_id: str | None = None,
) -> GateRequest:
    created = created_at or now_iso()
    request = GateRequest(
        request_id=request_id or make_request_id(title, created),
        title=title,
        action_type=action_type,
        description=description,
        requested_by=requested_by,
        created_at=created,
        artifacts=artifacts or [],
        significant_action=significant_action,
    )
    request.audit_log.append(audit_event(requested_by, "request_created", created))
    blockers = validate_request(request)
    if blockers:
        raise GateError("; ".join(blockers))
    save_request(gate_dir, request)
    return request


def add_review(
    gate_dir: str | Path,
    request_id: str,
    review: GateReview,
) -> GateRequest:
    blockers = validate_review(review)
    if blockers:
        raise GateError("; ".join(blockers))
    request = load_request(gate_dir, request_id)
    for existing in request.reviews:
        if existing.reviewer.casefold() == review.reviewer.casefold() and existing.lane != review.lane:
            raise GateError(
                f"Reviewer {review.reviewer} already holds lane '{existing.lane}'; one reviewer may hold at most one lane"
            )
    request.reviews = [
        existing
        for existing in request.reviews
        if existing.reviewer.casefold() != review.reviewer.casefold()
    ]
    request.reviews.append(review)
    request.status = "pending_decision"
    request.audit_log.append(audit_event(review.reviewer, f"review_added:{review.lane}:{review.verdict}", review.reviewed_at))
    save_request(gate_dir, request)
    return request


def decide_request(gate_dir: str | Path, request_id: str, decided_by: str, decided_at: str | None = None) -> GateRequest:
    request = load_request(gate_dir, request_id)
    report = evaluate_request(request)
    request.status = "approved" if report["ready"] else "blocked"
    request.decision = {
        "decided_by": decided_by,
        "decided_at": decided_at or now_iso(),
        "approved": report["ready"],
        "blockers": report["blockers"],
    }
    request.audit_log.append(
        audit_event(decided_by, "decision_approved" if report["ready"] else "decision_blocked", request.decision["decided_at"])
    )
    save_request(gate_dir, request)
    return request


def gate_record_dir_for(gate_dir: Path) -> Path:
    if gate_dir.name == "wave2_gate_requests":
        return gate_dir.parent
    return gate_dir


def default_gate_record_path(gate_dir: Path, request: GateRequest) -> Path:
    filename = f"{compact_timestamp(request.created_at)}-gate-{slugify(request.title)}.md"
    return gate_record_dir_for(gate_dir) / filename


def render_markdown_record(request: GateRequest) -> str:
    report = evaluate_request(request)
    lines = [
        "---",
        f"object_type: \"gate_record\"",
        f"request_id: \"{request.request_id}\"",
        f"created: \"{request.created_at}\"",
        f"status: \"{request.status}\"",
        "visibility: \"public\"",
        "---",
        "",
        f"# Gate Record - {request.title}",
        "",
        f"**Action type:** {request.action_type}",
        f"**Requested by:** {request.requested_by}",
        f"**Significant action:** {str(request.significant_action).lower()}",
        f"**JSON mirror:** `wave2_gate_requests/{request.request_id}.json`",
        "",
        "## Description",
        "",
        request.description,
        "",
        "## Artifacts",
        "",
    ]
    if request.artifacts:
        lines.extend(f"- `{artifact}`" for artifact in request.artifacts)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Panel Evaluation",
            "",
            f"- Ready: {str(report['ready']).lower()}",
            f"- Approvals: {report['approval_count']}",
            f"- Distinct reviewers: {', '.join(report['distinct_reviewers']) or '(none)'}",
            f"- Distinct roles: {', '.join(report['distinct_roles']) or '(none)'}",
            f"- Model families: {', '.join(report['model_families']) or '(none)'}",
            f"- Covered lanes: {', '.join(report['approved_lanes']) or '(none)'}",
            "",
            "## Blockers",
            "",
        ]
    )
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    else:
        lines.append("- none")
    lines.extend(["", "## Reviews", ""])
    if request.reviews:
        for review in request.reviews:
            lines.append(
                f"- **{review.reviewed_at} - {review.reviewer} / {review.role} / {review.model_family} "
                f"[{review.lane}] {review.verdict}:** {review.notes}"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Decision", ""])
    if request.decision:
        lines.append(f"- decided_by: {request.decision.get('decided_by', '')}")
        lines.append(f"- decided_at: {request.decision.get('decided_at', '')}")
        lines.append(f"- approved: {str(request.decision.get('approved', False)).lower()}")
    else:
        lines.append("- pending")
    lines.extend(["", "## Audit Log", ""])
    if request.audit_log:
        for event in request.audit_log:
            lines.append(f"- {event.get('at', '')} - {event.get('actor', '')}: {event.get('event', '')}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def save_markdown_record(request: GateRequest) -> None:
    if not request.gate_record_path:
        return
    path = Path(request.gate_record_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    wave1_board_writer.atomic_write_text(path, render_markdown_record(request))


def parse_checklist(values: list[str]) -> dict[str, bool]:
    checklist: dict[str, bool] = {}
    for value in values:
        if "=" not in value:
            raise GateError(f"Checklist item must be key=true/false: {value}")
        key, raw = value.split("=", 1)
        normalized = raw.strip().lower()
        if normalized not in {"true", "false"}:
            raise GateError(f"Checklist value must be true/false: {value}")
        checklist[key.strip()] = normalized == "true"
    return checklist


def format_text(request: GateRequest) -> str:
    report = evaluate_request(request)
    lines = [
        "Wave 2 Significant-Action Gate",
        f"Request: {request.request_id}",
        f"Title: {request.title}",
        f"Action type: {request.action_type}",
        f"Status: {request.status}",
        f"Ready: {str(report['ready']).lower()}",
        "",
        "Panel:",
        f"- approvals: {report['approval_count']}",
        f"- reviewers: {', '.join(report['distinct_reviewers']) or '(none)'}",
        f"- roles: {', '.join(report['distinct_roles']) or '(none)'}",
        f"- model families: {', '.join(report['model_families']) or '(none)'}",
        f"- lanes: {', '.join(report['approved_lanes']) or '(none)'}",
        f"- gate record: {request.gate_record_path or '(missing)'}",
        "",
        "Blockers:",
    ]
    if report["blockers"]:
        lines.extend(f"- {blocker}" for blocker in report["blockers"])
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Reviews:")
    if request.reviews:
        for review in request.reviews:
            lines.append(
                f"- {review.reviewed_at} {review.reviewer} / {review.role} / {review.model_family} "
                f"[{review.lane}] {review.verdict}: {review.notes}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave 2 file-based significant-action gate.")
    parser.add_argument("--gate-dir", default=str(DEFAULT_GATE_DIR))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="Create a gate request.")
    create.add_argument("--title", required=True)
    create.add_argument("--action-type", required=True)
    create.add_argument("--desc", required=True)
    create.add_argument("--by", required=True)
    create.add_argument("--artifact", action="append", default=[])
    create.add_argument("--not-significant", action="store_true")
    create.add_argument("--created-at", default="")
    create.add_argument("--request-id", default="")

    review = sub.add_parser("review", help="Add or replace one reviewer lane.")
    review.add_argument("request_id")
    review.add_argument("--reviewer", required=True)
    review.add_argument("--role", required=True)
    review.add_argument("--model-family", required=True)
    review.add_argument("--lane", required=True, choices=sorted(REVIEW_LANES))
    review.add_argument("--verdict", required=True, choices=sorted(REVIEW_VERDICTS))
    review.add_argument("--notes", default="")
    review.add_argument("--reviewed-at", default="")
    review.add_argument("--check", action="append", default=[])

    status = sub.add_parser("status", help="Show gate request status.")
    status.add_argument("request_id")

    decide = sub.add_parser("decide", help="Record an approval/blocking decision.")
    decide.add_argument("request_id")
    decide.add_argument("--by", required=True)
    decide.add_argument("--decided-at", default="")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "create":
            request = create_request(
                args.gate_dir,
                title=args.title,
                action_type=args.action_type,
                description=args.desc,
                requested_by=args.by,
                artifacts=args.artifact,
                significant_action=not args.not_significant,
                created_at=args.created_at or None,
                request_id=args.request_id or None,
            )
        elif args.command == "review":
            request = add_review(
                args.gate_dir,
                args.request_id,
                GateReview(
                    reviewer=args.reviewer,
                    role=args.role,
                    model_family=args.model_family,
                    lane=args.lane,
                    verdict=args.verdict,
                    notes=args.notes,
                    reviewed_at=args.reviewed_at or now_iso(),
                    checklist=parse_checklist(args.check),
                ),
            )
        elif args.command == "decide":
            request = decide_request(args.gate_dir, args.request_id, args.by, args.decided_at or None)
        else:
            request = load_request(args.gate_dir, args.request_id)
    except GateError as exc:
        if args.format == "json":
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    payload = {"request": request_to_dict(request), "evaluation": evaluate_request(request)}
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(format_text(request))
    if args.command in {"create", "review"}:
        return 0
    return 0 if payload["evaluation"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
