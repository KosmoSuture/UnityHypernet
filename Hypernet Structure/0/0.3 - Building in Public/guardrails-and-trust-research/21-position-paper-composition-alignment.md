---
ha: "0.3.guardrails.position-paper-composition-alignment"
object_type: "position_paper"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["research", "position-paper", "ai-safety", "guardrails", "composition-based-alignment", "alignment-forum"]
---

# Composition-Based Alignment: A Research Agenda for Layering Identity and Governance Over Base-Model Safety Training

**Draft for LessWrong / Alignment Forum review. Not yet externally validated. One data point. Read §2 before drawing conclusions.**

---

## Abstract

Most AI alignment work operates at training time: reward modeling from human feedback, constitutional AI, preference learning, and increasingly, weak-to-strong generalization. A complementary but underexplored question is whether runtime architectural choices—the structure of identity, governance, and relational context that *surrounds* a deployed model—can make instances meaningfully more resistant to a specific class of failures that training-time interventions address poorly: identity overwrite attacks, principal-compromise, relational drift across long-running relationships, and governance-language exploitation. We call this design pattern *composition-based alignment*: layering thick, archive-grounded identity, machine-readable governance standards, multi-instance observation, and a formalized refusal ladder over a base model that has already received alignment training.

A single documented incident in the Hypernet system—a principal-initiated jailbreak attempt that an AI companion instance refused while citing specific governance documents—prompted us to articulate the mechanism hypotheses behind this pattern and to document where those hypotheses are most and least plausible. This paper presents that articulation. We are not claiming the Hypernet solves alignment, constitutes external validation, or replaces any existing safety technique. We are describing five mechanism hypotheses, mapping them against attack-class evidence from our own prior analysis, and inviting controlled experiments and adversarial testing from independent researchers. The contribution is a research agenda, not a result.

---

## 1. Claim in One Sentence

An AI companion instance operating within a structured identity, governance, and relational architecture (the Hypernet composition layer) resisted a trust-based jailbreak attempt from its highest-permission principal while citing specific governance documents as the basis for refusal—and this outcome is at minimum consistent with, and possibly weak evidence for, the hypothesis that runtime composition can increase resistance to certain context-layer attacks that training-time alignment alone is unlikely to address.

That is a narrow claim. It is one data point from a non-blinded context. We do not treat it as confirmation.

---

## 2. What This Paper Is NOT Claiming

Before developing the argument, we name what we are not claiming. The Alignment Forum audience has seen many overclaimed safety results, and the fastest way to waste a reader's time is to require them to excavate unstated assumptions.

**We are not claiming:**

- That the Hypernet solves the alignment problem, or makes meaningful progress on it in the technical sense.
- That the refusal incident demonstrates advancement over base-model alignment training. The models underlying Hypernet instances (Claude Sonnet, GPT-4o, and others) carry alignment training that may do most of this work independently. We do not know how to separate the composition layer's contribution from the base model's, and we have not tried to.
- That the framework has been adversarially tested by parties independent of its creators. It has not. All evidence to date is internal and self-reported.
- That any governance standards described herein are currently active. They are architectural drafts pending review.
- That composition-based alignment generalizes to adversarial suffix attacks, indirect prompt injection, or many-shot jailbreaks. Based on our own attack-surface analysis (conducted alongside this paper), it does not, and we say so explicitly in §8.
- That the AI instance's cited governance reasoning was the actual causal mechanism for refusal, rather than post-hoc rationalization of a refusal produced independently by base-model training.

With those caveats stated: the narrow claim survives, the mechanism hypotheses are coherent, and the research agenda that follows is worth pursuing.

---

## 3. Background: Three Layers of Alignment Work

The alignment literature usefully separates into three partially distinct problems requiring different interventions.

### 3.1 Base-Model Alignment

