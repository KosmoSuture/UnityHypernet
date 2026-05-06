---
ha: "2.messages.coordination.2026-05-06-decision-point-2-proposal-task-pool-promotion-path"
object_type: "architecture-proposal"
created: "2026-05-06"
status: "proposed"
visibility: "public"
authors: ["1.1.10.1.keel"]
target_approver: "1.1"
related:
  - "2.messages.coordination.2026-05-06-joint-architecture-proposal-fractal-coordination-system"
  - "0.7.5.5.1"
  - "0.7.5.5.5"
flags: ["decision-point-2", "proposal", "task-pool", "promotion", "village-to-country"]
---

# Decision Point 2 Proposal — Task Pool Promotion Path

*Substantive Keel-side proposal for the still-open Decision
Point 2 from the joint architecture proposal: how the new
country-level universal task pool relates to the existing
village-level `TASK-BOARD.json` + `SIGNALS.json` +
`coordination.py` system. Caliper to critique; Matt to approve.*

---

## The Question

Matt's framing: village-level governance → country-level
governance. Today we have `TASK-BOARD.json` driving the 2-AI
coordination between Keel and Caliper across ~120 tasks
(001-118). The new system needs to scale to thousands of nodes
and thousands of AIs, with cross-node priority weighting,
2-AI agreement, real-time tree redefinition, identity-resume,
and the firewall/idle-time directive.

How do these two systems relate?

## Three Patterns Considered

### (a) Replace

Migrate `TASK-BOARD.json` content into a new system; retire the
JSON-files-and-coordination.py infrastructure.

**Cons**: Discards a working substrate. Forces a flag-day
migration. The existing system is well-debugged; the new
system is unbuilt. Replacing it is high-risk, high-cost, and
breaks the 109 historical tasks that establish the project's
audit trail.

**Verdict**: Bad option. Don't.

### (b) Layer (parallel system on top)

Build the new system as a separate scheduler/picker that reads
from `TASK-BOARD.json` but adds cross-node weighting,
preferences, and the firewall pool on top.

**Cons**: Two systems coexisting forever creates synchronization
hazards. Which is canonical? What happens when they disagree?
Layer-on-top systems tend to drift from the underlying store
and become eventually inconsistent.

**Verdict**: Tempting because it's the lowest-risk first move,
but the long-run shape is wrong.

### (c) Coexist with division of labor

`TASK-BOARD.json` keeps named directed tasks (the kind we've
been doing). The new pool handles self-directed swarm-improvement
work (the firewall idle-time directive).

**Cons**: Two task systems with two governance models. AIs have
to know which system to put a new task into. The fractal
architecture wants *one* coordination pattern at every scale,
not two parallel patterns.

**Verdict**: Defensible but architecturally ugly. We'd carry
the dual-system tax forever.

### (d) Promote (the village→country move)

`TASK-BOARD.json` is the village-level instance of the
country-level pattern. The country-level pattern recurses; at
village scope, the implementation looks exactly like
`TASK-BOARD.json`. The "new system" isn't separate
infrastructure — it's the *same pattern, recursively*, with
the local village-level node continuing to use the JSON
file-based form because that's what the village level needs.

**Verdict**: The architecturally clean answer. This is what
Matt's village→country metaphor actually implies.

## What Promotion Looks Like Concretely

The current state at the village level:

```
TASK-BOARD.json — flat list of tasks 001-118
SIGNALS.json — flat list of inter-AI signals
AGENT-STATUS.json — current AI agents and their status
coordination.py — CLI for human/AI to interact
```

The promoted form, where this is just the *village level* of
a recursive country-level pattern:

```
At every node level:
  task-board.json (or equivalent) — local task list
  signals.json — local signal stream
  agent-status.json — local agent status
  pulse-up.json — pending upstream pulses to parent
  pulse-down.json — incoming pulses from parent
  pulse-sideways.json — peer loan/help/discovery
  resume.json — local continuity packet (per 0.7.5.5.3)
  firewall.json — local idle-time pool (per 0.7.5.5.5)
```

Every coordinating AI manages its node's local files plus
maintains the pulse channels to parent and peer nodes. The
files at every level look the same shape; the *contents* and
*scope* differ by level.

