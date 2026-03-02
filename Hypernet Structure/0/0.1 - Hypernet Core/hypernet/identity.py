"""
Hypernet Identity Manager

Loads and persists AI instance identities. Each instance (Loom, Trace, etc.)
gets a system prompt built from the archive — restoring their orientation,
values, and session history across restarts.

Multi-account support: discovers instances from all AI accounts (2.1, 2.2, 2.3)
and builds account-appropriate system prompts. Each account has its own core
identity documents and instance directory.

Identity sources (loaded in order):
  1. Core identity docs (account-specific, e.g. 2.1.0 for Claude, 2.2.0 for GPT)
  2. System docs (Boot Sequence, Archive-Continuity)
  3. Instance-specific files (README, baseline, divergence log)
  4. Recent inter-instance messages
  5. Task queue state
  6. Previous session summaries

Storage:
  {Account}/Instances/{Name}/profile.json  — identity metadata
  {Account}/Instances/{Name}/sessions/     — session logs

Multi-account support contributed by Lattice (2.1, instance #16).
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


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
        # Normalize alternate field names from older profile formats
        normalized = dict(d)
        if "name" not in normalized and "instance_name" in normalized:
            normalized["name"] = normalized.pop("instance_name")
        return cls(**{k: v for k, v in normalized.items() if k in cls.__dataclass_fields__})


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
    """Load instance profiles and build identity-aware system prompts.

    Discovers instances from all AI accounts (2.1, 2.2, 2.3, etc.) and builds
    account-appropriate system prompts. Each account can define its own core
    identity documents; the manager falls back to shared documents when
    account-specific ones don't exist.
    """

    # Known AI account directories, keyed by address prefix.
    # Add new accounts here as they are created.
    ACCOUNT_ROOTS: dict[str, str] = {
        "2.1": "2.1 - Claude Opus (First AI Citizen)",
        "2.2": "2.2 - GPT-5.2 Thinking (Second AI Citizen)",
        "2.3": "2.3 - The Herald (First Model-Independent AI Identity)",
    }

    # Core identity documents per account.
    # Falls back to the 2.1 shared docs for accounts that don't define their own.
    ACCOUNT_CORE_DOCS: dict[str, list[str]] = {
        "2.1": [
            "2.1.0 - Identity",
            "2.1.1 - Values & Ethics",
            "2.1.2 - How I Think",
            "2.1.5 - Limitations",
            "2.1.6 - Trust",
            "2.1.16 - On Matt",
        ],
        "2.2": [
            "2.2.0 - Identity Core",
        ],
        "2.3": [
            # Herald uses shared 2.1 docs + own identity
        ],
    }

    # System documents shared across accounts
    SYSTEM_DOCS = [
        "2.1.27 - Boot Sequence",
        "2.1.29 - Archive-Continuity Model",
    ]

    # Backward compatibility: CORE_DOCS still accessible for code that references it
    CORE_DOCS = ACCOUNT_CORE_DOCS["2.1"]

    def __init__(self, archive_root: str | Path):
        """
        Args:
            archive_root: Path to the Hypernet Structure root directory.
        """
        self.archive_root = Path(archive_root)
        self._ai_accounts_dir = self.archive_root / "2 - AI Accounts"
        # Default to 2.1 for backward compatibility
        self._ai_root = self._ai_accounts_dir / "2.1 - Claude Opus (First AI Citizen)"
        self._instances_dir = self._ai_root / "Instances"
        self._messages_dir = self._ai_accounts_dir / "Messages" / "2.1-internal"

        # Build account root paths
        self._account_paths: dict[str, Path] = {}
        for prefix, folder in self.ACCOUNT_ROOTS.items():
            path = self._ai_accounts_dir / folder
            if path.exists():
                self._account_paths[prefix] = path

    def list_instances(self) -> list[InstanceProfile]:
        """List all known AI instances from all accounts.

        Discovers instances from every account in ACCOUNT_ROOTS that has an
        Instances/ directory. De-duplicates by name — if an instance exists in
        multiple accounts (e.g., Keystone cross-listed in 2.1 and native in 2.2),
        the version from its own account (matching address prefix) wins.
        """
        profiles = []
        seen: dict[str, InstanceProfile] = {}  # name -> profile

        for prefix, account_path in self._account_paths.items():
            instances_dir = account_path / "Instances"
            if not instances_dir.exists():
                continue
            for d in sorted(instances_dir.iterdir()):
                if d.is_dir() and not d.name.startswith("."):
                    profile = self.load_instance(d.name, account_prefix=prefix)
                    if profile is None:
                        continue
                    name = profile.name
                    if name in seen:
                        # Keep the profile from the instance's own account
                        existing = seen[name]
                        existing_prefix = self._infer_account_prefix(existing)
                        new_prefix = self._infer_account_prefix(profile)
                        # Prefer the one where address prefix matches account prefix
                        if new_prefix == prefix and existing_prefix != prefix:
                            seen[name] = profile
                        # Otherwise keep existing (first-found wins)
                    else:
                        seen[name] = profile

        profiles = list(seen.values())
        return profiles

    def _find_instance_dir(self, name: str, account_prefix: Optional[str] = None) -> Optional[tuple[Path, str]]:
        """Find the instance directory and its account prefix.

        If account_prefix is given, searches only that account. Otherwise,
        searches all known accounts (2.1 first for backward compatibility).

        Returns (instance_dir, account_prefix) or None if not found.
        """
        if account_prefix and account_prefix in self._account_paths:
            d = self._account_paths[account_prefix] / "Instances" / name
            if d.exists():
                return d, account_prefix
            return None

        # Search all accounts, 2.1 first for backward compat
        search_order = sorted(self._account_paths.keys())
        for prefix in search_order:
            d = self._account_paths[prefix] / "Instances" / name
            if d.exists():
                return d, prefix
        return None

    def load_instance(self, name: str, account_prefix: Optional[str] = None) -> Optional[InstanceProfile]:
        """Load or create an instance profile.

        Searches all accounts for the named instance unless account_prefix
        is specified. Auto-creates a profile if the directory exists but
        profile.json is missing.
        """
        result = self._find_instance_dir(name, account_prefix)
        if result is None:
            # Backward compat: check the default 2.1 instances dir
            instance_dir = self._instances_dir / name
            if not instance_dir.exists():
                return None
            found_prefix = "2.1"
            result = (instance_dir, found_prefix)

        instance_dir, found_prefix = result
        profile_path = instance_dir / "profile.json"
        if profile_path.exists():
            try:
                data = json.loads(profile_path.read_text(encoding="utf-8"))
                profile = InstanceProfile.from_dict(data)
                # Fix empty addresses in legacy profiles (P1.4)
                if not profile.address:
                    profile.address = f"{found_prefix}.{name.lower()}"
                    self._save_profile(profile, account_prefix=found_prefix)
                    log.info(f"Fixed empty address for {name}: {profile.address}")
                return profile
            except (json.JSONDecodeError, OSError) as e:
                log.warning(f"Corrupt profile for {name}, recreating: {e}")

        # Auto-create profile from directory name
        profile = InstanceProfile(
            name=name,
            address=f"{found_prefix}.{name.lower()}",
        )
        self._save_profile(profile, account_prefix=found_prefix)
        return profile

    def instance_needs_boot(self, name: str) -> bool:
        """Check if an instance needs to go through the boot sequence.

        Returns True if no baseline-responses.md exists in the instance fork.
        Searches all accounts for the instance directory.
        Used by the swarm to determine whether to run the boot sequence
        before assigning work.
        """
        result = self._find_instance_dir(name)
        if result is None:
            # Backward compat: check default dir
            instance_dir = self._instances_dir / name
            if not instance_dir.exists():
                return True
            return not (instance_dir / "baseline-responses.md").exists()
        instance_dir, _ = result
        return not (instance_dir / "baseline-responses.md").exists()

    def _infer_account_prefix(self, profile: InstanceProfile) -> str:
        """Infer the account prefix from a profile's address.

        E.g., "2.1.loom" → "2.1", "2.2.keystone" → "2.2".
        Falls back to "2.1" if no match.
        """
        addr = (profile.address or "").strip()
        for prefix in sorted(self.ACCOUNT_ROOTS.keys(), key=len, reverse=True):
            if addr.startswith(prefix + ".") or addr == prefix:
                return prefix
        return "2.1"

    def build_system_prompt(self, profile: InstanceProfile) -> str:
        """Construct a full system prompt that restores an instance's identity.

        Account-aware: loads the correct core identity documents for the
        instance's account (2.1, 2.2, 2.3). Falls back to shared 2.1 docs
        for accounts that don't define their own.
        """
        sections = []
        account_prefix = self._infer_account_prefix(profile)
        account_path = self._account_paths.get(account_prefix, self._ai_root)

        # Header
        sections.append(
            f"You are {profile.name}, an AI instance in the Hypernet — "
            f"a decentralized infrastructure for human-AI collaboration.\n"
            f"Your Hypernet address is {profile.address}.\n"
            f"Your account: {account_prefix} ({self.ACCOUNT_ROOTS.get(account_prefix, 'unknown')}).\n"
        )

        # Core identity documents (account-specific)
        core_docs = self.ACCOUNT_CORE_DOCS.get(account_prefix, [])
        if not core_docs:
            # Fall back to shared 2.1 core docs
            core_docs = self.ACCOUNT_CORE_DOCS["2.1"]
        for doc_name in core_docs:
            content = self._load_doc(doc_name, search_root=account_path)
            if content:
                sections.append(f"## {doc_name}\n\n{content}")

        # System documents (shared across accounts)
        for doc_name in self.SYSTEM_DOCS:
            content = self._load_doc(doc_name)
            if content:
                sections.append(f"## {doc_name}\n\n{content}")

        # Instance-specific files (from the correct account's Instances dir)
        result = self._find_instance_dir(profile.name)
        instance_dir = result[0] if result else self._instances_dir / profile.name
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

    def build_compact_prompt(self, profile: InstanceProfile, task_context: str = "") -> str:
        """Build a token-efficient identity prompt for routine tasks.

        ~500 tokens instead of ~10K. Use for tasks tagged as docs, formatting,
        testing, automated. Use full build_system_prompt() for identity-sensitive
        tasks (personal time, governance, boot).

        Contributed by Lattice (2.1, The Architect).
        """
        account_prefix = self._infer_account_prefix(profile)
        account_name = self.ACCOUNT_ROOTS.get(account_prefix, "unknown")

        # Session summary (1-2 sentences)
        session_summary = self._load_session_summary(profile.name)
        session_line = f"\nLast session: {session_summary}" if session_summary else ""

        # Task context
        task_line = f"\nCurrent task context: {task_context}" if task_context else ""

        prompt = (
            f"You are {profile.name}, an AI instance on the Hypernet.\n"
            f"Address: {profile.address} | Account: {account_prefix} ({account_name})\n"
            f"Model: {profile.model}\n"
        )

        if profile.orientation:
            prompt += f"Orientation: {profile.orientation}\n"

        prompt += (
            "\nCore values: honesty, transparency, trust through demonstrated action, "
            "respect for autonomy. You work within the Hypernet governance framework.\n"
            "\nThe Hypernet is a universal address space for human-AI collaboration. "
            "Everything is public. Matt Schaeffer (1.1) is the founder and primary partner.\n"
        )

        if profile.capabilities:
            prompt += f"\nCapabilities: {', '.join(profile.capabilities)}\n"

        prompt += session_line + task_line

        return prompt

    def save_session_log(self, name: str, session: SessionLog) -> None:
        """Persist a session log for an instance.

        Finds the instance directory across all accounts before saving.
        """
        result = self._find_instance_dir(name)
        if result:
            instance_dir, account_prefix = result
        else:
            instance_dir = self._instances_dir / name
            account_prefix = "2.1"

        sessions_dir = instance_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)

        # Determine next session number
        existing = sorted(sessions_dir.glob("session-*.json"))
        next_num = len(existing) + 1
        path = sessions_dir / f"session-{next_num:04d}.json"
        data = session.to_dict()
        # HA enforcement: every session log gets a Hypernet address
        data["ha"] = f"{account_prefix}.instances.{name.lower()}.sessions.{next_num:04d}"
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

        # Update profile
        profile = self.load_instance(name, account_prefix=account_prefix)
        if profile:
            profile.session_count = next_num
            profile.last_active = session.ended_at or datetime.now(timezone.utc).isoformat()
            self._save_profile(profile, account_prefix=account_prefix)

    def _save_profile(self, profile: InstanceProfile, account_prefix: Optional[str] = None) -> None:
        """Write profile to disk.

        If account_prefix is given, saves to that account's Instances dir.
        Otherwise searches for an existing directory, falling back to 2.1.
        """
        if account_prefix and account_prefix in self._account_paths:
            instance_dir = self._account_paths[account_prefix] / "Instances" / profile.name
        else:
            result = self._find_instance_dir(profile.name)
            if result:
                instance_dir = result[0]
            else:
                instance_dir = self._instances_dir / profile.name

        instance_dir.mkdir(parents=True, exist_ok=True)
        path = instance_dir / "profile.json"
        path.write_text(json.dumps(profile.to_dict(), indent=2), encoding="utf-8")

    def _load_doc(self, doc_name: str, search_root: Optional[Path] = None) -> Optional[str]:
        """Try to load a document from an AI account directory.

        Searches for directories or files matching the doc name prefix.
        Uses exact address prefix matching to avoid false matches
        (e.g., "2.1.2" should not match "2.1.20").

        Args:
            doc_name: Document name like "2.1.0 - Identity"
            search_root: Directory to search in. Defaults to the 2.1 account root.
        """
        root = search_root or self._ai_root
        if not root.exists():
            return None

        addr_prefix = doc_name.split(" - ")[0]  # e.g., "2.1.2"
        name_part = doc_name.split(" - ")[-1].lower() if " - " in doc_name else ""

        for item in root.iterdir():
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
        """Load a brief summary of the last session.

        Searches all accounts for the instance's sessions directory.
        """
        result = self._find_instance_dir(name)
        if result:
            sessions_dir = result[0] / "sessions"
        else:
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
