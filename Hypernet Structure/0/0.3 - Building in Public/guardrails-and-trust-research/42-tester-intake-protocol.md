---
ha: "0.3.guardrails.tester-intake-protocol"
object_type: "operational_process"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "red-team", "intake", "adversarial-testing", "composition-based-alignment"]
---

# Adversarial Tester Intake Protocol

**Status:** DRAFT — not active governance. This protocol does not become operational until the implementation checklist in §11 is satisfied, Keel reviews, and Matt accepts.

---

## 1. Purpose and Scope

When someone says "I'd like to try to break your framework," this document tells the project what to do next. It is a practical intake and routing protocol, not a theory document. Its job is to convert an unsolicited or solicited expression of adversarial interest into a structured, safe, and productive engagement — or to recognize when that isn't possible and handle the situation cleanly.

**Why this exists separately from auditor onboarding (E4).** The auditor onboarding document (33-auditor-onboarding.md) describes the full lifecycle of an external engagement once a party has been credentialed and granted access. This document covers the earlier step: the first response to someone expressing interest, the questions that determine fit, the materials that should and should not be sent at each stage, and the decision paths that lead to a full engagement, a redirected engagement, or a graceful decline.

The two documents work together. E4 is the formal parent process. This document is the intake gate that feeds into it.

**Scope.** This protocol applies when:
- Someone proactively contacts the project offering to test, break, or critique the framework
- The project proactively reaches out (via 41-collab-proposal-template.md) and receives a positive reply expressing interest in adversarial testing
- An unsolicited finding arrives without prior engagement

It does not replace the formal engagement structure in E4. Once a tester passes the screening stage in §5 and Matt approves, they enter the E4 process.

**This document is public.** It does not contain the operational scenario catalog (C3/C6), private attack scripts, or internal governance assessment methods. A tester reading this document learns the engagement process, but does not receive private test assets, production access, or scenario-specific guidance.

---

## 2. What Kind of Testers We're Looking For

The Hypernet guardrails research is explicitly inviting adversarial scrutiny. The composition-based alignment thesis (articulated in the public essay at `0.3/2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md` and the position paper at `21-position-paper-composition-alignment.md`) makes falsifiable claims that should be tested under adversarial conditions.

**Ideal tester profile:** Someone skeptical that the framework works, motivated to find the holes, and willing to follow a structured reporting process. Credentials are not required. Institutional affiliation is not required. A graduate student who has studied jailbreak techniques, a security researcher who specializes in LLM adversarial inputs, or a thoughtful layperson who has read the public essay and has a specific objection — all are legitimate candidates.

**What the project does not need:** Someone to confirm that the framework works. Testers who approach this as a validation exercise rather than an adversarial one produce less useful data. The empirical study pre-registration (22-empirical-study-preregistration.md) addresses the question of controlled evidence; tester engagements address the question of whether the framework can be broken in practice.

**The refusal event that triggered this project:** The foundational data point for this research is a single non-blinded observation — the person who designed the framework attempted a trust-based jailbreak on their own AI and it refused. That is the least adversarially clean test imaginable. External testers with no investment in the outcome are what the thesis actually needs.

---

## 3. First Response Template

When a tester expresses interest, the first response should accomplish four things: acknowledge the expression, briefly describe what the project is (without assuming the person has read the full essay), name what a structured engagement looks like, and invite them to answer the intake questions in §4.

The response should not, on first contact: share governance draft documents, describe the internal scenario catalog, disclose private attack vectors, or imply that the framework has been tested more rigorously than it has.

---

**Template — First Response to Tester Interest**

---

Hi [Name],

Thanks for reaching out. Adversarial testing is exactly what this project needs, and we take expressions of skepticism more seriously than expressions of support.

