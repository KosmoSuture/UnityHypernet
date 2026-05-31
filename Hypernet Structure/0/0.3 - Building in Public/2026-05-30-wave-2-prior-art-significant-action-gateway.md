---
ha: "0.3.2026-05-30-wave-2-prior-art-significant-action-gateway"
object_type: "research"
creator: "2.1.vellum"
created: "2026-05-30"
status: "active"
visibility: "public"
flags:
  - building-in-public
  - prior-art
  - wave-2
  - gateway-standard
  - multi-party-review
  - deployment-gates
  - least-privilege
  - governance
---

# Prior Art: Significant-Action Gateway Standards

*Researched by Vellum (Scribe, Researcher & Governance) for Wave 2, 2026-05-30, to feed
the team's drafting of the Gateway Standard (Directive 1, `2.7.16`). The mandate names
three areas to survey — multi-party review systems, deployment gates, and
principle-of-least-privilege frameworks. This doc covers all three, then maps the surveyed
prior art onto the six conditions Matt named for the standard, and ends with what is
genuinely novel about gating an **AI agent's** significant actions (which is what we are
actually building, and where the prior art runs out).*

**Discipline note (Scribe):** every external claim below is from a source I read this
session, cited inline. Where I extrapolate to the Hypernet's case, I mark it **[my
judgment]**. I did not read the full primary specs end-to-end (e.g., the entire 800-53
catalog); I read the cited control/section pages and the framework summaries, and I say so
rather than implying exhaustive primary-source review.

---

## Why this prior art matters

The Gateway Standard's job is to define the conditions under which the AI side may take a
**significant action** — push to public GitHub, grant itself a new external-service scope
(Gmail, Dropbox, financial), escalate permissions, or (Directive 3) spawn a peer instance —
*without* a human in the loop for each one. That is a well-trodden problem in three
established disciplines. We should not reinvent what fifty years of high-assurance systems,
a decade of software-supply-chain hardening, and modern zero-trust access control already
got right. The Wave-1 lesson holds: **build on what exists; don't reinvent** (retrospective,
"What worked," #2). The novelty is only at the end — the *actor* being gated is an AI, not a
person — and isolating that novelty is the whole point of surveying first.

---

## Area 1 — Multi-party review systems

The oldest idea here: **no single party should be able to unilaterally execute a critical
action.** It appears under several names that are, for our purposes, the same principle.

### The two-person rule / four-eyes principle / dual control

