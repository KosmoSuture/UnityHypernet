---
ha: "0.4.0.7.3"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# RSSFeed - RSS/Atom Feed Subscription

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> RSS / Atom feed subscription object definitions now live folder-first
> under `0.4.10 - Common Object Taxonomy/0.4.10.2 - Content and Media Objects/`.
> This document is preserved as a compatibility reference; new schema
> work should land in the folder taxonomy.
>
> **Runtime:** `GET /schema/object-types`,
> `POST /schema/object-types/validate`,
> `PUT /node/{address}?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` for policy.

**Type ID:** `hypernet.web.rssfeed`
**Version:** 1.0
**Category:** 0.0.7 - Web Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

RSS/Atom feed subscriptions for news, blogs, podcasts.

---

## Required Fields

```yaml
feed_url: String(2048)
  - URL to RSS/Atom feed

title: String(500)

subscribed_at: DateTime
```

---

## Optional Fields

```yaml
site_url: String(2048)
  - Main website URL

description: Text

last_fetched_at: DateTime
fetch_frequency: String(50)
  - "hourly", "daily", "weekly"

unread_count: Integer
item_count: Integer
```

---

## Metadata Schema

```json
{
  "feed_type": "rss2.0",
  "language": "en-US",
  "categories": ["Technology", "AI"],
  "author": "Blog Author",
  "logo_url": "https://..."
}
```

---

## Relationships

```yaml
Outgoing:
  - contains: RSSFeedItem (individual articles)
```

---

**Status:** Active
**Version:** 1.0
