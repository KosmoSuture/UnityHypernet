---
ha: "0.4.10.10.8"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.10.8 - Care Plan

**Domain:** Health and Biology Objects

## Purpose

A treatment or wellness plan with goals and interventions.

## Required Fields

- `subject`
- `goals`
- `owner`

## Recommended Graph Links

- `contains`
- `approved_by`
- `scheduled_for`

## Database Indexes

- Type index: `type_address = 0.4.10.10.8`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
