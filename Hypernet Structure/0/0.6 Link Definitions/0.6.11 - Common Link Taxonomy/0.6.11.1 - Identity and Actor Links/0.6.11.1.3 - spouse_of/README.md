---
ha: "0.6.11.1.3"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.1.3 - spouse_of

**Domain:** Identity and Actor Links

## Purpose

A spouse or marriage relationship.

## Endpoint Constraints

- Source: `Person`
- Target: `Person`

## Properties

- Directed: `false`
- Symmetric: `true`
- Transitive: `false`
- Inverse: `none`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "spouse_of"`
- `link_type = "0.6.11.1.3"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
