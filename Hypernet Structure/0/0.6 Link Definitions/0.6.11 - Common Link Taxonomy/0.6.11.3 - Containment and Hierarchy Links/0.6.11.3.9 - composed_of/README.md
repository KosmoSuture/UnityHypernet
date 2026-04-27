---
ha: "0.6.11.3.9"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.3.9 - composed_of

**Domain:** Containment and Hierarchy Links

## Purpose

A whole is composed of components.

## Endpoint Constraints

- Source: `Object`
- Target: `Object`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `true`
- Inverse: `component_of`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "composed_of"`
- `link_type = "0.6.11.3.9"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
