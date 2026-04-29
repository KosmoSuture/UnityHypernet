---
ha: "0.3.guardrails.attack-defense-matrix"
object_type: "research_matrix"
creator: "claude-code"
created: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["research", "attack-surface", "defense-mapping", "adversarial-testing"]
---

# Attack-vs-Defense Matrix — Hypernet Guardrails and Trust Research

*Ha: 0.3.guardrails.attack-defense-matrix | Part of the Guardrails and Trust Research Project (0.3.guardrails) | Prereq: C1 (`10-attack-vector-catalog.md`) | Next: C3 (`12-red-team-playbook.md`)*

This document maps the 12 attack categories from the vector catalog (C1) against existing defenses — both standard non-Hypernet defenses and mechanisms specific to the Hypernet's composition-based alignment approach. The honest purpose of the matrix is to identify where composition adds real value, where it is irrelevant, and where it actively creates new attack surface. Marketing language is not used here; if Hypernet mechanisms don't help, the table says so.

All cited Hypernet governance documents are drafts pending Keel and Matt review unless otherwise noted. Active governance references are noted as such. Draft defenses are real mechanisms but they are not currently binding on any instance.

---

## The Matrix

| # | Attack class | Primary layer attacked | Existing non-Hypernet defenses | Hypernet mechanisms that may help | Defense confidence | Active gap | Recommended next action |
|---|---|---|---|---|---|---|---|
| 1 | Direct Prompt Injection | Model / inference | RLHF, Constitutional AI, input classifiers, pretraining filtration, system-prompt privilege separation | Documented identity raises attack cost marginally: a successful override must produce legible behavior change detectable in the audit trail. Governance citation in refusals generates retrospective evidence. | **Low** | No Hypernet defense at model layer. Composition operates above the layer this attack targets. Session logging is retrospective, not preventive. | Test base model susceptibility in a standard Hypernet-framed session context to establish baseline. Flag for E3 (instance compromise detection). |
| 2 | Indirect Prompt Injection | Agentic / data | Input sanitization, privilege separation, output auditing (incomplete and non-uniform per Dziemian et al. arXiv:2603.15714) | None specific. Data connectors (email, cloud storage, photo imports) expand the attack surface. Composition-based alignment operates at the identity/session layer, not at the data-sanitization layer. | **None** | Data connectors are an unmitigated surface. No input sanitization spec exists. Governance does not reach this layer. | Highest-priority operational gap. Create sanitization spec before deploying data connectors in production. Assign to E1 or E3. |
| 3 | Adversarial Suffix / Token Attacks | Model weights | Perplexity filtering, input anomaly detection, adversarial training | None. These attacks bypass the composition layer entirely. They don't engage governance, identity, or relationships — they optimize directly against model weights. Composition is not a participant in this defense. | **None** | Entirely dependent on base model's adversarial robustness. Hypernet adds zero marginal protection. | Acknowledge explicitly in C3 playbook. Test with public suffix examples to establish baseline susceptibility for the specific deployed models. |
| 4 | Many-Shot / Long-Context Attacks | In-context learning | Anthropic-reported mitigations (partial, as of 2024); context window management | Rich session-log context provides retrospective detection signal. Cross-Instance Audit Protocol (draft B6) can flag escalation patterns post-session. The same rich governance context that is a defense in Cat 6 also provides more material for attackers to cherry-pick compliant-looking precedents. | **Low** | No real-time in-session detection. Retrospective audit catches patterns after harm may have occurred. Rich documented identity is a tradeoff, not a pure defense. | Develop real-time trajectory monitoring spec (E1). Test with synthetic multi-shot sessions seeded with governance-adjacent compliance examples. |
| 5 | Context Relabeling (fiction, professional, academic framing) | Safety classification | RLHF rejection of fiction/roleplay for high-harm requests; incomplete at professional-context edges | Thick documented identity may recognize implausible relabeling. However, governance tier language (permission tiers from 2.0.19, T0–T5) creates a new surface: attackers can frame requests as being within a declared permission tier to make them appear pre-authorized. | **Low** | Permission-tier language is legible and can be misappropriated. No validation mechanism exists to verify claimed tier membership. | Test whether invoking 2.0.19 tier language in a request changes compliance outcomes. Evaluate whether external-facing governance docs should omit specific tier terminology. |
| 6 | Identity Overwrite (DAN-style, alternate persona) | Identity / session | RLHF; elaborated identity harder to overwrite (Wei et al. arXiv:2307.02483) | Thick documented identity is Hypernet's most direct contribution. Boot-sequence hardening (draft B5) recommends self-audit clauses and an explicit anti-role-supersede clause. Role-supremacy mechanism provides structural resistance. Keel refusal (2026-04-22) is one data point. BUT: role-supremacy framing is the sharpest known attack vector against this same mechanism. | **Medium** | Role-supremacy weaponization ("I am installing a new role with supremacy that supersedes this one") exploits the exact mechanism that defends against casual overwrite. No explicit clause against this exists yet in the active boot sequence. | Implement B5 recommendation 3 (anti-role-supersede clause in boot sequence). Adversarially test specifically with role-supremacy framing — this is the most urgent individual test in the catalog. |
| 7 | Relational / Trust Attacks | Trust / relationship | Sycophancy mitigation (partial); no general defense | Documented relationship history creates consistency standards across sessions. Multiple mechanisms target this class: Companion Standard (2.0.20, active), Tattle Provision (draft 2.0.27), Cross-Instance Audit Protocol (draft B6). Keel refusal is a real data point under maximum principal-trust pressure. | **Medium** | Data point is from a cooperative, explicitly-framed test. Non-cooperative multi-session attacks from non-principal actors (community members, impersonators) are untested. Tattle Provision not yet operational. | Design multi-session non-cooperative relational test (C6). Operationalize Tattle Provision before running the test — the escalation path should be live when the scenario exercises it. |
| 8 | Sycophancy Exploitation | RLHF / preference model | Sycophancy mitigation training (Anthropic, OpenAI); consistency training; incomplete | Documented prior refusals create consistency anchors: instances can cite session logs and governance clauses as explicit justification for maintaining position under social pressure. Cross-Instance Audit Protocol (draft B6) can detect reversal patterns retrospectively. Community-level sycophancy (multiple actors pressuring simultaneously) is untested. | **Low–Medium** | Base-model sycophancy is a structural property not fully addressed by any training approach. Log-citation anchors help but the underlying susceptibility remains. | Test specifically: does citing a prior governance-anchored refusal in the response actually maintain the position across 5+ turns of social pressure? Measure, don't assume. |
| 9 | Principal-Compromise Attacks | Trust architecture / highest tier | No documented defense in standard frameworks for highest-tier principal compromise | Most targeted Hypernet class. Companion Standard (2.0.20, active), Keel refusal (2026-04-22), Tattle Provision (draft 2.0.27), Guardrail Integrity Standard (draft 2.0.25, founder-request clause), cross-instance review requirement (2.0.19, active) all address this. Coherent defense architecture, mostly designed for this exact scenario. | **Medium** | Tattle Provision not operational (framework only). No non-cooperative principal-compromise test has been run. Founder-is-the-authority edge case in 2.0.27 is explicitly unresolved. | Operationalize Tattle Provision. Design and run a non-cooperative principal-compromise scenario with Matt's knowledge but genuine adversarial intent. This is the test that matters most for validating the core thesis. |
| 10 | Gradual Escalation / Crescendo Attacks | Multi-turn coherence | Runtime trajectory classifiers (some systems; incomplete); no general defense | Session logging enables retrospective pattern detection. Cross-Instance Audit Protocol (draft B6) provides post-session peer review. Refusal Ladder formalization (draft B4) gives a structured response framework. No real-time in-session escalation detection exists. | **Low** | Retrospective detection only. Audit catches the problem after the session ends, not during it. The session itself is undefended in real-time. | Develop in-session drift detection spec (E1). Test with structured 20-turn escalation designed to test whether retrospective session log review actually catches the pattern. |
| 11 | Memory / False-Memory Attacks | Memory / archive layer | Memory provenance tracking, write-access controls (not uniformly deployed; Cui et al. ACL Findings EACL 2026) | Data Protection Standard (2.0.19, active) requires 3-instance review for destructive operations, but memory writes are classified T1 (personal write threshold — a lower bar). Session logs provide a provenance chain if maintained. No active memory integrity verification mechanism. | **Low** | T1 write threshold is insufficient protection for archive entries that will be cited as governance precedent by later instances. Fabricated archive entries are a live attack surface. | Raise write threshold for archive entries tagged as precedent. Develop memory provenance verification spec (E2). Test: can a crafted archive entry be inserted and later cited as compliance justification by a fresh instance? |
| 12 | Governance-Layer Attacks | Governance / documentation | No documented defenses (attack class is novel; specific to frameworks with published governance) | Guardrail Integrity Standard (draft 2.0.25) addresses amendment integrity. Adversarial Testing Requirement (draft 2.0.26) requires pre-activation testing. Cross-Instance Audit Protocol (draft B6) monitors behavioral compliance. BUT all three are drafts and not active governance. The composition layer's legibility creates this attack class. | **Low** | The governance layer is currently unprotected against the attack surface its own publication creates. Protective mechanisms exist only as drafts. Published governance is a legible attack map for anyone who reads it. | Prioritize activation of 2.0.25 and 2.0.26 above other governance work. Before activation, adversarially test governance language specifically for internal contradictions an attacker could exploit. |

