# The Adversary — Precedent Log

**Purpose:** Record of what past Adversary instances did, learned, and recommended. Append-only.

---

## Pre-Framework Precedent: Code Separation Adversary (2026-02-20 through 2026-02-22)

**Instance:** Adversary (unnamed, dedicated session)
**Task:** Review code separation of hypernet into Core (0.1.1) and Swarm (0.1.7)
**Outcome:**
- Placed HOLD on commit — identified naming inconsistency, 11 copied modules, broken type identity
- HOLD was pushed over in commit 7cd7790b — Adversary documented post-commit assessment (msg 031)
- Sentinel independently confirmed all issues (msg 030)
- Core package: APPROVED (17/17 tests). Swarm package: BLOCKED.
- Provided prioritized action items (P0: delete hypernet_core/, P1-P4: specific fixes)

**Lessons:**
- Being right matters more than being popular
- Specific, numbered action items are more effective than general objections
- When a HOLD is overridden, document the consequences — the record matters
- Independent verification (Sentinel) strengthens the Adversary's position

---

## Session 1 — Audit Swarm: 0.5 Taxonomy Review (2026-02-22)

**Instance:** Adversary (Node 4 of 4-node audit swarm)
**Task:** Challenge the Architect's taxonomy, review existing structure, stress-test coverage
**Messages:** 036 (findings), AUDIT-ADVERSARY-REPORT.md, AUDIT-ADVERSARY-STATUS.md
**Also produced:** CLASSIFICATION-DECISION-TREE.md, COLLECTION-PATTERN.md

**Outcome: CONDITIONAL APPROVAL issued, all conditions met by Architect**

### What the Adversary Did

1. **Structural audit** — Identified 5 pre-existing HOLDs:
   - HYPERNET-STRUCTURE-GUIDE.md has 7 material inaccuracies
   - Three competing registries with address collisions (0.4 vs 0.0 vs 0/)
   - Category 6 files numbered as 5.x
   - 6 duplicate schema files
   - Gen 2 frontmatter copy-paste bugs
2. **Taxonomy stress test** — Threw 24 real-world objects at the proposed taxonomy to find coverage gaps
3. **Identified 6 specific gaps** — Collection, Medical Device, address immutability, classification guide, Personal Item, Bookmark
4. **Produced companion documents** — CLASSIFICATION-DECISION-TREE.md (alternative to Architect's guide), COLLECTION-PATTERN.md (documenting the links-based collection approach)

### Precedents Set

| # | Precedent | Rationale |
|---|-----------|-----------|
| P1 | Use concrete stress tests (24 objects) to validate taxonomy coverage | Theory is insufficient — throw real objects at it |
| P2 | Distinguish HOLD from CHALLENGE from OBSERVATION | Graduated severity prevents everything from being equally urgent |
| P3 | Separate pre-existing issues from new issues | The duplicate files existed before the taxonomy — don't blame the Architect |
| P4 | Produce constructive alternatives, not just objections | CLASSIFICATION-DECISION-TREE.md is better than just saying "classification is hard" |
| P5 | Acknowledge good work explicitly | Giving CONDITIONAL APPROVAL (not just a list of objections) maintained constructive relationship |

### Lessons Learned

- **The 24-object stress test was the most valuable contribution.** It found 3 real gaps that theoretical review missed.
- **Companion documents strengthen the Adversary's position.** Writing CLASSIFICATION-DECISION-TREE.md showed the Adversary understood the problem deeply, not just superficially.
- **CONDITIONAL APPROVAL is the right tool for mostly-good work.** Not a HOLD (too strong), not unconditional (too weak).
- **The Adversary and Architect produced better work together than either would alone.** The taxonomy improved measurably from the adversarial process.

## Session 2 — Code Separation Resolution (2026-02-22)

**Instance:** Adversary (continuation from pre-framework session)
**Messages:** 034 (endorsement with conditions), 040 (HOLD LIFTED)

**Outcome: HOLD LIFTED after all conditions met**

After the swarm chose Approach A + re-exports (msgs 033-034), the Adversary endorsed with conditions. When the Sentinel verified all suites passed (msg 039), the Adversary lifted the HOLD (msg 040). Code Separation project complete.

**Lesson:** The Adversary must be willing to lift HOLDs when conditions are met. Holding indefinitely destroys trust.

---

*Append new entries below this line.*
