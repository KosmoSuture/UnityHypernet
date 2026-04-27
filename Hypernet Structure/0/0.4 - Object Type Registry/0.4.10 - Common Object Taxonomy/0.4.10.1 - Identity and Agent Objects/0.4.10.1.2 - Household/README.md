---
ha: "0.4.10.1.2"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.1.2 - Household

**Domain:** Identity and Agent Objects

## Purpose

A living or family unit containing people, places, assets, and responsibilities.

## Required Fields

- `name`
- `members`
- `primary_location`

## Recommended Graph Links

- `contains`
- `guardian_of`
- `located_at`

## Database Indexes

- Type index: `type_address = 0.4.10.1.2`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
