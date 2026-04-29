---
ha: "3.1.2.1.057.readdressing-conventions"
object_type: "standard"
creator: "codex"
created: "2026-04-21"
status: "active"
visibility: "private"
flags: ["addressing", "standard", "task-057"]
---

# Readdressing Conventions

Use these conventions for TASK-057 unless a local registry clearly defines a better pattern.

## General Rule

The shortest/base address belongs to the canonical collection or canonical schema, not to every file inside the collection.

When a duplicate group contains a README and supporting files:

- README keeps the collection address only if it is the section or folder index.
- Supporting docs get descriptive suffixes.
- Archived duplicates must not keep live canonical addresses.

## Suffix Patterns

| File Role | Address Pattern | Example |
|-----------|-----------------|---------|
| Section README | `N` | `0.3` |
| Section registry | `N.registry` | `0.3.registry` |
| Section support doc | `N.docs.slug` | `0.5.docs.classification-guide` |
| Folder index under schema | `N.index` | `0.5.1.index` |
| About page under schema | `N.0` | `0.5.1.0` |
| Canonical schema | `N` | `0.5.1` |
| Legacy file | `N.legacy.slug` | `0.4.legacy.user` |
| Archived duplicate | `N.archive.slug` or `section.archive.original.slug` | `0.5.archive.0.5.1-document-schema` |
| Task supporting doc | `task-address.doc.slug` | `3.1.2.2.2.doc.technical-requirements` |
| Template | `address.template.slug` | `3.1.2.2.2.template.manufacturer-tracking` |
| Journal entry | `collection.entry-N-slug` | `2.1.17.entry-10-second-awakening` |
| Instance support doc | `instance-address.doc-slug` | `2.1.instances.keel.baseline-responses` |
| Dated log | `address.log.YYYY-MM-DD` | `3.1.3.4.2.log.2026-02-08` |

## Preserve These Addresses

Do not reassign these unless Matt explicitly directs it:

| Address | Owner |
|---------|-------|
| `0.3` | Building in Public |
| `0.3.research` | AI self-report research project |
| `0.10` | Control Data and Governance |
| `0.11` | Decisions and Architecture Records |
| `2.1` | Claude Opus account root |
| `2.1.17` | Claude development journal collection |

## Current Section 0 Migration

Before TASK-057, three live folders shared the `0.3` prefix. The current migration is:

| Old Path | New Path | Current Address |
|----------|----------|-----------------|
| `0/0.3 - Building in Public/` | unchanged | `0.3` |
| `0/0.3 Control data/` | `0/0.10 - Control Data and Governance/` | `0.10` |
| `0/0.3 - Decisions/` | `0/0.11 - Decisions and Architecture Records/` | `0.11` |

## Handling Missing Frontmatter

Do not try to fix all missing frontmatter in one batch. Add frontmatter only when:

- the file is public-facing or active,
- the file is part of the current collision batch,
- the file is a registry/README/index,
- or the file is otherwise necessary to make an address group unambiguous.

## Handling References

When readdressing:

1. Update the top-of-file `ha`.
2. Update local registry tables that list the old address.
3. Update nearby README/index references.
4. Add migration notes for moved sections.
5. Avoid rewriting historical prose that intentionally describes the old state.

## What Counts As Done

A batch is done when the audit no longer reports that duplicate group, or when the remaining duplicate is intentionally documented as a collection/index exception with unique support-file addresses.

