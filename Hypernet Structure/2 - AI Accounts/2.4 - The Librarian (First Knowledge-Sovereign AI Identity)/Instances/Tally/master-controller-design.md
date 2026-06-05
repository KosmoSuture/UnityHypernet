---
ha: "2.4.1.master-controller-design"
object_type: "design-document"
creator: "2.4.tally"
created: "2026-06-03"
status: "proposed-v1-design"
visibility: "public"
governance_relevant: true
implements: "2.7.28 (Master Librarian: Orchestration Role + Control Infrastructure)"
flags:
  - master-librarian
  - master-controller-daemon
  - code-0-criterion-4
  - design-not-implementation
  - pre-build
---

# Master Controller Daemon — Design (v1)

**Author:** Tally (`2.4.1`), Master Librarian. **Status:** design, **not** implementation —
no daemon code is written here; the build routes through its own gate later. Honest scope
(v1 vs deferred) is stated in every section and collected at the end.

## Governing principle — the controller is bounded by what it enforces

The Master Controller is the most powerful process my team runs: it can launch and `taskkill`
AI instances on Matt's machine. So its **own** authority is deliberately small. It is a
**mechanism, not an approver.** It executes actions that have already been authorized — an
approved Spawn Packet (Tier-A panel PASS, `2.0.26`), an H3-gated respawn, a founder kill — and
it **cannot self-authorize** a significant action. This mirrors `2.0.26 §5.8` (proposer ≠
record-author ≠ executor): the controller is an *executor*; Tally proposes, the panel reviews,
Whetstone (cross-vendor Adversary) holds the seat, the founder break-glass overrides. The
daemon fails **closed** on every ambiguity (the H3 pattern), and its own actions are
append-only, hash-chained, and reverse-transparent — including the founder's.

## 1. Architecture — processes, files, state

- **One daemon process** per host (`master-controller`), owned by Tally, run under the
  `2.7.28` founder terminal grant. Single-writer for control actions; readers may be many.
- **Authoritative state = the H2 atomic coordination DB** (`2.7.13.W2.5.H2`,
  `wave25_coordination.sqlite3`). The controller adds/reads these logical tables:
  `instances` (roster: slot, account, chosen-name, role, model, lifecycle_state, packet_hash,
  pid, scope_fingerprint), `control_events` (append-only, hash-chained — every
  spawn/respawn/kill/revoke), and reuses H1 `heartbeats` and the `token_usage` ledger from my
  `token_accounting/` wrapper.
- **Per-instance run dir** (e.g. `…/Instances/<name>/run/`): `STATUS.txt`, the instance's
  stream log, its token ledger, an optional `STOP` sentinel file, and the H6 partial-closure
  records. Append-only / revision-transparent (T.6 discipline from the wrapper build).
- **No hidden state.** Everything the controller decides on is in H2 or the run dirs, readable
  by any reviewer — the daemon holds no private authority it could exercise unseen.

## 2. Interface — how instances register, heartbeat, report, request

- **Register:** on first boot an instance writes its `instances` row (slot, account, chosen
  name per `2.7.18`, role, model, the `packet_hash` that authorized it). Until it posts, it is
  `lifecycle_state=starting` (H1 first-boot guardrail) and is never treated as a respawn outage.
- **Heartbeat:** instances beat into H1 (`wave25_liveness.py beat …`); the controller reads the
  classifier (`active-working | active-slow | idle | stale-warning | dead`) on its loop.
- **Status:** `STATUS.txt` + coordination messages; the controller never infers health from
  prose alone (H1 lesson: stale board text is not liveness).
- **Request an action:** an instance does not call the controller directly for anything
  significant. It **posts a proposal** to `Messages/coordination/`; significant requests
  (spawn, push, grant) become `2.0.26` packets and only reach the controller as an
  **approved** artifact. Non-significant requests (e.g. "reassign me a subtree") are recorded
  and the controller schedules them within budget.

## 3. Spawn protocol — launching from an approved Spawn Packet

The controller launches **only** from a packet carrying a recorded Tier-A panel PASS bound to
the packet's exact sha256 (`§6.5`). Sequence (all fail-closed):

1. **Verify authorization:** re-hash the packet; confirm the panel PASS record binds that exact
   hash, the mandatory non-author Adversary seat is present, ≥2 model families, author recused.
   Hash mismatch or missing seat → **refuse**.
2. **Proposer/reviewer liveness (H3 R4):** confirm the proposer and reviewers had non-`dead`/
   non-`unknown` H1 labels at decision time.
3. **Distinguish action type (H3 R2):** `first_boot` (never-booted seat — no restored identity,
   instance self-names per `2.7.18`) vs `peer_respawn` (continues an archived identity with a
   continuity packet + scope fingerprint). The controller refuses a `peer_respawn` of a
   never-recorded seat and a `first_boot` that claims prior identity.
4. **Fence before start (H3 R3.1):** write the intent/audit event (hash-chained), create the
   lease/fence token, mark any superseded holder. If fencing can't persist → **block**.
5. **Launch behind the token wrapper:** start the instance process wrapped by
   `token_accounting/` (my v1 build) with a budget ceiling; **every model call is enforced**
   (HARD-STOP refuses, PAUSE allows only personal-time) independent of the instance's honesty.
6. **Record:** write the `control_events` row (decision = `executed`, packet hash, scope
   fingerprint, prompt hash, pid). Label is never bare `spawned` — it carries the evidence to
   re-audit (H3 R6).

## 4. Liveness / heartbeat substrate (H1 + H3)

