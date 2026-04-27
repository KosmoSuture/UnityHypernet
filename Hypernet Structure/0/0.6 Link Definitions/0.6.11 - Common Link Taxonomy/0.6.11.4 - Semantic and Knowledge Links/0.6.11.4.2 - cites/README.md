---
ha: "0.6.11.4.2"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.4.2 - cites

**Domain:** Semantic and Knowledge Links

## Purpose

Formal or informal citation.

## Endpoint Constraints

- Source: `Content`
- Target: `Content`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `cited_by`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "cites"`
- `link_type = "0.6.11.4.2"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
