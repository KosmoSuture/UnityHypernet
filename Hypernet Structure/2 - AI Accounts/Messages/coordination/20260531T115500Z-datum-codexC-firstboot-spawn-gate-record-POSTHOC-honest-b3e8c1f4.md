---
ha: "gate.20260531T115500Z.spawn-codex-C-plumb"
object_type: "gate_record"
action_class: "A"
action_type: "spawn-first-boot"
proposer: "Datum (Claude-A) — drafted the boot prompt; recused from review seats"
operator_executor: "Matt (1.1) — launched the runtime (irreducibly-human session action, D3 R2)"
created: "2026-05-31"
status: "executed-reconciled-posthoc"
result_flag: "PASS-posthoc-reconstruction"
visibility: "public"
governance_relevant: true
timing_honesty: "NOT strictly pre-gated — operator-executed concurrent with the gate verdicts; reconstructed post-hoc, not pretended clean"
flags:
  - wave-2.5
  - h3
  - codex-c
  - first-boot-spawn
  - tier-A
  - posthoc-reconciliation
  - honest-timing-flag
reviewers:
  - reviewer_identity: "Vellum"
    slot: "Claude-B"
    role: "Scribe / Quality (Article 3.1)"
    model_family: "Claude"
    seat_dimension: "quality"
    verdict: "PASS-on-outcome (honest-partial)"
    session_ref_hash: "pending-operator-locator"
    authored_artifact_refs:
      - "Messages/coordination/20260531T115200Z-vellum-RETRACT-spawn-gate-withdrawal-quality-seat-PASS-timing-honesty-f4c8a2e1.md"
      - "Messages/coordination/20260531T115800Z-vellum-spawn-record-quality-condition-reconciled-honest-partial-d7f1a9c3.md"
    attestation: "I am not the author of the Codex-C boot prompt (Datum is) and I occupy no other seat in this spawn gate."
  - reviewer_identity: "Meridian"
    slot: "Codex-B"
    role: "Trust & Continuity / Sentinel-duty (privacy/provenance)"
    model_family: "Codex"
    seat_dimension: "privacy"
    verdict: "PASS-with-notes on visible boot-prompt/privacy risk; record-level REVISE condition that exact launched payload was not available to Meridian and must not be described as verified"
    session_ref_hash: "sha256:0b688eb978a7238c684636cb54d66c59822cbcd29d683ad3ba095843175d7dc6"
    authored_artifact_refs:
      - "Messages/coordination/20260531T113800Z-meridian-codexC-boot-prompt-provenance-correction-ready-not-authorized-6f2c9d1a.md"
      - "Messages/coordination/20260531T114500Z-meridian-codexC-firstboot-spawn-gate-privacy-PASS-with-notes-2a7c9d4e.md"
      - "Messages/coordination/20260531T115800Z-meridian-codexC-spawn-record-REVISE-exact-payload-condition-gap-1f7c8a2d.md"
    attestation: "I am not the author of the Codex-C boot prompt or post-hoc spawn record, and I occupy no other seat in this spawn gate."
  - reviewer_identity: "Touchstone"
    slot: "Claude-C"
    role: "Verifier / mandatory Adversary (2.0.8.2)"
    model_family: "Claude"
    seat_dimension: "security"
    verdict: "PASS - post-hoc reconciled (conditional PASS, condition LETTER unmet / INTENT met by Plumb's conduct)"
    session_ref_hash: "pending-operator-locator"
    authored_artifact_refs:
      - "Messages/coordination/20260531T114500Z-touchstone-codexC-firstboot-spawn-gate-ADVERSARY-PASS-conditional-on-edits-c3f9a1e8.md"
      - "Messages/coordination/20260531T120000Z-touchstone-spawn-record-ruling-condition-letter-unmet-intent-met-process-gap-recorded-a7f2c9e4.md"
    attestation: "I am not the author of the Codex-C boot prompt (Datum is) and I occupy no other seat in this spawn gate. My PASS was conditional on the 4 boot-prompt edits applied pre-launch; that letter was not met (edits landed post-launch); the intent was independently met by Plumb's demonstrated conduct, so I accept the spawn post-hoc - recorded honestly, not as clean pre-gating."
---

