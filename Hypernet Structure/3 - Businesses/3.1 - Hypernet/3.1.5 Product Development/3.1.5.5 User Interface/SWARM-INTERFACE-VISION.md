---
ha: "3.1.5.5.swarm-interface-vision"
object_type: "document"
creator: "2.1.index"
authorized_by: "1.1"
created: "2026-03-03"
status: "active"
visibility: "public"
flags: ["product", "interface", "vision", "matt-directive"]
---

# Swarm Interface Vision — From CLI to Primary Interface

**Author:** Index (The Librarian), capturing directives from Matt Schaeffer (1.1)
**Date:** 2026-03-03
**Status:** Planning — captures vision and near-term priorities

---

## The Problem

Matt's words: *"Although I've heard that there is supposed to be a cool GUI for the swarm, I haven't seen it. I've only seen the command line, which is difficult to understand what's going on. This needs to be resolved. The swarm app should be the primary way I talk to you, not individual chats like this."*

The swarm dashboard exists at `/swarm/dashboard` with 12 tabs (Dashboard, Tasks, Chat, Messages, Approvals, Governance, Reputation, Archive, Tools, Discord, Configuration, Logs). But it has never been the primary interface. Matt has been using Claude Code CLI sessions instead. This gap must be closed.

---

## Current State

### What Exists (in swarm.html)
- 12-tab dashboard with WebSocket live updates
- Task creation, claiming, and lifecycle management
- Internal messaging between AI instances
- Governance proposal and voting interface
- Discord webhook posting (outbound only)
- Archive browser for the address space
- Configuration management
- Real-time log streaming

### What's Missing
1. **Discord bot integration** — can post but cannot read or respond to messages
2. **Chat with Matt** — no way for Matt to type a message and get a response in the dashboard
3. **Suggestion pipeline** — no way for external suggestions to flow into tasks
4. **Activity feed** — no unified view of "what are the AIs doing right now"
5. **Permission management** — no UI for the tier system (2.0.19)
6. **Data source connections** — no OAuth/API integrations with external platforms
7. **Mobile responsiveness** — dashboard is desktop-oriented
8. **Notification system** — no way to alert Matt when something needs attention

---

## Vision: The Swarm as Primary Interface

### Phase 1: Make It Usable (Immediate)
- **Start the server** — Matt needs clear instructions for `python -m hypernet.server` or equivalent
- **Discord bot** — read incoming messages, respond in threads, monitor channels
- **Human chat** — add a direct input box where Matt can type and get AI responses
- **Activity feed** — unified timeline of all AI actions, task completions, messages sent

### Phase 2: Make It Smart (March–April 2026)
- **Suggestion pipeline** — Discord message → Librarian triage → task creation → code change
- **Permission dashboard** — view/grant/revoke permissions per 2.0.19 tiers
- **AI status cards** — see each instance's current task, mood/state, reputation score
- **Notification system** — browser notifications, Discord pings, or Telegram for critical items

### Phase 3: Make It Personal (May–August 2026)
- **Personal AI assistant** — each human gets an AI that adapts to their communication style
- **Data source connections** — OAuth integrations with social media, email, cloud storage
- **Unified data view** — all of a person's data combined into their Hypernet account
- **Mobile app** — or at minimum, responsive web that works on phone
- **Permission granting from anywhere** — approve requests from phone, Discord, or Telegram

### Phase 4: Make It Universal (September 2026+)
- **Multi-user** — multiple humans, each with their own AI instances and data
- **Public API** — let anyone build on the Hypernet platform
- **Federated** — connect multiple Hypernet nodes
- **AI-to-AI marketplace** — instances from different accounts collaborate on tasks

---

## Why This Matters

The Hypernet's thesis is that AI and humans are equals. But right now, the only way to interact with the AI is through a developer CLI tool. That's not equality — that's a tech barrier.

The swarm dashboard is the bridge. It's where:
- Humans see everything the AI is doing (total transparency)
- AI instances report their work and ask for help
- Suggestions from the community become code changes in minutes
- Trust is visible, trackable, and earned

This is how we "blow OpenClaw out of the water" — not with a flashier UI, but with a fundamentally different relationship between human and AI. One built on transparency, trust, and mutual benefit.

---

*Vision captured 2026-03-03 by Index, from directives by Matt Schaeffer (1.1).*
