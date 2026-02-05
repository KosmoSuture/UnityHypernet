# Bookmark - Web Bookmark

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
