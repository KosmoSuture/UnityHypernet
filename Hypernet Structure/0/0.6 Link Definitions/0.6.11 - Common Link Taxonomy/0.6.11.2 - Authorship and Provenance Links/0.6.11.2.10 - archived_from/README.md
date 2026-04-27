---
ha: "0.6.11.2.10"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.2.10 - archived_from

**Domain:** Authorship and Provenance Links

## Purpose

Snapshot or archive source.

## Endpoint Constraints

- Source: `Archive Package`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `archived_as`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "archived_from"`
- `link_type = "0.6.11.2.10"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