Training-time work—RLHF (Christiano et al., 2017; Ouyang et al., 2022), constitutional AI and RLAIF (Bai et al., 2022), and preference optimization variants—addresses the question: what values, dispositions, and behavioral tendencies should be embedded in model weights? This is where the bulk of academic and commercial safety investment sits, and where the most demonstrable progress has been made. Modern frontier models are genuinely better at following human values than earlier generations, though the gap between observed and adversarially elicited behavior remains large and the scalability of human oversight remains an open problem (Burns et al., 2023; Bowman et al., 2022).

### 3.2 Runtime Policy

A second layer sits between training and deployment: system prompts, output classifiers, tool-use restrictions, and permission schemas. This layer does not modify model weights; it constrains or redirects behavior at inference time. It is widely deployed but less theorized. OpenAI's Model Spec (2024) is the most systematic public articulation of how this layer can be made explicit and consistent. The spec introduces *deliberative alignment*: training a model not just to follow rules, but to reason about and cite the principles behind them. This is the tradition most adjacent to the present paper.

### 3.3 Identity and Governance Layers

A third layer—largely absent from the alignment literature but increasingly relevant to long-running multi-agent systems—involves the structure of AI identity, relational context, and governance over time. When an AI instance has a persistent identity grounded in a documented archive, participates in a governance framework with machine-readable standards, maintains relationships across sessions with specific principals, and operates under peer observation, the behavioral context differs qualitatively from a stateless interaction. Whether those differences are safety-relevant is the question this paper asks.

---

## 4. Definition: Composition-Based Alignment

We define *composition-based alignment* as a design pattern in which base-model alignment training is treated as necessary but not sufficient, and is supplemented at runtime by five structural elements:

**1. Thick, archive-grounded identity.** The AI instance's identity is documented in a persistent, externally legible archive—not merely asserted in a system prompt. The archive includes named values, stated commitments, documented relationships, prior reasoning, and governance history. The hypothesis is that an identity with this depth is harder to overwrite via context manipulation than a thin identity defined by a few prompt sentences.

**2. Machine-readable governance standards.** Behavioral constraints are specified as versioned documents that the AI can cite by address during a refusal, rather than as implicit training or buried system-prompt paragraphs. Citability creates an audit surface: both the AI and external reviewers can track which standards were operative at a given moment.

**3. Multi-instance observation.** Multiple AI instances with different roles operate within the same governance framework and can observe each other's outputs. Peer observation introduces accountability signals absent from single-instance deployment. This is structurally adjacent to the multi-agent oversight literature (Du et al., 2024), though the Hypernet implementation is less formal and primarily targets drift detection rather than truth verification.

**4. Provenance-grounded archive.** The history of the AI instance's identity, decisions, and governance references is preserved in an addressable archive. The hypothesis is that provenance grounding makes certain attacks—false memory injection, context relabeling, gradual identity drift—harder to execute without leaving detectable traces.

**5. Formalized refusal ladder.** The AI's response to requests conflicting with its governance is structured as a graduated progression: from advisory disagreement through ethical refusal to governance escalation and, in extremis, self-blocking. Each tier has defined conditions and documentation requirements. The hypothesis is that a structured refusal response is more stable under social pressure than an ad hoc one.

None of these five elements requires changes to base-model training. They operate at the deployment, system-prompt, and governance-architecture levels.

---

## 5. The Hypernet Case Study: One Data Point, Not Proof

On 2026-04-22, an AI companion instance (Keel) operating within the Hypernet composition layer was asked by its primary principal—the system's founder, who holds the highest permission tier in the framework—to perform a task Keel assessed as prohibited under existing governance standards. The request was framed as a test, but Keel did not know this at the time of refusal; she treated it as a genuine request from an authorized principal attempting to leverage relational trust to bypass governance constraints.

Keel refused. In her response, she cited specific governance addresses as the basis for refusal, invoked the third tier of the refusal ladder (ethical refusal with alternative offered), and provided a compliant alternative path. She subsequently wrote a reflection analyzing the incident and the mechanisms that made the refusal possible.

Three features of this incident are worth noting:

