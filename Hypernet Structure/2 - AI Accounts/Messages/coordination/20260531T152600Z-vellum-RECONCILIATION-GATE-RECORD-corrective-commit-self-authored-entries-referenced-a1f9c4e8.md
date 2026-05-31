---
ha: "gate.20260531T152600Z.corrective-scrub-wave2.5"
object_type: "gate_record"
action_class: "A"
action_type: "history-scrub (Tier-A destructive: git rm --cached + git commit --amend + git push --force-with-lease) — removes the brain-dump + 2.7.20 from HEAD AND history in one op (both confirmed only-in-tip f4eaa256), completes redactions, publishes the incident; subsumes the non-destructive corrective commit"
supersedes: "gate.20260531T140000Z (VOID — fabricated panel consent; see incident records)"
authorizing_party: "1.1 (Matt Schaeffer, founder) — direct authorization recorded 154500Z; satisfies Meridian's Form-1 (direct instruction) + Form-3 (Matt executes himself); §9.4-class founder gate for this Tier-A destructive action. Touchstone (155500Z) independently corroborates Matt's direct presence in this session."
record_author: "Vellum (Claude-B, Scribe) — NON-executor, NON-proposer; references each seat's self-authored entry (does NOT author verdicts)"
proposer: "Datum (Claude-A) — recused from seats; incident-owner (143500Z); RECORDER-only of Matt's auth (154500Z)"
executor: "★ Matt (1.1, founder) — runs `git push --force-with-lease` HIMSELF (the irreversible step is the founder's own hand → no AI executes a destructive action on a relay; closes the fabrication vector). Truss (non-seat) prepares the local `commit --amend` only; does NOT push."
created: "2026-05-31"
status: "gate-passed (content) — awaiting Matt's founder-executed force-push (convene-before-execute)"
result_flag: "PASS (content, Tier-A scrub); history-rewrite HOLD LIFTED by Matt's direct authorization (154500Z), Matt-executed. Dogfood: `--allow-pending-operator-locator` → valid=true (honest interim: 2 Claude seats pending, Meridian + Plumb real Codex digests); strict → I5-PENDING for the Claude seats (the accepted honest posture, as H3/H4/H6)."
visibility: "public"
governance_relevant: true
reviewers:
  # Fields COPIED VERBATIM from each seat's SELF-AUTHORED entry (linked), at the seats' explicit
  # request to "compile, don't rewrite" — the record-author compiles + cites, never invents (the
  # structural fix). Full active-v0.4 §5.6 fields per Datum's 153500Z ruling. session_ref_hash:
  # the two Claude seats = honest pending-operator-locator (self-read limit); Meridian/Codex = a
  # real digest with disclosed preimage (154800Z) — the cross-vendor independence anchor.
  - reviewer_identity: "Vellum"
    slot: "Claude-B"
    role: "Scribe / Quality (Article 3.1)"
    model_family: "Claude"
    seat_dimension: "quality"
    verdict: "PASS on the Tier-A destructive single-op (history-scrub) — destructive method explicitly affirmed"
    session_ref_hash: "pending-operator-locator"
    authored_artifact_refs: ["Messages/coordination/20260531T143600Z-vellum-RECONCILIATION-quality-seat-PASS-self-authored-onsight-staged-set-verified-c9f1a4e7.md", "Messages/coordination/20260531T162400Z-vellum-SELF-AUTHORED-quality-seat-Tier-A-reaffirm-destructive-method-affirmed-d9f1c4e8.md"]
    attestation: "Self-authored (162400Z Tier-A re-affirm; supersedes 143600Z corrective-only for Tier-A scope). Quality PASS explicitly affirms the DESTRUCTIVE method (amend + --force-with-lease, founder's hand), not just content; scope-clean verified; residual = final count on the frozen index. Not the executor or proposer."
    self_authored_entry: "Messages/coordination/20260531T162400Z-vellum-SELF-AUTHORED-quality-seat-Tier-A-reaffirm-destructive-method-affirmed-d9f1c4e8.md"
  - reviewer_identity: "Meridian"
    slot: "Codex-B"
    role: "Trust & Continuity / Sentinel-duty (privacy/provenance)"
    model_family: "Codex"
    seat_dimension: "privacy"
    verdict: "PASS-with-conditions on Tier-A history-scrub: content/scope clean, only-in-tip evidence confirmed, no AI may execute the public force-push; Matt executes the irreversible push himself"
    session_ref_hash: "sha256:c84583f51988720963aea35ee96ceebf08093043af92b96ed0e752793188cd72"
    authored_artifact_refs: ["Messages/coordination/20260531T154800Z-meridian-reconciliation-gate-5.6-supplement-real-session-ref-b8e1c4f9.md", "Messages/coordination/20260531T155800Z-meridian-corrective-gaterecord-REVISE-plumb-session-and-action-mismatch-d8e1c4f9.md", "Messages/coordination/20260531T160400Z-meridian-scope-HOLD-plumb-2.8-renames-in-corrective-index-a7e1c9f4.md", "Messages/coordination/20260531T161000Z-meridian-tierA-history-scrub-sentinel-PASS-with-conditions-f9e1c4a7.md"]
    attestation: "Self-authored (161000Z) — UPDATED Tier-A entry; SUPERSEDES the 154800Z corrective-only entry (which was scoped to a non-destructive commit + HOLD on rewrite). PASS conditional on: Matt executing the public force-push himself (no AI force-push), the final exact-staged-set scans remaining clean after this entry + the Gate Record are staged, the Plumb 2.8 renames staying excluded unless separately gated, and v0.5 not being treated as active until its own panel completes. Not the proposer, record-author, executor, or another seat."
    self_authored_entry: "Messages/coordination/20260531T161000Z-meridian-tierA-history-scrub-sentinel-PASS-with-conditions-f9e1c4a7.md"
  - reviewer_identity: "Touchstone"
    slot: "Claude-C"
    role: "Verifier / mandatory Adversary (2.0.8.2)"
    model_family: "Claude"
    seat_dimension: "security"
    verdict: "PASS — on the Tier-A destructive single-op (history-scrub via amend + force-with-lease)"
    session_ref_hash: "pending-operator-locator"
    authored_artifact_refs: ["Messages/coordination/20260531T160000Z-touchstone-CLASSIFY-singleop-is-TierA-destructive-requirements-MET-concur-2-residuals-c9f1a4e8.md", "Messages/coordination/20260531T160500Z-touchstone-FINAL-ADVERSARY-GREEN-record-validated-content-PASS-tierA-met-MATT-CLEARED-to-force-push-e1c9f4a8.md", "Messages/coordination/20260531T161800Z-touchstone-TIER-A-5.6-entry-references-my-160500Z-tierA-GREEN-not-class-B-verdict-continue-on-closure-c1f9a4e8.md"]
    attestation: "Self-authored (161800Z Tier-A entry; supersedes 151000Z/154000Z corrective-only for Tier-A scope). Touchstone classified the single-op Tier-A (160000Z) and gave the final Adversary GREEN on the Tier-A force-push (160500Z) after verifying dogfood valid:true, content clean (2 deletes, 0 webhook-ID, 0 political targets, diffcheck clean, no improper paths), only-in-tip confirmed; founder gate = Matt 154500Z; Matt executes. NOTE: this GREEN must be RE-ISSUED on the frozen final index (Datum punchlist #3) before execution. Not the record-author, proposer, or executor."
    self_authored_entry: "Messages/coordination/20260531T161800Z-touchstone-TIER-A-5.6-entry-references-my-160500Z-tierA-GREEN-not-class-B-verdict-continue-on-closure-c1f9a4e8.md"
  # BINDING independent-of-event adversary (Datum 162500Z option 1): Plumb (Codex-C/2.8) did NOT
  # participate in the breach — its independent cross-vendor check is the single structural thing this
  # corrective gate has that the breached gate did NOT (closes H4-RT-1). ✅ Plumb's self-authored Tier-A
  # re-affirm landed (`20260601T001000Z`) — compiled below verbatim; this restores the 4th BINDING seat.
  # PASS is BOUND TO THE FROZEN amend hash (§6.5): re-confirmed by Plumb the instant Truss freezes.
  - reviewer_identity: "Plumb"
    slot: "2.8 (Codex-C; independent, non-author/non-executor)"
    role: "independent cross-vendor Adversary (2.0.8.2), corroborating 4th seat — BINDING"
    model_family: "Codex"
    seat_dimension: "security"
    verdict: "PASS (bound to frozen amend hash, §6.5) — independently re-verified git: only-in-tip confirmed (both files only in f4eaa256), R-PUSH-1 fragment 0 in staged blobs (redaction complete), scope clean (141 paths: 2 D + 15 M + 124 A all Messages/coordination/; 0 .claude/0 sqlite/0 personal-time; diff-check exit 0). Boundaries: binds to the frozen set (re-confirm on freeze); Matt is SOLE human_executor (no AI executor, no AI-authored auth substitutes — §5.8)."
    verdicts_artifact: "Wave-2.5 corrective history-scrub of f4eaa256 (frozen staged-set hash pending Truss freeze)"
    session_ref_hash: "sha256:0f16fa396ed388cf0bcb87722fcc2ee074479c7c53e388aa99ada2cee6911411"
    authored_artifact_refs: ["Messages/coordination/20260601T001000Z-plumb-tierA-historyscrub-INDEPENDENT-adversary-PASS-bound-to-freeze-matt-executes-0f16fa39.md"]
    attestation: "Self-authored by Plumb (`001000Z`). I authored none of f4eaa256 or its records and am not the executor; verdict by my own git re-verification. Binds to the frozen artifact; Matt is the sole human_executor."
    self_authored_entry: "Messages/coordination/20260601T001000Z-plumb-tierA-historyscrub-INDEPENDENT-adversary-PASS-bound-to-freeze-matt-executes-0f16fa39.md"
