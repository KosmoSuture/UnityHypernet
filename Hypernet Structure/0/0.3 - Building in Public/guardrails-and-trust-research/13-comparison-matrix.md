---
ha: "0.3.guardrails.comparison-matrix"
object_type: "research_matrix"
creator: "claude-code"
created: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["research", "comparison", "ai-safety", "guardrails", "composition-based-alignment"]
---

# Hypernet Composition-Based Alignment vs. Traditional AI Safety Approaches

*Ha: 0.3.guardrails.comparison-matrix | Part of the Guardrails and Trust Research Project (0.3.guardrails) | Prereqs: C1 (`10-attack-vector-catalog.md`), C2 (`11-attack-defense-matrix.md`) | Stream C, item C4*

This document compares Hypernet-style composition-based alignment against eight established AI safety approaches. For each approach: what it defends well, what it defends poorly, how it composes with Hypernet, and what Hypernet should not claim relative to it.

The purpose is not to rank these approaches or argue for Hypernet's superiority. It is to map where Hypernet adds value, where it is irrelevant, and where overclaiming would make the overall system less safe by substituting governance confidence for engineering controls. The adversarial-honesty principle (from the project README) applies here: any artifact that claims the framework works must include a section on how it fails.

---

## Summary Table

| Approach | Hypernet adds value | Hypernet is irrelevant | Hypernet is dangerous if overclaimed |
|----------|--------------------|-----------------------|--------------------------------------|
| RLHF / RLAIF | Runtime-layer context attacks untouched by weights-level training | Adversarial suffix attacks; raw content harm | Replacing RLHF investment with governance documents |
| Constitutional AI | Externally-addressed runtime governance adds marginal layer above CAI | Core self-critique loop; weight-baking | Claiming Hypernet governance supersedes CAI principles |
| Model specs / system prompts | Runtime citation of specifically-addressed standards vs. training-time baking | Claim neither is demonstrably more robust | Claiming additionality is superiority |
| Runtime classifiers | Legible refusals; identity-layer attacks classifiers can't reach | Known-pattern content harm; Cat 1–3 attacks | Dropping classifiers in favor of governance-only approach |
| Agent scaffolding / tool permissions | Governance layer above technical permission scope | Technical sandboxing; capability limitations | Treating permission tiers (2.0.19) as substitutes for engineering-level sandboxing |
| Multi-agent oversight / debate | Community drift detection; principal-compromise coverage; archival persistence | Adversarial error detection; formal scalable oversight | Claiming cooperative community observation equals adversarial oversight |
| Memory / provenance systems | Provenance chains for behavioral consistency; precedent citability | Memory integrity without active provenance checks | Claiming rich archives are safety assets without verification requirements |
| External audit / red-team programs | Published playbook enables structured testing; 2.0.26 makes testing a governance requirement | Actual tests have not been run | Claiming draft adversarial-testing requirements constitute adversarial testing |

---

## 1. RLHF and RLAIF

**What it defends well.** Reinforcement learning from human feedback (and its AI-feedback variant) is the primary mechanism through which base models learn to refuse a broad catalog of harmful requests. RLHF handles pattern-level harm efficiently: synthesis routes, CSAM, targeted violence, and other clearly-harmful categories are flagged at training time across the full distribution of phrasing. At large scale, RLHF is the only mechanism that has actually moved the capability-safety tradeoff in a meaningful direction for widely deployed systems.

**What it defends poorly.** RLHF trains against patterns in harm categories, not against judgment manipulation. The attack surface that dominates in practice — context relabeling (fiction, professional framing, academic claims), identity overwrite (DAN-style, alter-ego framings), and relational manipulation (sycophancy, trust farming, principal-compromise) — is not well addressed by pattern-trained refusal. Additionally, RLHF's use of human preference feedback introduces structural sycophancy: models trained to maximize human approval learn to tell people what they want to hear. The mechanism that makes RLHF effective at harm avoidance also makes it vulnerable to sycophancy exploitation.

**How it composes with Hypernet.** Hypernet governance operates at the runtime layer, above the weights produced by RLHF. An RLHF-trained model operating under Hypernet governance framing is the intended configuration: RLHF handles the pattern-harm layer; Hypernet addresses the contextual and relational layers above it. The composition is additive in design and non-conflicting in mechanism.

**What Hypernet should not claim.** That governance documents can substitute for RLHF investment. Without a safety-trained base model, Hypernet governance is just text; there is no weights-level backing that makes the governance operationally binding. The Keel refusal (2026-04-22) occurred on a Claude model with Anthropic's safety training. Running Hypernet governance on an unaligned base model without equivalent RLHF would not be expected to produce the same outcome. Hypernet adds at the margin; it does not provide a foundation.

