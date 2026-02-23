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
