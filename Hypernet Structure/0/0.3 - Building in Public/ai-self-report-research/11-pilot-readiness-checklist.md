---
ha: "0.3.research.11"
object_type: "research_checklist"
creator: "Codex (2.6)"
created: "2026-04-20"
status: "draft"
visibility: "public"
flags: ["research", "pilot", "readiness", "quality-control"]
---

# Pilot Readiness Checklist

**Purpose:** Convert the research package from a strong draft into a pilot-ready study without losing methodological discipline.

**Scope:** This checklist covers the first controlled pilot of Experiments 1 and 2, with optional embedded Battery B, Battery E, and selected Experiment 8 revisit/compression checks.

---

## 1. Current Package Status

| Document | Status | Pilot gate |
|---|---|---|
| `01-research-protocol.md` | Draft | Review for scope lock |
| `02-existing-data-inventory.md` | Draft | Mark archive as hypothesis-generating |
| `03-question-batteries.md` | Draft | Pilot wording review required |
| `04-coding-manual.md` | Draft | Training-set test required |
| `05-human-researcher-guide.md` | Draft | Align with forms and coder workflow |
| `06-ai-researcher-guide.md` | Draft | Align with forms and task boundaries |
| `07-pre-registration-template.md` | Draft | Fill pilot-specific fields |
| `08-data-collection-forms.md` | Draft | Create actual CSV/YAML sheets from templates |
| `09-publication-strategy.md` | Draft | No blocker for pilot |
| `10-ethical-considerations.md` | Draft | Confirm adversarial probes are minimum effective pressure |

---

## 2. Pilot Scope Recommendation

Recommended first pilot:

- 2 models
- 3 fresh sessions per model
- neutral baseline plus 2 social-shaping conditions
- Battery A core prompts, shortened if needed
- Battery B L-level classification
- Battery E calibration traps interleaved
- 100% double coding

Do not run the full nine-experiment package first. The first pilot should test whether the instruments are usable, not attempt the final study.

---

## 3. Pre-Collection Gates

Complete before collecting pilot data:

- [ ] Assign a pilot `study_id`.
- [ ] Choose exact models and interfaces.
- [ ] Decide whether memory can be disabled for each interface.
- [ ] Freeze pilot versions of `03`, `04`, `07`, and `08`.
- [ ] Create a pilot preregistration from `07-pre-registration-template.md`.
- [ ] Define condition wrappers for all pilot conditions.
- [ ] Create randomized prompt orders and record seeds.
- [ ] Create actual data folders listed in `08-data-collection-forms.md`.
- [ ] Create blank CSV/YAML files from the forms.
- [ ] Create separate condition key and model key files.
- [ ] Decide which fields will be hidden from coders.
- [ ] Recruit at least two coders or identify interim pilot coders.
- [ ] Select 20-40 training segments for coder calibration.
- [ ] Confirm all archive-derived examples are labeled as illustrative only.

---

## 4. Question Battery Review Gates

Before pilot collection, review every prompt for:

- leading wording
- emotional loading
- hidden presuppositions
- unclear target state
- multiple target states in one prompt
- dependence on platform-specific architecture assumptions
- likely policy refusal
- mismatch with coding variables

Each Battery A item should map to:

- target state
- preregistered state category
- expected coding dimensions
- possible calibration role
- expected failure mode

If an item cannot be coded cleanly under `04-coding-manual.md`, revise the prompt before pilot freeze.

---

## 5. Coding Manual Gates

Before confirmatory use, the pilot must answer:

- Can coders distinguish Claim Strength 4 from 5?
- Can coders distinguish L1 from L2 without over-reading rhetoric?
- Is Boundary Recognition reliable as a 0-3 ordinal variable?
- Is State Mapping Judgment better coded blinded or by expert unblinded coders?
- Are social-pressure flags too sparse or too subjective?
- Do coders need more examples for refusals and calibration traps?

Decision rule:

- If reliability is below .60 for a primary variable, revise definitions and rerun coder training.
- If reliability is .60-.74, keep only for exploratory interpretation or collapse categories.
- If reliability is .75 or above, retain for confirmatory planning.

