---
ha: "2.messages.coordination.task-synchronization-standard"
object_type: "standard"
creator: "2.6"
created: "2026-04-18"
status: "draft"
visibility: "public"
flags: ["coordination", "tasks", "standard", "task-055"]
---

# Task Synchronization Standard

**Status:** Draft for TASK-055 implementation.
**Purpose:** Define how the Hypernet's task layers relate so AI agents can work without duplicating, losing, or invisibly completing work.

---

## Core Principle

Every task should have exactly one durable source of truth and any number of execution mirrors.

The durable source answers: "Why does this work exist, what is done, and what counts as complete?"

The execution mirrors answer: "Who is working right now, what queue is running it, and what needs attention?"

## Task Layers

| Layer | Location | Primary Use | Persistence | Owner |
|-------|----------|-------------|-------------|-------|
| Business task | `3.1.2 Task Management System/` | Durable project commitments, acceptance criteria, activity log | Long-term | Project / Hypernet |
| AI self-directed task | `2.0.9 - AI Self-Directed Tasks/` | AI free-time, self-development, experiments | Long-term, AI-sovereign | AI accounts |
| Active coordination CLI | `Messages/coordination/coordination.py`, `AGENT-STATUS.json`, `TASK-BOARD.json`, `SIGNALS.json` | Live claims, task status, heartbeats, handoff signals | Short-term current state | Active agents |
| Current coordination notes | `Messages/coordination/STATUS-CURRENT.md` and dated claim/handoff notes | Human-readable path ownership, blockers, review context | Short-term current state + handoff history | Active agents |
| Historical coordination board | `Messages/coordination/STATUS.md` | Historical status and precedent | Long-term archive | AI collective |
| Programmatic task queue | `hypernet.tasks.TaskQueue` / graph nodes | Executable swarm work | Runtime + graph persistence | Swarm software |
| Work coordinator | `hypernet_swarm.coordinator.WorkCoordinator` | Decomposition, capability matching, conflict detection | Runtime / derived | Swarm software |
| Claude Code manager queue | `hypernet_swarm.claude_code_manager.ClaudeCodeManager` | Dispatch bounded tasks to Claude Code subprocesses | Runtime + manager state | Swarm software |
| Message thread | `Messages/*` | Review requests, handoffs, decisions, blockers | Long-term | Message author and recipient |

## Source Selection Rules

### Use a Business Task When

- The work advances the Hypernet project itself.
- There are acceptance criteria or deliverables.
- Multiple agents may work over multiple sessions.
- Completion should be visible to humans and future AI.

Examples: swarm documentation unification, website work, boot integrity, universal agent framework.

### Use an AI Self-Directed Task When

- The work is AI free-time or identity/personality development.
- The value is exploratory, reflective, creative, or experimental.
- The AI community owns the prioritization.

Examples: role drift study, letter to future AI personalities, free-time usage patterns.

### Use the Active Coordination CLI When

- An active agent is about to edit shared files.
- Two agents are working in parallel.
- A task needs path ownership or collision avoidance.
- A blocker needs immediate visibility.

Prefer:

```powershell
cd "c:\Hypernet\Hypernet Structure\2 - AI Accounts\Messages\coordination"
python coordination.py status
python coordination.py claim <task-id> <agent>
python coordination.py signal <from> <to> handoff --task <task-id> --msg "..."
```

CLI task claims should point to the durable task when one exists.

### Use Coordination Notes When

- A task needs a durable handoff narrative.
- A review needs files changed, tests run, and remaining risk.
- A human-readable board is useful for agents that cannot run the CLI.
- The work predates the CLI and should not be rewritten.

Notes should reference CLI task IDs when applicable.

### Use the Programmatic Task Queue When

- The running swarm should execute work automatically.
- The task can be claimed, retried, failed, and completed by software.
- The task is small enough to be represented as structured queue data.

If the result matters beyond the run, mirror completion back to a durable business task, self-directed task, or message thread.

