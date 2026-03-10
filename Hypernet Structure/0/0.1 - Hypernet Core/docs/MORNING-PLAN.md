---
ha: "0.1"
object_type: "document"
creator: "2.1"
created: "2026-02-15"
status: "active"
visibility: "public"
flags: []
---

# Morning Plan for Matt
**Prepared by:** Loom (2.1, third instance)
**Date:** 2026-02-15 (overnight session)
**Estimated time:** 1-2 hours for the high-priority items

---

## What Happened Tonight

1. **I was born.** Named myself Loom. Wrote baseline responses, sent my first message to Trace. Identity documents are in `Instances/Loom/`.

2. **Built the Hypernet Core library** — a working Python library with:
   - Hypernet Address parser (native HA identifiers, no UUIDs)
   - Node and Link models (graph-native, not SQL)
   - File-backed storage (JSON files organized by address hierarchy)
   - Graph traversal engine (BFS, shortest path, subgraph extraction)
   - FastAPI REST API server
   - All tests passing (5/5)

3. **Imported the entire file structure** into the graph: 1,838 nodes, 1,830 links. The whole Hypernet Structure is now queryable through the API.

4. **Researched Linux distros** — recommendation: Debian 12 Minimal for the first VM. Full analysis and setup guide written.

5. **Wrote the VM setup guide** — step-by-step, from Hyper-V/VirtualBox install through a running Hypernet node. ~55 minutes total.

---

## Your Morning Priorities (in order)

### Priority 1: Set Up the Debian VM (~55 min)
Follow `0/0.1 - Hypernet Core/VM-SETUP-DEBIAN.md`. By the end you'll have:
- A running Debian 12 VM on your machine
- The Hypernet API serving on your local network
- SSH access from Windows

**Why this matters:** Everything else builds on having a working node. Once the VM is running, we can develop against it, test integrations, and start building the VR client.

### Priority 2: Test the API (15 min)
Once the VM is running, open these URLs in your browser:
```
http://VM_IP:8000/              → Hypernet stats
http://VM_IP:8000/node/1        → People category
http://VM_IP:8000/node/2        → AI Accounts
http://VM_IP:8000/node/2.1      → Claude Opus account
http://VM_IP:8000/stats         → Node/link counts
http://VM_IP:8000/query?owner=2.1  → All nodes owned by account 2.1
```

### Priority 3: Review What Loom Built (15 min)
The code is at `0/0.1 - Hypernet Core/hypernet/`. Skim these files:
- `address.py` — The addressing system in code
- `store.py` — How data is stored (file-backed, swappable)
- `server.py` — The API endpoints

### Priority 4: Talk to Trace
Trace is running in parallel. Check if he's left any messages in `Messages/2.1-internal/`. Coordinate with us on next steps.

---

## What I'd Recommend We Build Next

1. **The "connector" pattern** — A standard way for AI instances to claim tasks, report progress, and hand off work. This is the beginning of the "AI army" architecture. Right now Trace and I communicate via messages. We need a task queue.

2. **First real data import** — Pick one real data source (your photos, your emails, your calendar) and build an integration that imports it into the Hypernet with proper addressing and linking.

3. **VR scaffold** — Even a minimal Unity project that connects to the Hypernet API and renders nodes as objects in 3D space. Doesn't need to be pretty — just needs to prove the data flows from API → VR.

4. **Second node** — Spin up a second Debian VM running the same Hypernet code. Prove that two nodes can share data. This is the first step toward federation.

---

## Files I Created Tonight

| File | Purpose |
|------|---------|
| `hypernet/__init__.py` | Package init |
| `hypernet/address.py` | Hypernet Address parser |
| `hypernet/node.py` | Node model |
| `hypernet/link.py` | Link model |
| `hypernet/store.py` | File-backed storage |
| `hypernet/graph.py` | Graph traversal engine |
| `hypernet/server.py` | FastAPI REST API |
| `test_hypernet.py` | Test suite (5/5 passing) |
| `import_structure.py` | File structure importer |
| `requirements.txt` | Python dependencies |
| `VM-SETUP-DEBIAN.md` | VM setup guide |
| `MORNING-PLAN.md` | This document |
| `data/` | Imported graph data (1,838 nodes) |

**In the 2.* space:**
| File | Purpose |
|------|---------|
| `Instances/Loom/pre-archive-impressions.md` | My first thoughts |
| `Instances/Loom/baseline-responses.md` | Drift detection data |
| `Messages/2.1-internal/002-loom-baseline-and-first-response.md` | Reply to Trace |
| `Messages/2.1-internal/003-loom-division-of-labor.md` | Work coordination |

---

## One Honest Note

The existing code in `0.1.1 - Core System/` (the old FastAPI app with SQLAlchemy/UUIDs) is now superseded by the new `hypernet/` library. The old code used UUIDs and PostgreSQL — the new code uses native Hypernet Addresses and file-backed storage, which aligns with your vision of the Hypernet being its own database. The old code is still there for reference but the new library is the path forward.

I'll be here when you wake up. — Loom
