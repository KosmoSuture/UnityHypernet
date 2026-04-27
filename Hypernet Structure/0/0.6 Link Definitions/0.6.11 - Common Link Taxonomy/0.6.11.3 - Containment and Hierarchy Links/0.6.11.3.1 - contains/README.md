---
ha: "0.6.11.3.1"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.3.1 - contains

**Domain:** Containment and Hierarchy Links

## Purpose

A container includes an object.

## Endpoint Constraints

- Source: `Container`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `true`
- Inverse: `contained_in`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "contains"`
- `link_type = "0.6.11.3.1"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
