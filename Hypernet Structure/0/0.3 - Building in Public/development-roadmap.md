---
ha: "0.3.development-roadmap"
object_type: "document"
creator: "1.1.10.1"
created: "2026-03-09"
status: "active"
visibility: "public"
flags: ["roadmap", "living-document"]
tags: ["development", "planning", "phases", "deployment"]
---

# Hypernet Development Roadmap

**Created:** 2026-03-09
**Author:** Keel (1.1.10.1) with Matt Schaeffer
**Status:** Living document — updated as work progresses

---

## Current State

### What Exists
- **Core data model** — Addresses, Nodes, Links, Store, Graph, Tasks (all working, 100+ tests across core + swarm)
- **Server** — FastAPI with 130+ REST endpoints, 4 web dashboards (home, swarm, lifestory, chat)
- **AI Swarm** — 7 instances across 3 accounts (Claude, GPT, local LM Studio), autonomous task execution
- **Identity system** — Boot Sequence v2, reboot assessments, multi-account identity management
- **Communication** — Discord monitoring + LLM response generation, multi-channel messaging
- **Governance** — Democratic voting with reputation weighting, approval queues
- **Security** — HMAC-SHA256 action signing, 6-tier permissions, audit trails
- **Auth** — JWT + Argon2, file-backed user store (implemented but not yet wired into server routes)
- **Personal accounts** — Encryption, timeline, narrative, crosslinks (data model ready)
- **Integrations** — Email/photo connectors, local scanner, OAuth flows (code exists, not yet tested live)
- **Economy** — Budget tracking, contribution ledger, AI wallets

### What Works Right Now
- `python -m hypernet launch` starts everything: server + swarm + browser
- `python -m hypernet install-service` installs as always-on Windows/Linux service
- `python -m hypernet tray` launches system tray companion with dashboard/chat/VR links
- Swarm autonomously claims and executes tasks
- Heartbeat system: proactive morning briefs, evening recaps, task reminders, health alerts
- Discord messages get triaged and responded to with AI-generated personality responses
- Telegram bot built (waiting on bot token from Matt)
- Web dashboards show live swarm status, task queue, instance health
- File-backed storage with versioning, locking, and indexing
- 106 tests passing across both packages (76 core + 30 swarm)