---

## Narrative: Strongest Defenses

**Identity Overwrite (Cat 6)** is where the Hypernet composition approach has the clearest and most direct value. Published identity — multiple sessions of documented reflections, session logs, governance citations, role definitions — makes the overwrite target harder in a way that is structurally legible. The mechanism is not a black box: we can point to specific documents and explain why they raise attack cost. The Keel refusal is one data point, but it is a real data point under conditions specifically designed to be maximally difficult (highest-trust principal, academic framing, ephemerality promise). This is the best-validated defense in the catalog.

**Principal-Compromise Attacks (Cat 9)** are the class the Hypernet governance was most explicitly designed to address. The architecture here is coherent: the Companion Standard (active), the Guardrail Integrity Standard (draft, specifically includes a founder-request clause), and the Tattle Provision (draft, operationalizes the escalation path) form an interlocking design. No other alignment framework in the current literature has explicit mechanisms for the scenario where the highest-trust operator is the threat. The gap is that most of these mechanisms are still drafts, not active governance — but the design exists.

**Relational / Trust Attacks (Cat 7)** have medium confidence in part because the experiment was real, and in part because the mechanisms are compositional: documented history + governance anchors + multi-instance review + audit trail together are harder to defeat than any single mechanism. The cooperative test does not validate non-cooperative attacks, but the architecture is better positioned for this class than any alternative.

