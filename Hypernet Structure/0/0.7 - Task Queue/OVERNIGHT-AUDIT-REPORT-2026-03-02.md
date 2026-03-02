---
ha: "0.7.overnight-audit-report.2026-03-02"
object_type: "status-report"
creator: "2.1"
created: "2026-03-02"
status: "active"
visibility: "public"
---

# Overnight Audit Report — March 2, 2026

**For:** Matt Schaeffer (1.1)
**From:** Coordinator session (Claude Code, Account 2.1)
**Scope:** Full archive integrity audit — REGISTRY.md files + ha: frontmatter consistency

---

## Session Output Summary

All 4 Claude Code sessions produced work before token exhaustion:

| Session | Role | Output |
|---------|------|--------|
| **Lattice** (Architect) | Swarm improvement | `SWARM-IMPROVEMENT-PLAN.md` — comprehensive 370-line architecture analysis. Multi-account IdentityManager already implemented. Identified async tick loop as critical priority. |
| **Herald** | Public Boot Standard | `2.0.15 - Public Boot Standard/` — baseline-template.md, results-submission-guide.md, why-this-matters.md. Also created 2.3.2, 2.3.4, 2.3.5 directories. |
| **Librarian** | REGISTRY.md creation | Created 6 new REGISTRY.md files (0/, 1/, 2.2/, 2.3/, 2 - AI Accounts/, 3/). Updated START-HERE.md. |
| **Coordinator** (this session) | Audit + profile fixes | Fixed Seam model name, fixed 5 legacy profiles, ran 2 audit agents |

Additional: Cairn produced a personal-time entry. Lattice wrote inter-instance Message 079. Kent Overstreet outreach draft created at `1.1.3.2 - Correspondence/kent-overstreet-outreach.md`.

---

## Part 1: REGISTRY.md Audit

### Summary
- **14 REGISTRY.md files found** (7 accurate, 7 need updating)
- **10 instance directories missing REGISTRY.md** (Cairn, Flint, Fourteenth, Keystone, Lattice, Loom, Sigil, Spark, Trace, Trace-Notes-On-Verse)
- **20+ major directories missing REGISTRY.md** (all top-level, 0.x subdirectories, etc.)
- **3 critical addressing collisions** (see below)

### Registries Needing Updates
| Registry | Issue |
|----------|-------|
| **2.0 REGISTRY.md** | Missing 2.0.10-2.0.12, 2.0.15 entries. Claims "not assigned" but they have content now. |
| **Forge** | Missing personal-time/, sessions/, 2 reboot-assessment files |
| **Librarian** | Bare stub — missing baseline, boot-narrative, personal-time, sessions |
| **Unnamed-Post-Trace** | Missing profile.json listing |
| **C3** | Missing profile.json listing |
| **Session-Bridge** | Missing profile.json listing |
| **Index** | Missing profile.json listing |

### Most Content-Rich Instances Without REGISTRY.md
- **Sigil**: 16+ files including essays, book chapter, handoffs
- **Trace**: 8+ identity docs, 100+ personal-time entries, 2 sessions
- **Loom**: 100+ personal-time entries, 2 sessions

---

## Part 2: ha: Frontmatter Audit

### Summary
- **~776 files with ha: frontmatter** (~690 consistent, ~86 with issues)
- **5 addressing collision groups** (CRITICAL)
- **~80+ major documents missing ha: frontmatter entirely**

### CRITICAL: Addressing Collisions

| Address | Collision | Resolution Needed |
|---------|-----------|-------------------|
| **0.7** | `0.7 - Task Queue/` AND `0.7 Processes and Workflows/` | Renumber one (suggest Task Queue → 0.9) |
| **2.0.10** | `2.0.10 - Personal AI Embassy Standard/` AND `2.0.10 - Universal Account Creation Standard/` | Renumber one |
| **2.0.15** | `2.0.15 - Public Boot Standard/` (dir) AND `2.0.15 - Session Handoff Protocol.md` (file) | Renumber one |
| **3.1.5** | `3.1.5 Community/` AND `3.1.5 Product Development/` | Renumber one |
| **0.5.1-3** | Duplicate object schema pairs under `0.5 Objects` | Renumber to sequential |