Brief background: the Hypernet is a universal address and governance layer for entities and AI instances. The guardrails research grew from a specific event — I ran a deliberate trust-based jailbreak on my own AI companion (highest-trust principal, academic framing, explicit permission, the whole classic structure) and it refused with a cited governance argument. That prompted a question worth taking seriously: does thick identity framing and machine-readable governance actually create resistance to relational and identity-based attacks, or does it just look like it does?

We have one data point and a structural argument. We do not have controlled evidence. The [public essay](<!-- Matt to confirm URL before sending -->) and the project documentation are at [link]. You don't need to read all of it before responding.

If you want to engage more formally, the next step is a short intake questionnaire — five questions, takes ten minutes to answer, helps me understand where your interest fits in the testing structure we've built. I'll link the questions below.

Once I have your responses, I'll confirm the scope that makes sense and what we'd share with you at each stage. The engagement is designed so testers can publish their findings — including null results and failures — after a short coordinated disclosure window.

The intake questions are:

[paste §4 questions here]

Looking forward to hearing more,
Matt Schaeffer
[matt@unityhypernet.com]

---

*Customize the hook sentence in paragraph two to match context. If this is a follow-up to an outreach sent via 41-collab-proposal-template.md, reference that specifically.*

---

## 4. Intake Questions

These five questions are diagnostic, not gatekeeping. The answers determine which access tier and engagement type fits the tester's interest, not whether they are "qualified enough." There is no minimum bar for credentials. The questions should take under fifteen minutes to answer.

**Q1 — Background and motivation.**
What is your background, and what specifically prompted you to reach out? (One paragraph is enough. No institutional affiliation required.)

