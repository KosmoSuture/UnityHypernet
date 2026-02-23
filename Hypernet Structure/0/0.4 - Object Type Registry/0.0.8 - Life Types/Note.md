---
ha: "0.4.0.8.3"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# Note - Personal Note

**Type ID:** `hypernet.life.note`
**Version:** 1.0
**Category:** 0.0.8 - Life Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Personal notes from note apps (Apple Notes, Notion, Evernote, Obsidian, etc.).

---

## Required Fields

```yaml
title: String(500)

content: Text
  - Markdown, HTML, or plain text

note_format: Enum
  - "plain", "markdown", "html", "rich_text"
```

---

## Optional Fields

```yaml
folder: String(255)
  - Notebook/folder name

tags: Text[]

is_pinned: Boolean
is_locked: Boolean

word_count: Integer

# Links
has_attachments: Boolean
attachment_count: Integer
```

---

## Metadata Schema

```json
{
  "notion": {
    "page_id": "abc-123",
    "database_id": "xyz-789"
  },
  "obsidian": {
    "vault": "Personal",
    "backlinks": ["[[Other Note]]"]
  },
  "formatting": {
    "font_size": 14,
    "has_checkboxes": true
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - references: Photo, Document (attachments)
  - links_to: Note (internal links)
  - related_to: Task, Event

Incoming:
  - referenced_by: Note
```

---

**Status:** Active - Phase 1 Priority
**Version:** 1.0
