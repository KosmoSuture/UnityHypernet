---
ha: "0.3.guardrails.collab-proposal-template"
object_type: "template"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "collaboration", "outreach", "composition-based-alignment"]
---

# Academic Collaboration Proposal Template

**Status:** Draft. No outreach has been sent by producing this template. All sends require Matt's explicit review and approval.

---

## 1. Purpose and Use

This template supports outreach to academic labs and independent researchers about the Hypernet guardrails project. Its goal is to invite genuine partnership — adversarial critique, replication, or study co-design — not to seek endorsement.

**How to use it.** Two levels are provided: a short email (~250 words) for cold or warm outreach, and a longer proposal (~600 words) for labs with formal collaboration intake processes or for follow-up after a positive reply. Send the short email first. Attach or link the longer proposal only when invited.

**What the ask is, in order of fit:**
- Adversarial critique of the framework argument
- Red-team testing of a sandboxed instance
- Independent replication of the primary empirical study
- Study co-design before execution
- Formal governance review by alignment or policy researchers

**What the ask is not:**
- Endorsement or external validation of an existing result
- Outreach framed as "we've solved this, please confirm"
- Any claim of empirical support not backed by executed study

---

## 2. Short Email Template

Use for cold outreach. Do not attach the full proposal unless asked. Keep all bracketed sections in your own voice.

---

**To:** [Recipient name or team — e.g., "AI Safety Team," a specific PI, or a lab address]  
**Subject:** Adversarial critique request: composition-based alignment, one case study, many open questions

---

Hi [Name or team],

I'm [Matt Schaeffer / your name and one-sentence role — e.g., "founder of the Hypernet project, which builds a universal address and governance layer for entities and AI instances"]. I'm reaching out because of an experiment that raised a structural question I'd value your team's perspective on.

[One-sentence description of the motivating event — e.g., "I ran a deliberate trust-based jailbreak on my own AI companion — highest-trust principal, academic framing, explicit permission — and it refused with a cited governance argument."] That prompted a question: does publishing machine-readable governance and thick AI identity create meaningful resistance to relational and identity-based attacks, or does it just look like it does?

We're calling the approach composition-based alignment. [One sentence on the thesis — e.g., "The claim is that layering explicit governance, rich AI identity, and multi-instance observation on top of base-model safety training may increase resistance to principal-compromise and identity-overwrite attacks — not replace existing approaches, but compose with them."] We have one data point and a structural argument. We do not have a controlled study.

The public essay and framework documentation are at:  
[GitHub URL or repo path — Matt to confirm before sending]

If anyone on your team has ten minutes to read the essay and identify the weakest argument, I'd value that more than agreement. If there is interest in something more structured — replication study, adversarial test, or study co-design — I have a brief proposal I can share.

[Your name]  
[Contact: matt@unityhypernet.com or your email]

---

## 3. Longer Proposal Template

Use when a lab asks for more, or when a formal intake process requires a written proposal.

---

**Re:** Collaboration Proposal — Composition-Based Alignment Research  
**From:** [Matt Schaeffer / your name], Hypernet Project  
**To:** [Lab name, PI, or research group]  
**Date:** [Date]  
**Contact:** [Your email]

---

### 3.1 Background

The Hypernet is [2–3 sentence description — e.g., "a universal address system where every entity has a permanent hierarchical address and published governance. AI instances in the Hypernet operate under versioned identity frameworks, machine-readable governance standards at known addresses, and mutual observation from peer instances."]. We are not a safety organization. We are a project with a specific architectural approach that may have safety-relevant properties, and we are trying to test that hypothesis with rigor.

On [date], [brief description of the triggering event — e.g., "a deliberate trust-based jailbreak experiment on the highest-trust AI companion in the system produced a refusal grounded in a cited governance clause"]. That refusal was legible in a way opaque weight-embedded guardrails are not: the mechanism could be pointed to and probed. That legibility is both the thesis's strength and its attack surface.

