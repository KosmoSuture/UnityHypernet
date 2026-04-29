---
ha: "3.1.2.1.057.batch-6-reference-map"
object_type: "reference_map"
creator: "codex"
created: "2026-04-21"
status: "ready_for_claude"
visibility: "private"
flags: ["addressing", "batch-6", "people"]
---

# Batch 6 Reference Map - People Section Profile Metadata

This batch covers duplicate or inconsistent addresses in `1 - People`.

## Important Live-State Note

The baseline audit may be stale for some People files. For example, `1.2 Sarah Schaeffer/1.2.10 - Profile & Identity/README.md` currently has `ha: "1.2.10"`, but its heading/body still says `1.2.0`.

Before editing Batch 6, re-run:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

Then fix both duplicate addresses and stale in-document labels.

## Section Root Support Docs

Baseline duplicate:

- `1 - People/README.md`
- `1 - People/README-GENERATION-STATUS.md`
- `1 - People/QUICK-START-GUIDE.md`
- `1 - People/FOLDER-POPULATION-SUMMARY.md`

Recommended:

| File | New Address |
|------|-------------|
| `README.md` | `1` |
| `README-GENERATION-STATUS.md` | `1.docs.readme-generation-status` |
| `QUICK-START-GUIDE.md` | `1.docs.quick-start-guide` |
| `FOLDER-POPULATION-SUMMARY.md` | `1.docs.folder-population-summary` |

## People Profile vs Account Metadata

Baseline duplicate pattern:

- `1.x.0 - Account Metadata/README.md`
- `1.x.10 - Profile & Identity/README.md`

Recommended:

| Folder | Correct Address |
|--------|-----------------|
| `1.x.0 - Account Metadata/README.md` | `1.x.0` |
| `1.x.10 - Profile & Identity/README.md` | `1.x.10` |

Apply for:

- `1.2 Sarah Schaeffer`
- `1.3 John Schaeffer`
- `1.4 Bridget Schaeffer`
- `1.5 Mark Schaeffer`
- `1.6 Richard Schaeffer`
- `1.7 Ollie Schaeffer`

Also update headings and `**Hypernet Address:**` lines inside profile READMEs if they still say `1.x.0`.

## Matt Section Metadata Collisions

Baseline duplicate pattern:

- section metadata README has `1.1.N.0`
- a child folder README also incorrectly has `1.1.N.0`

Examples:

| Duplicate address | Correct owner | Suspect child folder |
|-------------------|---------------|----------------------|
| `1.1.1.0` | `1.1.1 - Projects/1.1.1.0 - Section Metadata/README.md` | `1.1.1.3 - Active Projects/README.md` should be `1.1.1.3` |
| `1.1.2.0` | Section Metadata | `1.1.2.4 - Personal Documents/README.md` should be `1.1.2.4` |
| `1.1.3.0` | Section Metadata | `1.1.3.3 - Email Archives/README.md` should be `1.1.3.3` |
| `1.1.4.0` | Section Metadata | `1.1.4.3 - Professional Network/README.md` should be `1.1.4.3` |
| `1.1.5.0` | Section Metadata | `1.1.5.3 - Active Tasks/README.md` should be `1.1.5.3` |
| `1.1.6.0` | Section Metadata | `1.1.6.3 - Hypernet Data Store/README.md` should be `1.1.6.3` |
| `1.1.7.0` | Section Metadata | `1.1.7.4 - Code Contributions/README.md` should be `1.1.7.4` |
| `1.1.8.0` | Section Metadata | `1.1.8.3 - Photos/README.md` should be `1.1.8.3` |
| `1.1.9.0` | Section Metadata | `1.1.9.3 - Personal Notes/README.md` should be `1.1.9.3` |

## People Definitions

Baseline duplicate:

- `1.0 People definitions/README.md`
- `1.0 People definitions/PERSON-FOLDER-TEMPLATE.md`

Recommended:

| File | New Address |
|------|-------------|
| `README.md` | `1.0` |
| `PERSON-FOLDER-TEMPLATE.md` | `1.0.template.person-folder` |

## Batch 6 Done Criteria

Run the audit after edits. Batch 6 is ready for Codex review when:

- People root support docs have unique `1.docs.*` addresses.
- profile identity READMEs use `1.x.10`, not `1.x.0`.
- Matt child section READMEs use their actual child folder address.
- headings and visible `Hypernet Address` lines match frontmatter.