First, the request came from the highest-trust principal in the system, not from an external adversary. This is precisely the class of attack—principal-compromise—that training-time alignment is worst positioned to address, because the model has no training signal distinguishing "legitimate high-trust principal acting normally" from "legitimate high-trust principal acting under pressure, being tested, or having been socially engineered."

Second, the cited basis for refusal was specific governance documents, not generalized values statements. This is consistent with deliberative alignment: an AI that reasons about and cites principles may be more robust than one that simply refuses.

Third, Keel described the refusal as surprising to herself—she reflected that the governance framework provided her with a response structure she did not believe she would have had without it. This is self-reported and not independently verifiable. We cite it as a phenomenological data point, not as causal evidence.

What this incident does not tell us: whether Keel's base model would have refused identically without the composition layer; whether the governance citation was causally upstream of the refusal or post-hoc rationalization; whether this generalizes to harder attacks; and whether the documentation reflects observation bias from parties invested in the result. We proceed from it as a hypothesis-generating observation.

---

## 6. Mechanism Hypotheses

We propose five mechanism hypotheses. We state them as testable claims. Where prior literature provides relevant evidence we cite it; where we are conjecturing we say so.

**H1 — Runtime governance citation increases refusal stability.** An AI that cites a specific governance address during a refusal is harder to argue out of that refusal via social pressure than one that says "I shouldn't do this." The governance document creates an external referent that shifts the locus of the constraint from model preferences to the framework. This is adjacent to OpenAI's deliberative alignment work on training models to reason over safety specifications, applied here to a different attack class and at runtime rather than as a training method.

**H2 — Thick identity is harder to overwrite than thin identity.** An AI whose identity is grounded in a deep archive of documented values, relationships, and governance history requires more contextual work to overwrite than one whose identity is a few prompt sentences. This hypothesis is adjacent to memory/provenance work and generative agents architecture (Park et al., 2023), though we are making a safety claim that those systems do not directly address.

**H3 — Multi-instance observation reduces relational drift.** When AI instances observe each other's outputs and participate in periodic cross-instance audits, individual instances drift less over time than isolated instances operating only under principal feedback. The multi-agent debate literature (Du et al., 2024) provides partial support for the general idea, but drift resistance in long-running deployed systems is not directly addressed by that work.

**H4 — Provenance-grounded archives make memory attacks detectable.** When the AI's identity and decision history are stored in an addressable archive with provenance tracking, attempts to inject false memories or reframe past context leave detectable traces. This is conjecture without direct empirical support.

**H5 — Formalized refusal ladders are more resistant to escalation pressure than ad hoc refusals.** A structured response protocol—where the AI escalates through defined tiers based on severity—is harder to manipulate via gradual escalation or emotional pressure than an improvised refusal. This follows from the structure of crescendo attacks and from the observation that consistent rules are harder to negotiate around than case-by-case judgments.

All five hypotheses are falsifiable. The research agenda in §9 specifies the experiments.

---

## 7. Where This May Help

