---
ha: "0.4.10.1.8"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.1.8 - Persona

**Domain:** Identity and Agent Objects

## Purpose

A public or contextual presentation of an actor.

## Required Fields

- `name`
- `represented_actor`
- `context`

## Recommended Graph Links

- `persona_of`
- `acts_as`
- `visible_from`

## Database Indexes

- Type index: `type_address = 0.4.10.1.8`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
