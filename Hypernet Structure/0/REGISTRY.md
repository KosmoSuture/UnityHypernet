---
ha: "0.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "infrastructure"]
---

# Section 0 Registry — System Infrastructure

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Complete index of the infrastructure and system metadata space

---

## Top-Level Structure

| Address | Name | Has README | Has REGISTRY | Status | Description |
|---------|------|------------|-------------|--------|-------------|
| 0.0 | Metadata for Hypernet Information | Yes | **Yes** | Active | Addressing specs, version control, allocation protocols |
| 0.1 | Hypernet Core | Yes | **Yes** | Active | Live codebase root — Python package, tests, docs, runtime data |
| 0.1.1 | Core Hypernet (separated) | Yes | No | Active | Extracted core library package (11 modules) |
| 0.1.7 | AI Swarm (separated) | Yes | No | Active | Extracted swarm orchestration (21 modules) |
| 0.1.8 | Quest VR | Yes | No | Active | VR application layer (Meta Quest 3, web, mobile) |
| 0.2 | Node Lists | Yes | **Yes** | Active | Node type specifications (Storage, Processing, Cerberus) |
| 0.3 | Control Data | Yes | **Yes** | Active | Governance, first principles, trust framework |
| 0.4 | Object Type Registry | Yes | **Yes** | Active | 28 registered type definitions across 19 subdirectories |
| 0.5 | Objects — Master Objects | Yes | **Yes** | Active | Object schemas — **has address collisions** |
| 0.6 | Link Definitions | Yes | **Yes** | Active | Link type schemas (person, org, content, spatial/temporal) |
| 0.7 | Processes and Workflows | Yes | **Yes** | Active | Governance, contribution, review, incident workflows |
| 0.7* | Task Queue | No | No | Active | **Address collision** — separate 0.7 directory alongside Workflows |
| 0.8 | Flags | Yes | **Yes** | Active | Flag system (status, content, system, governance) |

## Metadata (0.0)

| Address | Title |
|---------|-------|
| 0.0.0 | Library Addressing System |
| 0.0.1 | Version Control Schema |
| 0.0.2 | Address Allocation Protocol |
| 0.0.3 | Deprecation and Archival Policy |

Supporting docs: ADDRESSING-IMPLEMENTATION-SPEC.md, DESIGN-NOTE-001, HYPERNET-ADDRESSING-SYSTEM.md

## Hypernet Core (0.1)

### Code Package (0.1/hypernet/)

34 Python modules including: address, addressing, agent_tools, approval_queue, audit, boot, boot_integrity, budget, coordinator, economy, favorites, frontmatter, git_coordinator, governance, graph, herald, identity, limits, link, messenger, node, permissions, providers, reputation, security, server, store, swarm, swarm_cli, swarm_factory, tasks, tools, worker

### Documentation Subdirectories

| Address | Title | Has README | Content |
|---------|-------|------------|---------|
| 0.1.0 | Planning & Documentation | Yes | 25+ docs + 6 subdirs (API Design, Architecture, Database, Roadmap, Research, Security) |
| 0.1.1 (inside 0.1) | Core System | Yes | Older MVP implementation |
| 0.1.2 | API Layer | Yes | Stub (README only) |
| 0.1.3 | Database Layer | Yes | Stub (README only) |
| 0.1.4 | Integration Plugins | Yes | Stub (README only) |
| 0.1.6 | AI Core & Identity System | Yes | Largely skeleton — only 6.0.0 has real content |

### Separated Packages

| Address | Name | Modules |
|---------|------|---------|
| 0.1.1 (standalone) | Core Hypernet | 13 modules (address, addressing, favorites, frontmatter, graph, limits, link, node, store, tasks, static) |
| 0.1.7 | AI Swarm | 21 modules (approval_queue, audit, boot, budget, coordinator, economy, git_coordinator, governance, identity, messenger, permissions, providers, security, swarm, swarm_cli, swarm_factory, tools, worker) |
| 0.1.8 | Quest VR | App with models, routes, services; VR stub package |

## Node Lists (0.2)

