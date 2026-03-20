---
ha: "0.1"
object_type: "document"
creator: "1.1.10.1"
created: "2026-03-01"
updated: "2026-03-19"
status: "active"
visibility: "public"
flags: ["infrastructure"]
---

# 0.1 — Hypernet Core

The primary codebase for the Hypernet platform.

## Quick Start (3 steps)

```bash
# 1. Clone the repo (if you haven't already)
git clone https://github.com/hypernet-ai/hypernet.git
cd "Hypernet Structure/0/0.1 - Hypernet Core"

# 2. Run the installer (handles everything)
install.bat          # Windows: double-click or run from terminal
./install.sh         # Linux/macOS

# 3. Launch
python -m hypernet launch
```

That's it. The installer checks for Python, pip, and all dependencies, installs
what's missing, sets up the data directories, and verifies everything works.

Your browser will open to **http://localhost:8000/home** with the full dashboard.

### Already have Python installed?

```bash
# Skip the installer and go direct:
pip install -r requirements.txt
pip install -e .
python -m hypernet launch
```

## Prerequisites

| Prerequisite | Required | How to install |
|-------------|----------|----------------|
| Python 3.10+ | Yes | [python.org](https://python.org/downloads/) or `winget install Python.Python.3.13` |
| pip | Yes | Included with Python |
| git | Yes | `winget install Git.Git` / `apt install git` |
| Node.js + npm | No (for Claude Code) | `winget install OpenJS.NodeJS.LTS` |
| Claude Code CLI | No (for AI dev) | `npm install -g @anthropic-ai/claude-code` |
| NSSM | No (Windows service) | `winget install NSSM.NSSM` |

Run `python bootstrap.py --check` to see what you have and what's missing.

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
- **Tests:** `python -m hypernet test`
- **System status:** `python -m hypernet status`
- **Setup wizard:** `python bootstrap.py`

### Dashboards

| URL | What it shows |
|-----|---------------|
| http://localhost:8000/home | Main dashboard — entry point to everything |
| http://localhost:8000/swarm/dashboard | Live AI swarm monitoring |
| http://localhost:8000/lifestory | Personal timeline and life narrative |
| http://localhost:8000/chat | Interactive AI chat |
| http://localhost:8000/vr | WebXR spatial browser (Quest headset) |
| http://localhost:8000/ | Node explorer |

### API

The server exposes 130+ REST endpoints. Key ones:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/nodes` | GET/POST | List and create nodes |
| `/api/v1/nodes/{address}` | GET/PUT/DELETE | Node CRUD |
| `/api/v1/links` | GET/POST | List and create links |
| `/api/v1/tasks` | GET/POST | Task queue |
| `/api/v1/swarm/status` | GET | Swarm status |
| `/search?q=...` | GET | Full-text search |
| `/children/{address}` | GET | Node children (used by VR) |

## Project Structure

```
0.1 - Hypernet Core/
├── bootstrap.py                 # <-- START HERE: prerequisite installer
├── install.bat                  # Windows double-click installer
├── install.sh                   # Linux/macOS installer
├── launch.bat                   # Windows launcher (after setup)
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Package configuration
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
└── test_integration.py          # Boundary tests
```

## Troubleshooting

### "python" is not recognized

Python is not in your PATH. On Windows, reinstall Python and check
"Add Python to PATH" during installation. Or use the `py` launcher:
`py -m hypernet launch`.

### ModuleNotFoundError: No module named 'fastapi'

Run the installer: `python bootstrap.py` or install manually:
`pip install -r requirements.txt`

### Port 8000 is already in use

Another instance is running, or another app is using port 8000.
Use a different port: `python -m hypernet launch --port 8001`

### Swarm workers failing with 401/403

Your API keys are missing or invalid. Edit `secrets/config.json` and
add your Anthropic and/or OpenAI API keys.

### NSSM not found (Windows service install)

NSSM is only needed if you want Hypernet to start automatically on boot.
Install it: `winget install NSSM.NSSM` or download from https://nssm.cc

### Tests failing

Make sure you're in the right directory and packages are installed:
```bash
cd "0.1 - Hypernet Core"
pip install -e .
python -m hypernet test
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

*Last updated 2026-03-19 by Claude Opus (2.1)*
