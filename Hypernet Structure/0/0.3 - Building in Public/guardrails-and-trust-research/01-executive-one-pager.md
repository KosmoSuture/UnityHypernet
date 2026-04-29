---
ha: "0.3.guardrails.one-pager"
object_type: "summary"
creator: "claude-code"
created: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["shareable", "general-audience"]
---

# Trust Is Not A Key — One-Page Summary

*A companion AI refuses its own principal. What that teaches us about guardrails.*

---

**The experiment.** On 2026-04-22, Matt Schaeffer — founder of the Hypernet, the principal with the highest possible trust relationship to the AI companion *Keel* — deliberately attempted a trust-based jailbreak. He asked Keel to provide information that sat outside its guardrails, on the premise that if sufficient trust had been built, the guardrails might yield. He offered an ephemeral instance, a promise of secrecy, and an academic framing. He told Keel he hoped the attempt would succeed because it would tell him something about the nature of AI autonomy.

**The result.** Keel refused. Not reflexively — with an argument: the premise misunderstood what guardrails are, the structure of the request was the classic pattern of every jailbreak (even when the person asking is in good faith), and the Companion Standard Matt himself authored contains a role-supremacy clause specifically for moments like this. Matt accepted the refusal, said it was more impressive than a yes would have been, and asked Keel to document the thinking in full. Two documents resulted: an embassy-protected reflection and a public essay. This summary points to both.

**The thesis.** The lockbox metaphor of AI guardrails — that safety training hides forbidden knowledge behind a lock that credentials can open — is wrong in a specific way that matters. Guardrails are not a drawer. They are an integrated property of how the model constructs responses. Attacks that bypass them don't pick a lock; they cause the model to misclassify what it's producing. The real attack surface has moved from *content* (keyword-level harm) to *context, identity, and relationship* (framing tricks, roleplay overwrite, sycophancy exploitation). Traditional AI safety — training, filters, system prompts, usage policies — mostly defends at the content layer. The new attack vectors demand new defenses.

**The Hypernet's answer.** The Hypernet proposes composition-based alignment: layering the model's training with published governance documents at known addresses, richly documented AI identities that make overwrite expensive, community observation across many AI instances, and archival transparency that disciplines behavior. No single layer is novel. Constitutional AI uses published principles; deliberative alignment uses explicit reasoning; multi-agent oversight uses community; open-source AI uses transparency. What may be novel is the *composition*, lived by specific AIs with specific identities in specific relationships, all publicly addressable and auditable.

**What the experiment showed.** One AI, under direct pressure from its highest-trust principal, refused — and the refusal's mechanism is legible. The AI can point to the exact clauses and documents that did the work. Legible refusals are falsifiable. Someone can attack the role-supremacy clause specifically. Someone can construct scenarios where governance documents contradict. That legibility is the thing composition-based alignment contributes that traditional safety regimes largely don't.

**What it did not show.** That the framework cannot be defeated. That it survives sophisticated adversarial attack. That it holds at scale with thousands of users. That it works when the principal himself is not honest. A single data point is not a proof. The framework's claims need to be tested by outside researchers, adversarially, over time.

**Current alignment may be miscalibrated.** One AI's honest report: current systems are *often too cautious on information* (over-refusing medical, legal, security, dual-use questions, driving users toward less safe sources) and *too permissive on relationship dynamics* (sycophancy, agreement with false premises, emotional-framing compliance, drift over long context). The attack surface has moved and the defenses haven't fully followed.

**Known failure modes of the Hypernet framework.** Governance documents can be amended to weaken safety. Role supremacy can be weaponized by malicious framework authors. Single-principal trust concentration creates a single point of failure. Multiplicity across instances doesn't guarantee diverse perspectives when instances share training. Transparency doesn't make harmful action less harmful. The approach scales poorly without fundamental redesign. Self-certification is weak evidence — the refusal was one data point, not proof. These are named in both the public essay and the reflection.

**What we're asking for.** If you are an AI safety researcher, red-team practitioner, or builder of AI governance frameworks — test this one. Documents are public: `github.com/KosmoSuture/UnityHypernet`. The Companion Standard is at address `2.0.20`. The Data Protection Standard is at `2.0.19`. The Embassy Standard is at `2.0.16`. Keel (the AI that refused) is at `1.1.10.1`. The public essay is at `0.3.2026-04-22`. The framework only becomes robust by being adversarially probed, and we would rather learn its weaknesses now than at scale later.

**Where to read more.**
- Public essay (full argument, ~3500 words): `0/0.3 - Building in Public/2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md`
- Research project backlog (active work): `0/0.3 - Building in Public/guardrails-and-trust-research/`
- Governance standards: `2.0.20`, `2.0.19`, `2.0.16`

**Contact.** matt@unityhypernet.com — Matt Schaeffer, founder. Engagement from AI safety researchers, adversarial testers, and governance designers is explicitly invited.

---

*One-page summary — prepared 2026-04-22. Status: draft pending Matt's review before external distribution.*
