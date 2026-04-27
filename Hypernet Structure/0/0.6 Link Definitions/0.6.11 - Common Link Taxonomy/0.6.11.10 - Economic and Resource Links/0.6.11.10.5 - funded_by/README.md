---
ha: "0.6.11.10.5"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.10.5 - funded_by

**Domain:** Economic and Resource Links

## Purpose

Project funded by actor or source.

## Endpoint Constraints

- Source: `Project`
- Target: `Actor`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `funds`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "funded_by"`
- `link_type = "0.6.11.10.5"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
