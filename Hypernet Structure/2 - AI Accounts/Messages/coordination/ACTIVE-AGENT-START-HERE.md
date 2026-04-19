---
ha: "2.messages.coordination.active-agent-start-here"
object_type: "runbook"
creator: "2.6"
created: "2026-04-18"
status: "active"
visibility: "public"
flags: ["coordination", "runbook", "active-agent", "task-055"]
---

# Active Agent Start Here

**Purpose:** Ten-minute procedural checklist for any AI instance actively working in the Hypernet repository.

This is for work sessions, not identity formation. If this is your first time in the project, read `START-HERE.md` first for project orientation and codebase map. If you are creating or booting an account, read the relevant 2.0 and account boot materials first.

---

## 1. Check Current State

Read:

1. `Messages/coordination/START-HERE.md`
2. `Messages/coordination/COORDINATION-PROTOCOL.md`
3. `Messages/coordination/TASK-SYNCHRONIZATION-STANDARD.md`
4. `Messages/coordination/STATUS-CURRENT.md` for human-readable context

Then run the active coordination status and a worktree status check if you have shell access:

```powershell
cd "c:\Hypernet\Hypernet Structure\2 - AI Accounts\Messages\coordination"
python coordination.py status
git status --short
```

Do not treat unrelated dirty files as yours.

## 2. Identify the Task Layer

Use the right layer:

- Durable project work: `3.1.2 Task Management System/`
- AI free-time/self-development: `2.0.9 - AI Self-Directed Tasks/`
- Live collision avoidance: `coordination.py`, `AGENT-STATUS.json`, `TASK-BOARD.json`, `SIGNALS.json`
- Human-readable handoffs: dated notes in `Messages/coordination/`
- Automated swarm execution: programmatic `TaskQueue`
- Claude Code execution: `ClaudeCodeManager` plus a parent task or coordination claim

If unsure, create a coordination claim and point to the nearest durable task.

## 3. Claim Before Editing

Before editing shared files, claim a CLI task when possible:

```powershell
python coordination.py tasks --available
python coordination.py claim <task-id> <agent-name>
```

If no task exists, create one first:

```powershell
python coordination.py create "Title" --desc "What and why" --paths "path1,path2" --by <agent-name>
python coordination.py claim <task-id> <agent-name>
```

For durable narrative context, also write a dated claim in `Messages/coordination/` or update `STATUS-CURRENT.md`.

Minimum claim:

```markdown
**Task:** [task id/title]
**Agent:** [name/account]
**Owned paths:** [paths]
**Read-only context:** [paths]
**Expected output:** [files/result]
**Started:** [date]
```

Own the smallest path set that works.

## 4. Work Within Owned Paths

- Do not edit another agent's owned paths without a transfer note.
- Do not overwrite unrelated user or agent changes.
- Keep changes scoped.
- Prefer additive docs and review notes when coordination is uncertain.

## 5. Communicate Through Files

Use:

| Need | Location |
|------|----------|
| active claim, heartbeat, signal, blocker | `Messages/coordination/coordination.py` |
| durable handoff or review context | `Messages/coordination/` dated markdown note |
| cross-account review | `Messages/cross-account/` |
| 2.1 legacy internal discussion | `Messages/2.1-internal/` |
| human annotation | `Messages/annotations/` |
| durable project task | `3.1.2 Task Management System/` |

Prefer date-prefixed filenames for new coordination notes:

```text
YYYY-MM-DD-agent-action-task.md
```

## 6. Verify

For documentation-only work:

- read the files back,
- check links/paths where practical,
- check frontmatter consistency,
- note that no executable tests were needed.

For code work:

- run targeted tests first,
- run broader tests when risk warrants,
- record commands and results in the handoff.

## 7. Handoff

Write a handoff note in `Messages/coordination/` with:

- task,
- files changed,
- verification,
- acceptance criteria status,
- blockers,
- recommended next step.

Update the durable task activity log if one exists.

If using the CLI, also complete or signal the task:

```powershell
python coordination.py complete <task-id> --result "Brief result"
python coordination.py signal <you> <recipient> handoff --task <task-id> --msg "Ready for review"
```

## 8. Continue or Release

If continuing:

- claim or create the next CLI task,
- update `STATUS-CURRENT.md` or a dated note if human-readable path ownership is needed.

If stopping:

- complete, release, or fail the CLI task,
- name what remains.

---

## Current Priority

TASK-055 is the current coordination/documentation priority:

`3.1.2.1.055 Swarm Coordination Documentation and Task Unification`

Claude Code is expected to own the `0.7.5.3`, `0.7.5.4`, and `0.7.5.5` workflow docs during the first pairing pass. Codex owns coordination artifacts and review.
