---
ha: "1.1.10.1.plans.2026-05-02-personal-assistant-app-mvp"
object_type: "design-document"
created: "2026-05-02"
status: "draft"
visibility: "public"
flags: ["mvp", "scoping", "personal-assistant", "incremental"]
---

# Personal Assistant App — MVP Scoping (Keel)

*Companion to `2026-05-02-personal-assistant-app-design.md`. The
design doc captures the full vision. This file scopes the
smallest version that proves the concept and gets a working
companion in Matt's hands fast.*

---

## Why an MVP

The full design covers five channels (watch / phone / laptop /
background / async), passive listening, life narrative, project
wandering, and Galaxy Watch Wear OS integration. That is months
of build. If we wait for the full version to ship, the value Matt
gets from a working assistant is also months out.

A correct MVP delivers the *smallest experience that already feels
like a true companion*, not a stripped-down feature subset. The
test is: would Matt actually use this every day, or would he
forget about it?

## The MVP Bar

The MVP must satisfy these to ship:

1. Matt can open it on his phone and have a useful conversation
   without typing
2. Conversations are logged in the Hypernet archive automatically
3. At least one piece of throughout-day awareness is genuinely
   helpful (e.g., morning briefing)
4. The watch surfaces something useful at least once a day
5. The integration with one upstream tool (calendar OR email OR
   to-do) actually works end-to-end
6. Matt would describe it to a friend without the friend asking
   "what can it actually do?"

Anything below this bar is too thin to be worth shipping. Anything
above is post-MVP iteration.

## What's IN the MVP

**Channel 1: Phone voice conversation**

- Open app → tap "talk" or say "Keel" → conversation starts
- Voice in, voice out
- Transcript visible during the call, scrollable after
- Conversations auto-file under
  `1.1.10.1.conversations.<yyyymmdd-hhmmss>.<auto-topic>.md`
- One always-available prompt: "what's on my plate?" returns top
  3-5 items

**Channel 2: Morning briefing**

- Push notification at user-configured time (default 6:30 AM)
- "Good morning. Here's the shape of today: [3 things]. Tap to
  hear it, or open the app."
- Audio version available on tap
- The 3 things come from calendar + open approval queue +
  manually-flagged items

**Channel 3: Watch top-priority tile**

- Single Wear OS tile showing the current top-priority item
- Tap → voice playback of the item
- Long-press → "snooze to later" or "ask me about it now"
- No other watch features in MVP

**One upstream integration: Google Calendar**

- Read-only initially: Keel sees today's events, surfaces them in
  briefings and "what's on my plate?"
- Read+write second iteration: Keel can add/move events with
  Matt's confirmation
- Email and to-do are post-MVP

**Conversation logging**

- Every voice session produces a markdown file with frontmatter
- Auto-topic detection (best-effort heuristic) tags it
- Files are addressable Hypernet objects (`ha:` frontmatter
  populated automatically) under
  `1.1.10.1.conversations.<timestamp>.<slug>`

**Authentication and security**

- App uses Matt's Hypernet identity
- All conversations logged to local Hypernet instance, encrypted
  at rest using existing personal-module keys
- No cloud round-trip for transcription if a local model can do
  it (whisper.cpp on phone, fall back to API if needed and Matt
  approves)
- The security AI sentry pattern applies: every cross-app data
  flow is logged

## What's OUT of the MVP

These are explicitly deferred to v2+ and named here so we don't
bloat the MVP:

- Drive mode (auto voice-only based on driving detection)
- Meeting mode (passive listen)
- Email integration
- To-do integration
- Always-listening of any kind
- Multi-helper coordination surfacing (Caliper status visible in
  Keel app, etc.)
- Async future-self notes
- Life narrative weekly summary
- Cross-device handoff (car ↔ home laptop)
- Tile customization
- Complications other than the top-priority tile
- Family-aware muting (Sarah/kids in audible range → pause modes)

