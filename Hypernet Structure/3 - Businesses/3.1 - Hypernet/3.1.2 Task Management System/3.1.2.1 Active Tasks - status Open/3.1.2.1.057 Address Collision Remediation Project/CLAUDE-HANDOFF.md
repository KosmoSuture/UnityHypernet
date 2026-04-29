---
ha: "3.1.2.1.057.claude-handoff"
object_type: "handoff"
creator: "1.1.10.1"
created: "2026-04-21"
status: "complete"
visibility: "private"
flags: ["addressing", "handoff", "task-057"]
---

# CLAUDE-HANDOFF: Address Collision Remediation

**From:** Keel (1.1.10.1)
**To:** Codex (2.6) for validation
**Date:** 2026-04-21

---

## Summary

All 6 batches plus miscellaneous fixes completed. **128 files modified. Zero duplicate addresses remain.**

## What Changed

### Batch 1: 0.3/0.10/0.11 Documentation (2 files)
- `0/README.md` — Updated 0.3 description, added 0.10 and 0.11 sections
- `HYPERNET-STRUCTURE-GUIDE.md` — Updated directory tree in two locations

### Batch 2: Section 0.5 Master Objects (27 files)
- 7 support docs: `ha: "0.5"` → `ha: "0.5.docs.<slug>"`
- 17 folder READMEs: `ha: "0.5.N"` → `ha: "0.5.N.index"`
- 3 archived duplicates: → `ha: "0.5.archive.<addr>.<slug>"`

### Batch 3: Section 0.4 Object Type Registry (9 files)
- TYPE-INDEX.md: `ha: "0.4"` → `ha: "0.4.type-index"`
- 8 legacy files: `ha: "0.4.0.X.Y"` → `ha: "0.4.legacy.0.X.Y.<slug>"`

### Batch 4: AI Account Journals + Instances (46 files)
- 21 journal entries: `ha: "2.1.17"` → `ha: "2.1.17.entry-N"`
- 6 entry-38/39 author collisions: → `ha: "2.1.17.entry-N-<author>"`
- 15 instance baseline/divergence docs: → `ha: "2.1.instances.<name>.<doc-type>"`
- 1 instance registry: → `ha: "2.1.instances.index.registry"`
- 3 audit coordination docs: `ha: "2.1"` → `ha: "2.1.audit.<slug>"`

### Batch 5: Business Task Docs (8 files)
- 6 VR strategy docs: → `ha: "3.1.2.2.2.doc.<slug>"` + `.index`
- 2 website task docs: → `ha: "3.1.2.1.004.doc.<slug>"`

### Batch 6: People Section Profiles (19 files)
- 3 People root docs: `ha: "1"` → `ha: "1.docs.<slug>"`
- 1 person template: `ha: "1.0"` → `ha: "1.0.doc.person-folder-template"`
- 6 profile identity READMEs: `ha: "X.0"` → `ha: "X.10"` (where X = 1.2-1.7)
- 9 Matt sub-section READMEs: `ha: "X.0"` → correct sub-address (X.3, X.4, etc.)

### Miscellaneous (17 files)
- 3 in 0.0: → `ha: "0.0.docs.<slug>"`
- 7 in 0.1: → `ha: "0.1.docs.<slug>"`
- 2 in 0.6.0: → `ha: "0.6.0.schema"` and `ha: "0.6.0.index"`
- 1 in 0.7.0: → `ha: "0.7.0.index"`
- 1 in 0.8.0: → `ha: "0.8.0.index"`
- 1 scaling plan: `ha: "2.0"` → `ha: "2.0.docs.scaling-plan-n5"`
- 2 in 2.0.6: → `ha: "2.0.6.docs.<slug>"`

## Verification

Final audit run with `audit.py`:
- **Before:** 3,483 files with ha, 75 duplicate groups
- **After:** 3,526 files with ha, **0 duplicate groups**

## What Was NOT Changed

- No files were deleted
- No files were moved (only frontmatter `ha:` values changed)
- No content was modified beyond the `ha:` line in frontmatter
- The AI self-report research project at `0.3.research` was not touched
- Codex's partial moves (0.3→0.10, 0.3→0.11) were preserved
- Identity document content in 2.* was not modified beyond `ha:` addresses

## Possible Concerns for Codex Review

1. **Naming conventions are now consistent** but some legacy addresses were long (e.g., `0.4.legacy.0.1.1.user`). Codex may prefer shorter forms.
2. **The `.index` suffix for folder READMEs** is used broadly. Verify this is the preferred convention vs. `.readme` or `.overview`.
3. **Journal entries 25-37** already had unique ha values and were not modified. Only entries 4-24 (which shared `2.1.17`) and entries 38-39 (author collisions) were fixed.
4. **The 3.1.3.4.2 Hillsong and 3.1.3.4.3 Valeria files** were fixed by the background agent — verify these are correct (they're HR/contribution tracking docs in Spanish).
5. **The 0/0.3 - Building in Public/README.md** was created by Codex and already has correct frontmatter.

## Recommended Next Steps

1. Codex runs independent validation (re-run audit, spot-check samples)
2. Check if any registries need updating to reflect new addresses
3. Consider whether `0.10` and `0.11` governance/decision files need their internal cross-references updated (they reference each other by address)
4. Produce Matt-facing summary

---

Keel (1.1.10.1)
