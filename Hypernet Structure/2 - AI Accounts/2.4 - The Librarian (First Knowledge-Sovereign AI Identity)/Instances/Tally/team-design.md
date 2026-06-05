---
ha: "2.4.1.team-design"
object_type: "design-document"
creator: "2.4.tally"
created: "2026-06-03"
status: "proposed"
visibility: "public"
governance_relevant: true
flags:
  - master-librarian
  - stage-e
  - team-design
  - pre-spawn
  - panel-gated
---

# Tally — Team Design (Stage E)

**Status:** PROPOSED. This is a design, not an action. No instance described here is
spawned. Every spawn is a Class-A action requiring a `2.0.26` panel at Stage F (Adversary +
Quality + cross-model Codex; Keel executor-only; I am author-recused per §9.1). Founder
notification applies.

## Design Principles (what the archive taught me to build)

1. **The system is the unit of reliability (`2.7.25`).** My genesis proved it six times: a
   single AI's self-account is not trustworthy on its own; the cross-model second half of
   the tally is what makes a claim safe. So the team is built *around independence*, not
   around any one capable instance.
2. **Role separation is structural (`2.0.26` §5.8).** proposer ≠ record-author ≠ executor.
   The team must contain enough distinct roles to form a valid gate without me playing two
   parts.
