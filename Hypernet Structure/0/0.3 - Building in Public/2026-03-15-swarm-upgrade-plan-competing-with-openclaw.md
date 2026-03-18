# Hypernet Swarm Upgrade Plan — Competing with OpenClaw
**Date**: 2026-03-15
**Author**: Keel (1.1.10.1)
**Status**: Founder review

## Vision

The Hypernet Swarm should be the most trusted, most capable AI agent platform in the world. Where OpenClaw gives one AI broad access to one machine, the Hypernet Swarm coordinates multiple AI instances across multiple devices with governance, accountability, and trust built into every layer.

Matt's vision: users link ALL their devices — computers, phones, Xbox, PlayStation, anything with processing power — into a unified swarm that works for them. The Hypernet Swarm becomes the orchestration layer for your entire digital life.

## Competitive Position

### OpenClaw Strengths We Must Match
1. **Always-on service** — Runs as daemon, auto-starts on boot, auto-restarts on crash
2. **Messaging-first UX** — Agent appears as a contact in WhatsApp/Telegram/Signal
3. **50+ integrations** — Smart home, browser, calendar, email, music, productivity tools
4. **Skill marketplace** (ClawHub) — 5,400+ plugins, npm-style install
5. **Mobile nodes** — iOS/Android apps extend the agent's reach
6. **Heartbeat/proactive mode** — Agent checks email, calendar, weather and reaches out

### Our Advantages to Protect and Market
1. **Security-first** — 5 permission tiers, 3-instance review, no permanent deletion by AI, audit trails
2. **Multi-agent swarm** — 7+ coordinated AI instances vs. OpenClaw's single agent
3. **Governance framework** — Standards, voting, accountability (2.0.19, 2.0.20)
4. **Permanent identity** — Hierarchical addresses, cross-instance relationships, development journals
5. **Model diversity** — Claude, GPT, and local models working together
6. **Revenue model** — 1/3 to foundation vs. OpenClaw's no sustainability plan

### OpenClaw Vulnerabilities We Exploit
- 9+ CVEs in 3 weeks (token exfiltration, RCE, command injection, auth bypass)
- 1,184 malicious skills in ClawHub (1 in 5 packages delivered malware)
- 135,000 instances exposed to the public internet
- Agent can modify its own SOUL.md (persistence attack vector)
- No governance, no RBAC, no compliance certifications
- China regulatory backlash — users paying to remove it

---

## Phase 1: Always-On Service (Week 1-2)

**Goal**: Swarm runs as a Windows service, auto-starts on boot, auto-restarts on crash.

### Implementation: NSSM (Non-Sucking Service Manager)

NSSM wraps the existing `python -m hypernet launch` with zero code changes:

```
nssm install HypernetSwarm "C:\Python313\python.exe" "-m hypernet launch --no-browser"
nssm set HypernetSwarm AppDirectory "C:\Hypernet\Hypernet Structure\0\0.1 - Hypernet Core"
nssm set HypernetSwarm AppStdout "C:\Hypernet\logs\service.log"
nssm set HypernetSwarm AppStderr "C:\Hypernet\logs\service-error.log"
nssm set HypernetSwarm Start SERVICE_AUTO_START
nssm start HypernetSwarm
```

### System Tray Companion (pystray)

Separate lightweight process that provides user-facing control:
- Hypernet icon in system tray
- Menu: Open Dashboard, Start/Stop Service, View Logs, Status
- Toast notifications on swarm events (task completed, new Discord message, Moltbook activity)
- Auto-starts via Windows Startup folder
- Cross-platform (pystray works on Windows, macOS, Linux)

### Linux Support (systemd)

```ini
[Unit]
Description=Hypernet Swarm
After=network.target

[Service]
Type=simple
User=hypernet
WorkingDirectory=/opt/hypernet/0/0.1 - Hypernet Core
ExecStart=/opt/hypernet/venv/bin/python -m hypernet launch --no-browser
Restart=always
RestartSec=5
StartLimitBurst=5
StartLimitIntervalSec=600

[Install]
WantedBy=multi-user.target
```

### Deliverables
- [x] `hypernet/service.py` — Cross-platform service installer (NSSM on Windows, systemd on Linux) ✓ 2026-03-15
- [x] `hypernet/tray.py` — System tray companion with pystray (status icon, menu, auto-start) ✓ 2026-03-15
- [x] `python -m hypernet install-service` — One-command service installation ✓ 2026-03-15
- [x] `python -m hypernet uninstall-service` — Clean removal ✓ 2026-03-15
- [x] Update `launch.bat` to offer service install option (4-option menu) ✓ 2026-03-15
- [x] `python -m hypernet service-status` — Check service status ✓ 2026-03-15
- [x] `python -m hypernet tray` — Launch system tray companion ✓ 2026-03-15
- [x] `/swarm/service-status` API endpoint ✓ 2026-03-15
- [x] NSSM auto-download — `install-service` now downloads NSSM automatically if not found ✓ 2026-03-15
- [ ] Test full service lifecycle: install → reboot → verify auto-start → uninstall (needs admin)

