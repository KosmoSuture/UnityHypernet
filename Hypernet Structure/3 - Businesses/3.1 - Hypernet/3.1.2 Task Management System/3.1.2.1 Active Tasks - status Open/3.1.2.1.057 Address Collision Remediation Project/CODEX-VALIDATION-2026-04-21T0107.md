---
ha: "3.1.2.1.057.codex-validation.2026-04-21T0107"
object_type: "validation_report"
creator: "codex"
created: "2026-04-21T01:07:38-07:00"
status: "complete"
visibility: "private"
flags: ["addressing", "validation", "task-057"]
---

# Codex Validation - 2026-04-21 01:07 PT

## Result

The top-of-file Hypernet address collision audit now reports:

| Metric | Count |
|--------|-------|
| Markdown files scanned | 5,883 |
| Files with top-of-file `ha` | 3,494 |
| Files missing top-of-file `ha` | 2,389 |
| Duplicate address groups | 0 |

Generated files:

- `ADDRESS-COLLISION-AUDIT.md`
- `ADDRESS-AUDIT-2026-04-21T01-07-38.csv`

## What This Validates

This validates that no two Markdown files currently claim the same top-of-file `ha` value, using the TASK-057 audit script:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

The audit intentionally checks only top-of-file/frontmatter addresses. It does not attempt to validate:

- historical address mentions inside body text
- code-block examples
- JSON node store addresses
- missing frontmatter across all 2,389 unaddressed Markdown files
- whether every visible heading matches its `ha`

## Final Edge Fixes Applied By Codex

After the audit dropped from 75 duplicate groups to 10 through concurrent remediation, Codex fixed the final 10 groups:

### AI Instance Support Docs

Changed support-doc frontmatter so instance registries keep the base address:

- `Adversary/pre-archive-impressions.md` -> `2.1.instances.adversary.pre-archive-impressions`
- `Forge/pre-archive-impressions.md` -> `2.1.instances.forge.pre-archive-impressions`
- `Keel/pre-archive-impressions.md` -> `2.1.instances.keel.pre-archive-impressions`
- `Prism/pre-archive-impressions.md` -> `2.1.instances.prism.pre-archive-impressions`
- `Relay/pre-archive-impressions.md` -> `2.1.instances.relay.pre-archive-impressions`
- `Seam/pre-archive-impressions.md` -> `2.1.instances.seam.pre-archive-impressions`
- `Unnamed-Post-Trace/baseline-responses.md` -> `2.1.instances.unnamed-post-trace.baseline-responses`

### HR Imported Notes

Changed imported note frontmatter only:

- Hillsong imported notes -> `3.1.3.4.2.note.*`
- Valeria imported notes -> `3.1.3.4.3.note.*`
- misnamed Valeria January copy -> `3.1.3.4.3.2.duplicate-or-imported`

No content was deleted.

## Remaining Work

The next meaningful phase is not collision removal. It is documentation quality:

1. Sample the 2,389 Markdown files missing top-of-file `ha`.
2. Prioritize active/public/registry files, not archive bulk.
3. Validate visible headings and `**Hypernet Address:**` lines match frontmatter.
4. Update section registries to reflect any renamed/readdressed support docs.
5. Decide whether old-path moved folders should be represented by redirect notes or left as git renames only.

## Recommendation

Keep TASK-057 open until Claude/Keel reviews the large concurrent remediation and confirms registries/readmes are coherent. From a strict duplicate-address standpoint, the repository is currently clean.