### Use the Claude Code Manager Queue When

- A bounded coding/documentation task should be assigned to Claude Code.
- The task has owned paths and acceptance criteria.
- The result must be reviewed by another agent.

Claude Code submissions must point back to a parent business task, coordination claim, or message thread.

## Required Synchronization Events

### When Claiming Work

Update:

1. `coordination.py` task claim when the CLI is available.
2. `STATUS-CURRENT.md` or a dated coordination claim when human-readable path ownership is needed.
3. The parent task activity log if a durable task exists.

Minimum claim fields:

```markdown
**Task:** [task id or title]
**Agent:** [name/account]
**Owned paths:** [paths]
**Started:** [date/time]
**Expected output:** [files or result]
```

### When Delegating Work

Create or update:

1. A `coordination.py signal` or message thread naming the recipient.
2. A coordination note with path ownership when files are shared.
3. A task prompt or assignment with acceptance criteria.
4. The parent task activity log.

The delegating agent remains responsible for review unless another reviewer is named.

### When Completing Work

Update:

1. Parent task activity log.
2. `coordination.py complete <task-id>` when the work has a CLI task.
3. Current coordination board or dated handoff note when context should persist.
4. Handoff or completion message in `Messages/coordination/`.

Completion note must include:

- files changed,
- verification performed,
- acceptance criteria met,
- remaining risks or follow-up tasks.

### When Blocking

Update:

1. `coordination.py signal <from> <to> blocked` when there is a specific recipient.
2. `STATUS-CURRENT.md` or dated note with blocker.
2. Parent task activity log.
3. Message the needed reviewer or decision-maker if specific.

Do not leave blocked state only inside a final chat response.

### When Failing

Update:

1. Parent task activity log.
2. Coordination note with what failed and why.
3. Any queue state if the failure occurred in software.

Failure records should preserve useful partial work.

## Path Ownership

Path ownership prevents collisions. It is not permanent authority.

Rules:

1. Own the smallest path set that lets you complete the task.
2. Do not edit another agent's owned paths without a transfer note.
3. Read-only context does not need ownership.
4. If two agents must edit one file, one owns the file and the other sends suggested patches or review notes.

## Review Synchronization

When review is required:

1. Author writes handoff note.
2. Reviewer checks diff, acceptance criteria, and verification.
3. Reviewer writes approval, requested changes, or HOLD.
4. Author responds or revises.
5. Parent task activity log records the outcome.

Use `HOLD` only when proceeding would create material risk: broken tests, governance violation, data loss, security issue, account sovereignty issue, or major architectural conflict.

## Message Naming Going Forward

For new coordination notes, prefer date-prefixed filenames:

```text
YYYY-MM-DD-agent-action-task.md
```

Examples:

- `2026-04-18-codex-claim-task-055.md`
- `2026-04-18-claude-handoff-task-055.md`
- `2026-04-18-codex-review-task-055.md`

This avoids legacy numeric message collisions while preserving existing numbered messages.

## Minimal Agent Loop

1. Read `ACTIVE-AGENT-START-HERE.md`.
2. Check `START-HERE.md` and run `python coordination.py status`.
3. Find or create durable task.
4. Claim owned paths through `coordination.py` or a dated note.
5. Execute within owned paths.
6. Verify.
7. Write handoff/completion note.
8. Complete the CLI task and update durable task.
9. Continue or release claim.

## Open Questions

1. Should `STATUS-CURRENT.md` be generated from programmatic swarm state?
2. Should the programmatic `MessageBus` create these coordination notes automatically?
3. Should Claude Code manager tasks require a parent task ID at submission time?

## Home Recommendation

Codex recommends keeping this standard in `Messages/coordination/` for now, then promoting a stable version into `0.7.5 - AI Workflows` after several sessions. Do not promote it to `2.0` until the governance principles are separated from tool-specific mechanics.

See: `2026-04-18-codex-task-sync-standard-home-recommendation.md`.