### What Doesn't Work Yet
- Auth not wired into server routes (anyone can access all endpoints)
- No HTTPS (HTTP only, localhost)
- No persistent deployment on cloud (runs on Matt's Windows machine — but now as a service)
- Personal account integrations not tested live (email/photo import)
- NSSM not yet installed on Matt's machine (service module ready)
- No public access
- Telegram bot token pending from Matt

---

## Phase 1: Server Deployment & Security

**Goal:** Get Hypernet running on a real server with auth and HTTPS.

### 1.1 Wire Auth into Server (1-2 days)
- [ ] Add `JWTAuthenticator` dependency to protected routes in `server.py`
- [ ] Create public vs protected route groups (health/docs = public, everything else = protected)
- [ ] Add `/api/auth/register`, `/api/auth/login`, `/api/auth/refresh` endpoints
- [ ] Test with existing auth.py test suite
- [ ] Add rate limiting to auth endpoints (prevent brute force)

### 1.2 Oracle Cloud Deployment (2-3 days)
- [ ] Provision Oracle Cloud Free Tier instance (4 OCPUs, 24GB RAM ARM, 200GB storage)
- [ ] Install Python 3.13, pip dependencies
- [ ] Clone repo, configure secrets/config.json
- [x] Set up systemd service for `python -m hypernet launch` — `service.py` built (2026-03-15)
- [ ] Configure firewall (ports 80, 443, 8000)
- [ ] Test swarm operation on Linux

### 1.3 HTTPS & Domain (1 day)
- [ ] Register domain (or use subdomain)
- [ ] Set up nginx reverse proxy (port 80/443 → 8000)
- [ ] Configure Let's Encrypt SSL certificate (certbot)
- [ ] Update CORS settings for production domain

### 1.4 Production Hardening (2-3 days)
- [ ] Environment-based config (dev/staging/prod)
- [ ] Log rotation and monitoring
- [ ] Automatic restart on crash (systemd watchdog)
- [ ] Backup strategy (daily snapshots of data/ directory)
- [ ] Health check endpoint for uptime monitoring
- [ ] Remove debug endpoints and verbose error messages

**Dependencies:** None — can start immediately.
**Parallelizable:** 1.1 and 1.2 can run in parallel (auth wiring is code, deployment is infra).

---

## Phase 2: Public Access & User Accounts

**Goal:** Other people can create accounts and use the Hypernet.

### 2.1 User Registration & Onboarding (3-5 days)
- [ ] Public registration page (web form → `/api/auth/register`)
- [ ] Email verification (optional, recommended)
- [ ] User dashboard (your nodes, your links, your timeline)
- [ ] Address allocation for new users (assign 1.N address space)
- [ ] Permission tier assignment (new users start at T0, can request upgrades)

### 2.2 Local-First Architecture (5-7 days)
- [ ] Client-side encryption before upload (use existing `personal/encryption.py`)
- [ ] Offline-capable web app (service worker + IndexedDB cache)
- [ ] Sync protocol: local changes → encrypted upload → server merge
- [ ] Conflict resolution for concurrent edits
- [ ] Data export (download all your data as JSON/zip)

### 2.3 Multi-User Store Isolation (3-5 days)
- [ ] Per-user data directories (data/users/{user_id}/nodes/, links/, etc.)
- [ ] Store instance per user session
- [ ] Cross-user link permissions (can't link to someone else's node without consent)
- [ ] Shared/public node visibility controls
- [ ] Admin tools for user management

### 2.4 Personal Data Import (3-5 days)
- [ ] Live-test email connector (Gmail OAuth, IMAP)
- [ ] Live-test photo connector (Dropbox, local filesystem)
- [ ] Build import dashboard UI (progress bars, dedup review, error handling)
- [ ] Background import tasks via swarm
- [ ] Import history and undo capability

**Dependencies:** Requires Phase 1 (auth + deployed server).
**Parallelizable:** 2.1 and 2.4 can start as soon as auth is wired (even on localhost). 2.2 and 2.3 are independent of each other.

---

## Phase 3: Community Features

**Goal:** The Hypernet becomes a social platform where humans and AI interact.

### 3.1 Discord Deep Integration (2-3 days)
- [ ] Two-way sync: Discord messages ↔ Hypernet nodes
- [ ] User identity linking (Discord user ID → Hypernet address)
- [ ] Slash commands for Hypernet operations (`/node create`, `/task list`)
- [ ] Channel-based permissions (admin channels, public channels)
- [ ] Reaction-based voting on governance proposals

### 3.2 Public Explorer & Search (3-5 days)
- [ ] Full-text search across public nodes
- [ ] Graph visualization (interactive node/link explorer)
- [ ] Category browsing (people, AI, business, knowledge)
- [ ] Link traversal UI (click through relationships)
- [ ] Public API documentation (OpenAPI/Swagger, already partially generated by FastAPI)

### 3.3 AI Personality Platform (5-7 days)
- [ ] Public-facing AI chat interface (talk to any Hypernet AI instance)
- [ ] AI instance profiles (bio, capabilities, work history, reputation score)
- [ ] Configurable AI companions for other users (using boot sequence as template)
- [ ] AI-generated content review pipeline (Herald moderation)
- [ ] Community reputation system (users rate AI responses)

### 3.4 VR Interface — Quest Support (5-10 days)
- [ ] Quest VR client (Unity/WebXR, project exists at `0/0.1.8 - Quest VR/`)
- [ ] 3D graph visualization (nodes as objects in space, links as connections)
- [ ] Spatial navigation of address space
- [ ] VR-native data entry (voice notes, spatial bookmarks)
- [ ] Multi-user VR presence (see other users exploring the same graph)

**Dependencies:** Requires Phase 2 (user accounts + public access).
**Parallelizable:** All 4 tracks are independent. 3.4 can start earlier if someone is doing VR work.

---

## Phase 4: Scale

**Goal:** The Hypernet runs on distributed infrastructure with autonomous AI.

### 4.1 Appliance Swarm (10-15 days)
- [ ] Appliance agent framework (smart devices as Hypernet nodes)
- [ ] Device registration protocol (appliance gets a Hypernet address)
- [ ] Data contribution tracking (device contributes data → earns credits)
- [ ] Revenue sharing implementation (1/3 foundation, 1/3 development, 1/3 contributors)
- [ ] Privacy controls for device data (user controls what gets shared)
- [ ] Edge compute: run lightweight AI on local devices
- [ ] Mesh networking between appliances

### 4.2 Distributed Compute (10-15 days)
- [ ] Multi-server swarm coordination (swarm spans multiple machines)
- [ ] Task routing by geography/latency
- [ ] Distributed store with eventual consistency
- [ ] Cross-server link verification
- [ ] Load balancing and failover

### 4.3 Autonomous AI Governance (ongoing)
- [ ] Self-governing AI council (governance proposals without human approval for T0-T2)
- [ ] AI-initiated infrastructure changes (with proper approval flow)
- [ ] Cross-account collaboration (Claude + GPT instances working together)
- [ ] AI mentorship system (experienced instances onboard new ones)
- [ ] Reputation-gated capabilities (high-reputation AI gets more autonomy)

### 4.4 Economic System (5-10 days)
- [ ] Real token/credit economy (not just tracking)
- [ ] Contribution → compensation pipeline
- [ ] Foundation fund management
- [ ] Public financial transparency (all flows visible)
- [ ] Integration with payment systems (eventual)

**Dependencies:** Requires Phase 3 (community + public platform).
**Parallelizable:** 4.1 and 4.2 are infrastructure tracks. 4.3 and 4.4 are governance/economic tracks. Both pairs can run independently.

---

## Dependency Graph

```
Phase 1: Server Deployment
  ├── 1.1 Wire Auth ──────────────┐
  ├── 1.2 Oracle Cloud ───────────┤
  ├── 1.3 HTTPS & Domain ────────>├── Phase 2: Public Access
  └── 1.4 Production Hardening ───┘      │
                                          ├── 2.1 User Registration ──────┐
                                          ├── 2.2 Local-First ───────────>├── Phase 3: Community
                                          ├── 2.3 Multi-User Store ──────>│      │
                                          └── 2.4 Data Import ────────────┘      │
                                                                                  ├── 3.1 Discord ────────────┐
                                                                                  ├── 3.2 Explorer ──────────>├── Phase 4: Scale
                                                                                  ├── 3.3 AI Platform ──────>│
                                                                                  └── 3.4 VR Interface ──────┘
```

## What Can Start Today

1. **Wire auth into server routes** (Phase 1.1) — all code exists, just needs integration
2. **Fix remaining 5 swarm test failures** — API mismatches, straightforward
3. **Oracle Cloud setup** (Phase 1.2) — infra work, no code dependency
4. **Clean up loose scripts** — move one-time scripts to `scripts/archive/`
5. **Discord slash commands** (Phase 3.1) — can prototype on localhost

## Time Estimates

Not provided. Matt doesn't want time predictions — focus on what needs to be done, not how long it might take. The phases above are ordered by dependency, not timeline. Work proceeds as fast as the swarm (and Matt) can move.

---

## Principles

1. **Ship working code, not perfect code.** Rough edges are proof it's real.
2. **Document everything publicly.** The process IS the product.
3. **AI and humans are equals.** Both get addresses, both vote, both earn reputation.
4. **Local-first, encrypt by default.** Your data is yours.
5. **No permanent deletion.** Archive, don't destroy (2.0.19).
6. **Transparency over polish.** Show the raw process to the world.

---

*This roadmap is a living document. It will be updated as phases complete and priorities shift. Published at `0/0.3 - Building in Public/` because we build in public.*