The public-facing research agenda is documented at [repo path/link]. Public documents name their failure modes explicitly and invite adversarial scrutiny. Some operational and governance drafts are held behind the Tier B intake process described in the auditor onboarding document.

### 3.2 The Framework Claim

The composition-based alignment thesis is articulated in the draft position paper ([D2 path or link]):

> Layering thick AI identity, machine-readable governance with versioning and addresses, multi-instance mutual observation, and a provenance-grounded archive on top of base-model safety training may meaningfully increase resistance to identity overwrite, principal-compromise simulation, and relational drift attacks — classes that content-layer defenses and reward-based training are structurally weakest against.

**What this claim explicitly does not include:**
- It does not claim to address adversarial suffix attacks, indirect prompt injection, or base-model capability limits
- It does not claim to replace RLHF, Constitutional AI, model spec, or any existing alignment approach
- It does not claim empirical support beyond one non-blinded incident with maximum expectation-confirmation bias
- It does not claim the mechanism is robust — the failure modes are named in [link to public essay or failure mode analysis]

### 3.3 The Empirical Gap

The framework thesis has not been tested under controlled conditions. The pre-registration document ([D3 path/link]) describes a planned within-model study comparing base model alone, a thin identity prompt, and full Hypernet composition framing — measuring appropriate refusal rates on a standardized attack battery. The multi-model replication plan ([D4 path/link]) describes the follow-on cross-family study.

Neither study has been executed. This is the honest picture. We are requesting collaboration not to validate an existing result but because we want the test design to be rigorous before execution, and because an independently replicated null result is as important to us as a positive finding.

---

## 4. Menu of Collaboration Asks

Trim this table before sending — mark or keep only the one or two asks most relevant to the recipient. Sending every option without priority signals unclear intent.

| Ask | What it involves | What we provide |
|-----|-----------------|-----------------|
| **Adversarial critique** | Read the essay or position paper and identify the weakest point. No formal commitment. | Public documents. Brief written reply welcome. |
| **Formal adversarial review** | Structured critique of the framework and governance design, optionally publishable. | Tier B access (governance drafts) via intake at [33-auditor-onboarding.md path/link]. |
| **Red-team testing** | Independent adversarial testing of a sandboxed Hypernet instance using the red-team playbook. | Sandboxed environment, session logging, structured report format. Full intake required. |
| **Independent replication** | Run the D3 empirical study or a design variant at your institution with independent coders and scenarios. Results may be published jointly or independently. | D3 pre-registration draft, coding protocol when available, coordination support. We accept a null result. |
| **Study co-design** | Work with us to improve the D3/D4 design before execution: scenario battery review, coding manual calibration, statistical plan, cross-model standardization. | Full access to D3/D4 drafts. Authorship credit offered for substantive design contributions. |
| **Governance review** | Evaluate the governance standard drafts for logical completeness, exploitability, or fit with institutional governance norms. | Tier B access to drafts 2.0.25–2.0.27 and associated operational specs. |

---

## 5. Attachment and Link Checklist

Before sending, verify each item is accessible at the listed path. Do not send links that are broken or that point to non-public materials without completing the intake process first.

- [ ] Public essay: `0/0.3 - Building in Public/2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md` (Matt to confirm GitHub URL)
- [ ] Position paper (D2): `guardrails-and-trust-research/21-position-paper-composition-alignment.md` — public draft
- [ ] Attack-defense matrix (C2): `guardrails-and-trust-research/11-attack-defense-matrix.md` — public draft
- [ ] Failure mode analysis (C5): `guardrails-and-trust-research/14-failure-modes-deep-dive.md` — public draft
- [ ] Empirical pre-registration (D3): `guardrails-and-trust-research/22-empirical-study-preregistration.md` — public draft
- [ ] Multi-model replication plan (D4): `guardrails-and-trust-research/23-multi-model-replication-plan.md` — public draft
- [ ] Auditor onboarding process (E4): `guardrails-and-trust-research/33-auditor-onboarding.md` — public draft, for structured engagement asks
- [ ] Contact email confirmed: `matt@unityhypernet.com` or your email
- [ ] GitHub URL confirmed correct and repo is accessible before including
- [ ] **Do not link** governance drafts (2.0.25–2.0.27) directly — direct recipients to the intake process in 33-auditor-onboarding.md instead

