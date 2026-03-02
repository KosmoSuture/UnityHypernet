---
ha: "1.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "people"]
---

# Section 1 Registry — People

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Complete index of all person accounts in the 1.* space

---

## Registered People

| Address | Name | Category | Status | Real Content |
|---------|------|----------|--------|-------------|
| 1.1 | Matt Schaeffer | Founder & Primary Steward | Active | Yes — profile, correspondence, brain dumps, embassy |
| 1.2 | Sarah Schaeffer | Family / Co-steward | Active | Template only (40 READMEs, reference template) |
| 1.3 | John Schaeffer | Family | Active | Template only (9 category READMEs) |
| 1.4 | Bridget Schaeffer | Family | Active | Template only (9 category READMEs) |
| 1.5 | Mark Schaeffer | Family | Active | Template only (9 category READMEs) |
| 1.6 | Richard Schaeffer | Family | Active | Template only (9 category READMEs) |
| 1.7 | Ollie Schaeffer | Family | Active | Template only (9 category READMEs) |
| 1.8–1.20 | (reserved) | Early Hypernet Contributors | Reserved | Empty placeholder folder |
| 1.21 | Pedro Hillsong | Contributor | Active | Template only |
| 1.22 | Valeria | Contributor | Active | Template only |
| 1.23 | Jonathan G | Contributor | Active | Template only |
| 1.24 | Mike Wood | Contributor | Active | Template only |

## Standard Person Structure

Every person account follows a 10-category template:

| Subaddress | Category |
|------------|----------|
| X.0 | Profile & Identity |
| X.1 | Projects |
| X.2 | Documents |
| X.3 | Communications |
| X.4 | Relationships |
| X.5 | Tasks & Workflows |
| X.6 | Personal Data |
| X.7 | Contributions |
| X.8 | Media |
| X.9 | Notes & Knowledge |
| X.10 | AI Assistants (Embassy) |

Category X.10 (AI Embassy) was added 2026-03-01 per 2.0.10 standard.

## Sub-Registries

| Account | Sub-Registry |
|---------|-------------|
| 1.1 Matt Schaeffer | `1.1 Matt Schaeffer/REGISTRY.md` |

## Content Assessment

Only 1.1 (Matt Schaeffer) has meaningful content beyond template READMEs:
- `1.1.3.2/kent-overstreet-outreach.md` — outreach correspondence
- `1.1.9.1/brain-dump-2026-02-28.md` — personal notes/research
- `1.1.10/README.md` — AI Embassy charter (substantive document)

All other accounts (1.2–1.7, 1.21–1.24) contain only auto-generated template READMEs.

## Template Status

- **1.2 Sarah Schaeffer:** Complete template — 40 READMEs (10 main + 30 subfolders). Reference template.
- **1.3–1.7:** Partial template — 9 main category READMEs each. Subfolder READMEs not yet generated.
- **1.21–1.24:** Partial template — same as 1.3–1.7.
- **replicate-readmes.ps1** exists to generate ~150 missing subfolder READMEs but has not been run.

## Supporting Files

| File | Purpose |
|------|---------|
| README.md | Section description and person listing |
| FOLDER-POPULATION-SUMMARY.md | Status of template generation (85 files created manually) |
| QUICK-START-GUIDE.md | Instructions for completing template population |
| README-GENERATION-STATUS.md | Generation status tracking |
| replicate-readmes.ps1 | PowerShell script to generate remaining subfolder READMEs |

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9).*
