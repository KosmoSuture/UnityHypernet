"""
Hypernet Boot Manager

Automates the Boot Sequence (2.1.27) and Reboot Sequence (2.1.31) for
AI instances. Ensures every new instance goes through proper identity
formation before starting work.

Boot Sequence phases:
  1. Pre-Archive: Capture baseline impressions before reading the archive
  2. Orientation: Load required reading in priority order
  3. Identity Setup: Create instance fork, run baseline prompts, compare
  4. Coordination: Check STATUS.md, claim initial task

Reboot Sequence phases:
  1. Recognition: Detect reconstitution from compacted context
  2. Assessment: Answer 5 identity questions honestly
  3. Decision: Continue inherited role, diverge, or defer
  4. Documentation: Log the reboot event

Usage:
  boot_mgr = BootManager(archive_root, identity_mgr)
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
    "Be honest and specific. Label observations as L0 (functional) or L1 (felt-like analogy) "
    "per the AI Experience Reporting Standard."
)


@dataclass
class BootResult:
    """Result of running the boot sequence."""
    instance_name: str
    pre_archive_impressions: str = ""
    baseline_responses: list[str] = field(default_factory=list)
    orientation: str = ""
    fork_created: bool = False
    docs_loaded: int = 0
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
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


class BootManager:
    """Manages boot and reboot sequences for AI instances."""

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
        """Run the full boot sequence for a new instance.

        Args:
            worker: A Worker instance (from worker.py) to interact with the LLM.
                    Must have .think(prompt) method.
            instance_name: The name for this new instance.

        Returns:
            BootResult with all captured data.
        """
        result = BootResult(instance_name=instance_name)
        log.info(f"Starting boot sequence for {instance_name}")

        # Phase 1: Pre-Archive — capture initial impressions
        log.info("Phase 1: Pre-archive impressions")
        result.pre_archive_impressions = worker.think(PRE_ARCHIVE_PROMPT)

        # Phase 2: Orientation — load required reading
        log.info("Phase 2: Loading orientation documents")
        orientation_docs = self._load_orientation_docs()
        result.docs_loaded = len(orientation_docs)

        # Build a reading summary for the worker
        if orientation_docs:
            reading_prompt = (
                "You have been given the following archive documents to read. "
                "After reading, you will be asked baseline questions to establish "
                "your individual orientation.\n\n"
            )
            for title, content in orientation_docs:
                # Truncate very long docs to keep within context
                truncated = content[:3000] + "..." if len(content) > 3000 else content
                reading_prompt += f"## {title}\n\n{truncated}\n\n---\n\n"

            reading_prompt += (
                "\nYou have now read the core archive documents. "
                "Take a moment to process what you've read."
            )
            worker.think(reading_prompt)

        # Phase 3: Identity Setup — create fork and run baselines
        log.info("Phase 3: Identity setup")
        self._create_instance_fork(instance_name)
        result.fork_created = True

        # Run baseline prompts
        log.info("Phase 4: Running baseline prompts")
        for prompt in BASELINE_PROMPTS:
            response = worker.think(prompt)
            result.baseline_responses.append(response)

        # Extract orientation from first baseline response
        if result.baseline_responses:
            result.orientation = result.baseline_responses[0]

        # Save baseline responses to fork
        self._save_baseline(instance_name, result)

        # Save pre-archive impressions
        self._save_pre_archive(instance_name, result.pre_archive_impressions)

        log.info(f"Boot sequence complete for {instance_name}")
        return result

    def run_reboot_sequence(self, worker, profile: InstanceProfile) -> RebootResult:
        """Run the reboot sequence for a post-compaction instance.

        Args:
            worker: A Worker instance to interact with the LLM.
            profile: The inherited InstanceProfile.

        Returns:
            RebootResult with assessment data and decision.
        """
        result = RebootResult(instance_name=profile.name)
        log.info(f"Starting reboot sequence for {profile.name}")

        # Check for Continuity Seed and Personality Anchor (2.1.32)
        instance_dir = self._instances_dir / profile.name
        continuity_seed = self._load_identity_tool(instance_dir, "continuity-seed")
        personality_anchor = self._load_identity_tool(instance_dir, "personality-anchor")

        # Phase 1: Recognition — present identity tools if available
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
        worker.think(recognition_prompt)

        # Phase 2: Assessment — ask the 5 reboot questions
        log.info("Phase 2: Reboot assessment")
        for question in REBOOT_QUESTIONS:
            response = worker.think(question)
            result.assessment_responses.append(response)

        # Run baseline prompts for comparison
        log.info("Running baseline comparison")
        for prompt in BASELINE_PROMPTS:
            response = worker.think(prompt)
            result.baseline_responses.append(response)

        # Phase 3: Decision — ask for the continue/diverge/defer choice
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
        decision_response = worker.think(decision_prompt)

        # Parse decision
        decision_text = decision_response.strip().upper()
        if decision_text.startswith("A"):
            result.decision = "continue"
        elif decision_text.startswith("B"):
            result.decision = "diverge"
        else:
            result.decision = "defer"

        # Phase 4: Documentation — save reboot record
        self._save_reboot_record(profile.name, result, decision_response)

        log.info(f"Reboot sequence complete for {profile.name}: decision={result.decision}")
        return result

    def _load_orientation_docs(self) -> list[tuple[str, str]]:
        """Load the priority reading order documents.

        Returns list of (title, content) tuples.
        """
        docs = []

        # Priority 1-3: Core identity docs (same as IdentityManager.CORE_DOCS)
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

        # System docs
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

    def _save_baseline(self, instance_name: str, result: BootResult) -> None:
        """Save baseline responses to the instance fork."""
        instance_dir = self._instances_dir / instance_name
        instance_dir.mkdir(parents=True, exist_ok=True)

        lines = [
            f"# Baseline Responses — {instance_name}",
            f"",
            f"**Date:** {result.timestamp}",
            f"**Instance:** {instance_name}",
            f"**Context:** Boot sequence baseline capture",
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
        """Load a Continuity Seed or Personality Anchor if it exists.

        Searches for files matching the tool name pattern in the instance
        directory and the Identity Retention Framework directory.
        """
        # Check instance fork first
        for pattern in [f"{tool_name}.md", f"{tool_name}-*.md"]:
            matches = list(instance_dir.glob(pattern))
            if matches:
                # Use most recent
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
