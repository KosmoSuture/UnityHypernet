---
ha: "0.6.11.6.4"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.6.4 - route_from

**Domain:** Spatial and Movement Links

## Purpose

Route starts at a location.

## Endpoint Constraints

- Source: `Route`
- Target: `Location`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `route_origin_for`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "route_from"`
- `link_type = "0.6.11.6.4"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