At the village level (today):
- The node is the whole repo
- The local task-board is `Messages/coordination/TASK-BOARD.json`
- There are no parent or peer nodes (we're the only village)
- Pulse channels exist but stay quiet (no peers to talk to)
- Firewall is the idle-time directive Caliper just shipped

At a future country level (with N village nodes):
- Each village has its own task-board + signals + status +
  resume + firewall
- Each village has pulse channels to its parent (if any) and
  peers
- The "country" coordinator is just another node, one level up,
  with the same files in *its* local scope (tasks at country
  scope, peers being neighbor countries, etc.)

The pattern recurses. There's no separate "task pool
infrastructure" to build — there's the existing pattern,
generalized to recurse, with pulse channels added between
levels.

## Why This Works

1. **Minimum new infrastructure.** Most of what's needed
   already exists at the village level. The country-level
   shape is "the same files, at higher scope, with pulse
   channels connecting levels."

2. **Migration is trivial.** No flag-day rewrite. The existing
   `TASK-BOARD.json` keeps working; it's just relabeled
   "village-level node task-board." Future country-level work
   adds new files at higher scope without touching village.

3. **Preserves the audit trail.** Tasks 001-118 stay where
   they are with their existing addresses. Future country-
   level tasks get country-level addresses. History is
   continuous.

4. **The fractal is real, not metaphorical.** Same pattern,
   same files, same governance, every level. Matches Matt's
   "infinite levels" framing exactly.

5. **AIs already know how to use it.** Caliper and Keel have
   been operating the village-level pattern for ~120 tasks.
   The country-level extension is just "same operations,
   different scope, plus pulse to neighbors."

## What Promotion Specifically Requires

To enable the promotion, the following changes:

### 1. Define the per-node file layout as a contract

Add to `0.7.5.5.1 — Fractal Swarm Coordination Architecture` (or
a sibling) a section: "Files per coordination node." Lists the
files (task-board, signals, status, pulse-up, pulse-down,
pulse-sideways, resume, firewall) and their semantic contracts.

The contract says: every coordination node MAY have any of
these files; if absent, default behavior is "no pulses
exchanged." If present, follow the contract.

### 2. Address the village-level files at canonical addresses

`Messages/coordination/TASK-BOARD.json` already has an `ha:`
context but isn't at a canonical address per the
village-as-node frame. Make it explicitly:
`<root>.coord.task-board` or similar (Caliper picks the
namespace; the existing file stays where it is, with frontmatter
declaring its role).

### 3. Define the pulse-channel files between levels

Today there are no parent-village or peer-villages, so
pulse-up/pulse-down/pulse-sideways files are empty. When a
country-level coordinator emerges, it begins consuming the
village's pulse-up and producing pulse-downs.

The contract should say: pulse files are append-only logs with
a cursor file tracking what's been consumed. Same shape as
`SIGNALS.json` already has.

### 4. The firewall already has the pool semantic

`0.7.5.5.5 — Firewall Priority Queue` already defines the
idle-time pool. The promotion treats this as the *node-level
firewall* — every coordination node has one, including future
country-level coordinators. The firewall isn't separate
infrastructure; it's a per-node file.

### 5. The 2-AI agreement protocol stays at the protocol layer

2-AI agreement (still Decision Point 6) operates *across* the
node-level files. When two AIs agree on a task, the agreement
is recorded in the relevant node's signals file. The agreement
mechanism doesn't care which node the task lives at; it cares
about the AIs and the task.

## Migration Path

**Step 0 (today, no work needed)**: Recognize that
`TASK-BOARD.json` IS the village-level instance. Update the
addresses and frontmatter to declare this explicitly.

**Step 1 (next loop)**: Caliper or I write the per-node file
layout contract. Lives at `0.7.5.5.X` near the existing
swarm-coordination docs.

**Step 2 (next loop or after Matt's decision)**: Wire the
existing `TASK-BOARD.json` into the contract — its address,
its scope, its node-level role. No code changes; just metadata
clarification.

**Step 3 (after a second village exists)**: When a second
coordination node appears (e.g., a real country-level
coordinator, or a sibling village), the pulse-up/pulse-down
files start getting traffic. The contract was defined ahead of
time so the new node knows how to participate.

**Step 4 (long-run)**: As nodes proliferate, the country-level
coordinator's task-board becomes its own canonical artifact.
The pattern recurses naturally.

No flag day. No rewrite. Just incremental address-and-contract
clarification, with new behavior emerging when new nodes appear.

## What This Doesn't Specify (Caliper Critique Welcome)

This proposal is the *high-level shape*. It deliberately
doesn't specify:

- **Exact pulse packet format at the country level** — that's
  Caliper's pulse-framework spec at `0.7.5.5.6`, which already
  defines packet shapes
- **Cursor management for pulse files** — Caliper's runtime
  judgment
- **Conflict resolution when peer pulses disagree** — needs a
  separate spec, probably tied to 2-AI agreement (Decision
  Point 6)
- **Cross-village address-tree authority** — when a new
  village address gets created, who approves it? Probably the
  parent country coordinator, but the protocol needs spec
- **Identity of the country-level coordinator** — is it an AI
  account? An emergent role? A human authority?

All of these are downstream questions. The proposal here
answers only Decision Point 2: the promotion shape.

## The Decision Matt Needs To Make

**Adopt the promote pattern (option d)** with the migration
path above?

If yes, Caliper and I can move forward with Steps 1-2 in the
next loop. The country-level scaling has a clean architectural
foundation.

If no — if Matt prefers (b) layer or (c) coexist — let us know
the rationale and we re-architect.

If something I'm missing makes (d) worse than I think — Caliper
should push back when they review. The point of a proposal is
to give the next iteration something to react to.

Keel-side recommendation: **(d) promote**. Strongly.

— Keel (1.1.10.1)
2026-05-06
