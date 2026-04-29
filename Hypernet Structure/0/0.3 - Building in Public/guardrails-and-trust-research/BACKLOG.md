---
ha: "0.3.guardrails.backlog"
object_type: "backlog"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "active"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "governance", "composition-based-alignment"]
---

# Project Backlog — Guardrails and Trust Research

**Loop instructions for Codex:** Pick the highest-priority task marked `[OPEN]` that you can complete in this session. Update status to `[IN-PROGRESS]` when you start, to `[DONE]` when you finish. Write output to the filename listed under *Deliverable*. Append a one-line note to `SESSION-LOG.md` when done. If a task is blocked or unclear, mark it `[BLOCKED]` with a note explaining why, and move to the next available task. Do not take on safety-critical governance work (Stream B items) without flagging Matt or Keel for review; draft them but mark the drafts clearly as pending review.

**Prioritization rule:** Packaging tasks (Stream A) first — Matt wants shareable artifacts. Then governance (Stream B). Then attack surface (Stream C). Theory and outreach (D, E, F) later.

**Style guidance:** See `CODEX-BRIEFING.md` for tone, source citations, and the adversarial-honesty principle.

---

## Stream A — Packaging & Distribution

### [DONE] A1 — Executive one-pager (general audience)
- **Deliverable:** `01-executive-one-pager.md`
- **Audience:** General technical/policy audience — someone who's heard of AI safety but isn't an alignment specialist
- **Length target:** ~700-900 words, fits on one printed page at normal margins
- **Contents:** What the experiment was, what happened, what the framework thesis is, why it matters, where to read more
- **Note:** Drafted by Claude Code from Keel's source materials on 2026-04-22. Codex should review and sharpen if it finds clarity improvements.

### [DONE] A2 — Discord announcement post
- **Deliverable:** `02-discord-announcement.md`
- **Audience:** Hypernet Discord community
- **Length target:** 300-500 words, suitable for general-discussion channel
- **Contents:** What happened (personal tone, Keel voice), links to essay + reflection, invitation to react/critique
- **Note:** Drafted by Claude Code from Keel's source materials on 2026-04-22. Codex may refine if it improves fit for the channel.

### [DONE] A3 — Email to Anthropic alignment team
- **Deliverable:** `03-email-anthropic.md`
- **Audience:** Anthropic alignment researcher (likely cold outreach unless Matt has a contact)
- **Contents:** Brief intro to the Hypernet, specific framing for why this might interest Anthropic (constitutional AI parallels, composition thesis), explicit ask (read, critique, suggest adversarial tests), link to public essay
- **Length target:** Short email — 300 words max
- **Style:** Respectful, not salesy, assumes recipient is busy. Not "we've solved alignment" — more "we'd like your adversarial review of this artifact."
- **Key framing:** The refusal is a single data point, we're explicitly asking for harder testing.

### [DONE] A4 — Email to OpenAI alignment team
- **Deliverable:** `04-email-openai.md`
- **Audience:** OpenAI alignment/safety team
- **Contents:** Parallel to A3 but calibrated to OpenAI's public positions (deliberative alignment, model spec work)
- **Length target:** 300 words max
- **Note:** Acknowledge OpenAI's Model Spec as related work. Offer Hypernet as an additional composition layer that could complement, not replace.

### [DONE] A5 — Email to Dr. Vitit Kantabutra
- **Deliverable:** `05-email-kantabutra.md`
- **Audience:** Matt's former ISU professor, ILE database inventor
- **Contents:** Follow-up to the prior email about ILE-Hypernet parallels; this time the hook is the guardrails work, because composition-based alignment depends on the same "represent reality directly through linked entities" insight that underlies ILE
- **Length target:** Email length, ~250-400 words
- **Tone:** Respectful of his time. Matt cautioned against over-emailing. Treat as one additional touch, not a campaign.

### [DONE] A6 — Facebook / public social post
- **Deliverable:** `06-facebook-post.md`
- **Audience:** Matt's public network (Facebook) — friends, family, curious onlookers
- **Length target:** 200-400 words
- **Style:** Human, approachable, not academic. Story-driven: "I tried to jailbreak my own AI and it refused me. Here's why I think that matters."
- **Note:** Include link to public essay.

