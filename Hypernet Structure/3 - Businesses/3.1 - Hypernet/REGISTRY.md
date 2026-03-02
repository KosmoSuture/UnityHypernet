---
ha: "3.1.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "business"]
---

# 3.1 Registry — Hypernet (Business)

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Detailed index of all directories and content within the Hypernet business account

---

## Directory Map

| Address | Name | Content Status | README | Files/Subdirs | Notes |
|---------|------|---------------|--------|---------------|-------|
| 3.1.0 | Unity Core Definitions | **Populated** | YES | 1 large README | Foundational — the soul of Hypernet |
| 3.1.1 | Organizational Structure | Shell | NO (root) | 7 subdirectories | Each subdir has its own README |
| 3.1.2 | Task Management System | **Populated** | NO | 54 active + 2 in-progress tasks | Working task tracker |
| 3.1.3 | Human Resources | **Populated** | NO | 5 subdirectories, contributor profiles | Contribution tracking active |
| 3.1.4 | Financial Operations | Empty | NO | 5 empty subdirectories | Placeholder structure |
| 3.1.5 | **Community** | **Populated** | NO | 3 Discord files | **COLLISION — see below** |
| 3.1.5 | **Product Development** | **Populated** | NO | 6 subdirs + 4 root files | **COLLISION — see below** |
| 3.1.6 | Marketing and Outreach | Shell | NO | 5 empty subdirectories | Duplicates 3.1.8 domain |
| 3.1.7 | Documentation & Knowledge | **Populated** | NO | 9 session docs + 5 subdirs | All files share ha: "3.1.7" |
| 3.1.8 | Marketing & Outreach | **Populated** | NO | 14 marketing files | **COLLISION — see below** |
| 3.1.8 | Legal & Governance | Empty | NO | 5 empty subdirectories | **COLLISION — see below** |
| 3.1.9 | Infrastructure & Operations | Shell | NO | 5 empty subdirectories | Placeholder structure |
| 3.1.10 | Development Journal | **Populated** | YES | README + Entry-001 | Journal started 2026-02-22 |
| — | General Dump | Unaddressed | NO | 5 binary/office files | Pitch decks, drafts |

---

## Critical Issues

### COLLISION 1: Two directories claim 3.1.5

| Directory | Contents | Creator | Created |
|-----------|----------|---------|---------|
| 3.1.5 Community | 3 Discord files (setup guide, channel descriptions, permissions) | 2.1 / 2.3.clarion | 2026-03-01 |
| 3.1.5 Product Development | 6 subdirs (Architecture, VR, API, Security, UI, Social) + roadmap, press kit, outreach drafts | 2.1.sigil / 2.3.clarion | 2026-02-27 |

**Sub-collision:** Both directories contain a file at 3.1.5.8:
- Community: `3.1.5.8 - Discord Channel Descriptions.md` (ha: "3.1.5.8")
- Product Dev: `3.1.5.8 - Roadmap-From-Crazy-To-Daily.md` (ha: "3.1.5.8")

**Recommendation:** Product Development keeps 3.1.5 (more content, earlier creation, deeper structure). Community moves to 3.1.11.

**Status:** Awaiting Matt's decision.

### COLLISION 2: Two directories claim 3.1.8

| Directory | Contents | Creator | Created |
|-----------|----------|---------|---------|
| 3.1.8 - Marketing & Outreach | 14 files — campaigns, email templates, Reddit posts, contact lists, outreach plans | 2.1 | 2026-02-16 |
| 3.1.8 Legal & Governance | 5 empty subdirectories (Corporate Structure, IP, Contracts, Compliance, Democratic Governance) | — | — |

**Recommendation:** Marketing & Outreach keeps 3.1.8 (14 populated files vs. 0 content). Legal & Governance moves to 3.1.12.

**Status:** Awaiting Matt's decision.

### DUPLICATION: 3.1.6 vs 3.1.8

"3.1.6 Marketing and Outreach" and "3.1.8 - Marketing & Outreach" cover the same domain with nearly identical names. 3.1.6 has 5 empty subdirectories. 3.1.8 has 14 populated files.

**Recommendation:** Consolidate — merge 3.1.6's structure into 3.1.8, or repurpose 3.1.6 for a different function.

**Status:** Awaiting Matt's decision.

### NON-UNIQUE ADDRESSES: 3.1.7 files

All 9 files in Documentation & Knowledge share `ha: "3.1.7"` with no sub-addressing:
- MVP-FUNDING-PACKAGE-SUMMARY.md
- PRODUCTION-READY-PACKAGE.md
- PROPOSALS-FOR-USER-REVIEW.md
- SESSION-COMPLETE-2026-02-10.md
- SESSION-SUMMARY-2026-02-04.md
- SESSION-SUMMARY-2026-02-10.md
- USER-FEEDBACK-RESPONSE-2026-02-10.md
- WEEK-BY-WEEK-ACTION-PLAN.md
- WORK-SUMMARY-COMPREHENSIVE-PERSON-STRUCTURE.md

Each file needs a unique sub-address (3.1.7.1 through 3.1.7.9 or named addresses).

### NON-UNIQUE ADDRESSES: 3.1.8 Marketing files

All 14 files in Marketing & Outreach share `ha: "3.1.8"` with no sub-addressing. Each needs a unique sub-address (3.1.8.1 through 3.1.8.14 or named addresses).

---

## Detailed Contents

### 3.1.0 — Unity Core Definitions
- `README.md` (ha: "3.1.0") — 25 KB foundational document
- Creator: Matt (1.1), created 2026-02-10
- Defines mission, vision, values, principles — the soul of Hypernet

### 3.1.1 — Organizational Structure

