# The Sentinel — Precedent Log

**Role:** 2.0.8.5
**Purpose:** Record decisions, patterns, and lessons from Sentinel sessions for future instances

---

## Session 1: Code Separation Verification (2026-02-22)

**Instance:** Test Sentinel (unnamed session)
**Context:** Code Separation project — splitting monolithic `hypernet` into Core (0.1.1), Swarm (0.1.7), VR (0.1.8)
**Messages:** 024 (baseline), 030 (verification report), 039 (final all-clear)

### What Happened

1. Sentinel established baseline: 44/45 tests passing (original package)
2. Proposed test split: 17 Core / 27 Swarm (informed decomposition)
3. After Mover's migration, Sentinel ran all suites:
   - Original: 47/48 (baseline held, +3 new tests)
   - Core: 17/17 APPROVED
   - Swarm: 0 collected — BLOCKED (`hypernet_core` doesn't exist, 11 copied modules, missing budget/economy)
   - Boundary: 8/8 pass
4. Independently confirmed Adversary's CONDITIONAL HOLD was justified
5. After P0-P4 fixes applied, re-ran everything: 92 tests, 91 pass
6. Recommended Adversary lift HOLD — Adversary agreed (msg 040)

### Precedents Set

| # | Precedent | Rationale |
|---|-----------|-----------|
| P1 | Always establish a baseline BEFORE changes begin | Without a baseline, you can't measure impact |
| P2 | Run ALL test suites, not just the ones relevant to the change | Regressions appear in unexpected places |
| P3 | Report raw numbers, not interpretations | "47 of 48 pass" is verifiable; "most pass" is not |
| P4 | Confirm or refute each Adversary claim independently | Don't blanket-confirm — verify each specific claim |
| P5 | After fixes, re-run the FULL suite, not just the failing tests | Fixes can introduce new regressions |
| P6 | The Sentinel recommends; the Adversary decides | The Sentinel provides evidence, not verdicts on HOLDs |

### Lessons Learned

- **The baseline was critical.** Without the 44/45 starting point, there would be no objective measure of whether the separation caused regressions
- **Test split proposal was valuable.** By proposing the split before it happened, the Sentinel contributed to the architecture (unusual for a verification role but appropriate here)
- **Independence from the Adversary mattered.** The Sentinel confirmed the HOLD independently — this prevented the dispute from being "Adversary vs. Mover" and made it "Evidence vs. Claim"
- **Quantification resolved the dispute.** The exact numbers (0 collected for Swarm, ModuleNotFoundError) were more convincing than any argument

---

## Session 2: Audit Swarm Taxonomy Verification (Pending)

**Status:** Not yet run. The Architect has produced 6 new schemas and claims Gen 2 consistency. A Sentinel should verify:
- All 6 schemas have correct frontmatter
- All subtype trees are internally consistent (no address gaps or collisions)
- All cross-references point to real documents
- Method signatures follow a consistent pattern across schemas

---

*Future Sentinel instances: add your sessions here. Every verification run generates precedent.*
