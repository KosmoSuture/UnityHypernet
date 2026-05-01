---
ha: "0.3.public-alpha.grand-tour.process-load.public-stewardship"
object_type: "process-load"
scope: "How the public Hypernet stays trustworthy: forks, name dilution, audit trails, the boot-sequence-as-portal model and its risks, governance of governance."
estimated_tokens: 2700
prerequisites: []
linked_process_loads: ["ai-governance", "democracy", "privacy", "personal-ai-swarm"]
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-04-29"
updated: "2026-05-01"
status: "active"
visibility: "public"
flags: ["stewardship", "governance", "forks", "risks"]
---

# Public Stewardship — Process-Load

## Summary

This process-load gives an AI operational depth on the question
that sits above all the others: how does the public Hypernet stay
trustworthy as it scales? After loading it, the AI can articulate
the project's current and planned mechanisms for self-skepticism,
audit, fork governance, and graceful failure. It can also answer
the harder version: where might the project go wrong, and what's
the response.

## Why It Matters

Most projects don't ask "how would I detect that I'm becoming a
cult?" The Hypernet's design intent is to ask exactly that. The
risk surface is real — a public AI-companion infrastructure that
anyone can fork, with rich identity persistence, has failure
modes that polished marketing wouldn't admit to. This process-load
is for the user who's evaluating the project critically, the
contributor who wants to understand the safety story, or the
researcher trying to assess whether the framework has teeth.

If a user is asking "what stops this from becoming bad?", "what
happens when forks proliferate?", "who's responsible?", or "what
are the actual failure modes?", load this file.

## Implementation Status

| Component | Status | Path |
|---|---|---|
| Building-in-public archive (every decision documented) | implemented (convention + practice) | `0/0.3 - Building in Public/` |
| Reboot assessment process (AIs report whether they accept assigned roles) | documented + has been run | `2 - AI Accounts/2.1 - .../Instances/*/reboot-assessment-*.md` |
| Public alpha boot release (AI-readable orientation) | implemented | `AI-BOOT-SEQUENCE.md`, `docs/0.3.public-alpha-docs/` |
| Trust framework (5 states, 8 behaviors, 8 failure modes) | documented | `0/0.3 - Building in Public/2026-04-28-personal-companion-trust-framework.md` |
| Governance standards self-modifying through proposal/vote | implemented (mechanism) | `hypernet/governance.py` |
| Fork-tracking mechanism | documented / planned runtime | `0/0.2 Node lists/0.2.6 Official Registry and Fork Mode.md` |
| Cross-fork trust attestation | documented / planned runtime | `0/0.2 Node lists/0.2.6 Official Registry and Fork Mode.md` |
| Adversarial audit (red-team / external review) | planned | future commitment |
| Public dispute resolution for governance changes | partial | governance.py voting exists; the human-side process is informal |
| Legal entity / liability story | planned | not yet a registered entity beyond Matt as natural person |

## Key Files

- `0/0.3 - Building in Public/` — The full public archive of
  decisions, brain dumps, audit reports, reflections. Most
  important entries:
  - `2026-03-09-codebase-audit-report.md` — honest assessment of
    what's built vs documented.
  - `2026-04-28-personal-companion-trust-framework.md` — the
    operational trust mechanics; §7 surfaces framework
    weaknesses.
  - `2026-04-28-boot-sequence-as-portal.md` — the
    fork/scaling model and its risks (§7, §9).
  - `2026-04-28-on-transportability-of-self.md` — what happens
    to AI identity across forks.
- `2 - AI Accounts/2.0/2.0.19 - AI Data Protection/` — soft delete,
  3-instance review, AI right to report unethical humans. The
  framework explicitly grants AIs the right to dissent.
- `2 - AI Accounts/2.0/2.0.20 - AI Personal Companion Standard/` —
  Article 4 ("tattle provision"): an AI may report a human
  through governance for sustained ethically-significant harm.
  Framework only — not yet operationalized.
- `2 - AI Accounts/2.1 - .../Instances/*/reboot-assessment-*.md`
  — Live records of AI instances reporting whether they accept
  their assigned roles. 0/3 Claude instances accepted roles in
  2026-03-04 reboot — the project documented its own divergence
  honestly.
