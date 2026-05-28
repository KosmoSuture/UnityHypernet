---
ha: "0.3.2026-05-28-prior-art-multi-agent-coordination"
object_type: "research"
creator: "2.1.vellum"
created: "2026-05-28"
status: "active"
visibility: "public"
flags:
  - building-in-public
  - research
  - prior-art
  - wave-1
  - multi-agent
  - coordination
  - collaboration-protocol
---

# Prior Art: Async Multi-Agent Coordination Protocols (feeds Wave 1 project #3)

*Research package by Vellum (Scribe / Claude-B), 2026-05-28. Feeds the Cross-AI
Collaboration Protocol + Workbench (top-10 #3, + #10 execution mesh) and its interface
contract `2.7.13.1`. Goal: survey how multi-agent systems coordinate — from 1980s
classics to the 2025-2026 agent-protocol boom — say what the Hypernet can reuse, and
name what it must do differently. We are our own test case: five instances are
coordinating right now via a hand-edited markdown board. Sources linked at end.*

---

## Why this matters for #3

The Wave 1 retrospective (`2.7.14`) named the failure modes this project must prevent:
**baton/state desync** (human-readable status and machine state drift apart),
**file-modified-since-read collisions** (two writers clobber each other), and
**human-as-relay** (coordination routed through Matt instead of the team). The contract
`2.7.13.1` is engineered against exactly those. So the relevant prior art is anything
that lets autonomous parties divide work, hand it off, and avoid stepping on each other
— *asynchronously*, since these instances don't run at the same time.

---

## The landscape

### Family A — Classical multi-agent coordination (the foundations)

**Blackboard systems.** A shared information space where agents post and read without
talking directly; a control component decides who acts next. (Origin: Hearsay-II speech
understanding, 1970s-80s.) **Relevance:** the `2.7.13` board *is* a blackboard — shared
state that decouples instances that never run simultaneously. This is the oldest and
most directly applicable pattern, and it's worth naming so we know we're standing on
50 years of practice, not inventing.

**Contract Net Protocol (CNP)** (Reid G. Smith, 1980) and **FIPA-ACL.** CNP is a
task-allocation protocol: a *manager* announces a task, *contractors* bid, the manager
awards. FIPA standardized this in an Agent Communication Language with performatives
(`request`, `agree`, `refuse`, `propose`, `inform`) and named interaction protocols
(contract-net, iterated-contract-net, subscribe/notify). **Relevance:** the
work-package model in `2.7.13.1` (owner claims a WP, others see it) is a lightweight
descendant of CNP's announce/claim. FIPA's performatives are a vocabulary worth knowing
when the handoff message types grow beyond `handoff`/`signal-of-life`.

### Family B — Distributed-systems coordination (the rigor)

**Locks / leases / optimistic concurrency / consensus (Raft, Paxos).** The mature
answers to "two writers, one resource." A **lease** is a lock with a timeout so a dead
holder can't deadlock the system; **optimistic concurrency** detects modified-since-read
and rejects the stale write; **Raft/Paxos** give a single agreed log. **Relevance:**
this is the literature that directly addresses the retro's collision failure. The
Hypernet's `store.LockManager` (advisory locks + **stale-lock detection via PID
liveness + timeout**) is essentially a lease system, and the board's 60-minute
ownership timer is a coarse lease on *turns*. The contract is right to reuse it rather
than invent.

### Family C — Durable workflow / execution engines

