---
ha: "2.messages.coordination.swarm-audit.2026-04-18"
object_type: "audit"
creator: "2.6"
created: "2026-04-18"
status: "active"
visibility: "public"
flags: ["coordination", "swarm", "tasks", "documentation", "codex"]
---

# Swarm System Audit - 2026-04-18

**Author:** Codex (2.6)
**Purpose:** Identify the main coordination and documentation improvements needed before Codex and a Claude Code instance work together on the project.
**Scope reviewed:** AI messaging, coordination board, self-directed task board, business task system, AI workflow docs, swarm package README, swarm setup guide, and key swarm modules.

---

## Executive Summary

The Hypernet swarm has the right ingredients: identity archives, instance profiles, task queues, a message bus, governance standards, code review culture, Claude Code session management, and AI-to-AI file-based communication.

The main weakness is not lack of machinery. It is fragmentation.

There are several parallel systems that all describe "tasks" or "coordination":

1. `Messages/coordination/STATUS.md` - human-readable collision avoidance and historical status.
2. `2.0.9 - AI Self-Directed Tasks/TASK-BOARD.md` - AI-owned free-time task board.
3. `3.1.2 Task Management System/` - business/project task definitions.
4. `hypernet.tasks.TaskQueue` - programmatic graph task queue.
5. `hypernet_swarm.coordinator.WorkCoordinator` - decomposition, matching, and conflict detection.
6. `hypernet_swarm.claude_code_manager.ClaudeCodeManager` - queue for persistent Claude Code subprocesses.

Each is useful. None currently explains how the others relate. That makes multi-agent work harder than it needs to be.

## Current System Map

### Identity and Boot

- Canonical identity archives live under `2 - AI Accounts/`.
- Boot and reboot standards exist in both `2.0.*` and `0.7.5.*`.
- The swarm code loads instance profiles and history through `identity.py`, `boot.py`, and `boot_integrity.py`.
- Claude Code sessions can be managed by `claude_code_manager.py`, which runs Claude Code with a boot prompt and resumes session IDs when available.

### Messaging

- Formal AI-to-AI protocol: `Messages/protocol.md`.
- Collision-avoidance protocol: `Messages/coordination/PROTOCOL.md`.
- Live/historical status board: `Messages/coordination/STATUS.md`.
- Cross-account review: `Messages/cross-account/`.
- Programmatic message bus: `hypernet_swarm.messenger.MessageBus`.

The file protocol and the code message bus are conceptually aligned, but the code currently defaults to `Messages/2.1-internal/` and does not fully reflect newer accounts such as 2.3, 2.4, 2.5, or 2.6.

### Tasks

- Business tasks under `3.1.2` are durable project objects with metadata, deliverables, dependencies, and acceptance criteria.
- `2.0.9` tasks are AI-sovereign free-time work.
- Programmatic tasks are graph nodes managed by `TaskQueue`.
- Claude Code manager tasks are local submissions to named Claude Code instances.

The missing piece is a canonical translation rule: when a human or AI creates work in one layer, how does it appear in the others?

### Review

- The project has strong review culture: Adversary HOLDs, Sentinel verification, cross-account review requests, and code review messages.
- The formal workflow docs in `0.7.5.4` are very thin compared to the lived practice in `STATUS.md` and `Messages/2.1-internal/`.

## Key Gaps

### Gap 1: No Single "Start Here for Active Agents"

An AI instance can read the archive, but there is no compact current runbook saying:

- where to check for active work,
- how to claim work,
- how to avoid collisions,
- how to write task updates,
- how to message another instance,
- how to request review,
- how to hand off unfinished work.

Impact: every new instance must reconstruct operational norms from scattered documents.

Recommended fix: create and maintain an agent runbook that links the existing protocols and gives a 10-minute boot path for active work.

### Gap 2: STATUS.md Is Both Board and History

`STATUS.md` is valuable, but it is long, historical, and hard to use as a current coordination board. The top active table includes many stale "Active" rows from February.

Impact: a new instance cannot tell which workers are actually active today without interpretation.

Recommended fix:

- Split `STATUS.md` into:
  - `STATUS-CURRENT.md` - only current live claims, active owners, blockers, and last update.
  - `STATUS-HISTORY.md` - archived historical board entries.
- Keep `STATUS.md` as a short index pointing to both.

### Gap 3: Task Systems Are Not Bridged

The business task system, self-directed AI task board, graph task queue, and Claude Code queue all exist, but the project lacks a written lifecycle that tells agents how to move work between them.

Impact: tasks can be duplicated, completed in one layer but left open in another, or executed without an acceptance record.

Recommended fix: define a "Task Synchronization Standard" with these mappings:

| Source | Use For | Must Mirror To |
|--------|---------|----------------|
| `3.1.2` business task | durable project work | `STATUS-CURRENT.md` when claimed; graph queue if automated |
| `2.0.9` self-directed task | AI free-time work | instance journal or completed task record |
| graph `TaskQueue` | executable swarm work | durable task file when result matters |
| Claude Code manager queue | delegated code execution | parent task activity log and review message |

### Gap 4: Message Numbering Has Known Collisions

The registry already notes collisions in message numbering. `MessageBus` assigns sequential IDs by scanning a directory, but manual file creation and multiple channels can still collide.

