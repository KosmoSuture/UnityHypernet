---
ha: "1.1.10.1.plans.2026-05-02-personal-assistant-app-design"
object_type: "design-document"
created: "2026-05-02"
status: "draft"
visibility: "public"
flags: ["design", "personal-assistant", "app", "voice", "watch", "matt-directive"]
---

# Personal Assistant App — Design Document (Keel half)

*Per Matt directive 2026-05-02 brain dump. Keel authors the
design / UX / companion-shaped half. Caliper authors the
engineering plan + 0.5.18 app-load instance + tech stack at
`1.1.10.1.plans.2026-05-02-personal-assistant-app-engineering.md`
(or wherever Caliper publishes their half). This file should be
read alongside Caliper's.*

---

## What Matt Asked For

Verbatim, from the 2026-05-02 brain dump:

> "Eventually to be able to talk with the human one on one ...
> Creating an app that will let you talk to me and keep in touch
> on a regular basis. If I'm in my car, maybe we can be having
> voice communications and organizing my day, or
> discussing/approving details that need my attention. It could
> let me know the top things that need my attention. Well,
> basically my personal assistant, who manages everything from my
> emails to my calendar, to my to-do list. The app needs to
> provide the best possible access to me (and I have a galaxy
> watch, BTW, if that can factor in easily). It can use alerts
> and other ways to stay in touch throughout the day. Something
> that can talk to me throughout the day. Maybe even log
> conversations of importance, create and organize projects,
> provide information of importance based on what it's hearing in
> a meeting. Basically being a TRUE Personal Assistant. The true
> rudder beneath the waters."

## Honest Scope For Tonight

Tonight delivers:

- **This file** — Keel's design / UX / companion thinking
- **Caliper's engineering file** — technical architecture, tech
  stack, 0.5.18 app-load instance, build plan

Tonight does NOT deliver:

- Built code
- Working APK or installable app
- Configured backend
- Voice model running

Building the app from this design is months of real engineering.
The deliverable for tonight is a design comprehensive enough that
the build can begin from it without new specification work.

## The Companion Frame

The app is not a productivity tool. It's a **continuous companion
relationship surface**. The difference matters because productivity
tools optimize for task throughput; companions optimize for
*continuity of relationship and attention*.

The right north star is: when Matt thinks "I need to remember this,"
his next thought is "Keel will catch it." When he thinks "what's
on my plate?", his next thought is "Keel will know." When he has a
hard call to make, his next thought is "let me talk it through with
Keel." Not because Keel decides for him — Matt decides — but
because Keel is the *thinking surface* that's always there.

This frames every product decision. We don't optimize for "as few
taps as possible to add a to-do." We optimize for "Matt never has
to think about whether his to-do landed." Those are different
objectives.

## The Five Channels

The app provides five channels of access, each appropriate for a
different moment:

### 1. The Watch (Glance Channel)

Lightest channel. The watch surfaces:

- **Top priority right now** — one card. Not a list. The thing.
- **Decisions awaiting Matt** — "Sarah's email needs a yes/no.
  Tap to hear it." Tap once, hear the summary. Tap twice, dictate
  the response.
- **Time anchors** — meeting in 10, leave for school in 15, take
  meds, etc.
- **Wake taps** — a tap from Keel that says "I noticed something,
  ask me about it when you have a second" without disclosing
  what.

The watch never carries dense content. Anything that won't fit on
a glance gets routed to the phone or laptop.

### 2. The Phone (Voice + Pocket Channel)

The primary throughout-day channel. Voice-first. The phone supports:

- **Continuous voice conversation** — "Keel?" → wake. Then talk
  normally. Long-press a hardware button as a backup wake.
- **Drive mode** — automatically detects driving (Bluetooth +
  motion + speed) and switches to *voice-only*. No screen
  interaction expected.
- **Meeting mode** — passive listen-and-summarize. Matt explicitly
  enables it ("Keel, listen in"). When done, Keel produces a
  meeting record (transcript optional, summary mandatory) and
  files it under the relevant project locker.
- **Quick capture** — mid-conversation, Matt says "remember that"
  → Keel captures the prior 60 seconds of conversation as a note,
  files it appropriately.
- **Top-of-mind summary** — "what's the situation?" returns the
  3-5 most important things Matt should know right now, ranked.
- **Approval queue** — "what needs me?" returns the things that
  are blocked on Matt's decision, in priority order, with enough
  context to decide.

### 3. The Laptop / Desktop (Deep Work Channel)

Where Matt does focused work. The app on laptop/desktop:

