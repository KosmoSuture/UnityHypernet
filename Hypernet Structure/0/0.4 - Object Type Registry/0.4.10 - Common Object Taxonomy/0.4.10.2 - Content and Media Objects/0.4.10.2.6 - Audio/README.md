---
ha: "0.4.10.2.6"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# 0.4.10.2.6 - Audio

**Domain:** Content and Media Objects

## Purpose

A sound recording, voice note, music file, or stream.

## Required Fields

- `file_ref`
- `duration`
- `mime_type`

## Recommended Graph Links

- `transcript_of`
- `created_by`
- `part_of`

## Database Indexes

- Type index: `type_address = 0.4.10.2.6`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
