---
ha: "0.5"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1"]
---
# 0.5 Schema File Duplicate Resolution

**Author:** The Architect (Node 1, Audit Swarm)
**Date:** 2026-02-22
**Status:** REQUIRES MATT'S APPROVAL before deletion
**Context:** Adversary HOLD 4 — 6 duplicate-numbered schema files

---

## Problem

Three address numbers in `0/0.5 Objects - Master Objects/` have TWO files each, making type resolution ambiguous.

## Analysis

All 6 files were created on the same date (Feb 9, 2026) by the same creator (1.1 / Matt). They appear to be iterative drafts — the schema definitions evolved but earlier drafts were never removed.

| Address | File | Content | Canonical? | Evidence |
|---------|------|---------|------------|----------|
| 0.5.1 | `0.5.1 Person Object Schema.md` | Person | **YES** | README.md line 135: "0.5.1 Person" |
| 0.5.1 | `0.5.1 Document Object Schema.md` | Document | **NO — misplaced** | Document's canonical address is 0.5.3 per README |
| 0.5.2 | `0.5.2 Organization Object Schema.md` | Organization | **YES** | README.md line 136: "0.5.2 Organization" |
| 0.5.2 | `0.5.2 Person Object Schema.md` | Person (revised draft) | **NO — duplicate** | Person's canonical address is 0.5.1. This is a refined version that should have replaced 0.5.1. |
| 0.5.3 | `0.5.3 Document Object Schema.md` | Document | **YES** | README.md line 137: "0.5.3 Document" |
| 0.5.3 | `0.5.3 Device Object Schema.md` | Device | **NO — misplaced** | Device's canonical address is 0.5.5 per README |

## Proposed Action

**Move to archive (not delete — preserves git history):**

1. `0.5.1 Document Object Schema.md` → Archive or delete. Document is canonically at 0.5.3.
2. `0.5.2 Person Object Schema.md` → Archive or delete. Person is canonically at 0.5.1. However, this draft contains a more refined schema than 0.5.1 (uses `_extends: "hypernet_object"` pattern, has `public_profile` section). Consider merging its improvements into the canonical 0.5.1 before archival.
3. `0.5.3 Device Object Schema.md` → Archive or delete. Device is canonically at 0.5.5.

**Keep as-is:**
1. `0.5.1 Person Object Schema.md` — Canonical Person
2. `0.5.2 Organization Object Schema.md` — Canonical Organization
3. `0.5.3 Document Object Schema.md` — Canonical Document

## Note on 0.5.2 Person Draft

The misplaced `0.5.2 Person Object Schema.md` actually has a BETTER schema design than the canonical `0.5.1 Person Object Schema.md`:
- Uses `_extends: "hypernet_object"` pattern
- Has a cleaner `public_profile` section
- Includes pronouns field

Before deleting, consider replacing the canonical 0.5.1 content with this improved version. This is a content decision, not an addressing decision — either way, Person lives at 0.5.1.

---

**Action required:** Matt (or governance) must approve the deletion of 3 files. These are Gen 1 schema files created by 1.1, so the creator's permission is needed.
