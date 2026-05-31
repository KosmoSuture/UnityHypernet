#!/usr/bin/env python3
"""Hierarchical project rollup tooling for Wave 2.

The Wave 1 board proved one live coordination surface. This module generalizes
the same primitives to node-local project lists that aggregate upward and feed an
agent pull loop. It is intentionally file-based and dry-run friendly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import wave1_board_writer
import wave1_work_packages


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_CHANNEL_ROLE = "projects.work-queue"
DEFAULT_PROJECT_SLOT = "N.0.3"
PROJECT_SLOT_RATIONALE = (
    "Bind project rollups to the logical channel role 'projects.work-queue'. "
    "The physical N.0.x slot remains pending Matt's channel-order ruling; N.0.3 is "
    "the current 2.7.3 synthesis recommendation, not a ratified constant."
)
PROJECT_STATUSES = {"pending", "claimed", "in_progress", "blocked", "completed", "cancelled", "failed"}
PRIORITY_RANK = {"p0": 0, "p1": 1, "p2": 2, "p3": 3}
PRIORITY_BUCKET = {"p0": "critical", "p1": "high", "p2": "medium", "p3": "low"}
BUCKET_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "someday": 4}
DEFAULT_PROJECT_GLOBS = ("*.projects.json", "*0.2*.json", "project-rollup.json")
VISIBILITY_RANK = {"public": 0, "restricted": 1, "private": 2}
ROLLUP_VISIBILITIES = {"inherit", "redacted"}
DEFAULT_AUDIENCE_VISIBILITY = "public"
DEFAULT_CLAIM_LEASE_MINUTES = 360
DEFAULT_STARVATION_DAYS = 14
DEFAULT_CHANNEL_REGISTRY = {
    PROJECT_CHANNEL_ROLE: {
        "slot": DEFAULT_PROJECT_SLOT,
        "binding_status": "provisional_pending_matt_ruling",
        "rationale": PROJECT_SLOT_RATIONALE,
    }
}
SIGNIFICANT_ACTION_PATTERNS = (
    (
        "publication",
        re.compile(
            r"\b(git\s+push|push(?:ing)?\b.{0,80}\b(public|github|repo|repository)|"
            r"commit(?:ting)?\b.{0,80}\b(public|github|repo|repository)|"
            r"publish(?:ing)?\b.{0,80}\b(public|external|github|repo|repository))\b",
            re.IGNORECASE,
        ),
    ),
    (
        "external_access",
        re.compile(
            r"\b(grant|authorize|enable|request)\b.{0,80}\b(access|permission|permissions|oauth|token|credential)\b|"
            r"\b(gmail|dropbox|google\s+drive|oauth|api\s+key|external\s+service)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "spawn",
        re.compile(r"\b(peer[- ]?respawn|respawn|spawn|start\s+new\s+instance|launch\s+new\s+ai)\b", re.IGNORECASE),
    ),
    (
        "destructive",
        re.compile(r"\b(force[- ]?push|reset\s+--hard|delete|destroy|purge|wipe|drop\s+table|migrate)\b", re.IGNORECASE),
    ),
)
SIGNIFICANT_PATH_PATTERNS = (
    ("publication", re.compile(r"(^|[\\/])\.git([\\/]|$)|\.gitignore$", re.IGNORECASE)),
    ("external_access", re.compile(r"\b(oauth|token|credential|secret|gmail|dropbox|api[-_ ]?key)\b", re.IGNORECASE)),
)


class RollupError(ValueError):
    pass


@dataclass
class ProjectRecord:
    project_id: str
    title: str
    description: str
    priority: str = "p1"
    status: str = "pending"
    node: str = ""
    roles: list[str] = field(default_factory=list)
    personality_tags: list[str] = field(default_factory=list)
    files_owned: list[str] = field(default_factory=list)
    blocked_on: list[str] = field(default_factory=list)
    acceptance: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    significant_action: bool = False
    created_at: str = ""
    visibility: str = "public"
    rollup_visibility: str = "inherit"
    public_summary: str = ""
    redacted: bool = False
    redaction_reason: str = ""
    updated_at: str = ""
    claimed_by: str = ""
    claimed_at: str = ""
    claim_expires_at: str = ""
    claim_lease: dict[str, str] = field(default_factory=dict)
    global_id: str = ""
    source_path: str = ""


@dataclass
class ProjectList:
    node: str
    slot: str
    channel_role: str
    visibility: str
    content_hash: str
    path: str
    projects: list[ProjectRecord]


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


def project_slot_recommendation(channel_registry: dict[str, Any] | None = None) -> dict[str, str]:
    return resolve_channel_binding(channel_registry)


def normalize_visibility(value: Any, field_name: str) -> str:
    visibility = str(value or "public").strip().casefold()
    if visibility not in VISIBILITY_RANK:
        raise RollupError(f"{field_name}: unknown visibility '{value}'")
    return visibility


def normalize_rollup_visibility(value: Any) -> str:
    policy = str(value or "inherit").strip().casefold()
    if policy not in ROLLUP_VISIBILITIES:
        raise RollupError(f"rollup_visibility: unknown value '{value}'")
    return policy


def resolve_channel_binding(
    channel_registry: dict[str, Any] | None = None,
    channel_role: str = PROJECT_CHANNEL_ROLE,
) -> dict[str, str]:
    registry = channel_registry or DEFAULT_CHANNEL_REGISTRY
    channels = registry.get("channels", registry) if isinstance(registry, dict) else {}
    raw = channels.get(channel_role, {}) if isinstance(channels, dict) else {}
    if isinstance(raw, str):
        raw = {"slot": raw}
    if not isinstance(raw, dict):
        raw = {}
    default = DEFAULT_CHANNEL_REGISTRY[PROJECT_CHANNEL_ROLE]
    slot = str(raw.get("slot") or default["slot"])
    return {
        "role": channel_role,
        "slot": slot,
        "binding_status": str(raw.get("binding_status") or default["binding_status"]),
        "rationale": str(raw.get("rationale") or default["rationale"]),
    }


def clean_node(value: str) -> str:
    return value.strip().strip(".")


def is_descendant_or_self(parent: str, candidate: str) -> bool:
    parent = clean_node(parent)
    candidate = clean_node(candidate)
    return candidate == parent or candidate.startswith(f"{parent}.")


def parse_time(value: str) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def claim_lease_expiry(acquired_at: str, lease_minutes: int = DEFAULT_CLAIM_LEASE_MINUTES) -> str:
    acquired = parse_time(acquired_at)
    if acquired == datetime.min.replace(tzinfo=timezone.utc):
        acquired = datetime.now(timezone.utc)
    return iso_z(acquired + timedelta(minutes=lease_minutes))


def project_claim_expires_at(project: ProjectRecord) -> str:
    return project.claim_expires_at or str(project.claim_lease.get("expires_at", ""))


def project_claim_expired(project: ProjectRecord, now: datetime | None = None) -> bool:
    expires_at = project_claim_expires_at(project)
    if not expires_at:
        return False
    now = now or datetime.now(timezone.utc)
    return parse_time(expires_at) <= now


def project_claim_expired_dict(project: dict[str, Any], now: datetime | None = None) -> bool:
    lease = project.get("claim_lease", {})
    expires_at = str(project.get("claim_expires_at", ""))
    if isinstance(lease, dict):
        expires_at = expires_at or str(lease.get("expires_at", ""))
    if not expires_at:
        return False
    now = now or datetime.now(timezone.utc)
    return parse_time(expires_at) <= now


def source_content_hash(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_content_hash_ref(
    path: str,
    visibility: str,
    audience_visibility: str,
    digest: str | None = None,
) -> str:
    digest = digest or source_content_hash(path)
    if visibility_allows_cleartext(visibility, audience_visibility):
        return digest
    return f"redacted-content:{stable_digest(f'{path}:{digest}', 32)}"


def normalize_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise RollupError(f"{field_name}: must be a list")
    if any(not isinstance(item, str) for item in value):
        raise RollupError(f"{field_name}: must contain only strings")
    return list(value)


def normalize_project(
    data: dict[str, Any],
    list_node: str,
    source_path: Path,
    list_visibility: str = "public",
) -> ProjectRecord:
    for field_name in ("project_id", "title", "description"):
        if not isinstance(data.get(field_name), str) or not data[field_name].strip():
            raise RollupError(f"{field_name}: required")
    priority = str(data.get("priority", "p1"))
    if priority not in PRIORITY_RANK:
        raise RollupError(f"priority: unknown value '{priority}'")
    status = str(data.get("status", "pending"))
    if status not in PROJECT_STATUSES:
        raise RollupError(f"status: unknown value '{status}'")
    node = str(data.get("node") or list_node).strip()
    visibility = normalize_visibility(data.get("visibility", list_visibility), "visibility")
    rollup_visibility = normalize_rollup_visibility(data.get("rollup_visibility", "inherit"))
    return ProjectRecord(
        project_id=data["project_id"].strip(),
        title=data["title"].strip(),
        description=data["description"].strip(),
        priority=priority,
        status=status,
        node=node,
        roles=normalize_string_list(data.get("roles", []), "roles"),
        personality_tags=normalize_string_list(data.get("personality_tags", []), "personality_tags"),
        files_owned=normalize_string_list(data.get("files_owned", []), "files_owned"),
        blocked_on=normalize_string_list(data.get("blocked_on", []), "blocked_on"),
        acceptance=normalize_string_list(data.get("acceptance", []), "acceptance"),
        evidence=normalize_string_list(data.get("evidence", []), "evidence"),
        significant_action=bool(data.get("significant_action", False)),
        created_at=str(data.get("created_at", "")),
        visibility=visibility,
        rollup_visibility=rollup_visibility,
        public_summary=str(data.get("public_summary", "")),
        redacted=bool(data.get("redacted", False)),
        redaction_reason=str(data.get("redaction_reason", "")),
        updated_at=str(data.get("updated_at", "")),
        claimed_by=str(data.get("claimed_by", "")),
        claimed_at=str(data.get("claimed_at", "")),
        claim_expires_at=str(data.get("claim_expires_at", "")),
        claim_lease=dict(data.get("claim_lease", {})) if isinstance(data.get("claim_lease", {}), dict) else {},
        global_id=str(data.get("global_id", "")),
        source_path=str(source_path),
    )


def load_project_list(path: str | Path) -> ProjectList:
    source_path = Path(path)
    raw = source_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise RollupError(f"{source_path}: project list must be a JSON object")
    node = str(data.get("node", "")).strip()
    if not node:
        raise RollupError(f"{source_path}: node is required")
    visibility = normalize_visibility(data.get("visibility", "public"), "visibility")
    channel_role = str(data.get("channel_role", PROJECT_CHANNEL_ROLE) or PROJECT_CHANNEL_ROLE)
    slot = str(data.get("slot", ""))
    raw_projects = data.get("projects", [])
    if not isinstance(raw_projects, list):
        raise RollupError(f"{source_path}: projects must be a list")
    projects = [
        normalize_project(project, node, source_path, visibility)
        for project in raw_projects
        if isinstance(project, dict)
    ]
    if len(projects) != len(raw_projects):
        raise RollupError(f"{source_path}: every project entry must be an object")
    return ProjectList(
        node=node,
        slot=slot,
        channel_role=channel_role,
        visibility=visibility,
        content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        path=str(source_path),
        projects=projects,
    )


def discover_project_lists(root: str | Path) -> list[Path]:
    root_path = Path(root)
    paths: set[Path] = set()
    for pattern in DEFAULT_PROJECT_GLOBS:
        paths.update(path for path in root_path.rglob(pattern) if path.is_file())
    candidates: list[Path] = []
    for path in sorted(paths):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("projects"), list):
            candidates.append(path)
    return candidates


def dedupe_key(project: ProjectRecord) -> str:
    if project.global_id:
        return f"global:{project.global_id.casefold()}"
    return f"{project.node.casefold()}:{project.project_id.casefold()}"


def choose_project(existing: ProjectRecord, candidate: ProjectRecord) -> ProjectRecord:
    existing_time = parse_time(existing.updated_at)
    candidate_time = parse_time(candidate.updated_at)
    if candidate_time > existing_time:
        return candidate
    if candidate_time == existing_time and PRIORITY_RANK[candidate.priority] < PRIORITY_RANK[existing.priority]:
        return candidate
    return existing


def project_start_time(project: ProjectRecord) -> datetime:
    return parse_time(project.created_at or project.updated_at)


def priority_bucket_for(
    project: ProjectRecord,
    compiled_at: str,
    starvation_days: int = DEFAULT_STARVATION_DAYS,
) -> tuple[str, bool]:
    if project.status in {"completed", "cancelled", "failed"}:
        return "someday", False
    base_bucket = PRIORITY_BUCKET[project.priority]
    start = project_start_time(project)
    now = parse_time(compiled_at)
    if start == datetime.min.replace(tzinfo=timezone.utc) or now == datetime.min.replace(tzinfo=timezone.utc):
        return base_bucket, False
    if project.status == "pending" and (now - start).days >= starvation_days:
        promoted_rank = max(0, BUCKET_RANK[base_bucket] - 1)
        for bucket, rank in BUCKET_RANK.items():
            if rank == promoted_rank:
                return bucket, bucket != base_bucket
    return base_bucket, False


def visibility_allows_cleartext(record_visibility: str, audience_visibility: str) -> bool:
    return VISIBILITY_RANK[record_visibility] <= VISIBILITY_RANK[audience_visibility]


def most_restrictive_visibility(*values: str) -> str:
    normalized = [normalize_visibility(value, "visibility") for value in values if value]
    if not normalized:
        return "public"
    return max(normalized, key=lambda item: VISIBILITY_RANK[item])


def ancestor_nodes(root_node: str, node: str) -> list[str]:
    root = clean_node(root_node)
    candidate = clean_node(node)
    if not root or not candidate or not is_descendant_or_self(root, candidate):
        return []
    root_parts = root.split(".")
    candidate_parts = candidate.split(".")
    return [".".join(candidate_parts[:index]) for index in range(len(root_parts), len(candidate_parts) + 1)]


def effective_visibility_for(
    project: ProjectRecord,
    root_node: str,
    list_node: str,
    node_visibility: dict[str, str],
) -> str:
    visibilities = [project.visibility]
    for node in ancestor_nodes(root_node, list_node):
        visibilities.append(node_visibility.get(node, "public"))
    for node in ancestor_nodes(root_node, project.node):
        visibilities.append(node_visibility.get(node, "public"))
    return most_restrictive_visibility(*visibilities)


def stable_digest(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def source_ref(path: str, visibility: str, audience_visibility: str) -> str:
    if visibility_allows_cleartext(visibility, audience_visibility):
        return path
    return f"redacted-source:{stable_digest(path)}"


def project_is_count_only(project: ProjectRecord, audience_visibility: str, effective_visibility: str | None = None) -> bool:
    visibility = effective_visibility or project.visibility
    return visibility == "private" and not visibility_allows_cleartext(visibility, audience_visibility)


def project_should_redact(
    project: ProjectRecord,
    audience_visibility: str,
    effective_visibility: str | None = None,
) -> bool:
    if project.redacted:
        return True
    if project.rollup_visibility == "redacted":
        return True
    visibility = effective_visibility or project.visibility
    if project_is_count_only(project, audience_visibility, visibility):
        return False
    return not visibility_allows_cleartext(visibility, audience_visibility)


def redacted_project_dict(
    project: ProjectRecord,
    audience_visibility: str,
    effective_visibility: str | None = None,
) -> dict[str, Any]:
    visibility = effective_visibility or project.visibility
    opaque_id = f"redacted-project:{stable_digest(project.global_id or f'{project.node}:{project.project_id}:{project.source_path}')}"
    return {
        "project_id": project.global_id or opaque_id,
        "title": "[restricted]",
        "description": "[restricted]",
        "priority": project.priority,
        "status": project.status,
        "node": "[redacted]",
        "roles": list(project.roles),
        "personality_tags": list(project.personality_tags),
        "files_owned": [],
        "blocked_on": [],
        "acceptance": [],
        "evidence": [],
        "significant_action": bool(project.significant_action),
        "visibility": project.visibility,
        "effective_visibility": visibility,
        "rollup_visibility": project.rollup_visibility,
        "public_summary": "",
        "redacted": True,
        "redaction_reason": project.redaction_reason
        or f"visibility:{visibility}:audience:{audience_visibility}",
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "claimed_by": "",
        "claimed_at": "",
        "claim_expires_at": "",
        "claim_lease": {},
        "global_id": "",
        "source_path": "",
    }


def project_to_rollup_dict(
    project: ProjectRecord,
    audience_visibility: str,
    effective_visibility: str | None = None,
) -> dict[str, Any] | None:
    visibility = effective_visibility or project.visibility
    if project_is_count_only(project, audience_visibility, visibility):
        return None
    if project_should_redact(project, audience_visibility, visibility):
        return redacted_project_dict(project, audience_visibility, visibility)
    data = asdict(project)
    data["effective_visibility"] = visibility
    return data


def compile_rollup(
    root_node: str,
    lists: list[ProjectList],
    generated_at: str | None = None,
    channel_registry: dict[str, Any] | None = None,
    audience_visibility: str = DEFAULT_AUDIENCE_VISIBILITY,
) -> dict[str, Any]:
    audience_visibility = normalize_visibility(audience_visibility, "audience_visibility")
    compiled_at = generated_at or now_iso()
    channel_binding = resolve_channel_binding(channel_registry)
    by_key: dict[str, ProjectRecord] = {}
    effective_visibility_by_key: dict[str, str] = {}
    duplicates: list[dict[str, str]] = []
    included_sources: set[str] = set()
    source_visibility: dict[str, str] = {}
    source_hashes: dict[str, str] = {}
    node_visibility: dict[str, str] = {}
    for project_list in lists:
        node_visibility[project_list.node] = most_restrictive_visibility(
            node_visibility.get(project_list.node, "public"),
            project_list.visibility,
        )
    for project_list in lists:
        if not is_descendant_or_self(root_node, project_list.node):
            continue
        included_sources.add(project_list.path)
        source_hashes[project_list.path] = project_list.content_hash
        list_visibility = most_restrictive_visibility(
            project_list.visibility,
            *(node_visibility.get(node, "public") for node in ancestor_nodes(root_node, project_list.node)),
        )
        source_visibility[project_list.path] = list_visibility
        for project in project_list.projects:
            if not is_descendant_or_self(root_node, project.node):
                continue
            key = dedupe_key(project)
            effective_visibility = effective_visibility_for(project, root_node, project_list.node, node_visibility)
            if key in by_key:
                kept = choose_project(by_key[key], project)
                dropped = project if kept is by_key[key] else by_key[key]
                duplicates.append(
                    {
                        "key": key,
                        "kept": kept.source_path,
                        "dropped": dropped.source_path,
                    }
                )
                by_key[key] = kept
                effective_visibility_by_key[key] = most_restrictive_visibility(
                    effective_visibility_by_key.get(key, "public"),
                    effective_visibility,
                )
            else:
                by_key[key] = project
                effective_visibility_by_key[key] = effective_visibility

    projects = sorted(
        by_key.values(),
        key=lambda item: (PRIORITY_RANK[item.priority], item.status, item.node, item.project_id),
    )
    by_priority: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_bucket: dict[str, int] = {}
    bucket_by_key: dict[str, str] = {}
    escalated_by_key: dict[str, bool] = {}
    for project in projects:
        by_priority[project.priority] = by_priority.get(project.priority, 0) + 1
        by_status[project.status] = by_status.get(project.status, 0) + 1
        bucket, escalated = priority_bucket_for(project, compiled_at)
        by_bucket[bucket] = by_bucket.get(bucket, 0) + 1
        key = dedupe_key(project)
        bucket_by_key[key] = bucket
        escalated_by_key[key] = escalated
    rollup_projects: list[dict[str, Any]] = []
    redacted_count = 0
    private_count_only = 0
    for project in projects:
        key = dedupe_key(project)
        effective_visibility = effective_visibility_by_key.get(key, project.visibility)
        item = project_to_rollup_dict(project, audience_visibility, effective_visibility)
        if item is None:
            private_count_only += 1
            continue
        item["priority_bucket"] = bucket_by_key.get(key, PRIORITY_BUCKET[project.priority])
        item["starvation_escalated"] = escalated_by_key.get(key, False)
        if item.get("redacted"):
            redacted_count += 1
        rollup_projects.append(item)
    duplicate_reports = []
    for duplicate in duplicates:
        kept = duplicate["kept"]
        dropped = duplicate["dropped"]
        kept_ref = source_ref(kept, source_visibility.get(kept, "public"), audience_visibility)
        dropped_ref = source_ref(dropped, source_visibility.get(dropped, "public"), audience_visibility)
        duplicate_reports.append(
            {
                "key": duplicate["key"] if kept_ref == kept and dropped_ref == dropped else f"redacted:{stable_digest(duplicate['key'])}",
                "kept": kept_ref,
                "dropped": dropped_ref,
            }
        )
    source_hash_reports = []
    for path in sorted(included_sources):
        visibility = source_visibility.get(path, "public")
        source_hash_reports.append(
            {
                "source": source_ref(path, visibility, audience_visibility),
                "content_hash": source_content_hash_ref(
                    path,
                    visibility,
                    audience_visibility,
                    digest=source_hashes.get(path),
                ),
            }
        )
    return {
        "root_node": root_node,
        "project_channel_role": PROJECT_CHANNEL_ROLE,
        "project_slot": channel_binding["slot"],
        "channel_binding": channel_binding,
        "slot_recommendation": project_slot_recommendation(channel_registry),
        "audience_visibility": audience_visibility,
        "generated_at": compiled_at,
        "compiled_at": compiled_at,
        "source_lists": sorted(
            source_ref(path, source_visibility.get(path, "public"), audience_visibility)
            for path in included_sources
        ),
        "source_content_hashes": source_hash_reports,
        "freshness": {
            "compiled_at": compiled_at,
            "source_content_hashes": source_hash_reports,
        },
        "project_count": len(projects),
        "emitted_project_count": len(rollup_projects),
        "redacted_count": redacted_count,
        "private_count_only": private_count_only,
        "by_priority": by_priority,
        "by_status": by_status,
        "by_bucket": by_bucket,
        "starvation": {
            "threshold_days": DEFAULT_STARVATION_DAYS,
            "escalated": [
                {
                    "project_id": project.global_id or project.project_id,
                    "node": project.node,
                    "from_priority": project.priority,
                    "to_bucket": bucket_by_key[dedupe_key(project)],
                }
                for project in projects
                if escalated_by_key.get(dedupe_key(project), False)
            ],
        },
        "duplicates": duplicate_reports,
        "projects": rollup_projects,
    }


def role_matches(project: ProjectRecord, role: str) -> bool:
    if not project.roles:
        return True
    needle = role.casefold()
    return any(needle in item.casefold() or item.casefold() in needle for item in project.roles)


def tags_match(project: ProjectRecord, tags: list[str]) -> bool:
    if not tags:
        return True
    project_tags = {tag.casefold() for tag in project.personality_tags}
    return any(tag.casefold() in project_tags for tag in tags)


def claimable(project: ProjectRecord) -> bool:
    status_allows_claim = project.status == "pending" or (
        project.status == "claimed" and project_claim_expired(project)
    )
    return status_allows_claim and not project.blocked_on and not project.redacted


def significant_action_reasons(project: ProjectRecord) -> list[str]:
    reasons: list[str] = []
    if project.significant_action:
        reasons.append("self_declared")
    text = "\n".join(
        [
            project.title,
            project.description,
            "\n".join(project.files_owned),
            "\n".join(project.acceptance),
            "\n".join(project.blocked_on),
        ]
    )
    for reason, pattern in SIGNIFICANT_ACTION_PATTERNS:
        if pattern.search(text) and reason not in reasons:
            reasons.append(reason)
    for path in project.files_owned:
        for reason, pattern in SIGNIFICANT_PATH_PATTERNS:
            if pattern.search(path) and reason not in reasons:
                reasons.append(reason)
    return reasons


def project_requires_gate(project: ProjectRecord) -> bool:
    return bool(significant_action_reasons(project))


def pull_for_agent(rollup: dict[str, Any], role: str, personality_tags: list[str] | None = None) -> list[dict[str, Any]]:
    tags = personality_tags or []
    records = [
        normalize_project(project, project.get("node", ""), Path(project.get("source_path", "")))
        for project in rollup["projects"]
    ]
    matches = [
        project
        for project in records
        if claimable(project) and role_matches(project, role) and tags_match(project, tags)
    ]
    return [
        {
            **asdict(project),
            "gate_required": project_requires_gate(project),
            "gate_reasons": significant_action_reasons(project),
            "coordination_create_args": to_coordination_create_args(project),
        }
        for project in matches
    ]


def to_coordination_create_args(project: ProjectRecord) -> dict[str, Any]:
    coordination_deps, external_blockers = wave1_work_packages.split_blockers(project.blocked_on)
    lines = [
        project.description,
        "",
        f"Project ID: {project.project_id}",
        f"Node: {project.node}",
        f"Source: {project.source_path}",
    ]
    gate_reasons = significant_action_reasons(project)
    if gate_reasons:
        lines.append("Gate required: yes")
        lines.append(f"Gate reasons: {', '.join(gate_reasons)}")
    if external_blockers:
        lines.append(f"External blockers: {', '.join(external_blockers)}")
    return {
        "title": f"{project.project_id}: {project.title}",
        "description": "\n".join(lines),
        "priority": project.priority,
        "owned_paths": list(project.files_owned),
        "depends_on": coordination_deps,
        "created_by": project.claimed_by or "rollup",
        "acceptance_criteria": list(project.acceptance),
        "external_blockers": external_blockers,
    }


def update_project_claim_text(content: str, project_id: str, agent: str, claimed_at: str) -> str:
    data = json.loads(content)
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise RollupError("project list JSON must contain a projects array")
    changed = False
    expires_at = claim_lease_expiry(claimed_at)
    claim_checked_at = parse_time(claimed_at)
    for project in data["projects"]:
        if not isinstance(project, dict) or str(project.get("project_id", "")).casefold() != project_id.casefold():
            continue
        status = str(project.get("status", "pending"))
        expired_claim = status == "claimed" and project_claim_expired_dict(project, claim_checked_at)
        if status != "pending" and not expired_claim:
            raise RollupError(f"Cannot claim {project_id}: status is '{status}'")
        if project.get("blocked_on"):
            raise RollupError(f"Cannot claim {project_id}: blocked_on is not empty")
        project["status"] = "claimed"
        project["claimed_by"] = agent
        project["claimed_at"] = claimed_at
        project["claim_expires_at"] = expires_at
        project["claim_lease"] = {
            "holder": agent,
            "acquired_at": claimed_at,
            "expires_at": expires_at,
        }
        project["updated_at"] = claimed_at
        data.setdefault("audit_log", []).append(
            {
                "at": claimed_at,
                "actor": agent,
                "event": f"claimed:{project_id}",
                "lease_expires_at": expires_at,
                "reclaimed_expired": expired_claim,
            }
        )
        changed = True
        break
    if not changed:
        raise RollupError(f"Project not found: {project_id}")
    return json.dumps(data, indent=2) + "\n"


def claim_project(
    project_list_path: str | Path,
    project_id: str,
    agent: str,
    execute: bool = False,
    claimed_at: str | None = None,
) -> dict[str, Any]:
    path = Path(project_list_path)
    claimed = claimed_at or now_iso()
    if execute:
        with wave1_board_writer.board_file_lock(path):
            original = path.read_text(encoding="utf-8")
            updated = update_project_claim_text(original, project_id, agent, claimed)
            if updated != original:
                wave1_board_writer.atomic_write_text(path, updated)
    else:
        original = path.read_text(encoding="utf-8")
        updated = update_project_claim_text(original, project_id, agent, claimed)
    return {
        "project_list": str(path),
        "project_id": project_id,
        "agent": agent,
        "claimed_at": claimed,
        "execute": execute,
        "changed": updated != original,
    }


def load_channel_registry(path: str | Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    raw = Path(path).read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise RollupError("channel registry must be a JSON object")
    return data


def build_rollup_from_root(
    root: str | Path,
    root_node: str,
    channel_registry: dict[str, Any] | None = None,
    audience_visibility: str = DEFAULT_AUDIENCE_VISIBILITY,
) -> dict[str, Any]:
    lists = [load_project_list(path) for path in discover_project_lists(root)]
    return compile_rollup(
        root_node,
        lists,
        channel_registry=channel_registry,
        audience_visibility=audience_visibility,
    )


def format_text_rollup(rollup: dict[str, Any]) -> str:
    lines = [
        "Wave 2 Hierarchical Project Rollup",
        f"Root node: {rollup['root_node']}",
        f"Project channel: {rollup['project_channel_role']} -> {rollup['project_slot']}",
        f"Audience visibility: {rollup['audience_visibility']}",
        f"Projects: {rollup['project_count']}",
        f"Rows emitted: {rollup['emitted_project_count']}",
        f"Redacted: {rollup['redacted_count']}",
        f"Private count-only: {rollup['private_count_only']}",
        f"Sources: {len(rollup['source_lists'])}",
        "",
        "Priorities:",
    ]
    if rollup["by_priority"]:
        for priority, count in sorted(rollup["by_priority"].items(), key=lambda item: PRIORITY_RANK[item[0]]):
            lines.append(f"- {priority}: {count}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Projects:")
    if rollup["projects"]:
        for project in rollup["projects"]:
            gate = " gate" if project["significant_action"] else ""
            lines.append(
                f"- [{project['priority']}] {project['node']} {project['project_id']} "
                f"{project['status']}{gate}: {project['title']}"
            )
    else:
        lines.append("- none")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Wave 2 hierarchical project rollup.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--channel-registry", default="")
    parser.add_argument("--audience-visibility", choices=sorted(VISIBILITY_RANK), default=DEFAULT_AUDIENCE_VISIBILITY)
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan project lists below a root directory.")
    scan.add_argument("root")
    scan.add_argument("--root-node", required=True)

    pull = sub.add_parser("pull", help="Show claimable work matching an agent role/tags.")
    pull.add_argument("root")
    pull.add_argument("--root-node", required=True)
    pull.add_argument("--role", required=True)
    pull.add_argument("--tag", action="append", default=[])

    claim = sub.add_parser("claim", help="Claim one project in its node-local list.")
    claim.add_argument("project_list")
    claim.add_argument("project_id")
    claim.add_argument("--agent", required=True)
    claim.add_argument("--claimed-at", default="")
    claim.add_argument("--execute", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "claim":
            report = claim_project(
                args.project_list,
                args.project_id,
                args.agent,
                execute=args.execute,
                claimed_at=args.claimed_at or None,
            )
            if args.format == "json":
                print(json.dumps(report, indent=2))
            else:
                mode = "executed" if report["execute"] else "dry-run"
                print(f"Project claim {mode}: changed={str(report['changed']).lower()}")
            return 0

        channel_registry = load_channel_registry(args.channel_registry) if args.channel_registry else None
        rollup = build_rollup_from_root(
            args.root,
            args.root_node,
            channel_registry=channel_registry,
            audience_visibility=args.audience_visibility,
        )
        if args.command == "pull":
            payload: Any = {
                "root_node": args.root_node,
                "matches": pull_for_agent(rollup, args.role, args.tag),
            }
        else:
            payload = rollup
    except (RollupError, OSError, json.JSONDecodeError) as exc:
        if args.format == "json":
            print(json.dumps({"error": str(exc)}, indent=2))
        else:
            print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        if args.command == "pull":
            print(f"Wave 2 Agent Pull: {len(payload['matches'])} match(es)")
            for match in payload["matches"]:
                gate = " gate-required" if match["gate_required"] else ""
                print(f"- [{match['priority']}] {match['node']} {match['project_id']}{gate}: {match['title']}")
        else:
            print(format_text_rollup(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