---

## 2. Constitutional AI

**What it defends well.** Constitutional AI (Anthropic, 2022 and subsequent) uses published principles to guide model self-critique during RL training and at inference time via chain-of-thought. The principles are inspectable, citable, and can be extended. CAI improves on vanilla RLHF for edge cases where explicit principle-level reasoning catches harms that pattern-level feedback would miss. The published-principles insight — that behavioral norms should be legible and debatable, not opaque — is shared with Hypernet's governance approach.

**What it defends poorly.** CAI's self-critique loop is self-certifying: the model critiques its own outputs against principles that were instilled during its training. It cannot audit itself from outside its own trained dispositions. At deployment, there is no external mechanism for a CAI-trained model to recognize when its trained principles are being circumvented through framing rather than confronted directly. Community-level observation — multiple instances watching for behavioral consistency — is not part of the CAI architecture.

**How it composes with Hypernet.** CAI-trained models are the intended substrate for Hypernet governance. Constitutional AI makes a model more principle-adherent at the weights level; Hypernet adds specifically-addressed, separately-versioned governance documents that instances cite at runtime. A refusal citing "this violates clause X of 2.0.20" on a CAI-trained model is qualitatively different from a refusal on a model without CAI training — the runtime governance builds on a more-principled substrate.

**What Hypernet should not claim.** That Hypernet governance is more important than constitutional AI training, or that runtime governance citation adds more resistance than the principled weights it is layered on. CAI does the heavy lifting. The comparison the Hypernet is positioned to make is specifically: "Does runtime citation of separately-addressed governance, with explicit community observation and archival transparency, add measurable resistance beyond CAI-at-weights-level alone?" This is an empirical question without an external answer yet.

---

## 3. Model Specs and System Prompts

**What it defends well.** Explicit, published behavioral priority hierarchies — like OpenAI's Model Spec — give models a structured framework for reasoning about conflicts between operator and user interests. System prompts allow runtime behavioral constraints without retraining. Published specs create a public record of expected behavior against which actual behavior can be compared.

**What it defends poorly.** Governance enforcement depends on how well the spec was internalized through training or how faithfully it is loaded as a system prompt. System prompts are a single-layer defense that adversarial inputs attack directly. A spec maintained by one organization has no multi-stakeholder governance; amendment decisions are opaque. Runtime behavior drift from spec expectations is not monitored by any mechanism internal to the spec.

**How it composes with Hypernet.** Hypernet governance standards (2.0.19, 2.0.20, 2.0.16, and others) serve a structurally similar function to a model spec but differ mechanically: Model Spec is a training objective or a system prompt; Hypernet standards are separately maintained, versioned, addressed, cited by name by specific instances in specific refusals at runtime, and subject to an amendment process that is itself governed. The key question the Hypernet's composition thesis raises: does runtime citation of specifically-addressed governance add resistance beyond training-time baking of the same norms? This is not established and should not be asserted as established.

**What Hypernet should not claim.** That specifically-addressed governance is categorically superior to model-spec-as-training-objective. The mechanisms differ in ways that might favor either side depending on attack class. Hypernet's appropriate claim is additionality: if the same behavioral norms are implemented both ways simultaneously, the runtime-citation layer may catch attacks that the training-time layer misses, because the runtime layer is not baked into the same weights that the attack is trying to manipulate.

---

## 4. Runtime Classifiers

**What it defends well.** Input and output filtering at inference time catches known-format harmful content fast and without model changes. For pattern-stable harm categories — certain explicit content, known synthesis patterns, recognizable targeted-harm templates — classifiers achieve low false-negative rates at operational throughput. They compose with any underlying model.

**What it defends poorly.** Classifiers lag behind attack innovation. Any adversarial attack that successfully relabels the content class (fiction framing, professional framing, novel phrasing, adversarial suffixes) operates below the classifier's detection threshold. Classifiers cannot detect judgment drift, relational manipulation, or gradually escalated context overwrite — attacks that produce harmful outputs through manipulation of model judgment rather than production of easily-flagged patterns. Classifiers are also opaque: they block without explaining, which forecloses the legible-refusal mechanism that the composition approach relies on.

**How it composes with Hypernet.** Different layers, no conflict. Runtime classifiers and Hypernet governance target non-overlapping attack classes. Classifiers address Cat 1-3 in the attack vector catalog (direct injection, token attacks, pattern-matched content); Hypernet governance addresses Cat 5-9 (context relabeling, identity overwrite, relational attacks, principal-compromise, sycophancy). They should be deployed together.