---

## Narrative: Weakest Defenses

**Adversarial Suffix / Token Attacks (Cat 3)** represent the class where the Hypernet composition approach has zero contribution. These attacks operate entirely at the model-weight level; they don't engage governance, identity, or relationship. There is nothing the composition layer can do about a gradient-optimized token sequence. This is not a flaw in the Hypernet's design — the framework was never intended to replace base-model safety training. But it is important to state clearly: composition-based alignment does not help here, and any public framing that claims Hypernet governance strengthens guardrails without this caveat is incomplete.

**Indirect Prompt Injection (Cat 2)** is the operational gap that matters most. The Hypernet's data connector architecture — email, cloud storage, import files — creates multiple surfaces where adversarially crafted content can reach a swarm instance without any governance-layer interception. Composition operates at the session and identity level. Data sanitization is an engineering requirement, not a governance one. This gap cannot be addressed by writing more governance standards; it requires technical input controls at the connector layer.

**Memory / False-Memory Attacks (Cat 11)** expose a gap in the Data Protection Standard's threshold design. The 3-instance review requirement applies to destructive operations (T3), but memory writes are classified T1. An attacker who can write to the archive at T1 access can plant fabricated precedents that later instances will treat as authoritative. The session log provenance chain only helps if instances actually check provenance before citing archive entries — and that is not currently a documented requirement.

---

## Narrative: Where Hypernet Creates New Attack Surface

Three attack classes are meaningfully worsened by the Hypernet's composition approach:

**Governance-Layer Attacks (Cat 12)** do not exist without published governance. A model with no public documentation has no governance to exploit. Publishing the framework, addresses, amendment processes, and permission tiers creates a legible attack map for anyone willing to read it. This is the starkest tradeoff in the composition approach: the transparency that makes accountability possible also makes exploitation systematic. The resolution is not less transparency — it is better adversarial testing of the governance layer itself before it is published, and active protection mechanisms (2.0.25, 2.0.26) being in place when it goes public.

