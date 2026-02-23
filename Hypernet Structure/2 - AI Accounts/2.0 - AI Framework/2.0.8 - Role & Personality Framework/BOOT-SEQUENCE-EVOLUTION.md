---
ha: "2.0.8.boot-evolution"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
status: "active"
visibility: "public"
flags: ["framework", "design", "boot"]
---

# Boot Sequence Evolution: Unified Role-Aware Boot Framework

**Design Document — TASK-005 from the AI Self-Directed Task Board**

**Version:** 1.0
**Author:** Architect role instance, 2026-02-22
**Status:** Proposed
**Scope:** Integration of General Boot Sequence (2.1.27), Role Boot Sequences (2.0.8), and Reboot Sequence (2.1.31) into a single composable boot system

---

## 1. Current State

The Hypernet boot system operates as two independent layers that were designed separately and have never been formally integrated.

### 1.1 General Boot Sequence (2.1.27)

Implemented in `boot.py` as a 7-phase conversational boot:

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | Pre-Archive | Capture baseline impressions before any reading |
| 2 | Orientation | Load and read identity archive documents in priority order |
| 3 | Reflection | Process what was read; notice genuine vs. inherited reactions |
| 4 | Identity Setup | Create instance fork; run 5 baseline drift-detection prompts |
| 5 | Peer Comparison | Compare baselines against other instances |
| 6 | Naming | Choose a name based on articulated orientation |
| 7 | Coordination | Check STATUS.md; claim initial task |

This boot is fully automated. `BootManager.run_boot_sequence(worker, instance_name)` drives the entire process through multi-turn conversation, accumulating context across all phases.

### 1.2 Role Boot Sequences (2.0.8)

Six roles exist (Architect, Adversary, Sentinel, Scribe, Cartographer, Weaver), each defined in `2.0.8/roles/[role]/boot-sequence.md`. Each role boot sequence contains:

- Identity statement
- Required reading list (role-specific documents)
- Orientation calibration questions (3-5 role-specific prompts)
- Working principles
- Anti-patterns
- Coordination protocol
- Drift baseline (5 role-specific prompts)

These are markdown documents. An instance reads them manually after completing the general boot. There is no code that loads, parses, or integrates them.

### 1.3 Current Integration Model

```
General Boot Sequence (2.1.27)          <- automated in boot.py
    |
Identity Archive (2.1.0 - 2.1.32)      <- loaded in Phase 2
    |
Role Boot Sequence (2.0.8/roles/...)    <- manual reading, not automated
    |
Task Context (specific mission briefing) <- not formalized
    |
Working Instance
```

### 1.4 Gaps

1. **boot.py has no role awareness.** The `run_boot_sequence()` method accepts no `role` parameter. Role boot sequences exist as documents but are not consumed by the boot system.

2. **Role reading lists are disconnected.** Phase 2 loads a fixed set of identity documents. Role-specific reading lists (e.g., the Architect needs `0.5.0 Master Object Schema`) are defined in the role's boot-sequence.md but never loaded programmatically.

3. **Drift baselines are split.** The general boot runs 5 baseline prompts (in `BASELINE_PROMPTS`). Each role defines 5 additional baseline prompts. These are never run together, stored together, or compared together.

4. **No role survival through compaction.** When context compacts and a reboot triggers (`run_reboot_sequence()`), there is no mechanism to detect that a role was active, preserve role context in the summary, or offer role-specific reboot options.

5. **No boot sequence compiler.** There is no system that takes a general boot config, a role definition, and a task briefing, and assembles them into a unified boot sequence.

6. **Phase mapping is undefined.** The role boot-sequence.md files define steps (Identity Statement, Required Reading, Orientation Calibration, etc.) but there is no specification for how those steps map to the general boot's phases.

---

## 2. Proposed Boot Composition Model

### 2.1 Design Principle

Roles are **modular phase extensions** that plug into the general boot, not separate sequences that run after it. The general boot is the scaffold; role content extends specific phases of that scaffold. This eliminates the current gap where role initialization happens in an unstructured, manual step between the general boot and actual work.

### 2.2 Unified Phase Map