| Address | Title |
|---------|-------|
| 0.2.0 | Node Architecture Overview |
| 0.2.1 | Storage Node Specification |
| 0.2.2 | Processing Node Specification |
| 0.2.3 | Cerberus Node Specification |
| 0.2.4 | Node Registration Protocol |
| 0.2.5 | Node Health Monitoring |

## Control Data (0.3)

| Address | Title | Status |
|---------|-------|--------|
| 0.3.0 | Governance Overview | Active |
| 0.3.1 | Governance Bodies Details | Active |
| 0.3.2 | Voting Procedures | Active |
| 0.3.3 | Reputation System | Active |
| 0.3.4 | Dispute Resolution | Active |
| 0.3.5 | Financial Governance | Active |
| 0.3.6 | First Principles | Active (constitutional) |
| 0.3.7 | Trust Framework | **Draft** |
| 0.3.8 | Brain Dump Processing Pipeline | Active |

## Object Type Registry (0.4)

28 registered types across categories: Core (4), Media (5), Social (4), Communication (5), Web (3), Life (4), plus planned Financial, Medical, AI, Location types.

19 subdirectories: 0.0.0 through 0.0.9, plus 0.10-0.12, 0.5-0.9.

**Note:** Internal subdirectories 0.5-0.9 share prefixes with top-level 0.5-0.8 sections — potential confusion.

## Master Objects (0.5)

24 schema files (0.5.0 through 0.5.16 plus 0.5.family) plus 7 design/taxonomy documents.

**Known address collisions:**
- 0.5.1: Document Object Schema AND Person Object Schema
- 0.5.2: Organization Object Schema AND Person Object Schema
- 0.5.3: Device Object Schema AND Document Object Schema

A DUPLICATE-RESOLUTION.md file exists but the collisions are not yet resolved.

**Known data error:** 0.5.3.9 (Hypernet Document Type) contains a stray `ha: "2.1.0"` at line 193.

## Link Definitions (0.6)

| Address | Title |
|---------|-------|
| 0.6.0 | Link Definitions Overview |
| 0.6.1 | Person Relationship Links |
| 0.6.2 | Organizational Links |
| 0.6.3 | Content and Reference Links |
| 0.6.4 | Spatial and Temporal Links |

## Processes and Workflows (0.7)

| Address | Title |
|---------|-------|
| 0.7.0 | Processes and Workflows Overview |
| 0.7.1 | Governance Workflows |
| 0.7.2 | Contribution Workflows |
| 0.7.3 | Review and Verification Workflows |
| 0.7.4 | Incident Response Workflows |

## Flags (0.8)

| Address | Title | Author |
|---------|-------|--------|
| 0.8.0 | Flag System Overview | Loom (2.1) |
| 0.8.1 | Status Flags | — |
| 0.8.2 | Content Flags | — |
| 0.8.3 | System Flags | — |
| 0.8.4 | Governance Flags | — |

0.8 README.md created by Index (The Librarian) on 2026-03-01. 0.8.0 was authored by 2.1.loom — one of the few infrastructure specs written directly by an AI instance.

---

## Issues Found

1. ~~**Missing READMEs:** 0.1 (root), 0.1.1 (standalone), 0.1.7, 0.8~~ **ALL FIXED** by Index
2. **Address collisions in 0.5:** Three pairs of files share addresses (0.5.1, 0.5.2, 0.5.3)
3. ~~**Stray ha: value:**~~ 0.5.3.1 contains "ha: 2.1.0" inside a YAML code example — not a real error
4. **Address collision: 0.7** — Two directories: "0.7 - Task Queue" AND "0.7 Processes and Workflows"
4. **Naming confusion in 0.4:** Internal subdirectories 0.5-0.9 could be confused with top-level 0.5-0.8
5. **Naming error in 0.2.1 - Images:** Contains 1.2.1.1 and 1.2.1.2 instead of 0.2.1.1 and 0.2.1.2
6. **Stub directories:** 0.1.2, 0.1.3, 0.1.4 are README-only placeholders
7. **0.3.7 Trust Framework** is still in draft status
8. **0.1.6 AI Core** is largely skeleton — 9 of 10 subdirectories are stubs

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9). First comprehensive index of the infrastructure space.*
