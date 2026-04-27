---
ha: "0.4.10.8.9"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.8.9 - Citation

**Domain:** Science and Knowledge Objects

## Purpose

A structured reference to a source.

## Required Fields

- `source`
- `locator`
- `style`

## Recommended Graph Links

- `cites`
- `references`
- `evidence_for`

## Database Indexes

- Type index: `type_address = 0.4.10.8.9`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
