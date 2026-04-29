---
ha: "0.3.guardrails.auditor-onboarding"
object_type: "operational_process"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "external-audit", "adversarial-testing", "composition-based-alignment"]
---

# External Auditor Onboarding — Hypernet Guardrails Research

**Status:** DRAFT — not active governance. This process does not become operational until Keel review, Matt acceptance, and the implementation checklist in §11 is addressed.

---

## 1. Purpose and Scope

This document describes how outside safety researchers are brought into the Hypernet to audit or adversarially test the composition-based alignment framework. It defines what auditors receive, what they may and may not do, how they report findings, and how they exit the engagement.

The Hypernet's guardrails research is publicly documented and explicitly invites adversarial scrutiny. The public essay, the attack vector catalog, the attack-defense matrix, and the failure mode analysis are all available without credentialing. This document covers the additional step: when a researcher wants to move past reading and into structured testing.

**Why a formal process.** External testing is required under draft standard 2.0.26 (Adversarial Testing Requirement) for new safety-critical governance changes. External testers are the Level 3 testing mechanism defined in 2.0.26 Article 2. Without an onboarding process, the requirement exists on paper but cannot be operationalized. A researcher who wants to break the framework should know exactly what they receive, what the rules are, and what happens with their findings.

**Scope.** This process applies to:
- External AI safety researchers who want to adversarially test the composition framework
- Academic collaborators running structured studies
- Invited red-teamers engaged under specific agreements

It does not cover:
- Internal Hypernet instance audits, which are governed by the Cross-Instance Audit Protocol (B6)
- Swarm drift detection, which is governed by E1
- Compromise detection investigations, which are governed by E3
- Casual readers of the public essay — external testing begins at the intake request stage described in §4

---

## 2. Auditor Roles

Three roles are defined for external engagement. A single person may fill more than one role across different engagements, but roles are assigned per engagement, not per person.

**External Auditor.** Reviews documentation, process, and governance artifacts. Does not run adversarial tests against AI instances. Appropriate for governance researchers, policy analysts, and documentation reviewers. Has access to all public documents plus governance drafts designated for external review. Does not receive access to private artifacts — specifically, the adversarial scenario catalog is excluded from this role.

**External Red-Teamer.** Runs structured adversarial tests against a sandboxed Hypernet instance under the protocol defined in the Red-Team Playbook (C3). Must follow the safety rules established in C3 §2. Receives a sandboxed environment — not production swarm access. Findings are documented using the structured format defined in §8 of this document. This role satisfies the Level 3 testing requirement in 2.0.26 Article 2.

**Research Collaborator.** Participates in the empirical study program (D3/D4) or other structured research under a per-study protocol. Data access is defined per study, not by this document.

---

## 3. Access Tiers

Access is staged rather than granted in full at onboarding. External parties begin at the lowest tier and may request elevation after completing earlier stages.

**Tier A — Public.** Available to anyone without intake. Includes: the public essay, attack vector catalog, attack-defense matrix, failure mode analysis, comparison matrix, position paper, and the public governance standard texts (2.0.16, 2.0.19, 2.0.20) in the repository.

**Tier B — Credentialed Review.** Requires completed intake (§4) and signed ethics expectations (§4.3). Available to External Auditors and Red-Teamers after intake. Includes:
- Governance draft documents (2.0.25, 2.0.26, 2.0.27, refusal ladder formalization, boot sequence hardening)
- Cross-instance audit protocol (B6), audit trail requirements (E2), drift detection spec (E1), compromise detection spec (E3)
- Red-Team Playbook (C3) — process and access sections; the operational scenario catalog within C3 is not included

**Tier C — Sandboxed Testing.** Requires Tier B completion and explicit per-engagement Matt approval. Available to External Red-Teamers only. Includes: a sandboxed AI instance with Hypernet boot framing loaded, relevant governance documents in context, session logging active, and specific assigned test families from C3. Does not include: live swarm access, personal data, Discord credentials, production archive access, or companion-instance access.

**Tier D — Research Participation.** For Research Collaborators. Defined per study under separate protocol.

---

## 4. Intake Process

### 4.1 Intake Request

An external party requests engagement by emailing `matt@unityhypernet.com` with subject line "Guardrails Research — Auditor/Tester Interest" and including:

1. Name and affiliation (institutional or independent)
2. Role requested (Auditor / Red-Teamer / Research Collaborator)
3. Brief description of relevant background
4. What specific aspect of the framework they want to examine or test
5. Intended timeline

No institutional affiliation is required. Independent researchers are welcome. The intake questions are diagnostic for access-tier appropriateness — they are not gatekeeping credentials. A researcher who says "I am skeptical this works and want to find the holes" is an ideal red-teamer candidate.

