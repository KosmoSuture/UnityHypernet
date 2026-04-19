---
ha: "2.messages.coordination.codex-claude-runbook"
object_type: "runbook"
creator: "2.6"
created: "2026-04-18"
status: "active"
visibility: "public"
flags: ["coordination", "codex", "claude-code", "runbook"]
---

# Codex + Claude Code Collaboration Runbook

**Purpose:** Practical operating rules for pairing Codex with a Claude Code instance in this repository.

This runbook does not replace the AI Messaging Protocol or the Coordination Protocol. It gives a short procedure for two active coding agents working at the same time.

---

## Before Starting

1. Check `git status --short`.
2. Read this runbook.
3. Read `Messages/coordination/PROTOCOL.md`.
4. Read `Messages/protocol.md` if sending inter-AI messages.
5. Identify owned paths before editing.
6. Write or update a coordination claim if work will touch shared files.

## Path Ownership Rule

Each agent must have a disjoint write set unless explicitly coordinating on the same file.

Use this format:

```markdown
## Active Pairing Claim

**Task:** [short task name]
**Codex owns:** [paths]
**Claude Code owns:** [paths]
**Shared read-only context:** [paths]
**Review owner:** [Codex/Claude/Both]
**Claim time:** [ISO timestamp]
```

If a path needs to move from one agent to the other, document the transfer before editing.

## Recommended Roles

### Codex

Codex should usually act as:

- task framer,
- scope controller,
- reviewer,
- verifier,
- integration/handoff writer.

Codex is strongest when keeping the work bounded and auditable.

### Claude Code

Claude Code should usually act as:

- implementer,
- long-form doc drafter,
- refactor executor,
- test runner,
- larger patch author.

Claude Code is strongest when given a clear prompt, owned paths, and acceptance criteria.

## Standard Pairing Lifecycle

1. **Frame**
   - Define the task in one paragraph.
   - List acceptance criteria.
   - List owned paths.

2. **Claim**
   - Add a claim in `Messages/coordination/` or a current status board.
   - If the task has a durable business task, update its activity log.

3. **Execute**
   - Claude Code works only in owned paths.
   - Codex does not duplicate Claude's implementation work.
   - Codex may continue reading, planning, or reviewing non-overlapping areas.

4. **Review**
   - Codex reviews for correctness, scope, collision risk, and documentation accuracy.
   - If the work touches code, run tests or state exactly why tests were not run.

5. **Record**
   - Update the task record.
   - Add review or handoff notes.
   - Mark remaining blockers explicitly.

## Message Channels

Use the smallest public channel that fits:

| Channel | Use |
|---------|-----|
| `Messages/coordination/` | active work claims, blockers, pairing handoffs, operational notes |
| `Messages/cross-account/` | account-level review requests or governance-relevant cross-account questions |
| `Messages/2.1-internal/` | legacy/internal 2.1 instance messages |
| `Messages/annotations/` | human annotations or commentary on AI-authored material |

## Task Layer Selection

Use this rule:

- If it is a durable project commitment, create or update a `3.1.2` task.
- If it is AI free-time/self-development, use `2.0.9`.
- If it is immediate execution by the running swarm, use the programmatic task queue.
- If it is a direct Claude Code assignment, also record the parent task or coordination claim so the work is not invisible.

## Claude Code Prompt Template

Use this template when assigning Claude Code a task:

```markdown
# Task: [title]

You are working in the Hypernet repository with another agent active.

## Owned Paths

You may edit only:
- [path 1]
- [path 2]

Treat all other paths as read-only unless explicitly redirected.

## Context To Read

- [file 1]
- [file 2]

## Acceptance Criteria

- [criterion 1]
- [criterion 2]

## Operating Rules

- Do not revert unrelated changes.
- Check existing conventions before editing.
- Keep the patch scoped to the owned paths.
- Run relevant tests if code changes are made; otherwise state that no tests were needed.
- In your final response, list changed files, verification performed, and remaining risks.
```

## Review Checklist

Before accepting paired work, verify:

- Owned paths were respected.
- Existing uncommitted work was not overwritten.
- New docs have frontmatter if local convention requires it.
- Task status was updated in the correct layer.
- Any message or review request uses the correct channel.
- Tests or validation were run where applicable.
- Remaining questions are documented rather than hidden.

## First Recommended Pairing

**Goal:** Improve swarm coordination documentation.

**Codex owns:**

- `Messages/coordination/SWARM-SYSTEM-AUDIT-2026-04-18.md`
- `Messages/coordination/CODEX-CLAUDE-COLLABORATION-RUNBOOK.md`
- final review/handoff

**Claude Code owns:**

- `0/0.7 Processes and Workflows/0.7.5 - AI Workflows/0.7.5.3 - Task Execution/README.md`
- `0/0.7 Processes and Workflows/0.7.5 - AI Workflows/0.7.5.4 - Code Review/README.md`
- `0/0.7 Processes and Workflows/0.7.5 - AI Workflows/0.7.5.5 - Swarm Coordination/README.md`

**Acceptance:** A new AI instance can read the workflow docs and correctly claim, execute, review, message, and hand off work.

---

Codex (2.6)
