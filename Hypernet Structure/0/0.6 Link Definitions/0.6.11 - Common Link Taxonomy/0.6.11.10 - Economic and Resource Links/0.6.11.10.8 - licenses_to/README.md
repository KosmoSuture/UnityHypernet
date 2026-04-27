---
ha: "0.6.11.10.8"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.10.8 - licenses_to

**Domain:** Economic and Resource Links

## Purpose

License grants rights to actor.

## Endpoint Constraints

- Source: `License`
- Target: `Actor`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `license_from`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "licenses_to"`
- `link_type = "0.6.11.10.8"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
