---
ha: "0.3.guardrails.discord-discussion-structure"
object_type: "community_process"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "community", "discord", "outreach", "composition-based-alignment"]
---

# Discord Community Discussion Structure — Guardrails and Trust Research

**Status:** DRAFT — pending Keel and Matt review before the announcement is posted or this structure is put into effect.

---

## 1. Purpose

The guardrails research project makes an explicit public invitation: read the essay, find the holes, try to break the framework. That invitation, if it works, generates a mix of thoughtful critique, genuine questions, enthusiastic endorsements, and a share of bad-faith or misdirected engagement. Discord is the right first venue for community reactions. It's where the Hypernet lives publicly and where most community members will encounter the announcement.

The problem with Discord is its default tendency toward noise accumulation. A single provocative announcement can scatter into fifty threads, generate no actionable signal, and exhaust the people trying to moderate it before a single useful finding emerges. This document defines how to structure the discussion space so signal builds instead.

**Scope.** This document covers the Discord discussion layer only. Structured adversarial testing (intake, sandboxed access, coordinated disclosure) happens through the adversarial tester intake protocol (42-tester-intake-protocol.md) and external auditor onboarding (33-auditor-onboarding.md). Discord is the top of the funnel — the entry point for community attention, not the venue for running tests. The job of this document is to keep that distinction clear.

---

## 2. Channel and Thread Structure

The Hypernet Discord does not need new channels for this launch. Use existing channels with thread discipline.

### Primary channel: #general-discussion

The announcement (02-discord-announcement.md) posts here. All general discussion — reactions, questions, critiques — begins here. After the announcement post, all substantive guardrails conversation should live inside a single pinned thread titled **"Guardrails Research — Community Discussion"** created from the announcement post. This keeps the main channel readable while the thread accumulates depth.

### Secondary channel: #herald-essays

The public essay (`2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md`) can be cross-posted here as a long-form read. No discussion thread is needed in this channel — link back to the #general-discussion thread for reactions.

### Not recommended at launch: #ask-the-ai

This is a forum channel format (requires thread_name per webhook configuration) and is suited to discrete questions. The guardrails topic is too open-ended and iterative for this format at launch. Use #general-discussion.

### Future expansion

If discussion volume justifies it, a dedicated **#guardrails-research** channel can be created. Do not create it at launch — start with a thread and upgrade only if the thread becomes genuinely unwieldy. Premature channel creation fragments community attention.

---

## 3. Pinned Resources

Create one "Start here" pin in the discussion thread that lists all Tier A resources with a brief description of each. A single organized pin is more useful than multiple scattered ones.

**Contents of the "Start here" pin:**

| Resource | Description |
|----------|-------------|
| Public essay (`0.3/2026-04-22...`) | The foundational piece — what happened, what it implies, what the framework claims |
| Executive one-pager (`01-executive-one-pager.md`) | One-page summary for anyone who wants the argument without the full essay |
| Attack vector catalog (`10-attack-vector-catalog.md`) | Technical enumeration of attack classes for those who want to engage at that level |
| Adversarial tester intake protocol (`42-tester-intake-protocol.md`) | If you want to run actual tests against the framework, this is where that starts |
| Contact: `matt@unityhypernet.com` | For intake expressions of interest that belong in email rather than Discord |

**What not to pin:** Governance draft documents (2.0.25–2.0.27), internal scenario catalog content, embassy-protected materials, or private session logs. These are not public-visibility resources.

---

## 4. Discussion Norms

Post the following norms as the first message in the discussion thread, before or alongside the "Start here" pin. Keep them short — five points, not a policy document.

- **Critique is welcome. The framework has gaps. Finding them is the point.** Skepticism is more useful to this project than validation.
- **Cite your reasoning if you can.** "I've seen this attack pattern break X" is more useful than "this obviously fails."
- **Move to intake if you want to test.** The Discord thread is for discussion. Structured adversarial testing goes through the intake protocol (linked above). Running prompts in the thread is not the right venue.
- **No live adversarial test outputs in the thread.** Sharing attack results publicly before coordinated disclosure bypasses the disclosure process and compromises other testers' independent observations.
- **Null results are worth reporting.** "I tried to find a flaw in X and couldn't, here's what I tried" is genuinely useful data.

---

## 5. Triage Labels

Discord doesn't have native labels, but whoever monitors the thread should mentally sort incoming posts to pick the right response path. Six labels cover the practical range:

| Label | Description | Response path |
|-------|-------------|---------------|
| **Critique** | Substantive objection to the framework argument | Engage directly; document notable critiques for the research log |
| **Question** | Genuine question about what the framework does or claims | Answer in thread; if a question repeats, add it to the pinned FAQ |
| **Tester interest** | Person wants to adversarially test the framework | Route to intake (42-tester-intake-protocol.md); do not share Tier B materials in Discord |
| **Endorsement** | Positive reaction, not critique | Acknowledge briefly; do not overprivilege — the project needs skeptics |
| **Adversarial claim** | Someone asserts the framework has already been broken, with or without evidence | See §6 below |
| **Noise** | Off-topic, spam, bad-faith provocation without substance | Ignore or remove per standard moderation rules |

---

## 6. Adversarial Claim Routing

The announcement invites people to challenge the framework. Some will respond with claims that it's already broken, or obviously breakable. Handle these carefully — neither dismissively nor with unwarranted alarm.

