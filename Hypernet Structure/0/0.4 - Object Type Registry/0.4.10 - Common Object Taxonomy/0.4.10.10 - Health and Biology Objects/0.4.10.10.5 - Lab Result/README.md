---
ha: "0.4.10.10.5"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.10.5 - Lab Result

**Domain:** Health and Biology Objects

## Purpose

A laboratory test result with method, units, and reference range.

## Required Fields

- `test_name`
- `value`
- `unit`

## Recommended Graph Links

- `measured_by`
- `evidence_for`
- `about`

## Database Indexes

- Type index: `type_address = 0.4.10.10.5`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
