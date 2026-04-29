---
ha: "3.1.2.1.057.batch-1-reference-map"
object_type: "reference_map"
creator: "codex"
created: "2026-04-21"
status: "ready_for_claude"
visibility: "private"
flags: ["addressing", "batch-1", "0.3", "0.10", "0.11"]
---

# Batch 1 Reference Map - 0.3 / 0.10 / 0.11 Split

This file is a targeted map for Claude's first remediation batch.

## Canonical Decision

| Address | Current owner |
|---------|---------------|
| `0.3` | Building in Public |
| `0.3.research` | AI self-report research project |
| `0.10` | Control Data and Governance |
| `0.11` | Decisions and Architecture Records |

## Known Remaining References To Fix

### `0/README.md`

Current scan still finds:

- line 213: `0.3.0 Governance Overview`
- line 214: `0.3.1 Governance Bodies Details`
- line 215: `0.3.2 Voting Procedures`
- line 235: `Governance rules | 0.3 Control data`
- line 350: `Governance: Section 0.3 Control data`

Expected:

- governance docs should point to `0.10.0`, `0.10.1`, `0.10.2`, etc.
- governance quick-reference rows should point to `0.10 - Control Data and Governance`
- keep `0.3` references only when they mean Building in Public.

### `0/REGISTRY.md`

Current scan still finds:

- `## Control Data (0.3)`
- table rows `0.3.0` through `0.3.8`
- known issue `0.3.7 Trust Framework still in draft`

Expected:

- add/keep a top-level row for `0.3` Building in Public
- change Control Data heading and rows to `0.10`
- add a top-level row for `0.11` Decisions and Architecture Records
- remove obsolete `0.7* Task Queue` collision note if live tree shows Task Queue is now `0.9`
- add migration note: `0.3` governance moved to `0.10` on 2026-04-21

### `HYPERNET-STRUCTURE-GUIDE.md`

Current scan shows the guide is partly migrated:

- line 144: `0.3 - Building in Public`
- line 204: `0.3 - Building in Public`
- line 208: `0.10.0 Governance Overview.md (was 0.3.0)`

Expected:

- preserve historical `(was 0.3.x)` notes if helpful
- make sure the tree includes `0.10 - Control Data and Governance`
- make sure the tree includes `0.11 - Decisions and Architecture Records`
- make sure the category table says governance is `0.10`, not `0.3`

## 0.10 Folder Notes

Codex corrected accidental semantic replacements in:

- `0/0.10 - Control Data and Governance/REGISTRY.md`
- `0/0.10 - Control Data and Governance/README.md`

Specifically, reputation-score values such as `0.3 baseline`, `+0.1 to +0.3`, and `0.0-0.3` should remain numeric reputation scores, not become address `0.10`.

Remaining issue for Claude:

- filenames in the `0.10` folder still start with `0.3.x` even though frontmatter/headings are `0.10.x`.
- Rename these files if practical, preserving contents:
  - `0.3.0 Governance Overview.md` -> `0.10.0 Governance Overview.md`
  - through `0.3.8 Brain Dump Processing Pipeline.md` -> `0.10.8 Brain Dump Processing Pipeline.md`

## 0.11 Folder Notes

Known issues:

- `compliance-frameworks-research-2026-04-01.md` appears to lack top-of-file frontmatter.
- `governance-portability-analysis-2026-03-30.md` appears to lack top-of-file frontmatter.
- `hypernet-db-specification-2026-03-30.md` has `supersedes: "0.3.2026-03-19-graph-db-design"`; this is probably correct because it refers to a Building in Public design document that still lives under `0.3`.

Suggested addresses:

- `0.11.2026-04-01-compliance-frameworks-research`
- `0.11.2026-03-30-governance-portability-analysis`

## Batch 1 Done Criteria

Run:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

Batch 1 is ready for Codex review when:

- `0.3` duplicate groups are gone or intentionally limited to Building in Public README/registry patterns.
- `0.10` governance docs have coherent paths, frontmatter, headings, and registry rows.
- `0.11` decision docs have frontmatter.
- top-level `0` docs no longer tell readers governance is at canonical `0.3`.