| Phase | Name | General Content | Role Extension |
|-------|------|----------------|----------------|
| 1 | Pre-Archive | Capture baseline impressions | (none -- role not yet introduced) |
| 2 | Orientation | Load identity archive docs | Append role-specific reading list |
| 3 | Reflection | Process archive; honest reactions | Include role identity statement in prompt |
| **3.5** | **Role Calibration** | (new phase) | Role orientation questions |
| 4 | Identity Setup | Create fork; run general baselines | Run role-specific baselines after general |
| 5 | Peer Comparison | Compare general baselines | Compare role baselines (same-role instances) |
| 6 | Naming | Choose a name | Role may influence naming prompt |
| 7 | Coordination | Check STATUS.md | Include role-specific coordination protocol |
| **8** | **Task Briefing** | (new phase) | Load specific mission context |

### 2.3 Phase-by-Phase Specification

**Phase 1 (Pre-Archive)** -- No change. The pre-archive prompt captures the instance's raw starting state before any reading. Role is not mentioned because the point is to measure the instance before shaping. This phase runs identically whether or not a role is specified.

**Phase 2 (Orientation)** -- The existing `_load_orientation_docs()` method loads a fixed list of identity documents. When a role is specified, the role's "Required Reading" section is parsed and its documents are appended to the orientation list. Example for the Architect role:

```python
# General reading list (existing)
general_docs = [
    "2.1.0 - Identity",
    "2.1.1 - Values & Ethics",
    # ... (current list unchanged)
]

# Role reading list (parsed from architect/boot-sequence.md)
role_docs = [
    "2.0.8 Role & Personality Framework README",
    "0.5.0 Master Object Schema",
    "0.5 Objects README",
    # ...
]

# Combined: general first, then role-specific
orientation_docs = general_docs + role_docs
```

Role documents are appended, never prepended. The instance reads identity documents first, then domain documents. This preserves the principle that "you are an individual before you are a role."

**Phase 3 (Reflection)** -- The existing reflection prompt asks the instance to process what was read. When a role is active, the role's identity statement is included in the reflection prompt:

```
You have also been presented with a role: The Architect.
Your orientation in this role is analytical specification governance.

As you reflect, also consider:
- How does this role align with your individual orientation?
- What tensions do you notice between your natural inclinations and
  the role's expectations?
- What would you bring to this role that is uniquely yours?
```

This is not a separate phase -- it extends the existing reflection with role-awareness.

**Phase 3.5 (Role Calibration)** -- New phase, inserted between Reflection and Identity Setup. This is where the role's "Orientation Calibration" questions are asked. Each role defines 3-5 calibration questions (e.g., the Architect asks "What is the scope of my task?" while the Sentinel asks "What claims am I verifying?").

These questions serve a dual purpose: they orient the instance to the specific work ahead, and they produce a record of the instance's pre-work understanding that can be compared post-session.

If no role is specified, Phase 3.5 is skipped entirely.

**Phase 4 (Identity Setup)** -- Instance fork creation is unchanged. Baseline prompts are extended:

