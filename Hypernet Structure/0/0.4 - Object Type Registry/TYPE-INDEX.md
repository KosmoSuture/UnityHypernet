---
ha: "0.4.type-index"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
updated: "2026-04-26"
status: "active"
visibility: "public"
flags: ["registry", "database-first"]
---

# Hypernet Object Type Registry - Master Index

**Status:** Database-first registry active
**Canonical common taxonomy:** `0.4.10 - Common Object Taxonomy`
**Common object types defined:** 100
**Legacy phase-1 types preserved:** 28

## Rule

If a type is new, define it in its own folder with a `README.md`. Root-level files are indexes, migration notes, or legacy summaries.

## Primary Taxonomy

| Address | Domain | Count |
|---|---|---:|
| `0.4.10.1` | Identity and Agent Objects | 10 |
| `0.4.10.2` | Content and Media Objects | 10 |
| `0.4.10.3` | Communication and Social Objects | 10 |
| `0.4.10.4` | Place and Event Objects | 10 |
| `0.4.10.5` | Work and Process Objects | 10 |
| `0.4.10.6` | Commerce and Finance Objects | 10 |
| `0.4.10.7` | Legal and Governance Objects | 10 |
| `0.4.10.8` | Science and Knowledge Objects | 10 |
| `0.4.10.9` | System and Device Objects | 10 |
| `0.4.10.10` | Health and Biology Objects | 10 |

## Legacy Phase-1 Types

These remain valid but should be reconciled with `0.4.10` over time.

| Category | Examples |
|---|---|
| Core | BaseObject, User, Link, Integration |
| Media | Photo, Video, Audio, Document, Screenshot |
| Social | SocialPost, SocialAccount, SocialConnection, SocialMessage |
| Communication | Email, SMS, ChatMessage, VoiceCall, VideoCall |
| Web | WebPage, Bookmark, RSSFeed |
| Life | CalendarEvent, Task, Note, Contact |

## Database Contract

Every object instance should carry:

- `address`
- `type_address`
- `data`
- `created_at`, `updated_at`, `deleted_at`
- `creator`, `owner`, `visibility`
- `source_type`, `source_id`
- link indexes through first-class links rather than embedded free-text references

## Next Work

1. Reconcile old `0.0.*` phase-1 type files against `0.4.10`.
2. Add runtime object-type registry loading from folder READMEs.
3. Add validation so writes require a registered `type_address`.
4. Add migration notes for legacy root-level object files.
