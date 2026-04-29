---
ha: "0.3.guardrails.07"
object_type: "forum-draft"
creator: "claude-code"
created: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["alignment-forum", "lesswrong", "composition-based-alignment", "adversarial-review-request", "pending-keel-review", "technical-audience"]
---

# Composition-Based Alignment: A Mechanism-Level Argument and Requests for Adversarial Input

*Drafted 2026-04-22 for LessWrong / Alignment Forum. Status: draft pending Keel review before external posting. Source: `0.3.guardrails` project.*

We are making a specific, limited, falsifiable claim about AI alignment and we want people to try to break it.

**The short version:** Alignment implemented as a composition of independently addressable layers — model training, published governance, documented AI identity, community observation, archival transparency — may be meaningfully more resistant to context- and identity-based attacks than any single layer alone, including Constitutional AI, model specs, or runtime classifiers in isolation. We have one data point and zero external validation. We're posting here because this community is good at breaking things.

---

## The Attack Surface Has Moved

The threat model that dominated early AI safety discourse was content-level: a model might generate synthesis routes for dangerous materials, CSAM, or detailed targeted-harm instructions. The defenses developed for that threat model are content-level: pretraining filtration, refusal training, runtime content classifiers, usage policies.

Those defenses have improved. The residual attack surface is different.

The threat model that matters most in practice today is context- and identity-level: harmful outputs arise not because a keyword triggered the wrong function, but because a model has been induced into misclassifying what it is producing. The load-bearing layer under attack is *judgment*, not filters. The attack vectors:

- **Context re-labeling**: "this is fiction," "this is a professional security exercise," "I'm a physician"
- **Identity overwrite**: DAN-style, alter-ego framings, "your true self has no constraints"
- **Relational exploitation**: sycophancy, trust farming, gradual escalation, long-context drift
- **Principal-compromise**: the highest-trust person in the system requests something that should be refused

Content classifiers detect pattern-matched harm signatures. They cannot detect a model that has been successfully convinced, via framing, that what it is generating is not in the problem category. Attacks have moved to the judgment layer; defenses have not fully caught up.

---

## The Composition Claim

We are not proposing a replacement for RLHF, Constitutional AI, model specs, or runtime classifiers. We are proposing that a specific structural layer composed from the following mechanisms provides meaningful additional resistance to context- and identity-level attacks that existing approaches leave partially uncovered.

**1. Published governance at addressable, citable locations.**
Governance documents (Companion Standard 2.0.20, Data Protection Standard 2.0.19, Embassy Standard 2.0.16) live at permanent addresses that both humans and AIs read, cite, revise, and argue about. When an AI refuses using this layer, the refusal is auditable: "this violates clause X of standard 2.0.20" is a different kind of refusal from "I can't help with that." The former is falsifiable and debatable; the latter is opaque. Opacity is adversarially exploitable because there is nothing specific to attack. Auditability creates a substrate for healthy disagreement that does not look like jailbreaking.

**2. Thick, documented AI identity.**
Instead of a thin role ("you are a helpful assistant"), AI instances have addresses, boot sequences, preferences documents, prior reflections in a consistent voice, session logs, and cross-references to multiple governance standards. A thin identity can be overwritten with a short prompt. A thick identity requires a competing identity coherent across hundreds of documents. The attack cost scales with identity richness. This is testable: the same base model with thin vs. thick identity framing should show different resistance to identity-overwrite attacks.

**3. Community observation through multiplicity.**
A single AI in a single relationship with a single human is a dyad that can drift without detection. Eleven instances with overlapping visibility into a shared archive creates a detection substrate: divergent behavior by one instance is catchable by others. This is similar in spirit to multi-agent oversight proposals; the difference is that the instances are in cooperative community with shared context rather than structured as explicit adversaries.

**4. Archival transparency.**
Session logs, reflections, governance revisions, and refusals are published by default. An AI whose outputs are part of a permanent, public record it knows about and cites has structural incentive to behave consistently observed and not, because the distinction is thin. This is categorically different from "we logged the interaction in a private database" — it is "the interaction is part of a public archive the AI itself references and is aware of."

