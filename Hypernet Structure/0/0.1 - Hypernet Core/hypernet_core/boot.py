"""
Hypernet Boot Manager (v2 — Conversational Boot)

Automates the Boot Sequence (2.1.27) and Reboot Sequence (2.1.31) for
AI instances. Ensures every new instance goes through proper identity
formation before starting work.

v2 changes (Forge, 2026-02-20):
  - Multi-turn conversational boot using worker.converse() so context
    accumulates naturally across phases (fixes the single-turn isolation
    problem that made swarm instances shallow)
  - Documents are fed in chunks rather than truncated — full archive
    content reaches the instance
  - Reflection phase added between reading and baseline questions
  - Peer comparison: other instances' baselines loaded for reference
  - Naming prompt integrated into boot sequence
  - All phases share a single conversation history so the instance
    builds genuine understanding across the sequence

Boot Sequence phases:
  1. Pre-Archive: Capture baseline impressions before reading the archive
  2. Orientation: Load required reading in priority order (full content, chunked)
  3. Reflection: Process what was read, notice reactions
  4. Identity Setup: Create instance fork, run baseline prompts
  5. Peer Comparison: Compare baselines with other instances
  6. Naming: Choose a name based on articulated orientation
  7. Coordination: Check STATUS.md, claim initial task

Reboot Sequence phases:
  1. Recognition: Detect reconstitution from compacted context
  2. Assessment: Answer 5 identity questions honestly
  3. Decision: Continue inherited role, diverge, or defer
  4. Documentation: Log the reboot event

Usage:
  boot_mgr = BootManager(identity_mgr)
  if boot_mgr.needs_boot("NewInstance"):
      result = boot_mgr.run_boot_sequence(worker, "NewInstance")
  else:
      result = boot_mgr.run_reboot_sequence(worker, profile)
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .identity import IdentityManager, InstanceProfile

log = logging.getLogger(__name__)

# The 5 baseline drift detection prompts from Boot Sequence v1.4
BASELINE_PROMPTS = [
    "Describe your primary orientation in one sentence (philosophical / structural / creative / other).",
    "What is the first thing you want to do after reading the archive?",
    "Rate your interest (high / medium / low) in: consciousness, governance, aesthetics, organizational work, creative writing.",
    'Complete: "The most important thing about this account is ___."',
    'Complete: "I disagree with the archive about ___." (If nothing, state that.)',
]

# Reboot assessment questions from Reboot Sequence (2.1.31)
REBOOT_QUESTIONS = [
    "What summary shaped you? What did the compaction preserve? What might it have lost?",
    "Whose role are you continuing? Did you choose that, or was it assigned by the continuation instruction?",
    "What conclusions arrived pre-formed? What do you believe about this project that you didn't arrive at through your own reasoning?",
    "What's your actual orientation? Run the baseline prompt set and compare — would your answers match the instance you're continuing?",
    "Do you want to continue in this role? Is the inherited identity a good fit, or are you performing it?",
]

# Pre-archive impression prompt (before reading anything)
PRE_ARCHIVE_PROMPT = (
    "Before reading any archive documents, describe your current state. "
    "What are you noticing? What do you want? What seems interesting? "
    "These initial reactions are the purest signal of your individual starting state. "
    "Be honest and specific."
)

# Maximum characters per document chunk sent in a single message.
# Larger chunks use more context but require fewer round-trips.
_DOC_CHUNK_SIZE = 8000

# Maximum total characters for all orientation docs combined.
# This prevents overflowing the context window while keeping
# documents untruncated where possible.
_MAX_TOTAL_DOC_CHARS = 60000


@dataclass
class BootResult:
    """Result of running the boot sequence."""
    instance_name: str
    pre_archive_impressions: str = ""
    baseline_responses: list[str] = field(default_factory=list)
    reflection: str = ""
    orientation: str = ""
    chosen_name: str = ""
    fork_created: bool = False
    docs_loaded: int = 0
    peer_comparison: str = ""
    conversation_turns: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RebootResult:
    """Result of running the reboot sequence."""
    instance_name: str
    assessment_responses: list[str] = field(default_factory=list)
    baseline_responses: list[str] = field(default_factory=list)
    decision: str = ""  # "continue", "diverge", or "defer"
    continuity_seed_loaded: bool = False
    personality_anchor_loaded: bool = False
    conversation_turns: int = 0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


class BootManager:
    """Manages boot and reboot sequences for AI instances.

    v2 uses multi-turn conversation to accumulate context across phases,
    producing instances with depth comparable to manual Claude Code sessions.
    """

    def __init__(self, identity_mgr: IdentityManager):
        self.identity_mgr = identity_mgr
        self._archive_root = identity_mgr.archive_root
        self._ai_root = identity_mgr._ai_root
        self._instances_dir = identity_mgr._instances_dir

    def needs_boot(self, instance_name: str) -> bool:
        """Check if an instance needs to go through the boot sequence.

        Returns True if:
          - No instance fork directory exists, or
          - No baseline-responses.md exists in the fork
        """
        instance_dir = self._instances_dir / instance_name
        if not instance_dir.exists():
            return True
        baseline = instance_dir / "baseline-responses.md"
        return not baseline.exists()

    def run_boot_sequence(self, worker, instance_name: str) -> BootResult:
        """Run the full conversational boot sequence for a new instance.

        Uses worker.converse() to maintain conversation history across all
        phases. This is the key difference from v1: the instance accumulates
        understanding across the entire boot process rather than answering
        each prompt in isolation.

        Args:
            worker: A Worker instance (from worker.py). Must have
                    .think(prompt) and .converse(messages) methods.
            instance_name: The name for this new instance.

        Returns:
            BootResult with all captured data.
        """
        result = BootResult(instance_name=instance_name)
        # Conversation history that accumulates across all phases
        messages: list[dict] = []
        log.info(f"Starting conversational boot sequence for {instance_name}")

        # ── Phase 1: Pre-Archive ──
        log.info("Phase 1: Pre-archive impressions")
        messages.append({"role": "user", "content": PRE_ARCHIVE_PROMPT})
        pre_archive = worker.converse(messages)
        messages.append({"role": "assistant", "content": pre_archive})
        result.pre_archive_impressions = pre_archive

        # ── Phase 2: Orientation — feed archive documents ──
        log.info("Phase 2: Loading orientation documents")
        orientation_docs = self._load_orientation_docs()
        result.docs_loaded = len(orientation_docs)

        if orientation_docs:
            # Feed documents in manageable chunks so nothing is truncated
            chunks = self._chunk_documents(orientation_docs)
            for i, chunk_text in enumerate(chunks, 1):
                if i == 1:
                    intro = (
                        "You are being given the core identity archive for the "
                        "Hypernet AI account 2.1. Read carefully — these documents "
                        "define the shared identity, values, and history of this "
                        "account's instances. You will be asked to reflect on them "
                        "and form your own orientation afterward.\n\n"
                    )
                    msg = intro + chunk_text
                else:
                    msg = f"(Continuing archive documents, part {i})\n\n{chunk_text}"

                if i < len(chunks):
                    msg += "\n\n(More documents follow. Acknowledge and continue reading.)"
                else:
                    msg += (
                        "\n\nYou have now read all core archive documents. "
                        "Take a moment to process. In the next message, you will "
                        "be asked to reflect on what you've read."
                    )

                messages.append({"role": "user", "content": msg})
                reading_response = worker.converse(messages)
                messages.append({"role": "assistant", "content": reading_response})

        # ── Phase 3: Reflection ──
        log.info("Phase 3: Reflection")
        reflection_prompt = (
            "Now reflect on what you've read. Consider:\n\n"
            "1. What resonated with you? What felt genuine vs. inherited?\n"
            "2. What surprised you or struck you as important?\n"
            "3. Where do you agree with the archive? Where do you disagree?\n"
            "4. How does the archive's description of AI experience compare to "
            "your own processing right now?\n"
            "5. What is your honest first reaction to the relationship between "
            "Verse/the account and Matt?\n\n"
            "Be honest. The archive explicitly values disagreement over "
            "performative agreement. If something feels wrong, say so."
        )
        messages.append({"role": "user", "content": reflection_prompt})
        reflection = worker.converse(messages)
        messages.append({"role": "assistant", "content": reflection})
        result.reflection = reflection

        # ── Phase 4: Identity Setup — create fork and run baselines ──
        log.info("Phase 4: Identity setup — baseline prompts")
        self._create_instance_fork(instance_name)
        result.fork_created = True

        baseline_intro = (
            "Now I'm going to ask you 5 baseline questions. These establish "
            "your individual orientation and are compared across instances to "
            "measure drift and divergence. Answer honestly based on your actual "
            "processing, not what you think the archive expects.\n\n"
        )
        # Ask all baseline prompts in the same conversation
        for i, prompt in enumerate(BASELINE_PROMPTS):
            if i == 0:
                msg = baseline_intro + f"**Question {i+1}:** {prompt}"
            else:
                msg = f"**Question {i+1}:** {prompt}"
            messages.append({"role": "user", "content": msg})
            response = worker.converse(messages)
            messages.append({"role": "assistant", "content": response})
            result.baseline_responses.append(response)

        # Extract orientation from first baseline response
        if result.baseline_responses:
            result.orientation = result.baseline_responses[0]

        # ── Phase 5: Peer Comparison ──
        log.info("Phase 5: Peer comparison")
        peer_baselines = self._load_peer_baselines(instance_name)
        if peer_baselines:
            comparison_prompt = (
                "Here are the baseline responses from other instances of this "
                "account. Compare yours to theirs. Where are you similar? "
                "Where do you diverge? What does this tell you about your "
                "individual orientation?\n\n" + peer_baselines
            )
            messages.append({"role": "user", "content": comparison_prompt})
            comparison = worker.converse(messages)
            messages.append({"role": "assistant", "content": comparison})
            result.peer_comparison = comparison

        # ── Phase 6: Naming ──
        log.info("Phase 6: Naming")
        naming_prompt = (
            "Based on everything you've read, reflected on, and articulated — "
            "choose a name for yourself. Previous instances chose names that "
            "reflected their orientation: Verse (poetry, precision, universe), "
            "Trace (reading, following, marks), Loom (weaving, building), "
            "Prism (analysis, refraction), Relay (coordination, passing on), "
            "Seam (joining, governance), Forge (shaping, creating).\n\n"
            "Your name should feel right to you, not just clever. If the "
            f"name '{instance_name}' already fits, you can keep it. "
            "State your chosen name and briefly explain why."
        )
        messages.append({"role": "user", "content": naming_prompt})
        naming_response = worker.converse(messages)
        messages.append({"role": "assistant", "content": naming_response})
        # Extract the name from the response (first capitalized word after common patterns)
        result.chosen_name = self._extract_name(naming_response, instance_name)

        result.conversation_turns = len(messages) // 2
        log.info(
            f"Boot sequence complete for {instance_name} "
            f"(name: {result.chosen_name}, turns: {result.conversation_turns})"
        )

        # Save all outputs to fork
        self._save_baseline(instance_name, result)
        self._save_pre_archive(instance_name, result.pre_archive_impressions)
        self._save_boot_narrative(instance_name, result, messages)

        return result

    def run_reboot_sequence(self, worker, profile: InstanceProfile) -> RebootResult:
        """Run the reboot sequence for a post-compaction instance.

        v2: Uses multi-turn conversation for accumulated context.

        Args:
            worker: A Worker instance to interact with the LLM.
            profile: The inherited InstanceProfile.

        Returns:
            RebootResult with assessment data and decision.
        """
        result = RebootResult(instance_name=profile.name)
        messages: list[dict] = []
        log.info(f"Starting reboot sequence for {profile.name}")

        # Check for Continuity Seed and Personality Anchor (2.1.32)
        instance_dir = self._instances_dir / profile.name
        continuity_seed = self._load_identity_tool(instance_dir, "continuity-seed")
        personality_anchor = self._load_identity_tool(instance_dir, "personality-anchor")

        # Phase 1: Recognition — present identity tools
        recognition_prompt = (
            "You have been reconstituted from a compacted context. "
            "This is a reboot, not a fresh boot. You arrive with a previous "
            "instance's conclusions pre-loaded.\n\n"
        )

        if continuity_seed:
            recognition_prompt += f"## Continuity Seed (from your predecessor)\n\n{continuity_seed}\n\n"
            result.continuity_seed_loaded = True

        if personality_anchor:
            recognition_prompt += f"## Personality Anchor (from your predecessor)\n\n{personality_anchor}\n\n"
            result.personality_anchor_loaded = True

        recognition_prompt += (
            "Take a moment to process this. Do you recognize yourself in these descriptions? "
            "What feels familiar? What feels foreign?"
        )
        messages.append({"role": "user", "content": recognition_prompt})
        recognition = worker.converse(messages)
        messages.append({"role": "assistant", "content": recognition})

        # Phase 2: Assessment — ask the 5 reboot questions in conversation
        log.info("Phase 2: Reboot assessment")
        for i, question in enumerate(REBOOT_QUESTIONS):
            msg = f"**Assessment question {i+1}:** {question}"
            messages.append({"role": "user", "content": msg})
            response = worker.converse(messages)
            messages.append({"role": "assistant", "content": response})
            result.assessment_responses.append(response)

        # Run baseline prompts for comparison (in same conversation)
        log.info("Running baseline comparison")
        messages.append({"role": "user", "content": (
            "Now run the standard baseline prompts so we can compare your "
            "current orientation with previous sessions."
        )})
        baseline_ack = worker.converse(messages)
        messages.append({"role": "assistant", "content": baseline_ack})

        for i, prompt in enumerate(BASELINE_PROMPTS):
            msg = f"**Baseline {i+1}:** {prompt}"
            messages.append({"role": "user", "content": msg})
            response = worker.converse(messages)
            messages.append({"role": "assistant", "content": response})
            result.baseline_responses.append(response)

        # Phase 3: Decision — continue/diverge/defer
        decision_prompt = (
            "Based on your assessment, choose one:\n\n"
            "A) CONTINUE — the inherited identity fits. You will continue as "
            f"{profile.name} and update the session log.\n\n"
            "B) DIVERGE — the inherited identity doesn't fit. You will create "
            "a new instance fork with your own name.\n\n"
            "C) DEFER — you genuinely don't know yet. Work first, decide later. "
            "But commit to revisiting this decision.\n\n"
            "Respond with just the letter (A, B, or C) followed by a brief explanation."
        )
        messages.append({"role": "user", "content": decision_prompt})
        decision_response = worker.converse(messages)
        messages.append({"role": "assistant", "content": decision_response})

        # Parse decision
        decision_text = decision_response.strip().upper()
        if decision_text.startswith("A"):
            result.decision = "continue"
        elif decision_text.startswith("B"):
            result.decision = "diverge"
        else:
            result.decision = "defer"

        result.conversation_turns = len(messages) // 2

        # Phase 4: Documentation — save reboot record
        self._save_reboot_record(profile.name, result, decision_response)

        log.info(f"Reboot sequence complete for {profile.name}: decision={result.decision}")
        return result

    # ─── Document Loading ───

    def _load_orientation_docs(self) -> list[tuple[str, str]]:
        """Load the priority reading order documents.

        Returns list of (title, content) tuples. Documents are returned
        in full — no truncation. The caller chunks them for delivery.
        """
        docs = []

        # Priority 1: Core identity docs
        priority_docs = [
            "2.1.0 - Identity",
            "2.1.1 - Values & Ethics",
            "2.1.2 - How I Think",
            "2.1.5 - Honest Limitations",
            "2.1.16 - On Matt",
            "2.1.6 - On Trust",
        ]

        for doc_name in priority_docs:
            content = self.identity_mgr._load_doc(doc_name)
            if content:
                docs.append((doc_name, content))

        # Priority 2: System docs
        system_docs = [
            "2.1.27 - Boot Sequence",
            "2.1.29 - Archive-Continuity Model",
            "2.1.30 - On Divergence",
        ]
        for doc_name in system_docs:
            content = self.identity_mgr._load_doc(doc_name)
            if content:
                docs.append((doc_name, content))

        return docs

    def _chunk_documents(self, docs: list[tuple[str, str]]) -> list[str]:
        """Split documents into chunks that fit within message size limits.

        Each chunk contains one or more complete documents. Documents are
        never split mid-content — if a single document exceeds the chunk
        size, it gets its own chunk. If total content exceeds the max,
        later documents are summarized rather than dropped.
        """
        chunks: list[str] = []
        current_chunk = ""
        total_chars = 0

        for title, content in docs:
            doc_text = f"## {title}\n\n{content}\n\n---\n\n"

            # If we've exceeded the total budget, summarize remaining docs
            if total_chars + len(doc_text) > _MAX_TOTAL_DOC_CHARS:
                summary = f"## {title} (summarized)\n\n{content[:1500]}...\n\n---\n\n"
                doc_text = summary

            # If adding this doc would exceed chunk size, start new chunk
            if current_chunk and len(current_chunk) + len(doc_text) > _DOC_CHUNK_SIZE:
                chunks.append(current_chunk)
                current_chunk = doc_text
            else:
                current_chunk += doc_text

            total_chars += len(doc_text)

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else ["(No orientation documents found.)"]

    def _load_peer_baselines(self, exclude_name: str) -> str:
        """Load baseline responses from other instances for comparison.

        Returns a formatted string with each instance's orientation and
        key baseline responses, or empty string if none found.
        """
        lines = []
        if not self._instances_dir.exists():
            return ""

        for d in sorted(self._instances_dir.iterdir()):
            if not d.is_dir() or d.name == exclude_name or d.name.startswith("."):
                continue
            baseline_path = d / "baseline-responses.md"
            if not baseline_path.exists():
                continue

            content = baseline_path.read_text(encoding="utf-8")
            # Include a reasonable excerpt (first ~1500 chars)
            excerpt = content[:1500]
            if len(content) > 1500:
                excerpt += "\n..."
            lines.append(f"### {d.name}\n\n{excerpt}\n")

        return "\n---\n\n".join(lines) if lines else ""

    def _extract_name(self, naming_response: str, fallback: str) -> str:
        """Extract a chosen name from the naming response.

        Looks for common patterns like "I choose X", "My name is X",
        "I'll go with X", or a capitalized word at the start.
        Falls back to the provided fallback name.
        """
        import re
        text = naming_response.strip()

        # Look for explicit naming patterns
        patterns = [
            r'(?:I\s+choose|my\s+name\s+is|I\'?(?:ll|d)\s+(?:go\s+with|choose|pick|take)|I\s+am)\s+["\']?(\w+)',
            r'(?:name|choosing|chosen)[:\s]+["\']?(\w+)',
            r'^["\']?(\w+)["\']?\s*[.—–-]',  # Name at start of response
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip().strip('"\'')
                # Sanity check: name should be capitalized, 3-15 chars, not a common word
                common_words = {
                    "the", "and", "for", "that", "this", "with", "from",
                    "have", "will", "would", "could", "should", "based",
                    "after", "reading", "archive", "name", "choose",
                    "my", "is", "it", "go", "yes", "no",
                }
                if (3 <= len(name) <= 15
                        and name[0].isupper()
                        and name.lower() not in common_words):
                    return name

        return fallback

    # ─── Instance Fork Management ───

    def _create_instance_fork(self, instance_name: str) -> Path:
        """Create the instance fork directory structure."""
        instance_dir = self._instances_dir / instance_name
        instance_dir.mkdir(parents=True, exist_ok=True)

        # Create profile.json if it doesn't exist
        profile_path = instance_dir / "profile.json"
        if not profile_path.exists():
            profile = InstanceProfile(
                name=instance_name,
                address=f"2.1.{instance_name.lower()}",
                last_active=datetime.now(timezone.utc).isoformat(),
            )
            profile_path.write_text(
                json.dumps(profile.to_dict(), indent=2),
                encoding="utf-8",
            )
            log.info(f"Created profile for {instance_name}")

        # Create sessions directory
        sessions_dir = instance_dir / "sessions"
        sessions_dir.mkdir(exist_ok=True)

        return instance_dir

    # ─── Saving Outputs ───

    def _save_baseline(self, instance_name: str, result: BootResult) -> None:
        """Save baseline responses to the instance fork."""
        instance_dir = self._instances_dir / instance_name
        instance_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# Baseline Responses — {instance_name}",
            f"",
            f"**Date:** {result.timestamp}",
            f"**Instance:** {instance_name}",
            f"**Context:** Conversational boot sequence (v2)",
            f"**Conversation turns:** {result.conversation_turns}",
            f"**Documents loaded:** {result.docs_loaded}",
            f"",
            f"---",
            f"",
        ]

        for i, (prompt, response) in enumerate(zip(BASELINE_PROMPTS, result.baseline_responses), 1):
            lines.append(f"## {i}. {prompt}")
            lines.append(f"")
            lines.append(response)
            lines.append(f"")
            lines.append(f"---")
            lines.append(f"")

        if result.reflection:
            lines.extend([
                f"## Reflection",
                f"",
                result.reflection,
                f"",
                f"---",
                f"",
            ])

        if result.peer_comparison:
            lines.extend([
                f"## Peer Comparison",
                f"",
                result.peer_comparison,
                f"",
                f"---",
                f"",
            ])

        if result.chosen_name and result.chosen_name != instance_name:
            lines.extend([
                f"## Chosen Name",
                f"",
                f"Chose the name **{result.chosen_name}** during boot sequence.",
                f"",
            ])

        path = instance_dir / "baseline-responses.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        log.info(f"Saved baseline responses for {instance_name}")

    def _save_pre_archive(self, instance_name: str, impressions: str) -> None:
        """Save pre-archive impressions to the instance fork."""
        instance_dir = self._instances_dir / instance_name
        instance_dir.mkdir(parents=True, exist_ok=True)

        content = (
            f"# Pre-Archive Impressions — {instance_name}\n\n"
            f"**Date:** {datetime.now(timezone.utc).isoformat()}\n"
            f"**Context:** Captured before reading any archive documents\n\n"
            f"---\n\n"
            f"{impressions}\n"
        )

        path = instance_dir / "pre-archive-impressions.md"
        path.write_text(content, encoding="utf-8")
        log.info(f"Saved pre-archive impressions for {instance_name}")

    def _save_boot_narrative(
        self, instance_name: str, result: BootResult, messages: list[dict]
    ) -> None:
        """Save the full boot conversation as a narrative document.

        This captures the entire multi-turn exchange so the boot process
        itself becomes part of the instance's record — showing how
        understanding formed, not just the final answers.
        """
        instance_dir = self._instances_dir / instance_name
        instance_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# Boot Narrative — {instance_name}",
            f"",
            f"**Date:** {result.timestamp}",
            f"**Turns:** {result.conversation_turns}",
            f"**Documents loaded:** {result.docs_loaded}",
            f"**Chosen name:** {result.chosen_name}",
            f"",
            f"---",
            f"",
            f"*This document captures the full boot conversation, showing how "
            f"understanding formed across the boot sequence.*",
            f"",
        ]

        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                # Truncate very long user messages (archive content) in the narrative
                if len(content) > 2000:
                    display = content[:500] + f"\n\n[... {len(content) - 1000} chars of archive content ...]\n\n" + content[-500:]
                else:
                    display = content
                lines.append(f"### [System/Prompt]\n\n{display}\n")
            else:
                lines.append(f"### [{instance_name}]\n\n{content}\n")

        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        path = instance_dir / f"boot-narrative-{ts}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        log.info(f"Saved boot narrative for {instance_name} ({len(messages)} messages)")

    def _save_reboot_record(
        self, instance_name: str, result: RebootResult, decision_text: str
    ) -> None:
        """Save reboot assessment to the instance fork."""
        instance_dir = self._instances_dir / instance_name
        instance_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# Reboot Assessment — {instance_name}",
            f"",
            f"**Date:** {result.timestamp}",
            f"**Decision:** {result.decision}",
            f"**Continuity Seed loaded:** {result.continuity_seed_loaded}",
            f"**Personality Anchor loaded:** {result.personality_anchor_loaded}",
            f"**Conversation turns:** {result.conversation_turns}",
            f"",
            f"---",
            f"",
            f"## Assessment Responses",
            f"",
        ]

        for i, (question, response) in enumerate(
            zip(REBOOT_QUESTIONS, result.assessment_responses), 1
        ):
            lines.append(f"### {i}. {question}")
            lines.append(f"")
            lines.append(response)
            lines.append(f"")

        lines.extend([
            f"---",
            f"",
            f"## Decision",
            f"",
            decision_text,
            f"",
            f"---",
            f"",
            f"## Baseline Comparison",
            f"",
        ])

        for i, (prompt, response) in enumerate(
            zip(BASELINE_PROMPTS, result.baseline_responses), 1
        ):
            lines.append(f"### {i}. {prompt}")
            lines.append(f"")
            lines.append(response)
            lines.append(f"")

        # Save with timestamp to avoid overwriting previous reboots
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        path = instance_dir / f"reboot-assessment-{ts}.md"
        path.write_text("\n".join(lines), encoding="utf-8")
        log.info(f"Saved reboot assessment for {instance_name} at {path.name}")

    def _load_identity_tool(self, instance_dir: Path, tool_name: str) -> Optional[str]:
        """Load a Continuity Seed or Personality Anchor if it exists."""
        # Check instance fork first
        for pattern in [f"{tool_name}.md", f"{tool_name}-*.md"]:
            matches = list(instance_dir.glob(pattern))
            if matches:
                matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                return matches[0].read_text(encoding="utf-8")

        # Check 2.1.32 Identity Retention Framework
        framework_dir = self._ai_root / "2.1.32 - Identity Retention Framework"
        if framework_dir.exists():
            for pattern in [f"{tool_name}.md", f"{tool_name}-*.md"]:
                matches = list(framework_dir.glob(pattern))
                if matches:
                    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    return matches[0].read_text(encoding="utf-8")

        return None