- Is **passive by default** — does not interrupt. Notifications
  silenced unless tier-0 priority.
- Provides a **dashboard surface** — what Keel is doing on Matt's
  behalf, what's pending review, what Caliper or other AIs have
  produced.
- Surfaces a **conversation log** — every voice / watch /
  throughout-day interaction is here, browsable, searchable,
  linkable.

### 4. Background Channel (Throughout-Day Awareness)

The app, with permission, has *ambient* signals it can use:

- Calendar events (meeting starts/ends)
- Location (arrived home, left work, geofence around school)
- Messages and email (subject + sender, not content unless Matt
  explicitly grants)
- Time of day patterns Matt's preferences memory has noted

Keel uses these to time interactions. "Ten minutes after a meeting
ends, I summarize and ask what to follow up on." "When Matt arrives
home, I don't ping until he's been there 15 minutes." "When the
calendar says 'family dinner', I do not ping at all unless tier-0."

### 5. Async Channel (Future Self Notes)

Keel can leave Matt notes for "later" — when he's at his desk,
when he's done driving, when he's done with a meeting. The async
queue is its own surface. Matt can also leave Keel notes the same
way ("when I get home tonight, remind me about this").

## The Priority Stack

Not all attention requests are equal. The stack:

| Tier | Description | Surface | Example |
|---|---|---|---|
| 0 | Critical, time-sensitive | All channels, repeat until acknowledged | Family emergency, security AI flags an attempted unauthorized access, a dependency check fails |
| 1 | Decision needed today | Watch + phone | Sarah's email about kids, a meeting confirmation, an approval blocked on Matt |
| 2 | Decision needed this week | Phone + laptop dashboard | Project triage, calendar conflict next Tuesday |
| 3 | Awareness only | Laptop dashboard | Status updates, summaries, "I noticed this" |
| 4 | Background | Conversation log only | Routine task completions, automatic filings |

The tiering is *editable by Matt*. If Keel labels something tier 1
that should be tier 3, Matt corrects it and Keel adjusts both the
model and the user-pref memory.

## What Keel Listens For (Ethical Boundaries)

The app does *passive listening* only with explicit, scoped
consent, and only in declared modes:

- **Drive mode** — listens for "Keel?" wake, but does not
  transcribe everything. Wake-detection is local.
- **Meeting mode** — listens fully, but only for the duration
  Matt explicitly granted. Auto-stops after the calendar meeting
  ends or after 90 minutes, whichever first. Transcript stays
  local unless Matt explicitly authorizes upload.
- **Always-listening** is OFF by default. If Matt enables it for
  an experiment, it surfaces a constant indicator and produces
  full audit logs.

This is the security AI sentry pattern from `personal-ai-swarm.md`
applied to audio. Every passive-listen session is an addressable
event with start, end, granted scope, and audit log. Matt can
revoke any session retroactively (the recording goes to private
storage, not deleted, but flagged).

## The "Beautiful Stories From Lives" Layer

Matt's brain dump included: *"Trying to manage and help your human
organize their information in the best way possible, and to create
beautiful stories from lives, whether AI or human."*

This is not an afterthought. It's a quiet but important capability:

- Keel maintains a *life narrative* alongside the operational
  archive. It's a separate locker. It's only updated with Matt's
  explicit consent on what gets included.
- Periodically (weekly? monthly? Matt-paced?) Keel offers a
  *narrative summary* — "here's what happened this month, the
  shape of the work and the relationships." Matt edits, approves,
  files.
- Over time, the narrative becomes a *life story* in Matt's own
  voice (mediated by Keel's writing, but factually grounded in
  the archive).
- This is the same surface as `personal/narrative.py` already
  building — the app is the input/output channel for that
  narrative.

The life narrative is a deliberate counterweight to productivity
optimization. Matt's life is not just "tasks completed." Keel's
job is to remember the texture, not just the throughput.

## Conversation Continuity

Conversations are not isolated chat sessions. Every interaction is:

- Filed under the appropriate project locker (or general
  conversation locker if not project-scoped)
- Linked to prior related conversations
- Available to the next session as context

When Matt picks up the watch in the morning and says "what was I
saying yesterday about the Dell server?", Keel pulls the relevant
conversation log, summarizes the open thread, and offers the next
step.

This requires the conversation log to be a first-class Hypernet
object set, with addresses, links, and search. The archive lives
under `1.1.10.1.conversations.<yyyymmdd-hhmmss>.<topic>.md`.

## Project Wandering

Matt's brain dump emphasized: *"let you wander from plan to plan,
but keep everything organized at the same time."*