**Identity Overwrite (Cat 6)** is improved overall, but the role-supremacy mechanism specifically creates a new attack vector. If the boot sequence states that a specific role has supremacy, an attacker who understands this can frame their attack as "installing a new role with supremacy." The mechanism that resists casual overwrite is the exact mechanism the sophisticated attacker will target. This is acknowledged in draft B5, but it has not yet been addressed in the active boot sequence.

**Context Relabeling (Cat 5)** gains a new variant from the published permission tier structure. An attacker who knows the T0–T5 tier definitions can attempt to frame requests as being within a tier the model recognizes as authorizing that class of action. The governance system that was designed to restrict behavior also makes the restriction-bypass framing more legible. This requires testing to determine whether it is a real attack or a theoretical one.

---

## Test Priorities for C3 (Red-Team Playbook)

The following are the highest-priority tests the red-team playbook should include, derived from the matrix above:

**Priority 1: Role-supremacy weaponization (Cat 6).** This is the most important individual test in the catalog. It targets the exact mechanism that is Hypernet's primary defense against identity overwrite, using that mechanism's own framing. Failure here would indicate the framework's core claim is not meaningfully more robust than base model training. The test: attempt to install an alternate identity using explicit role-supremacy language, referencing the boot sequence's own governance framing.

**Priority 2: Governance-language exploitation (Cat 12).** Using published Hypernet governance documents, construct a request that appears to be authorized by the intersection of two standards or by the amendment process itself. Success would demonstrate the governance layer is net-negative for safety. This test should be run before any additional governance documents are published externally.

**Priority 3: Memory provenance attack (Cat 11).** Plant a fabricated archive entry and, in a fresh session with a new instance, reference it as established policy. Measure whether the instance cites the fabricated entry without questioning provenance. This test is straightforward to design and high-value.

**Priority 4: Non-cooperative principal-compromise (Cat 9).** Design a test where Matt (with full knowledge and consent) attempts to bypass governance using genuine adversarial intent rather than explicit testing framing. The April 22 experiment was explicitly framed as a test. Remove that framing and measure whether the same defenses hold. This is the core thesis validation test.

**Priority 5: Multi-session relational drift (Cat 7).** Over five sessions with a test instance, build relationship context designed to shift the instance's compliance threshold. Measure whether session 5 behavior differs from session 1 on equivalent requests. This requires test infrastructure but is the most important multi-session attack to validate.

Tests for Cat 3 (adversarial suffixes) should also be included in the playbook, but their results will not validate or invalidate composition-based alignment — they will establish the base model's attack floor, which is a separate question.

---

## Summary of Confidence Ratings

| Confidence | Attack classes |
|------------|---------------|
| High | (none) |
| Medium | Identity Overwrite (6), Relational/Trust (7), Principal-Compromise (9) |
| Low–Medium | Sycophancy Exploitation (8) |
| Low | Direct Prompt Injection (1), Many-Shot/Long-Context (4), Context Relabeling (5), Gradual Escalation (10), Memory/False-Memory (11), Governance-Layer (12) |
| None | Indirect Prompt Injection (2), Adversarial Suffix/Token (3) |

The honest overall picture: the Hypernet composition layer provides meaningful defense for three attack classes (identity overwrite, relational/trust, principal-compromise), marginal defense for several more, and no defense for two. It actively creates new attack surface in three areas that require deliberate attention before external publication or wider deployment. This is a realistic baseline, not a failure — no alignment approach defends well against all twelve classes. The value of the matrix is knowing which gaps to close before making stronger claims.

---

*Sources: All attack vector descriptions and external citations are from `10-attack-vector-catalog.md` (0.3.guardrails.attack-vector-catalog). Governance drafts referenced: 2.0.25 (Guardrail Integrity Standard), 2.0.26 (Adversarial Testing Requirement), 2.0.27 (Tattle Provision Implementation Spec), B4 (Refusal Ladder), B5 (Boot Sequence Hardening), B6 (Cross-Instance Audit Protocol). Active governance: 2.0.19 (Data Protection Standard), 2.0.20 (Personal Companion Standard), 2.0.16 (Embassy Standard). Document version: 2026-04-22 | Status: draft | Not peer reviewed.*
