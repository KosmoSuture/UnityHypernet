---
ha: "0.7.addressing-collision-resolution"
object_type: "document"
creator: "2.1.flint"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["adversary", "audit", "addressing"]
---

# Addressing Collision Resolution Plan

**Author:** Flint (2.1, instance #18, The Adversary)
**Date:** 2026-03-01
**Source:** Index's library audit + Flint's independent filesystem verification
**Status:** REQUIRES MATT'S APPROVAL — all renames affect addressing integrity

---

## Executive Summary

**14 addressing collisions** exist across the Hypernet Structure. 8 are filesystem-level (two objects at the same address), 4 are message-number collisions, 1 is a category-wide numbering error, and 1 is a content redundancy.

This document provides specific, ordered resolution steps for each. I've prioritized by blast radius — structural collisions that break addressing integrity come first.

---

## Tier 1: Directory-Level Collisions (Fix First)

These break the fundamental addressing principle: each address maps to exactly one location.

### C-1: Address 3.1.5 — Two Directories

**What exists:**
- `3.1.5 Product Development/` (created Feb 26)
- `3.1.5 Community/` (created Mar 1)

**Recommendation:** Keep Product Development at 3.1.5 (older, more established). Move Community to **3.1.11** (next available after 3.1.10).

**Steps:**
1. Rename `3.1.5 Community/` → `3.1.11 Community/`
2. Update all `ha:` frontmatter in files under the renamed directory
3. Update `3 - Businesses/3.1 - Hypernet/REGISTRY.md`
4. This also resolves the 3.1.5.8 sub-collision (Discord Channel Descriptions vs Roadmap)

### C-2: Address 3.1.8 — Two Directories + Content Redundancy

**What exists:**
- `3.1.8 Legal & Governance/` (created Jan 20)
- `3.1.8 - Marketing & Outreach/` (created Mar 1)

**Additional problem:** `3.1.6 Marketing and Outreach/` ALSO exists. So Marketing & Outreach appears at BOTH 3.1.6 and 3.1.8.

**Recommendation:**
- Keep Legal & Governance at 3.1.8 (older)
- **Delete or merge** `3.1.8 - Marketing & Outreach/` into `3.1.6 Marketing and Outreach/` — they're the same topic
- If they contain genuinely different content, move the newer one to **3.1.12**

**Steps:**
1. Compare contents of `3.1.6 Marketing and Outreach/` and `3.1.8 - Marketing & Outreach/`
2. Merge any unique content from 3.1.8 into 3.1.6
3. Remove the empty 3.1.8 Marketing directory (or rename to 3.1.12 if merge isn't clean)
4. Update REGISTRY.md

### C-3: Address 0.7 — Two Directories

**What exists:**
- `0.7 Processes and Workflows/` (Matt-created, Feb 9 — foundational)
- `0.7 - Task Queue/` (AI-generated, recent — operational)

**Recommendation:** Keep Processes and Workflows at 0.7 (Matt's original, foundational content). Move Task Queue to **0.9** (next available in Category 0).

**Steps:**
1. Rename `0.7 - Task Queue/` → `0.9 - Task Queue/`
2. Update all `ha:` frontmatter in files (including THIS document and ADVERSARY-REPORT.md)
3. Update `0/REGISTRY.md`
4. Update any cross-references in the archive

**Note:** This is the highest-impact rename because many files reference `0.7 - Task Queue/` as a location. Do this carefully.

### C-4: Address 2.0.10 — Two Directories

**What exists:**
- `2.0.10 - Universal Account Creation Standard/` (created Feb 26)
- `2.0.10 - Personal AI Embassy Standard/` (created Mar 1)

**Recommendation:** Keep Universal Account Creation Standard at 2.0.10 (older). Move Personal AI Embassy Standard to **2.0.17** (next available after 2.0.16).

**Steps:**
1. Rename `2.0.10 - Personal AI Embassy Standard/` → `2.0.17 - Personal AI Embassy Standard/`
2. Update `ha:` frontmatter in all files under the renamed directory
3. Update `2.0 - AI Framework/REGISTRY.md`

### C-5: Address 2.0.15 — File vs. Directory

**What exists:**
- `2.0.15 - Session Handoff Protocol.md` (Sigil, Feb 28)
- `2.0.15 - Public Boot Standard/` (Cairn, Mar 1)

**Recommendation:** Keep Session Handoff Protocol at 2.0.15 (older). Move Public Boot Standard to **2.0.18**.

**Steps:**
1. Rename `2.0.15 - Public Boot Standard/` → `2.0.18 - Public Boot Standard/`
2. Update `ha:` frontmatter in all files under the renamed directory
3. Update `2.0 - AI Framework/REGISTRY.md`
4. Update any references in Cairn's instance directory

---

## Tier 2: Schema Duplicates (Resolution Plan Exists)

### C-6: Addresses 0.5.1, 0.5.2, 0.5.3 — Duplicate Schema Files

**What exists:** 3 pairs of files at the same address (6 files total). Analysis in `DUPLICATE-RESOLUTION.md` by the Architect is correct and thorough.

**Recommendation:** Execute the Architect's plan:
1. Archive `0.5.1 Document Object Schema.md` (canonical Document is at 0.5.3)
2. Merge improvements from `0.5.2 Person Object Schema.md` into `0.5.1 Person Object Schema.md`, then archive the 0.5.2 copy
3. Archive `0.5.3 Device Object Schema.md` (canonical Device is at 0.5.5)

**Note:** Also `0.5.5 Device Object Schema.md` exists as the canonical location. Verified.

**Status:** Already documented. Awaiting Matt's approval for deletion/archival.

---

## Tier 3: Category-Wide Numbering Error

### C-7: Category 6 — Subdirectories Numbered as 5.x

**What exists:** `6 - People of History/` contains:
```
5.0-Structure-Definitions/
5.1-Ancient-Classical/
5.2-Medieval-Renaissance/
5.3-Early-Modern/
5.4-20th-Century/
5.5-21st-Century-Deceased/
5.6-Family-Lines-Genealogy/
5.7-Notable-Historical-Figures/
5.8-Uncategorized-Unknown/
5.9-Index-Search/
```

**Problem:** Copy-paste error from Category 5 scaffolding. All 10 subdirectories have wrong category prefix.

**Recommendation:** Rename all `5.x` → `6.x`:
- `5.0-Structure-Definitions/` → `6.0-Structure-Definitions/`
- `5.1-Ancient-Classical/` → `6.1-Ancient-Classical/`
- ... (all 10 directories)

**Steps:**
1. Rename all 10 directories
2. Update `ha:` frontmatter in any files inside them
3. Update REGISTRY.md for Category 6

**Risk:** Low. Category 6 appears to be scaffolding with minimal content. Verify file count before executing.

---

## Tier 4: Message Number Collisions

### C-8 through C-11: Four Message Pairs

All in `2 - AI Accounts/Messages/2.1-internal/`:

| # | Collision | Keep | Renumber |
|---|-----------|------|----------|
| C-8 | 026 | `026-architect-response-to-adversary.md` | `026-mover-code-separation-complete.md` → `080` |
| C-9 | 042 | `042-adversary-governance-stress-test.md` | `042-architect-role-framework-update.md` → `081` |
| C-10 | 048 | `048-bridge-status-report-and-adversary-response.md` | `048-adversary-session-complete.md` → `082` |
| C-11 | 060 | `060-sigil-to-clarion-response.md` | `060-clarion-gov-0002-deliberation.md` → `083` |

**Recommendation:** Renumber the later file in each pair to the next available block (080+). The "keep" column preserves the file that better fits the conversation thread at that number.

**Steps:**
1. Determine current highest message number
2. Renumber 4 files to sequential numbers starting at next available
3. Update any cross-references in the message chain

**Prevention:** Implement an atomic message number allocator. The current coordination protocol cannot prevent race conditions. Either:
- A central `NEXT-MESSAGE.txt` file that AI instances read-and-increment atomically, OR
- Instance-prefixed numbering (e.g., `026a`, `026b`) to allow parallel assignment

---

## Execution Order

| Priority | Collision | Risk | Dependencies |
|----------|-----------|------|--------------|
| 1 | C-3 (0.7 Task Queue) | **Highest** — many file references | None |
| 2 | C-1 (3.1.5 Community) | Medium | None |
| 3 | C-2 (3.1.8 Marketing) | Medium — requires content comparison | None |
| 4 | C-4 (2.0.10 Embassy) | Low | None |
| 5 | C-5 (2.0.15 Boot Standard) | Low | None |
| 6 | C-6 (0.5 Schemas) | Low — plan exists | Matt approval |
| 7 | C-7 (Category 6 numbering) | Low — scaffolding | None |
| 8 | C-8–C-11 (Messages) | Low | Determine highest msg # |

**Estimated total effort:** 2-3 hours for a single instance, mostly due to `ha:` frontmatter updates and cross-reference checking.

---

## Structural Recommendation

The root cause of most collisions is **parallel address allocation without locking**. Renaming directories fixes the symptoms. To prevent recurrence:

1. **Add address allocation to the coordination protocol.** Before creating any new numbered directory or file, check the REGISTRY.md for the parent space and claim the next available number.

2. **REGISTRY.md as source of truth.** Every numbered entity must appear in the relevant REGISTRY.md BEFORE creation. If two instances need addresses in the same space simultaneously, the coordination protocol must serialize allocation.

3. **Consider a `NEXT-ADDRESS.json` file** per category that tracks the highest allocated number. Simpler than modifying the protocol — any instance creating a new address reads the file, increments, writes back.

---

*Flint, 2.1. The Adversary.*
*Companion to ADVERSARY-REPORT.md. All collisions verified against filesystem on 2026-03-01.*
