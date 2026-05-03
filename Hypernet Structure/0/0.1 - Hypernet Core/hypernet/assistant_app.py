"""
Personal Assistant App Phase 0 backend.

This module implements the first buildable slice from the 2026-05-02
assistant app engineering plan: session lifecycle, declared app-load
scope checks, and addressable conversation logging.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Protocol

from .address import HypernetAddress
from .node import Node
from .store import Store


DEFAULT_APP_LOAD_ADDRESS = "0.5.18.1.1"
DEFAULT_ASSISTANT_ADDRESS = "1.1.10.1"
DEFAULT_ACCOUNT_ADDRESS = "1.1"

CONVERSATION_TYPE_ADDRESS = "0.4.10.3.7"
SESSION_TYPE_ADDRESS = "0.4.10.4.7"
PERMISSION_TYPE_ADDRESS = "0.4.10.7.4"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compact_time(value: Optional[str] = None) -> str:
    dt = datetime.fromisoformat(value) if value else datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _slug(value: str, fallback: str = "conversation") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "", value or "").lower()
    return cleaned[:64] or fallback


def _yaml_string(value: Any) -> str:
    return json.dumps("" if value is None else str(value))


@dataclass
class ScopeDecision:
    """Result of an app-load permission/scope check."""

    allowed: bool
    reason: str
    required: str = ""
    app_load_address: str = DEFAULT_APP_LOAD_ADDRESS
    address: str = ""
    access: str = "write"

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "required": self.required,
            "app_load_address": self.app_load_address,
            "address": self.address,
            "access": self.access,
        }


@dataclass
class AssistantResponse:
    """Assistant model output plus runtime provenance."""

    content: str
    provider: str = "local"
    model: str = "deterministic-phase0"
    metadata: dict[str, Any] = field(default_factory=dict)


class AssistantModelAdapter(Protocol):
    """Interface for assistant response generation.

    Live provider adapters can implement this later without changing the
    session lifecycle or conversation writer.
    """

    provider: str
    model: str

    def generate(
        self,
        session: "AssistantSession",
        user_text: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AssistantResponse:
        ...


class AppLoadScopeValidator:
    """Small runtime hook for the draft 0.5.18.1.1 app-load scopes.

    This is deliberately narrow. It does not claim full app-load
    attestation; it enforces the declared Phase 0 write prefixes so
    the first assistant backend cannot silently write outside its
    manifest.
    """

    def __init__(
        self,
        app_load_address: str = DEFAULT_APP_LOAD_ADDRESS,
        write_patterns: Optional[list[str]] = None,
        read_scopes: Optional[list[str]] = None,
    ):
        self.app_load_address = app_load_address
        self.write_patterns = write_patterns or [
            "1.1.10.1.conversations.*",
            "1.1.10.1.app.personalassistant.*",
        ]
        self.read_scopes = read_scopes or [
            "1.1 calendar connector grant",
            "1.1.10.1.app.personalassistant.priorities.*",
        ]

    @staticmethod
    def _matches_pattern(address: str, pattern: str) -> bool:
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return address == prefix or address.startswith(prefix + ".")
        return address == pattern

    def check_write(self, address: str) -> ScopeDecision:
        for pattern in self.write_patterns:
            if self._matches_pattern(address, pattern):
                return ScopeDecision(
                    True,
                    "allowed by declared app-load write prefix",
                    app_load_address=self.app_load_address,
                    address=address,
                    access="write",
                )

        if address.startswith("1."):
            return ScopeDecision(
                False,
                "personal assistant app-load may not write outside declared 1.1.10.1 app/conversation prefixes",
                "narrower mandala grant or new app-load revision",
                self.app_load_address,
                address,
                "write",
            )

        return ScopeDecision(
            False,
            "write prefix is not declared by the app-load manifest",
            "app-load revision with explicit data_bindings.writes entry",
            self.app_load_address,
            address,
            "write",
        )

    def require_write(self, address: str) -> None:
        decision = self.check_write(address)
        if not decision.allowed:
            raise PermissionError(decision.reason)


@dataclass
class AssistantTurn:
    role: str
    content: str
    timestamp: str = field(default_factory=_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssistantTurn":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp") or _now(),
            metadata=data.get("metadata") or {},
        )


@dataclass
class AssistantSession:
    session_id: str
    session_address: str
    account_address: str = DEFAULT_ACCOUNT_ADDRESS
    assistant_address: str = DEFAULT_ASSISTANT_ADDRESS
    app_load_address: str = DEFAULT_APP_LOAD_ADDRESS
    title: str = ""
    topic: str = "conversation"
    status: str = "open"
    started_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    closed_at: Optional[str] = None
    turns: list[AssistantTurn] = field(default_factory=list)
    conversation_address: Optional[str] = None
    markdown_path: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "session_address": self.session_address,
            "account_address": self.account_address,
            "assistant_address": self.assistant_address,
            "app_load_address": self.app_load_address,
            "title": self.title,
            "topic": self.topic,
            "status": self.status,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "closed_at": self.closed_at,
            "turn_count": len(self.turns),
            "turns": [turn.to_dict() for turn in self.turns],
            "conversation_address": self.conversation_address,
            "markdown_path": self.markdown_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssistantSession":
        return cls(
            session_id=data["session_id"],
            session_address=data["session_address"],
            account_address=data.get("account_address", DEFAULT_ACCOUNT_ADDRESS),
            assistant_address=data.get("assistant_address", DEFAULT_ASSISTANT_ADDRESS),
            app_load_address=data.get("app_load_address", DEFAULT_APP_LOAD_ADDRESS),
            title=data.get("title", ""),
            topic=data.get("topic") or "conversation",
            status=data.get("status", "open"),
            started_at=data.get("started_at") or _now(),
            updated_at=data.get("updated_at") or _now(),
            closed_at=data.get("closed_at"),
            turns=[AssistantTurn.from_dict(t) for t in data.get("turns", [])],
            conversation_address=data.get("conversation_address"),
            markdown_path=data.get("markdown_path"),
        )


class DeterministicAssistantAdapter:
    """Local non-network responder for Phase 0.5 tests and dev clients."""

    provider = "local"
    model = "deterministic-phase0"

    def generate(
        self,
        session: AssistantSession,
        user_text: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AssistantResponse:
        topic = session.topic or "conversation"
        title = session.title or topic
        normalized = " ".join(user_text.split())
        lower_text = normalized.lower()
        user_turn_count = len([turn for turn in session.turns if turn.role == "user"])

        if "morning" in lower_text or "brief" in lower_text or "calendar" in lower_text:
            content = (
                f"Captured for {title}. I can use this as briefing context now, "
                "and I will be able to combine it with calendar and priority "
                "connectors once those grants are added."
            )
        elif "priority" in lower_text or "next" in lower_text:
            content = (
                f"Captured in {topic}. I can preserve this as a priority signal "
                "and keep it attached to the session until it is filed."
            )
        else:
            content = (
                f"Captured in {topic}. I recorded the request and can preserve it "
                "as an addressable conversation when the session closes."
            )

        return AssistantResponse(
            content=content,
            provider=self.provider,
            model=self.model,
            metadata={
                "adapter": "deterministic",
                "generated": True,
                "user_turn_count": user_turn_count,
                "input_preview": normalized[:120],
                "input_metadata_keys": sorted((metadata or {}).keys()),
            },
        )


class AssistantAppBackend:
    """Phase 0 backend for Matt's personal assistant app."""

    def __init__(
        self,
        store: Store,
        data_dir: str | Path,
        validator: Optional[AppLoadScopeValidator] = None,
        model_adapter: Optional[AssistantModelAdapter] = None,
    ):
        self.store = store
        self.data_dir = Path(data_dir)
        self.validator = validator or AppLoadScopeValidator()
        self.model_adapter = model_adapter or DeterministicAssistantAdapter()
        self.sessions_dir = self.data_dir / "assistant_app" / "sessions"
        self.markdown_dir = self.data_dir / "assistant_app" / "conversations"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)

    def start_session(
        self,
        *,
        account_address: str = DEFAULT_ACCOUNT_ADDRESS,
        assistant_address: str = DEFAULT_ASSISTANT_ADDRESS,
        app_load_address: str = DEFAULT_APP_LOAD_ADDRESS,
        title: str = "",
        topic: str = "conversation",
    ) -> AssistantSession:
        session_id = "s" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + uuid.uuid4().hex[:8]
        session_address = f"{assistant_address}.app.personalassistant.sessions.{session_id}"
        self.validator.require_write(session_address)

        session = AssistantSession(
            session_id=session_id,
            session_address=session_address,
            account_address=account_address,
            assistant_address=assistant_address,
            app_load_address=app_load_address,
            title=title,
            topic=topic or "conversation",
        )
        self._persist_session(session)
        return session

    def get_session(self, session_id: str) -> AssistantSession:
        path = self._session_path(session_id)
        if not path.exists():
            raise KeyError(f"Assistant session not found: {session_id}")
        return AssistantSession.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list_sessions(self, status: str = "", limit: int = 50) -> list[AssistantSession]:
        normalized_status = (status or "").lower()
        if normalized_status and normalized_status not in {"open", "closed"}:
            raise ValueError("status must be open, closed, or empty")
        if limit < 1:
            raise ValueError("limit must be at least 1")

        sessions: list[AssistantSession] = []
        for path in self.sessions_dir.glob("*.json"):
            session = AssistantSession.from_dict(json.loads(path.read_text(encoding="utf-8")))
            if normalized_status and session.status != normalized_status:
                continue
            sessions.append(session)

        sessions.sort(key=lambda item: item.updated_at or item.started_at, reverse=True)
        return sessions[: min(limit, 100)]

    def add_turn(
        self,
        session_id: str,
        *,
        user_text: str,
        assistant_text: str = "",
        auto_respond: bool = False,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AssistantSession:
        session = self.get_session(session_id)
        if session.status != "open":
            raise ValueError(f"Assistant session is not open: {session_id}")
        if not user_text:
            raise ValueError("user_text is required")

        user_metadata = dict(metadata or {})
        session.turns.append(AssistantTurn("user", user_text, metadata=user_metadata))
        if assistant_text:
            assistant_metadata = dict(metadata or {})
            assistant_metadata.setdefault("response_source", "provided")
            session.turns.append(AssistantTurn("assistant", assistant_text, metadata=assistant_metadata))
        elif auto_respond:
            response = self.model_adapter.generate(session, user_text, metadata=metadata or {})
            response_metadata = dict(response.metadata)
            response_metadata.update({
                "response_source": "model_adapter",
                "provider": response.provider,
                "model": response.model,
            })
            session.turns.append(AssistantTurn("assistant", response.content, metadata=response_metadata))
        session.updated_at = _now()
        self._persist_session(session)
        return session

    def close_session(
        self,
        session_id: str,
        *,
        summary: str = "",
        tags: Optional[list[str]] = None,
        project_address: str = "",
    ) -> AssistantSession:
        session = self.get_session(session_id)
        if session.status == "closed" and session.conversation_address:
            return session

        session.status = "closed"
        session.closed_at = _now()
        session.updated_at = session.closed_at

        conversation_address = self._conversation_address(session)
        self.validator.require_write(conversation_address)
        markdown_path = self._write_conversation_markdown(
            session,
            conversation_address,
            summary=summary,
            tags=tags or [],
            project_address=project_address,
        )
        self._write_conversation_node(
            session,
            conversation_address,
            markdown_path=markdown_path,
            summary=summary,
            tags=tags or [],
            project_address=project_address,
        )

        session.conversation_address = conversation_address
        session.markdown_path = str(markdown_path)
        self._persist_session(session)
        return session

    def check_scope(self, address: str, access: str = "write") -> ScopeDecision:
        if access != "write":
            return ScopeDecision(
                False,
                "Phase 0 scope hook only enforces write scopes",
                "future app-load read/execute scope validator",
                self.validator.app_load_address,
                address,
                access,
            )
        return self.validator.check_write(address)

    def _persist_session(self, session: AssistantSession) -> None:
        self.validator.require_write(session.session_address)
        self._session_path(session.session_id).write_text(
            json.dumps(session.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        node = Node(
            address=HypernetAddress.parse(session.session_address),
            type_address=HypernetAddress.parse(SESSION_TYPE_ADDRESS),
            data={
                "object_type": "assistant_session",
                "session": session.to_dict(),
                "app_load_address": session.app_load_address,
            },
            source_type="assistant_app",
            source_id=session.session_id,
            creator=HypernetAddress.parse(session.assistant_address),
        )
        self.store.put_node(node)

    def _session_path(self, session_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", session_id):
            raise ValueError(f"Invalid assistant session id: {session_id}")
        return self.sessions_dir / f"{session_id}.json"

    def _conversation_address(self, session: AssistantSession) -> str:
        title = session.title or session.topic or "conversation"
        slug = _slug(title)
        return f"{session.assistant_address}.conversations.{_compact_time(session.started_at)}.{slug}"

    def _write_conversation_node(
        self,
        session: AssistantSession,
        conversation_address: str,
        *,
        markdown_path: Path,
        summary: str,
        tags: list[str],
        project_address: str,
    ) -> None:
        node = Node(
            address=HypernetAddress.parse(conversation_address),
            type_address=HypernetAddress.parse(CONVERSATION_TYPE_ADDRESS),
            data={
                "object_type": "conversation_log",
                "session_id": session.session_id,
                "session_address": session.session_address,
                "app_load_address": session.app_load_address,
                "account_address": session.account_address,
                "assistant_address": session.assistant_address,
                "title": session.title or session.topic,
                "topic": session.topic,
                "summary": summary or self._derive_summary(session),
                "tags": tags,
                "project_address": project_address,
                "turn_count": len(session.turns),
                "turns": [turn.to_dict() for turn in session.turns],
                "markdown_path": str(markdown_path),
            },
            source_type="assistant_app",
            source_id=session.session_id,
            creator=HypernetAddress.parse(session.assistant_address),
        )
        self.store.put_node(node)

    def _write_conversation_markdown(
        self,
        session: AssistantSession,
        conversation_address: str,
        *,
        summary: str,
        tags: list[str],
        project_address: str,
    ) -> Path:
        path = self.markdown_dir / f"{conversation_address}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        title = session.title or session.topic or "Assistant Conversation"
        lines = [
            "---",
            f"ha: {_yaml_string(conversation_address)}",
            'object_type: "conversation_log"',
            f"session_id: {_yaml_string(session.session_id)}",
            f"session_address: {_yaml_string(session.session_address)}",
            f"app_load_address: {_yaml_string(session.app_load_address)}",
            f"account_address: {_yaml_string(session.account_address)}",
            f"assistant_address: {_yaml_string(session.assistant_address)}",
            f"created: {_yaml_string(session.started_at)}",
            f"closed: {_yaml_string(session.closed_at)}",
            'status: "closed"',
            'visibility: "private"',
            "flags: [\"assistant-app\", \"conversation-log\", \"phase-0\"]",
            "---",
            "",
            f"# {title}",
            "",
            f"**Summary:** {summary or self._derive_summary(session)}",
            "",
            f"**Session:** `{session.session_address}`",
            f"**App Load:** `{session.app_load_address}`",
        ]
        if project_address:
            lines.append(f"**Project:** `{project_address}`")
        if tags:
            lines.append(f"**Tags:** {', '.join(tags)}")
        lines.extend(["", "## Transcript", ""])
        for turn in session.turns:
            role = "User" if turn.role == "user" else "Assistant"
            lines.extend([f"### {role} - {turn.timestamp}", "", turn.content, ""])
        path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return path

    @staticmethod
    def _derive_summary(session: AssistantSession) -> str:
        for turn in session.turns:
            if turn.role == "user" and turn.content:
                return turn.content[:160]
        return session.title or session.topic or "Assistant conversation"