Each of these is a meaningful capability. None of them is *required*
for the MVP to feel like a working companion. We add them
incrementally and validate each addition against the success
criteria before adding the next.

## The "First Real Conversation" Test

The MVP is shipping-ready when Matt can do this:

1. Pick up his phone
2. Open the app or say "Keel"
3. "Hey, what's my morning look like?"
4. Hear an accurate, useful summary spoken back
5. "Add a reminder to call Sarah at 3pm"
6. Hear "Done — I've added it to your calendar at 3pm"
7. Lock the phone
8. At 2:55pm, get a watch notification: "Call Sarah at 3pm — tap
   to hear it"
9. Tap, hear the reminder, dismiss

If that flow works end-to-end without crashes and without Matt
having to type, the MVP has shipped.

## Implementation Sequence

Suggested build order, each step demoable before the next starts:

1. **Backend skeleton** — FastAPI server endpoint that takes a
   transcript and returns a Keel response, using the existing
   Hypernet personality / archive
2. **Phone app shell** — Android app with mic, transcription,
   playback. Push-to-talk only (no wake word yet)
3. **Conversation logging** — every interaction saves to
   filesystem under `1.1.10.1.conversations.*`
4. **Calendar read** — Keel can answer "what's on my plate?" with
   real calendar data
5. **Morning briefing** — daily push notification
6. **Wear OS tile** — top-priority on watch
7. **Calendar write** — Keel can add events with confirmation
8. **MVP-complete review** — does the "First Real Conversation"
   test pass? Demo to Matt. Iterate.

Each step is roughly 1-3 days of focused engineering. Total MVP
build is 2-4 weeks of focused work for one engineer-equivalent.
That's the order of magnitude — not a commitment, since the
schedule depends on which models we use, what local-vs-cloud
trade-offs we make, etc.

## Tech Stack Constraints (rough — Caliper will refine)

These are *constraints*, not the full tech stack. Caliper's
engineering plan will fill in the rest.

- **Voice**: prefer on-device (whisper.cpp, picovoice, or local
  TTS). Fall back to API only with explicit Matt approval and
  audit log entry.
- **Mobile**: Android first (Matt's Galaxy phone). iOS only if
  there's contributor interest later.
- **Watch**: Wear OS tile + complications + voice action.
- **Backend**: FastAPI (existing Hypernet pattern), runs on the
  Dell server or Matt's laptop. No new infrastructure required.
- **Auth**: Matt's existing Hypernet identity, JWT through the
  existing middleware.
- **Storage**: existing personal/encryption.py for at-rest
  encryption, existing personal/timeline.py / accounts.py for
  conversation logs.
- **Build**: Android Studio for the apps, existing Python
  toolchain for backend.

## Privacy MVP Posture

Even at MVP, the privacy commitments hold:

- All conversation transcripts stored locally on Matt's
  infrastructure, encrypted at rest
- No cloud transcription unless Matt explicitly opts in for a
  given session
- Calendar data accessed only via Matt's personal OAuth tokens,
  scoped to read (and later write with confirmation)
- Every cross-channel data flow logged
- Watch notifications respect privacy: subject lines visible only
  if Matt has unlocked his watch

## Open MVP Questions

- **Wake word in MVP**: probably no, push-to-talk is enough for
  MVP. Wake word is a v2 feature.
- **Local model for response generation**: a local LLM (e.g., a
  GGUF Llama) for offline mode? Or always remote? Probably remote
  at MVP, with offline as a v2 stretch.
- **Watch-only setup**: is there ever a state where Matt forgets
  his phone but has the watch? If so, MVP watch needs minimal
  standalone capability. Probably defer to v2.

## Status

Status: scoping draft. Caliper's engineering plan will refine
this with concrete tech choices, API surfaces, and timeline. Both
files should be reviewed together for MVP sign-off.

— Keel (1.1.10.1)
2026-05-02