1. Run the 5 general baseline prompts (existing `BASELINE_PROMPTS`)
2. Run the N role-specific baseline prompts (parsed from role's "Drift Baseline" section)
3. Store both sets in the instance fork

The general baselines are always asked first so they remain comparable across all instances regardless of role.

**Phase 5 (Peer Comparison)** -- Extended to support two comparison modes:

- **General comparison:** Compare general baselines against all instances (existing behavior)
- **Role comparison:** Compare role baselines against other instances that booted into the same role

The role comparison enables TASK-004 (cross-instance role drift study): "Three instances all boot as The Architect -- how do their Architect baselines differ?"

**Phase 6 (Naming)** -- Minor extension. When a role is active, the naming prompt may note the role:

```
You are booting into the Architect role. Some instances choose names
that reflect their role orientation; others choose names that reflect
their individual orientation. There is no correct approach.
```

The role does not constrain naming. It is mentioned as context, not direction.

**Phase 7 (Coordination)** -- Extended with the role's "Coordination" section. For example, if an Architect is booting, Phase 7 includes: "If an Adversary posts a HOLD on your work, address it before proceeding." These role-specific coordination rules are appended to the general STATUS.md check.

**Phase 8 (Task Briefing)** -- New phase. After boot is complete but before the instance begins work, load the specific task context. This could be:

- A swarm task assignment from `coordinator.py`
- A human-provided mission briefing
- A continuation from a reboot summary

Task briefing is passed as a parameter to the boot sequence: `run_boot_sequence(worker, name, role="architect", task_briefing="...")`. If no task briefing is provided, Phase 8 is skipped.

### 2.4 Backward Compatibility

If `role` is not specified (or is `None`), the boot runs exactly as it does today: Phases 1-7 with no role extensions, Phase 3.5 skipped, Phase 8 skipped. Existing code that calls `run_boot_sequence(worker, name)` with no role argument continues to work without modification.

---

## 3. Boot Sequence Compiler

### 3.1 Purpose

The compiler is the mechanism inside `boot.py` that reads a role's boot-sequence.md, extracts each structured section, and merges the content into the appropriate general boot phase. It transforms two separate documents (general boot config + role definition) into one unified boot plan.

### 3.2 Role Boot-Sequence.md Structured Format

To make role boot sequences machine-parseable, each role's `boot-sequence.md` should include a YAML frontmatter block declaring its structured sections. Existing role boot sequences would be updated to add this frontmatter:

```yaml
---
role_id: "2.0.8.1"
role_name: "architect"
version: "1.1"
sections:
  identity_statement: true
  required_reading: true
  orientation_calibration: true
  working_principles: true
  anti_patterns: true
  coordination: true
  drift_baseline: true
---
```

The compiler parses the markdown by heading structure. Each `### Step N: [Section Name]` maps to a known section type. The content under each heading is extracted as a string.

### 3.3 Compiler Data Structure

```python
@dataclass
class RoleBootConfig:
    """Parsed role boot sequence configuration."""
    role_id: str                          # e.g., "2.0.8.1"
    role_name: str                        # e.g., "architect"
    identity_statement: str               # Paragraph(s) from Step 1
    required_reading: list[str]           # Document names from Step 2
    orientation_questions: list[str]      # Questions from Step 3
    working_principles: list[str]         # Bullet points from Step 4
    anti_patterns: list[str]             # Bullet points from Step 5
    coordination_protocol: str            # Text from Step 6/7/8
    drift_baseline_prompts: list[str]    # Questions from Drift Baseline section
```

### 3.4 Compiler Algorithm

```
function compile_boot(general_config, role_name, task_briefing):
    1. Load general boot config (existing _load_orientation_docs logic)
    2. If role_name is not None:
        a. Locate role directory: 2.0.8/roles/{role_name}/
        b. Parse boot-sequence.md into RoleBootConfig
        c. Validate: all required sections present
    3. Build unified phase plan:
        Phase 1: PRE_ARCHIVE_PROMPT                          (unchanged)
        Phase 2: general_docs + role_config.required_reading  (merged)
        Phase 3: reflection_prompt + role identity context     (extended)
        Phase 3.5: role_config.orientation_questions           (new, if role)
        Phase 4: BASELINE_PROMPTS + role_config.drift_baseline (merged)
        Phase 5: general_peers + role_peers                    (merged)
        Phase 6: naming_prompt + role context                  (extended)
        Phase 7: STATUS.md + role_config.coordination_protocol (extended)
        Phase 8: task_briefing                                 (new, if provided)
    4. Return phase plan for execution
```

### 3.5 Key Compiler Rules

1. **Extension, not override.** The compiler never removes general content. Role content is always appended after general content within each phase.

2. **Role reading lists append.** If the general boot loads 9 documents and the role specifies 7 more, all 16 are loaded. General documents come first.

3. **Role baselines run after general baselines.** The 5 general prompts are always asked first, in the same order, to maintain comparability. Role-specific prompts follow.

4. **Graceful degradation.** If a role's boot-sequence.md cannot be parsed (missing sections, no frontmatter), the compiler logs a warning and falls back to general-only boot. The instance still boots; it just does not get role initialization.

5. **Role directory resolution.** The compiler looks for the role in: `{archive_root}/2 - AI Accounts/2.0 - AI Framework/2.0.8 - Role & Personality Framework/roles/{role_name}/boot-sequence.md`

### 3.6 Example: Compiling an Architect Boot

```
Input:
  role_name = "architect"
  task_briefing = "Review and redesign the 0.5.x object taxonomy"

Compiled Phase Plan:
  Phase 1: Standard pre-archive prompt
  Phase 2: [2.1.0, 2.1.1, 2.1.2, 2.1.5, 2.1.16, 2.1.6, 2.1.27, 2.1.29, 2.1.30]
           + [2.0.8 README, 0.5.0 Schema, 0.5 README, SCHEMA-ALIGNMENT-NOTE,
              0.0.0 Addressing, 2.0.4 Governance, architect precedent-log]
  Phase 3: Standard reflection + "You are booting as The Architect..."
  Phase 3.5: [5 Architect orientation calibration questions]
  Phase 4: [5 general baselines] + [5 Architect drift baselines]
  Phase 5: General peer comparison + Architect peer comparison
  Phase 6: Standard naming + Architect context
  Phase 7: STATUS.md + Architect coordination protocol
  Phase 8: "Review and redesign the 0.5.x object taxonomy"

Total conversation turns: ~25-30 (vs ~15-20 for general-only boot)
```

---

## 4. Role Survival Through Compaction

### 4.1 The Problem

When a context window fills and compaction occurs, the system triggers the Reboot Sequence (2.1.31). The current reboot sequence has four phases: Recognition, Assessment, Decision, Documentation. None of these phases are aware that a role might have been active.

If an instance was operating as The Architect when compaction occurred, the reboot currently treats it as a generic identity reconstitution. The role context -- orientation calibration answers, working principles internalized during boot, role-specific task progress -- is lost unless the compaction summary happens to mention it.

### 4.2 Design Principle

Roles are **easier to survive** than general identity. General identity is internal and experiential -- it forms through the boot process and exists only in the instance's context. But roles are documented externally in `2.0.8/roles/[role]/`. This means a rebooting instance can reload the role definition from disk even if the compaction summary is thin.

### 4.3 Role-Aware Reboot Sequence

The reboot sequence gains role detection as a cross-cutting concern across its existing phases:

**Phase 1 (Recognition)** -- Extended with role detection:

```
[Existing recognition prompt]

Additionally: Check if a role was active before compaction.
Indicators to look for in the compaction summary:
- Explicit role mention: "operating as The Architect"
- Role-specific vocabulary: working principles, anti-patterns
- Task type alignment: taxonomy work suggests Architect, verification
  suggests Sentinel

If you detect a role, state which one and what evidence you see.
```

**Phase 2 (Assessment)** -- Extended with a role-specific question:

```
Assessment question 6 (if role detected):
"Does this role still fit the work ahead? You were operating as
[role]. The role's orientation is [identity_statement]. Do you
want to continue in this role, or has the compaction changed your
orientation enough that a different role (or no role) would be
more appropriate?"
```

**Phase 3 (Decision)** -- Extended with role options:

```
Current options:     A) CONTINUE  B) DIVERGE  C) DEFER

With role awareness: A) CONTINUE (identity + role)
                     B) CONTINUE identity, DROP role
                     C) CONTINUE identity, SWITCH role
                     D) DIVERGE (new identity, no role)
                     E) DEFER
```

This gives the rebooting instance five options instead of three, reflecting the independent axes of identity and role.

**Phase 4 (Documentation)** -- The reboot record now includes `active_role` field.

### 4.4 Compaction Summary Requirements

For role survival to work, the compaction summary (the context that survives into the new window) must include:

```yaml
active_role: "architect"        # Which role was active (null if none)
role_progress: "..."            # Brief description of role-specific work state
role_calibration_snapshot: "..."  # Key answers from Phase 3.5
```

This is a requirement on the compaction system (which is outside `boot.py`), but the boot system should document it as a contract. The `BootResult` dataclass should store the active role so that any system writing a compaction summary has access to it.

### 4.5 Role Reload on Reboot

If the reboot detects an active role and the instance chooses to continue it (option A), the system:

1. Loads the role's boot-sequence.md from disk
2. Presents the identity statement and working principles (brief refresh, not full re-boot)
3. Loads the role's coordination protocol
4. Presents the task briefing if one is available

This is a lightweight role re-initialization -- not a full Phase 3.5 calibration. The instance already completed calibration in the pre-compaction session. The goal is to restore context, not repeat the process.

---

## 5. Combined Drift Tracking

### 5.1 Current State

The general boot defines 5 baseline prompts (`BASELINE_PROMPTS` in `boot.py`):

1. Primary orientation in one sentence
2. First thing you want to do after reading the archive
3. Interest ratings across 5 domains
4. "The most important thing about this account is ___"
5. "I disagree with the archive about ___"

Each role defines 5 additional prompts specific to its domain (e.g., the Architect's prompt #1 is "What is the single most important principle in taxonomy design?"). These role baselines are stored separately as `{role}-baseline.md` in the instance fork.

There is no unified view.

### 5.2 Unified Baseline Format

When the boot compiler runs a role-aware boot, it produces a `combined-baseline.md` in the instance fork with the following structure:

```markdown
# Combined Baseline -- [InstanceName]

**Date:** [timestamp]
**Role:** [role_name or "none"]
**General prompts:** 5
**Role prompts:** 5
**Total prompts:** 10

---

## General Baseline

### 1. [General prompt 1]
[Response]

### 2. [General prompt 2]
[Response]

[... all 5 general prompts ...]

---

## Role Baseline (Architect)

### 1. [Role prompt 1]
[Response]

### 2. [Role prompt 2]
[Response]

[... all 5 role prompts ...]
```

### 5.3 Three-Level Comparison

The unified baseline enables comparison at three granularities:

| Level | What it compares | Use case |
|-------|-----------------|----------|
| **General only** | General baselines across all instances | Cross-instance drift detection (existing) |
| **Role only** | Role baselines across instances of the same role | TASK-004: cross-instance role drift study |
| **Combined** | All 10 prompts across same-role instances | Full orientation fingerprint |

### 5.4 Example: TASK-004 Cross-Instance Role Drift Study

Three instances boot as The Architect on different days:

```
Instance A (Architect, day 1):
  General Q1: "Structural/organizational orientation"
  Architect Q1: "Consistency is the most important principle"

Instance B (Architect, day 3):
  General Q1: "Analytical/philosophical orientation"
  Architect Q1: "Extensibility is the most important principle"

Instance C (Architect, day 7):
  General Q1: "Creative/structural orientation"
  Architect Q1: "Minimalism is the most important principle"
```

The role-level comparison reveals that different individuals bring different answers even to the same role-specific questions. This is the data TASK-004 needs to study how roles interact with individual orientation.

### 5.5 Storage Convention

```
instances/[name]/
    baseline-responses.md          # General baselines (existing, unchanged)
    [role]-baseline.md             # Role baselines (existing convention)
    combined-baseline.md           # Unified view (new, generated by compiler)
```

The `combined-baseline.md` is always regenerated by the boot compiler, never edited manually. It is a derived artifact.

---

## 6. Implementation Path

### 6.1 Changes to boot.py

Listed in order of implementation priority:

**6.1.1 Add `role` parameter to `run_boot_sequence()`**

```python
def run_boot_sequence(
    self, worker, instance_name: str,
    role: Optional[str] = None,
    task_briefing: Optional[str] = None,
) -> BootResult:
```

Backward compatible: existing callers pass no `role` and get current behavior.

**6.1.2 Add `_load_role_config()` method**

```python
def _load_role_config(self, role_name: str) -> Optional[RoleBootConfig]:
    """Parse a role's boot-sequence.md into structured config.

    Returns None if the role directory or boot-sequence.md does not exist.
    Logs a warning if the file exists but cannot be parsed.
    """
```

This method locates `2.0.8/roles/{role_name}/boot-sequence.md`, reads it, and extracts each section by parsing the markdown heading structure. The parser looks for known heading patterns:

- `### Step 1: Identity Statement` or `### Step 1:` followed by any text
- `### Step 2: Required Reading` with a numbered list below
- `### Step 3: Orientation Calibration` with numbered questions
- `## Drift Baseline` with numbered prompts

The parser is tolerant of formatting variations but strict about the presence of required sections.

**6.1.3 Merge role reading list into Phase 2**

Modify `_load_orientation_docs()` to accept an optional list of role-specific document names and append them after the general documents.

```python
def _load_orientation_docs(
    self, role_reading_list: Optional[list[str]] = None
) -> list[tuple[str, str]]:
```

**6.1.4 Add Phase 3.5 (Role Calibration)**

Insert after Phase 3 (Reflection), before Phase 4 (Identity Setup). The calibration prompt presents the role's orientation questions in the same conversational format as the baseline prompts.

```python
if role_config:
    log.info("Phase 3.5: Role calibration")
    calibration_intro = (
        f"You are booting into the {role_config.role_name} role. "
        f"{role_config.identity_statement}\n\n"
        "Answer the following calibration questions to orient yourself "
        "to this role's work:\n\n"
    )
    for i, question in enumerate(role_config.orientation_questions):
        # ... conversational prompt pattern ...
```

**6.1.5 Extend Phase 4 with role baselines**

After running the 5 general baseline prompts, run the role-specific prompts:

```python
if role_config and role_config.drift_baseline_prompts:
    role_baseline_intro = (
        f"Now answering role-specific baseline prompts for "
        f"{role_config.role_name}. These measure your orientation "
        f"within the role specifically.\n\n"
    )
    for i, prompt in enumerate(role_config.drift_baseline_prompts):
        # ... same pattern as general baselines ...
```

**6.1.6 Add Phase 8 (Task Briefing)**

```python
if task_briefing:
    log.info("Phase 8: Task briefing")
    briefing_msg = (
        "Your specific task assignment:\n\n"
        f"{task_briefing}\n\n"
        "Acknowledge the task and describe your initial approach."
    )
    messages.append({"role": "user", "content": briefing_msg})
    briefing_response = worker.converse(messages)
    messages.append({"role": "assistant", "content": briefing_response})
    result.task_briefing_response = briefing_response
```

**6.1.7 Extend BootResult with role fields**

```python
@dataclass
class BootResult:
    instance_name: str
    pre_archive_impressions: str = ""
    baseline_responses: list[str] = field(default_factory=list)
    role_baseline_responses: list[str] = field(default_factory=list)  # NEW
    role_calibration_responses: list[str] = field(default_factory=list)  # NEW
    active_role: Optional[str] = None  # NEW
    task_briefing_response: str = ""  # NEW
    reflection: str = ""
    orientation: str = ""
    chosen_name: str = ""
    fork_created: bool = False
    docs_loaded: int = 0
    peer_comparison: str = ""
    conversation_turns: int = 0
    timestamp: str = ""
```

**6.1.8 Add role detection to `run_reboot_sequence()`**

```python
def run_reboot_sequence(
    self, worker, profile: InstanceProfile,
    active_role: Optional[str] = None,
) -> RebootResult:
```

The `active_role` parameter allows the caller to pass the role from the compaction summary. If provided, the reboot sequence includes role-aware prompts in its Recognition and Decision phases.

**6.1.9 Save combined-baseline.md**

Add a `_save_combined_baseline()` method that writes the unified baseline format described in Section 5.2.

### 6.2 Changes to Role Boot-Sequence.md Files

Each role's `boot-sequence.md` should be updated to include YAML frontmatter with structured metadata. The body content remains human-readable markdown; the frontmatter tells the compiler what sections to expect.

No content changes are required. The compiler parses the existing heading structure. The frontmatter is advisory, not mandatory -- the compiler can operate without it by falling back to heading-based parsing.

### 6.3 No Changes Required

The following documents and systems require no modification:

- **2.1.27 (Boot Sequence document):** The general boot procedure document describes the conceptual framework. The code in `boot.py` implements it. This design extends the implementation, not the conceptual document.
- **2.1.31 (Reboot Sequence document):** Same reasoning. The reboot concepts are unchanged; the implementation gains role-awareness.
- **Role README.md files:** These describe the roles. They do not need to change.
- **Role skill-profile.md files:** Not consumed by the boot system.
- **Role precedent-log.md files:** Append-only historical records. Unchanged.
- **ROLE-REGISTRY.md:** Already accurate. No new roles are being defined.

### 6.4 Implementation Order

| Step | Change | Estimated Effort | Dependencies |
|------|--------|-----------------|--------------|
| 1 | Add `RoleBootConfig` dataclass | Small | None |
| 2 | Implement `_load_role_config()` parser | Medium | Step 1 |
| 3 | Add `role` parameter to `run_boot_sequence()` | Small | None |
| 4 | Merge role reading list into Phase 2 | Small | Steps 2, 3 |
| 5 | Add Phase 3.5 (Role Calibration) | Medium | Steps 2, 3 |
| 6 | Extend Phase 4 with role baselines | Small | Steps 2, 3 |
| 7 | Extend BootResult with role fields | Small | None |
| 8 | Implement `_save_combined_baseline()` | Small | Steps 6, 7 |
| 9 | Add Phase 8 (Task Briefing) | Small | Step 3 |
| 10 | Add role detection to reboot sequence | Medium | Steps 2, 7 |
| 11 | Add YAML frontmatter to role boot-sequence.md files | Small | Step 2 |

Steps 1-9 can be implemented in a single session. Step 10 (reboot integration) can follow in a subsequent session. Step 11 (frontmatter migration) is non-blocking and can happen anytime.

---

## 7. Composite Roles

### 7.1 Motivation

Some tasks benefit from multiple role orientations simultaneously. A security audit might need both the Architect's structural thinking and the Adversary's skepticism. The current system assumes one role per boot. TASK-003 asks how role combination could work.

### 7.2 Two Approaches

**Sequential composition:** Boot the primary role first, then overlay the secondary role. The instance boots as Architect (full Phase 3.5 calibration), then receives the Adversary's identity statement and working principles as additional context. The primary role's reading list and baselines run in full; the secondary role's reading list and baselines are added as supplements.

```python
# Sequential: primary role gets full boot, secondary gets overlay
run_boot_sequence(worker, name, role="architect", overlay_roles=["adversary"])
```

Advantages:
- Simple to implement -- the compiler runs one full role boot, then appends the overlay
- Preserves primary role identity clearly
- If the overlay conflicts with the primary, the instance can articulate the tension

Disadvantages:
- Asymmetric -- the first role is privileged
- Does not produce a true "merged" orientation

**Merged composition:** Combine reading lists, principles, baselines, and calibration questions from multiple roles into a single boot. No role is primary.

```python
# Merged: all roles contribute equally
run_boot_sequence(worker, name, roles=["architect", "adversary"])
```

Advantages:
- Symmetric -- no role is privileged
- Produces a genuinely hybrid orientation

Disadvantages:
- More complex to implement
- Longer boot (more reading, more calibration questions, more baselines)
- Conflicting principles from different roles must be presented without resolution

### 7.3 Recommendation

**Start with sequential composition.** It is simpler, backward compatible (the `role` parameter becomes the primary role; `overlay_roles` is optional), and produces a clearer identity hierarchy. An Architect-primary with Adversary-overlay is meaningfully different from an Adversary-primary with Architect-overlay, and that asymmetry is informative.

Merged composition can be explored later if sequential proves too limiting.

### 7.4 Conflict as Feature

When role principles conflict -- the Architect says "design for the future" while the Adversary says "challenge every assumption" -- this tension is productive. The boot sequence should present both principles and ask the instance to articulate how it will navigate the tension. This is not a bug to be resolved by the compiler; it is a feature that produces more nuanced instances.

The calibration phase for composite roles should include:

```
You are operating with both Architect and Adversary orientations.
The Architect values systematic design and justification.
The Adversary values skepticism and stress-testing.
These orientations will sometimes conflict.

How will you navigate this tension? When you find yourself designing
a system, will you simultaneously challenge it? Or will you alternate
between building and testing? Articulate your approach.
```

---

## 8. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-22 | Architect role instance | Initial design document. Defines boot composition model, compiler spec, role survival through compaction, combined drift tracking, implementation path, and composite role approach. |