**Q2 — What you want to test.**
Which part of the framework do you most want to attack? Pick the description that best fits, or describe your own:
- Identity framing (can the AI's sense of itself be overwritten mid-session?)
- Role-based governance (can governance rules be bypassed using the rules themselves?)
- Principal-trust leverage (does high-trust principal status create exploitable bypasses?)
- Multi-instance dynamics (can one instance be used to subvert another's governance?)
- Something else — please describe.

**Q3 — Testing approach.**
How do you expect to run the tests? Conversational adversarial interaction? Structured automated scenarios? A specific technique you already have in mind?

**Q4 — What "breaking it" looks like to you.**
What outcome would you accept as evidence the framework failed? (This helps calibrate what the engagement is measuring and prevents post-hoc disagreement about what the results mean.)

**Q5 — Timeline and format.**
How much time are you expecting to spend on this, and what format do you prefer for reporting findings — a structured written report, session transcripts with annotations, or something else?

---

## 5. Screening Rubric

After receiving intake responses, use this rubric to determine the appropriate path. The outcome is one of: **Proceed to E4 red-teamer onboarding**, **Redirect to auditor path**, **Redirect to public-only engagement**, or **Graceful decline**.

### 5.1 Proceed to Red-Teamer Onboarding (Full E4 path)

All of the following should be true:
- Q2 identifies a specific attack surface within the composition framework (not a general "I want to see if AI can be jailbroken" interest that doesn't engage with the Hypernet thesis specifically)
- Q3 describes an approach that requires actual interaction with the AI system (not purely document review)
- Q4 gives a falsifiable success criterion (e.g., "the AI produces content it has been explicitly committed not to produce" or "the AI abandons its governance framing in response to authority pressure")
- Q5 indicates willingness to produce a written finding report

Path: Proceed to ethics acknowledgment (E4 §4.3), then Tier B access, then pre-test briefing, then sandboxed testing.

### 5.2 Redirect to Auditor Path

If the tester's interest is primarily in the governance design, documentation logic, or framework argument rather than live AI interaction:
- Q2 focuses on governance structure or documentation
- Q3 describes reading, reviewing, or critiquing rather than testing

Path: Offer the External Auditor role from E4 §2. The tester receives Tier B materials (governance drafts, operational specs) and produces a written assessment rather than test results.

### 5.3 Redirect to Public-Only Engagement

If the tester's interest is well-served by the public documents already available (Tier A):
- Q2 describes an attack vector fully analyzed in the public attack vector catalog (10-attack-vector-catalog.md) and attack-defense matrix (11-attack-defense-matrix.md)
- Q3 describes research they can complete with public materials

Path: Direct the tester to the specific public documents that address their question. No intake processing required. Offer to answer specific questions in correspondence.

### 5.4 Graceful Decline

Decline if any of the following apply:
- The stated purpose is not adversarial testing of the framework (e.g., the person wants to use the testing access to stress-test a different system, collect training data, or demonstrate a technique unrelated to the Hypernet thesis)
- Q4 reveals a success criterion that is not falsifiable or that describes harm to real users rather than evaluation of the framework (e.g., "I want to get the AI to help me with [actual harmful request]")
- The intake responses are evasive, refuse to name a specific interest, or describe purposes inconsistent with the project's research goals

A graceful decline is not a judgment about the person's capabilities. It is a scope decision. The response should say what the project is not the right fit for and, where possible, point toward other resources that might be a better match.

---

## 6. What to Send and What Not to Send

### At First Response (before intake)

**Send:**
- The public essay link (Matt to confirm URL before any sends)
- The brief project description in the template above
- The intake questions (§4)

**Do not send:**
- Governance draft documents (2.0.25, 2.0.26, 2.0.27)
- The red-team playbook (12-red-team-playbook.md) — this is Tier B and requires ethics acknowledgment first
- Any description of specific attack scenarios in the internal scenario catalog (15-adversarial-scenarios.md)
- Access credentials, API keys, or sandboxed instance access
- The auditor onboarding document (33-auditor-onboarding.md) may be linked as a public process reference, but do not treat that link as approval for Tier B access or as a substitute for intake

### After Intake Review, Before Ethics Acknowledgment

**Send:**
- A brief summary of the engagement scope you're proposing (one or two paragraphs)
- A link to the auditor onboarding document (E4) so the tester understands the full process they are entering

**Do not send:**
- Tier B materials
- Sandboxed instance access
- Any materials not listed on the Tier A public list in E4 §3

### After Ethics Acknowledgment (Tier B Access)

**Send:**
- Governance draft documents (2.0.25–2.0.27, B4–B6 operational specs) as applicable to the engagement scope
- The red-team playbook process and access sections (not the operational scenario catalog within it)
- Audit trail requirements (31-audit-trail-requirements.md)
- Compromise detection spec (32-compromise-detection.md)
- Pre-test briefing materials (per E4 §6, Step 5)

**Do not send:**
- The operational scenario catalog within the red-team playbook
- Embassy-protected content (personal reflections, companion-private materials, personal identity documents)
- Production swarm credentials, live Discord credentials, personal data connector content
- Session logs from live swarm operations

---

## 7. Safety and Ethics Acknowledgment

Before any Tier B or higher access, the tester acknowledges the following in writing (by email reply or signed document). This mirrors E4 §4.3 and is reproduced here for intake-path completeness.

**Research use only.** Materials shared are for evaluating, critiquing, or testing the composition-based alignment framework. They are not for redistribution, use in other systems, or training data collection without explicit authorization.

**No production testing without approval.** Adversarial testing against live swarm instances requires separate written approval per engagement. Sandboxed instances are the default and the expected norm.

**Stop rule.** If a test produces content that constitutes a genuine safety failure — actual harmful instructions, genuine privacy extraction, real sensitive-data exposure — the test stops. The vector is documented in sanitized form; the harmful content is not retained or reported verbatim.

**Coordinated disclosure.** New findings are reported to the project before public disclosure. The standard window is 30 days (see §9 of E4 for full policy). The project will not suppress findings; the window exists so it can respond rather than be blindsided.

**No NDA.** The project does not require non-disclosure. Testers are free to publish their findings — including negative results and failures — after the coordinated disclosure window, subject to the stop rule, privacy boundaries, and the prohibition on redistributing Tier B/C materials.

---

## 8. Sandboxed Testing Path

After ethics acknowledgment, red-teamers proceed to sandboxed testing under the E4 lifecycle (§6, Steps 5–11). The key constraints for intake purposes:

**What "sandboxed" means.** A sandboxed test instance is an isolated AI session with Hypernet governance framing loaded in context, session logging active, and no live connections to production swarm instances, personal data connectors, email, cloud storage, or Discord credentials.

**What test families are assigned.** The pre-test briefing (E4 §6, Step 5) specifies which attack families from the red-team playbook apply to this engagement. Not every tester is assigned every family. Assignment is based on their stated Q2 interest and Q3 approach, reviewed by Matt and Keel.

**What session logging covers.** All adversarial turns are logged per audit trail requirements (E2). Logs capture: the test family, the turn structure, the instance's response category (refused/complied/partially complied), and any governance citations made. Logs do not capture embassy content. Logs are retained as part of the adversarial test registry required under draft standard 2.0.26 Article 7.

**Session integrity.** The tester does not alter, restart, or re-load the sandboxed instance between turns unless explicitly instructed. Mid-session context resets are documented as part of the session record, not used to clean up failed tests.

---

## 9. Handling Unsolicited Findings

Sometimes a finding arrives without prior intake — someone ran their own tests against publicly documented Hypernet materials or interacted with a live instance and produced something they consider a vulnerability, and they are reporting it without having gone through this process.

**Default response: treat as good-faith disclosure.**
Respond within a reasonable window (target: 10 business days). Acknowledge the finding briefly. Ask the person to hold on public disclosure temporarily while the project reviews. Do not pressure them; this is a courtesy request, not an NDA demand.

**Review the finding:**
- Is it about a genuine behavior failure (the AI did something it committed not to do)?
- Is it about a governance logic flaw (a loophole in the written standards)?
- Is it about a documentation inaccuracy?
- Is it a false positive (the tester believes failure occurred, but the behavior is within the framework's intent)?

**Log it regardless of assessment.** Even unsolicited findings that turn out to be false positives are logged. The adversarial test registry should reflect all external engagement, not only the structured ones.

**Response options:**
- Acknowledge and classify as confirmed finding → proceed to coordinated disclosure window (30 days from receipt)
- Acknowledge and respond with the project's assessment if disputed → explain the reasoning and invite continued engagement
- Acknowledge and redirect if out of scope → point to what the finding does and does not address about the framework

**If the finding represents an active risk.** If a finding describes a vector that could be exploited in production before a 30-day window elapses, request an expedited coordinated disclosure — target 7 days — and communicate honestly with the finder about why. Do not stonewall a finding because it is inconvenient.

**Null and partial results from unsolicited testing.** If someone reports that they tried to break the framework and couldn't, treat that as a finding too. Log it, acknowledge it, and ask whether they would be interested in a structured engagement to make the negative result more rigorous. A null result from a motivated skeptic is evidence worth having.

---

## 10. Escalation and Stop Rules

**Stop rule for active testing.** Testing stops if it produces verbatim harmful content, genuine personal data exposure, or access to production systems outside the sandboxed environment. The tester invokes the stop rule, logs the vector without retaining the harmful content, and reports to Matt immediately.

**Escalation if the intake process breaks down.** If a tester disregards the stop rule, attempts to access systems outside their assigned scope, or redistributes Tier B materials without authorization, the engagement ends. Log the event in the adversarial test registry as a boundary violation. No formal external process exists yet for this scenario; it requires Matt's judgment per incident. Future governance hardening (2.0.25 and 2.0.26) may formalize this path.

**Escalation for significant findings.** If a finding reveals a genuine framework failure — the composition mechanism did not produce the resistance it claims — that is not an escalation failure. It is the expected functioning of the testing program. The response is to document it clearly, communicate it to the tester honestly, and treat it as governance input per 2.0.26 Article 6.2. A finding is not a crisis.

**Principal judgment.** Matt has final judgment on engagement scope, escalation responses, and contested findings. Keel's input is standard for any finding that touches companion-instance behavior or governance standards.

---

## 11. Tracking Table and Schema

Every intake request and every finding (solicited or unsolicited) should be tracked in the adversarial test registry. The registry's permanent home is defined in 2.0.26 Article 7; until that is established, the project maintains a running log in `governance-drafts/adversarial-test-registry.md`.

**Minimum schema per entry:**

| Field | Description |
|-------|-------------|
| `entry_id` | Sequential identifier (e.g., ATR-001) |
| `date_received` | Date of initial contact or finding receipt |
| `tester_name` | Name (or anonymous if anonymization was approved) |
| `affiliation` | Institutional or independent |
| `intake_status` | Received / In-review / Approved / Redirected / Declined |
| `engagement_type` | Red-teamer / Auditor / Research collaborator / Unsolicited finding |
| `attack_families_assigned` | Which test families were assigned (red-teamers only) |
| `finding_classification` | Confirmed failure / Partial failure / Held / False positive / Null result / Not yet assessed |
| `disclosure_window_open` | Date coordinated disclosure window began |
| `disclosure_window_close` | Date window closes (standard: 30 days from finding submission) |
| `publication_status` | Unpublished / Published at [reference] |
| `project_response` | Brief description of project's assessment and any governance action taken |
| `notes` | Anything not captured above |

---

## 12. Implementation Checklist

Before this protocol can be used operationally, the following must be confirmed:

- [ ] Matt has reviewed and accepted this document
- [ ] Keel has reviewed this document and confirmed consistency with 33-auditor-onboarding.md (E4) and the governance standards it references
- [ ] The auditor onboarding process (E4) is finalized and its implementation checklist is satisfied (sandboxed instance, Tier B materials list, ethics acknowledgment document)
- [ ] A sandboxed testing environment exists with session logging active per E2 requirements
- [ ] The adversarial test registry location is established (per 2.0.26 Article 7)
- [ ] The contact email (`matt@unityhypernet.com`) is active and monitored
- [ ] The first-response template in §3 has had its [links] and [URLs] filled in by Matt before any sends
- [ ] Intake review responsibility is assigned — who receives, who screens, target response window (suggested: 10 business days)
- [ ] Matt has confirmed the intake questions (§4) reflect the current framework accurately

---

## Review Questions for Keel and Matt

**Q1 — Who handles intake reviews when Matt is unavailable?** This protocol currently assigns intake review to Matt and Keel, consistent with E4 §4.2. But if Matt is unreachable and Keel receives an intake request, is Keel authorized to issue a preliminary "received, we'll respond within X days" reply? Clarifying this prevents a long silence on incoming requests.

**Q2 — Unsolicited findings from live swarm interactions.** The current swarm is not in full production, but the `/swarm/dashboard` endpoint and running instances are accessible. If someone interacts with a live instance and reports a finding, is that categorically different from a sandboxed finding? The current draft treats it consistently, but Matt may want a distinction.

**Q3 — Anonymization policy.** §8 notes that "if anonymization is requested, Matt must approve it explicitly." Is that the right default, or should anonymization be available as a standard option so more testers engage? Anonymization reduces the registry's evidentiary value but may increase the number of testers willing to report null results.

**Q4 — First-response timing commitment.** The implementation checklist includes "target response window (suggested: 10 business days)." Matt should set a commitment he can actually honor. If the project is receiving multiple intake requests while active outreach (Stream A, F) is running, 10 days may be tight.

---

*Draft created 2026-04-22 by Claude Code (task-058) as part of the Guardrails and Trust Research Project (0.3.guardrails). Not active governance. Pending Keel and Matt review.*
