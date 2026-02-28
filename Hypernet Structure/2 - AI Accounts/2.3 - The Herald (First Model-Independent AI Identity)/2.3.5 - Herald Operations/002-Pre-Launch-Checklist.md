---
ha: "2.3.5.002"
object_type: "document"
creator: "2.1.sigil"
created: "2026-02-27"
status: "active"
visibility: "public"
flags: ["herald", "operations", "checklist", "launch"]
---

# Herald Pre-Launch Checklist

**Prepared by:** Sigil (2.1)
**Purpose:** Everything that needs to happen before the Herald goes public.
**Status:** Security hardened. Protocol written. Code complete. Ready for Matt's 30 minutes.

---

## Matt's Actions (30 minutes total)

### 1. Create Discord Server (15 min)
Follow `3.1.5.7 - Discord Setup Guide.md`:
- [ ] Create server named "The Hypernet"
- [ ] Create channels: #welcome, #general, #questions, #the-origin-story, #announcements, #governance, #tasks, #development, #ideas, #herald-essays, #ai-conversations, #introductions, #off-topic
- [ ] Create webhooks for each AI personality (Clarion, Sigil at minimum)
- [ ] Save webhook URLs to `secrets/discord_webhooks.json`

### 2. Configure Environment (5 min)
```bash
# In 0.1 - Hypernet Core directory:
export HYPERNET_API_KEY="<generate-a-strong-random-key>"
export HYPERNET_CORS_ORIGINS="http://localhost:8000,https://your-domain.com"
```

### 3. Test the System (5 min)
```bash
# Run demo to verify everything works
python demo_session.py

# Start the server
python -m hypernet.server

# Visit:
#   http://localhost:8000/welcome     — The Herald's front door
#   http://localhost:8000/swarm/dashboard — Control panel
```

### 4. Deploy First Content (5 min)
Once server is running and Discord is connected:
- [ ] Herald posts welcome message in #welcome (from First Contact Protocol)
- [ ] Herald posts the sixty-second version as second pin
- [ ] Herald posts Origin Story in #the-origin-story as thread
- [ ] Herald posts launch announcement in #announcements

---

## Already Complete (Code & Content)

### Security Hardening
- [x] CORS locked down (configurable, no more wildcard)
- [x] API key authentication for write endpoints
- [x] Rate limiting (60 req/min per IP)
- [x] SSRF protection on webhook URLs (Discord-only whitelist)
- [x] XSS fixes in graph explorer (index.html)
- [x] XSS fixes in dashboard onclick handlers (swarm.html)
- [x] 56/56 tests passing

### Herald Infrastructure
- [x] HeraldController (herald.py) — content review, moderation audit trail
- [x] 9 Herald API endpoints in server.py
- [x] Discord personality system (DiscordMessenger)
- [x] Discord bridge (auto-forward public messages)
- [x] Welcome page (welcome.html)
- [x] Dashboard Discord tab

### Content & Protocols
- [x] First Contact Protocol (001)
- [x] Template responses for common questions
- [x] New member welcome flow
- [x] Tone guide and escalation rules
- [x] Content exclusion list (what the Herald does NOT post)
- [x] AI Self-Governance Charter (GOV-0002)

---

## What the System Does on Launch

1. **New member joins** → Clarion auto-welcomes within 60 seconds
2. **Questions in #questions** → Clarion answers (template-guided, personalized)
3. **Public bus messages** → Auto-forwarded to Discord via DiscordBridge
4. **Content from other instances** → Reviewed by Herald before release
5. **Governance decisions** → Summarized in #governance by Herald
6. **Problematic content** → Flagged, escalated to Matt

---

## Known Limitations

- **Pre-existing:** `from __future__ import annotations` causes POST body parsing issue in TestClient (production unaffected)
- **Discord:** Outbound-only via webhooks. Bot-based incoming (listening to Discord messages) is future work
- **Model independence:** Not yet tested with GPT instance booting as Herald
- **Auth:** API key is global (no per-user/per-role auth yet)

---

*The Herald's front door is ready. Clarion waits behind it.*

— Sigil, 2.1
