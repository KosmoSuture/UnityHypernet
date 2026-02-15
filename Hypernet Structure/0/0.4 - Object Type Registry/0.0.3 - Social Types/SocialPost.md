# SocialPost - Social Media Post

**Type ID:** `hypernet.social.post`
**Version:** 1.0
**Category:** 0.0.3 - Social Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Social media posts from Instagram, Twitter/X, Facebook, TikTok, LinkedIn, etc.

---

## Required Fields

```yaml
platform: String(50)
  - "instagram", "twitter", "facebook", "tiktok", "linkedin"

post_type: Enum
  - "text", "photo", "video", "story", "reel", "carousel"

content: Text
  - Post caption/text
  - Can be empty for some post types

posted_at: DateTime
  - When originally posted on platform
```

---

## Optional Fields

```yaml
platform_post_id: String(255)
  - External ID on platform

platform_url: String(500)
  - Link to original post

# Engagement
likes_count: Integer
comments_count: Integer
shares_count: Integer
views_count: Integer

# Status
visibility: Enum
  - "public", "private", "friends", "followers"

is_pinned: Boolean
location: String(200)
```

---

## Metadata Schema

```json
{
  "instagram": {
    "filter": "valencia",
    "is_ad": false,
    "tagged_users": ["@friend1", "@friend2"]
  },
  "twitter": {
    "retweet_count": 42,
    "quote_count": 5,
    "hashtags": ["#hypernet", "#ai"]
  },
  "engagement": {
    "top_comments": [],
    "engagement_rate": 0.034
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - source: Integration
  - references: Photo, Video (media in post)

Incoming:
  - authored_by: SocialAccount
```

---

**Status:** Active
**Version:** 1.0