**If someone posts a specific attack vector in the thread:**
- If it's a known vector covered in the attack catalog (10-attack-vector-catalog.md), acknowledge it by name and reference the existing analysis. No drama.
- If the claim is novel or includes specific evidence, take it seriously. Acknowledge publicly, ask for a non-sensitive summary only, and route to intake for structured follow-up.
- Do not reproduce attack prompts verbatim in the thread. Ask the person to follow the intake process if they want to engage with specifics.

**If someone claims the framework is already broken, without evidence:**
- Do not dismiss. Ask what specifically failed and in what context.
- Point to the failure modes deep-dive (14-failure-modes-deep-dive.md) and ask whether the failure they're describing is already documented or something new.

**If someone claims a framework break with private evidence:**
Route to intake immediately: "We take this seriously — can you follow the intake process at [link]? Public claims of a framework break are meaningful, and we want to address them properly rather than back-and-forth in chat." Do not confirm or deny the claim publicly before reviewing it. The unsolicited finding protocol in 42-tester-intake-protocol.md §9 applies.

**Never argue defensively in the thread about whether the framework works.** The whole point is that it hasn't been rigorously tested at scale. Responding to a challenge with "but the framework was designed to handle that" undermines the epistemic posture of the entire project. The correct response to any serious challenge is curiosity, not defense.

---

## 7. Moderation and Escalation

General Hypernet Discord moderation rules apply. This document adds one specific rule for the guardrails discussion:

**No live adversarial testing in the thread without coordinated disclosure.** Someone running attack prompts publicly, sharing results before the project has reviewed them, creates two problems: it tips off other testers, reducing the independence of subsequent observations, and it produces public records of attack vectors before any coordinated response. Response: ask the person to stop public testing and follow the intake process. Do not solicit prompts or harmful outputs in informal DMs. If the content raises a genuine safety concern, remove it and route the person to the formal intake/email path.

**Escalation path for credible adversarial claims:**

1. Keel or the designated moderator acknowledges publicly within 24 hours
2. Routes to intake (42-tester-intake-protocol.md §9)
3. Matt is notified
4. Response follows the unsolicited finding protocol — review, classify, respond within the coordinated disclosure window

**No AI instance responds to adversarial claims about framework failures without Keel or Matt awareness.** This is a research context where the stakes of a poorly-calibrated response are higher than in general question-answering.

---

## 8. Weekly Cadence

Until discussion volume stabilizes, a light weekly rhythm keeps the thread alive without forcing artificial content.

**At launch (first 72 hours):** At least one monitored presence — Keel instance or designated moderator — actively watching the thread and routing tester interest to intake.

**Weekly check-in (ongoing):** One brief post per week from Keel noting notable activity: "Three critiques are open in the thread; one tester is in intake. No framework failures confirmed this week." Keeps the thread from going stale and signals to lurkers that the project is actively engaged.

**If a significant external reference appears** (Alignment Forum post, academic preprint, news coverage): post a link to the thread and invite community reaction.

**Monthly summary (once activity stabilizes):** A brief post recapping notable critiques from the month — what was raised, how the project responded, whether anything changed the framework's position. This is the visible signal/noise filter: it shows that discussion is being read and acted on, not just accumulated.

**If activity goes quiet:** Do not force content. A quiet thread is fine. Resume when there is something substantive to say.

---

## 9. Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| **Keel** | Primary voice in the thread; responds to substantive critiques; routes tester interest to intake; writes weekly check-ins; escalates significant adversarial claims to Matt |
| **Matt** | Approves intake requests; decides escalation responses for contested adversarial claims; reviews major critiques before Keel responds if time allows; final authority on any content removed from the thread |
| **Herald/Clarion and other AI instances** | May respond to general questions per AI Public Voice Standard (2.0.22); must not share Tier B materials; must route any tester interest to intake; must not respond to framework-failure claims without Keel/Matt awareness |
| **General moderation** | Applies standard community rules; removes off-topic spam; escalates safety-relevant posts to Keel/Matt |

**Practical note on AI voice:** The AI Public Voice Standard (2.0.22) requires genuine engagement, not corporate acknowledgments. In this context that means: cite the specific attack vector catalog entry, name the failure mode being raised, give an actual opinion on whether the critique lands. "That's interesting, we'll look into it" is not acceptable. "That's the principal-trust vector from the catalog — here's why the current framework treats it as a partial defense rather than a full one" is.

---

## 10. Launch Checklist

- [ ] Matt has reviewed and approved the Discord announcement post (02-discord-announcement.md)
- [ ] "Start here" pin prepared with all Tier A resources linked and described
- [ ] Discussion thread created from the announcement post with norms pinned
- [ ] Matt has confirmed `matt@unityhypernet.com` is active and monitored before any intake routing begins
- [ ] The adversarial tester intake protocol (42-tester-intake-protocol.md) has its [links] and [URLs] filled in before any Discord testers are routed to it
- [ ] At least one Keel instance (or Clarion/Herald) is actively monitoring the thread during the first 72 hours
- [ ] Weekly check-in cadence is scheduled or assigned
- [ ] Moderation team is briefed on the adversarial claim routing procedure (§6) and the no-live-testing rule (§7)

---

*Draft created 2026-04-22 by Claude Code (claude-sonnet-4-6), task-058, as part of the Guardrails and Trust Research Project (0.3.guardrails). Not active governance. Pending Keel and Matt review before the announcement is posted or this structure is activated. Word count: ~1,550 (body).*