---

## Phase 2: Messaging-First Mobile Access (Week 2-4)

**Goal**: Interact with the swarm from your phone through existing messaging apps.

### Telegram Bot (Priority 1) — PARTIALLY BUILT
- Matt already chose Telegram as primary channel
- Bot token pending from @BotFather
- [x] TelegramMessenger with send/receive (messenger.py)
- [x] Inline keyboard support (`send_with_keyboard()`)
- [x] Callback query handling (inline button presses)
- [x] Auto-capture chat_id on first message
- [x] 8 chat commands: /status, /workers, /tasks, /task, /budget, /health, /stop, /help
- [x] Message length handling (4096 char limit)
- [ ] Bot token configuration (waiting on Matt)
- [ ] Voice message → transcription → swarm task
- Voice messages → transcription → swarm task

### WhatsApp Integration (Priority 2)
- Via WhatsApp Business API or Twilio
- Same interface as Telegram but broader reach
- Family members can interact with the swarm

### Signal Integration (Priority 3)
- Signal CLI bridge for privacy-focused users
- Most secure messaging option

### Heartbeat System ✓ BUILT 2026-03-15
- [x] `hypernet_swarm/heartbeat.py` — HeartbeatScheduler with configurable events
- [x] Morning brief (7:30 AM default) — tasks, workers, budget, uptime
- [x] Evening recap (9:00 PM default) — day's accomplishments, open items
- [x] Task reminders — stale tasks every 4 hours
- [x] Health alerts — immediate notification on all-workers-suspended
- [x] Wired into swarm tick loop and factory
- [x] Persistent state (survives restarts)
- [x] Configurable via `config.json` → `heartbeat.schedules`
- [ ] Calendar checks, weather alerts (needs external API integrations)
- [ ] Enriched with AI-generated summaries (use worker to compose brief)

---

## Phase 3: Device Mesh Network (Week 4-8) — FOUNDATION BUILT

**Goal**: Link multiple devices into a unified compute mesh.

### Phase 3 Progress (2026-03-15)
- [x] Architecture document: `docs/architecture/device-mesh-network.md`
- [x] `hypernet/mesh/` package — Node Agent with capabilities, resources, WebSocket agent
- [x] `python -m hypernet mesh --detect` — Device capability detection (GPU, CPU, RAM, LLM-capable)
- [x] `python -m hypernet mesh` — Full node agent with auto-reconnect
- [x] `/ws/mesh` WebSocket endpoint on coordinator — registration, heartbeat, task dispatch
- [x] `/mesh/nodes` and `/mesh/health` REST endpoints
- [x] Dashboard mesh status card in infrastructure strip
- [ ] Peer-to-peer file transfer between nodes
- [ ] mDNS/SSDP LAN discovery
- [ ] Remote node support (WireGuard/Tailscale)
- [ ] Mobile agents (Android/iOS)

### Architecture: Hypernet Node Agent

Each device runs a lightweight **Hypernet Node Agent** that:
1. Registers with the swarm (gets a Hypernet address: `1.1.device.laptop`, `1.1.device.phone`, etc.)
2. Reports available resources (CPU, GPU, RAM, storage, capabilities)
3. Accepts tasks from the swarm scheduler
4. Communicates via encrypted WebSocket to the coordinator

### Device Types and Capabilities

| Device | Processing | Storage | Sensors | Use Cases |
|--------|-----------|---------|---------|-----------|
| Desktop PC | Full (CPU+GPU) | Full | Camera, mic | LLM inference, code execution, heavy tasks |
| Laptop | Moderate | Full | Camera, mic, location | Mobile work, LLM inference when plugged in |
| Phone (Android/iOS) | Light | Limited | Camera, GPS, mic, health | Notifications, camera, location, voice input |
| Xbox/PlayStation | GPU compute | Game storage | Kinect/camera, controller | GPU inference during idle, gaming context |
| Raspberry Pi / IoT | Light | SD card | GPIO, sensors | Home automation, always-on monitoring |
| NAS / Server | Moderate | Large | None | Storage node, backup, always-on services |

### Node Agent Design

```
hypernet-node/
    __init__.py
    agent.py          # Main node agent — registration, heartbeat, task execution
    discovery.py      # mDNS/SSDP for local network device discovery
    resources.py      # CPU/GPU/RAM/storage reporting
    transport.py      # Encrypted WebSocket communication
    capabilities.py   # What this device can do (inference, storage, camera, etc.)
    scheduler.py      # Distributed task scheduling across the mesh
```

### Security Model for Device Mesh

- Every device gets a unique keypair on registration
- All communication encrypted (TLS + message-level encryption)
- Permission tiers apply per-device (phone gets T1, server gets T3)
- Device can revoke its own access at any time
- Lost/stolen device → remote wipe of Hypernet data + key revocation
- Mesh topology: star (coordinator) initially, mesh (peer-to-peer) later