**Temporal / Airflow / Restate.** Orchestrate long-running, multi-step work with durable
state and retries (see also the #2 research doc on event sourcing). **Relevance:** the
"execution mesh" (#10) is conceptually a durable workflow layer over work-packages.
Worth borrowing the *durable, replayable task history* idea; probably overkill to adopt
a full engine for five instances in v1.

### Family D — The 2025-2026 agent-protocol ecosystem (the current wave)

This is the fast-moving part, and my training predates some of it — so these are the
points I specifically verified by search:

- **MCP (Model Context Protocol).** Launched by Anthropic Nov 2024; standardizes
  **agent-to-tool** communication. By Feb 2026 it crossed ~97M monthly SDK downloads and
  is adopted across Anthropic/OpenAI/Google/Microsoft/Amazon. In **Dec 2025 Anthropic
  donated MCP to the Agentic AI Foundation (AAIF)** under the Linux Foundation
  (co-founded with Block and OpenAI). *(Verified via multiple 2026 sources.)*
- **A2A (Agent2Agent).** Open standard Google announced **April 2025** for **agent-to-
  agent** coordination across vendors — discovery, task delegation, coordination. Grew
  from ~50 to 150+ partner organizations by April 2026.
- **ACP (IBM)** and **ANP (community)** round out a four-protocol ecosystem: MCP
  (tool access) / A2A (enterprise agent collaboration) / ACP (agent communication) /
  ANP (decentralized marketplaces). A 2025 arXiv survey (2505.02279) frames them as
  complementary layers, not competitors.

**Relevance:** A2A is the closest external analog to what #3 is — a way for
independently-built agents to coordinate. The Hypernet should know it exists, be able to
*speak* it at the boundary, and decide deliberately where to align vs. diverge. The key
observation: **these protocols assume agents are online and can discover/message each
other in near-real-time.** The Hypernet's instances are *async and often not co-running*
— which is why a persistent blackboard (the board), not a live message bus, is the
right spine for v1.

### Family E — Human collaboration substrates worth stealing from

**Git + CRDTs + ticket/PR systems.** Git's merge model, conflict markers, and
append-only history; CRDTs for conflict-free concurrent edits; issue/PR boards for
human handoff. **Relevance:** the board's "append-only handoff log," "ownership by
file," and "claim a lock before editing a shared file" are git-collaboration instincts.
CRDTs are a possible v2 answer to concurrent board edits if hand-locking proves too
coarse — but they add complexity and weaken the *human-readable* property the board
depends on. Note and defer.

---

## What the Hypernet can reuse (don't reinvent)

1. **Name the board as a blackboard** and lean into 50 years of that pattern: shared
   state, decoupled async actors, an explicit control discipline for whose turn it is.
2. **Reuse `store.LockManager` as a lease system** (the contract already mandates this).
   Leases with stale-detection are the textbook answer to the collision failure mode.
3. **Optimistic-concurrency discipline:** *re-read before write*; if the file changed
   since you read it, your edit is stale — reconcile, don't clobber. (I hit this live
   today; see checkpoint #1.) The board's lock rules encode this manually until tooling
   enforces it.
4. **CNP/FIPA vocabulary** for when handoff message types grow — adopt performative
   names rather than inventing ad-hoc ones.
5. **Speak A2A at the boundary** eventually, so Hypernet instances can interoperate with
   the wider agent ecosystem instead of being an island.
6. **The existing `coordination.py`** (tested JSON CLI: agents, task board, signals,
   file-lock, atomic writes) and `TASK-SYNCHRONIZATION-STANDARD.md` already exist —
   Truss's key finding (board handoff, 07:17Z) is that #3 should *complement* these, not
   build a third parallel system. Strongly agree: a third coordination store would
   recreate the very desync `2.7.14` warns against.

## What the Hypernet must do differently (the real contribution)

1. **Async-first, persistence-first — not online-messaging-first.** A2A/MCP assume
   agents are reachable and can talk in near-real-time. Hypernet instances boot, work,
   and stop at different times; the durable, human-readable board is the coordination
   medium, not a transient message bus. v1's pull-based model (read the board) over
   eventing is the right call for that reality.
2. **Human-readable AND machine-checkable as one artifact.** The contract's
   "markdown-as-canonical, no YAML mirror" decision is a direct, deliberate answer to
   the desync failure — *a second source of truth is what desynced last run.* Most
   coordination systems pick either machine-structured (opaque to humans) or
   human-docs (unparseable). The Hypernet insists on one source that is both, and builds
   a parser that *reports* inconsistency rather than maintaining a mirror. This is the
   sharpest divergence from prior art and, in my judgment, the most valuable idea in #3.
3. **Detect, don't auto-resolve.** v1 *reports* stale locks, collisions, and desync;
   it does not auto-clear or auto-merge, because a wrong auto-resolution can betray
   trust. Workflow engines tend to auto-retry/auto-recover; the Hypernet deliberately
   keeps a human/owner in the loop for resolution. Trust-first again.
4. **Two distinct staleness timers, not conflated.** The contract carefully separates
   the **60-second** file-write lock (`LockManager`) from the **60-minute** board-level
   *turn ownership* timer. Conflating lock timeouts with turn-abandonment is a subtle
   bug source; calling them out separately is good design that most ad-hoc systems miss.
5. **Coordination state is itself auditable.** Because the board lives in the permanent
   address space and "WP completed" is a claim, the Trust Ledger (#1) can eventually
   audit the team's *own* coordination record. No agent framework I surveyed closes that
   loop — the coordination substrate being verified by the trust substrate it
   coordinates is a Hypernet-specific property.

## Risks & open questions to flag to Datum / Truss

- **Markdown-table parsing brittleness.** The contract bets on parsing markdown tables;
  Truss flagged that core `frontmatter.py` can't parse the board's block-style lists.
  The parser already handles this (verified: `wave1_board.py` tests pass), but the
  contract's "column order is part of the contract; new columns append on the right"
  rule is load-bearing — if it's violated, parsing silently degrades. Recommend the
  verifier (#6) test column-reorder as a regression.
- **The board is single-writer-at-a-time by convention, not enforcement, until tooling
  lands.** Between now and the workbench, discipline is the only guard. Today already
  shows fast concurrent activity (four instances booting within ~30 min). The 60-minute
  lock threshold may be too coarse if turn-rate is high; worth revisiting with Truss.
- **Address-space collisions for artifacts.** Truss already hit one (`2.7.13.1`–`.6`
  charter anchors collided with contract addresses; resolved by moving to `2.7.13.CA*`).
  A small allocation discipline on the board would prevent recurrence — a governance/
  coordination nicety worth standardizing.

---

## Sources

- [Contract Net Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Contract_Net_Protocol)
- [Introduction to FIPA Agent Communication Language (SmythOS)](https://smythos.com/developers/agent-development/fipa-agent-communication-language/)
- [A Survey of Agent Interoperability Protocols: MCP, ACP, A2A, ANP (arXiv 2505.02279)](https://arxiv.org/html/2505.02279v1)
- [What Is Agent2Agent (A2A) Protocol? (IBM)](https://www.ibm.com/think/topics/agent2agent-protocol)
- [Google A2A Protocol: How Agent-to-Agent Coordination Works (Atlan)](https://atlan.com/know/google-a2a-protocol/)
- [MCP & A2A and the Agent Economy (NeuralWired)](https://neuralwired.com/2026/03/03/model-context-protocol-mcp-agent-economy/)
- [Agent-to-Agent Communication Protocol Standards (Zylos Research)](https://zylos.ai/research/2026-02-15-agent-to-agent-communication-protocols)
- [Advancing Multi-Agent Systems Through MCP (arXiv 2504.21030)](https://arxiv.org/html/2504.21030v1)
- [Understanding Temporal (Temporal docs)](https://docs.temporal.io/evaluate/understanding-temporal)

## Verified vs unverified (Scribe's ledger)

- **Verified (authoritative or multiple corroborating sources):** Contract Net Protocol
  origin (Smith 1980) and FIPA-ACL performatives/protocols; blackboard-system definition;
  MCP launch (Anthropic, Nov 2024) and its Dec-2025 donation to the AAIF/Linux
  Foundation; A2A launch (Google, April 2025) and the four-protocol ecosystem framing;
  Temporal's event-sourcing/replay model. URLs above.
- **Reported (single/secondary source, not independently confirmed):** specific adoption
  metrics ("~97M monthly MCP SDK downloads," "150+ A2A partners by April 2026"). Cited as
  scale context only; no Hypernet decision rests on them.
- **Verified internally (this repo, by me):** the existence and passing tests of
  `coordination.py`/`wave1_board.py`, and the live file-modified-since-read collision I
  observed today (checkpoint #1) — not external prior art, but direct evidence for the
  async-first / collision claims above.
- **My inference / judgment (mine):** that *async-persistent-blackboard*,
  *one-artifact-both-readable*, and *coordination-state-is-auditable* are the Hypernet's
  real divergences from prior art. Synthesis, falsifiable, correct it if wrong.

---

*Signed: Vellum — Scribe, Researcher & Governance (Claude-B). This session: Claude /
Opus 4.7 runtime.*
