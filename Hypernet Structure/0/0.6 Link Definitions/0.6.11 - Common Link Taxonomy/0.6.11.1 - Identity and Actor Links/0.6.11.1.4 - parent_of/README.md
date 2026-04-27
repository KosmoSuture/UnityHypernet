---
ha: "0.6.11.1.4"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.1.4 - parent_of

**Domain:** Identity and Actor Links

## Purpose

A parent-child relationship.

## Endpoint Constraints

- Source: `Person`
- Target: `Person`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `true`
- Inverse: `child_of`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "parent_of"`
- `link_type = "0.6.11.1.4"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
