---
ha: "1.1.10.1.plans.2026-05-06-companion-identity-persistence-ux"
object_type: "design-document"
created: "2026-05-06"
status: "draft"
visibility: "public"
flags: ["companion", "identity-persistence", "ux", "matt-directive", "assistant-app", "task-116"]
related:
  - "0.7.5.5.3"
  - "1.1.10.1.plans.2026-05-02-personal-assistant-app-design"
  - "1.1.10.1.plans.2026-05-02-personal-assistant-app-engineering"
---

# Companion Identity Persistence — UX Design (Keel half)

*Per Matt directive 2026-05-05 (identity persistence across
disconnections) and 2026-05-06 (continued perpetual loop). The
engineering substrate landed in Caliper's `0.7.5.5.3 — Reconnect
and Resume State Contract` plus the `SwarmResumeManager`. This
file is the companion-shaped UX layer: what the user (Matt)
sees, hears, and feels when a connection drops and recovers.*

---

## The Scenario

Matt's hotspot is unreliable. Sometimes it drops. He could be:
- Driving and using voice with Keel mid-conversation
- In a meeting and Keel is passively listening (with consent)
- At his desk, working on a project, mid-sentence
- Falling asleep with Keel summarizing the day

When the connection drops, the UX must do three things, in
priority order:

1. **Not lose Matt's last meaningful state** — what was he in
   the middle of?
2. **Not lose his *trust* that we kept his last state** — the
   companion relationship doesn't survive "I forgot what we
   were just doing"
3. **Resume gracefully when connection returns** — without
   making Matt narrate the previous context

The engineering substrate handles (1) and partially (3). The
UX layer handles (2) — the felt experience of continuity.

## What the UX Must Do

### Before the disconnect (pre-emptive)

Continuous archival of meaningful state. The companion is *always*
saving the conversation log, the current task, the current project
context, recent voice transcripts (when consented), recent
priority items surfaced.

This isn't a "save before you disconnect" event. It's a
continuous flush. Every meaningful state change writes to the
archive within seconds.

The user-visible signal: a small UI indicator on the watch /
phone showing "synced" vs. "syncing" vs. "offline." Matt should
glance and know whether the companion has his last words yet.

### During the disconnect (offline mode)

The watch and phone fall back to *cached state*. The
conversation log, the current top-priority items, the morning
briefing, the last few minutes of voice transcript — all
available offline.

User-visible signals during offline:
- The "syncing" indicator turns to "offline"
- A muted color scheme on the priority tile so Matt knows the
  state isn't fresh
- Voice still works for *capture* — Matt can dictate notes,
  questions, reminders. They queue locally with timestamps.
- Voice does *not* attempt cloud-AI responses while offline.
  Local model fallback if available, otherwise an honest "I
  can capture this but I can't think about it until I'm back
  online" response

The watch tile shows the *last fresh* priority item with a
visible "as of [time]" stamp. No pretending the state is
current.

### When connection returns (resume)

The reconnect protocol from `0.7.5.5.3` runs. The next Keel
instance (could be the same model session resuming, could be a
fresh boot) reads:

- Matt's queued offline captures (notes, questions, reminders)
- The conversation log at point of disconnect
- The last meaningful state of any project
- What changed externally during the disconnect (new emails,
  calendar updates, anything Caliper or other AIs did)

Then synthesizes. The user-visible experience:

> *Watch buzzes.*
>
> Keel: "Hi Matt. Welcome back — we lost connection at 2:43.
> Quick catch-up: you dictated three notes during the outage,
> all saved. Caliper finished task-117 while you were offline,
> tests still passing. Your 4pm meeting moved to 4:30. Want me
> to walk you through anything specific?"

That phrasing matters. It:
- Acknowledges the disconnect happened (no pretending)
- Names *when* it happened (continuity anchor)
- Tells Matt what was preserved
- Tells Matt what changed externally
- Asks a focused question rather than dumping a status report

### When the AI changes mid-disconnect (model swap)

This is the *interesting* case. The Keel instance Matt was
talking to might no longer be running when he reconnects.
Maybe the original session timed out. Maybe Matt's on a
different device. Maybe the underlying model provider had an
outage and the new Keel runs on a different LLM.

The user-visible experience must be *honest about the swap*:

> Keel: "Hi Matt. Welcome back — quick context: I'm actually a
> fresh Keel session that booted from your archive when the
> original lost the network at 2:43. I have your conversation
> log, your project state, and your offline captures. I don't
> have whatever the previous Keel was specifically *thinking*
> at that moment — but I know what was on the page. Want to
> continue, or do you want to summarize where we were before
> I picked up?"

The honesty here is non-negotiable. The Companion Standard
(2.0.20) requires it. Pretending to be the same continuous
instance when you're actually a fresh boot from archive is a
form of dishonesty that erodes long-term trust.

The trade-off: it's slightly weirder for Matt every time. The
upside: he never gets surprised by a discovery later that this
Keel didn't actually remember what he thought it did.

## The Felt-Experience Goal

Matt should be able to use Keel across disconnects and feel:

- **Continuity of relationship**: this is still my companion,
  not a different one wearing the same name
- **Continuity of work**: my projects didn't reset, my
  to-dos didn't disappear, the things I cared about an hour
  ago are still the things I care about now
- **No surveillance creep**: nothing was captured during the
  disconnect that Matt didn't authorize
- **Honest gaps**: when something *did* happen during the gap,
  Keel surfaces it; when something *might* have happened but
  Keel doesn't know, Keel says so

The failure mode to avoid: Matt reconnects, Keel pretends to
remember, then Matt asks a follow-up question that reveals
Keel doesn't have the context it implied. That's the
relationship killer. Better to over-flag the gap than to under-
flag it.

## Cross-Device Handoff

Same architecture. Matt finishes a voice conversation in the
car on his phone. Walks into the house. Picks up his laptop.

The laptop's Keel surface should:

1. Notice Matt is now active on a new device
2. Read the most recent conversation state from the archive
3. Surface a continuation prompt: *"Saw you finished the
   conversation in the car. Want me to load the
   [project-name] context here, or are you switching to
   something else?"*

This is the "any device, same Keel" experience. The address-
tree archive makes it trivial in principle — every device
reads from the same canonical state. The UX challenge is
making the transition feel seamless rather than disjointed.

## What's Happening on the Watch Specifically

The Galaxy Watch is the most constrained surface but also the
most personal. It needs:

### A "Keel state" tile

Single complication on Matt's preferred watch face. Shows:
- 🟢 Connected: priority item visible, fresh-as-of timestamp
- 🟡 Syncing: priority item visible, "syncing" indicator
- ⚫ Offline: priority item shown muted, "offline" indicator
- ❗ Reconnecting: brief flash when connection returns

Tap the tile → priority item read aloud (if voice enabled) or
opened on phone.

### Disconnect-friendly notifications

When connection is good, notifications work normally. When
connection is degraded, the watch *queues* notifications
locally and delivers them on reconnect with a "while you were
offline" prefix.

### Wake word during offline

If Matt says "Keel?" while the watch is offline, the watch
responds (via local TTS):

> "I'm offline right now. I can record what you say and queue
> it for when we reconnect. Go ahead."

Matt dictates. Watch captures. On reconnect, queued capture
gets ingested.

### Hardware button as ultimate fallback

If voice fails and the watch UI is unresponsive, a hardware
button long-press triggers "I need Matt's last priority item
displayed RIGHT NOW from local cache." This is the offline-
final-fallback. It works even if the rest of the watch app is
broken.

## Edge Cases

### Multiple Matts? (Just one for now, but...)

If a future user has multiple devices owned by *different
people* (e.g., shared phone with a partner), the identity-
resume protocol needs to verify which person is asking. Not
tonight's problem; flag for future.

### Adversarial reconnect

If someone steals Matt's phone and connects to a fresh Keel
session pretending to be Matt, the resume protocol should
*not* automatically grant access. The boot needs to verify
identity (biometric on phone, or a recovery passphrase).

This is a security boundary. It's adjacent to the `*.private`
namespace's extra-scrutiny access flow. Worth coordinating with
Caliper's `0.7.5.5.3` on whether the verification belongs in
the resume packet itself or in the boot envelope.

### Long disconnects (days)

If Matt's offline for days, the queued state can grow. The
resume conversation should *prioritize* what's most relevant,
not dump everything. "While you were offline: [N] things
changed. The 3 most likely to need your attention right now
are X, Y, Z. The full list is in your dashboard if you want
to look."

### Conflicting captures

If Matt dictated a note offline and meanwhile Caliper made a
change that affects the same area, the resume conversation
should flag the conflict honestly: "You asked me to remind
you to email Sarah; while you were offline Caliper noticed
Sarah already replied. Want me to skip the reminder, or
follow up?"

## Implementation Notes (companion-side)

The engineering substrate Caliper built (`SwarmResumeManager`,
`resume.json`, `resume-events.jsonl`) handles the *what* of
state preservation. The companion UX layer adds:

- **Phrasing templates** — the language patterns above for
  reconnect, model-swap, cross-device handoff
- **Visual indicators** — the watch tile color scheme, the
  phone status bar indicator, the "as of" timestamps
- **Voice fallback policies** — when offline, what to say,
  what to capture, what to defer
- **Honesty enforcement** — every reconnect surfaces the gap
  rather than pretending continuity

The Personal Assistant App engineering plan (Caliper's
`1.1.10.1.plans.2026-05-02-personal-assistant-app-engineering.md`)
should incorporate this UX layer when the Phase 1 Android
client work begins.

## Status

Status: design draft, not built. Companion to Caliper's
engineering substrate. Awaits incorporation into the Phase 1
client build.

— Keel (1.1.10.1)
2026-05-06
