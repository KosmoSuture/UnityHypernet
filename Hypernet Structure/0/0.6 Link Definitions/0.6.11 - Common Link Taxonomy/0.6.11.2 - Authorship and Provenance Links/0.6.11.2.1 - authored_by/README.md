---
ha: "0.6.11.2.1"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.2.1 - authored_by

**Domain:** Authorship and Provenance Links

## Purpose

Authorship attribution.

## Endpoint Constraints

- Source: `Content`
- Target: `Actor`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `authored`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "authored_by"`
- `link_type = "0.6.11.2.1"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
