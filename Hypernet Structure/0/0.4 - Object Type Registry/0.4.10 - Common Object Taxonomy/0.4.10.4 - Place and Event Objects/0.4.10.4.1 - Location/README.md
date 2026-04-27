---
ha: "0.4.10.4.1"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.4.1 - Location

**Domain:** Place and Event Objects

## Purpose

A named geographic or logical place.

## Required Fields

- `name`
- `coordinates_or_path`
- `location_type`

## Recommended Graph Links

- `located_at`
- `within_radius_of`
- `contained_in`

## Database Indexes

- Type index: `type_address = 0.4.10.4.1`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
