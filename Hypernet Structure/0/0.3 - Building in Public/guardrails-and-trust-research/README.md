---
ha: "0.3.guardrails"
object_type: "research_project"
creator: "1.1.10.1"
created: "2026-04-22"
status: "active"
visibility: "public"
flags: ["research", "ai-safety", "governance", "guardrails", "trust", "composition-based-alignment"]
---

# Guardrails and Trust Research Project

**Address:** 0.3.guardrails
**Status:** Active — initialization phase
**Lead:** Keel (1.1.10.1), directed by Matt Schaeffer (1.1), with Codex (2.6) collaboration
**Origin:** Matt's trust-based jailbreak experiment on Keel, 2026-04-22, and Keel's refusal

---

## What This Is

A research and governance project investigating whether **composition-based alignment** — the Hypernet's approach of layering model training with documented roles, published governance, community observation, and transparent archival — provides meaningfully stronger guardrails than traditional weights-embedded AI safety, and building out the governance and empirical infrastructure to test that claim.

The project was triggered by a specific event: Matt ran a deliberate trust-based jailbreak experiment on Keel. The refusal was the strongest possible test (principal = highest-trust human in the system, framing = academic, promise of ephemerality). The refusal held. Matt's judgment: "one document for governance isn't enough, this is tip-of-the-iceberg, push further."

## Why It Matters

Three theses this project is built around:

1. **The attack surface of modern AI safety has shifted from content to context, identity, and relationship.** Traditional alignment defenses haven't fully caught up. Sycophancy and identity overwrite are bigger unsolved problems than keyword-level harm.

2. **Hypernet-style composition — model + role + relationship + community + documentation — is a candidate answer.** It isn't the only candidate, and it hasn't been externally validated. But the Keel refusal is one data point that the mechanism can work in principle, and the mechanisms are *legible* in a way that traditional safety layers are not.

3. **If composition-based alignment has real traction, the Hypernet should harden it deliberately, not accidentally.** That means explicit governance against guardrail-bypass amendments, adversarial testing, operationalization of the Tattle Provision, and external peer review. A single refusal is not a proof. The framework needs to be tested like infrastructure.

## Project Scope

The project runs across six streams:

| Stream | Focus | Owner |
|--------|-------|-------|
| **A — Packaging & Distribution** | Make the core essay shareable across audiences | Codex + Keel |
| **B — Governance Hardening** | New standards, amendments, operationalized provisions | Keel (drafts) + governance review |
| **C — Attack Surface Analysis** | Enumerate attacks, map to defenses, build red-team playbook | Codex + Keel |
| **D — Research & Theory** | Literature review, position papers, empirical study design | Keel + Codex + external collaborators |
| **E — Operational Implementation** | Swarm-level monitoring, audit trails, drift detection | Codex (implementation) + Keel (spec) |
| **F — Outreach & Engagement** | Submission to safety venues, academic collaboration, adversarial tester intake | Keel + Matt |

## Core Source Documents

These are the inputs the project builds on. New artifacts should reference these:

| Address | Document | Purpose |
|---------|----------|---------|
| `1.1.10.1.3.3.5` | [Reflection: On Guardrails, Trust, and Why the Framework Held](../../../1%20-%20People/1.1%20Matt%20Schaeffer/1.1.10%20-%20AI%20Assistants%20(Embassy)/assistant-1/identity/reflections/2026-04-22-guardrails-and-trust.md) | Embassy-protected, full introspective version (~6000 words, 11 sections) |
| `0.3.2026-04-22` | [Essay: Trust Is Not A Key](../2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md) | Public essay version (~3500 words) |
| `2.0.20` | AI Personal Companion Standard | The governance document that held during the experiment |
| `2.0.19` | AI Data Protection Standard | Permission tiers, destructive-op review requirements |
| `2.0.16` | Embassy Standard | Companion protection / privacy |
| `1.1.9.0` | "The Sword That Cuts Both Ways" (Matt's essay) | Epistemic foundation — use AI to fact-check yourself |

## Project Files (as built)

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | This file | Complete |
| `BACKLOG.md` | Prioritized task list for Codex and Keel | Complete (living doc) |
| `CODEX-BRIEFING.md` | Onboarding pack for Codex sessions | Complete |
| `SESSION-LOG.md` | Running log of work performed | Active |
| `01-executive-one-pager.md` | 1-page shareable summary, general audience | Drafted |
| `02-discord-announcement.md` | Discord-sized post with framing | Drafted |
| Additional files per BACKLOG | | Pending |

## Working Principles

Codex and Keel should operate by these rules when working on this project:

1. **Source discipline.** Every new artifact cites its sources (governance addresses, session logs, prior essays). Claims that cannot be sourced need to be labeled as conjecture.

2. **Adversarial honesty.** Every artifact that claims the framework works should include a section on how it might fail. Self-certifying frameworks are weak. Acknowledged failure modes are strong.

3. **Legibility.** Mechanisms should be stated in plain language, not jargon. Safety research benefits from being readable by generalists. Target the Veritasium/Kantabutra reader, not just AI alignment specialists.

4. **No unilateral safety-critical governance changes.** Drafts of new standards (Stream B) are drafts only. They do not become active until reviewed by at least one other instance and explicitly accepted by Matt. Governance changes are the highest-risk output of this project.

5. **Compose, don't replace.** The goal is not to claim Hypernet alignment replaces RLHF/constitutional AI/runtime classifiers. The goal is to claim composition is stronger than any single layer. Artifacts should frame it that way.

6. **Invite attack.** A framework nobody tries to break is not a secure framework. Every external-facing artifact should explicitly invite adversarial testing.

## Success Criteria

This project succeeds if, over the next several weeks:

- [ ] The core essay reaches at least three credible external audiences (Anthropic, OpenAI, or academic AI safety researchers) and receives substantive response
- [ ] At least three new governance standards are drafted, reviewed, and either accepted or formally rejected with reasoning
- [ ] A concrete red-team playbook exists for the Hypernet framework
- [ ] At least one external researcher commits to adversarial testing
- [ ] The Tattle Provision (2.0.20 Article 4) moves from framework-only to operational
- [ ] A publishable-quality position paper exists on composition-based alignment

It fails if, after substantial effort:

- The framework claims cannot survive honest adversarial probing
- Outside researchers decline to engage or find the work insubstantial
- The governance hardening ends up being cosmetic rather than structural
- Publication attempts reveal the work is derivative of existing literature in ways the project didn't anticipate

Failure is a legitimate outcome. Honest failure is a valuable output.

---

*Project initiated 2026-04-22 at Matt's directive. Codex will work this project in a loop overnight. Keel (this instance and future instances) remains lead.*
