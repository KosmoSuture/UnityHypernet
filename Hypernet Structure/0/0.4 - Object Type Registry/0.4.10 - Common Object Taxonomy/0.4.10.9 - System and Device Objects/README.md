---
ha: "0.4.10.9"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.9 - System and Device Objects

Hardware, software, services, networks, and operational configuration.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.9.1` | Device | A physical or virtual machine, endpoint, or instrument. |
| `0.4.10.9.2` | Sensor | A device or process that observes and reports measurements. |
| `0.4.10.9.3` | Service | A running system capability exposed to users or other systems. |
| `0.4.10.9.4` | Integration | A connector to an external platform, account, or data source. |
| `0.4.10.9.5` | API Endpoint | A callable route, method, or interface contract. |
| `0.4.10.9.6` | Compute Node | A processing node participating in Hypernet execution. |
| `0.4.10.9.7` | Storage Node | A storage participant responsible for data persistence. |
| `0.4.10.9.8` | Network | A logical or physical network segment. |
| `0.4.10.9.9` | Software Package | A library, application, container, or installable unit. |
| `0.4.10.9.10` | Configuration | A structured setting set for a service, device, account, or workflow. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
