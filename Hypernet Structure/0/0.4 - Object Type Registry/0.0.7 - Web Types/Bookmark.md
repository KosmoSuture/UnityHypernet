---
ha: "0.4.0.7.2"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# Bookmark - Web Bookmark

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> Bookmark object definitions now live folder-first under
> `0.4.10 - Common Object Taxonomy/0.4.10.2 - Content and Media Objects/`.
> This document is preserved as a compatibility reference; new schema
> work should land in the folder taxonomy.
>
> **Runtime:** `GET /schema/object-types`,
> `POST /schema/object-types/validate`,
> `PUT /node/{address}?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` for policy.

**Type ID:** `hypernet.web.bookmark`
**Version:** 1.0
**Category:** 0.0.7 - Web Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Browser bookmarks - saved links without full page content.

---

## Required Fields

```yaml
url: String(2048)

title: String(500)

bookmarked_at: DateTime
```

---

## Optional Fields

```yaml
description: Text
favicon_url: String(500)

folder: String(255)
  - Browser folder/category

tags: Text[]

is_favorite: Boolean
visit_count: Integer
last_visited_at: DateTime
```

---

## Metadata Schema

```json
{
  "browser": "Chrome",
  "folder_path": "Work/Projects/Hypernet",
  "imported_from": "chrome_bookmarks_export.html"
}
```

---

## Relationships

```yaml
Outgoing:
  - archives: WebPage (full saved version)
```

---

**Status:** Active
**Version:** 1.0
