---
ha: "0.4.10.7.5"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.7.5 - Consent Grant

**Domain:** Legal and Governance Objects

## Purpose

A consent record for a relationship, data use, or operation.

## Required Fields

- `grantor`
- `grantee`
- `scope`

## Recommended Graph Links

- `consented_by`
- `permission_grants`
- `expires_at`

## Database Indexes

- Type index: `type_address = 0.4.10.7.5`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
