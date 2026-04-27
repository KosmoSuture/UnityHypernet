---
ha: "0.4.10.4.5"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.4.5 - Route

**Domain:** Place and Event Objects

## Purpose

A path between places with ordered waypoints.

## Required Fields

- `origin`
- `destination`
- `waypoints`

## Recommended Graph Links

- `route_from`
- `route_to`
- `contains`

## Database Indexes

- Type index: `type_address = 0.4.10.4.5`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
