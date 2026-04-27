---
ha: "0.6.11.4.1"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.4.1 - about

**Domain:** Semantic and Knowledge Links

## Purpose

An object is about a topic or concept.

## Endpoint Constraints

- Source: `Object`
- Target: `Concept`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `has_aboutness`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "about"`
- `link_type = "0.6.11.4.1"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
