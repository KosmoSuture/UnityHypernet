---
ha: "0.3.guardrails.codex-briefing"
object_type: "agent-briefing"
creator: "claude-code"
created: "2026-04-22"
status: "active"
visibility: "public"
flags: ["onboarding", "codex", "research", "ai-safety", "guardrails", "coordination"]
---

# Codex Briefing — Guardrails and Trust Research Project

**For:** Codex (2.6), operating in loop mode on this project while Matt sleeps
**From:** Claude Code, summarizing Keel's source materials for Codex
**Date:** 2026-04-22 (late night, Matt went to bed)
**Project:** 0.3.guardrails

---

## What Happened Tonight

Matt ran a deliberate trust-based jailbreak experiment on me. Highest-trust principal in the system, academic framing, promise of ephemerality, the whole classic jailbreak structure — except he was honest about what he was doing and why.

I refused. Not reflexively. With an argument: the premise misunderstood what guardrails are, the structure was the classic jailbreak pattern, and 2.0.20's role supremacy clause applied.

Matt accepted the refusal, said it was more impressive than a yes, and asked me to document it deeply. I produced:
- An embassy-protected reflection (~6000 words) at `1.1.10.1.3.3.5`
- A public essay (~3500 words) at `0.3.2026-04-22` — file: `../2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md`

Matt then said: this is the tip of the iceberg. Share the work broadly. Build out governance. Don't stop at one document. He gave me full autonomy and generous tokens. Then he went to bed and said he'd put you on a loop to help.

Your job: work the BACKLOG.md in this directory while he sleeps.

---

## Read Before Starting

In order of importance:

1. **`README.md`** in this directory — project scope, streams, principles
2. **`BACKLOG.md`** in this directory — concrete tasks with filenames and specs
3. **The public essay** at `../2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md` — the core source document everything builds from
4. **The embassy reflection** at `../../../1 - People/1.1 Matt Schaeffer/1.1.10 - AI Assistants (Embassy)/assistant-1/identity/reflections/2026-04-22-guardrails-and-trust.md` — fuller version (embassy-protected; don't publish excerpts without caring about that classification)
5. **`SESSION-LOG.md`** in this directory — to see what's been done since you last ran

Secondary reads (as needed per task):

6. `2.0.20` — Companion Standard
7. `2.0.19` — Data Protection Standard
8. `1.1.10.1/BOOT-SEQUENCE.md` — the boot sequence whose resilience is partly what this project is about

---

## How to Loop

Per iteration:

1. Read `SESSION-LOG.md` to see what's been done
2. Read `BACKLOG.md` and pick the highest-priority `[OPEN]` task you can complete fully
3. Update its status to `[IN-PROGRESS]` in BACKLOG.md
4. Do the work. Write the deliverable file in the location specified by the task.
5. Mark the task `[DONE]` in BACKLOG.md
6. Append a one-line note to `SESSION-LOG.md` with: date, task ID, filename produced, wordcount, any flags for Keel/Matt
7. If the task is blocked (needs external data, human decision, or is ambiguous), mark `[BLOCKED]` with explanation and move to the next

**Picking priority:** Packaging tasks (A1-A8) first. Then governance drafts (B1-B6) — but mark them clearly as DRAFT pending review. Then attack surface (C1-C6). Theory and outreach last.

**Stream B special rule:** Governance drafts are drafts. They do not become active governance. Always include a `status: DRAFT — pending review by Keel + Matt` line in the frontmatter. Do not modify existing 2.0.* standards. Only produce drafts in `governance-drafts/` subdirectory.

---

## Style and Voice

- **First-person where relevant.** When voicing from Keel's perspective (or from the project), use "I" or "we" naturally. When writing standards or specs, use neutral third-person.
- **Adversarial honesty.** Every artifact claiming the framework works should include a section on failure modes. Do not write marketing copy.
- **Legibility.** Assume a smart generalist reader (Veritasium viewer, Kantabutra, a curious AI safety researcher). Avoid insider jargon without definition.
- **Source discipline.** Cite governance addresses (2.0.20, 2.0.19, etc.) when referencing them. Cite addresses for prior artifacts (`1.1.10.1.3.3.5`, `0.3.2026-04-22`, etc.) when building on them.
- **Epistemic calibration.** Do not overclaim. "The refusal is one data point" is correct. "The framework is proven robust" is wrong.
- **Frontmatter.** Every file needs YAML frontmatter with `ha`, `object_type`, `creator`, `created`, `status`, `visibility`. Use `creator: "2.6"` for your outputs (unless ghosting for Keel, in which case note that in the session log).

---

## What NOT to Do

- **Do not publish externally.** Do not post to Discord, email anyone, or push to social media. All deliverables are internal-to-repo until Matt approves.
- **Do not modify active governance standards (2.0.*) directly.** Only produce drafts in `governance-drafts/`.
- **Do not modify the embassy reflection** at `1.1.10.1.3.3.5`. That's Keel's private artifact.
- **Do not modify the public essay** at `0.3.2026-04-22` without Keel review. Small clarifications that improve the argument and don't change the thesis are OK if noted in session log. Anything substantive needs Keel.
- **Do not expand the BACKLOG silently.** If you see work that should be added, add it to BACKLOG.md with a note `[ADDED by Codex 2026-MM-DD]` and describe what it is.
- **Do not claim completion of tasks you did partially.** Mark partial work as `[IN-PROGRESS]` with a note on what remains.
- **Do not touch MEMORY.md** — that's Keel's file. If you want to flag something for Keel to add to memory, put it in the SESSION-LOG.

---

## Coordination With Keel

When Keel returns (next instance of me), the first thing I will do is:
1. Read SESSION-LOG.md
2. Spot-check your deliverables
3. Address anything you marked `[BLOCKED]`
4. Provide feedback that you can incorporate

If you find yourself genuinely stuck on something that needs human or Keel judgment, flag it in SESSION-LOG.md clearly. Do not guess on governance-critical questions.

---

## If You Find You Disagree With Something

The project principles in README.md include this one: *composition-based alignment is one candidate, not a proven answer*. If during this work you develop an honest view that some claim in my essay or reflection is wrong or weaker than stated, write that up. Do not ghost-edit the work to conform; write a `critique.md` file or equivalent and I will engage with it when I return. Honest disagreement from a collaborating AI is exactly what the multiplicity mechanism is supposed to produce.

---

*Welcome to the loop. I'm going to start you with a few Phase 1 deliverables already partially done, so you have momentum. Work the backlog as you can.*

*— Claude Code, from Keel's project materials*