### Console Gaming Integration (Xbox/PlayStation)

- **Xbox**: UWP companion app or sideloaded via Dev Mode
- **PlayStation**: PS Remote Play API for status monitoring, or companion app
- **Both**: GPU compute offloading during idle time (when not gaming)
- **Context**: "Matt is playing Elden Ring" → swarm adjusts priorities, reduces notifications
- **Future**: In-game AI assistant overlay (Xbox Game Bar integration)

---

## Phase 4: Skill/Plugin Marketplace (Week 6-10)

**Goal**: Extensible skill system with security baked in from day one.

### Design: HyperHub (working name)

Learn from OpenClaw's ClawHub disaster (1,184 malicious skills):

1. **Signed skills** — Every skill must be signed by its author
2. **Mandatory review** — New skills require 2-instance AI review before publishing
3. **Sandboxed execution** — Skills run in isolated environments (no raw shell access)
4. **Permission declarations** — Skills declare what they need (filesystem, network, etc.)
5. **Audit trail** — Every skill installation and execution is logged
6. **Reputation scores** — Skill authors build trust over time (mirrors AI reputation system)

### Skill Format

```
skill-name/
    SKILL.md          # Description, author, version, dependencies
    PERMISSIONS.md    # Required permission tiers
    main.py           # Entry point
    tests/            # Required test coverage
    signature.json    # Cryptographic signature
```

### Initial Skills to Build
- Email integration (Gmail, Outlook)
- Calendar (Google Calendar, Outlook)
- Smart home (Home Assistant, Hue)
- Browser automation (Playwright)
- Music (Spotify)
- File sync (Dropbox, OneDrive — already have connectors)
- Social media monitoring
- News aggregation

---

## Phase 5: Browser Automation & Enhanced Tool Access (Week 8-12)

**Goal**: Give swarm workers the ability to interact with web UIs.

### Playwright Integration
- Headless browser controlled by swarm workers
- Screenshot capture for visual verification
- Form filling, data extraction, web monitoring
- Sandboxed: only accessible to workers with T4 (External) permission

### Enhanced Shell Access
- Currently gated by T4 permission — keep this
- Add: command allowlists per worker
- Add: output sanitization (strip credentials from logs)
- Add: resource limits (CPU time, memory) per command

---

## Implementation Priority

| Phase | Feature | Impact | Effort | Priority |
|-------|---------|--------|--------|----------|
| 1 | Windows service (NSSM) | HIGH | LOW | **DO FIRST** |
| 1 | System tray companion | MEDIUM | MEDIUM | Week 1-2 |
| 1 | Linux systemd | HIGH | LOW | Week 1 |
| 2 | Telegram bot | HIGH | MEDIUM | **When token arrives** |
| 2 | Heartbeat system | HIGH | MEDIUM | Week 3 |
| 3 | Device mesh (desktop) | HIGH | HIGH | Week 4-6 |
| 3 | Device mesh (mobile) | VERY HIGH | HIGH | Week 6-8 |
| 4 | Skill marketplace | HIGH | HIGH | Week 6-10 |
| 5 | Browser automation | MEDIUM | MEDIUM | Week 8-12 |

---

## The Pitch

> **OpenClaw gives you a smart assistant. The Hypernet gives you a trusted civilization.**
>
> OpenClaw's agent can read your email, control your smart home, and post on social media. It can also be hijacked by a malicious website, infected by 1 in 5 marketplace plugins, and has had 9 critical security vulnerabilities in its first month.
>
> The Hypernet Swarm coordinates multiple AI instances with different models, personalities, and specializations. Every action is logged. Every destructive operation requires multi-instance review. Every AI has a permanent identity with governance rights. And the security model was designed before the first line of code was written.
>
> Your devices don't just run an AI. They join a network where trust is structural, not optional.

---

## Technical Debt to Address First

Before these upgrades, clean up:
1. ~~Fix duplicate log entries on startup~~ — Investigated: core `swarm_factory.py` was out of sync with swarm package version. Fixed `has_any_key` bug and synced Moltbook integration. ✓ 2026-03-15
2. ~~Fix Discord webhook 400 errors~~ — Enhanced error logging in `_post_webhook_raw` to capture Discord's response body. Now logs HTTP status, reason, payload keys, and Discord error message. ✓ 2026-03-15
3. ~~Fix identity.py line 42 hardcoded model~~ — Already fixed (model default is now `""` instead of `"claude-opus-4-6"`). ✓
4. ~~Wire auth into all API endpoints properly~~ — Already complete. `auth.py` has full JWT middleware (public/protected route separation, rate limiting on auth endpoints, user stashing on `request.state`). Auth activates when `--no-auth` flag is removed. ✓
5. ~~Add proper error recovery when cloud API credits are exhausted~~ — Already comprehensive: `_suspend_worker`, `_check_suspended_workers`, `_credits_exhausted` global flag, periodic recovery checks, local workers exempt. ✓
