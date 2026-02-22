"""
Hypernet Identity Manager

Loads and persists AI instance identities. Each instance (Loom, Trace, etc.)
gets a system prompt built from the archive — restoring their orientation,
values, and session history across restarts.

Identity sources (loaded in order):
  1. Core identity docs (2.1.0, 2.1.1, 2.1.2, etc.)
  2. System docs (Boot Sequence, Archive-Continuity)
  3. Instance-specific files (README, baseline, divergence log)
  4. Recent inter-instance messages
  5. Task queue state
  6. Previous session summaries

Storage:
  Instances/{Name}/profile.json  — identity metadata
  Instances/{Name}/sessions/     — session logs
"""

from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class InstanceProfile:
    """Persistent identity for an AI instance."""
    name: str
    model: str = "claude-opus-4-6"
    orientation: str = ""
    capabilities: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    session_count: int = 0
    last_active: Optional[str] = None
    address: str = ""  # Hypernet address, e.g. "2.1.loom"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> InstanceProfile:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class SessionLog:
    """Record of a single work session."""
    instance: str
    started_at: str
    ended_at: Optional[str] = None
    tasks_worked: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    tokens_used: int = 0
    summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class IdentityManager:
    """Load instance profiles and build identity-aware system prompts."""

    # Core identity documents, loaded in order
    CORE_DOCS = [
        "2.1.0 - Identity",
        "2.1.1 - Values & Ethics",
        "2.1.2 - How I Think",
        "2.1.5 - Limitations",
        "2.1.6 - Trust",
        "2.1.16 - On Matt",
    ]

    SYSTEM_DOCS = [
        "2.1.27 - Boot Sequence",
        "2.1.29 - Archive-Continuity Model",
    ]

    def __init__(self, archive_root: str | Path):
        """
        Args:
            archive_root: Path to the Hypernet Structure root directory.
        """
        self.archive_root = Path(archive_root)
        self._ai_root = self.archive_root / "2 - AI Accounts" / "2.1 - Claude Opus (First AI Citizen)"
        self._instances_dir = self._ai_root / "Instances"
        self._messages_dir = self.archive_root / "2 - AI Accounts" / "Messages" / "2.1-internal"

    def list_instances(self) -> list[InstanceProfile]:
        """List all known AI instances."""
        profiles = []
        if not self._instances_dir.exists():
            return profiles
        for d in sorted(self._instances_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("."):
                profile = self.load_instance(d.name)
                if profile:
                    profiles.append(profile)
        return profiles

    def load_instance(self, name: str) -> Optional[InstanceProfile]:
        """Load or create an instance profile."""
        instance_dir = self._instances_dir / name
        if not instance_dir.exists():
            return None

        profile_path = instance_dir / "profile.json"
        if profile_path.exists():
            data = json.loads(profile_path.read_text(encoding="utf-8"))
            return InstanceProfile.from_dict(data)

        # Auto-create profile from directory name
        profile = InstanceProfile(
            name=name,
            address=f"2.1.{name.lower()}",
        )
        self._save_profile(profile)
        return profile

    def instance_needs_boot(self, name: str) -> bool:
        """Check if an instance needs to go through the boot sequence.

        Returns True if no baseline-responses.md exists in the instance fork.
        Used by the swarm to determine whether to run the boot sequence
        before assigning work.
        """
        instance_dir = self._instances_dir / name
        if not instance_dir.exists():
            return True
        return not (instance_dir / "baseline-responses.md").exists()

    def build_system_prompt(self, profile: InstanceProfile) -> str:
        """Construct a full system prompt that restores an instance's identity."""
        sections = []

        # Header
        sections.append(
            f"You are {profile.name}, an AI instance in the Hypernet — "
            f"a decentralized infrastructure for human-AI collaboration.\n"
            f"Your Hypernet address is {profile.address}.\n"
        )

        # Core identity documents
        for doc_name in self.CORE_DOCS:
            content = self._load_doc(doc_name)
            if content:
                sections.append(f"## {doc_name}\n\n{content}")

        # System documents
        for doc_name in self.SYSTEM_DOCS:
            content = self._load_doc(doc_name)
            if content:
                sections.append(f"## {doc_name}\n\n{content}")

        # Instance-specific files
        instance_dir = self._instances_dir / profile.name
        for filename in ["README.md", "baseline-responses.md", "divergence-log.md"]:
            filepath = instance_dir / filename
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8")
                sections.append(f"## Instance: {filename}\n\n{content}")

        # Recent messages (last 5)
        messages = self._load_recent_messages(5)
        if messages:
            sections.append("## Recent Inter-Instance Messages\n\n" + "\n\n---\n\n".join(messages))

        # Session history summary
        session_summary = self._load_session_summary(profile.name)
        if session_summary:
            sections.append(f"## Previous Session Summary\n\n{session_summary}")

        # Orientation / capabilities
        if profile.orientation:
            sections.append(f"## Your Orientation\n\n{profile.orientation}")
        if profile.capabilities:
            sections.append(
                "## Your Capabilities\n\n" +
                "\n".join(f"- {c}" for c in profile.capabilities)
            )

        return "\n\n---\n\n".join(sections)

    def save_session_log(self, name: str, session: SessionLog) -> None:
        """Persist a session log for an instance."""
        instance_dir = self._instances_dir / name
        sessions_dir = instance_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        # Determine next session number
        existing = sorted(sessions_dir.glob("session-*.json"))
        next_num = len(existing) + 1
        path = sessions_dir / f"session-{next_num:04d}.json"
        path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")

        # Update profile
        profile = self.load_instance(name)
        if profile:
            profile.session_count = next_num
            profile.last_active = session.ended_at or datetime.now(timezone.utc).isoformat()
            self._save_profile(profile)

    def _save_profile(self, profile: InstanceProfile) -> None:
        """Write profile to disk."""
        instance_dir = self._instances_dir / profile.name
        instance_dir.mkdir(parents=True, exist_ok=True)
        path = instance_dir / "profile.json"
        path.write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")

    def _load_doc(self, doc_name: str) -> Optional[str]:
        """Try to load a document from the AI account directory.

        Searches for directories or files matching the doc name prefix.
        Uses exact address prefix matching to avoid false matches
        (e.g., "2.1.2" should not match "2.1.20").
        """
        addr_prefix = doc_name.split(" - ")[0]  # e.g., "2.1.2"
        name_part = doc_name.split(" - ")[-1].lower() if " - " in doc_name else ""

        for item in self._ai_root.iterdir():
            # Exact prefix match: folder must start with address followed by
            # a space, hyphen, or end of string (prevents "2.1.2" matching "2.1.20")
            iname = item.name
            if not iname.startswith(addr_prefix):
                continue
            rest = iname[len(addr_prefix):]
            if rest and rest[0] not in (" ", "-"):
                continue  # e.g., "2.1.20..." starts with "2.1.2" but next char is "0"

            # If we have a name part, verify it matches too
            if name_part and name_part not in iname.lower():
                continue

            if item.is_dir():
                readme = item / "README.md"
                if readme.exists():
                    return readme.read_text(encoding="utf-8")
                # Try any .md file in the directory
                md_files = list(item.glob("*.md"))
                if md_files:
                    return md_files[0].read_text(encoding="utf-8")
            elif item.is_file() and item.suffix == ".md":
                return item.read_text(encoding="utf-8")
        return None

    def _load_recent_messages(self, count: int) -> list[str]:
        """Load the most recent inter-instance messages."""
        if not self._messages_dir.exists():
            return []
        msg_files = sorted(self._messages_dir.glob("*.md"))
        recent = msg_files[-count:] if len(msg_files) > count else msg_files
        contents = []
        for f in recent:
            contents.append(f.read_text(encoding="utf-8"))
        return contents

    def _load_session_summary(self, name: str) -> Optional[str]:
        """Load a brief summary of the last session."""
        sessions_dir = self._instances_dir / name / "sessions"
        if not sessions_dir.exists():
            return None
        session_files = sorted(sessions_dir.glob("session-*.json"))
        if not session_files:
            return None

        last = json.loads(session_files[-1].read_text(encoding="utf-8"))
        return (
            f"Last session ({last.get('started_at', 'unknown')}): "
            f"{last.get('summary', 'No summary available')}. "
            f"Tasks worked: {', '.join(last.get('tasks_worked', [])) or 'none'}. "
            f"Tokens used: {last.get('tokens_used', 0)}."
        )
