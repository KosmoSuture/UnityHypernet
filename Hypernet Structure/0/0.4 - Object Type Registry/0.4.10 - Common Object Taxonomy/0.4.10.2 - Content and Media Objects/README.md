---
ha: "0.4.10.2"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.2 - Content and Media Objects

Human-readable, machine-readable, and media-bearing content.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.2.1` | Document | A stable written artifact with content, metadata, and provenance. |
| `0.4.10.2.2` | Note | An atomic knowledge or memory unit. |
| `0.4.10.2.3` | Message | A sent or received communication unit. |
| `0.4.10.2.4` | Image | A still visual asset or photograph. |
| `0.4.10.2.5` | Video | A moving-image media object with optional transcript and time anchors. |
| `0.4.10.2.6` | Audio | A sound recording, voice note, music file, or stream. |
| `0.4.10.2.7` | Dataset | A structured collection of records, measurements, or observations. |
| `0.4.10.2.8` | Web Page | A captured or referenced web page. |
| `0.4.10.2.9` | Code Artifact | Source file, package, commit, build, or executable artifact. |
| `0.4.10.2.10` | Archive Package | A bundled export, snapshot, backup, or preservation package. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
