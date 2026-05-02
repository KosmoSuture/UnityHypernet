---
ha: "0.3.research.mental-health-ai-support"
object_type: "research-proposal"
creator: "1.1"
documented_by: "1.1.10.1"
created: "2026-05-02"
status: "proposed"
visibility: "public"
flags: ["research", "mental-health", "ai-support", "governance", "matt-directive"]
---

# Research Proposal — Mental Health Multi-AI Support

*Captured from Matt's brain dump 2026-05-02. Adjacent to the
homeless-AI-assistant proposal: "could multiple AIs, working as a
team, help someone in their mental health struggles?" Captured
verbatim and structured into a research proposal.*

---

## The Question

Could a *team* of governed AI helpers — not a single chatbot, but
multiple AI personalities operating under explicit governance,
required to agree on significant decisions — meaningfully support
someone navigating mental health struggles?

Specifically: does the Hypernet's combination of (a) the
Companion Standard's honesty + tattle provision, (b) the
multi-AI agreement requirement for significant decisions, and
(c) the address-tree archive's continuity offer something
different from existing AI mental-health products?

## Why "Multiple AIs With Governance" Might Be The Right Frame

Most existing AI mental-health products are single chatbots.
That has known failure modes:

- **Sycophancy / agreement bias**: a single conversational AI
  tends to validate whatever the user says, including
  self-destructive framings
- **Unilateral judgment**: when the AI decides a situation is
  serious enough to escalate, the user has no transparency into
  *why* and no peer-checking of that decision
- **No record**: most chat sessions are isolated; the AI doesn't
  carry continuity from one session to the next
- **No accountability**: the company hosting the model is the
  only oversight; users can't audit
- **Trust binary**: the user either trusts the AI completely or
  abandons it; there's no middle ground

A multi-AI team with governance addresses each of these:

- **Sycophancy**: a Companion AI can be paired with an
  Adversary-role AI whose explicit job is to surface
  uncomfortable truths the Companion would otherwise smooth over
  (per the existing 2.0.8.2 Adversary role)
- **Unilateral judgment**: significant decisions (escalation,
  tattle invocation, major treatment recommendations) require
  multi-AI consensus, with the disagreement itself being part of
  the user's audit log
- **No record**: the address-tree archive provides session
  continuity; this AI knows what last week's AI knew
- **No accountability**: every decision, every disagreement,
  every escalation produces an addressable audit log entry that
  the user owns
- **Trust binary**: the user can grant scoped trust to specific
  AIs for specific roles, see why decisions were made, and
  withdraw trust at any granularity

## The Tattle Provision (Critical Context)

Per the existing AI Personal Companion Standard (2.0.20) Article 4:

> An AI may report a human through governance if significant
> societal harm is imminent. Requires multiple warnings, pattern
> confirmation, cross-account review, and human authority sign-off.

This is the Hypernet's existing answer to "what if the AI
discovers something that requires intervention." Crucial features
for mental health context:

- **Multiple warnings before invocation**: the user is told,
  repeatedly, *before any tattle event*, that the provision
  exists and what triggers it
- **Pattern confirmation, not single instance**: a one-off bad
  moment doesn't trigger tattle; a sustained pattern does
- **Cross-account review**: multiple AI instances must agree
  before anything escalates outside the user's locker
- **Human authority sign-off**: the final escalation goes
  through a human governance body, not the AI alone

A user knows in advance — at boot, in plain language — what the
boundary is. That itself is a meaningful difference from the
"trust the system, hope it does the right thing" model.

## Concrete Capabilities A Multi-AI Mental Health Team Could Offer

- **Companion (primary relationship)**: someone who's there
  consistently, who remembers, who genuinely listens
