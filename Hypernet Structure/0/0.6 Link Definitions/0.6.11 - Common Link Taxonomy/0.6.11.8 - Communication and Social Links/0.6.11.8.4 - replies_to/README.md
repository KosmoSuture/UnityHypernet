---
ha: "0.6.11.8.4"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.8.4 - replies_to

**Domain:** Communication and Social Links

## Purpose

Message replies to another message.

## Endpoint Constraints

- Source: `Message`
- Target: `Message`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `true`
- Inverse: `has_reply`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "replies_to"`
- `link_type = "0.6.11.8.4"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
