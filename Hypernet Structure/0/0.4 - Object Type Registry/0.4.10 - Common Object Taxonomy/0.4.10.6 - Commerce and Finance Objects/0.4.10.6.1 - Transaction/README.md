---
ha: "0.4.10.6.1"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.6.1 - Transaction

**Domain:** Commerce and Finance Objects

## Purpose

A movement of money, value, asset, or obligation.

## Required Fields

- `amount`
- `currency`
- `parties`

## Recommended Graph Links

- `paid_for`
- `billed_to`
- `credits`

## Database Indexes

- Type index: `type_address = 0.4.10.6.1`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