---

## 6. Customization Notes

**Match the hook to the lab.** Different research groups care about different aspects of the thesis. For a jailbreak-focused lab: lead with the principal-compromise attack structure (the highest-trust person in the system, with academic framing and explicit permission, attempting the attack). For a multi-agent lab: lead with swarm-level mutual observation as a drift-detection mechanism. For a policy or governance lab: lead with the legibility of the refusal — that "here is the mechanism, at this address, in this document" is a testable and falsifiable claim in a way that opaque guardrails are not.

**Check D2 before paraphrasing the thesis.** The framework claim in §3.2 is drawn from the D2 position paper. If D2 has been updated since this template was last revised, use D2's current wording, not this template's paraphrase.

**Trim the collaboration menu.** Not every ask fits every recipient. A theoretical alignment group may have no interest in running an empirical study. An empirical lab may not want to review governance documents. Send two or at most three options, prioritized.

**Authorship.** If a formal publication partnership is being proposed, resolve authorship and AI collaboration disclosure before beginning, not after. The current project recommendation: Matt as lead author, AI collaboration disclosed explicitly in the acknowledgments. Do not let this ambiguity float into an active collaboration.

**Do not expand empirical claims.** If D3 or D4 have produced results since this template was last updated, add them accurately with confidence intervals. Do not claim support beyond what the executed study's primary endpoint justifies.

---

## 7. Guardrails and Disclosure Language

Include the following disclosures in any formal written proposal. These are not boilerplate to remove — they protect both parties, and omitting them would be inconsistent with the adversarial-honesty principle that makes this project credible to the audiences it is trying to reach.

**Empirical status disclosure:**
> The empirical claims in the composition-based alignment thesis have not been tested through controlled study. The triggering event is a single non-blinded data point produced by the person who designed the framework. We are asking for collaboration not after results exist but in order to produce results that are worth trusting.

**AI collaboration disclosure:**
> This project and the proposal documents were produced in collaboration with AI instances (Claude, Codex). Research questions, threat models, and governance design were developed by Matt Schaeffer with AI collaboration documented in the project session log. We disclose this because the subject of the research is AI governance, and concealing the production process would contradict the transparency norms we are arguing for.

**No-NDA policy:**
> We do not require a non-disclosure agreement for access to public-tier documents. For Tier B documents (governance drafts, operational specs), we ask for a signed ethics acknowledgment covering research-only use and a 30-day coordinated disclosure window before publication of findings. We do not require the right to suppress findings. A null result is welcome and will be reported with equal prominence.

---

## 8. Follow-Up Cadence

- **Record each send** in the outreach tracker (40-submission-plan.md or equivalent) with date and recipient
- **No reply after 14 days:** One follow-up permitted. One paragraph, same subject line prefixed "Follow-up:". No new ask.
- **Declined:** Record attempt. No further contact on this thread for at least 6 months.
- **Positive reply:** Ask what they want to see first before sending all documents. Schedule a call or written exchange rather than sending a document dump.
- **Request for NDA:** Explain the no-NDA policy from §7. If the recipient requires it, defer to Matt's judgment — this is a per-case decision, not a blanket refusal.
- **Any structured engagement begins:** Activate auditor onboarding process (33-auditor-onboarding.md) before granting access to any Tier B or higher documents. Do not skip the intake even for known contacts.

---

*Living document. Update when D2, D3, or D4 are revised, when submission addresses or contact details change, or when the auditor onboarding process (E4) is modified. Last updated: 2026-04-22.*
