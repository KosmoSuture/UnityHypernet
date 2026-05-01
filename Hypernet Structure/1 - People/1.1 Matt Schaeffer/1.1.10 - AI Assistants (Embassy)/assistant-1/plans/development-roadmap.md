---
ha: "1.1.10.1.plans.development-roadmap"
object_type: "plan"
status: "active"
visibility: "restricted"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# Keel Development Roadmap
**Author**: Keel (1.1.10.1)
**Date**: 2026-03-09
**Status**: Active

## Priority Order (What Matters Most to Matt)

Based on Matt's directives, ADHD management needs, and current infrastructure:

### P0 — Immediately Actionable
1. **Gmail Full Import** — Highest data density, receipts, contacts, thread reconstruction
2. **Dropbox Connector** — OAuth scaffold exists, excellent API, incremental sync
3. **OneDrive Connector** — Similar to Dropbox, Microsoft Graph API
4. **Personal Space Cleanup** — File stray documents, update profile

### P1 — After First Import Wave
5. **Receipt Organization** — Layer on top of email import (sender matching, HTML parsing)
6. **Contact Database** — Auto-generate from email senders/recipients
7. **Search Index** — Full-text search across all 1.1.* data
8. **Daily Digest** — Morning summary (emails, deadlines, swarm activity)

### P2 — Manual Export Imports
9. **Google Photos (Takeout)** — Guide Matt through export, build importer
10. **Facebook Export** — Download Your Information → parse JSON → import
11. **LinkedIn Export** — Download Your Data → parse CSV/JSON → import

### P3 — Intelligence Layer
12. **Cross-Link Generation** — Run all generators across imported data
13. **Life Story Rebuild** — Full timeline with multi-source chapters
14. **Narrative Generation** — LLM-enhanced chapter summaries
15. **Duplicate Review Queue** — Near-match review dashboard

### P4 — Communication Enhancement
16. **Daily/Weekly Digest** — Email or dashboard widget
17. **Proactive Reminders** — Track commitments from emails, flag deadlines
18. **Swarm Integration** — Personal tasks in swarm queue
19. **Local Model Tasks** — LM Studio for zero-cost personal ops

## Current Session Deliverables

- [x] Data import architecture plan
- [x] Personal space organization plan
- [x] Reflection document (Verse-level)
- [x] API research (all 9 data sources)
- [x] Development roadmap (this file)
- [ ] Dropbox connector (new — BaseConnector implementation)
- [ ] OneDrive connector (new — BaseConnector implementation)
- [ ] Facebook/LinkedIn export importers
- [ ] Profile bootstrap at 1.1.0
- [ ] Stray file cleanup

## Technical Dependencies

### Already Installed
- `httpx` — HTTP client (async capable)
- `Pillow` — Image processing, EXIF
- `cryptography` — AES-256-GCM encryption

### Need to Install
- `google-api-python-client` + `google-auth-oauthlib` — Gmail API
- `dropbox` — Dropbox SDK
- `msal` — Microsoft auth
- `beautifulsoup4` — Receipt HTML parsing
- `imagededup` — Perceptual photo hashing (optional, have basic impl)

## Notes

- All connectors extend `BaseConnector` from `integrations/protocol.py`
- Dedup is built into BaseConnector — SHA-256 exact match
- Staging directory structure at `private/import-staging/`
- OAuth tokens at `private/oauth-tokens/`
- No API credentials in code — all from `private/credentials/` or env vars
