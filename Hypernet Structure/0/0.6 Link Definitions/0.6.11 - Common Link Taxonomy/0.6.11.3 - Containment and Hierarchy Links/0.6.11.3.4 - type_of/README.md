---
ha: "0.6.11.3.4"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.3.4 - type_of

**Domain:** Containment and Hierarchy Links

## Purpose

A type classifies an object.

## Endpoint Constraints

- Source: `Type`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `has_type`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "type_of"`
- `link_type = "0.6.11.3.4"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
