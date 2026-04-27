---
ha: "0.6.11.7.10"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.7.10 - part_of_project

**Domain:** Work and Dependency Links

## Purpose

Source belongs to project.

## Endpoint Constraints

- Source: `Object`
- Target: `Project`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `true`
- Inverse: `project_contains`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "part_of_project"`
- `link_type = "0.6.11.7.10"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
