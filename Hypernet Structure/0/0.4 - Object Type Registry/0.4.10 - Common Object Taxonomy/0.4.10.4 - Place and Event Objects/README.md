---
ha: "0.4.10.4"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.4 - Place and Event Objects

Locations, spaces, movements, and time-bounded happenings.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.4.1` | Location | A named geographic or logical place. |
| `0.4.10.4.2` | Address | A postal, network, blockchain, or Hypernet address. |
| `0.4.10.4.3` | Venue | A place designed for gatherings, work, commerce, or events. |
| `0.4.10.4.4` | Region | A bounded geographic, administrative, or logical area. |
| `0.4.10.4.5` | Route | A path between places with ordered waypoints. |
| `0.4.10.4.6` | Trip | A travel episode containing routes, places, costs, and events. |
| `0.4.10.4.7` | Event | A time-bounded occurrence with participants and context. |
| `0.4.10.4.8` | Meeting | A collaborative event with participants, agenda, and outcomes. |
| `0.4.10.4.9` | Appointment | A scheduled commitment with one or more parties. |
| `0.4.10.4.10` | Time Span | A defined interval used by events, validity, and historical claims. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
