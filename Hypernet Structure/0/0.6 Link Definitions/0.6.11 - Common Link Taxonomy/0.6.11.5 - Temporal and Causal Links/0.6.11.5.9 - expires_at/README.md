---
ha: "0.6.11.5.9"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.5.9 - expires_at

**Domain:** Temporal and Causal Links

## Purpose

Source validity ends at target time.

## Endpoint Constraints

- Source: `Object`
- Target: `Time Span`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `expiration_of`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "expires_at"`
- `link_type = "0.6.11.5.9"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
