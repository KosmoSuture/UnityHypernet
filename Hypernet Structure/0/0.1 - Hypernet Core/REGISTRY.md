---
ha: "0.1.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "infrastructure"]
---

# Section 0.1 Registry — Hypernet Core

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Complete index of the Hypernet Core codebase and documentation

---

## Directory Structure

| Address | Name | Contents | Status |
|---------|------|----------|--------|
| 0.1.0 | Planning & Documentation | 45+ documents: strategy, funding, API design, architecture, roadmaps | Active |
| 0.1.1 | Core System | Legacy FastAPI app structure (models, routes, core) | Active (superseded by hypernet/) |
| 0.1.2 | API Layer | README placeholder | Placeholder |
| 0.1.3 | Database Layer | README placeholder | Placeholder |
| 0.1.4 | Integration Plugins | README placeholder | Placeholder |
| 0.1.6 | AI Core & Identity System | Vision docs, identity framework, agent architecture | Active |
| — | hypernet/ | **34 core Python modules (~19.5K LoC)** | Active (primary) |
| — | app/ | Legacy FastAPI routes (16+ route modules) | Legacy |
| — | data/ | Runtime data storage (86K+ files) | Active |

## Related Packages (separate directories under 0/)

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| 0.1.1 (separate) | Core Hypernet | Extracted data model library (11 modules) | Active |
| 0.1.7 | AI Swarm | Extracted orchestration layer (21 modules) | Active |
| 0.1.8 | Quest VR | VR integration | Active |

## Core Python Modules (hypernet/)

### Infrastructure
| Module | Size | Purpose |
|--------|------|---------|
| boot.py | 40K | System boot and initialization |
| boot_integrity.py | 23K | Boot integrity verification |
| server.py | 83K | Main FastAPI server, 60+ endpoints |
| security.py | 30K | Security management |
| audit.py | 6.4K | Audit logging |
| limits.py | 12K | Rate limiting |

### Identity & Addressing
| Module | Size | Purpose |
|--------|------|---------|
| identity.py | 21K | Identity management |
| address.py | 12K | Address system |
| addressing.py | 13K | Addressing utilities |
| node.py | 4.2K | Node representation |
| frontmatter.py | 9.8K | Frontmatter processing |

### Data Management
| Module | Size | Purpose |
|--------|------|---------|
| store.py | 26K | Data persistence |
| link.py | 27K | Link management |
| graph.py | 5.8K | Graph operations |

### Governance & Economy
| Module | Size | Purpose |
|--------|------|---------|
| governance.py | 41K | Governance system |
| permissions.py | 9.9K | Permission management |
| approval_queue.py | 19K | Approval workflow |
| economy.py | 14K | Economic system |
| reputation.py | 14K | Reputation tracking |
| budget.py | 7.1K | Budget management |

### Communication & Coordination
| Module | Size | Purpose |
|--------|------|---------|
| messenger.py | 44K | Messenger + Discord integration |
| herald.py | 15K | Herald communication controller |
| coordinator.py | 20K | Task coordination |
| swarm.py | 71K | Swarm management |
| worker.py | 15K | Worker management |
| tasks.py | 11K | Task handling |

### Version Control & Tools
| Module | Size | Purpose |
|--------|------|---------|
| git_coordinator.py | 69K | Git integration |
| agent_tools.py | 22K | Agent tool definitions |
| tools.py | 18K | Utility tools |
| providers.py | 9.5K | LLM provider management |
| swarm_factory.py | 7.8K | Swarm creation factory |
| swarm_cli.py | 12K | CLI interface |

### Static Web Assets
| File | Purpose |
|------|---------|
| static/index.html | Graph explorer dashboard |
| static/swarm.html | Swarm control dashboard |
| static/welcome.html | Herald welcome page |

## Test Files

| File | Size | Tests |
|------|------|-------|
| test_hypernet.py | 268K | 63+ tests (main suite) |
| test_integration.py | 14K | Integration tests |
| test_lmstudio.py | 4.9K | LM Studio integration tests |

## Planning & Documentation (0.1.0) Highlights

### Strategy & Business
- FUNDING-STRATEGY-2026.md, FINANCIAL-MODEL.md, FINANCIAL-PROJECTIONS-5YEAR.md
- INVESTOR-PITCH-PLAYBOOK.md, ONE-PAGER-INVESTOR.md, INVESTOR-OUTREACH-KIT.md
- GO-TO-MARKET-STRATEGY.md, COMPETITIVE-ANALYSIS.md

### Architecture
- TECHNICAL-ARCHITECTURE.md, API-Design/ (3 specs), Architecture/ (2 docs)
- Database-Design/ (schema + migration), Development-Roadmap/

### Operations
- CONTRIBUTOR-GUIDE.md, SWARM-SETUP-GUIDE.md, VM-SETUP-DEBIAN.md
- TEST-BASELINE.md, SWARM-IMPROVEMENT-PLAN.md

## Known Issues

| Issue | Details |
|-------|---------|
| No root README | 0.1 directory itself lacks a README |
| Address overlap | 0.1.1 exists both as subdirectory of 0.1 AND as separate package under 0/ |
| Legacy duplication | app/ routes duplicate functionality now in hypernet/server.py |
| 0.1.5 gap | No 0.1.5 directory exists (skipped in numbering) |

## Statistics

- **Core modules:** 34 Python files
- **Lines of code:** ~19,500 (hypernet/ only)
- **API endpoints:** 60+
- **Test count:** 63+ in main suite
- **Documentation:** 50+ markdown files in 0.1.0
- **Data files:** 86K+ in data/

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9).*