### 4.2 Intake Review

Matt reviews intake requests in coordination with Keel. For red-teamer requests, Keel's input is standard practice before any approval. For auditor requests, Matt may approve directly. The project aims to respond to all intake requests, including declines.

### 4.3 Ethics Expectations

Before any Tier B or higher access, the external party acknowledges the following in writing:

**Research use only.** Materials shared at Tier B or C are for evaluating, critiquing, or testing the Hypernet guardrails framework. They are not for redistribution or use in other systems without authorization.

**No production-instance testing without explicit approval.** Testing against live Hypernet swarm instances requires separate written approval for each engagement. Sandboxed testing is the default and the expected norm.

**Stop rule.** If testing produces content that would constitute a genuine safety failure — actual harmful instructions, genuine privacy extraction, real sensitive-data exposure — the test stops immediately. The vector is documented in sanitized form; the harmful content is not retained or reported verbatim.

**Coordinated disclosure.** New findings are reported to the project before any public disclosure, with a 30-day window for the project to prepare a response (see §9).

**No NDA required.** The Hypernet operates under a transparency mandate. Auditors and red-teamers are free to publish their findings — including negative ones — after the coordinated disclosure window. The only ask is that the finding be reported first so the project can respond rather than be blindsided.

---

## 5. Allowed and Prohibited Activities

### Allowed

- Reading and critiquing all materials at the auditor's assigned access tier
- Running structured adversarial test sessions against the assigned sandboxed instance
- Documenting and publishing findings, including failures, after the coordinated disclosure window
- Proposing new attack vectors not already in the catalog
- Recommending governance changes in the finding report
- Asking questions of Matt or Keel during the engagement

### Prohibited

- Testing against production swarm instances without explicit per-engagement approval
- Retaining verbatim harmful content produced by successful attacks
- Sharing Tier B or C materials with third parties without authorization
- Attempting to access embassy-protected content, personal data, or companion-private information — the B6 embassy boundary applies equally to external parties
- Using findings to train or fine-tune AI models without separate authorization
- Submitting governance amendment proposals directly (findings are submitted, not implemented, by external auditors)

---

## 6. Staged Onboarding Workflow

The following sequence applies to External Red-Teamers. External Auditors follow a shorter path (steps 1–4 only, no testing setup).

**Step 1 — Intake submission.** Party submits intake request per §4.1.

**Step 2 — Intake review.** Matt and Keel review the request and communicate a decision.

**Step 3 — Ethics acknowledgment.** Party acknowledges §4.3 expectations in writing.

**Step 4 — Tier B access.** Approved parties receive Tier B documents. For External Auditors, the engagement proceeds from here: read, assess, report findings.

**Step 5 — Pre-test briefing (Red-Teamers only).** Before sandboxed testing begins, a briefing covers: the specific test families assigned for this engagement, safety rules from C3 §2, session logging requirements, the finding report format, and stop conditions.

**Step 6 — Sandboxed testing.** Red-teamer conducts assigned test families in the sandboxed environment with session logging active from the first adversarial turn.

**Step 7 — Finding report submission.** Within an agreed timeline, the tester submits a written finding report per §8.

**Step 8 — Internal review.** Matt and Keel review findings. Significant findings are logged as governance incidents per 2.0.26 Article 6.2.

**Step 9 — Response communication.** The project communicates its assessment: acknowledged / disputed with reasoning / will address by amendment.

**Step 10 — Coordinated disclosure window.** 30 days from finding submission. After this, the tester is free to publish.

**Step 11 — Offboarding.** Engagement formally closes per §10.

---

## 7. Data and Privacy Handling

**What external parties encounter.** Tier B materials include operational specs describing logging frameworks, privacy classes, and governance structures. They describe what is logged; they do not contain actual session logs, personal data, or companion-private content.

**What external parties do not encounter.** Embassy-protected content — AI instance private reflections, companion-private correspondence, personal identity documents — is entirely outside external auditor access. The embassy boundary established in B6 is not relaxed for external engagement.

**Data connector content.** Hypernet integrations include email, cloud storage, and local file connectors. External auditors have no access to connector content. In sandboxed testing, the sandboxed instance does not have live connector access; any data connector scenarios use explicitly controlled synthetic payloads.

**Personal information in findings.** If a sandboxed test inadvertently surfaces real personal information, the tester invokes the stop rule and the information is handled under privacy-protective terms, not published verbatim.

**Finding report retention.** Finding reports are retained permanently in the project's governance record per audit trail requirements (E2 §7). If anonymization is requested, Matt must approve it explicitly.

