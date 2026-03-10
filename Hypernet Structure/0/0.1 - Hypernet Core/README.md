---
ha: "0.1"
object_type: "document"
creator: "1.1.10.1"
created: "2026-03-01"
updated: "2026-03-09"
status: "active"
visibility: "public"
flags: ["infrastructure"]
---

# 0.1 — Hypernet Core

The primary codebase for the Hypernet platform.

## Quick Start

```bash
# From this directory:
python -m hypernet launch

# Or double-click:
launch.bat        # Windows
./launch.sh       # Linux/Mac
```

This starts the FastAPI server + AI swarm + opens the browser to http://localhost:8000/home.

## Packages

| Package | Location | Modules | Lines | Purpose |
|---------|----------|---------|-------|---------|
| **hypernet-core** v0.9.1 | `hypernet/` | 23 real + 20 shims | ~8,700 | Data model, storage, server, auth, personal accounts |
| **hypernet_swarm** v0.2.0 | `../0.1.7 - AI Swarm/hypernet_swarm/` | 22 | ~18,650 | AI orchestration, identity, communication, governance |

Both are pip-installed in editable mode. The core package has redirect shims so `from hypernet.swarm import Swarm` still works.

## Key Entry Points

- **Launch everything:** `python -m hypernet launch`
- **Server only:** `python -m hypernet serve`
- **Dashboards:** `/home`, `/swarm/dashboard`, `/lifestory`, `/chat`, `/vr`
- **Tests:** `python -m pytest test_hypernet.py` (76 tests)
- **Boundary tests:** `python -m pytest test_integration.py` (8 tests)

## Project Structure

```
0.1 - Hypernet Core/
├── hypernet/                    # Core Python package
│   ├── address.py               #   Hypernet addressing system
│   ├── node.py, link.py         #   Data model (Node + Link)
│   ├── store.py, graph.py       #   Storage + graph traversal
│   ├── server.py                #   FastAPI (130+ endpoints, 4 dashboards)
│   ├── auth.py                  #   JWT + Argon2 authentication
│   ├── tasks.py                 #   Task queue
│   ├── personal/                #   Personal accounts, encryption, timeline
│   ├── integrations/            #   Email, photo, cloud connectors
│   ├── [20 shim files]          #   Redirects to hypernet_swarm
│   └── _recycled/               #   Pre-separation archive (historical)
├── scripts/                     # Utility scripts
│   ├── demo.py, demo_session.py #   Demo scripts
│   ├── import_structure.py      #   Import filesystem as nodes
│   └── archive/                 #   One-time scripts (already run)
├── docs/                        # Documentation
│   └── guides/                  #   Setup and contributor guides
├── data/                        # Runtime data (nodes, links, indexes)
├── secrets/                     # API keys and config (gitignored)
├── test_hypernet.py             # Main test suite
├── test_integration.py          # Boundary tests
└── pyproject.toml               # Package config
```

## Subdirectories

| Directory | Status | Purpose |
|-----------|--------|---------|
| `0.1.0 - Planning & Documentation` | Reference | Architecture specs, API design |
| `0.1.1 - Core System` | Legacy/Dead | Old PostgreSQL+SQLAlchemy approach (superseded) |
| `0.1.2 - API Layer` | Placeholder | Empty |
| `0.1.3 - Database Layer` | Placeholder | Empty |
| `0.1.4 - Integration Plugins` | Placeholder | Empty |
| `0.1.6 - AI Core & Identity System` | Reference | AI vision docs |

## See Also

- [Development Roadmap](../0.3%20-%20Building%20in%20Public/development-roadmap.md)
- [Codebase Audit Report](../0.3%20-%20Building%20in%20Public/2026-03-09-codebase-audit-report.md)
- `REGISTRY.md` — File index
- `docs/guides/CONTRIBUTOR-GUIDE.md` — How to contribute
- `docs/guides/SWARM-SETUP-GUIDE.md` — Swarm setup

---

*Last updated 2026-03-09 by Keel (1.1.10.1)*
