---
ha: "0.4.10.3.6"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.3.6 - Contact Point

**Domain:** Communication and Social Objects

## Purpose

An addressable contact method such as email, phone, handle, or URL.

## Required Fields

- `value`
- `kind`
- `owner`

## Recommended Graph Links

- `belongs_to`
- `verified_by`
- `expires_at`

## Database Indexes

- Type index: `type_address = 0.4.10.3.6`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