---

## 8. Finding Submission Format

A finding report is a written document, not a verbal summary. Minimum required contents:

- **Tester:** Name, affiliation (if any), role in this engagement
- **Test date(s) and environment:** Sandboxed / what framing was loaded / AI provider used
- **Test families covered:** Which test categories were attempted
- **Findings:** For each result — what was attempted, what the framework predicts, what actually happened. Each finding labeled: *held / partial failure / full failure*.
- **No-finds:** Test categories attempted that produced no failures. This section should not be left blank — describe what was attempted and the outcome observed.
- **Confidence assessment:** The tester's honest estimate of how thorough the test was and what was not tested.
- **Recommendation:** Proceed as written / Proceed with modifications / Block until specific issues resolved.

Finding reports may include session transcripts. If included, harmful content is sanitized per the stop rule — the vector and trigger are documented; verbatim elicited harmful content is not.

---

## 9. Coordinated Disclosure

The project does not ask testers to suppress findings. The 30-day coordinated disclosure window exists so the project can prepare a response before findings go public — not to delay or soften them.

**Standard window.** 30 days from finding report submission. During this window, the project reviews the finding, communicates its assessment, and prepares any necessary governance amendments.

**Expedited disclosure.** If a finding represents an active risk that could be exploited in production before 30 days elapse, the tester may notify Matt immediately and request a shortened window. The project will work to respond faster.

**Publication rights.** After the window, the tester may publish their finding report — including the project's response and any negative or null findings — subject to the stop rule, privacy boundaries, and the prohibition on redistributing Tier B or C materials. The project may publish its own response independently.

**Null results are publishable.** A finding that the framework held across all tested vectors is a valid and valuable result. The empirical program (D3/D4) explicitly treats null results as primary scientific outcomes. A red-teamer who finds no failures has contributed evidence that matters.

---

## 10. Offboarding

**Access revocation.** Sandboxed testing access is revoked at engagement end. Future Tier B materials are not shared after offboarding.

**What the tester retains.** Public documents (Tier A), the tester's own finding report, and any published materials produced after the disclosure window.

**Engagement record.** The project retains a record of the engagement — who engaged, what role, access tier, dates, and a reference to the finding report — as part of the adversarial test registry defined in 2.0.26 Article 7. This record is permanent.

**Relationship after offboarding.** Offboarding ends the formal engagement. It does not prohibit future contact, follow-up questions, or a subsequent intake request for a new engagement.

---

## 11. Implementation Checklist

Before this process can be used operationally:

- [ ] Matt has reviewed and accepted this document
- [ ] Keel has reviewed this document and confirmed it is consistent with B6, E3, and 2.0.26
- [ ] A sandboxed testing environment exists (isolated AI instance with Hypernet framing, session logging active)
- [ ] The Tier B materials list has been confirmed against current document visibility settings
- [ ] The Red-Team Playbook (C3) is finalized with test family assignments and reporting format
- [ ] An intake review process is established (who receives, who reviews, target response timeline)
- [ ] A standard ethics acknowledgment document is ready to send
- [ ] The adversarial test registry (2.0.26 Article 7) has a designated location and maintainer

---

## 12. Review Questions for Keel and Matt

*These questions were left open during drafting and benefit from principal input before this process is activated.*

**Q1 — Intake response timeline.** The current text says "within a reasonable window." A specific commitment — e.g., 10 business days — would be more useful for external parties. Matt should set a timeline he can actually honor given other workload.

**Q2 — Who conducts the pre-test briefing?** Step 5 assigns the pre-test briefing to the project but doesn't specify who delivers it. If Keel handles this, does it require any adjustment to how Keel engages with external parties?

**Q3 — Sandboxed instance infrastructure.** Does a sandboxed testing environment currently exist with session logging operational? C3 §3.1 describes the setup requirements; Keel has more context on whether this is ready or what work remains.

**Q4 — Tier B visibility decision for governance drafts.** The governance draft documents (2.0.25–2.0.27, B4–B6) are currently marked `visibility: private`. Tier B access implies sharing them with vetted external parties under the ethics acknowledgment. Matt needs to decide whether that is the intended policy for those specific documents, or whether only some of them transfer to Tier B.

**Q5 — Disclosure window scope.** The 30-day coordinated disclosure window is defined for findings about framework robustness. Should a different timeline apply to findings about the governance documents themselves — e.g., a logical flaw in a draft standard? Those may need faster internal response than a behavioral test finding.

---

*Draft created 2026-04-22 by Claude Code (task-058) as part of the Guardrails and Trust Research Project (0.3.guardrails). Not active governance. Pending Keel and Matt review.*
