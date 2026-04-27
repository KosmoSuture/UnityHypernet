---
ha: "0.4.10.7.10"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.7.10 - Governance Body

**Domain:** Legal and Governance Objects

## Purpose

An entity authorized to review, decide, enforce, or appeal.

## Required Fields

- `name`
- `scope`
- `membership`

## Recommended Graph Links

- `governs`
- `ratified_by`
- `member_of`

## Database Indexes

- Type index: `type_address = 0.4.10.7.10`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