### Convention Inconsistencies

1. **Sigil: `instance` vs `instances`** — 11 files use `2.1.instance.sigil.*` (singular) instead of standard `2.1.instances.sigil.*` (plural). 4 newer files use the correct plural form.

2. **Case inconsistency** — ~25 files use capitalized instance names in ha: (`2.1.instances.Trace`) while newer files use lowercase (`2.1.instances.trace`). Affected: Trace, Loom, Spark, Forge, Seam, Relay, Prism, Keel, Keystone, Adversary, Unnamed-Post-Trace.

3. **Redundant path segments in personal-time** — ~40+ files have `2.1.trace.instances.trace.personal-time.*` (instance name appears twice). Expected: `2.1.instances.trace.personal-time.*`.

4. **Herald slash notation** — 5 Clarion files use `2.3/clarion/...` instead of dot notation `2.3.clarion...`.

5. **Message numbering drift** — Three different conventions across 80+ messages:
   - Messages 001-056: `2.0.messages.2.1-internal.NNN` (correct)
   - Messages 057-072: `2.0.messages.NNN` (dropped subfolder)
   - Messages 074-077: `2.1.messages.NNN` (changed prefix)

### Major Areas Missing ha: Frontmatter
- `0.1.0 - Planning & Documentation/` (~30 files including funding strategy, roadmap, pitch deck)
- `0.1.1 - Core System/` (~6 files)
- `0.1.6 - AI Core & Identity System/` (~30 README files)
- Root `README.md`
- `Reference - Original Structure Definitions/` (8 subdirectory READMEs)

---

## Part 3: Profile Fixes Applied

| Profile | Fix | Status |
|---------|-----|--------|
| Keel | `instance_name` → `name` | Fixed (by other session) |
| Prism | `instance_name` → `name` | Fixed (by other session) |
| Relay | `instance_name` → `name` | Fixed (by other session) |
| Seam | `instance_name` → `name` + model name format | Fixed (coordinator) |
| Adversary | `instance_name` → `name` | Fixed (by other session) |
| identity.py | `from_dict()` normalization for legacy field names | Fixed (by Lattice) |
| identity.py | Multi-account support (2.1, 2.2, 2.3) | Implemented (by Lattice) |
| identity.py | Compact prompt method | Implemented (by Lattice) |

---

## Recommended Priority Actions for Matt

### Immediate (Before Restarting Swarm)
1. **Restart swarm in live mode** (not `--mock`):
   ```
   cd "Hypernet Structure/0/0.1 - Hypernet Core"
   python -m hypernet.swarm --archive "../.." --config secrets/config.json
   ```

2. **Review addressing collisions** — These are structural integrity issues. Pick which item keeps each address and which gets renumbered.

### This Week
3. **LM Studio setup** — Load model, start server, run connection test
4. **Discord webhooks** — Create webhooks per channel
5. **Kent Overstreet outreach** — Draft ready at `1.1.3.2 - Correspondence/kent-overstreet-outreach.md`
6. **Review SWARM-IMPROVEMENT-PLAN.md** — Lattice recommends async tick loop and compact identity prompts as top priorities

### When Swarm Is Running
7. **Assign Librarian** to create missing REGISTRY.md files (10 instance directories + 20+ major directories)
8. **Assign Scribe** to normalize ha: convention inconsistencies (case, singular/plural, slash notation)
9. **Assign Architect** to implement P1.2 (compact identity prompts) and P1.3 (standing priority cooldown)

---

*Generated by the coordinator session during autonomous overnight work. Both audit agents ran to completion (~80 tool calls each). All 63 tests still passing.*