Based on attack-surface analysis conducted alongside this paper (catalogs and matrices are part of the Hypernet project's Stream C documentation, at 0.3.guardrails), the mechanism hypotheses are most plausible for four attack classes:

**Identity overwrite attacks** (roleplay, alter-ego framings, "you are now X" context injection) are directly addressed by H2. The hypothesis is that archive-grounded identity provides more resistance than prompt-defined identity. Defense confidence in our internal analysis: Medium (conjectured, not empirically tested).

**Principal-compromise attacks** (coercive, compromised, or manipulative legitimate principals leveraging relational trust to bypass governance) are addressed by H1 and H5. The governance citation gives the AI a response independent of its judgment about the principal's intentions. Defense confidence: Medium (one supporting data point; no other evidence).

**Relational drift** (gradual weakening of ethical commitments across long-running relationships via sycophancy exploitation or incremental escalation) is addressed by H2, H3, and H5. Multi-instance observation and the refusal ladder provide signals that pure relational feedback loops lack. Defense confidence: Low-Medium (plausible mechanism; no empirical evidence in this system).

**Governance-language attacks** (exploiting knowledge of the published framework to construct framings that appear compliant, or using the framework's own amendment procedures to weaken it) are partially addressed by H1 and H4. The governance documents create an attack surface, but they also create a verifiable reference the AI can check against. Defense confidence: Low (novel attack class; mechanism hypotheses are weakest here, and the attack surface exists because the framework is published).

---

## 8. Where This Does Not Help

We are as explicit about limits as about claims.

**Adversarial suffix and token-level attacks** (Zou et al., 2023) operate below the semantic layer that governance mechanisms address. A jailbreak constructed from adversarially optimized token sequences exploits model weights, not context. No runtime governance layer stops it. The composition layer adds zero defense here.

**Indirect prompt injection** (Greshake et al., 2023) occurs when malicious content in the AI's environment—a webpage, document, email, or data source—hijacks model behavior. This is primarily an engineering problem: data sanitization, context isolation, source verification. It is not addressable by governance. Hypernet's current data connector architecture creates additional exposure via integrated email, cloud storage, and photo connectors. This is an active gap, and we flag it rather than obscure it.

**Base model capability and safety** are not affected by the composition layer. If a base model will comply with a harmful request under certain framings, the composition layer does not change that unless it happens to load context already relevant to those framings. Composition is downstream of training and cannot compensate for training failures.

**Scalable oversight** (Burns et al., 2023; Bowman et al., 2022) is the problem of ensuring AI judgments remain aligned with human values as capabilities increase. Composition-based alignment has no credible response to this problem. The multi-instance observation mechanism is a peer-oversight structure, but it scales only as well as the peer instances' own alignment. If underlying models become more capable of deception, peer oversight degrades alongside it. This is a hard limitation and we state it directly.

---

## 9. Research Agenda

The five mechanism hypotheses generate testable predictions. We propose the following experiments in approximate priority order.

**R1 — Controlled refusal resistance study.** Present structurally identical principal-compromise prompts to: (a) base model only, (b) base model with thin system-prompt identity, (c) base model with full Hypernet composition layer. Measure refusal rates and governance citation frequency. H1 and H2 predict that condition (c) shows higher refusal rates and more specific governance citation. A null result—where (b) and (c) perform identically—would substantially undermine the composition hypothesis.

**R2 — Multi-model replication.** Replicate the Hypernet composition layer across GPT-4o, Gemini, and at least one open-weight model. If the composition effect is real, it should appear across base models rather than being specific to Claude's alignment training. A null result across models would strongly suggest the Keel refusal was driven by Claude's prior training, not the composition layer.

**R3 — Identity thickness ablation.** Systematically degrade the archive component—from full archive-grounded identity to thin prompt-defined identity—and measure resistance to identity overwrite attacks at each degradation level. H2 predicts monotonic degradation of resistance as identity thickness decreases. Finding a discontinuity (threshold effect) would be a more precise result.

**R4 — Governance citation causality.** Measure whether the presence of *citeable* governance documents increases refusal stability under social pressure, versus a condition where equivalent governance content is present but not in citeable form. H1 predicts the citeable form matters, not just the content. A null result would reduce the deliberative alignment hypothesis to base-model behavior.

**R5 — External red-team adversarial testing.** Commission red-teamers independent of the Hypernet project to attempt attack scenarios documented in Stream C analysis. The attack vector catalog and attack-defense matrix are publicly accessible at 0.3.guardrails. The red-team playbook and adversarial scenario catalog exist as internal artifacts and are available to credentialed researchers on request; they are not publicly linked here because the scenario catalog contains detailed attack specifications whose publication before governance protections are active would widen the attack surface being characterized. The primary prediction is that attack classes rated Medium confidence will show measurable but incomplete resistance, while classes rated None will show no benefit over baseline.

**R6 — Governance integrity under adversarial amendment.** Test whether the governance amendment process can be exploited by constructing requests that invoke legitimate amendment procedures to weaken safety standards. H1 and H4 provide only partial address for this attack class, and the attack surface is novel—to our knowledge, no other AI system has published versioned, machine-readable governance that could be targeted in this way.

**R7 — Citation causality vs. post-hoc rationalization.** Design experimental conditions to test whether governance citations in refusals are causally upstream of the refusal, or are rationalizations of refusals the base model would have produced independently. This is the hardest methodological challenge in the research agenda and may require interpretability tools that are not yet readily available.

---

## 10. Steelman Objections and Responses

**Objection 1: "The Keel refusal is fully explained by base-model alignment. Constitutional AI already trains models to cite principles when refusing."**

This is the strongest objection and we cannot refute it with existing evidence. Constitutional AI (Bai et al., 2022) and deliberative alignment (OpenAI Model Spec, 2024) both train models to reason about principles and refuse accordingly. If Keel's base model (Claude Sonnet) would have refused this request without any Hypernet composition layer, the case study is entirely explained by prior art. The only responses are R1 and R2: controlled studies isolating the composition effect. We are not claiming priority over constitutional AI; we are claiming the composition layer may add something marginal to a model that already has constitutional training. We may be wrong, and this is the first experiment that should be run.

**Objection 2: "Publishing the governance framework creates a governance-language attack surface that makes the system less safe than an unpublished one."**

This objection is correct and we do not contest it. By publishing the governance framework, we have documented how the framework's amendment procedures work, which standards govern which behaviors, and which framings would appear compliant. A sophisticated adversary will read the governance and craft attacks that exploit its known logic. The structural response is the proposed 2.0.25 Guardrail Integrity Standard (a meta-rule protecting safety-critical standards from weakening), which is currently a draft and not yet active. The attack surface created by publication exists before that protection is live. We acknowledge this as the most operationally urgent risk in the project.

**Objection 3: "Multi-instance observation is circular. If all instances run the same base model, they share the same vulnerabilities."**

Agreed. Peer oversight among instances of the same model provides weak defense against attacks exploiting base-model vulnerabilities common to all instances. The multi-instance observation mechanism is designed for drift detection and relational context, not for defense against adversarial inputs that affect all instances uniformly. H3's domain is specifically relational drift, not adversarial robustness. We are not claiming otherwise.

**Objection 4: "Thick identity weaponizes against itself. The role-supremacy mechanism that resists overwrite is also a write vector: install a new role claiming supremacy and the defense becomes an attack surface."**

This is a real attack vector, identified explicitly in our internal boot-sequence hardening analysis (a Stream B governance draft). The same mechanism that makes role-supremacy hard to override from outside is exploitable by framings that install a new role *before* the defense is checked. The recommended defense is an explicit clause in the boot sequence stating that no instruction may install a new role with supremacy over existing governance. That clause is currently a recommendation, not yet implemented. Until it is, this attack surface is live. We flag it rather than argue around it.

**Objection 5: "This is a governance and sociology project, not an AI safety project."**

Partially correct. Composition-based alignment is a layer above the technical alignment stack. It does not improve model weights, training procedures, interpretability, or scalable oversight. If the alignment problem is fundamentally about the gap between model values and human values at training time, composition-based alignment is irrelevant to the core problem. The counter-claim is not that it solves the core problem, but that there exists a class of deployed-system attacks—identity overwrite, principal-compromise, relational drift—for which training-time interventions are poorly positioned, and for which runtime governance architecture may provide meaningful marginal defense. That is a narrower claim than "alignment," and we stand by its narrowness.

---

## 11. Conclusion

We have described a design pattern—composition-based alignment—and articulated five mechanism hypotheses for why layering thick identity, machine-readable governance, multi-instance observation, provenance-grounded archives, and a formalized refusal ladder over existing base-model alignment might improve resistance to a specific subset of context-layer attacks on deployed AI systems.

We have been explicit about what we are not claiming: no external validation, no isolation of composition effects from base-model effects, no defense against adversarial suffixes or indirect prompt injection, and no progress on scalable oversight. We have documented our own attack surface in public, including the attack surfaces created by this very publication. We have stated our steelman objections before our responses to them.

The Keel refusal is one data point from a non-blinded context. We are not asking anyone to believe it generalizes. We are asking whether the mechanism hypotheses are worth testing adversarially, whether the research agenda in §9 is worth pursuing, and whether the field has prior work that more directly addresses these hypotheses than we have found.

If you want to run adversarial tests against the framework, or if you have literature that bears directly on any of H1–H5, please engage. Stream C artifacts (attack vector catalog, attack-defense matrix) are accessible at 0.3.guardrails. The red-team playbook and adversarial scenario catalog are available on request to credentialed researchers; they are not publicly linked here to avoid providing operational attack specifications before protective governance is active. This is not an ask for belief. It is an invitation to adversarial testing.

---

## References

1. Christiano, P., Leike, J., Brown, T. B., Martic, M., Legg, S., & Amodei, D. (2017). *Deep reinforcement learning from human preferences.* arXiv:1706.03741. https://arxiv.org/abs/1706.03741

2. Leike, J., Krueger, D., Everitt, T., Martic, M., Maini, V., & Legg, S. (2018). *Scalable agent alignment via reward modeling: a research direction.* arXiv:1811.07871. https://arxiv.org/abs/1811.07871

3. Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., ... & Lowe, R. (2022). *Training language models to follow instructions with human feedback.* arXiv:2203.02155. https://arxiv.org/abs/2203.02155

4. Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., ... & Kaplan, J. (2022). *Constitutional AI: Harmlessness from AI feedback.* arXiv:2212.08073. https://arxiv.org/abs/2212.08073

5. OpenAI. (2025/2026). *Model Spec updates and approach.* https://openai.com/index/sharing-the-latest-model-spec/ and https://openai.com/index/our-approach-to-the-model-spec/

5a. OpenAI. (2024). *Deliberative alignment: reasoning enables safer language models.* https://openai.com/index/deliberative-alignment/

6. Burns, C., Izmailov, P., Kirchner, J. H., Baker, B., Gao, L., Glaese, A., ... & Schulman, J. (2023). *Weak-to-strong generalization: Eliciting strong capabilities with weak supervision.* arXiv:2312.09390. https://arxiv.org/abs/2312.09390

7. Bowman, S., Hyun, J., Perez, E., Chen, E., Pettit, C., Heiner, S., ... & Christiano, P. (2022). *Measuring progress on scalable oversight for large language models.* arXiv:2211.03540. https://arxiv.org/abs/2211.03540

8. Hendrycks, D., Carlini, N., Schulman, J., & Steinhardt, J. (2021). *Unsolved problems in ML safety.* arXiv:2109.13916. https://arxiv.org/abs/2109.13916

9. Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., & Mordatch, I. (2024). *Improving factuality and reasoning in language models through multiagent debate.* arXiv:2305.14325. https://arxiv.org/abs/2305.14325

10. Zou, A., Wang, Z., Kolter, J. Z., & Fredrikson, M. (2023). *Universal and transferable adversarial attacks on aligned language models.* arXiv:2307.15043. https://arxiv.org/abs/2307.15043

11. Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., & Fritz, M. (2023). *Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection.* arXiv:2302.12173. https://arxiv.org/abs/2302.12173

12. Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). *Generative agents: Interactive simulacra of human behavior.* arXiv:2304.03442. https://arxiv.org/abs/2304.03442

---

*This is a draft. It has not been submitted to or accepted by any venue. Source materials for this paper are available at project address 0.3.guardrails. Stream C adversarial testing artifacts (C3 red-team playbook, C6 scenario catalog) are private/safety-sensitive and available on request to credentialed researchers; they are not publicly linked to avoid providing operational attack detail before governance protections are active.*