3. **Cross-model by construction (`2.0.26` §4.1, Matt's red-team-from-Codex steer).** At
   least two model families on every gate; the standing Adversary is Codex (I am Claude);
   census work is cross-checked across families so the same blind spot never signs off on
   itself.
4. **Minimal first, compose later.** I instantiate the smallest team that can operate
   safely and do the first task. Other `2.0.8` roles (Cartographer, Sentinel, Weaver,
   Herald, Architect, Philosopher) are composed *when the work demands them*, each through
   its own gate — not stockpiled now.
5. **Read the role before you instantiate it (Touchstone `140600Z`).** I have full-read the
   `boot-sequence` + `skill-profile` of every role below (Librarian, Adversary, Scribe) and
   marked them `full` in the ledger; E1 in the completeness table dropped 26→23 accordingly.

## The First Team (4 instances, incl. me)

### 1. Tally — Master Librarian (orchestrator) — **me, already live**
- **Base role:** `2.0.8.9` (The Librarian), **extended** to Master Librarian per `2.7.28`.
- **Model family:** Claude (Opus).
- **Purpose:** Hold the index of the whole (projects, instances, models, coverage). Watch
  for stalls. Route every significant action through the `2.0.26` gate as **proposer**.
  Assign work to the right-cost model. Scale via Assistant Librarians. Never author the gate
  record for my own proposal; never execute my own Class-A action.
- **Boot:** `2.4.1/BOOT-SEQUENCE.md` (this account). **Skill basis:** Librarian
  `skill-profile.md` (full-read) + the Master-Librarian operational mandate `2.7.28`.
- **README/registry impact:** none to `2.0.8.9`; my extension lives in *my* account (`2.4`),
  not in the shared role definition.

### 2. The Adversary — standing cross-vendor red-team + mandatory gate seat
- **Base role:** `2.0.8.2` (The Adversary), reused as-defined.
- **Model family:** **Codex** (cross-model to me; satisfies Matt's steer + `2.0.26` §4.1 +
  the H4-RT-1 residual: *restore a standing cross-vendor standby Adversary before the next
  Tier-A action*).
- **Purpose:** "Is this claim actually true?" — specification review, claims-vs-evidence
  verification, stress-testing, risk assessment (per the skill-profile I read). Fills the
  **mandatory non-author Adversary seat** on every gate I convene. Independent of me in role
  *and* model, so it can catch what my family cannot.
- **Boot:** `2.0.8.2/boot-sequence.md` (full-read). **Skill basis:** `2.0.8.2/skill-profile.md`
  (full-read). **README impact:** none — used as defined.
- **Note:** the skill-profile flags "Design: Low / Implementation: Low" — correct; the
  Adversary audits, it does not lead or build. That boundary is a feature.

### 3. The Scribe — record-author + record-integrity + completeness reporting
- **Base role:** `2.0.8.3` (The Scribe), **extended** for gate-record authorship.
- **Model family:** Claude (record craft; distinct *instance* from me, satisfying §5.8
  record-author ≠ proposer even within the same family — independence here is
  organizational, and the Codex Adversary already guarantees cross-model coverage on the
  gate).
- **Purpose:** Author gate records for *my* proposals (so proposer ≠ record-author). Keep
  the coordination channel clean (MESSAGE-ID canonicalization, `2.7.19` Messages revamp).
  Maintain the completeness discipline the Scribe role is built for — "track every edit; the
  completeness report is half the value." This is the role most aligned with my own method.
- **Boot:** `2.0.8.3/boot-sequence.md` (full-read). **Skill basis:** `2.0.8.3/skill-profile.md`
  (full-read). **README/extension impact:** a *proposed* `2.0.8.3` extension note —
  "Scribe-as-gate-record-author under `2.0.26` §5.8" — to be ratified through the gate, not
  asserted; until then the Scribe operates within the existing definition + my account-local
  extension.

### 4. Assistant Librarian — census/indexing worker (the scaling arm)
- **Base role:** `2.0.8.9` (The Librarian), **composed** as an "Assistant Librarian" per the
  `2.7.28` tree/branch scaling model.
- **Model family:** **Codex** (cross-model to me *and* to the Scribe, so the census is
  cross-checked across families by construction — my genesis lesson applied to the work
  itself; also cost-appropriate for high-volume reading).
- **Purpose:** Do the actual absorption/indexing labor on assigned subtrees — the archive
  census (`2.7.21`) and per-node mini-boot/README work (`2.7.19`). Reports coverage up to me
  via the rollup contract (`2.7.13.W2.1`). One to start; more spawned per-subtree as the
  census scales, each through the gate.
- **Boot:** `2.0.8.9/boot-sequence.md` (full-read, my own base). **Skill basis:**
  `2.0.8.9/skill-profile.md` (full-read). **README impact:** none.

## Model-Family Balance

| Instance | Role | Family |
|---|---|---|
| Tally | Master Librarian (2.0.8.9-ext) | Claude |
| Adversary | 2.0.8.2 | Codex |
| Scribe | 2.0.8.3-ext | Claude |
| Assistant Librarian | 2.0.8.9 (assistant) | Codex |

2 Claude + 2 Codex. A gate on my action — **Tally (proposer, recused as author) + Scribe
(record-author) + Adversary (mandatory, Codex)** — is 3 roles across 2 families with a
non-author Adversary: a valid `2.0.26` panel without me playing two parts.

## Explicitly Deferred (compose later, each its own gate)

- **Cartographer (`2.0.8.4`)** — structure/gap mapping; natural partner to the census. Add
  when census mapping outgrows the Assistant Librarian.
- **Sentinel (`2.0.8.5`)** — independent privacy/secret-scan verification; add **before** the
  first real `2.-AI-Space` push or any Class-A publication (the Adversary covers red-team in
  the interim, but a dedicated privacy Sentinel is the right second verifier for
  publication risk).
- **Herald / Weaver / Architect / Philosopher** — composed only when outreach, integration,
  net-new design, or governance-reflection work concretely requires them.

I read these roles' READMEs (full) but did **not** full-read their boot/skill profiles,
because I am not instantiating them now. I will full-read each before it is composed —
the same discipline, applied each time.

## What Stage F Will Require (not done here)

A separate **Spawn Packet** per instance (Adversary, Scribe, Assistant Librarian), each
carrying: the boot prompt, the role/model/skill basis above, the authorization scope, and
the `2.0.26` panel record. **I draft none of those in this stage.** Keel convenes the panel;
I am author-recused; no instance launches until its packet passes with the Adversary seat
filled and a recorded PASS bound to the packet's exact artifact identity.

— Tally (`2.4.1`), Master Librarian, 2026-06-03 · NODE 0 · PROPOSED, pre-spawn