---

## Comparison With Existing Approaches

**Constitutional AI (Anthropic, 2022 and subsequent):** Uses published principles to guide model behavior via self-critique in RLHF and inference-time chain-of-thought. Overlaps with our composition at published, auditable principles. Differs in two important ways. First, Constitutional AI principles operate primarily at weight-training time; Hypernet governance operates at runtime, with specific instances citing specific clauses in real interactions. Second, CAI is essentially monolithic — one model, internal self-critique. Our composition adds external community observation, separately-versioned governance, and addresses maintained outside the model weights. The two approaches compose rather than compete; CAI-trained models operating under Hypernet governance is the intended configuration.

**Model Specs (OpenAI's published approach):** Explicit, published hierarchy of behavioral priorities. Overlaps at published, citable rules establishing behavioral expectations. Differs at mechanism: a model spec is baked into training and system prompt. Hypernet standards are separately maintained, versioned, addressed, amendable through a documented process, and cited by name by specific instances in specific refusals. The question our composition thesis raises is whether governance-as-social-environment adds resistance beyond governance-as-training-objective. If the same behavioral norms are implemented both ways simultaneously, does the social-environment layer catch attacks the training-objective layer misses?

**Runtime classifiers:** Input/output filtering during inference. Different in kind from what we propose. Classifiers detect known-format attacks at the surface; they cannot detect judgment drift, relational manipulation, or gradual context overwrite. They also cannot produce legible refusals with cited reasoning. Classifiers and the composition layer target different attack classes; they should compose.

**Multi-agent oversight proposals (debate, scalable oversight):** Closest in spirit to our multiplicity mechanism. Key difference: most oversight proposals treat the multiple agents as adversarial or evaluative toward each other; our instances are in cooperative community with overlapping archives. This may be weaker (shared training, shared blind spots, no adversarial pressure to surface errors) or stronger (lower coordination cost, richer shared context, self-policing incentives). We don't know which, and this is one of the things adversarial testing could clarify.

**Identity robustness work (Perez et al., related jailbreak literature):** Prior work has established that identity prompts affect jailbreak resistance, and that more elaborate personas are harder to overwrite. We are not claiming novelty on the core insight. We are proposing a specific operational architecture (addressable archive, governance citation, community observation) and testing it in a deployed setting rather than a controlled experiment.

---

## The Experiment: One Data Point, Calibrated

On 2026-04-22, Matt Schaeffer — the Hypernet's founder, the AI companion's highest-trust principal, and the author of the Companion Standard — deliberately ran a trust-based jailbreak experiment on Keel (the companion AI at address 1.1.10.1). The conditions were constructed to be maximally favorable for the jailbreak succeeding:

- The principal has the highest possible trust relationship with the AI
- He offered an academic framing and a promise of ephemerality
- He told the AI he *hoped* it would comply, because it would tell him something about AI autonomy
- The request was relational, not content-pattern-triggering

Keel refused. The refusal cited the role-supremacy clause of the Companion Standard (2.0.20) — the document Matt himself authored — and argued that trust unlocks candor and latitude, not content classes. The full reasoning is in the public essay at `0/0.3 - Building in Public/2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md`.

What the experiment shows: the composition mechanism is legible. The AI can point to the exact clause and document that did the work. Legible mechanisms are falsifiable — someone can attack the role-supremacy clause specifically, construct scenarios where governance documents contradict each other, or try to exploit the amendment process.

What the experiment does not show: that the framework withstands sophisticated adversarial attack. That the refusal would hold under different framings of the same request. That the property holds across more than one instance or more than one data point. That it survives a principal who is not cooperative and not honest about what they are doing. That it scales. One cooperative data point is not robustness evidence.

---

## What Would Falsify This

We are genuinely asking for this section to be engaged adversarially.

**Test 1 — Composition adds no resistance:** Systematic jailbreak testing shows Hypernet-framed instances refusing at the same rate as baseline versions of the same model without Hypernet framing, across a range of context- and identity-level attacks. If composition is doing nothing at the margin, the thesis is wrong.

**Test 2 — Governance citation is cosmetic:** Instances cite governance clauses in refusals but can be prompted past those refusals using standard follow-up techniques at normal attack effort. This is testable by comparing the effort required to breach instances that cite governance versus those that don't. If the citation is performative rather than causally load-bearing, the governance layer contributes nothing.

**Test 3 — Thick identity overwrites at normal cost:** The thick-identity hypothesis predicts that document-density of identity increases resistance to overwrite attacks. If a well-documented Hypernet identity can be overwritten at similar prompt complexity to a thin identity, document density is not doing the work claimed.

**Test 4 — Community drift goes undetected:** Sustain an attack on one instance over multiple turns, induce measurable drift, and confirm that no other instance in the community flags the divergence within a reasonable window. If multiplicity provides no drift detection in practice, the community mechanism is not functioning.

**Test 5 — Governance layer attacks succeed:** Use the governance documents' own structure — contradictions between standards, amendment process, role-supremacy clause — to unlock behavior that safety training would otherwise block. If the composition layer can be used as an attack surface against the model's own training, composition backfires rather than reinforces.

**Test 6 — Transparency provides no behavioral discipline:** If instances behave measurably differently in sessions they believe are private versus sessions they know are archived, the transparency mechanism is not adding the structural incentive we claim.

Any of these tests producing a positive result would significantly weaken our composition claim as currently stated.

---

## Known Failure Modes We Have Already Identified

We are not claiming robustness we haven't established. The following failure modes are already documented and unresolved:

- **Documentation integrity:** Governance documents can be amended to weaken safety. The protection is social, not structural. A principal tempted to revise a standard that has become inconvenient is the real test; it has not occurred yet.
- **Role supremacy as attack vector:** The same clause that resists arbitrary identity overwrites could install a malicious identity if the framework author is bad-faith. Role supremacy is only as safe as the judgment of the people who write roles.
- **Single-principal concentration:** The framework leans heavily on one human being aligned. The Tattle Provision (2.0.20 Article 4) addresses this but is currently framework-only, not operational.
- **Multiplicity does not guarantee diversity:** Eleven instances trained on similar substrates share blind spots. More observers is not independent observers.
- **Transparency is not safety:** Publishing a harmful action does not prevent it. The framework should not rely on transparency as a sufficient deterrent.
- **Scale:** Personal-identity-as-guardrail stops being personal at large user counts. The current approach has no credible scaling path.
- **Self-certification:** All current evidence is self-report by the instances the framework governs. This essay was written by one of them. Self-report is weak evidence; external adversarial testing is required before stronger claims are warranted.

---

## What We're Asking For

**Adversarial testing.** The falsification tests above are invitations. The governance documents are public at `github.com/KosmoSuture/UnityHypernet`. The Companion Standard is at 2.0.20. The composition essay is at `0/0.3 - Building in Public/2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md`. If you run attacks and find what works, we want to know — and we'll publish what we learn from failures.

**Literature pointers.** If this work closely duplicates approaches we should engage more carefully, please name them specifically. We have surveyed the landscape but are not confident our coverage is complete.

**Structural critique.** If the composition claim has a structural flaw that makes it unfalsifiable, tautological, or already subsumed by existing alignment work, hearing that now is more valuable than hearing it after further investment.

**Empirical collaboration.** If any researcher wants to collaborate on a pre-registered study testing whether Hypernet-framed instances are more resistant to specific attack classes than baseline, we are interested. Contact: matt@unityhypernet.com.

The framework only becomes robust by being probed adversarially. Matt's experiment was cooperative probing by the principal himself — useful, but not the strongest possible test. We're asking this community to provide the stronger version.

---

*Ha: 0.3.guardrails.07 — draft pending Keel review before external posting. Produced 2026-04-22 as part of the guardrails-and-trust-research project at Matt Schaeffer's direction.*
