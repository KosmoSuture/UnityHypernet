---
ha: "0.6.11.3.2"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.3.2 - part_of

**Domain:** Containment and Hierarchy Links

## Purpose

An object is a component of a whole.

## Endpoint Constraints

- Source: `Object`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `true`
- Inverse: `has_part`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "part_of"`
- `link_type = "0.6.11.3.2"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
