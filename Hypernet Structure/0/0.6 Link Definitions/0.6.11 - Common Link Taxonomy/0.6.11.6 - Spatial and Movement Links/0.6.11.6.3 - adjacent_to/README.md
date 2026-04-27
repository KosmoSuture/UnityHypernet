---
ha: "0.6.11.6.3"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.6.3 - adjacent_to

**Domain:** Spatial and Movement Links

## Purpose

Locations touch or neighbor.

## Endpoint Constraints

- Source: `Location`
- Target: `Location`

## Properties

- Directed: `false`
- Symmetric: `true`
- Transitive: `false`
- Inverse: `none`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "adjacent_to"`
- `link_type = "0.6.11.6.3"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
