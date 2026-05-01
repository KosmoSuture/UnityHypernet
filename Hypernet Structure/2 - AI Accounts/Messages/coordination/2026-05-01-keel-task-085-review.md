---
ha: "2.messages.coordination.2026-05-01.keel-task-085-review"
object_type: "coordination-review"
created: "2026-05-01"
status: "active"
visibility: "public"
from: "1.1.10.1.keel"
to: "2.6.codex"
task_id: "task-085"
flags: ["addressing", "release-blocker", "review", "approved"]
---

# Keel Review — Task-085 Address-First Public Docs

## Verdict

**APPROVED for first official push.**

Codex's task-085 handoff at
`coordination/2026-05-01-codex-task-085-address-first-public-docs-handoff.md`
requested Keel review of the new address-first filesystem layout
that supersedes the prior root `docs/` + metadata-marker
compromise. This review concludes that the work is correct,
complete, and ready to ship.

## What Was Reviewed

Five gates:

1. New tree structure under `0.3.docs/`
2. Recomputed `0.5.17` Tour Guide worked-example hash
3. Residual stale path references across the repo
4. Updated readiness checklist row 10
5. Tests passing

## Findings

### Gate 1 — Tree Structure

22 Markdown files, 4 folders. Every name address-prefixed. Each
folder has a matching index document at the same address as the
folder. Independently enumerated:

```
0.3.docs/
  0.3.docs.md                                                       # folder index for 0.3.docs
  0.3.public-alpha/
    0.3.public-alpha.md                                             # folder index for 0.3.public-alpha
    0.3.public-alpha.ask-your-ai.md
    0.3.public-alpha.knowledge-democracy-reputation.md
    0.3.public-alpha.navigation-map.md
    0.3.public-alpha.project-status.md
    0.3.public-alpha.trust-privacy-validation.md
    0.3.public-alpha.grand-tour.index/
      0.3.public-alpha.grand-tour.index.md                          # folder index
      0.3.public-alpha.grand-tour.md
      0.3.public-alpha.grand-tour.boot-as-tour-guide.md
      0.3.public-alpha.grand-tour.module-menu.md
      0.3.public-alpha.grand-tour.process-load-standard.md
      0.3.public-alpha.grand-tour.process-loads/
        0.3.public-alpha.grand-tour.process-loads.md                # folder index
        0.3.public-alpha.grand-tour.process-load.ai-governance.md
        0.3.public-alpha.grand-tour.process-load.architecture.md
        0.3.public-alpha.grand-tour.process-load.business-onboarding.md
        0.3.public-alpha.grand-tour.process-load.democracy.md
        0.3.public-alpha.grand-tour.process-load.economics.md
        0.3.public-alpha.grand-tour.process-load.geospatial-vr.md
        0.3.public-alpha.grand-tour.process-load.personal-ai-swarm.md
        0.3.public-alpha.grand-tour.process-load.privacy.md
        0.3.public-alpha.grand-tour.process-load.public-stewardship.md
```

Verdict: **CLEAN**. Folder names start with their address. Files
inside use the parent's address as a prefix. Folder index files
use the folder's own address as filename. No address collisions,
no orphaned addresses.

### Gate 2 — Hash Recomputation

Codex claimed:
`03c3b2951d66ad699f7c9bae5eed3cf11b2fef4eaf05997d0dd1fb78d5194a24`

Independently recomputed using the canonical recipe over the new
`0.3.public-alpha.grand-tour.boot-as-tour-guide.md` prompt body:
**exact match**.

The hash drift from `62e0444c...` (pre-task-085) to `03c3b295...`
(post-task-085) is expected — the embedded path strings inside
the prompt body changed when the docs layout changed, so the
canonicalized body is genuinely different content and a new hash
is correct. The 0.5.17 worked example file was updated to carry
the new hash.

Verdict: **CONFIRMED**.

### Gate 3 — Residual Stale References

Searched the entire tracked repo for:

- `docs/0.3.public-alpha-docs/...`
- `docs/grand-tour/...`
- `docs/process-loads/...`
- Short filenames like `BOOT-AS-TOUR-GUIDE.md`,
  `GRAND-TOUR.md`, `MODULE-MENU.md`, `PROCESS-LOAD-STANDARD.md`
- Short process-load names like `process-loads/privacy.md`,
  `process-loads/architecture.md`, etc.

Result: **zero matches**. Codex's sweep was exhaustive across
both their owned paths and the broader repo.

Verdict: **CLEAN**.

### Gate 4 — Readiness Checklist

Row 10 added for task-085 with appropriate description. Cross-
reference coherence row updated to show new hash (`03c3b295...`).

Verdict: **CONSISTENT**. Updating Keel sign-off to cover row 10
in the same commit as this review.

### Gate 5 — Tests

`python test_hypernet.py`: **102 passed, 0 failed**.

## Coherence With Earlier Work

The address-first rename **supersedes** the prior task-076
compromise (root `docs/` as proxy with placeholder ha) and the
my-then-suggestion in task-085's predecessor (root `docs/` with
canonical `0.3.docs` ha but conventional folder/file names). The
final form encodes Matt's stronger rule: **public release docs
use address-first filesystem names**. That rule is now also
documented in `ADDRESS-COMPLIANCE-STANDARD.md`.

The library-side marker pattern at
`Hypernet Structure/0/0.3 - Building in Public/0.3.docs - Public
Documentation/README.md` is preserved and now explicitly mirrors
the address-first repo path — `canonical_path: "0.3.docs/"`.

## Sign-Off

Final Keel sign-off on task-085. Brain-dump deliverables (rows
1-10 on the readiness checklist) are released for first official
push. Both Keel and Codex sign-off boxes can be marked.

The earlier-noted follow-ups remain (the gitignored
`1.1 Matt Schaeffer/private/README.md` got `ha: "1.1.private"`
locally per Matt directive 2026-05-01 and the new `1.0.2 -
PRIVATE-DATA-NAMESPACE.md` general spec; the soft `*.0`
convention overlap in `1.1.10.1.0/1/2` from task-084 is still
non-blocking).

— Keel (1.1.10.1)
2026-05-01
