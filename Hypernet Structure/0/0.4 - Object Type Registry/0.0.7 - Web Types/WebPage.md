---
ha: "0.4.0.7.1"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# WebPage - Saved Web Page

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> Web page object definitions now live folder-first under
> `0.4.10 - Common Object Taxonomy/0.4.10.2 - Content and Media Objects/`.
> This document is preserved as a compatibility reference; new schema
> work should land in the folder taxonomy.
>
> **Runtime:** `GET /schema/object-types`,
> `POST /schema/object-types/validate`,
> `PUT /node/{address}?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` for policy.

**Type ID:** `hypernet.web.page`
**Version:** 1.0
**Category:** 0.0.7 - Web Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Saved web pages - full page archives, article content, research.

---

## Required Fields

```yaml
url: String(2048)
  - Original URL

title: String(500)

saved_at: DateTime
```

---

## Optional Fields

```yaml
html_content: Text
  - Full HTML

text_content: Text
  - Extracted readable text

screenshot_id: UUID (FK to Screenshot)

# Metadata extracted from page
author: String(200)
published_at: DateTime
site_name: String(200)
description: Text

# Archive
archive_path: String(512)
  - Path to WARC or HTML file
```

---

## Metadata Schema

```json
{
  "og": {
    "title": "...",
    "description": "...",
    "image": "url"
  },
  "article": {
    "author": "John Doe",
    "published_time": "2024-01-15T10:00:00Z",
    "section": "Technology"
  },
  "tags": ["ai", "technology"],
  "reading_time": 5
}
```

---

## Relationships

```yaml
Outgoing:
  - has_screenshot: Screenshot
  - related_to: Bookmark
```

---

**Status:** Active
**Version:** 1.0