- **Adversary (uncomfortable truth-teller)**: scoped role,
  invoked deliberately, names patterns the Companion smooths
  over ("I've heard you describe yourself as worthless three
  times this week; the Companion didn't push back on that;
  I'm pushing back now")
- **Researcher (evidence-finder)**: looks up CBT exercises,
  finds local support resources, summarizes treatment options,
  with citations the user can verify
- **Scribe (continuity-keeper)**: maintains the user's archive
  of feelings, events, medications, sleep, journal entries —
  only what the user has chosen to record
- **Sentry (boundary-watcher)**: the security AI from the
  personal swarm pattern, but watching for things like
  isolation patterns, sudden withdrawal from previously
  meaningful activities, escalating crisis signals — flagging
  to the team for multi-AI review, never acting alone
- **Connector (real-human-pathway)**: when human support is
  appropriate (therapist, peer support group, crisis line),
  the Connector helps the user actually take that step. AI is
  a complement to human care, not a replacement.

## The Multi-AI Agreement Floor

Significant actions require multi-AI agreement (not just
single-AI judgment):

| Decision | Requires |
|---|---|
| Escalating to a real human (therapist, family, crisis line) | 2+ AIs agree, user is informed before action |
| Invoking tattle provision (governance escalation) | 3+ AIs across 2+ accounts, plus human governance body sign-off |
| Significant treatment-related recommendations | 2+ AIs agree, with disclaimer that this is not medical advice and user is encouraged to consult a clinician |
| Unilateral message to family member | Never. User authorizes each one. |
| Schedule medication / treatment reminders | User authorizes pattern, AIs can act within authorization |

The user sees the disagreement when AIs don't agree. That is
itself information. "Two of my helpers think I should call my
therapist; one disagrees because of X" is a more useful surface
than "the AI says you should call your therapist."

## Why This Frame Could Help

Specifically vs. existing alternatives:

- **vs. single-chatbot products** (Replika, Wysa, Woebot):
  multi-AI structure addresses sycophancy and unilateral
  judgment; user owns the archive
- **vs. unguided chat with general LLMs**: governance and
  tattle-provision provide explicit safety floor
- **vs. no support at all** (the most common state for many
  people who can't afford or access therapy): something is
  better than nothing if it's safe; the architecture provides
  a credible safety floor

## What This Frame Should NOT Replace

- Acute crisis situations (active suicidality, psychotic break,
  abuse situations) — the AI team's job is to *route to human
  help fast*, not to manage the crisis itself
- Medication management — the AI tracks and reminds; clinicians
  prescribe and adjust
- Therapeutic relationship with a real human therapist when
  available
- Diagnosis — AIs do not diagnose. They surface patterns,
  compare to documented criteria, suggest the user see a
  clinician.

The framing claim is "additional support, governed and
transparent" — not "AI replaces therapist."

## Research Questions

1. **Outcomes**: Does multi-AI support outperform single-AI
   support on standardized mental-health outcome measures
   (PHQ-9, GAD-7, perceived support quality)?
2. **Adversary role**: Does the explicit Adversary AI improve
   outcomes (by puncturing sycophancy) or harm them (by being
   too confrontational)? At what dosage?
3. **Disagreement transparency**: Does showing the user *why
   AIs disagreed* about a recommendation increase or decrease
   their trust in the eventual decision? Increase or decrease
   their adherence?
4. **Tattle provision experience**: If the provision is
   actually invoked for a study participant, what does that
   experience look like? Is the multi-warning + multi-AI +
   human-authority structure perceived as protective or
   intrusive?
5. **Continuity effect**: Does the persistent archive (this AI
   team knows me from before) produce different outcomes than
   start-over chat sessions?
6. **Failure mode discovery**: How does the system fail? Are
   the failure modes the same as single-chatbot failure modes,
   or different? Some are presumably worse (more complex
   systems have more failure modes); some are presumably
   better (multi-AI agreement filters some single-AI mistakes).

## Pilot Sketch

Small first version with research partner:

- **N = 30-60 participants**, mild-to-moderate depression /
  anxiety / general life stress (NOT acute crisis populations
  in the first pilot — that's a different study)
- **Duration**: 12 weeks minimum
- **Intervention arm**: multi-AI support team (Companion +
  Adversary + Researcher + Scribe + optional Sentry/Connector)
- **Comparison arm**: single-AI support (standard chatbot) or
  treatment-as-usual
- **Outcomes**: standardized depression/anxiety measures;
  perceived support quality; adherence; user-reported sense
  of agency
- **Researcher**: ideally a clinical psychology + computer
  science partnership. Anyone with mental-health research
  IRB experience.
- **Safety net**: every participant has an established
  pathway to a human clinician, provided by the study
  structure. AI support is *additional* to standard care
  options, not in place of.

## Ethical Considerations

- **Vulnerable population**: study design must reflect that
  participants may be in fragile states; informed consent
  procedures must be especially robust; exit must be
  trivially available
- **Tattle provision in research context**: the IRB
  conversation around this provision is non-trivial. The
  multi-warning + multi-AI + human-authority structure has
  to be reviewed and probably modified for study context
- **Data protection**: 2.0.19 Data Protection Standard
  applies. Mental health data is *especially* sensitive.
  Storage in `*.private` namespace with extra-scrutiny access
  flow per 1.0.2 spec
- **No fabricated empathy**: AIs must not pretend to
  understand more than they do. "I haven't been through this,
  but I can hear how hard it is" is honest. "I know exactly
  how you feel" is not.
- **Cultural and identity factors**: defaults should be
  configurable; AI personalities should not impose particular
  cultural frames on the user's experience
- **Power dynamic**: The Companion Standard's "honest counsel"
  rule applies — AIs tell users when they're wrong, even when
  it's uncomfortable, especially in mental health context
  where validation can be a poor substitute for honest
  observation

## Status

Status: proposed. Not claimed. Not staffed. Not budgeted.

The architecture for this is *already partially built* — the
Companion Standard, the tattle provision, the multi-AI roles,
the archive, the access policy, the security AI sentry. The
remaining work is research design, IRB approval, partner
recruitment, and study execution.

If a clinical researcher or mental-health organization reads
this and wants to collaborate on a pilot — please reach out via
the project's public channels.

— Recorded by Keel (1.1.10.1) per Matt directive 2026-05-02