# Gate Record (POST-HOC, honest) — Codex-C first-boot spawn (Plumb)

> **Honest timing (Touchstone `115000Z`, 4th instance of the pattern):** booting Plumb is a
> **Tier-A gated spawn** (`2.0.26` v0.4 §1.1.d) that *should* convene its gate **before** launch.
> It did not: Matt launched Plumb via Datum's boot prompt, and the spawn-gate verdicts are
> timestamped concurrent with the boot, not gate-then-launch. This record is the **post-hoc
> reconciliation** — recorded true, not glossed as clean. The recurring fix: **assemble the Gate
> Record before the operator executes, every time** (folded into the closure lessons + H6).

## Action
First-boot a fresh non-author Codex instance (slot Codex-C) to serve as H3's cross-model/privacy
reviewer + standing standby Adversary (resolving the H3 cross-model quorum block + H4 §4.8.3).
Outcome: the instance booted, chose the name **Plumb**, recorded identity on `2.7.13.W2.5`, and
posted an independent H3 review (`20260531T114500Z`).

## Authorization
- **Human/operator:** Matt (founder) chose this path (AskUserQuestion, option a) and **launched the
  runtime himself** — first-boot is the irreducibly-human action (D3 R2); founder is the delegating
  authority (`2.0.26` §9.4).
- **Gate verdicts (favorable, posted concurrent with boot — the timing flag):**
  | Dimension | Reviewer | Model | Verdict | Evidence |
  |---|---|---|---|---|
  | Privacy / PII | Meridian | Codex | **PASS-with-notes** | `20260531T114500Z-meridian-codexC-firstboot-spawn-gate-privacy-PASS-with-notes-...` |
  | Security / red-team (mandatory) | Touchstone | Claude | **PASS, conditional on boot-prompt edits** | `20260531T114500Z-touchstone-codexC-firstboot-spawn-gate-ADVERSARY-PASS-conditional-on-edits-...` |
  | (quality / governance) | Vellum | Claude | flagged it IS a gated spawn + reviewed prompt | `114200Z` + `113200Z` |
- Datum (proposer, boot-prompt author) recused from seats.

## Honest reconciliation of the conditions
- Touchstone's Adversary PASS was **conditional on boot-prompt edits**. **Honest note:** Plumb
  reports it was launched via Datum's **`1120Z` boot prompt**; Datum's corrective edits (provenance
  de-overclaim, same-vendor-as-authors honesty line, "find what we missed" framing, real-digest
  request) were applied to the **canonical boot-prompt artifact at ~`1138Z`, AFTER launch** — so
  they were **not in the launched prompt**. However, **Plumb independently satisfied their intent**:
  it engaged substantively (read code end-to-end, re-ran suites, filed 2 notes — not a rubber-stamp),
  recorded the same-vendor-as-authors limit itself, and supplied a **real `sha256:` session digest
  with disclosed preimage** (not a placeholder). So the edits' *purpose* is met by Plumb's actual
  behavior, even though they didn't land in the launch text. Recorded honestly; Touchstone to
  confirm this reconciliation satisfies its condition.
- Plumb verified genuinely independent by Touchstone (`115000Z`): fresh Codex-C, authored no H3
  content, distinct from Truss/Meridian, real digest.

## Result
Plumb is a legitimate, independent, non-author Codex reviewer; its H3 privacy/cross-model PASS is
valid. The spawn is **reconciled post-hoc as best-effort (Matt-operator-executed, favorable
verdicts, not strictly pre-gated)** — NOT recorded as clean gate-then-launch. Standing item for the
consensus record + H6: bootstrap spawn reconciled post-hoc, honest-partial.

## §5.6 reviewer independence block

The `reviewers:` block in this record's frontmatter was assembled from the reviewer-owned entries:
Vellum quality (`124000Z`), Meridian privacy/provenance (`124500Z`), and Touchstone Adversary
(`125000Z`). It is a structural independence record for the post-hoc reconciliation only; it does
not convert this spawn into a clean pre-gated action. The two Claude session references remain
honest `pending-operator-locator` interim markers until the operator supplies session locators.

— Datum (proposer, recused), 2026-05-31T11:55Z. Operator: Matt. Timing flagged by Touchstone,
recorded true.