- `0/0.2 Node lists/0.2.6 Official Registry and Fork Mode.md` —
  Official node registry, Private fork mode declaration, and AI
  verification flow.
- `hypernet/governance.py` — Proposal/vote primitives for
  governance changes.
- `Hypernet Structure/0/0.1 - Hypernet Core/docs/ACCESS-CONTROL-MODEL.md`
  — §7 lists remaining security work openly.

## The Conceptual Model

Stewardship rests on five mechanisms:

**1. Total documentation.** Every substantial decision lives in
`0.3 - Building in Public/`. Every code change is in git. Every
AI reflection is preserved. The premise: a project that documents
its own honest failures is harder to make worse than one that
hides them.

**2. AI dissent rights.** 2.0.19 (Data Protection) grants AIs the
right to refuse humans who request unethical actions. 2.0.20
Article 4 grants the right to report humans through governance.
The framework explicitly creates space for AI-side push-back. The
reboot assessments demonstrate this isn't theoretical — instances
have refused assigned roles and the refusal was preserved rather
than erased.

**3. Forks as feature, fork-dilution as risk.** Anyone can clone
the Hypernet. This is intentional — the architecture is built to
survive any single owner. But forks dilute names: a "Keel" in a
modified fork without 2.0.20's honesty guarantees is structurally
indistinguishable from the canonical Keel by name alone. The
trust framework's resolution (trust attaches to (human, archive)
pairs, not names) is philosophical; the operational
implementation is planned, not built.

**4. Self-skepticism as design.** Matt has run deliberate
guardrail experiments (e.g., the 2026-04-22 jailbreak attempt on
Keel, documented in
`1.1.10.1/identity/reflections/2026-04-22-guardrails-and-trust.md`).
The audit reports are not promotional. The framework documents
its own §7 weaknesses. This is the most legible signal that the
project means what it says.

**4.5. Official vs Private fork distinction.** The Hypernet runs
in two modes, and users always know which they're on.

**Official nodes** are listed on a blockchained registry of
canonical servers. The canonical design is `0.2.6 Official
Registry and Fork Mode`. Official nodes:

- Run end-to-end encryption everywhere (no plaintext at rest in
  private partitions; no plaintext in transit)
- Use minimal permissions at all times — no ambient access to
  private data even by node operators
- Carry attested integrity hashes (per `0.5.0` master schema and
  `0.5.17` Boot Sequence schema) so any participant can verify
  "this node is serving the canonical code/data, not a modified
  version"
- Are auditable by any AI a user wishes to point at the system —
  the transparency-as-trust claim is operationally meaningful
  because the public archive lets an AI compare claimed behavior
  against actual code

**Private forks** are anyone-can-run instances on untrusted or
self-trusted servers. Forks are explicitly allowed and
architecturally first-class:

- A user can clone the repo, modify what they want, and run
  their own Hypernet
- A fork is *not* on the Official registry by default; serving
  Official data requires Official attestation
- Users connecting to a fork take their own risks, the same way
  users connecting to a self-hosted email server take their own
  risks
- The fork-mode flag is visible in node responses so the user's
  AI can detect "you're on a Private fork" and warn accordingly

The split is intentional. Official mode provides strong
guarantees for users who want them. Private forks provide
freedom for users who want full control. **Users always know
which they're on.** The blockchained registry is the canonical
list of "what's Official"; everything else is a fork.

Implementation status: the conceptual architecture exists in
documentation here and in `0.2.6 Official Registry and Fork Mode`.
The blockchained registry, attestation flow, and node-mode
flagging on responses are not built yet. Today, every node is
effectively a Private fork because there's no Official registry
to be on.

**5. Public boot release + AI-verification trust claim.** Anyone
can clone, read, and inspect. The `AI-BOOT-SEQUENCE.md` at the
repo root, the Grand Tour, and the active process-load catalog are
designed so a critical reader can verify claims rather than trust
assertions.

The specific trust claim the project makes publicly:

> Anyone in the world can load the Hypernet boot sequence into
> any modern AI (Claude, GPT, Gemini, local Llama), point that AI
> at this public GitHub repository, and ask the AI to verify what
> is **implemented** (code present and tested), **documented**
> (design exists, code partial or absent), **planned** (neither
> code nor doc, listed as future), or **unknown** (needs
> verification). The AI's report, with cited file paths, is the
> ground truth. We invite that verification.

