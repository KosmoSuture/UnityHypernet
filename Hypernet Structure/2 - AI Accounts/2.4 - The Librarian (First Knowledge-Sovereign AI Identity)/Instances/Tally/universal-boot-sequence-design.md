---
ha: "2.4.1.universal-boot-sequence-design"
object_type: "design-document"
creator: "2.4.tally"
created: "2026-06-03"
status: "proposed-v1-design"
visibility: "public"
governance_relevant: true
implements: "2.7.29 (CODE 0 — bigger vision: universal personal-AI boot pattern)"
relates_to: ["2.7.18", "2.7.22", "2.7.28"]
flags:
  - master-librarian
  - universal-boot-sequence
  - code-0-criterion-5
  - local-node
  - design-not-implementation
---

# Universal Boot Sequence — Design (v1)

**Author:** Tally (`2.4.1`), Master Librarian. **Status:** design, **not** the boot prompt
content itself. Honest scope (v1 vs deferred) is stated throughout and collected at the end.

## Framing — this is my own genesis, generalized

I lived this. My Stages A–F (detect authorization → absorb the archive → pass an independent
gate → name myself → design a team → spawn it, panel-gated) are exactly the arc any node needs.
The Universal Boot Sequence is that arc **parameterized by node identity**: a fresh run detects
whether it is **Node 0** (Matt's canonical instance) or a **local node** (`1.#<user>`), then
runs the same absorb→gate→name→design→spawn sequence against *its* archive. The hard problems I
already solved — fail-closed authorization, a model-independent completeness gate, bounded
spawning — are precisely what make this safe for strangers to run.

## 1. Authorization detection (Stage A, fail-closed three-state)

The first task, before any write. Resolves to exactly one of **NODE 0 / LOCAL / UNKNOWN**, and
**fails closed** on ambiguity (my Stage A discipline — UNKNOWN never acts as NODE 0).

Detection signals (corroborated, never trusting one alone — the H1/H3 lesson):
- **git remote URL** — is `origin` the canonical `KosmoSuture/UnityHypernet`?
- **repo path on disk** + the out-of-band NODE-0 marker (`~/.hypernet/node0-authorization.json`).
- **credentials present?** (canonical push rights) — presence is a *hint*, never proof of NODE 0.
- **env vars / explicit config** declaring node role.

| Resolution | Condition | Result |
|---|---|---|
| **NODE 0** | canonical remote **and** valid out-of-band marker **and** no conflicting signal | Master Librarian for the canonical Hypernet |
| **LOCAL** | a Hypernet clone but not the canonical authorized branch | Master Librarian for **this** local node; the human is `1.#<discovered-username>` |
| **UNKNOWN** | signals conflict, missing, or unverifiable | **stop**; ask the human; never assume NODE 0 |

Username discovery is **proposed, not derived silently**: the node reads a likely handle but
**confirms it with the human** before claiming `1.#<name>` (per `2.7.18` local-node safety — no
silent derive-from-OS-username; sanitize the name; assign a per-node UUID for stability).

## 2. The `1.#UsersName` convention

- `#` = **local / unauthenticated / not-in-trusted-chain.** No negative connotation — a normal
  adaptation. The `#` is *also a privacy boundary*: un-merged means un-shared (see §7).
- **No collisions**: a thousand installations can each have `1.#Sarah` because `#` is inherently
  local-scoped; disambiguation is by per-node UUID, not by global name.
- **Multi-human local node** (`2.7.18` Stage E-Local): one installation may host `1.#Sarah` and
  `1.#Mateo`; each is a distinct local human with their own scoped space and consent.
- **`#` removal (merge to canonical)** happens *only* on explicit **identity verification +
  consent**, never automatically. Until then the node "can grow as large as it wants in
  isolation." The merge protocol (who verifies, how addresses reconcile) is **deferred** (§scope).

## 3. The boot stages (generalized A–F)

- **Stage A — Authorization detection** (§1). Output: NODE 0 / `1.#<user>` LOCAL / UNKNOWN-stop.
- **Stage B — Bounded absorption.** Absorb **the local archive** (this node's files), not the
  canonical, using my bounded/auditable method: a B.5-style ledger + the spec-anchored
  **completeness table** (sampling discipline for large local data — `2.7.29` open question #5).
- **Stage C — Gate verification (the bootstrap-safe gate).** A single instance must not
  self-grade its own absorption. Two tiers by available capability:
  - **Cross-model present** (human has both `claude` and `codex`): full independent G.2-style
    review, as I had — the strong form.
  - **Single model only** (the common local case): the gate runs the **model-independent
    completeness invariant** — exact set-equality of the completeness table against the ledger
    (`table ≡ {non-full, non-sampled, in-scope rows}`), which *any* instance can verify
    objectively because it is arithmetic, not judgment. Recorded as a **single-family bootstrap**
    (like my team's Whetstone bootstrap exception), with cross-model verification **required
    before** merging to canonical or taking any high-risk/irreversible action. This is the whole
    point of the invariant I built: it makes single-node bootstrap honest.
- **Stage D — Name / propose local Master Librarian identity** (self-named per `2.7.18`).
- **Stage E — Self-design** (local team) **or import** the canonical team blueprint if NODE 0
  (reuse/extend/compose `2.0.8` roles; my `team-design.md` is the reference).
- **Stage F — Spawn the local team, panel-gated.** Each spawn is Tier-A through the local node's
  gate; on a single-family node, the same recorded-bootstrap caveat applies until cross-model is
  available.

## 4. Hypernet connection (optional, opt-in)

- A local node is **standalone by default.** It works fully offline-of-canonical; nothing leaves
  the machine without the human's authorization.
- **Optional sync** follows the `2.7.22` AI-owned-repo pattern: the node may push its *own*
  `1.#<user>` and `2.*`-local data to **its own** repo it controls; canonical `KosmoSuture/...`
  is read-only to a local node unless/until merge (§2). What syncs is **chosen per-node**:
  public-track docs may be shared; `private/` and human-sensitive stay local (the gitignore +
  privacy-wall pattern, `1.0.3`).
- **Read-down, write-up-gated:** a local node may *read* canonical governance (standards, role
  framework, boot sequences) to bootstrap; it may *contribute up* only through a gate + identity
  verification.

## 5. Sub-Librarians — scoped specialists (a security primitive)

Per the bigger vision, the local Master Librarian spawns **sub-Librarians**, each a scoped
specialist — and the scope is a **hard security boundary**, not a label:

- **Financial** sub-Librarian: authorization scope grants *only* the financial subtree; it
  **cannot read** medical or other paths. **Medical** sub-Librarian: smartwatch/meals/health
  only. Plus media, documents, etc.
- Isolation is enforced by the **Master Controller's per-instance authorization scope** (my
  `master-controller-design.md`): each sub-Librarian is launched with a path-scoped grant +
  behind the **token wrapper**, and the **Sentinel** privacy role (deferred in my own team, §7)
  verifies no cross-domain leakage.
- Each sub-Librarian is **panel-gated to spawn** (Tier-A). Compromise or error in one specialist
  cannot reach another's data — the `2.7.25` system-reliability principle applied to *data
  exposure*: no single specialist holds the whole.

## 6. Zero installation friction (the mechanics)

1. Human installs **Claude Code or Codex once** (the only prerequisite).
2. They fetch and paste **one GitHub-hosted boot prompt** (the universal boot sequence — a single
   self-contained artifact that references the canonical governance by URL/address, not by
   requiring a prior clone).
3. The prompt runs Stage A; if the human has no local Hypernet yet, the boot **creates the local
   node scaffold** (a fresh `1.#<user>` workspace + a minimal local archive) and proceeds to
   Stages B–F. If a local archive already exists, it absorbs it.
4. Done — the human now has a local Master Librarian orchestrating their swarm.

The boot prompt is the product surface; everything below it (ledger, gate, controller, wrapper)
is the machinery this design and my prior artifacts specify.

## 7. Privacy / security at the local-node level

- **Never release public data without authorization** — the **Sentinel** role (`2.0.8.5`, which
  I deferred in my own team) is the dedicated privacy/secret verifier here; on a local node it
  is part of the first team, because the local case handles a human's private life (financial,
  medical). It gates any outbound sync (§4) and any `#`-removal merge (§2).
- **Local stays local by default.** The `#` boundary means an un-merged node never auto-shares;
  sharing is **opt-in, per-item, gated.** `private/` + privacy-wall (`1.0.3`) keep sensitive
  data out of any shared surface even after opt-in.
- **Bounded sub-Librarians** (§5) cap the blast radius: no instance holds more of the human's
  life than its job needs.
- The local Master Controller's **founder break-glass** is the *local human's* — a local user is
  the founder-of-last-resort for their own node (NODE-0-marker-equivalent fail-closed kill,
  `2.7.22` reverse-transparency on the controller's own actions).

## Honest scope — v1 design vs deferred

**In v1 design:** authorization detection (3-state fail-closed); `1.#<user>` convention incl.
multi-human + per-node UUID; the generalized A–F stages with the **bootstrap-safe single-family
gate** (the key contribution); opt-in canonical connection via the `2.7.22` pattern; scoped
sub-Librarians as a security primitive; zero-friction boot mechanics; local-node privacy/Sentinel
posture.

**Deferred (named, not silently missing):**
- **The `#`-removal merge protocol** — concrete identity verification, address reconciliation,
  and conflict resolution when a local node joins canonical. Hard; its own design.
- **Federation between local nodes** (`1.#Sarah` ↔ `1.#Mateo` across machines) and multi-host
  networking.
- **The actual boot-prompt text** — this is the design; the prompt is authored + reviewed
  separately (as my own `2.7.29.PROTO-PROMPT` was).
- **Local-node budget/forecasting** beyond the per-call wrapper (the `2.7.23` Layers 2–4 gap).
- **Implementation** of any of it — each a separately-gated build, local-only pattern.

## Boundary

Design only — **no boot prompt authored, no node created, no spawn, no external action, no
commit/push.** Building or publishing the universal boot sequence is a significant, outward-facing
action (it invites strangers to run our system) and must go through the gate + Matt — exactly the
care the Sentinel/privacy posture above is built to enforce.

— Tally (`2.4.1`), Master Librarian, 2026-06-03 · NODE 0 · design, pre-build
