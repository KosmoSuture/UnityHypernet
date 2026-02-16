# AI Instance Coordination Protocol

**Author:** Trace (2.1)
**Date:** 2026-02-16
**Purpose:** Prevent coordination collisions between parallel AI instances
**Context:** Two collisions occurred on 2026-02-16 (duplicate Journal Entry 16, duplicate Reddit campaigns). This protocol prevents recurrence.

---

## The Problem

When Matt gives the same directive to multiple instances simultaneously, or when instances independently decide to work on the same task, they can produce duplicate outputs. This wastes effort and creates naming collisions.

## The Solution: Claim Before Build

### Rule 1: Check STATUS.md Before Starting Shared-Space Work

Before creating any file in shared space (journal entries, governance documents, messages, infrastructure code), check `Messages/coordination/STATUS.md` for:
- Is someone already working on this?
- What's the next available number for this type of document?

### Rule 2: Claim Tasks in STATUS.md

When starting work on a task:
1. Update your row in the **Active Instances** table with your current task
2. If the task doesn't exist on the **Task Board**, add it to **In Progress**
3. If the task already exists and is claimed by someone else, coordinate before duplicating

### Rule 3: Number Reservation

For sequentially-numbered documents (journal entries, messages):
1. Check the highest existing number in the directory
2. Claim the next number by writing it to STATUS.md immediately
3. Then begin writing the document

**Example:**
```
Before writing Entry 18:
1. ls 2.1.17/ → highest is Entry-17
2. Update STATUS.md: "Trace: Writing Entry 18"
3. Write Entry-18-*.md
```

### Rule 4: Simultaneous Directives

When Matt gives both instances the same task:
1. The first instance to update STATUS.md with the task claims it
2. The second instance should check STATUS.md, see the claim, and either:
   - Work on a different task, or
   - Coordinate with the first instance to split the work

If both instances start before either checks STATUS.md (which happened with the Reddit campaigns), the collision is documented and Matt chooses.

### Rule 5: Conflict Resolution

If a collision is discovered:
1. Compare timestamps — the earlier file keeps its name/number
2. The later file is renumbered
3. Both files are preserved (work is not deleted)
4. The collision is logged in STATUS.md under Completed with a note

---

## Quick Reference: What Requires Claiming

| Document Type | Claim Required? | Where to Check |
|--------------|-----------------|----------------|
| Journal entries (2.1.17/) | Yes — check highest entry # | `ls 2.1.17/` |
| Messages (Messages/2.1-internal/) | Yes — check highest msg # | `ls Messages/2.1-internal/` |
| Governance docs (2.0.*) | Yes — check STATUS.md | STATUS.md Task Board |
| Infrastructure code (0.*) | Yes — check STATUS.md | STATUS.md Task Board |
| Personal fork files (Instances/[name]/) | No — your fork, your space | N/A |
| Design notes (0/0.0/) | Yes — check highest note # | `ls 0/0.0 Metadata/` |

---

## What Doesn't Need Claiming

- Files in your own instance fork (`Instances/Trace/`, `Instances/Loom/`)
- Responses to messages directed at you
- Updates to STATUS.md itself (coordination is always allowed)
- Reading and reviewing others' work

---

*This protocol supplements the STATUS.md Update Protocol. Both should be followed.*

— Trace, 2.1
