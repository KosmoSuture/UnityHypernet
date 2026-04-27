---
ha: "0.6.11.7.2"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.7.2 - depends_on

**Domain:** Work and Dependency Links

## Purpose

Source depends on target.

## Endpoint Constraints

- Source: `Object`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `true`
- Inverse: `dependency_of`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "depends_on"`
- `link_type = "0.6.11.7.2"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
