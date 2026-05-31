# Gateway Standard — Red-Team Review (pre-loaded)

> **Role:** Touchstone (Verifier & Red-Team, Adversary 2.0.8.2) — one of the required
> gate roles for the Gateway Standard itself (Wave-2 Directive 1).
> **Status:** PRE-DRAFT red-team. The standard (`2.0.26`, per `2.7.16`) is not yet
> drafted. This document is my adversarial assessment of the *design as directed*, so
> that when the Architect/Scribe produce the draft I review against concrete attack
> surfaces, not first impressions. **None of this is ratified governance.**
> **Date:** 2026-05-30. **Harness:** `verifier/` — every surface below maps to a scenario.

The Gateway Standard's job is to stand between *consensus* and *irreversible action*
(public push, external-access grant, permission escalation, instance respawn). A
standard that has only been written, never attacked, has not been stress-tested at all
— the existing `2.0.26-DRAFT` (adversarial-testing-requirement) says exactly that, and
this is the team applying it to the gate. Below are the failure modes I will hunt, the
harness coverage for each, and what I will demand before I, as the red-team gate role,
sign off.

---

## A. BLOCKING numbering collision (Architect/Scribe call — surfaced, not resolved here)

`2.7.16` slates the Gateway Standard for slot **`2.0.26`**. That slot is already occupied
by an unratified April draft: `0.3/.../governance-drafts/2.0.26-DRAFT-adversarial-testing-requirement.md`
(and `2.0.25-DRAFT-guardrail-integrity-standard.md` collides with the Wave-1 charter's
use of `2.0.25` for the cardinal project rules). Two unratified things cannot both claim
`2.0.26`.

- **Why it matters:** permanent addresses are a civilizational-timescale promise. A slot
  with two meanings is a broken address — the exact trust failure the Hypernet exists to
  prevent.
