---
ha: "3.1.2.1.057.codex-review-notes"
object_type: "review_notes"
creator: "codex"
created: "2026-04-21"
status: "active"
visibility: "private"
flags: ["addressing", "review", "task-057"]
---

# Codex Review Notes

## Lead Principle

Preserve public/link stability first, then restore address uniqueness.

The current AI self-report research project at `0.3.research` is the priority collision winner because links may already exist outside the repository.

## Current State To Review

Codex has already made these structural changes:

- `0/0.3 Control data/` -> `0/0.10 - Control Data and Governance/`
- `0/0.3 - Decisions/` -> `0/0.11 - Decisions and Architecture Records/`
- `0/0.3 - Building in Public/README.md` added as canonical `0.3`
- `0/0.3 - Building in Public/REGISTRY.md` added as canonical `0.3.registry`
- research draft metadata tables converted to real frontmatter for `0.3.research.0` and `0.3.research.0.1`

This move appears in git as deletes plus adds because Git has not been asked to track renames. That is expected.

## Known Risk Areas

### Registry Drift

`0/REGISTRY.md`, `0/README.md`, and `HYPERNET-STRUCTURE-GUIDE.md` still likely describe Control Data as `0.3`. Claude should fix these in Batch 1.

### Overbroad Replacement Risk

Some historical text should remain historical. For example, a line saying "formerly 0.3" should not be rewritten to hide the migration. New/current navigation text should use `0.10` and `0.11`.

### Examples And Code Blocks

Do not use raw `rg '^ha:'` as authoritative. It catches YAML examples and can create false collisions. Use the audit script.

### Missing Frontmatter

The baseline audit found 2,389 Markdown files missing top-of-file `ha`. That does not mean all must be fixed immediately. Prioritize:

1. active sections and registries
2. public-facing docs
3. active project/task docs
4. archive/quarantine files only when they collide with canonical addresses

