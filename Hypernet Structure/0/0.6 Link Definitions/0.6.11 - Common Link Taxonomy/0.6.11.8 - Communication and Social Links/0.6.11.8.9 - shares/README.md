---
ha: "0.6.11.8.9"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.8.9 - shares

**Domain:** Communication and Social Links

## Purpose

Actor shares or republishes object.

## Endpoint Constraints

- Source: `Actor`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `shared_by`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "shares"`
- `link_type = "0.6.11.8.9"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
