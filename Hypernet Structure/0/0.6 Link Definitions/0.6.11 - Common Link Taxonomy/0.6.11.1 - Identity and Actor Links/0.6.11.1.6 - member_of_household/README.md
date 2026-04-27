---
ha: "0.6.11.1.6"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# 0.6.11.1.6 - member_of_household

**Domain:** Identity and Actor Links

## Purpose

A person belongs to a household.

## Endpoint Constraints

- Source: `Person`
- Target: `Household`

## Properties

- Directed: `true`
- Symmetric: `false`
- Transitive: `false`
- Inverse: `household_has_member`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "member_of_household"`
- `link_type = "0.6.11.1.6"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