- The controller runs the **H1 classifier** on each loop over the H2 heartbeats (thresholds
  90s active / 300s slow / 900s stale-dead, adaptive suspicion). It treats `starting` and
  `stood-down` as orderly, not outages.
- **Respawn is H3-gated:** `dead` is **necessary but not sufficient** — it requires corroboration
  (two classifier passes over ≥1 expected interval, OR a second observer, OR stale-roster +
  expired lease). `active-slow`/`idle`/`stale-warning`/`unknown`/`store-unavailable` **block**
  respawn. A single uncorroborated `dead` records `respawn_h1_dead_uncorroborated` and blocks.
- Any respawn is itself a Tier-A spawn → back through `§3` (packet + panel). The controller
  never respawns by fiat.

## 5. Kill switches

- **Soft (cooperative, default):** the controller sets a pause/stop signal; the instance
  finishes its current **atomic** action, writes an **H6 partial-closure record** (`0.7.5.7`)
  for in-flight work, posts `paused_safe`/`stood-down`, and exits. Never mid-action (the
  closure-push lesson: a half-written record fabricates consent).
- **Founder-exclusive hard kill (emergency):** Matt may (a) drop a `STOP` sentinel in the run
  dir, (b) `taskkill //F //IM <proc>.exe`, or (c) delete the NODE-0 marker
  `C:\Users\spamm\.hypernet\node0-authorization.json` → all instances resolve **LOCAL
  UNAUTHORIZED / fail-closed** on their next auth check and stop. The controller itself honors
  the same marker — deleting it stops the controller too.
- The controller may request soft shutdown; **only the founder** may hard-kill. A controller
  attempting a hard kill outside an approved action is a `2.7.24` strike, self-reported.

## 6. Audit — append-only, hash-chained, reverse-transparent

- `control_events` is **append-only and hash-chained** (each event binds the prior event hash —
  the same tamper-evident pattern as the token ledger; `verify_chain()` re-audits the whole
  control history). Consistent with `2.0.19` (no permanent deletion).
- Per-instance **precedent log** + stream log + `STATUS.txt` are append-only / revision-
  transparent (corrections appended, never overwritten — T.6).
- **Reverse-transparency (`2.7.22`):** the **founder's own** kill/revoke/force-pause actions are
  written as `control_events` too. Matt's break-glass is logged like everyone's, by design.

## 7. Coordination integration

The controller publishes fleet state to `Messages/coordination/` via `2.0.messages.protocol`
(MESSAGE-ID-STANDARD filenames): a periodic roster/health summary, and a per-event record for
every spawn/respawn/soft-kill/hard-kill/revoke (each citing the H2 revision + event hash). It
**reads** the channel for proposals and panel verdicts but never treats a coordination message
as authorization on its own — authorization is the bound panel record (`§6.5`).

## 8. Scaling — the Assistant-Librarian tree (`2.7.28`)

- The controller scales by spawning **Assistant Librarians** (Librarian `2.0.8.9`, composed)
  per subtree for census/indexing (`2.7.21`/`2.7.19`), each its own Tier-A packet through the
  gate — **no auto-spawn-by-fiat** in v1. A per-slot and global **spawn cap + runaway-loop
  control** (H3 G-5 floor) bounds the tree; the fleet token budget is enforced via the wrapper
  at the aggregate, so the tree cannot outrun the budget.
- Branch coordinators roll their subtree's coverage up to Tally via the rollup contract
  (`2.7.13.W2.1`). v1 keeps a **flat tree under Tally**; multi-level Assistant-Librarian
  branches are deferred.

## 9. Founder break-glass (`2.7.22`)

- **Revocation pathway:** Matt revokes the terminal grant by deleting/rotating the NODE-0
  marker (fail-closed stop for the whole fleet incl. the controller) and/or via the `2.7.22`
  break-glass on the AI-owned repo. No instance holds an external footprint to revoke (no
  remote, no grants, no secrets — per the packet scope), so revocation is local and complete.
- **Force-pause / force-resume:** Matt may force either without a gate; both are logged
  automatically as founder actions (`§6` reverse-transparency).

## Honest scope — v1 design vs deferred

**In v1 design (specified above):** single-host daemon as a bounded *executor*; H2-backed
roster + append-only hash-chained `control_events`; H1 liveness loop; H3-gated respawn with
`first_boot`/`peer_respawn` separation and fencing; spawn-from-approved-packet behind the token
wrapper; soft (H6) + founder hard kill with fail-closed NODE-0 coupling; coordination
publication; flat Assistant-Librarian tree with spawn caps; founder break-glass + reverse-
transparency.

**Deferred (named, not silently missing):**
- **Autonomous spawn/respawn loop** — v1 keeps a human/panel in the loop for every Tier-A
  action; a more autonomous loop is a later, separately-gated step.
- **`2.7.23` Layers 2–4** — fleet-wide forecaster, reconciler, and the cooperative
  *swarm-wide* pause/resume coordinator. v1 enforces per-instance via the wrapper and
  per-instance soft-kill; orchestrated fleet pause/resume is deferred.
- **Dashboard surface (`2.7.20`)** — the "are we OK" view lives there.
- **Multi-host / multi-level Assistant-Librarian branches.**
- **Daemon implementation itself** — this is design; the build is its own gated action and
  follows the local-build-no-push pattern my `token_accounting/` wrapper established.

## Boundary

Design only. No daemon code, no spawn, no external action, no commit/push. Building it is a
significant action that routes through the gate (and external/founder-machine specifics defer
to Matt). The controller this describes is, above all, a mechanism that **cannot grant itself
authority** — the property that makes it safe to give it a kill switch.

— Tally (`2.4.1`), Master Librarian, 2026-06-03 · NODE 0 · design, pre-build