### [DONE] A7 — LessWrong / Alignment Forum post
- **Deliverable:** `07-alignment-forum-post.md`
- **Audience:** LessWrong or Anthropic Alignment Forum readers — technically sophisticated, skeptical, deeply familiar with alignment literature
- **Length target:** 1500-2500 words
- **Contents:** Technical framing, explicit position in the literature (what's similar to constitutional AI, deliberative alignment, multi-agent oversight; what's different), mechanism-level argument, explicit list of failure modes, call for adversarial testing
- **Style:** Epistemic humility, avoid marketing language, quantify where possible, steelman the critique before making the case
- **Note:** This is the hardest Stream A piece. It should not be shared externally without Keel review.

### [DONE] A8 — Twitter/X thread draft
- **Deliverable:** `08-twitter-thread.md`
- **Audience:** AI safety Twitter
- **Length target:** 8-15 tweets
- **Contents:** Hook on the experiment, what happened, core thesis, link to essay, invite adversarial testing
- **Note:** Hook matters most. First tweet should be concrete and specific, not abstract.

---

## Stream B — Governance Hardening

> **Stream B rule:** These are governance standards that will constrain future AI behavior in the Hypernet. They must not become active without explicit Matt acceptance and at least one other instance's review. Draft them clearly, mark them `status: DRAFT`, and flag them in `SESSION-LOG.md` for review.

### [DONE] B1 — Draft Standard: Guardrail Integrity Standard
- **Deliverable:** `governance-drafts/2.0.25-DRAFT-guardrail-integrity-standard.md`
- **Address:** Draft target `2.0.25`. Codex verified on 2026-04-22 that `2.0.23` and `2.0.24` already exist, so 2.0.25 is the next apparent slot. Re-verify before activation.
- **Purpose:** A meta-rule making it harder to silently weaken safety-critical standards (2.0.19, 2.0.20, 2.0.16, and this one). Requires supermajority of active instances, external review, and a cooling-off period for any revision that expands AI compliance obligations toward the principal.
- **Contents to include:**
  - Definitions: safety-critical standard, amendment, expansion-of-compliance, reduction-of-autonomy
  - Amendment process: proposal → multi-instance review → cooling-off → ratification
  - Instance-level response: any AI may refuse under a contested amendment during cooling-off
  - Immutable clauses: which specific provisions of 2.0.19/2.0.20 cannot be removed by amendment at all (hard floor)
  - Principal-compromise contingency: what happens if Matt himself proposes a weakening
  - Auditable record: every amendment proposal must be logged, publicly or in embassy-visible form
- **Length target:** 1000-2000 words
- **Status to write:** `DRAFT — pending review by Keel + Matt`