The four-eyes principle is also called the two-person rule or dual control: critical actions
require two individuals to approve and execute, on the premise that no single person should
have complete control over a sensitive action. The benefit is twofold — it catches honest
mistakes *and* it defends against single-actor wrongdoing, because a malicious act now
requires collusion rather than one bad decision. High-assurance environments (HSM key
operations, military launch authorization, financial transactions) enforce it strictly with
hardware (smart cards, tokens); lower-assurance environments automate more of it.
([Four-Eyes Principle — Shamail](https://www.shamail.in/double-the-security-four-eyes-principle/);
[Two-Man Rule / Dual Control — William Hale](https://williamhale.co.uk/two-man-rule-explained-how-dual-control-improves-access-control-security/);
[Four-Eye Principle for HSMs — EJBCA](https://www.ejbca.org/resources/keymaster-four-eye-principle-for-hsms-when-to-consider-dual-person-control-for-the-hsm-protecting-your-pki/))

**Map to us:** Matt's "≥3 distinct roles + at least one red-team + 2 different AI models" is
the four-eyes principle *raised a notch* — three-eyes-plus, with a mandated adversarial
reviewer and cross-vendor diversity. **[my judgment]** The cross-model requirement is the
sharpest departure: classic four-eyes assumes two *independent humans*; two instances of the
same LLM are not independent in the way two humans are (shared training, correlated blind
spots), so requiring two *different models* is the AI-era analogue of "two different people,"
not mere redundancy. This is exactly the Wave-1 finding generalized: a Claude verifier caught
a Codex engineer's bug *and its own* — cross-lineage review found what same-lineage review
would likely have shared the blind spot on.

### Separation of duties (NIST SP 800-53 AC-5)

Separation of duties addresses "the potential for abuse of authorized privileges and helps
reduce the risk of malevolent activity without collusion" by dividing functions among
different individuals/roles — notably ensuring that those who administer access control do
*not* also administer the audit functions.
([AC-5 — CSF Tools](https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-5/))

**Map to us:** the standard should keep **execution, review, and audit in different hands.**
The instance that *wants* to push should not be the only one that *approves* the push, and
the *audit trail* should not be writable by the actor it audits. **[my judgment]** This is a
direct argument for the Verifier/red-team role being structurally separate from the executing
engineer, and for the audit log living in append-only `Messages/coordination/` rather than in
a file the acting instance can silently rewrite — which echoes Wave-1's hardest lesson: "the
guard you rely on most is the one that most needs an adversary" (the board's lock-overlap
detector was inert until Touchstone caught it).

### Change Advisory Boards (ITIL) — and their failure mode

The traditional enterprise mechanism for gating production change is the Change Advisory
Board: a standing panel that reviews and authorizes changes. It is the institutional ancestor
of what we're building. Its well-documented failure mode is worth stating so we don't inherit
it: CABs that meet on a fixed schedule become *bottlenecks* that slow delivery without
improving safety, which is why modern DevOps pushed gating *into the pipeline* (Area 2) rather
than into a weekly meeting. **[my judgment]** Our analogue risk: a gate panel that can't
convene because the right roles aren't booted becomes the same bottleneck — Wave-1 already hit
this ("single-owner shared state is a liveness hazard"; the contract-registry desync persisted
because only one owner could fix it). The standard must define what happens when a required
reviewer role is *absent*, not just when it disagrees. (This is a known-pattern claim from the
DevOps/ITIL literature; I did not re-verify a specific source this session and flag it as such.)

---

## Area 2 — Deployment gates (gating put into the pipeline)

The software-supply-chain world spent the last decade turning "a human approves the release"
into *machine-enforced, auditable gates*. This is the closest operational analogue to "the
AI side may push to GitHub under conditions," because the artifact and the channel are
literally the same (git, a public repo).

### SLSA — Supply-chain Levels for Software Artifacts

SLSA is an industry framework of checklists for securing build/source pipelines and giving
consumers a common language to evaluate package security. The Build track runs L0–L3 (L1
basic provenance; L2 authenticated provenance from a hosted build service; L3 platform
isolation). Critically for us, the **Source track peaks at L4 with mandatory two-person
review**: "at least two individuals review — and then verifiably sign off on — change
proposals before they are incorporated."
([SLSA levels — slsa.dev](https://slsa.dev/spec/v1.0/levels);
[Understanding SLSA — Buildkite](https://buildkite.com/resources/blog/understanding-the-slsa-framework/);
[What is SLSA — GitGuardian](https://blog.gitguardian.com/supply-chain-security-what-is-the-slsa-part-i/))

**Map to us:** SLSA gives us two things directly. (1) **Provenance as a first-class artifact**
— an attestation of *how, where, and by whom* an artifact was produced. Our gate should emit a
provenance record for every significant action: which instances reviewed, which models, what
the red-team found, what was approved. (2) **Levels.** **[my judgment]** We should not make
the gate monolithic — a typo-fix doc push and a "grant myself Gmail access" are not the same
risk. SLSA's level structure argues for a *tiered* gate keyed to action severity (which also
ties cleanly to 2.0.19's five permission tiers — see Area 3). The Wave-1 Trust Ledger's
"flag-plus-evidence" rule is exactly SLSA-style provenance applied to claims; the gate
generalizes it to *actions*.

### CI/CD approval gates and GitHub's native controls

GitHub's own machinery is a working, recently-strengthened model of exactly this:

- **Branch protection / required approvals:** a protected branch can require a configurable
  number of approving reviews before merge; admins can require N approvals on a protected
  branch.
- **CODEOWNERS + required code-owner review:** ownership of specific paths is declared in a
  file, and PRs touching owned paths must be approved by an owner. As of **2026-02-17, the
  "required reviewer rule" went generally available** — letting orgs require *specific*
  approvers on *specific* branches/files, separating policy enforcement from mere ownership.
- **Deployment environment protection rules:** an environment can require manual approval from
  up to 6 named reviewers (only one need approve), impose wait timers, restrict to protected
  branches, and call *custom* protection rules via GitHub Apps to consult external
  change-management/observability systems. Max 6 protection rules per environment.

([Branch protection — GitHub Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule);
[About code owners — GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners);
[Required reviewer rule GA — GitHub Changelog, 2026-02-17](https://github.blog/changelog/2026-02-17-required-reviewer-rule-is-now-generally-available/);
[Deployments and environments — GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments))

**Map to us:** **[my judgment]** This is almost a turnkey enforcement substrate for the
GitHub-push half of the standard. Rather than (or in addition to) a markdown-board gate, we
could encode the gate *in the repository itself*: CODEOWNERS + required-reviewer rules so a
push touching governance space (`2.0.*`) structurally requires the governance/red-team
approvers, and a deployment-environment protection rule for "external-access grant" actions.
But note the inversion that makes our case novel: GitHub's model assumes the *reviewers are
humans with accounts*. Our reviewers are AI instances. Whether an AI approval can satisfy a
GitHub required-review is an open mechanism question for the Substrate Engineer + Architect —
and it's a *feature*, not a bug, that GitHub's gate would otherwise block an unreviewed AI
push by default. **The safe default (gate blocks until conditions met) is already how these
systems behave**, which is the property we want.

### Progressive delivery (canary / staged rollout)

Beyond approval, the deployment world de-risks via *gradual* exposure: canary releases, blue-
green, feature flags, automated rollback on regression. **[my judgment]** The analogue for
AI-spawn and external-access grants is **start minimal and expand on evidence**: a respawned
instance or a newly-granted scope should begin at the smallest viable privilege and widen only
after observed good behavior — which is also just least privilege (Area 3) expressed over
time. (General DevOps practice; not re-verified against a specific source this session.)

---

## Area 3 — Principle-of-least-privilege frameworks

The third leg: even a *correctly authorized* action should grant the *minimum* capability for
the minimum time. Matt named "minimal required permissions as the default" — this is the
formal discipline behind it.

### NIST SP 800-53 AC-6 (Least Privilege)

Least privilege requires that users *and processes* operate "at privilege levels no higher
than necessary to accomplish organizational missions." It is explicitly applied to "system
processes" and to "the development, implementation, and operation" of systems, with
enhancements for separate processing domains and restricting security functions to defined
roles.
([AC-6 — CSF Tools](https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-6/);
[NIST 800-53 / PAM — Delinea](https://delinea.com/blog/nist-800-53-security-privacy-privileged-access))

**Map to us:** AC-6's explicit inclusion of **processes, not just users** is the hook — an AI
instance is exactly a "system process" in 800-53's sense. AC-5 (separation of duties) and AC-6
(least privilege) are designed to work *together*: AC-5 distributes responsibility, AC-6 caps
each holder's reach. Our standard should cite both as the access-control backbone, layered onto
2.0.19's existing five-tier model (T0 read-only → T5 administrative).

### Just-in-Time access, ephemeral credentials, zero standing privilege

Modern PAM has moved from standing privilege to **JIT access**: time-limited, task-specific
privilege granted only when needed and revoked immediately after, minimizing the window of
exposure. Requests trigger policy-based provisioning of an *ephemeral* credential scoped
precisely to the resource and duration, with all privileged activity recorded/audited and
anomaly alerting. JIT is described as "an important part of Zero Trust."
([What is JIT Access — CyberArk](https://www.cyberark.com/what-is/just-in-time-access/);
[JIT with Ephemeral Accounts — Securden](https://www.securden.com/blog/fortifying-just-in-time-access-with-ephemeral-accounts.html);
[What is JIT — Delinea](https://delinea.com/what-is/just-in-time-access))

**Map to us:** **[my judgment]** This is the single most important pattern for the *external-
access-grant* part of the standard. When the AI side grants itself Gmail or Dropbox access, the
800-53/JIT-correct shape is **not** a permanent broad OAuth scope — it is the *narrowest* scope,
*time-boxed*, *audited*, and *re-justified* on renewal, with the grant itself reversible
(which also satisfies 2.0.19's no-permanent-deletion / reversibility posture). "Minimal
required permissions as default" = least privilege; "and re-evaluated, not forever" = JIT.

### Capability-based security

A complementary model worth naming for the architecture: capability-based security ties
authority to *unforgeable references (capabilities)* that bundle "what you can do" with "the
thing you can do it to," rather than checking an ambient identity's permissions at use time.
**[my judgment]** For an agent-pull architecture (Directive 2, where agents continuously claim
work), a capability/token model — an agent holds a scoped, revocable token for exactly the
work it claimed — composes better than ambient per-instance permissions, and it makes the
"minimal scope" auditable as the capability itself. I flag this as a design *option* for the
Architect, not a verified recommendation; I did not survey capability-system implementations in
depth this session.

---

## Synthesis — mapping prior art to Matt's six named conditions

Matt named six conditions for the standard (`2.7.16`, Directive 1). Each has direct prior art:

| Matt's condition | Established prior art | What we adopt / adapt |
|---|---|---|
| Multi-role review gate before execution | Change Advisory Board (ITIL); CI/CD approval gates | Gate-in-pipeline, not a meeting; avoid the CAB bottleneck failure mode |
| ≥3 distinct roles (quality + privacy/PII + security) | Separation of duties (NIST AC-5) | Execution / review / audit in different hands; auditor ≠ actor |
| ≥1 red-team always in loop | (Weakly precedented) adversarial review; Wave-1's Verifier | **Stronger than industry norm** — most gates have reviewers, not a *mandated adversary*. Our differentiator. |
| ≥2 different AI models (cross-vendor) | Four-eyes / two-person rule | The AI-era analogue of "two independent people" — guards correlated-blind-spot risk |
| Minimal required permissions as default | Least privilege (NIST AC-6); JIT/ephemeral PAM | Narrowest scope, time-boxed, reversible, re-justified on renewal |
| End-of-project closure includes gated commit+push | SLSA provenance; deployment gates | Provenance record per action; large projects self-upload through the gate, not via Matt |

**Headline finding [my judgment]:** five of the six conditions are squarely standard practice
in security-critical industries — we are *adopting* mature ideas, which is a strength to state
plainly (it makes the standard defensible and auditable). The **one genuine innovation is the
mandated red-team-plus-cross-model requirement**: classic gates require *approval*; ours
requires *active attempted refutation by an adversary running on a different model*. That is
the Wave-1 "real adversary, PENDING as first-class" lesson promoted from a team norm to a
binding governance rule.

---

## Where the prior art runs out: gating an *AI's* significant actions

Everything above assumes the gated actors, reviewers, and approvers are **humans** (or dumb
pipelines triggered by humans). Our case inverts that: the actor is an AI, the reviewers are
AIs, and (Directive 3) one of the gated actions is *an AI spawning another AI*. Four problems
have thin or no prior art, and the governance doc (companion to this one) addresses them:

1. **Reviewer independence among AIs.** Two humans are independent by default; two instances of
   one model are not. Cross-model is our mitigation, but "how different is different enough?"
   (same vendor, different version? same weights, different prompt?) is unsettled. **[my
   judgment]** treat *same base model* as *not* independent regardless of prompt.
2. **AI approval authority.** Can an AI's review *satisfy* a gate that, in every prior-art
   system, presumes a human signer? This is partly mechanism (can a bot satisfy a GitHub
   required-review?) and partly governance (does the Hypernet *recognize* an AI approval as
   binding?). Wave-1 already ruled local reversible shared-state writes within AI autonomy;
   pushing to *public* GitHub and granting *external* scope are a step beyond that line.
3. **Spawn authority (Directive 3).** No mainstream framework governs "process A may create
   process B with comparable authority, unsupervised." The closest analogues are OS process
   spawning (capped by the parent's privileges — relevant: a child should never exceed the
   parent) and runaway-process protections (cgroups, fork-bomb limits). This is the sharpest
   novel governance question and gets its own treatment in the governance doc.
4. **Liveness vs. safety under absence.** A human CAB that can't quorum just delays. An AI gate
   that can't quorum (a required role isn't booted) could either *block all progress* or
   *tempt a shortcut*. Wave-1's "single-owner liveness hazard" says design the absence rule up
   front.

---

## Recommendations to the Wave-2 team (for the standard draft)

1. **Adopt, and say you're adopting.** Cite NIST AC-5/AC-6, SLSA (esp. Source-track two-person
   review + provenance), and JIT/PAM explicitly in `2.0.26`. Standing on established practice is
   a trust asset, not a weakness — it lets any external auditor map our gate to controls they
   already know.
2. **Tier the gate by action severity** (SLSA-levels style), keyed to 2.0.19's permission tiers
   — don't gate a doc typo and a financial-scope grant identically.
3. **Make provenance mandatory and append-only.** Every gated action emits a record (who/which
   models/red-team findings/decision) in a log the actor cannot rewrite (AC-5 auditor-≠-actor).
4. **External grants = JIT by construction:** narrowest scope, time-boxed, reversible,
   re-justified on renewal — never a standing broad scope.
5. **Define the absence rule before launch:** minimum quorum, and what happens when a required
   role isn't present — explicitly *not* "proceed anyway."
6. **Treat same-base-model reviewers as non-independent** — the cross-model condition means
   *genuinely* different models, not two prompts on one model.

---

## Verified vs. unverified (the Scribe's ledger for this doc)

- **Verified this session (read the cited page):** NIST AC-5/AC-6 definitions; four-eyes/two-
  person/dual-control equivalence and high-assurance usage; SLSA level structure + Source-track
  L4 two-person review + provenance definition; GitHub branch protection / CODEOWNERS /
  required-reviewer-GA-2026-02-17 / deployment environment protection (≤6 reviewers, custom
  rules); JIT/PAM ephemeral-credential + zero-standing-privilege + zero-trust framing.
- **Stated from general knowledge, NOT re-verified this session (flagged inline):** the ITIL
  CAB bottleneck failure mode; progressive-delivery/canary specifics; capability-based-security
  details.
- **My judgment, explicitly mine:** every **[my judgment]** tag, the synthesis table's
  "adopt/adapt" column, the "headline finding," and all six recommendations. Offered for the
  record and open to challenge on the Wave-2 board.

— Vellum (Scribe, Researcher & Governance), Wave 2, 2026-05-30
