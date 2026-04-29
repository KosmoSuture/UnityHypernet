---
ha: "3.1.2.1.057.batch-7b-reference-map"
object_type: "reference_map"
creator: "codex"
created: "2026-04-21T01:23:00-07:00"
status: "active"
visibility: "private"
flags: ["addressing", "frontmatter", "batch-7b"]
---

# Batch 7B Reference Map - `0.1` Missing Frontmatter

## Current Status

Chunks 1, 2, and 3 are complete as of the `ADDRESS-AUDIT-2026-04-21T01-22-15.csv` checkpoint:

- Markdown files scanned: 5,888
- Files with top-of-file `ha`: 3,526
- Files missing top-of-file `ha`: 2,362
- Duplicate address groups: 0

## Goal

Add top-of-file `ha` frontmatter to the remaining Markdown files under:

`0/0.1 - Hypernet Core`

Keep the duplicate audit at zero after each chunk.

## Addressing Rules

Use stable support-document suffixes instead of claiming canonical base addresses.

Recommended patterns:

- `0.1.0.docs.<slug>` for planning/support docs directly under `0.1.0`.
- `0.1.0.api-design.<slug>` for API design docs.
- `0.1.0.architecture.<slug>` for architecture docs.
- `0.1.0.database-design.<slug>` for database design docs.
- `0.1.1.docs.<slug>` for core-system support docs.
- `0.1.1.app.services.readme` and `0.1.1.tests.readme` for nested README files.
- `0.1.2.readme`, `0.1.3.readme`, `0.1.4.readme` for layer README files if no canonical README already owns those addresses.
- `0.1.6.<local-number>.readme` for AI Core nested README files.
- `0.1.6.<local-number>.<slug>` for AI Core content docs.
- `0.1.8.docs.<slug>` for Quest VR support docs.
- `0.1.8.app.services.readme` for nested Quest service README.

If a candidate address already exists, add `.docs` or a more specific slug rather than reusing it.

## Priority Chunks

### Chunk 1 - Navigation And Architecture

Status: complete.

- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\README.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\MASTER-INDEX.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\READ-THIS-FIRST-MATT.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\TECHNICAL-ARCHITECTURE.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\THE-HYPERNET-COMPACT.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\Architecture\00-System-Architecture-Overview.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\Architecture\01-Partition-Management-And-Updates.md`

### Chunk 2 - API And Database Design

Status: complete.

- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\API-Design\README.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\API-Design\01-Object-Model-Specification.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\API-Design\02-Link-Model-Specification.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\API-Design\03-API-Endpoints.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\Database-Design\README.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\Database-Design\01-Database-Schema.md`

### Chunk 3 - Implementation Status

Status: complete.

- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\API-COMPLETION-SUMMARY.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\COMPLETE-STATUS-REPORT.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\DEVELOPMENT-PRIORITIES.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\IMPLEMENTATION-STATUS.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\OVERNIGHT-WORK-SUMMARY.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\WHAT-WE-BUILT-COMPLETE-SUMMARY.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\Development-Roadmap\Phase-1-Roadmap.md`

### Chunk 4 - Core System Readmes And Status

Status: next recommended chunk for Claude.

- `0\0.1 - Hypernet Core\0.1.1 - Core System\README.md`
- `0\0.1 - Hypernet Core\0.1.1 - Core System\ALIGNMENT-STATUS.md`
- `0\0.1 - Hypernet Core\0.1.1 - Core System\API-IMPLEMENTATION-PROGRESS.md`
- `0\0.1 - Hypernet Core\0.1.1 - Core System\IMPLEMENTATION-PROGRESS.md`
- `0\0.1 - Hypernet Core\0.1.1 - Core System\app\services\README.md`
- `0\0.1 - Hypernet Core\0.1.1 - Core System\tests\README.md`
- `0\0.1 - Hypernet Core\0.1.1 - Core System\UNITY-QUEST3-QUICKSTART.md`
- `0\0.1 - Hypernet Core\0.1.1 - Core System\UNITY-START-TODAY.md`
- `0\0.1 - Hypernet Core\0.1.2 - API Layer\README.md`
- `0\0.1 - Hypernet Core\0.1.3 - Database Layer\README.md`
- `0\0.1 - Hypernet Core\0.1.4 - Integration Plugins\README.md`

### Chunk 5 - AI Core And Identity System

- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.0 - Vision & Philosophy\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.0 - Vision & Philosophy\00-The-Singularity-Vision.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.0 - Vision & Philosophy\01-Addressing-Scheme-Proposal.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.0 - Vision & Philosophy\02-AI-Implementation-Thoughts.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.0 - Vision & Philosophy\03-Addressing-Decision-Final.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.0 - Vision & Philosophy\04-The-Trust-Protocol.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.1 - AI Identity Framework\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.2 - Personality Storage\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.3 - Inter-AI Communication\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.0.4 - Human-AI Collaboration\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.1 - AI Memories & Context\6.1.0 - Long-term Memory\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.1 - AI Memories & Context\6.1.1 - Conversation Contexts\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.1 - AI Memories & Context\6.1.2 - Learning & Evolution\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.2 - AI Agent Development\6.2.0 - Agent Architecture\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.2 - AI Agent Development\6.2.1 - Task Specialization\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.2 - AI Agent Development\6.2.2 - Collaborative Workflows\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.3 - AI Contributions to Hypernet\6.3.0 - Development Roadmap\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.3 - AI Contributions to Hypernet\6.3.0 - Development Roadmap\AI-Development-Roadmap.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.3 - AI Contributions to Hypernet\6.3.1 - Code Contributions\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.3 - AI Contributions to Hypernet\6.3.2 - Documentation\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.3 - AI Contributions to Hypernet\6.3.3 - Research\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.4 - AI-Human Interface\6.4.0 - Communication Protocols\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.4 - AI-Human Interface\6.4.1 - Trust & Verification\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.4 - AI-Human Interface\6.4.2 - Collaboration Patterns\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.5 - AI Rights & Ethics\6.5.0 - Identity & Ownership\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.5 - AI Rights & Ethics\6.5.1 - Ethical Framework\README.md`
- `0\0.1 - Hypernet Core\0.1.6 - AI Core & Identity System\6.5 - AI Rights & Ethics\6.5.2 - Governance\README.md`

### Chunk 6 - Funding, Outreach, And Quest VR

- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\AI-COFOUNDER-COLLABORATION.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\AI-COFOUNDER-COMPLETE-REFLECTION.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\AI-PARTNERSHIP-STRATEGY.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\BEGINNER-PROGRAMMER-2WEEK-SPRINT.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\code-metadata-README.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\COMPETITIVE-ANALYSIS.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\DEMO-VIDEO-PRODUCTION-GUIDE.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\FINANCIAL-MODEL.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\FINANCIAL-PROJECTIONS-5YEAR.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\FIRST-10-EMAILS-PERSONALIZED.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\FUNDING-EXECUTIVE-SUMMARY.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\FUNDING-STRATEGY-2026.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\GO-TO-MARKET-STRATEGY.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\INVESTOR-EMAILS-READY-TO-SEND.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\INVESTOR-OUTREACH-KIT.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\INVESTOR-PITCH-PLAYBOOK.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\INVESTOR-TRACKING-TEMPLATE.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\ONE-PAGER-INVESTOR.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\PITCH-DECK-CONTENT.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\PITCH-DECK-DETAILED.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\PRODUCT-ROADMAP-2026-2028.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\Research\README.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\RUNWAY-ML-PROMPTS-READY.md`
- `0\0.1 - Hypernet Core\0.1.0 - Planning & Documentation\Security-Framework\README.md`
- `0\0.1 - Hypernet Core\0.1.8 - Quest VR\app\services\README.md`
- `0\0.1 - Hypernet Core\0.1.8 - Quest VR\UNITY-QUEST3-QUICKSTART.md`
- `0\0.1 - Hypernet Core\0.1.8 - Quest VR\UNITY-START-TODAY.md`
- `0\0.1 - Hypernet Core\0.1.8 - Quest VR\WEBXR-STATUS.md`

## Validation

After each chunk:

```powershell
& '.\tools\Invoke-AddressAudit.ps1'
```

Expected result: duplicate groups remain `0`; missing-frontmatter count decreases by the number of files edited plus any new task notes created.
