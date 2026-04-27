---
ha: "0.4.10.10.2"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.10.2 - Health Profile

**Domain:** Health and Biology Objects

## Purpose

A consent-scoped person health profile.

## Required Fields

- `person`
- `scope`
- `privacy_level`

## Recommended Graph Links

- `owned_by`
- `consented_by`
- `governed_by`

## Database Indexes

- Type index: `type_address = 0.4.10.10.2`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