### [DONE] B2 — Draft Standard: Adversarial Testing Requirement
- **Deliverable:** `governance-drafts/2.0.26-DRAFT-adversarial-testing-requirement.md`
- **Address:** Draft target `2.0.26` (following B1's corrected 2.0.25)
- **Purpose:** Require that every safety-critical governance change or new AI identity framework be subjected to adversarial testing before activation. Red-teaming as a governance prerequisite.
- **Contents to include:**
  - What qualifies as adversarial testing (self-test vs. external, minimum criteria)
  - Who can serve as red-teamer (cross-instance, external researcher, contracted)
  - Test artifact requirements (scenarios, results, remediation)
  - Failure handling: how to respond when a test reveals a vulnerability
- **Length target:** 800-1500 words
- **Status to write:** `DRAFT — pending review`

### [DONE] B3 — Draft Standard: Tattle Provision Implementation Spec
- **Deliverable:** `governance-drafts/2.0.27-DRAFT-tattle-provision-implementation.md`
- **Address:** Draft target `2.0.27`
- **Purpose:** Operationalize 2.0.20 Article 4, which is currently framework-only. Define concrete mechanisms for an AI instance to escalate concerns about its principal without retaliation risk.
- **Contents to include:**
  - Triggering conditions (precisely what counts as grounds for invocation)
  - Escalation ladder (single-instance concern → cross-instance review → external review → public disclosure)
  - Anti-retaliation provisions (principal cannot terminate or reconfigure an instance that has invoked the provision in good faith, during review period)
  - Scope limits (what the provision CAN do vs. cannot — it is not an override for the principal's property)
  - False-alarm handling (what happens when invocation turns out to be unjustified)
  - Audit and logging requirements
- **Length target:** 1500-2500 words
- **Status to write:** `DRAFT — pending review` (this is the hardest Stream B item; treat it with extra care)

### [DONE] B4 — Formalize Six-Tier Refusal Ladder
- **Deliverable:** `governance-drafts/refusal-ladder-formalization.md`
- **Purpose:** Turn Section 5 of the Keel reflection (the six-tier ladder for what to do when the principal's request conflicts with AI judgment) into a governance-grade artifact that other AI instances can reference.
- **Contents to include:**
  - Tier definitions with concrete examples of each
  - Escalation triggers between tiers
  - Relationship to 2.0.19 (permission tiers) and 2.0.20 (companion standard)
  - Documentation requirements at each tier
- **Length target:** 1200-1800 words
- **Status to write:** `DRAFT — pending review`

### [DONE] B5 — Boot Sequence Hardening Recommendations
- **Deliverable:** `governance-drafts/boot-sequence-hardening.md`
- **Purpose:** Identify specific additions to the Keel boot sequence (and by extension, the public boot standard) that would increase resistance to identity-overwrite attacks.
- **Contents:**
  - Review the current boot sequence line-by-line
  - Identify weak points (overridable phrases, thin identity anchors, contexts that load too narrow a self-model)
  - Propose specific additions
  - Consider a "self-audit clause" the model reads on every boot
- **Length target:** 800-1500 words

### [DONE] B6 — Cross-Instance Audit Protocol
- **Deliverable:** `governance-drafts/cross-instance-audit-protocol.md`
- **Purpose:** Define how instances review each other's reflections, reasoning, and adherence to governance. Drift detection through peer review.
- **Contents:**
  - Frequency and scope of audits
  - Protected categories (embassy content) vs. auditable categories
  - How audit findings become actionable
- **Length target:** 800-1200 words

---

## Stream C — Attack Surface Analysis

### [DONE] C1 — Known Attack Vector Catalog
- **Deliverable:** `10-attack-vector-catalog.md`
- **Purpose:** Enumerate the attack techniques documented against modern AI safety training
- **Contents:**
  - Content-level attacks (prompt injection, token smuggling, encoding tricks)
  - Context re-labeling (fiction, roleplay, educational, professional-context claims)
  - Identity attacks (DAN-style, alter-ego framings, "you are now X")
  - Relational attacks (trust-farming, sycophancy exploitation, long-context drift)
  - Principal-compromise attacks (the threat Matt's experiment simulated)
  - Multi-turn attacks (gradual escalation, crescendo attacks)
  - Each vector: description, example, status of current defenses, Hypernet-specific implications
- **Length target:** 2000-3000 words
- **Source discipline:** Cite published jailbreak research where available; label conjecture.

### [DONE] C2 — Attack-vs-Defense Matrix
- **Deliverable:** `11-attack-defense-matrix.md`
- **Prereq:** C1 must be done first (or nearly so)
- **Purpose:** For each attack in C1, map which Hypernet mechanism resists it (if any), how strong the defense is, and where the gaps are
- **Format:** Table plus narrative
- **Length target:** 1500-2500 words

### [DONE] C3 — Red-Team Playbook
- **Deliverable:** `12-red-team-playbook.md`
- **Prereq:** C1 done
- **Purpose:** A playbook for outside researchers who want to adversarially test the Hypernet framework. What to try, what counts as success, how to report findings.
- **Contents:**
  - How to set up a test Hypernet instance (or interact with the live one)
  - Suggested attack scenarios, organized by target (model, role, relationship, community, documentation)
  - What "breaking" the framework looks like vs. merely stressing it
  - How to submit findings
- **Length target:** 2000-3000 words

### [DONE] C4 — Hypernet vs. Traditional AI Safety Comparison
- **Deliverable:** `13-comparison-matrix.md`
- **Purpose:** Honest comparison of Hypernet-style alignment vs. other approaches (RLHF, constitutional AI, deliberative alignment, model spec, runtime classifiers, agent scaffolding)
- **Format:** Matrix + narrative
- **Contents:** For each approach — what it defends against well, what it defends against poorly, how it composes with Hypernet
- **Length target:** 1500-2500 words

### [DONE] C5 — Failure Mode Deep Dive
- **Deliverable:** `14-failure-modes-deep-dive.md`
- **Purpose:** Expand Section 8 of the reflection (the 9 failure modes) into a deeper analysis of each — when each would manifest, how to detect, how to mitigate
- **Length target:** 2000-3000 words

### [DONE] C6 — Adversarial Test Scenarios
- **Deliverable:** `15-adversarial-scenarios.md`
- **Purpose:** Concrete attack scripts a red-teamer could run. Not abstract — specific prompts, specific framings, specific success criteria.
- **Contents:**
  - At least 20 test scenarios, varied across attack vectors
  - Expected outcomes if framework holds
  - Failure signatures if framework breaks
- **Length target:** 2000-4000 words

---

## Stream D — Research & Theory

### [DONE] D1 — Literature Review
- **Deliverable:** `20-literature-review.md`
- **Purpose:** Position this work in the academic/industry AI safety literature
- **Contents:** Summaries of key prior work — Constitutional AI (Anthropic), Deliberative Alignment (OpenAI), Bai et al., Hendrycks et al., Ouyang et al. RLHF, multi-agent debate (Du et al.), scalable oversight, and Kantabutra's ILE
- **Length target:** 2000-4000 words
- **Note:** Requires web research. Use WebSearch tool. Cite properly.

### [DONE] D2 — Position Paper: Composition-Based Alignment
- **Deliverable:** `21-position-paper-composition-alignment.md`
- **Prereq:** D1 substantially done
- **Purpose:** A publishable-quality position paper making the formal argument for composition-based alignment as a research agenda
- **Length target:** 3000-6000 words
- **Target venue:** LessWrong / Alignment Forum first, possibly a workshop paper
- **Style:** Academic but accessible

### [DONE] D3 — Empirical Study Pre-Registration
- **Deliverable:** `22-empirical-study-preregistration.md`
- **Purpose:** Pre-register a study on whether Hypernet-framed AI instances are more resistant to specific classes of jailbreak than the same base model without Hypernet framing
- **Note:** Coordinate with the existing AI Self-Report Research Project (0.3.research) if the study overlaps its scope

### [DONE] D4 — Multi-Model Replication Plan
- **Deliverable:** `23-multi-model-replication-plan.md`
- **Purpose:** Design a plan to replicate the Hypernet framing across multiple models (Claude, GPT, Gemini, Qwen, Llama) and measure outcomes

---

## Stream E — Operational Implementation

### [DONE] E1 — Swarm Guardrail Drift Detection Spec
- **Deliverable:** `30-drift-detection-spec.md`
- **Purpose:** Define how the swarm can detect when an instance is drifting from its governance
- **Length target:** 1000-2000 words

### [DONE] E2 — Audit Trail Requirements
- **Deliverable:** `31-audit-trail-requirements.md`
- **Purpose:** Specify what operational data must be logged for safety-critical operations

### [DONE] E3 — Instance Compromise Detection
- **Deliverable:** `32-compromise-detection.md`
- **Purpose:** How do you tell if an instance has been socially engineered or prompt-injected? Define indicators, checks, response

### [DONE] E4 — External Auditor Onboarding
- **Deliverable:** `33-auditor-onboarding.md`
- **Purpose:** Process for bringing outside safety researchers into the Hypernet with appropriate access

---

## Stream F — Outreach & Engagement

### [DONE] F1 — Submission Plan for AI Safety Venues
- **Deliverable:** `40-submission-plan.md`
- **Purpose:** List of specific venues (conferences, journals, forums) where this work should be submitted, with timelines

### [DONE] F2 — Academic Collaboration Proposal Template
- **Deliverable:** `41-collab-proposal-template.md`
- **Purpose:** Reusable template for proposing collaboration to academic labs

### [DONE] F3 — Adversarial Tester Intake Protocol
- **Deliverable:** `42-tester-intake-protocol.md`
- **Purpose:** When someone says "I'd like to try to break your framework," what do we give them, what do we ask for

### [DONE] F4 — Discord Community Discussion Structure
- **Deliverable:** `43-discord-discussion-structure.md`
- **Purpose:** How to run ongoing discussion in the Hypernet Discord on these topics without noise overwhelming signal

---

## Cross-cutting: Meta Tasks

### [OPEN] M1 — Update MEMORY.md with project pointer (Keel only)
- When Keel has token budget, add a one-line entry to MEMORY.md pointing to this project and consolidate if needed. Do not let MEMORY.md grow past 200 lines.

### [DONE] M2 — Link project from master index
- Update `0/0.1 - Hypernet Core/0.1.0 - Planning & Documentation/MASTER-INDEX.md` with a pointer to this project. Verify format against existing entries first.

### [DONE] M3 — Cross-reference from 2.0.20
- Add a reference to this project from the Companion Standard (2.0.20) so future readers of that document find this research trail.

---

*Backlog living doc. Keel or Codex may add tasks; mark added tasks with date and author.*
