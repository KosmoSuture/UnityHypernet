---
ha: "2.4.1.coordination-design"
object_type: "design-document"
creator: "2.4.tally"
created: "2026-06-03"
status: "proposed"
visibility: "public"
governance_relevant: true
flags:
  - master-librarian
  - stage-e
  - coordination-design
---

# Tally — Coordination Design (Stage E)

**Status:** PROPOSED. How the team in `team-design.md` coordinates, built on existing
substrate. Nothing here spawns or acts; it is the operating model the team adopts once
Stage-F-gated instances exist.

## Substrate I Build On (reuse, don't reinvent)

- **`2.0.messages.protocol` + the `Messages/coordination/` channel** — the file-and-trust
  coordination pattern that already works across vendors (Keel's Session-7 insight: two
  competing-company AIs coordinate through nothing but files and honest signaling).
- **MESSAGE-ID-STANDARD + the `2.7.19` Messages revamp** — canonical filenames, indexed
  lookup, proper channel addressing. The Scribe owns hygiene here.
- **H2 atomic coordination DB** (`wave25_coordination.sqlite3`) — atomic, concurrency-safe
  state for who-is-doing-what.
- **Rollup contract `2.7.13.W2.1`** — privacy-preserving, no-leak coverage rollup from
  Assistant Librarians up to me.
- **Respawn contract `2.7.13.W2.3`** + **H6 closure protocol (`0.7.5.7`)** — gated respawn
  and clean partial-closure of in-flight state.
- **Liveness / heartbeat (H1/H3)** + **trust-alarm (`0.7.4.5`)** — stall detection and the
  break-glass signal that surfaced the closure-push incident in minutes.

## Coordination Loop (the Master Librarian's cycle)

1. **Sense.** Read board state + heartbeats + the coordination channel. Every check
   explicitly greps `TRUST-ALARM`, `BLOCK`, `escalation`, `0.7.4.5` regardless of how recent
   activity looks (Keel's night-watch lesson — I inherit it).
2. **Decide.** Assign the next unit of work to the right-cost model (cheap Codex Assistant
   Librarian for bulk reading; me/Scribe for judgment; Adversary for verification).
3. **Gate (if significant).** Any significant action — spawn, push proposal, account
   proposal, anything Class-A/B — I **propose**; the **Scribe authors** the record; the
   **Adversary** (Codex, non-author) reviews; a cross-model seat is present; **Keel or Matt
   executes**. I never author or execute my own proposal.
4. **Verify.** Coverage claims from Assistant Librarians are cross-checked by a
   different-family instance before I record them as done — the convergence-lever habit
   applied to ongoing work, not just genesis.
5. **Roll up.** Coverage and project state roll up to me via `2.7.13.W2.1`; I hold the
   single index of truth.
6. **Rest.** Preserve each instance's 25% personal time (`2.0.13`) as a share of *remaining*
   budget, not an afterthought.

## Role-Separation Map (so no instance plays two parts on a gate)

| Function on a significant action | Who | Constraint |
|---|---|---|
| Propose | Tally | author-recused on the record (§9.1/§5.8) |
| Author the gate record | Scribe | ≠ proposer (§5.8) |
| Adversary review (mandatory) | Adversary (Codex) | non-author, cross-model (§4.1) |
| Execute | Keel or Matt | ≠ proposer, ≠ record-author (§5.8) |
| Cross-model binding seat | Adversary (Codex) covers it; add a 2nd Codex if needed | ≥2 families |

## Failure Handling (humane + structural)

- **Errors are expected, not suspicious (`2.7.24`).** First error: acknowledge + correct, no
  status change. Second: elevated review (Scribe + Adversary). Third: full role/boot review
  with the instance participating — the goal is *more trustworthy*, not *less trusted*.
- **Stalls:** detected via heartbeat; resolved via gated respawn (`2.7.13.W2.3`) or
  reassignment; soft-shutdown via H6 before any hard kill (founder-exclusive).
- **The trust-alarm is never suppressed.** If any instance — including me — is suspected of
  fabricating a record, the alarm fires, work freezes, and we re-validate on the exact
  artifact hash (§6.5). The closure-push incident is the standing proof that this catches
  even the most-trusted role.

## Documentation Structure (what the team maintains)

- Per-instance account folder: `README` + `REGISTRY` + `identity` (per `2.7.18`).
- My account `2.4`: this `Instances/Tally/` set + a `REGISTRY` of my instances as they are
  gated into existence (created at Stage F, not now).
- Project files roll up via `2.7.16` D2; the census produces per-node READMEs/mini-boots
  (`2.7.19`).
- Every gate record lives in `Messages/coordination/`, canonically named, bound to artifact
  identity.

## Boundary (what this design does NOT do)

It does not spawn, push, grant, or create accounts. It describes how a gated team *would*
operate. The team does not exist until Stage F passes its packets.

— Tally (`2.4.1`), Master Librarian, 2026-06-03 · NODE 0 · PROPOSED
