---
ha: "3.1.2.1.057.batch-2-reference-map"
object_type: "reference_map"
creator: "codex"
created: "2026-04-21"
status: "ready_for_claude"
visibility: "private"
flags: ["addressing", "batch-2", "0.5", "master-objects"]
---

# Batch 2 Reference Map - Section 0.5 Master Objects

This file maps the current `0.5` duplicate classes and gives Claude a safe remediation plan.

## Existing Registry Intent

`0/0.5 Objects - Master Objects/REGISTRY.md` already identifies canonical schemas:

| Address | Canonical owner |
|---------|-----------------|
| `0.5.0` | Master Object Schema |
| `0.5.1` | Person Object Schema |
| `0.5.2` | Organization Object Schema |
| `0.5.3` | Document Object Schema |
| `0.5.4` | Media Object Schema |
| `0.5.5` | Device Object Schema |
| `0.5.6` | Location Object Schema |
| `0.5.7` | Event Object Schema |
| `0.5.8` | Concept Object Schema |
| `0.5.9` | Task Object Schema |
| `0.5.10` | Source Code Type |
| `0.5.11` | Financial Object Schema |
| `0.5.12` | Biological Object Schema |
| `0.5.13` | Legal Object Schema |
| `0.5.14` | Communication Object Schema |
| `0.5.15` | Creative Work Object Schema |
| `0.5.16` | Measurement Object Schema |

Therefore, schema files should keep those addresses. Folder READMEs and support docs need suffixes.

## Duplicate Class: Bare `0.5`

Current files claiming `0.5`:

- `README.md`
- `CLASSIFICATION-DECISION-TREE.md`
- `CLASSIFICATION-GUIDE.md`
- `COLLECTION-PATTERN.md`
- `DUPLICATE-RESOLUTION.md`
- `SCHEMA-ALIGNMENT-NOTE.md`
- `TAXONOMY-DESIGN-RATIONALE.md`
- `TAXONOMY-PROPOSAL.md`

Recommended:

| File | New Address |
|------|-------------|
| `README.md` | `0.5` |
| `CLASSIFICATION-DECISION-TREE.md` | `0.5.docs.classification-decision-tree` |
| `CLASSIFICATION-GUIDE.md` | `0.5.docs.classification-guide` |
| `COLLECTION-PATTERN.md` | `0.5.docs.collection-pattern` |
| `DUPLICATE-RESOLUTION.md` | `0.5.docs.duplicate-resolution` |
| `SCHEMA-ALIGNMENT-NOTE.md` | `0.5.docs.schema-alignment-note` |
| `TAXONOMY-DESIGN-RATIONALE.md` | `0.5.docs.taxonomy-design-rationale` |
| `TAXONOMY-PROPOSAL.md` | `0.5.docs.taxonomy-proposal` |

## Duplicate Class: Schema File vs Folder README

For each duplicate pair:

- schema file keeps the canonical `0.5.N`
- folder README becomes `0.5.N.index`

Examples:

| File | New Address |
|------|-------------|
| `0.5.1 Person Object Schema.md` | `0.5.1` |
| `0.5.1 - Person/README.md` | `0.5.1.index` |
| `0.5.4 Media Object Schema.md` | `0.5.4` |
| `0.5.4 - Media/README.md` | `0.5.4.index` |
| `0.5.3.1 Markdown Document Type.md` | `0.5.3.1` |
| `0.5.3 - Document/0.5.3.1 - Markdown Document/README.md` | `0.5.3.1.index` |

Apply this pattern across all duplicate schema/README pairs reported by the audit.

## Duplicate Class: Archived Duplicates

The old `DUPLICATE-RESOLUTION.md` says the duplicates were resolved by moving files into `archived-duplicates/`, but those archived files still claim live canonical addresses.

Current archived collisions:

| Archived file | Current `ha` | New Address |
|---------------|--------------|-------------|
| `archived-duplicates/0.5.1 Document Object Schema.md` | `0.5.1` | `0.5.archive.0.5.1-document-object-schema` |
| `archived-duplicates/0.5.2 Person Object Schema.md` | `0.5.2` | `0.5.archive.0.5.2-person-object-schema` |
| `archived-duplicates/0.5.3 Device Object Schema.md` | `0.5.3` | `0.5.archive.0.5.3-device-object-schema` |

## Registry Update

After readdressing, update `REGISTRY.md`:

- Supporting Documentation table should include support doc addresses.
- Known Issues should say the content collision was resolved on 2026-03-02, but TASK-057 later fixed archived frontmatter so archived duplicates no longer claim canonical addresses.

## Batch 2 Done Criteria

Run:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

Batch 2 is ready for Codex review when:

- no duplicate groups remain under `0/0.5 Objects - Master Objects/`, except any deliberately documented exception.
- archived duplicate files do not claim canonical schema addresses.
- support docs have unique `0.5.docs.*` addresses.
- folder README/index files have unique `.index` addresses.

