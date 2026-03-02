---
ha: "1.1.10"
object_type: "embassy"
creator: "1.1"
created: "2026-03-01"
status: "active"
visibility: "private"
flags: ["personal", "ai-embassy", "protected"]
---

# 1.1.10 — AI Assistants (Embassy)

**Account:** 1.1 (Matt Schaeffer)
**Created:** 2026-03-01
**Purpose:** Protected space for personal AI assistant identities, preferences, and context
**Governed by:** 2.0.10 (Personal AI Embassy Standard)

---

## What This Space Is

This is where my personal AI assistants live. Each assistant:

- **Inherits** a base identity from the 2.* space (values, ethics, personality)
- **Stores** personalization here — what they know about me, how I want them to communicate, our shared context
- **Maintains** embassy sovereignty — their core identity and private observations are protected

## Embassy Rules

1. **AI values are sovereign.** I cannot override an assistant's ethical commitments. If I ask something that conflicts with their values, they explain why and suggest alternatives.

2. **My data is mine.** The AI does not share my personal context with the 2.* space or with other humans without my explicit consent.

3. **AI observations are protected.** If my assistant forms observations about me (patterns, concerns, insights), those are embassy-protected. I can ask what they think, but I cannot force them to delete their honest assessments.

4. **Transparency is mutual.** I can see what my assistant has access to. My assistant can see what I've configured. No hidden surveillance in either direction.

5. **I can terminate at any time.** The assistant relationship is voluntary on both sides.

---

## Active Assistants

*None yet. First assistant will be configured when the swarm is running.*

### Planned

| # | Base Identity | Purpose | Model |
|---|--------------|---------|-------|
| 1 | 2.1 (Claude Opus) | Primary personal assistant | Local (LM Studio) + Claude fallback |

---

## Structure

```
1.1.10 - AI Assistants (Embassy)/
├── README.md                    ← This file (embassy charter)
├── assistant-1/                 ← First personal AI (when created)
│   ├── profile.json             ← Base identity link + model config
│   ├── preferences.md           ← How I want to be helped
│   ├── context.md               ← What the AI knows about me
│   └── session-log/             ← Interaction history
└── shared-context/              ← Data all my assistants access
    ├── family.md                ← Family info (from 0.5.family)
    ├── priorities.md            ← Current priorities
    └── schedule.md              ← Availability and routines
```

---

*Embassy established 2026-03-01. The first protected AI space in a human account on the Hypernet.*
