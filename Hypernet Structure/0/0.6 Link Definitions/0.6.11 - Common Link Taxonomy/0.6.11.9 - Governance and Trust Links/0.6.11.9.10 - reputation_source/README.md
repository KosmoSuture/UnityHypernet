---
ha: "0.6.11.9.10"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.9.10 - reputation_source

**Domain:** Governance and Trust Links

## Purpose

Object contributes to actor reputation.

## Endpoint Constraints

- Source: `Object`
- Target: `Actor`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `has_reputation_source`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "reputation_source"`
- `link_type = "0.6.11.9.10"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