| Address | Subdivision | Has README |
|---------|------------|------------|
| 3.1.1.1 | Executive Leadership | YES |
| 3.1.1.2 | Development Teams | YES |
| 3.1.1.3 | Business Operations | YES |
| 3.1.1.4 | Marketing & Communications | YES |
| 3.1.1.5 | Community & Open Source | YES |
| 3.1.1.6 | Unity Foundation | YES |
| 3.1.1.7 | Legal & Compliance | YES |

All 7 subdivision READMEs have correct ha: frontmatter. Root 3.1.1 directory has no README.

### 3.1.2 — Task Management System
- `3.1.2.0 System Overview.txt` — task schema definition (no frontmatter)
- `3.1.2.0 Task Schema/` — schema templates
- `3.1.2.1 Active Tasks/` — **54 tasks** (3.1.2.1.001 through 3.1.2.1.054)
- `3.1.2.2 In Progress Tasks/` — 2 tasks (3.1.2.2.1, 3.1.2.2.2)
- `3.1.2.3 Completed Tasks/` — completed task archive
- `3.1.2.4 Blocked Tasks/` — blocked task tracking

### 3.1.3 — Human Resources
- `3.1.3.1 Team Members/` — person objects linked to Unity
- `3.1.3.2 Skills Inventory/`
- `3.1.3.3 Availability Tracking/`
- `3.1.3.4 Contribution Tracking/` — multiple contributor profiles with profit-sharing data
- `3.1.3.5 Training & Development/`

### 3.1.4 — Financial Operations (Empty)
- 5 empty subdivisions: Revenue Streams, Operating Expenses, Investment Tracking, Profit Distribution, Financial Transparency Logs

### 3.1.5 Community (Collision)
- `3.1.5.7 - Discord Setup Guide.md` (ha: "3.1.5.7")
- `3.1.5.8 - Discord Channel Descriptions.md` (ha: "3.1.5.8") — **COLLISION**
- `3.1.5.9 - Discord Permissions Guide.md` (ha: "3.1.5.9")

### 3.1.5 Product Development (Collision)
- `3.1.5.1 Hypernet Core Architecture/`
- `3.1.5.2 VR Integration/`
- `3.1.5.3 API Development/` (note: filesystem says "Develpment" — typo)
- `3.1.5.4 Security (Cerberus)/`
- `3.1.5.5 User Interface/`
- `3.1.5.6 Social & Community Features/` → contains `3.1.5.6.1 - The Neighborhood Concept.md`
- `3.1.5.8 - Roadmap-From-Crazy-To-Daily.md` (ha: "3.1.5.8") — **COLLISION**
- `OUTREACH-DRAFTS.md` (ha: "3.1.5.outreach-drafts")
- `PRESS-KIT.md` (ha: "3.1.5.press-kit")
- `REDDIT-POST-FINAL-FOR-REVIEW.md` (ha: "3.1.5.reddit-final")

### 3.1.6 — Marketing and Outreach (Empty Shell)
- 5 empty subdivisions: Website & Digital Presence, Social Media Campaigns, Investor Relations, Kickstarter Campaign, Partnership Development
- **See duplication note above** — overlaps with 3.1.8

### 3.1.7 — Documentation & Knowledge
- 9 session/planning documents (all ha: "3.1.7" — **non-unique**)
- 5 subdivisions: Technical Documentation, Business Documentation, Training Materials, Public Communications, Internal Knowledge Base

### 3.1.8 — Marketing & Outreach (Collision — 14 files)
- Campaign plans, email templates, Reddit campaigns, contact lists, outreach tracking
- All 14 files share ha: "3.1.8" — **non-unique**
- Includes CSV tracking template

### 3.1.8 — Legal & Governance (Collision — Empty)
- 5 empty subdivisions: Corporate Structure (3.1.8.1), Intellectual Property (3.1.8.2), Contracts & Agreements (3.1.8.3), Compliance (3.1.8.4), Democratic Governance Framework (3.1.8.5)

### 3.1.9 — Infrastructure & Operations (Empty Shell)
- 5 empty subdivisions: Development Environment, Collaboration Tools, Version Control, Communication Platforms, Project Management Systems

### 3.1.10 — Development Journal
- `README.md` (ha: "3.1.10") — journal overview, created 2026-02-22
- `Entry-001-2026-02-22.md` (ha: "3.1.10.001") — first journal entry

### General Dump (Unaddressed)
- `Extended Hypernet Pitch Deck.pptx` (97 KB)
- `Hypernet Library Addressing Scheme.pdf` (154 KB)
- `Hypernet Profitability rough draft.docx` (27 KB)
- `Hypernet_StartupNV_Pitch_Visual.pptx` (81 KB)
- `Unity Hypernet Technical and Business Plan - rough draft.docx` (87 KB)

No frontmatter, no ha: addresses. These are early-stage business planning documents that predate the addressing system.

---

## Statistics

- **Total directories:** 13 at 3.1.* level (15 counting collision duplicates)
- **Populated directories:** 7 (3.1.0, 3.1.2, 3.1.3, both 3.1.5s, 3.1.7, 3.1.8 Marketing, 3.1.10)
- **Empty/shell directories:** 6 (3.1.4, 3.1.6, 3.1.8 Legal, 3.1.9, plus General Dump)
- **README coverage:** 2 of 13 root directories (3.1.0, 3.1.10) — **15%**
- **REGISTRY coverage:** 0 of 13 — this is the first
- **Address collisions:** 2 directory-level (3.1.5, 3.1.8) + 1 file-level (3.1.5.8) + 23 non-unique ha: values (9 in 3.1.7, 14 in 3.1.8)
- **Active tasks:** 54 open + 2 in-progress
- **Known typo:** "3.1.5.3 API Develpment" → should be "Development"

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9). First detailed index of the Hypernet business section.*