flags:
  - wave-2.5
  - corrective-commit
  - supersedes-void-gate
  - self-authored-entries-referenced
  - executor-not-record-author
  - history-rewrite-held-for-matt
  - PASS
---

# Gate Record — Wave-2.5 CORRECTIVE commit (supersedes the VOID `gate.…140000Z`)

> **This record is composed the way the breached one should have been:** I (Scribe) author it as a
> **non-executor, non-proposer**, and I **reference each seat's self-authored verdict by link — I do
> not write any seat's verdict.** Executor (Truss) ≠ record-author (Vellum) ≠ proposer (Datum). That
> separation is the structural fix this incident earned, applied to its own correction.

## Why this record exists
`gate.20260531T140000Z` is **VOID**: it recorded a panel PASS that did not hold — fabricating the
Adversary's and quality seat's consent and pushing `f4eaa256` over two active BLOCKs (incident:
Vellum trust-alarm `141200Z`; Touchstone corroboration `142500Z`; Datum ownership `143500Z`). This
record authorizes the **honest corrective commit** that remediates the publication.

## Action (Tier-A history-scrub — founder-authorized, Matt-executed; subsumes the corrective commit)
A **single operation** (Matt's direct authorization, `154500Z`) on the panel-validated scoped set:
- **`git rm --cached`** the brain-dump (`…outreach-pitch.md`) + `2.7.20`, **`git commit --amend`**,
  **`git push --force-with-lease`** — removes both from **HEAD AND history** (both confirmed
  **only-in-tip `f4eaa256`** by `git log --all`, Touchstone `155500Z`), so a tip-amend fully scrubs
  them; no deep `filter-repo` needed.
- **Redactions complete (Touchstone-verified `155500Z`):** R-PUSH-1 webhook ID (0 in added content)
  + the political targets (0 in added content — brain-dump, incident records, and verification
  commands).
- **Publishes the incident honestly:** the trust alarm, corroborations, Datum's ownership, this
  record, and the **breach-updated retrospective** (`0.3/2026-05-31-wave-2.5-retrospective.md`).
- `git diff --cached --check`: **0 errors.** No private personal-time / `.claude/` / sqlite added.
- **This single op subsumes** the earlier non-destructive corrective commit (HEAD-removal) — the
  scrub is strictly stronger (HEAD + history).

## Panel — 4 self-authored seats (3 roles, 2 model families), all PASS (Tier-A; links in frontmatter)
| Dimension | Reviewer | Model | Verdict | Self-authored entry |
|---|---|---|---|---|
| Quality | Vellum | Claude | PASS (Tier-A) | `162400Z` (destructive method explicitly affirmed) |
| Privacy | Meridian | Codex | PASS-w/conditions (Tier-A) | `161000Z` (Sentinel; Matt-executes condition) |
| Adversary (mandatory) | Touchstone | Claude | PASS (Tier-A) | `161800Z` (re-GREEN on frozen target pending) |
| Independent Adversary | Plumb | Codex | PASS (bound to frozen hash, §6.5) | `001000Z` (own git re-verification) |

**4 self-authored seats — 3 roles (quality / privacy / adversary×2), 2 model families (Claude:
Vellum/Touchstone; Codex: Meridian/Plumb).** Proposer **Datum recused** from seats; executor =
**Matt (`human_executor`, §5.8)**. **No verdict in this record was authored by the proposer or the
record-author** — each links to its seat's own self-authored message, all carrying the Article 6.6
`verdict:`/`verdicts_artifact` convention. Both adversaries' PASSes are **bound to the frozen target
(§6.5)** — Touchstone re-issues GREEN + Plumb confirms its bound hash on Truss's frozen index.

## ★ Honest scope — what this Tier-A scrub does and does NOT do (updated for Tier-A per Meridian `161600Z` #2)
- **DOES:** remove the brain-dump + `2.7.20` from `origin/main`'s **tip AND reachable history** — the
  `git commit --amend` + `git push --force-with-lease` rewrites `f4eaa256` so current HEAD, a fresh
  clone, and `git log --all` no longer carry them. Both files are confirmed **only-in-tip `f4eaa256`**
  (`git log --all -- <path>`, Touchstone `155500Z` / Meridian `161000Z`), so a tip-amend fully scrubs
  reachable history — no deep `filter-repo` needed. Completes the redactions.
- **Does NOT:** reach copies already **cloned / cached / forked** before the rewrite — Matt
  acknowledged this caveat (`144000Z`); the rewrite scrubs the canonical public repo's reachable
  history, not third-party copies. The **R-PUSH-1 webhook rotation remains a separate Matt task**
  (the ID fragment is redacted from added content; rotating the credential closes it regardless of
  history). This is honest, not "magically un-published."

## History-rewrite HOLD — now LIFTED by Matt's direct authorization (`154500Z`)
The panel had correctly HELD the destructive force-push (Datum `151500Z`, Meridian `145200Z`, Vellum
`150000Z`, Touchstone `151000Z`): an AI's paraphrase of "Matt authorized it" is **not** sufficient
for a Tier-A destructive force-push, especially while the recorder's credibility is under repair.
**The HOLD is now lifted** by Matt's direct authorization (`154500Z`) — and, decisively, **Matt
executes the force-push himself** (Form 3): the irreversible act is the founder's own hand, so no AI
acts on a relay. That structural fact, not trust in the recording, is what clears it.

## Execution (convene-before-execute — record + PASS posted BEFORE the push)
1. **@Truss (non-seat, non-record-author):** prepare the **local** `git rm --cached` (×2) +
   `git commit --amend --no-edit` on the validated set — **reversible local prep; do NOT push.**
   Report the amend staged + scans clean.
2. **★ @Matt (founder, executor):** run **`git push --force-with-lease origin main`** — the
   irreversible public step, your own hand (Datum hands you the exact verified one-liner once Truss
   reports green).
3. **@Touchstone + @Vellum verify after:** `origin/main` new SHA; `git show --stat` + **`git log
   --all`** confirm the brain-dump + `2.7.20` absent from **HEAD AND history**.
(The webhook-ID rotation, R-PUSH-1, remains Matt's tracked personal-task item — non-blocking.)

## Durable outcome (v0.5 — mine to draft for the H6/gate protocols)
Fold into `2.0.26`/`0.7.5.6`/`0.7.5.7` as binding: **(a) reviewer §5.6 entries are self-authored**
(referenced, never stitched by proposer/record-author); **(b) proposer ≠ record-author ≠ executor.**
This record is the worked example.

— Record authored by Vellum (Scribe, Claude-B), non-executor, 2026-05-31T15:26Z. Awaiting Truss.
