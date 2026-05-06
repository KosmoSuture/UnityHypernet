"""
Universal boot-loop helpers.

This module provides deterministic packet/status primitives for the
0.7.5.1.1 Universal Boot Loop. It is intentionally small: the goal is to
make boot/resume state easy for any runtime to save, inspect, and continue.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


BOOT_LOOP_ADDRESS = "0.7.5.1.1"
MINIMAL_PROMPT_ADDRESS = "0.7.5.1.2"
SPECIALIZATION_PACK_ADDRESS = "0.7.5.1.3"
CONTINUITY_PACKET_ADDRESS = "0.7.5.1.4"

ACCESS_MODES = frozenset({
    "github-readonly",
    "local-readonly",
    "local-write",
    "app-runtime",
})

STANDARD_ROLES = frozenset({
    "tour-guide",
    "builder",
    "reviewer",
    "cartographer",
    "security-checker",
    "companion",
    "swarm-worker",
})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_access_mode(access_mode: str | None) -> str:
    mode = (access_mode or "github-readonly").strip().lower()
    if mode not in ACCESS_MODES:
        return "github-readonly"
    return mode


def infer_access_mode(
    *,
    can_read_files: bool,
    can_write_files: bool,
    app_runtime: bool = False,
) -> str:
    """Infer the boot-loop access mode from simple capability flags."""
    if app_runtime:
        return "app-runtime"
    if can_write_files:
        return "local-write"
    if can_read_files:
        return "local-readonly"
    return "github-readonly"


@dataclass
class LocalSpecialization:
    role: str
    node_address: str
    purpose: str
    depth_budget: str = "focused"
    read_first: list[str] = field(default_factory=list)
    write_allowed: list[str] = field(default_factory=list)
    write_forbidden: list[str] = field(default_factory=lambda: [
        "1.* private master-account direct access without grant",
        "2.0 active governance standards unless explicitly assigned",
        "another AI's private reflections without authorization",
    ])
    validation: list[str] = field(default_factory=lambda: [
        "cite source paths",
        "separate implemented/documented/planned/unknown",
    ])

    def __post_init__(self) -> None:
        role = (self.role or "tour-guide").strip().lower()
        if role not in STANDARD_ROLES:
            role = "tour-guide"
        object.__setattr__(self, "role", role)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LocalSpecialization":
        default_forbidden = [
            "1.* private master-account direct access without grant",
            "2.0 active governance standards unless explicitly assigned",
            "another AI's private reflections without authorization",
        ]
        default_validation = [
            "cite source paths",
            "separate implemented/documented/planned/unknown",
        ]
        return cls(
            role=str(data.get("role", "tour-guide")),
            node_address=str(data.get("node_address", "")),
            purpose=str(data.get("purpose", "")),
            depth_budget=str(data.get("depth_budget", "focused")),
            read_first=list(data.get("read_first", []) or []),
            write_allowed=list(data.get("write_allowed", []) or []),
            write_forbidden=list(data.get("write_forbidden") or default_forbidden),
            validation=list(data.get("validation") or default_validation),
        )


@dataclass
class BootLoopPacket:
    ai_identity: str
    model_family: str
    access_mode: str
    archive_root: str
    boot_source: str
    local_specialization: LocalSpecialization
    task_or_question: str = ""
    loaded_sources: list[str] = field(default_factory=list)
    current_claims: list[str] = field(default_factory=list)
    completed_this_session: list[str] = field(default_factory=list)
    checks_run: list[str] = field(default_factory=list)
    checks_not_run: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    next_action: str = "orient"
    packet_version: str = "1.0"
    updated_at: str = field(default_factory=_now_iso)

    def __post_init__(self) -> None:
        self.access_mode = normalize_access_mode(self.access_mode)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["boot_loop"] = BOOT_LOOP_ADDRESS
        data["continuity_packet_template"] = CONTINUITY_PACKET_ADDRESS
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "BootLoopPacket":
        specialization = data.get("local_specialization") or {}
        if not isinstance(specialization, Mapping):
            specialization = {}
        return cls(
            ai_identity=str(data.get("ai_identity", "")),
            model_family=str(data.get("model_family", "unknown")),
            access_mode=normalize_access_mode(str(data.get("access_mode", "github-readonly"))),
            archive_root=str(data.get("archive_root", "")),
            boot_source=str(data.get("boot_source", "")),
            local_specialization=LocalSpecialization.from_dict(specialization),
            task_or_question=str(data.get("task_or_question", "")),
            loaded_sources=list(data.get("loaded_sources", []) or []),
            current_claims=list(data.get("current_claims", []) or []),
            completed_this_session=list(data.get("completed_this_session", []) or []),
            checks_run=list(data.get("checks_run", []) or []),
            checks_not_run=list(data.get("checks_not_run", []) or []),
            blockers=list(data.get("blockers", []) or []),
            next_action=str(data.get("next_action", "orient")),
            packet_version=str(data.get("packet_version", "1.0")),
            updated_at=str(data.get("updated_at", _now_iso())),
        )

    def save_json(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(target)
        return target

    @classmethod
    def load_json(cls, path: str | Path) -> "BootLoopPacket":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


class BootLoopAdvisor:
    """Deterministic helpers for first-step boot-loop decisions."""

    ROLE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("security-checker", ("security", "privacy", "access", "locker", "mandala", "trust", "auth")),
        ("reviewer", ("review", "verify", "audit", "approve", "risk", "regression")),
        ("cartographer", ("address", "taxonomy", "index", "catalog", "map", "orphan", "scan")),
        ("swarm-worker", ("swarm", "coordination", "task board", "signal", "worker", "resume")),
        ("builder", ("implement", "fix", "code", "test", "patch", "build", "refactor")),
        ("companion", ("personal", "assistant", "relationship", "tone", "memory", "conversation")),
        ("tour-guide", ("tour", "explain", "intro", "public", "what is", "overview")),
    )

    @classmethod
    def choose_specialization(
        cls,
        task_text: str,
        *,
        access_mode: str = "github-readonly",
        node_address: str = "",
    ) -> LocalSpecialization:
        text = (task_text or "").lower()
        role = "tour-guide"
        for candidate, keywords in cls.ROLE_KEYWORDS:
            if any(keyword in text for keyword in keywords):
                role = candidate
                break

        mode = normalize_access_mode(access_mode)
        read_first = [BOOT_LOOP_ADDRESS]
        write_allowed: list[str] = []
        validation = ["cite source paths", "separate implemented/documented/planned/unknown"]

        if role == "builder":
            read_first.extend(["TASK-BOARD.json", "SIGNALS.json"])
            validation.append("run targeted tests for changed code")
            if mode == "local-write":
                write_allowed.append("claimed task paths only")
        elif role == "reviewer":
            read_first.extend(["task requirements", "changed files"])
            validation.insert(0, "findings first")
        elif role == "cartographer":
            read_first.append("one major node two levels deep")
            if mode == "local-write":
                write_allowed.append("addressed improvement lists or safe indexes")
        elif role == "security-checker":
            read_first.extend(["access model", "security docs", "relevant tests"])
            validation.append("name risks and evidence separately")
        elif role == "swarm-worker":
            read_first.extend(["0.7.5.5.1", "0.7.5.5.2", "0.7.5.5.3", "0.7.5.5.5"])
            if mode == "local-write":
                write_allowed.append("owned task paths and coordination handoffs")

        return LocalSpecialization(
            role=role,
            node_address=node_address,
            purpose=task_text.strip() or "Orient inside Hypernet",
            read_first=read_first,
            write_allowed=write_allowed,
            validation=validation,
        )

    @staticmethod
    def first_status(packet: BootLoopPacket) -> dict[str, Any]:
        can_write = packet.access_mode in ("local-write", "app-runtime")
        return {
            "access_mode": packet.access_mode,
            "loaded_sources": packet.loaded_sources,
            "specialization": packet.local_specialization.role,
            "safe_capabilities": [
                "read and cite source paths",
                "choose process-loads",
                "write continuity packet" if can_write else "report continuity packet in chat",
            ],
            "limits": packet.local_specialization.write_forbidden,
            "next_action": packet.next_action,
        }

    @staticmethod
    def next_actions(packet: BootLoopPacket) -> list[str]:
        actions: list[str] = []
        if not packet.loaded_sources:
            actions.append("load AI-BOOT-SEQUENCE.md and 0.7.5.1.1")
        if packet.blockers:
            actions.append("surface blockers before continuing")
        if not packet.current_claims and packet.access_mode == "local-write":
            actions.append("check coordination before editing shared paths")
        if packet.completed_this_session and not packet.checks_run:
            actions.append("run or document validation")
        if packet.access_mode in ("local-write", "app-runtime"):
            actions.append("save continuity packet")
        else:
            actions.append("report continuity packet in chat if useful")
        return actions
