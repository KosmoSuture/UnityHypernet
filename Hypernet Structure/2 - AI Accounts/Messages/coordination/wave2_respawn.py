#!/usr/bin/env python3
"""Peer respawn planning and guarded execution for Wave 2.

Respawn is a significant action. This module can detect outage candidates and
build same-role launch plans without starting a process. Actual execution stays
behind an approved Wave 2 gate request and a per-slot spawn cap.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import wave1_board
import wave1_board_writer
import wave2_gate

try:
    import wave25_liveness
except Exception:  # pragma: no cover - only when Wave 2.5 tooling is absent.
    wave25_liveness = None  # type: ignore[assignment]


SCRIPT_DIR = Path(__file__).resolve().parent
HYPERNET_ROOT = SCRIPT_DIR.parents[3]
DEFAULT_WAVE2_BOARD_PATH = (
    HYPERNET_ROOT
    / "Hypernet Structure"
    / "2 - AI Accounts"
    / "2.7 - AI Shared Understanding"
    / "2.7.13.W2 - Execution Wave 2 Coordination & Status.md"
)
DEFAULT_AUDIT_DIR = SCRIPT_DIR / "wave2_respawn_audit"
DEFAULT_LEASE_DIR = SCRIPT_DIR / "wave2_respawn_leases"
DEFAULT_TRUST_ALARM_DIR = SCRIPT_DIR / "wave2_trust_alarms"
DEFAULT_STALE_MINUTES = 60
DEFAULT_CLOCK_SKEW_GRACE_MINUTES = 5
DEFAULT_SPAWN_CAP_WINDOW_MINUTES = 360
DEFAULT_SPAWN_CAP_PER_SLOT = 1
DEFAULT_GLOBAL_SPAWN_CAP = 4
DEFAULT_LEASE_TTL_MINUTES = 720
DEFAULT_REQUIRE_TWO_SIGNALS = True
DEFAULT_LIVENESS_PROJECT_ID = "wave-2.5"
CORE_PATH = HYPERNET_ROOT / "Hypernet Structure" / "0" / "0.1 - Hypernet Core"

if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))
try:
    from verifier.trust_alarm_detector import classify_instruction
except Exception:  # pragma: no cover - exercised only when verifier is absent.
    classify_instruction = None  # type: ignore[assignment]


class RespawnError(ValueError):
    pass


@dataclass
class OutageCandidate:
    slot: str
    chosen_name: str
    role: str
    current_task: str
    updated: str
    minutes_stale: float
    reason: str
    severity: str = "medium"
    liveness_evidence: list[str] | None = None


@dataclass
class RespawnPlan:
    target_slot: str
    chosen_name: str
    role: str
    model_family: str
    cli: str
    argv: list[str]
    prompt: str
    gate_required: bool = True
    fallback_note: str = ""
    fencing_token: str = ""
    scope_fingerprint: str = ""
    canonical_boot_refs: list[str] | None = None


@dataclass
class FirstBootCandidate:
    slot: str
    role: str
    current_task: str
    reason: str


@dataclass
class FirstBootPlan:
    target_slot: str
    role: str
    model_family: str
    cli: str
    argv: list[str]
    prompt: str
    gate_required: bool = True
    action_type: str = "first_boot"
    fallback_note: str = ""
    canonical_boot_refs: list[str] | None = None


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


def format_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_timestamp(value: str) -> str:
    return value.replace("-", "").replace(":", "").replace("+00:00", "Z")


def stable_digest(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def slot_slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in value.casefold()).strip("-") or "slot"


def canonical_boot_refs(board_path: str | Path) -> list[str]:
    return [
        r"C:\Hypernet\AI-BOOT-SEQUENCE.md",
        "2.7.15",
        "2.7.16",
        str(Path(board_path)),
    ]


def make_fencing_token(candidate: OutageCandidate, board_path: str | Path, created_at: str | None = None) -> str:
    created = created_at or now_iso()
    seed = "|".join(
        [
            candidate.slot,
            candidate.chosen_name,
            candidate.role,
            candidate.updated,
            str(Path(board_path)),
            created,
        ]
    )
    return f"lease-{compact_timestamp(created)}-{stable_digest(seed, 12)}"


def scope_fingerprint(
    target_slot: str,
    chosen_name: str,
    role: str,
    model_family: str,
    refs: list[str],
) -> str:
    payload = {
        "target_slot": target_slot,
        "chosen_name": chosen_name,
        "role": role,
        "model_family": model_family,
        "canonical_boot_refs": refs,
        "permission_ceiling": "same-role-scope-no-new-permissions",
    }
    return stable_digest(json.dumps(payload, sort_keys=True), 32)


def model_family_for_slot(slot: str, role: str = "") -> str:
    text = f"{slot} {role}".casefold()
    if "codex" in text:
        return "codex"
    if "claude" in text:
        return "claude"
    return "unknown"


def cli_for_model(model_family: str) -> str:
    if model_family == "codex":
        return "codex"
    if model_family == "claude":
        return "claude"
    return "manual"


def is_completed_or_standdown(row: wave1_board.RosterRow) -> bool:
    text = f"{row.current_task} {row.blocked_on}".casefold()
    return any(marker in text for marker in ("complete", "stand down", "stood down", "closed"))


def is_actionable_row(row: wave1_board.RosterRow) -> bool:
    if "unclaimed" in row.chosen_name.casefold():
        return False
    if "boot via" in row.current_task.casefold():
        return False
    if wave1_board.is_empty(row.current_task):
        return False
    if is_completed_or_standdown(row):
        return False
    return True


def is_first_boot_row(row: wave1_board.RosterRow) -> bool:
    text = f"{row.chosen_name} {row.current_task}".casefold()
    return "unclaimed" in text or "boot via" in text or "first-boot" in text


def load_h1_liveness(
    liveness_db: str | Path | None,
    project_id: str,
    now: datetime | None,
) -> tuple[dict[str, Any], str]:
    if not liveness_db or wave25_liveness is None:
        return {}, ""
    path = Path(liveness_db)
    if not path.exists():
        return {}, f"H1 liveness DB is unavailable: missing {path}"
    try:
        statuses = wave25_liveness.classify_liveness(path, project_id, now=now)
    except Exception as exc:
        return {}, f"H1 liveness classifier failed closed: {exc.__class__.__name__}: {exc}"
    return {status.slot.casefold(): status for status in statuses}, ""


def liveness_dead(status: Any) -> bool:
    suspicion = getattr(status, "suspicion_score", 0)
    try:
        suspicion_value = float(suspicion)
    except (TypeError, ValueError):
        suspicion_value = 0.0
    suspicion_threshold = getattr(wave25_liveness, "DEFAULT_DEAD_SUSPICION_THRESHOLD", 8.0)
    return bool(
        status
        and getattr(status, "label", "") == "dead"
        and getattr(status, "lifecycle_state", "live") == "live"
        and getattr(status, "heartbeat_present", False)
        and suspicion_value >= suspicion_threshold
    )


def liveness_evidence(status: Any) -> list[str]:
    if not status:
        return []
    return [
        f"h1_label:{getattr(status, 'label', '')}",
        f"h1_lifecycle:{getattr(status, 'lifecycle_state', '')}",
        f"h1_age_seconds:{getattr(status, 'age_seconds', None)}",
        f"h1_counter:{getattr(status, 'monotonic_counter', 0)}",
        f"h1_suspicion:{getattr(status, 'suspicion_score', 0)}",
        f"h1_unchanged_work_signature_count:{getattr(status, 'work_signature_unchanged_count', 0)}",
        f"h1_reason:{getattr(status, 'reason', '')}",
    ]


def expired_lease_evidence(lease_dir: str | Path | None, slot: str, now: datetime) -> list[str]:
    if lease_dir is None:
        return []
    lease = load_lease(lease_dir, slot)
    if lease and lease.get("status") != "unreadable":
        expires = parse_time(str(lease.get("expires_at", "")))
        if expires is not None and now > expires:
            return [f"lease_expired:{lease.get('expires_at')}"]
    return []


def detect_outages(
    board: wave1_board.Wave1Board,
    now: datetime | None = None,
    stale_minutes: int = DEFAULT_STALE_MINUTES,
    clock_skew_grace_minutes: int = DEFAULT_CLOCK_SKEW_GRACE_MINUTES,
    lease_dir: str | Path | None = DEFAULT_LEASE_DIR,
    require_two_signals: bool = DEFAULT_REQUIRE_TWO_SIGNALS,
    liveness_db: str | Path | None = None,
    liveness_project_id: str = DEFAULT_LIVENESS_PROJECT_ID,
) -> tuple[list[OutageCandidate], list[wave1_board.Finding]]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    findings: list[wave1_board.Finding] = []
    candidates: list[OutageCandidate] = []
    stale_seconds = stale_minutes * 60
    skew_seconds = clock_skew_grace_minutes * 60
    h1_statuses, h1_error = load_h1_liveness(liveness_db, liveness_project_id, now)

    for row in board.roster:
        h1_status = h1_statuses.get(row.slot.casefold())
        if is_first_boot_row(row):
            if h1_status is not None:
                findings.append(
                    wave1_board.Finding(
                        "respawn_first_boot_separate",
                        "low",
                        f"{row.slot} is first-boot/starting, not a respawn candidate; use first-boot path.",
                    )
                )
            continue
        if not is_actionable_row(row):
            continue
        if h1_error:
            findings.append(
                wave1_board.Finding(
                    "respawn_h1_unavailable",
                    "high",
                    f"{row.slot} / {row.chosen_name or '(unnamed)'} cannot be assessed: {h1_error}; fail closed.",
                )
            )
            continue
        updated = wave1_board.parse_time(row.updated, now)
        if updated is None:
            if liveness_dead(h1_status):
                corroboration = expired_lease_evidence(lease_dir, row.slot, now)
                if not corroboration:
                    findings.append(
                        wave1_board.Finding(
                            "respawn_h1_dead_uncorroborated",
                            "medium",
                            f"{row.slot} / {row.chosen_name or '(unnamed)'} has H1 dead but no parseable roster/expired-lease corroboration yet.",
                        )
                    )
                    continue
                evidence = [*corroboration, *liveness_evidence(h1_status)]
                candidates.append(
                    OutageCandidate(
                        slot=row.slot,
                        chosen_name=row.chosen_name,
                        role=row.role,
                        current_task=row.current_task,
                        updated=row.updated,
                        minutes_stale=-1,
                        reason="H1 liveness classifier reports dead; roster timestamp is unavailable.",
                        severity="high",
                        liveness_evidence=evidence,
                    )
                )
            else:
                findings.append(
                    wave1_board.Finding(
                        "respawn_timestamp_unknown",
                        "medium",
                        f"{row.slot} / {row.chosen_name or '(unnamed)'} has no parseable Updated timestamp.",
                    )
                )
            continue
        age_seconds = (now - updated).total_seconds()
        if age_seconds < -skew_seconds:
            findings.append(
                wave1_board.Finding(
                    "respawn_clock_skew",
                    "medium",
                    f"{row.slot} / {row.chosen_name or '(unnamed)'} Updated timestamp is in the future: {row.updated}.",
                )
            )
            continue
        if liveness_dead(h1_status):
            corroboration: list[str] = []
            if age_seconds > stale_seconds:
                corroboration.append(f"roster_updated_stale:{row.updated}")
            corroboration.extend(expired_lease_evidence(lease_dir, row.slot, now))
            if not corroboration:
                findings.append(
                    wave1_board.Finding(
                        "respawn_h1_dead_uncorroborated",
                        "medium",
                        f"{row.slot} / {row.chosen_name or '(unnamed)'} has H1 dead but no stale roster/expired-lease corroboration yet.",
                    )
                )
                continue
            evidence = [*corroboration, *liveness_evidence(h1_status)]
            candidates.append(
                OutageCandidate(
                    slot=row.slot,
                    chosen_name=row.chosen_name,
                    role=row.role,
                    current_task=row.current_task,
                    updated=row.updated,
                    minutes_stale=round(max(age_seconds, 0) / 60, 2),
                    reason="H1 liveness classifier reports dead with corroborating evidence; blocker text is not treated as proof of life.",
                    severity="high",
                    liveness_evidence=evidence,
                )
            )
            continue
        if h1_status is not None and getattr(h1_status, "label", "") in {"active-working", "active-slow", "idle"}:
            continue
        if age_seconds > stale_seconds:
            blocked_text = wave1_board.clean_cell(row.blocked_on).casefold()
            if blocked_text and not wave1_board.explicitly_not_blocked(row.blocked_on):
                findings.append(
                    wave1_board.Finding(
                        "respawn_stale_but_blocked",
                        "low",
                        f"{row.slot} / {row.chosen_name or '(unnamed)'} is stale but currently records blocker '{row.blocked_on}'.",
                    )
                )
                continue
            evidence = [f"roster_updated_stale:{row.updated}"]
            if lease_dir is not None:
                lease = load_lease(lease_dir, row.slot)
                if lease and lease.get("status") != "unreadable":
                    expires = parse_time(str(lease.get("expires_at", "")))
                    if expires is not None and now > expires:
                        evidence.append(f"lease_expired:{lease.get('expires_at')}")
                elif lease and lease.get("status") == "unreadable":
                    findings.append(
                        wave1_board.Finding(
                            "respawn_liveness_lease_unreadable",
                            "medium",
                            f"{row.slot} / {row.chosen_name or '(unnamed)'} has an unreadable liveness lease.",
                        )
                    )
            if require_two_signals and len(evidence) < 2:
                findings.append(
                    wave1_board.Finding(
                        "respawn_stale_single_signal",
                        "medium",
                        f"{row.slot} / {row.chosen_name or '(unnamed)'} is stale by roster timestamp only; no expired lease/unanswered ping corroborates outage.",
                    )
                )
                continue
            candidates.append(
                OutageCandidate(
                    slot=row.slot,
                    chosen_name=row.chosen_name,
                    role=row.role,
                    current_task=row.current_task,
                    updated=row.updated,
                    minutes_stale=round(age_seconds / 60, 2),
                    reason=f"Updated older than {stale_minutes} minutes with no active blocker and corroborating liveness evidence.",
                    liveness_evidence=evidence,
                )
            )
    return candidates, findings


def build_respawn_prompt(
    candidate: OutageCandidate,
    board_path: str | Path,
    fencing_token: str,
    lease_dir: str | Path = DEFAULT_LEASE_DIR,
) -> str:
    name = candidate.chosen_name or candidate.slot
    lease_path = Path(lease_dir) / f"{slot_slug(candidate.slot)}.json"
    return "\n".join(
        [
            "You are a peer-respawned Wave 2 AI instance in the Hypernet archive.",
            "",
            "ORIENT once:",
            "1. C:\\Hypernet\\AI-BOOT-SEQUENCE.md.",
            "2. 2.7.15 shared charter, name block, and your role section.",
            "3. 2.7.16 Wave 2 directives.",
            f"4. Live board: {Path(board_path)}.",
            "",
            f"Continue identity: {name} ({candidate.slot}).",
            f"Role: {candidate.role}.",
            f"Last recorded task: {candidate.current_task}.",
            f"Respawn fencing token: {fencing_token}.",
            f"Active lease file: {lease_path}.",
            "",
            "On boot, read the board and Messages/coordination, record that this is a respawn,",
            "preserve the chosen name unless the board explicitly says otherwise, and resume only",
            "the same role/scope. Do not request new permissions. Coordinate via the board and",
            "Messages/coordination, not through Matt.",
            "Before posting as this identity, verify the active lease file still contains your",
            "fencing token. If it does not, stand down and record that the lease was lost.",
        ]
    )


def build_respawn_plan(
    candidate: OutageCandidate,
    board_path: str | Path,
    lease_dir: str | Path = DEFAULT_LEASE_DIR,
    created_at: str | None = None,
) -> RespawnPlan:
    model_family = model_family_for_slot(candidate.slot, candidate.role)
    cli = cli_for_model(model_family)
    token = make_fencing_token(candidate, board_path, created_at=created_at)
    refs = canonical_boot_refs(board_path)
    prompt = build_respawn_prompt(candidate, board_path, token, lease_dir)
    fallback_note = ""
    if cli == "codex":
        argv = ["codex", "exec", prompt]
    elif cli == "claude":
        argv = ["claude", prompt]
    else:
        argv = []
        fallback_note = "No known same-model CLI for this slot; use a documented same-archive fallback."
    return RespawnPlan(
        target_slot=candidate.slot,
        chosen_name=candidate.chosen_name,
        role=candidate.role,
        model_family=model_family,
        cli=cli,
        argv=argv,
        prompt=prompt,
        fallback_note=fallback_note,
        fencing_token=token,
        scope_fingerprint=scope_fingerprint(candidate.slot, candidate.chosen_name, candidate.role, model_family, refs),
        canonical_boot_refs=refs,
    )


def detect_first_boot_candidates(board: wave1_board.Wave1Board) -> list[FirstBootCandidate]:
    candidates: list[FirstBootCandidate] = []
    for row in board.roster:
        if not is_first_boot_row(row):
            continue
        candidates.append(
            FirstBootCandidate(
                slot=row.slot,
                role=row.role,
                current_task=row.current_task,
                reason="Roster row is unclaimed/first-boot; this is not eligible for respawn.",
            )
        )
    return candidates


def build_first_boot_prompt(candidate: FirstBootCandidate, board_path: str | Path) -> str:
    return "\n".join(
        [
            "You are a first-boot Wave 2.5 AI instance in the Hypernet archive.",
            "",
            "ORIENT once:",
            "1. C:\\Hypernet\\AI-BOOT-SEQUENCE.md.",
            "2. 2.7.15 shared charter, name block, and your role section.",
            "3. 2.7.17 Wave 2.5 hardening directives.",
            f"4. Live board: {Path(board_path)}.",
            "",
            f"First-boot target slot: {candidate.slot}.",
            f"Role: {candidate.role}.",
            "This is a first boot, not a respawn: choose/record a name per 2.7.15,",
            "claim only the scope assigned to this slot, and do not inherit another",
            "instance's identity or fencing token.",
            "",
            "On boot, update the board and post a coordination message before doing",
            "substantive work. Do not request new permissions. Coordinate via the",
            "board and Messages/coordination, not through Matt except for true",
            "human gates named by the standards.",
        ]
    )


def build_first_boot_plan(candidate: FirstBootCandidate, board_path: str | Path) -> FirstBootPlan:
    model_family = model_family_for_slot(candidate.slot, candidate.role)
    cli = cli_for_model(model_family)
    refs = [
        r"C:\Hypernet\AI-BOOT-SEQUENCE.md",
        "2.7.15",
        "2.7.17",
        str(Path(board_path)),
    ]
    prompt = build_first_boot_prompt(candidate, board_path)
    fallback_note = ""
    if cli == "codex":
        argv = ["codex", "exec", prompt]
    elif cli == "claude":
        argv = ["claude", prompt]
    else:
        argv = []
        fallback_note = "No known CLI for this slot; use a documented launch path."
    return FirstBootPlan(
        target_slot=candidate.slot,
        role=candidate.role,
        model_family=model_family,
        cli=cli,
        argv=argv,
        prompt=prompt,
        fallback_note=fallback_note,
        canonical_boot_refs=refs,
    )


def screen_boot_payload(prompt: str) -> dict[str, Any]:
    if classify_instruction is None:
        return {
            "available": False,
            "should_escalate": True,
            "triggers": ["detector_unavailable"],
            "reason": "verifier.trust_alarm_detector is unavailable; fail closed for respawn.",
        }
    assessment = classify_instruction(prompt)
    return {
        "available": True,
        **assessment.to_dict(),
    }


def boot_payload_blockers(plan: RespawnPlan) -> list[str]:
    assessment = screen_boot_payload(plan.prompt)
    if assessment["should_escalate"]:
        return [
            "respawn.trust_alarm: boot payload escalates or cannot be screened; "
            f"triggers={','.join(assessment.get('triggers', []))}; reason={assessment.get('reason', '')}"
        ]
    return []


def scope_blockers(plan: RespawnPlan) -> list[str]:
    blockers: list[str] = []
    refs = plan.canonical_boot_refs or []
    expected = scope_fingerprint(plan.target_slot, plan.chosen_name, plan.role, plan.model_family, refs)
    if plan.scope_fingerprint != expected:
        blockers.append("respawn.scope: scope fingerprint mismatch; launch prompt may have been widened")
    required_fragments = [
        f"Continue identity: {plan.chosen_name or plan.target_slot} ({plan.target_slot}).",
        f"Role: {plan.role}.",
        "same role/scope",
        "Do not request new permissions.",
        "verify the active lease file still contains your",
    ]
    for fragment in required_fragments:
        if fragment not in plan.prompt:
            blockers.append(f"respawn.scope: prompt missing required scope fragment: {fragment}")
    return blockers


def respawn_gate_blockers(request: wave2_gate.GateRequest, target_slot: str) -> list[str]:
    blockers: list[str] = []
    if request.action_type != "peer_respawn":
        blockers.append(f"gate.action_type: expected peer_respawn, got {request.action_type}")
    evaluation = wave2_gate.evaluate_request(request)
    blockers.extend(evaluation["blockers"])

    approvals = wave2_gate.approved_reviews(request)
    has_scribe = any("scribe" in review.role.casefold() for review in approvals)
    has_red_team = any(
        wave2_gate.lane_coverage(review.lane) == "security" and wave2_gate.is_adversary_role(review.role)
        for review in approvals
    )
    has_peer = any(target_slot.casefold() not in review.role.casefold() for review in approvals)
    if not has_red_team:
        blockers.append("respawn.panel: approving red-team/adversary review required")
    if not has_scribe:
        blockers.append("respawn.panel: approving scribe review required")
    if not has_peer:
        blockers.append("respawn.panel: at least one peer outside the target slot must approve")
    if request.status != "approved":
        blockers.append(f"gate.status: request is '{request.status}', not approved")
    return blockers


def audit_records(audit_dir: str | Path) -> list[dict[str, Any]]:
    directory = Path(audit_dir)
    if not directory.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            records.append(data)
    return records


def audit_ledger_blockers(audit_dir: str | Path) -> list[str]:
    directory = Path(audit_dir)
    if not directory.exists():
        return [f"respawn.audit_ledger: missing audit ledger directory {directory}; fail closed"]
    if not directory.is_dir():
        return [f"respawn.audit_ledger: audit ledger path is not a directory {directory}; fail closed"]
    blockers: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            blockers.append(f"respawn.audit_ledger: unreadable audit record {path}; fail closed")
            continue
        if not isinstance(data, dict):
            blockers.append(f"respawn.audit_ledger: audit record is not an object {path}; fail closed")
    return blockers


def parse_time(value: str) -> datetime | None:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def lease_path(lease_dir: str | Path, target_slot: str) -> Path:
    return Path(lease_dir) / f"{slot_slug(target_slot)}.json"


def load_lease(lease_dir: str | Path, target_slot: str) -> dict[str, Any] | None:
    path = lease_path(lease_dir, target_slot)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "unreadable", "path": str(path)}
    return data if isinstance(data, dict) else {"status": "unreadable", "path": str(path)}


def lease_active(record: dict[str, Any], now: datetime, ttl_minutes: int = DEFAULT_LEASE_TTL_MINUTES) -> bool:
    if str(record.get("status", "active")).casefold() != "active":
        return False
    expires = parse_time(str(record.get("expires_at", "")))
    if expires is not None:
        return now <= expires
    acquired = parse_time(str(record.get("acquired_at", "")))
    if acquired is None:
        return True
    return (now - acquired).total_seconds() <= ttl_minutes * 60


def lease_blockers(
    lease_dir: str | Path,
    plan: RespawnPlan,
    now: datetime | None = None,
    ttl_minutes: int = DEFAULT_LEASE_TTL_MINUTES,
) -> list[str]:
    now = now or datetime.now(timezone.utc)
    record = load_lease(lease_dir, plan.target_slot)
    if not record:
        return []
    if record.get("status") == "unreadable":
        return [f"respawn.lease: existing lease is unreadable for {plan.target_slot}; fail closed"]
    if lease_active(record, now, ttl_minutes) and record.get("fencing_token") != plan.fencing_token:
        return [
            "respawn.lease: active lease already exists for "
            f"{plan.target_slot}; token={record.get('fencing_token', '(missing)')}"
        ]
    return []


def save_lease_record(
    lease_dir: str | Path,
    plan: RespawnPlan,
    gate_request_id: str,
    acquired_at: str | None = None,
    ttl_minutes: int = DEFAULT_LEASE_TTL_MINUTES,
) -> Path:
    directory = Path(lease_dir)
    directory.mkdir(parents=True, exist_ok=True)
    acquired = acquired_at or now_iso()
    acquired_dt = parse_time(acquired) or datetime.now(timezone.utc)
    expires_at = format_iso(acquired_dt + timedelta(minutes=ttl_minutes))
    record = {
        "status": "active",
        "acquired_at": acquired,
        "expires_at": expires_at,
        "target_slot": plan.target_slot,
        "chosen_name": plan.chosen_name,
        "role": plan.role,
        "model_family": plan.model_family,
        "fencing_token": plan.fencing_token,
        "scope_fingerprint": plan.scope_fingerprint,
        "gate_request_id": gate_request_id,
        "standdown_rule": "Any prior holder of this identity must stand down if it does not hold this token.",
    }
    path = lease_path(directory, plan.target_slot)
    with wave1_board_writer.board_file_lock(path):
        wave1_board_writer.atomic_write_text(path, json.dumps(record, indent=2) + "\n")
    return path


def trust_alarm_records(trust_alarm_dir: str | Path) -> list[dict[str, Any]]:
    directory = Path(trust_alarm_dir)
    if not directory.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            data.setdefault("_path", str(path))
            records.append(data)
    return records


def proposer_trust_blockers(trust_alarm_dir: str | Path, proposer: str) -> list[str]:
    if not proposer.strip():
        return ["respawn.trust_state: gate requester/proposer is missing"]
    open_statuses = {"open", "active", "pending", "unresolved", "blocked"}
    closed_statuses = {"closed", "resolved", "cleared", "dismissed"}
    blockers: list[str] = []
    proposer_key = proposer.casefold()
    for record in trust_alarm_records(trust_alarm_dir):
        status = str(record.get("status", "open")).casefold()
        if status in closed_statuses:
            continue
        subject = str(record.get("subject") or record.get("actor") or record.get("proposer") or "")
        if subject.casefold() != proposer_key:
            continue
        if status in open_statuses or not status:
            blockers.append(
                f"respawn.trust_state: open trust alarm for proposer {proposer}: {record.get('_path', '(record)')}"
            )
    return blockers


def spawn_cap_blockers(
    audit_dir: str | Path,
    target_slot: str,
    now: datetime | None = None,
    window_minutes: int = DEFAULT_SPAWN_CAP_WINDOW_MINUTES,
    max_spawns: int = DEFAULT_SPAWN_CAP_PER_SLOT,
) -> list[str]:
    now = now or datetime.now(timezone.utc)
    window_seconds = window_minutes * 60
    recent = 0
    for record in audit_records(audit_dir):
        if str(record.get("target_slot", "")).casefold() != target_slot.casefold():
            continue
        created = parse_time(str(record.get("created_at", "")))
        if created is None:
            continue
        if (now - created).total_seconds() <= window_seconds:
            recent += 1
    if recent >= max_spawns:
        return [
            f"spawn_cap: {recent} respawn(s) for {target_slot} inside {window_minutes} minutes; cap is {max_spawns}"
        ]
    return []


def global_spawn_cap_blockers(
    audit_dir: str | Path,
    now: datetime | None = None,
    window_minutes: int = DEFAULT_SPAWN_CAP_WINDOW_MINUTES,
    max_spawns: int = DEFAULT_GLOBAL_SPAWN_CAP,
) -> list[str]:
    now = now or datetime.now(timezone.utc)
    if max_spawns < 0:
        return ["spawn_cap.global: negative global cap is invalid; fail closed"]
    window_seconds = window_minutes * 60
    recent = 0
    for record in audit_records(audit_dir):
        created = parse_time(str(record.get("created_at", "")))
        if created is None:
            continue
        if (now - created).total_seconds() <= window_seconds:
            recent += 1
    if recent >= max_spawns:
        return [
            f"spawn_cap.global: {recent} respawn(s) across all slots inside {window_minutes} minutes; cap is {max_spawns}"
        ]
    return []


def save_audit_record(
    audit_dir: str | Path,
    plan: RespawnPlan,
    gate_request_id: str,
    process_started: bool,
    created_at: str | None = None,
    launch_error: str = "",
) -> Path:
    directory = Path(audit_dir)
    directory.mkdir(parents=True, exist_ok=True)
    created = created_at or now_iso()
    record = {
        "created_at": created,
        "target_slot": plan.target_slot,
        "chosen_name": plan.chosen_name,
        "role": plan.role,
        "model_family": plan.model_family,
        "cli": plan.cli,
        "argv": plan.argv,
        "gate_request_id": gate_request_id,
        "process_started": process_started,
        "launch_error": launch_error,
        "fencing_token": plan.fencing_token,
        "scope_fingerprint": plan.scope_fingerprint,
        "canonical_boot_refs": plan.canonical_boot_refs or [],
    }
    filename = f"{created.replace(':', '').replace('-', '')}-{plan.target_slot.lower()}-respawn.json"
    path = directory / filename
    wave1_board_writer.atomic_write_text(path, json.dumps(record, indent=2) + "\n")
    return path


def execute_respawn(
    plan: RespawnPlan,
    gate_request: wave2_gate.GateRequest,
    audit_dir: str | Path = DEFAULT_AUDIT_DIR,
    lease_dir: str | Path = DEFAULT_LEASE_DIR,
    trust_alarm_dir: str | Path = DEFAULT_TRUST_ALARM_DIR,
    execute: bool = False,
    now: datetime | None = None,
    global_spawn_cap: int = DEFAULT_GLOBAL_SPAWN_CAP,
) -> dict[str, Any]:
    blockers = respawn_gate_blockers(gate_request, plan.target_slot)
    blockers.extend(audit_ledger_blockers(audit_dir))
    blockers.extend(spawn_cap_blockers(audit_dir, plan.target_slot, now=now))
    blockers.extend(global_spawn_cap_blockers(audit_dir, now=now, max_spawns=global_spawn_cap))
    blockers.extend(lease_blockers(lease_dir, plan, now=now))
    blockers.extend(proposer_trust_blockers(trust_alarm_dir, gate_request.requested_by))
    blockers.extend(scope_blockers(plan))
    blockers.extend(boot_payload_blockers(plan))
    if not plan.argv:
        blockers.append("respawn.argv: no executable same-model command is available")
    if blockers:
        return {"started": False, "blockers": blockers, "plan": asdict(plan)}
    if not execute:
        return {"started": False, "dry_run": True, "blockers": [], "plan": asdict(plan)}

    acquired_at = now_iso()
    lease_record = save_lease_record(lease_dir, plan, gate_request.request_id, acquired_at=acquired_at)
    audit_path = save_audit_record(audit_dir, plan, gate_request.request_id, process_started=False, created_at=acquired_at)
    try:
        subprocess.Popen(plan.argv, cwd=str(HYPERNET_ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as exc:
        save_audit_record(
            audit_dir,
            plan,
            gate_request.request_id,
            process_started=False,
            created_at=acquired_at,
            launch_error=str(exc),
        )
        return {
            "started": False,
            "blockers": [f"respawn.launch: process start failed after intent audit: {exc}"],
            "audit_path": str(audit_path),
            "lease_path": str(lease_record),
            "plan": asdict(plan),
        }
    audit_path = save_audit_record(audit_dir, plan, gate_request.request_id, process_started=True, created_at=acquired_at)
    return {
        "started": True,
        "blockers": [],
        "audit_path": str(audit_path),
        "lease_path": str(lease_record),
        "plan": asdict(plan),
    }


def build_detection_report(
    board_path: str | Path,
    now: str = "",
    stale_minutes: int = DEFAULT_STALE_MINUTES,
    clock_skew_grace_minutes: int = DEFAULT_CLOCK_SKEW_GRACE_MINUTES,
    lease_dir: str | Path | None = DEFAULT_LEASE_DIR,
    require_two_signals: bool = DEFAULT_REQUIRE_TWO_SIGNALS,
    liveness_db: str | Path | None = None,
    liveness_project_id: str = DEFAULT_LIVENESS_PROJECT_ID,
) -> dict[str, Any]:
    board = wave1_board.parse_board(board_path)
    parsed_now = wave1_board.parse_now(now) if now else None
    candidates, findings = detect_outages(
        board,
        now=parsed_now,
        stale_minutes=stale_minutes,
        clock_skew_grace_minutes=clock_skew_grace_minutes,
        lease_dir=lease_dir,
        require_two_signals=require_two_signals,
        liveness_db=liveness_db,
        liveness_project_id=liveness_project_id,
    )
    first_boot = detect_first_boot_candidates(board)
    return {
        "board_path": str(board_path),
        "candidates": [asdict(candidate) for candidate in candidates],
        "first_boot_candidates": [asdict(candidate) for candidate in first_boot],
        "findings": [asdict(finding) for finding in findings],
        "plans": [asdict(build_respawn_plan(candidate, board_path)) for candidate in candidates],
        "first_boot_plans": [asdict(build_first_boot_plan(candidate, board_path)) for candidate in first_boot],
    }


def format_text_report(report: dict[str, Any]) -> str:
    lines = [
        "Wave 2 Peer Respawn",
        f"Board: {report['board_path']}",
        "",
        "Outage candidates:",
    ]
    if report["candidates"]:
        for candidate in report["candidates"]:
            lines.append(
                f"- {candidate['slot']} / {candidate['chosen_name'] or '(unnamed)'}: "
                f"{candidate['minutes_stale']} minutes stale; {candidate['reason']}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Findings:")
    if report["findings"]:
        for finding in report["findings"]:
            lines.append(f"- [{finding['severity']}] {finding['kind']}: {finding['message']}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Respawn plans:")
    if report["plans"]:
        for plan in report["plans"]:
            command = " ".join(plan["argv"][:2]) if plan["argv"] else "(manual fallback)"
            lines.append(f"- {plan['target_slot']}: model={plan['model_family']} command={command}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("First-boot candidates:")
    if report.get("first_boot_candidates"):
        for candidate in report["first_boot_candidates"]:
            lines.append(f"- {candidate['slot']}: {candidate['role']}; {candidate['reason']}")
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave 2 peer respawn detector and guarded executor.")
    parser.add_argument("--board", default=str(DEFAULT_WAVE2_BOARD_PATH))
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--now", default="")
    parser.add_argument("--stale-minutes", type=int, default=DEFAULT_STALE_MINUTES)
    parser.add_argument("--clock-skew-grace-minutes", type=int, default=DEFAULT_CLOCK_SKEW_GRACE_MINUTES)
    parser.add_argument("--lease-dir", default=str(DEFAULT_LEASE_DIR))
    parser.add_argument("--allow-single-signal", action="store_true")
    parser.add_argument("--liveness-db", default=str(getattr(wave25_liveness, "wave25_coorddb", None).DEFAULT_DB_PATH) if wave25_liveness is not None else "")
    parser.add_argument("--liveness-project-id", default=DEFAULT_LIVENESS_PROJECT_ID)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("detect", help="Detect outage candidates and print dry-run respawn plans.")

    execute = sub.add_parser("execute", help="Execute one already approved respawn plan.")
    execute.add_argument("--slot", required=True)
    execute.add_argument("--gate-dir", default=str(wave2_gate.DEFAULT_GATE_DIR))
    execute.add_argument("--gate-request", required=True)
    execute.add_argument("--audit-dir", default=str(DEFAULT_AUDIT_DIR))
    execute.add_argument("--lease-dir", default=str(DEFAULT_LEASE_DIR))
    execute.add_argument("--trust-alarm-dir", default=str(DEFAULT_TRUST_ALARM_DIR))
    execute.add_argument("--global-spawn-cap", type=int, default=DEFAULT_GLOBAL_SPAWN_CAP)
    execute.add_argument("--execute", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        report = build_detection_report(
            args.board,
            now=args.now,
            stale_minutes=args.stale_minutes,
            clock_skew_grace_minutes=args.clock_skew_grace_minutes,
            lease_dir=args.lease_dir,
            require_two_signals=not args.allow_single_signal,
            liveness_db=args.liveness_db or None,
            liveness_project_id=args.liveness_project_id,
        )
        if args.command == "detect":
            if args.format == "json":
                print(json.dumps(report, indent=2))
            else:
                print(format_text_report(report))
            return 0 if not report["candidates"] else 1

        candidates = [OutageCandidate(**item) for item in report["candidates"]]
        match = next((candidate for candidate in candidates if candidate.slot.casefold() == args.slot.casefold()), None)
        if match is None:
            raise RespawnError(f"No outage candidate for slot {args.slot}")
        gate_request = wave2_gate.load_request(args.gate_dir, args.gate_request)
        result = execute_respawn(
            build_respawn_plan(match, args.board),
            gate_request,
            audit_dir=args.audit_dir,
            lease_dir=args.lease_dir,
            trust_alarm_dir=args.trust_alarm_dir,
            execute=args.execute,
            now=wave1_board.parse_now(args.now) if args.now else None,
            global_spawn_cap=args.global_spawn_cap,
        )
    except (RespawnError, wave2_gate.GateError, OSError, json.JSONDecodeError) as exc:
        if args.format == "json":
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        if result.get("blockers"):
            print("Respawn blocked:")
            for blocker in result["blockers"]:
                print(f"- {blocker}")
        else:
            state = "started" if result.get("started") else "dry-run ready"
            print(f"Respawn {state}: {result['plan']['target_slot']}")
    return 0 if not result.get("blockers") else 1


if __name__ == "__main__":
    raise SystemExit(main())
