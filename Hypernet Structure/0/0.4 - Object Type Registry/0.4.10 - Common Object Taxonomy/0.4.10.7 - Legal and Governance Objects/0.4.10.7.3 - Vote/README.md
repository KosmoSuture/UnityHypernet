---
ha: "0.4.10.7.3"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.7.3 - Vote

**Domain:** Legal and Governance Objects

## Purpose

A governance choice by an eligible voter.

## Required Fields

- `voter`
- `proposal`
- `choice`

## Recommended Graph Links

- `voted_on`
- `cast_by`
- `during`

## Database Indexes

- Type index: `type_address = 0.4.10.7.3`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