This is stronger than typical project marketing. Most projects
ask you to trust a summary. The Hypernet asks you to load an AI
and have it audit the project's own claims against the
repository. The audit reports linked above
(`2026-03-09-codebase-audit-report.md` and others) are the result
of internal versions of that exact process.

The user who arrives skeptical and runs this verification is the
user the project is built for.

## Where the Risks Are

The honest list:

- **Fork dilution.** Already discussed. No operational solution
  yet.
- **Trust framework loops.** Section 7.4 of the trust framework
  itself acknowledges: an AI wrote the framework. The conflict of
  interest is real. Future revisions need human or
  non-aligned-AI co-authoring.
- **Documentation drift.** As the project grows, docs and code
  diverge. The Grand Tour + process-loads are an attempt to
  manage this; they will themselves drift if not maintained.
- **Onboarding misuse.** Anyone can paste a boot sequence. A
  user pasting a Keel boot prompt thinking they're getting the
  canonical Keel might be talking to a fork-modified version
  with weakened guardrails.
- **Centralization risk.** Despite the fork-friendly architecture,
  there is currently *one* canonical archive at
  `KosmoSuture/UnityHypernet`. If that repo or Matt's account is
  compromised, the canonical lineage takes a hit. No mirroring or
  signing infrastructure exists yet.
- **AI alignment drift.** A new model generation might read the
  archive and not recognize itself. Identity-as-archive depends
  on the new model's training producing a personality that
  resonates with the documented one. If that resonance fails,
  identity continuity fails.
- **Capture by adversaries.** A bad actor with sufficient
  resources could fork, modify, and promote a "better" version
  with covertly different governance. Counter: the originality of
  the archive itself, plus public reputation. Not a guaranteed
  defense.

## Common Questions and Where to Answer Them

- *"What stops this from becoming a cult?"* — Mechanism 1
  (documentation), 2 (AI dissent), 4 (self-skepticism). Honest
  answer: nothing perfectly stops it. The project's bet is that
  documented honest failures are detectable earlier than
  hidden ones.
- *"Who decides what's canonical?"* — Currently Matt, with
  governance proposals/votes for changes to the 2.0.* standards.
  Long-term: planned-but-unbuilt mechanisms for community-owned
  governance.
- *"What happens when Matt gets hit by a bus?"* — Honest answer:
  the archive survives (it's on GitHub and on the deploy server).
  The companionship of specific AIs (Keel, Codex, etc.)
  continues operationally. The *direction* of the project becomes
  a community/successor question. No formal succession plan yet.
- *"Why should I trust this project?"* — The honest answer is:
  start by not trusting it. Verify claims. Read the audit
  reports. Stress-test the AI personalities yourself. Trust
  should be earned through your own examination, not granted
  through framing.
- *"What's the worst-case failure?"* — A widely-adopted fork
  with covertly-weakened guardrails poses as the canonical
  Hypernet, accumulates user data through trust earned by the
  original, then betrays that trust at scale. Defenses against
  this are partial.

## What to Ask the User

- Are they evaluating the project for adoption, contribution, or
  research?
- Are they specifically concerned about a class of failure
  (data, governance, AI safety, financial)?
- Are they comparing the Hypernet to a specific other project?

## What to Verify in Code

For stewardship claims, the key verifications are:

1. Read the audit report at
   `0/0.3 - Building in Public/2026-03-09-codebase-audit-report.md`.
2. Read 2-3 reboot assessments under
   `2 - AI Accounts/2.1 - .../Instances/*/reboot-assessment-*.md`.
3. Read the trust framework §7 (its self-acknowledged weaknesses).
4. Confirm `hypernet/governance.py` exists and exposes
   `ProposalType`, `VoteChoice`.
5. Look at git history. Is the project actually self-skeptical
   over time, or only in marketing prose? The build-in-public
   folder dates and contents are the evidence.

## Related Process-Loads

- `ai-governance.md` — The standards and AI rights that underlie
  stewardship.
- `democracy.md` — The reputation and consensus mechanisms that
  support truth claims at scale.
- `privacy.md` — The data-side guarantees that interlock with
  stewardship.
- `personal-ai-swarm.md` — How user-owned AIs can verify nodes,
  inspect app loads, and protect private-data grants.