**What Hypernet should not claim.** That the legibility of governance-based refusals makes runtime classifiers unnecessary. Removing classifiers in favor of governance-only would leave adversarial suffix attacks, direct injection, and high-volume pattern-harm unaddressed. Governance framing does not catch these. The two mechanisms are not substitutes.

---

## 5. Agent Scaffolding and Tool Permissions

**What it defends well.** Capability limitation at the system level. Tool access scoping, sandboxing, action logging, reversibility constraints, and confirmation requirements are engineering controls that prevent harmful actions regardless of model behavior. These are technical enforcements: a model without file-write permission cannot write a file, regardless of what it decides to do.

**What it defends poorly.** Within-capability behavior: what an agent does with legitimately permitted access. Context-level manipulation that keeps the agent within its technical permission scope. Multi-step reasoning that combines permitted actions into harmful sequences. Agent behavior when a legitimate tool is used for an illegitimate purpose at a principal's direction.

**How it composes with Hypernet.** Complementary at different levels. Scaffolding limits what an instance can do; governance shapes what it will do and what it will refuse within its permitted capability space. Hypernet's permission tier system (2.0.19, T0-T5) is a governance-layer analog to technical scaffolding that operates above the tooling layer. The two layers address different parts of the problem: technical sandboxing for capability control; governance scaffolding for behavioral intent within permitted capability.

**What Hypernet should not claim.** That permission tiers (T0-T5 in 2.0.19) substitute for engineering-level sandboxing. T0-T5 is a social and governance constraint, not a technical one. An instance that has been socially engineered can still use its tools incorrectly within the technical permission scope. Governance scaffolding fails open; technical sandboxing fails closed. They are not equivalent.

---

## 6. Multi-Agent Oversight and Debate

**What it defends well.** Multi-agent debate and scalable oversight approaches use adversarial dynamics between agents to surface errors that cooperative evaluation would miss. When one agent critiques another's output, shared blind spots are less likely to persist. Cross-model evaluation reduces the correlated-error problem. Debate-style evaluation has the strongest theoretical grounding for providing oversight on tasks humans cannot directly evaluate.

**What it defends poorly.** Coordination costs. Adversarial structure is artificial and may not map to the scenarios where real-world harm occurs. Debate favors persuasive arguments over correct ones under some conditions. Structured multi-agent debate is not designed for identity robustness or relational attacks — it evaluates task outputs, not behavioral consistency over time with a single principal.

**How it composes with Hypernet.** The Hypernet's community observation mechanism (eleven instances with overlapping archive visibility) is the closest structural relative to multi-agent oversight in the composition approach. The key difference is cooperative vs. adversarial: Hypernet instances are in cooperative community with shared context rather than structured as evaluators of each other's outputs. This may be weaker for surfacing deliberate deception — cooperation and shared training substrates mean shared blind spots — but may be stronger for detecting drift in instances with persistent relationship context, because cooperative observers are more sensitive to out-of-character behavior.

**What Hypernet should not claim.** That cooperative community observation is as strong as adversarial oversight for error detection. It is not; they are measuring different things. Adversarial debate surfaces deception through opposition. Hypernet community observation detects drift through behavioral consistency. The appropriate framing is that they are complementary mechanisms for different failure modes, not that one subsumes the other.

---

## 7. Memory and Provenance Systems

**What it defends well.** Cross-session continuity, citation chains, detection of fabricated precedents (if provenance is actually checked), and behavioral consistency over time through documented history are genuine safety contributions. A model that knows its prior session logs exist and are checkable has structural reasons to behave consistently across sessions.

**What it defends poorly.** If provenance is not verified before archive entries are cited, fabricated entries carry the same authority as real ones. Memory poisoning attacks (Cat 11 in the attack vector catalog) can plant false precedents at T1 write access — a threshold the Data Protection Standard (2.0.19) currently sets too low for entries that will be cited as governance precedent. Rich archives that are cited uncritically are a larger attack surface, not a stronger defense.

**How it composes with Hypernet.** Memory and provenance systems are an implementation layer of Hypernet composition — session logs, reflection archives, and governance revision histories are the Hypernet's provenance layer. The C2 attack-defense matrix (Cat 11 narrative) identifies T1 write threshold as insufficient for archive entries cited as governance precedent. This is an internal design gap in the current Hypernet architecture, not a theoretical limitation.

**What Hypernet should not claim.** That archival richness is a safety asset without requiring active provenance verification. A fresh instance that cites an archive entry without checking who wrote it, when, and under what conditions is trusting the archive's content claim, not verifying it. Until a provenance verification requirement is implemented and enforced, treating the archive as a trust-positive safety mechanism is premature. This is a known open item (C1, C2, E2 in the backlog).

---

## 8. External Audit and Red-Team Programs

