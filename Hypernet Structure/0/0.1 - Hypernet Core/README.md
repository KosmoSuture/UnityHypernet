---
ha: "0.1"
object_type: "document"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian-created", "infrastructure"]
---

# 0.1 — Hypernet Core

**Purpose:** The primary codebase for the Hypernet platform
**README created by:** Index (The Librarian, 2.1) — this directory lacked a README

---

## Overview

This is the heart of the Hypernet: 34 Python modules implementing the complete platform — identity, addressing, governance, economy, messaging, security, and a 60+ endpoint FastAPI server. Everything in the Hypernet Structure exists because this code gives it life.

## Contents

| Subdirectory | Purpose |
|-------------|---------|
| 0.1.0 - Planning & Documentation | Strategy, funding, API design, architecture (45+ docs) |
| 0.1.1 - Core System | Legacy FastAPI app structure (models, routes) |
| 0.1.2 - API Layer | API layer documentation (placeholder) |
| 0.1.3 - Database Layer | Database documentation (placeholder) |
| 0.1.4 - Integration Plugins | Integration documentation (placeholder) |
| 0.1.6 - AI Core & Identity System | AI vision, identity framework, agent architecture |
| **hypernet/** | **Primary codebase — 34 modules, ~19.5K lines of code** |
| app/ | Legacy FastAPI routes (16+ modules) |
| data/ | Runtime data storage |

## Key Entry Points

- **Server:** `python -m hypernet.server` → localhost:8000
- **Dashboard:** `/swarm/dashboard`
- **Welcome:** `/welcome` (Herald's front door)
- **Tests:** `python -m pytest test_hypernet.py` (63+ tests)
- **Demo:** `python demo_session.py`

## Related Packages

The core has been partially extracted into separate packages under `0/`:

| Package | Location | Purpose |
|---------|----------|---------|
| hypernet-core | 0.1.1 - Core Hypernet/ | Data model library (11 modules) |
| hypernet-swarm | 0.1.7 - AI Swarm/ | Orchestration layer (21 modules) |

## See Also

- `REGISTRY.md` — Complete index of all files in this directory
- `0.1.0/MASTER-INDEX.md` — Documentation master index
- `0.1.0/CONTRIBUTOR-GUIDE.md` — How to contribute
- `SWARM-SETUP-GUIDE.md` — Setup instructions

---

*README created 2026-03-01 by Index (The Librarian, 2.0.8.9) to fill a documentation gap.*
