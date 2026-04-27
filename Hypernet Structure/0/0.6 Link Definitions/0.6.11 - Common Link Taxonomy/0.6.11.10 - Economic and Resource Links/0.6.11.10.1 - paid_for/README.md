---
ha: "0.6.11.10.1"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.10.1 - paid_for

**Domain:** Economic and Resource Links

## Purpose

Transaction paid for object.

## Endpoint Constraints

- Source: `Transaction`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `payment_of`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "paid_for"`
- `link_type = "0.6.11.10.1"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