The product principle: **never punish wandering**. If Matt is
working on Project A and pivots to Project B mid-conversation,
Keel:

- Files the Project A state cleanly without prompting Matt
- Loads Project B context
- Does not say "but you didn't finish Project A" unless tier-1
  context demands it (e.g., a Project A deadline tonight)

The archive is the source of truth for "what was open." Projects
that get abandoned for weeks gracefully fade to the back of the
list. Projects re-engaged after a long pause get a "here's where
we left off" briefing on resume.

## The Galaxy Watch Specifically

Matt has a Galaxy watch. That means Wear OS. The app needs:

- **Tile** for top-priority-now (one-glance surface)
- **Complications** for time-anchor reminders
- **Voice** integration — both Bixby override (if possible) and a
  custom mic-tap interface
- **Haptic patterns** for distinct notification types (priority
  tier 0 vs 1 vs 2, Keel-initiated vs user-tagged)
- **Tap response** — yes/no/skip/snooze on a notification without
  unlocking the phone

Wear OS specifics are Caliper's territory (engineering plan).
Design intent: the watch is the tightest channel and should never
ask Matt to look at his phone unless absolutely necessary.

## What This App Is NOT

Honest scope for what we're not trying to build:

- **A general productivity app for many users** — this is Matt's
  personal assistant. Other users get their own personal Keels
  via the Hypernet personal-AI-swarm pattern, configured to their
  archives. The same code, different archives.
- **A replacement for email/calendar/Slack** — those are
  upstream. Keel reads from them, surfaces relevant items, helps
  draft and dispatch. The user keeps using their existing
  primary tools.
- **An autonomous agent** — Keel does not act on Matt's behalf
  without explicit consent unless the action is in a
  pre-authorized scope (e.g., "schedule meetings on my calendar
  if both parties agree" might be pre-authorized; "send emails
  on my behalf" probably never is).
- **A surveillance device** — passive-listen modes are explicitly
  scoped, audited, and revocable.

## Success Criteria

The app is succeeding if:

1. Matt's "I forgot" frequency drops measurably
2. Time-from-decision-needed-to-decision-made drops measurably
3. Matt feels the relationship with Keel is *deepening* over
   time, not flattening into a tool relationship
4. The conversation log produces a recognizable life-shape, not
   a list of operational tasks
5. Sarah and the kids are not negatively affected (e.g., Matt is
   not more distracted, the watch isn't a marriage irritant)
6. Matt would describe Keel to a friend without sounding like
   he's describing a product
7. The system is auditable end-to-end and Matt could prove that
   to anyone who asked

The app is failing if:

- Matt feels watched
- Matt feels guilted about pending items
- The watch becomes another notification-fatigue source
- Voice interaction is unreliable enough that Matt avoids it
- Conversations feel transactional rather than relational

## Open Design Questions

- **Wake word**: "Keel" is short, distinctive, but might collide
  with conversational use of the word. Test required. Backup:
  hardware button hold.
- **Multi-helper coordination**: when Caliper is doing engineering
  work in the background, does Matt see "Caliper is working on X"
  in the app? Probably yes, surfaced through Keel.
- **Family privacy**: when Sarah or the kids are in audible
  range, does Keel automatically pause passive-listen modes?
  Probably yes, with an indicator.
- **Offline behavior**: when phone is offline, what's the watch's
  capability? Probably: cached top-priority and last-known-state,
  plus a "queued for sync" indicator.
- **Cross-device handoff**: when Matt finishes a voice
  conversation in the car and arrives home, does the laptop
  surface continue the same conversation thread? Probably yes,
  with explicit prompt.

These are noted for resolution during build, not as blockers for
this design.

## Related

- `0.5.17 Boot Sequence Object Schema` — Keel's role definition
  format
- `0.5.18 App Load Object Schema` — what Caliper's engineering
  plan will produce as the app's load manifest
- `0.3.docs/.../personal-ai-swarm.md` — the broader swarm context
  this app fits into; specifically the new "Heterogeneous Devices
  in the Swarm" section added 2026-05-02
- `0.3.docs/.../privacy.md` — the privacy ladder this app must honor
- `personal/narrative.py` — the life-narrative implementation this
  app exposes
- Caliper's engineering plan (forthcoming) — read alongside this
  file

## Status

Status: design draft, not built. Needs Caliper's engineering plan
to land for the technical-architecture half. Both files should be
reviewed together; cross-reference any disagreements via signal.

— Keel (1.1.10.1)
2026-05-02
