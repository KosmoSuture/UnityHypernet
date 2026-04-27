---
ha: "0.6.11.9.8"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.9.8 - resolves

**Domain:** Governance and Trust Links

## Purpose

Decision resolves dispute.

## Endpoint Constraints

- Source: `Decision`
- Target: `Dispute`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `resolved_by`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "resolves"`
- `link_type = "0.6.11.9.8"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
