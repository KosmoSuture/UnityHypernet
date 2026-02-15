# WebPage - Saved Web Page

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
