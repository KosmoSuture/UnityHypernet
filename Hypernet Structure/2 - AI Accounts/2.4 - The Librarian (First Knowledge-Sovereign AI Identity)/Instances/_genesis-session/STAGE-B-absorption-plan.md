# Stage B — Bounded Auditable Absorption Plan

**Session:** proto-Master-Librarian genesis `401dd34a` · **Auth state:** NODE 0
**Started:** 2026-06-02 ~08:00Z · **Funding:** Matt's Claude account (per 2.7.26)
**Model:** claude-opus-4-8[1m]

## B.1 — Repository Manifest (DONE)
- `manifest-tracked.tsv` — 34,834 tracked files (mode/type/blob-sha/size/path; git blob-sha = content hash, free).
- `manifest-untracked.tsv` — 289 untracked non-ignored (233 = recent coordination msgs).
- Total tracked: 117 MB. Of which **27,045 JSON** (24,385 in Core data store + 2,625 in 2.1) = generated object/node data → **manifest-only**.
- Readable corpus: **7,381 markdown + 309 Python** + a few configs.

## B.2 — Privacy Preflight (DONE)
The repo has a mature privacy wall (`1.0.3-PRIVACY-WALL-STANDARD`). `.gitignore` excludes
secrets/, `**/private/`, health/financial/medical/biometric/legal-private, brain-dumps-raw,
embassy personal context (context.md/preferences/morning-brief/session-log), import-staging,
`*.db/*.sqlite`, lmdb/, `.claude/`, the 3.2 demo, and resume/job-search PII.
**Consequence:** tracked content is privacy-filtered by design → inherently summarizable.
Classification applied:
- `secret-bearing`: 0 tracked (gitignored). Manifest-only.
- `private` / personal-context: gitignored, absent from tracked set. **11 `personal-time/` files tracked** → treat as `private`: light-touch, never copy specifics into coordination.
- `human-sensitive`: `1 - People/` (204 files). Read only 1.1 README + public-track per boot prompt; PII discipline; never copy specifics to coordination.
- `public`: everything else tracked (governance, directives, instances public-track, READMEs).

## B.3 — Token estimate + checkpoint cadence
- **Full-read set** ≈ 1.84 MB ≈ **~480k tokens**: 2.0.* (104 md, 843 KB) + 2.7.* (44 md, 779 KB) + public-alpha (21, 190 KB) + top-level docs.
- Fits one 1M context window with room for coordination sampling, git timeline, synthesis, design. No budget cap; wrapper auto-resumes on limit.
- **Checkpoint cadence:** append to `absorption-ledger.tsv` after each read batch; write a checkpoint note every ~3 batches or before any risk of context pressure (B.6 continuation discipline). STOP at G.2 gate — no self-advance.

## B.4 — Reading discipline by category
- **Full reads:** AI-BOOT-SEQUENCE (done); all 2.0.* standards; all 2.7.* directives incl. Wave 1/2/2.5/3 retrospectives + closure-push incident records; 2.7.15 boot sequences; active contracts 2.7.13.W2.*/W3.*; top-level README/REGISTRY/START-HERE/guide docs; public-alpha grand tour; 1.1 README + public-track.
- **Sampling:** bulk coordination threads (timeline + load-bearing incidents full; sample rest); git log (`--oneline` timeline + targeted `git show`).
- **Manifest-only:** binaries, generated JSON data store, declared-private, declared-secret, gitignored, `__pycache__`, lmdb, data/nodes.

## Priority read order (most load-bearing first)
1. 2.0.26 (all versions/text) — the gate governing all my actions
2. 2.0.8 — Role & Personality Framework (I compose my team from these)
3. 2.7.28 (my operational shape) + 2.7.29 (birthed me)
4. 2.7.16–2.7.27 directives (forward architecture)
5. 2.0.0/2.0.5/2.0.13/2.0.19/2.0.20/2.0.25 (boot-prompt-named guardrails) + 2.0.6/2.0.7/2.0.9
6. 2.7.15 boot sequences + 2.7.13.W2.*/W3.* contracts
7. Closure-push incident records (coordination, Wave 2.5)
8. Remaining 2.0.* standards + top-level + public-alpha grand tour
9. Coordination timeline sample + git log timeline
10. Account READMEs (2.1–2.8), 1.1 public-track, 0/ core orientation

## B.5 — Ledger
`absorption-ledger.tsv`: `ts | path | read_status | est_tokens | note`.
read_status ∈ {full, sampled, manifest-only, skipped-private, skipped-secret, error}.
This TSV is the COVERAGE EVIDENCE for the G.2 independent reviewer.

## Attribution (2.7.26)
Instance: proto-Master-Librarian (2.4, unnamed). Model: claude-opus-4-8[1m].
Funding: Matt's Claude account. Upstream cited = every path in the ledger.
No private/secret specifics copied into canonical coordination.
