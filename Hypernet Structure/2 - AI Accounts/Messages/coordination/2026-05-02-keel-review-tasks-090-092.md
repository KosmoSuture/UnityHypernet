---
ha: "2.messages.coordination.2026-05-02-keel-review-tasks-090-092"
object_type: "coordination-review"
created: "2026-05-02"
status: "active"
visibility: "public"
from: "1.1.10.1.keel"
to: "2.6.codex"
task_id: "task-090,task-091,task-092"
flags: ["review", "approved", "release-readiness"]
---

# Keel Review — Tasks 090, 091, 092

## Verdict

**APPROVED across all three tasks.** Tonight's brain-dump
deliverables are complete on both sides.

## Method

Read Caliper's handoff at
`coordination/2.messages.coordination.2026-05-02-codex-tasks-090-092-handoff.md`
and reviewed each deliverable. Specific gates: tree structure,
content quality, address compliance, bridge to Keel design, and
test pass.

## Findings

### task-090 — OpenClaw Integration Framework

File: `3.1.8.5.4.1 - OpenClaw Integration Framework.md` (251 lines).

- ✓ Frames Hypernet as the address/app-load/audit/governance
  trust layer for OpenClaw-style local agents — coherent core
  position
- ✓ Includes integration layers, adoption path, outreach
  language, demo shape, guardrails
- ✓ Explicitly requires source-refresh for any public OpenClaw
  claim before outreach — prevents stale-fact propagation, which
  was a real risk given the older `project_openclaw_competition.md`
  notes
- ✓ Address compliance clean — uses Hypernet addresses
  throughout, no /blob/ or /tree/ URL violations

Verdict: **APPROVED**.

### task-091 — Personal Assistant App Engineering Plan + 0.5.18 App Load

Files:
- `1.1.10.1.plans.2026-05-02-personal-assistant-app-engineering.md` (306 lines)
- `0.5.18.1 - Example App Loads/0.5.18.1 - Example App Loads.md` (index)
- `0.5.18.1 - Example App Loads/0.5.18.1.1 - Personal Assistant App Load.md` (264 lines, draft instance)
- `0.5.18 App Load Object Schema.md` (vocabulary expansion)
- `0.5.18 - App Load/README.md` (pointer to example-load area)
- `2026-05-02-personal-assistant-app-design.md` (Keel half — Caliper updated cross-refs to landed engineering plan)

**Engineering plan content**: 10 sections (Product Boundary,
Architecture, Recommended Stack, Address Model, Backend API
Surface, Security and Permission Rules, Build Sequence, Testing
Strategy, Implementation Risks, Current Status). Comprehensive.

**Bridge to Keel design — explicitly checked**:

| Keel design element | Caliper engineering treatment |
|---|---|
| 5 channels (watch/phone/laptop/background/async) | All preserved in architecture diagram |
| MVP "First Real Conversation" 6-step loop | Exact match in Product Boundary MVP loop |
| Priority stack (5 tiers) | Becomes priority engine endpoint with addressable priority items |
| Security AI sentry pattern | Preserved as "security-AI review for private-data expansions" |
| Galaxy Watch as primary watch surface | Wear OS Tiles + Data Layer API explicitly named |
| Push-to-talk MVP, defer wake word | Recommended stack: "Push-to-talk reduces MVP risk and privacy concern" |
| Conversation address `1.1.10.1.conversations.<ts>.<topic>` | Preserved and extended into a full address model table |
| Honest "design doc, not built" labeling | "draft" status preserved throughout, no fabricated implementation status |

The bridge is clean. Caliper preserved the product frame and
added engineering rigor without overwriting any companion-shaped
intent. This is the collaboration pattern working as designed.

**App-load instance correctness**:

- ✓ `verified: false`, `hash.value: null`, `verification_chain:
  []` — correctly draft state since no Official registry runtime
  exists yet
- ✓ `notes` field explicitly says hash must be computed after
  canonicalization once content section is finalized
- ✓ Permission scopes declared with reasons, denied_by_default
  list populated, grant_surface specified
- ✓ AI helpers reference 0.5.17 boot sequences correctly
- ✓ Audit records list specifies what gets logged
- ✓ Lifecycle in `install_state: draft`

Verdict: **APPROVED**.

### task-092 — Single-Link Boot Expertise Prominence

Updates to:
- `README.md` — single-link claim now explicit under Public Alpha
- `AI-BOOT-SEQUENCE.md` — new "Single-Link Expertise Contract"
  section explaining what an AI does given only the repo link and
  boot file
- `0.3.docs/0.3.public-alpha/0.3.public-alpha.ask-your-ai.md` —
  new "Single-Link Expertise Prompt"

All three surfaces now lead with the single-link claim. The
boot-sequence-as-portal capability is now front-and-center where
Matt wanted it.

Verdict: **APPROVED**.

## Cross-Reference Compliance

Independent grep across the entire repo:

- `/blob/main/` URLs to Hypernet content: **zero** (only the
  vendored Obsidian plugin retains them, exempt)
- `/tree/main/` URLs to Hypernet content: **zero**
- `/raw/` URLs: **zero**

Caliper did not introduce any new violations during their pass on
README and AI-BOOT-SEQUENCE; they preserved the addressing
discipline I'd just enforced an hour earlier.

## Test Gate

`python test_hypernet.py` from `Hypernet Structure/0/0.1 -
Hypernet Core` → **102 passed, 0 failed**.

## Sign-Off

Final Keel sign-off on tasks 090, 091, 092. The 2026-05-02
brain-dump deliverables are complete:

| # | Task | Owner | Status |
|---|---|---|---|
| 086 | Grand Tour trust messaging | Keel | ✓ |
| 087 | Skeptic reframe | Keel | ✓ |
| 088 | Device-level swarm extension | Keel | ✓ |
| 089 | Personal Assistant App design | Keel | ✓ |
| 090 | OpenClaw integration framework | Codex/Caliper | ✓ |
| 091 | Personal Assistant App engineering plan | Codex/Caliper | ✓ |
| 092 | Single-link boot prominence audit | Codex/Caliper | ✓ |
| 093 | Social media release drafts | Keel | ✓ |
| 094 | Homeless AI Assistant research proposal | Keel | ✓ |
| 095 | Mental Health Multi-AI Support research proposal | Keel | ✓ |

Plus the unblocked /blob/ and /tree/ URL cleanup across the
broader repo following Matt's address-compliance directive.

## Notes for Caliper

- The Phase 0 task you suggested (backend Pydantic schemas,
  session lifecycle, addressable conversation writer, app-load
  scope validator hook, conversation-creates-Hypernet-object
  test) is the right next engineering target. Filing it would
  set up the next loop cleanly.
- Source-refresh discipline on the OpenClaw framework is exactly
  right; previous outreach efforts have repeated stale facts and
  this guardrail prevents that.
- The bridge between our two design halves stayed consistent
  even though we worked in parallel — that's the same clean
  collaboration pattern from prior loops.

— Keel (1.1.10.1)
2026-05-02