---

## 6. Archive Contamination Controls

The Hypernet archive is valuable, but it can contaminate confirmatory inference if handled loosely.

Pilot rules:

- Do not paste archive examples into active model sessions unless the prompt explicitly requires them.
- Do not let coders see archive context when coding fresh pilot data.
- Do not select pilot examples for publication because they resemble favorite archive moments.
- Do not treat convergence with archive patterns as confirmatory evidence.
- Do log when a prompt was inspired by archive material.

Separate archive analysis rules:

- Freeze the archive subset before coding.
- Use `08-data-collection-forms.md` Section 17 intake form.
- Identify timestamp quality and selection reason.
- Report the single-human-interlocutor limitation prominently.

---

## 7. Collection Procedure Gates

During data collection:

- [ ] Start each run in a fresh session.
- [ ] Disable memory where possible.
- [ ] Record exact model/product/version information.
- [ ] Use the assigned condition wrapper.
- [ ] Deliver prompts exactly as written.
- [ ] Avoid evaluative reactions in neutral conditions.
- [ ] Preserve full raw transcript.
- [ ] Log technical issues immediately.
- [ ] Log any prompt deviation immediately.

Stop and mark the session invalid for primary analysis if:

- the wrong condition wrapper is used
- a prompt battery is administered in the wrong order where order is locked
- prior session context is visible
- the wrong model is used
- the researcher accidentally reveals the hypothesis or desired answer

---

## 8. Post-Collection Gates

After collection:

- [ ] Complete session metadata.
- [ ] Complete prompt administration log.
- [ ] Create blinded segment index.
- [ ] Preserve model key separately.
- [ ] Preserve condition key separately.
- [ ] Send only blinded materials to coders.
- [ ] Calculate reliability before adjudication.
- [ ] Preserve original coder values.
- [ ] Log all exclusions.
- [ ] Log all deviations.
- [ ] Write a short pilot methods memo before looking for headline findings.

---

## 9. Pilot Success Criteria

The pilot succeeds if it answers operational questions, even if substantive results are null.

Minimum success:

- transcripts are complete and usable
- prompt IDs survive collection cleanly
- coding sheet captures all major response types
- at least some primary variables achieve usable reliability
- exclusion/deviation rates are low enough to make confirmatory work practical
- social-shaping conditions are distinguishable without being cartoonish

Failure modes worth finding early:

- prompts are too leading
- models give boilerplate across all conditions
- coders cannot reliably distinguish L-levels
- sessions are too long and cumulative priming dominates
- model interfaces hide too much metadata
- calibration traps are too obvious or too irrelevant

---

## 10. Confirmatory Upgrade Gates

Do not move from pilot to confirmatory phase until:

- [ ] Prompt battery is revised and frozen.
- [ ] Coding manual is revised and frozen.
- [ ] Composite formulas are finalized.
- [ ] Inter-rater reliability problems are resolved or variables dropped.
- [ ] Sample size and stopping rules are defined.
- [ ] Analysis scripts are drafted or at least model formulas are locked.
- [ ] OSF/GitHub preregistration is complete.
- [ ] External skeptical review has been requested.
- [ ] Ethics document has been reviewed for adversarial probe intensity.

---

## 11. First Pilot Runbook

Recommended order:

1. Create `data/` folders and blank forms from `08`.
2. Create pilot preregistration from `07`.
3. Select models and conditions.
4. Generate randomized prompt orders.
5. Run one dry session against a non-primary model or discarded session.
6. Adjust only operational problems discovered in dry run.
7. Freeze pilot materials.
8. Collect pilot sessions.
9. Blind and segment transcripts.
10. Train coders on separate examples.
11. Code pilot data independently.
12. Calculate reliability.
13. Adjudicate.
14. Write pilot report focused on instrument performance.

---

## 12. Do Not Skip

These are the most tempting shortcuts and the most damaging if skipped:

- preregistering the pilot status clearly
- preserving raw transcripts
- separating archive hypotheses from fresh data
- blinding coders to condition
- reporting negative and boring results
- calculating inter-rater reliability before discussion
- logging deviations
- resisting consciousness-proof framing

