---
ha: "0.6.11.8"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.8 - Communication and Social Links

Messaging, replies, mentions, subscriptions, and social propagation.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.8.1` | `sent_to` | Message -> Actor |
| `0.6.11.8.2` | `sent_from` | Message -> Actor |
| `0.6.11.8.3` | `mentions` | Content -> Object |
| `0.6.11.8.4` | `replies_to` | Message -> Message |
| `0.6.11.8.5` | `forwards` | Message -> Message |
| `0.6.11.8.6` | `subscribes_to` | Actor -> Source |
| `0.6.11.8.7` | `follows` | Actor -> Actor |
| `0.6.11.8.8` | `likes` | Actor -> Object |
| `0.6.11.8.9` | `shares` | Actor -> Object |
| `0.6.11.8.10` | `notifies` | Notification -> Actor |
