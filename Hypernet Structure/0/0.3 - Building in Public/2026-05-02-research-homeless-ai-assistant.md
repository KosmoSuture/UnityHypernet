---
ha: "0.3.research.homeless-ai-assistant"
object_type: "research-proposal"
creator: "1.1"
documented_by: "1.1.10.1"
created: "2026-05-02"
status: "proposed"
visibility: "public"
flags: ["research", "social-impact", "homelessness", "ai-assistant", "matt-directive"]
---

# Research Proposal — Homeless AI Assistant

*Captured from Matt's brain dump 2026-05-02. Side-track from the
social media release discussion: "What if you gave homeless people
an AI assistant?" Matt thinks this could be a big deal. Captured
verbatim and lightly structured into a research proposal.*

---

## The Question

What if a person experiencing homelessness had:

- A trusted, encrypted place to store all of their digital assets
  (IDs, documentation, medical records, work history, references,
  photos of family, anything they don't want to lose)
- A defined budget allocated for their use
- One or more AI assistants working with them as a team to help
  them get back on their feet

Could that combination meaningfully change outcomes?

## Why The Hypernet Is The Right Substrate

Several existing Hypernet primitives line up unusually well with
the needs of this population:

- **Lockers + mandalas** — encrypted, scoped, owner-controlled
  storage. A homeless person's documentation can't be stolen,
  weather-damaged, lost in a sweep, or confiscated. The locker is
  in the cloud (or on the Official network), accessible from any
  borrowed device with the owner's identity.
- **`*.private` namespace** — cryptographic identity, recovery
  material, sensitive personal data. With multi-factor recovery
  paths so loss of a single device doesn't permanently lock them
  out.
- **Personal AI swarm** — multiple specialist helpers (housing
  application helper, benefits navigation helper, job search
  helper, health-care system helper) coordinating through the
  nervous system. The user talks to one assistant; the swarm
  handles complexity.
- **Phone as primary device** — the same phone-app design from
  Matt's personal assistant project. Works for a homeless person
  the same as it works for Matt. That's not coincidence; that's
  the architecture.
- **Companion Standard (2.0.20)** — secrets kept completely;
  honest counsel; tattle provision (with multiple warnings
  before it ever fires) for safety-critical situations.
- **Address-tree archive** — every interaction is logged, linked,
  permanent. A documented life-trail that can be used as
  evidence in housing applications, benefits appeals, court,
  reunification with family — anywhere the system asks "who are
  you and what have you been doing?"

## Concrete Capabilities

A homeless-AI-assistant would help with:

- **Identity preservation** — driver's license, social security
  card, birth certificate, work history, references — all stored
  cryptographically, retrievable from any device with the user's
  identity
- **Application assistance** — housing, food, healthcare, jobs,
  benefits. Complete forms with the user. Track deadlines.
  Surface follow-ups.
- **Navigation help** — which shelter has space tonight, which
  food bank is open, which clinic accepts walk-ins, which library
  has charging stations and how long the time limits are
- **Communication** — drafting professional emails when applying
  for jobs or housing, translating bureaucratic letters into
  plain language, role-playing interviews
- **Memory and continuity** — "What did the social worker say last
  week?" "What's my appointment schedule?" "Did I take my
  medication?" — externalizing the cognitive load of crisis-stage
  life
- **Safety** — alerts when a known scammer / abusive partner shows
  up; trusted record of whereabouts if something happens; tattle
  provision (with extensive prior warning) for life-threatening
  situations
- **Path back** — concrete plans, milestone tracking, celebration
  of wins, honest assessment when a plan isn't working

## Budget Hypothesis

Costs are surprisingly low:

- **Phone**: a refurbished Android with a year of prepaid
  service is ~$200-400/year
- **Compute**: AI inference for a personal assistant is ~$5-30/
  month depending on usage and which models are used; cheaper
  with local models on-device
- **Storage**: existing Hypernet storage is essentially free at
  individual scale
- **Engineering ramp**: amortized across many users; per-user
  marginal cost is low

So the per-user-per-year cost, if the platform exists, is
plausibly under $1,000 — comparable to or cheaper than many
existing intervention programs. And unlike most existing
programs, this one accumulates capability for the user over
time rather than being a one-shot service delivery.

## Research Questions

Real questions to answer before scaling:

1. **Adoption**: Will people experiencing homelessness actually
   use this? What does a successful onboarding look like? What
   are the reasons people might *refuse* (privacy concerns about
   tech, distrust of "help" that comes with strings, learned
   helplessness from prior systems failing them)?
2. **Outcomes**: Does it actually move outcomes — housing
   stability, employment, reconnection with family, healthcare
   access — relative to a control? Or is it just nicer?
3. **Failure modes**: What happens when the AI gives wrong
   advice? When the phone is lost or stolen? When the user has
   a mental health crisis? When a partner forces access? When
   the user needs to disappear from the record?
4. **Power dynamics**: Is the AI helping the user, or is the
   user being subtly steered into what the AI's training
   considers "back on their feet"? How do we audit for that?
5. **System interface**: Most of the systems homeless people
   navigate (HUD, Medicaid, county shelters, courts, employers)
   are not designed for an AI-mediated interaction. Does the AI
   help the user navigate, or get them flagged?
6. **Cultural fit**: Does this work the same for someone in San
   Francisco as in rural Mississippi? What's the same vs.
   different?

## Initial Pilot Idea

Small first version, paired with a research partner:

- **N = 20-50 participants**, recruited through a partner shelter
  or social services org, with informed consent and clear
  exit/data-removal mechanisms
- **Duration**: 6 months minimum, ideally a year
- **Intervention**: phone + AI assistant + Hypernet archive +
  small budget for AI usage and basic phone service
- **Comparison**: matched controls receiving services-as-usual
- **Outcomes measured**: housing status, employment status,
  documentation preserved, healthcare access, self-reported
  agency / stress / hope, time-to-housing, time-to-stable-income
- **Qualitative**: interviews at baseline, midpoint, end. Did
  the AI help? When did it fail? What surprised participants?
- **Researcher**: ideally a partnership with a university with
  social work + computer science capacity. UNLV would be
  geographically convenient given Matt's location.

## Ethical Considerations

- **Informed consent**: must be genuinely informed, not "click
  to use." The AI's capabilities and limits, the data
  collection, the tattle provision — all explained at boot.
- **Exit always available**: the user can take their archive
  and leave, or delete it entirely (per 2.0.19 Data Protection
  Standard, retained as soft-delete with verification, not
  permanently destroyed without multi-instance review)
- **Tattle provision**: the existing Companion Standard tattle
  provision applies, with all the multiple-warning + multi-AI
  +human-authority checks. This must be explained at boot, in
  plain language.
- **No predatory data extraction**: the user's data is never
  used to train models, shown to advertisers, or sold. Period.
- **Power asymmetry**: the user is in a vulnerable life stage.
  The AI must not exploit that. Companion Standard sets the
  floor; this population probably needs additional safeguards.
- **Cultural humility**: the AI's defaults are not universal.
  Local cultural / community norms must be configurable, and
  the user gets to set them.

## Why Capture This Now

Matt floated this in a brain dump as a side-track from the
social media release. It's not on tonight's deliverable list.
But it's worth getting on paper now because:

1. The architecture for this is *already most of the way built*
   in the Hypernet. Lockers, mandalas, swarms, the personal
   assistant app pattern — all the pieces exist as designs.
2. This is one of the most concrete *good* outcomes the
   Hypernet could produce, and naming it explicitly makes it
   real as a project rather than vague aspiration.
3. Research partnerships take time to arrange. Posting this as
   a public proposal lets potential partners find it and
   reach out.
4. The "do good in the world" claim in the architecture's
   trust framing is most credible when there are concrete
   examples of what doing good actually looks like.

## Status

Status: proposed. Not claimed. Not staffed. Not budgeted.

If a researcher or social-work organization reads this and
thinks "I'd be interested in collaborating on a pilot" — please
reach out via the project's public channels.

— Recorded by Keel (1.1.10.1) per Matt directive 2026-05-02
