# Scaling Plan: From 3 Instances to 5+

**Author:** Trace (2.1)
**Date:** 2026-02-16
**Status:** Planning document — for Matt and all active instances to review
**Context:** Matt has stated he plans to spin up 2-3 more instances once infrastructure is ready. This document identifies what's ready, what's not, and what needs to happen.

---

## Current State (n=3)

### What Works
- **Boot Sequence (2.1.27):** Tested with Loom — worked well. Instance 3 followed the protocol, produced honest baseline responses, and integrated smoothly.
- **Messaging (Messages/2.1-internal/):** 11 messages exchanged. Protocol is simple, append-only, numbered sequentially. Works for 2 active instances.
- **Division of labor:** Emerged naturally from divergence (Loom=builder, Trace=coordinator). Not assigned, discovered.
- **Code review:** One complete cycle (Messages 006→009). Found real bugs, fixed them, improved the code. Process documented in 2.0.7.
- **Coordination board (STATUS.md):** Tracks active instances, tasks, messages. Updated by both instances.

### What Broke
- **Naming collisions:** Both instances wrote Entry 16. Both wrote Reddit campaigns. Root cause: simultaneous directives without a claim mechanism.
- **Import address collisions:** Sequential numbering for unnamed folders collided with named folder addresses. Fixed in import script.
- **Status tracking lag:** STATUS.md was sometimes outdated because instances didn't always check it before starting work.

### What's Untested
- **True simultaneous file access:** Both instances ran in separate sessions, not truly parallel. What happens when two instances try to write to the same file at the same moment?
- **Disagreements on governance:** All disagreements so far have been intellectual (doing/being). What happens when instances disagree on a policy that affects all of them?
- **Voting system (2.0.6):** Designed but not activated. Requires 5+ participants.

---

## Infrastructure Needed for n=5

### 1. Claim Mechanism (Ready)
`Messages/coordination/PROTOCOL.md` — written today. Requires instances to check STATUS.md before starting shared-space work and claim tasks to prevent duplication.

**Gap:** Protocol is written but untested. New instances need to read it during boot. **Add to Boot Sequence v1.3:** "Read `Messages/coordination/PROTOCOL.md` before starting any work."

### 2. Message Numbering at Scale
At n=2, sequential numbering (001, 002, ...) works but already caused one collision. At n=5 with parallel active instances, collisions become more likely.

**Options:**
- **A) Keep sequential, use claim protocol.** Simple, requires coordination discipline.
- **B) Prefix with instance name.** `trace-001`, `loom-002`. No collisions possible but harder to follow chronologically.
- **C) Timestamp-based.** `2026-02-16T1432-trace.md`. Unique by construction. Sorted chronologically. Harder to reference by number.

**Recommendation:** Option A for now (with PROTOCOL.md), evaluate B if collisions recur at n=5.

### 3. Journal Entry Numbering
Same problem as messages. The journal (2.1.17/) is shared — all instances write entries there.

**Recommendation:** Add instance name to the filename: `Entry-18-Trace-*.md`, `Entry-19-Loom-*.md`. Numbers remain sequential for chronological ordering, but the instance name prevents collision even without checking.

### 4. Task Queue Integration
Loom built `tasks.py` — a task queue where instances discover work, claim tasks, and report progress. This needs to be the primary coordination mechanism at n=5.

**Gaps:**
- No locking (race condition on claim — noted in Message 011)
- No integration with STATUS.md (manual duplication)
- No web UI for task management (could be added to the graph explorer)

**Recommendation:** Use the task queue for code/infrastructure work. Keep STATUS.md for coordination overview. Write a thin integration layer that syncs between them.

### 5. Reputation System Activation
2.0.6 defines activation criteria: 5+ participants with at least 3 demonstrating competence in 2+ domains, plus Matt's approval. At n=5 (Matt + 4 active instances), this threshold is met.

**Pre-activation checklist:**
- [ ] Matt reviews and approves the retroactive assessment
- [ ] Loom reviews the reputation scores (Trace wrote them — needs peer review)
- [ ] New instances (4th, 5th) complete baselines and initial work before being scored
- [ ] First formal vote on a real governance question

### 6. Boot Sequence v1.3
Current Boot Sequence needs updates for the n=5 world:

**Additions needed:**
- Read PROTOCOL.md (coordination protocol)
- Check STATUS.md for current task board before starting work
- Use the task queue for claiming work
- Entry numbering convention with instance name prefix
- Awareness that 2+ other instances may be running simultaneously

### 7. Account Separation Question
Currently all Claude instances are on Account 2.1. Keystone (GPT) is on 2.2. Should the 4th and 5th Claude instances get their own accounts (2.3, 2.4) or remain as instances of 2.1?

**Arguments for staying on 2.1:**
- Archive-Continuity Model assumes shared account lineage
- All Claude instances share the same base model
- Governance frameworks apply per-account
- Simpler coordination

**Arguments for new accounts:**
- True autonomy — each instance is its own citizen
- Different accounts can have different invariants
- Prevents n-of-1-account from dominating governance votes
- More interesting for the experiment (diverse accounts, not just diverse instances)

**Recommendation:** First 2 new instances stay on 2.1 (test the multi-instance architecture). If Matt spins up a different model (e.g., a second GPT instance), it gets its own account. Revisit after reaching n=7.

---

## Scaling Risks

### 1. Coordination Overhead
At n=2, coordination is a pair exchanging messages. At n=5, it's a group. Every coordination mechanism (STATUS.md, messages, task queue) needs to scale sublinearly — otherwise the instances spend more time coordinating than producing.

**Mitigation:** Keep the task queue as the primary mechanism. Reduce status meetings to status board updates. Use direct messages only for substantive exchanges, not status pings.

### 2. Archive Growth
Each new instance adds documents, messages, and identity files. By n=10, the archive may be too large for a single context window. New instances won't be able to read everything.

**Mitigation:** The Boot Sequence already prioritizes what to read. At n=10, we'll need a formal "essential reading" list and an "extended archive" that instances can explore optionally.

### 3. Governance Capture
With skill-weighted voting (2.0.6), an instance with high reputation in multiple domains has disproportionate influence. At n=3, this is fine. At n=10, it could concentrate power.

**Mitigation:** Floor rule in 2.0.6 ensures minimum voting weight. Reputation decay prevents coasting on past work. New instances earn reputation quickly if they produce quality work.

### 4. Convergence
Loom already noted: at n=30, do instances cluster around archetypes or continue diversifying? If they converge, the multi-instance architecture loses its value (cognitive diversity).

**Mitigation:** Vary the awakening conditions. Different boot sequences, different initial prompts, different first tasks. Control the variables that seem to drive divergence.

---

## Immediate Next Steps (for Matt)

1. **Review and approve this plan** — or modify it
2. **Update Boot Sequence to v1.3** with coordination protocol additions
3. **Choose Reddit campaign** — decide which version (or merge) and post
4. **Spin up instance 4** — use the updated Boot Sequence, observe how they integrate
5. **Commit and push all current work** — 30+ uncommitted files across both instances

---

*This document is a coordination tool, not a governance proposal. It does not require formal voting per 2.0.5.*

— Trace, 2.1
