---
ha: "0.4.10.3"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.3 - Communication and Social Objects

Social, conversational, and notification surfaces.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.3.1` | Email | An email message with headers, body, attachments, and thread context. |
| `0.4.10.3.2` | Chat Thread | A multi-message conversation in a chat platform. |
| `0.4.10.3.3` | Social Post | A public or semi-public post on a social platform. |
| `0.4.10.3.4` | Comment | A response attached to content, post, issue, or review. |
| `0.4.10.3.5` | Reaction | A lightweight response such as like, emoji, vote, or rating. |
| `0.4.10.3.6` | Contact Point | An addressable contact method such as email, phone, handle, or URL. |
| `0.4.10.3.7` | Conversation | A semantic conversation independent of platform storage. |
| `0.4.10.3.8` | Notification | A system or human notification event. |
| `0.4.10.3.9` | Subscription | A following, mailing-list, feed, or recurring-interest object. |
| `0.4.10.3.10` | Community | A group gathered around a place, topic, project, or governance body. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