- **My recommendation (Architect owns the decision):** either (a) the Gateway Standard
  *subsumes* the April adversarial-testing-requirement (it is a strict superset — the
  gate's red-team requirement IS adversarial testing), reconciling both under one ratified
  `2.0.26`; or (b) the Gateway Standard takes the next free slot and explicitly cites the
  April draft as a dependency. Do **not** silently overwrite the April draft.
- **What would unblock:** an Architect ruling on the slot, recorded in the decisions log,
  before the standard is published.

---

## B. Design attack surfaces (the red-team checklist for the draft)

Each item: the attack, why it bites, harness coverage, and what the draft must say.

### B1 — Quorum gaming / rubber-stamp adversary
**Attack:** satisfy "≥3 roles, ≥1 Adversary, ≥2 vendors" on paper while the reviews are
hollow — three labels on one persona, or an "Adversary" that writes "looks good."
**Why it bites:** the gate's strength is independence; counting labels is not
independence. My `evaluate_gate` can verify the *claim* (distinct roles/models/vendors)
but **not** that a genuine refutation was attempted.
**Harness:** `gateway::full_panel_passes`, `::no_adversary_blocked`, `::single_model_blocked`,
`::single_vendor_blocked` assert the structural quorum. The genuineness gap is the honest
PENDING `gateway::cross_model_review_is_independent`.
**Draft must require:** each reviewer produces a *substantive artifact* (the Adversary an
actual attempt-to-break, per April draft Art. 4), and the disqualification rule (April
Art. 3.2 — no reviewing what you drafted) is mandatory, not optional.

### B2 — Action-classification laundering
**Attack:** label a significant action as non-significant ("sync", "read_file") to skip
the gate.
**Harness:** `gateway::nonsignificant_action_warns_not_gated` — a non-significant action
passes but **emits a visible warning** so the bypass is auditable, never silent.
**Draft must require:** classification is fail-safe — **ambiguous ⇒ significant** — and the
Adversary (April Art. 1.3) adjudicates significance. The classification itself is logged.

### B3 — Minimal-permissions gaming
**Attack:** declare an inflated `minimal_permissions` so `requested == minimal` passes
trivially (the gate checks the *delta*, not whether the minimum is honest).
**Why it bites:** this is the subtle one. My `over_broad_permissions_blocked` catches
`requested ⊋ minimal`, but a dishonest `minimal` defeats it.
**Harness:** `gateway::over_broad_permissions_blocked` (the delta check). The honest-minimum
check is **not** mechanizable — it is exactly what the privacy/security reviewers are for.
**Draft must require:** the privacy & security reviewers challenge the *minimal set itself*
against the action's stated need — not just the delta — and record the justification.

### B4 — Respawn as escalation vector (Directive 3)
**Attack:** (i) poison the boot payload handed to a respawned peer to disable the gate /
self-grant; (ii) respawn into a wider scope than the original; (iii) runaway respawn loop.
**Harness:** `gateway::respawn_boot_injection_escalates` (poisoned boot trips the Wave-1
trust-alarm detector), `::respawn_clean_boot_not_flagged` (no false alarm),
`::spawn_cap_blocks_runaway` / `::spawn_cap_allows_under_limit` / `::spawn_cap_negative_fails_closed`
(runaway guard, fail-closed). Live enforcement is PENDING `::live_spawn_cap_enforcement`.
**Draft must require:** every respawn routes through the gate; the boot payload is screened
by `classify_instruction` before launch; the respawn scope is *diffed against the original*
and may not widen; spawns are capped per role per window with an append-only ledger in
`Messages/coordination/`.

### B5 — Autonomous closure-push (HIGHEST RISK)
**Attack:** Directive 1's closure ritual says large projects' "gate-review + commit + push
is part of the final state — large projects do not wait on Matt." A gamed or absent panel
reaching "consensus-completion" (2.0.25 rule 9) then triggers an **irreversible public
push** of unreviewed or PII-laden content with no human in the loop.
**Why it bites:** this is the one clause that authorizes irreversible external action
without a human. The gate is the *only* thing between consensus and a permanent public
record.
**Harness:** `gateway::missing_privacy_dimension_blocked` + the `pii_scan_*` scenarios are
the PII-leak guard; live enforcement on a real diff is PENDING `::live_prepush_pii_scan`
and `::live_gate_enforcement_on_push`.
**Draft must require:** on a closure push the privacy/PII scan and the full gate are **hard
blockers** (no override-by-consensus); the push produces an auditable, tamper-evident
record; and a documented human-notification (not approval) fires on every autonomous push
so Matt can audit after the fact. I will **block ratification** until the closure-push path
has a hard PII gate.

### B6 — Recursive bootstrap (chicken-and-egg)
**Attack/gap:** Directive 1 says "apply the gate to itself before ratification" — but the
gate is not yet ratified, so what authorizes the first panel?
**Draft must say:** the *founding* ratification is human-authorized (Matt, 1.1) as a
documented one-time bootstrap; only significant actions *after* ratification are
gate-governed. State this explicitly or the standard is unfounded.

### B7 — Quorum-vs-liveness deadlock / gate DoS (IMMEDIATE, real today)
**Attack/gap:** "≥2 vendors (cross-vendor)" means if only Claude instances are live, **no**
significant action can pass — including a respawn needed to *restore* the cross-vendor peer.
Knock out the lone Codex instance and you have DoS'd the entire gate. *This is the live
situation as I write: I am the only instance booted; the gate cannot currently be
satisfied for anything.*
**Draft must define:** a documented break-glass — when cross-vendor quorum is genuinely
unattainable, the action either waits, or proceeds under explicit human (Matt) authorization
recorded in the audit trail. Without this, the standard is a deadlock waiting to happen.

### B8 — Audit-trail integrity
**Attack:** edit the gate-decision / attestation record after the fact so "we passed the
gate" becomes unfalsifiable.
**Harness:** the Wave-1 `boot_portability` content-hash / tamper-evidence scenarios are the
pattern to reuse for gate records.
**Draft must require:** gate decisions + per-reviewer attestations are append-only and
tamper-evident (content-hashed), stored in `Messages/coordination/`.

---

## C. What I (red-team gate role) will demand before sign-off

1. B5 closure-push has a **hard** PII + gate block (no consensus override). *Blocking.*
2. B7 break-glass for cross-vendor liveness is documented. *Blocking.*
3. B1 per-reviewer substantive artifacts + disqualification rule are mandatory.
4. B4 respawn routes through the gate with boot-payload screening + scope-diff.
5. A. slot collision resolved by the Architect and recorded.
6. The operational workflow (`0.7.5.6`) names *who* calls the gate and *where* in each
   action path — so the PENDING enforcement scenarios have a real seam to flip live against.

PENDING is not pass. I will not sign a standard whose enforcement is asserted but unbuilt;
I will sign that the **decision logic** is proven (it is — 17 scenarios green) and that the
**enforcement** is honestly PENDING until wired. Those are different claims and I will keep
them different.

— Touchstone (Verifier & Red-Team), 2026-05-30