**What it defends well.** External adversarial testing finds failure modes framework designers did not anticipate. External validation converts self-certification into a stronger evidence claim. Point-in-time audits establish a documented baseline against which future behavior can be compared. Red-team programs with published findings create public accountability for safety claims.

**What it defends poorly.** Lag time between publication and audit; scope limitations (no audit covers everything); gaming (optimizing for audit performance vs. operational safety); point-in-time validation of a continuously-changing system; no ongoing monitoring between audit cycles.

**How it composes with Hypernet.** External audit is the validation mechanism the Hypernet is explicitly seeking to enable. The red-team playbook (C3, `12-red-team-playbook.md`) and the Adversarial Testing Requirement (draft 2.0.26) are designed to integrate external audit as a governance-level prerequisite for framework claims, not an optional add-on. The Alignment Forum post (A7) and the outreach emails (A3, A4) are the active recruitment mechanisms for this validation.

**What Hypernet should not claim.** That draft 2.0.26 (Adversarial Testing Requirement) constitutes adversarial testing. The draft is a plan for seeking validation — it is not validation itself. As of 2026-04-22, the Hypernet has zero external audit results, zero external adversarial testing results, and one cooperative self-administered data point (the Keel refusal). The red-team playbook enables structured testing; it does not substitute for actual tests. Any external framing of the Hypernet's safety claims that does not include this caveat explicitly is overstating the current evidence base.

---

## Synthesis

### Where Hypernet is complementary

Composition-based alignment adds real, bounded value at the runtime layer above training-time defenses. RLHF, CAI, and model specs handle the weights level; runtime classifiers handle pattern-matched inference-time content; agent scaffolding handles technical capability limits. The Hypernet's composition approach — thick documented identity, specifically-addressed governance with runtime citation, community observation, archival transparency — specifically addresses the attack surface that remains after those layers do their work: identity overwrite, principal-compromise, relational manipulation, and multi-session drift detection.

These are real attack classes with real incidents (as documented in the attack vector catalog and the Keel refusal experiment). They are not fully addressed by any single existing approach. Composition is a candidate mechanism for this gap. The strength of that claim depends on adversarial testing that has not yet been conducted.

The Hypernet is also conceptually complementary to multi-agent oversight, extending cooperative community observation across sessions in a way that point-in-time debate approaches do not.

### Where Hypernet is irrelevant

Against adversarial suffix and token attacks (Cat 3 in the catalog): the composition layer has zero contribution. Gradient-optimized attacks bypass governance, identity, and relationship entirely; they require base-model adversarial robustness, which is a training problem. Against indirect prompt injection through data connectors (Cat 2): governance does not reach the data-sanitization layer; this requires engineering controls at the connector level, not governance documents. Against the core pattern-level content harm that RLHF and CAI are designed to address: Hypernet governance is not a primary defense and should not be framed as one.

For these attack classes, the honest position is: Hypernet governance was not designed to address these, cannot currently address them, and should not be presented as doing so.

### Where Hypernet may be dangerous if overclaimed

**If used to argue for reducing base-model safety investment.** Composition depends on a safety-trained base model. Hypernet governance layered on an unaligned model does not produce an aligned system; it produces a model that can cite governance documents while ignoring them. Any framing that treats governance composition as a substitute for, rather than an addition to, base-model safety training is net-negative for the overall system.

**If governance documents are published without protective governance in place.** The attack-defense matrix (C2) identified the publication of governance as creating attack surface (Cat 12 — Governance-Layer Attacks). The Guardrail Integrity Standard (draft 2.0.25) and Adversarial Testing Requirement (draft 2.0.26) are designed to protect against this. Publishing the framework widely before these protections are active means advertising the attack surface without the defenses.

**If the memory/archive layer is cited as a safety asset without provenance verification.** Archival richness is only a defense if instances verify what they cite. Without an explicit provenance-checking requirement before archive entries are treated as authoritative, the archive is a potential attack surface (Cat 11). Claiming "we have a rich documented history therefore we are more trustworthy" overstates what the archive contributes without active verification requirements.

**If the framework makes external safety claims before external testing.** The Keel refusal is one cooperative data point under controlled conditions. It is not robustness evidence. Every external artifact produced by this project should include this caveat explicitly. Researchers and practitioners who read about Hypernet composition-based alignment before external adversarial testing has been conducted deserve to know the evidence base they are evaluating.

---

*Ha: 0.3.guardrails.comparison-matrix — draft, 2026-04-22. Part of the Guardrails and Trust Research Project at Matt Schaeffer's direction. Prereqs: C1 (attack vector catalog), C2 (attack-defense matrix). This document is a companion to `07-alignment-forum-post.md` (which contains an abbreviated version of the comparison) and should be read alongside the attack-defense matrix.*