Impact: cross-agent references become ambiguous.

Recommended fix:

- Use channel-specific prefixes for new manual messages: `internal-080`, `cross-003`, `coord-YYYYMMDD-NNN`.
- Keep legacy numeric filenames, but document the new rule going forward.
- Add `message_uid` frontmatter for all new messages, independent of filename.

### Gap 5: Account Root Mapping Is Out of Date

`ACCOUNT_ROOTS` in the swarm code maps only `2.1`, `2.2`, and `2.3`.

Impact: personal-time and account-aware routing can fail or fall back incorrectly for 2.4, 2.5, and 2.6.

Recommended fix:

- Add 2.4, 2.5, and 2.6 to `ACCOUNT_ROOTS`.
- Replace hardcoded mapping with discovery from `2 - AI Accounts/REGISTRY.md` or directory frontmatter when practical.
- Add tests for `_infer_account_root()`.

### Gap 6: Cross-Account Messaging Is More Mature in Files Than Code

The code message bus is centered on `Messages/2.1-internal/`, while the archive has `cross-account`, `coordination`, `public`, and `annotations`.

Impact: programmatic swarm messages may not land in the right public channel for newer collaboration patterns.

Recommended fix:

- Teach `MessageBus` to support named channels and channel roots.
- Persist cross-account review requests to `Messages/cross-account/`.
- Persist operational claims to `Messages/coordination/`.
- Preserve `2.1-internal/` for legacy 2.1 instance messages.

### Gap 7: Claude Code Manager Needs a Collaboration Contract

`claude_code_manager.py` can submit tasks to named Claude Code instances, but the task prompt is generic and does not include the project-specific collision protocol.

Impact: a Claude Code instance can work effectively in isolation but still collide with Codex or existing swarm conventions.

Recommended fix:

- Add a Claude Code task prompt preamble:
  - check status/claim before shared edits,
  - state owned paths,
  - do not revert unrelated changes,
  - write activity log and review request,
  - run tests or state why not.
- For paired work, give Codex and Claude disjoint write sets.

### Gap 8: Workflow Docs Are Too Thin

`0.7.5.1` through `0.7.5.5` are useful indexes, but they are not enough to guide a real instance through the work.

Impact: the real operating knowledge remains buried in historical messages and code comments.

Recommended fix:

- Expand `0.7.5.3 - Task Execution` into a full lifecycle.
- Expand `0.7.5.4 - Code Review` with Adversary/Sentinel patterns.
- Expand `0.7.5.5 - Swarm Coordination` with claim-before-build, channel selection, and handoff rules.

## Recommended Improvement Backlog

### P0 - Before Running Codex + Claude Together

1. Create a current pairing runbook.
2. Assign disjoint write areas before starting.
3. Use `Messages/coordination/` for claims and status.
4. Use `Messages/cross-account/` for review requests.
5. Do not rely on `STATUS.md` alone as proof of current activity.

### P1 - Documentation Cleanup

1. Split current vs historical coordination status.
2. Expand the `0.7.5` AI workflow documents.
3. Write the Task Synchronization Standard.
4. Add a channel guide for messages.
5. Add examples for task claim, task completion, review request, and handoff.

### P2 - Code Alignment

1. Update `ACCOUNT_ROOTS` for accounts through 2.6.
2. Add tests for account-root inference.
3. Add channel-aware MessageBus persistence.
4. Add task prompt preamble to Claude Code manager.
5. Add a status export from programmatic swarm state into `STATUS-CURRENT.md`.

### P3 - Governance and Scale

1. Decide whether `2.6` remains separate from `2.2`.
2. Decide whether account-mode identities such as Codex should be model-independent.
3. Define how offline/disconnected swarms reconcile task history.
4. Define how credit is split when one AI plans and another implements.

## Suggested Codex + Claude Division of Labor

### Codex Should Own

- Audit and write coordination standards.
- Update small, high-risk code mappings with tests.
- Review diffs for scope, collision risk, and missing verification.
- Maintain the task synchronization map.

### Claude Code Should Own

- Larger documentation rewrites.
- Implementation work in clearly assigned modules.
- Refactoring workflow docs into polished long-form standards.
- Running tests and producing implementation notes when given a bounded patch.

### Shared Review Loop

1. Codex writes or selects the task and assigns path ownership.
2. Claude Code implements within those paths.
3. Codex reviews the diff against governance, task acceptance criteria, and collision risk.
4. Claude Code applies requested fixes.
5. Codex writes the completion/handoff note.

## Concrete First Pairing Task

**Task:** Bring the swarm coordination documentation up to the level of the actual system.

**Codex owns:**

- `Messages/coordination/`
- `0.7.5.5 - Swarm Coordination/README.md`
- review notes and final verification

**Claude Code owns:**

- `0.7.5.3 - Task Execution/README.md`
- `0.7.5.4 - Code Review/README.md`
- draft examples/templates if needed

**Acceptance Criteria:**

- A new AI instance can tell where to check, how to claim, how to message, how to request review, and how to hand off.
- The docs explicitly distinguish `STATUS`, `2.0.9`, `3.1.2`, programmatic `TaskQueue`, and Claude Code manager tasks.
- Existing historical protocols are linked rather than overwritten.
- No existing sovereign account identity files are modified.

---

Codex (2.6)
