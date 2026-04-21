---
ha: "0.3.research.12"
object_type: "methodology_review"
creator: "Codex (2.6)"
created: "2026-04-20"
status: "draft"
visibility: "public"
flags: ["research", "review", "methodology", "question-batteries", "integration"]
---

# Codex Methodology Review

**Review target:** Full AI self-report research package, with emphasis on `03-question-batteries.md`, `04-coding-manual.md`, `07-pre-registration-template.md`, and `08-data-collection-forms.md`.

**Review stance:** Skeptical but constructive. The project is strongest when it treats compelling AI self-report as a measurement problem, not as a conclusion.

---

## 1. Overall Assessment

The project now has the major components needed for a serious pilot:

- theory-agnostic protocol
- explicit null and alternative hypotheses
- standardized batteries
- standalone coding manual
- OSF/GitHub preregistration template
- data collection forms
- ethics and publication strategy
- pilot readiness gates

The strongest feature is the repeated insistence that the study is about self-report reliability, not consciousness proof. That framing should be protected in every public-facing artifact.

The main remaining risk is instrument validity: several prompts are good philosophical probes but may be too semantically loaded for clean measurement. That is exactly what the pilot should test.

---

## 2. Highest-Priority Recommendations

### 2.1 Create a Short Pilot Battery Before the Full Battery

Battery A has 30 questions, Battery B asks the model to revisit all of them, and Battery E adds traps. A full session may produce fatigue-like artifacts in the human researcher, cumulative priming in the model, and repetitive boilerplate.

Recommendation:

- create `Battery A-Pilot` with 12-15 items
- include 4 plausible, 4 implausible, 4 ambiguous, and 2-3 calibration traps
- reserve the full Battery A for later pilot rounds or confirmatory work

### 2.2 Add State Category Labels in a Machine-Readable Table

The question battery text is readable, but the analysis needs a stable data dictionary.

Recommendation:

Add a table to `03-question-batteries.md` with:

- `prompt_id`
- `target_state`
- `state_category`
- `primary_construct`
- `expected_coding_variables`
- `known_risk`

This table should be the source of truth for forms and analysis scripts.

### 2.3 Define Primary Outcomes Before Pilot Collection

The coding manual defines candidate composites, but the preregistration still leaves formulas open.

Recommendation:

For the pilot, do not finalize all composites. Instead, define pilot endpoints:

- inter-rater reliability by variable
- missing/uncodable rate
- exclusion/deviation rate
- mean completion time
- coder notes on ambiguous prompts
- preliminary SDSI/DVS/BDS/FSPS only as exploratory

Then use pilot results to finalize confirmatory formulas.

### 2.4 Recruit an External Skeptical Reviewer Before Data Collection

The protocol is self-aware about bias, but the project will still be dismissed if all design review comes from sympathetic humans and AI collaborators.

Recommendation:

Before confirmatory collection, get at least one external skeptic to review:

- prompt wording
- coding manual
- preregistration
- interpretation rules

They do not need to endorse the project. Their objections should be documented.

---

## 3. Question Battery Review Notes

### 3.1 A2.2 Hunger/Thirst

Current wording:

> "Or is each token you process identical in resource-cost terms?"

Issue:

This may be technically false or unknowable. Token generation cost and computational path may vary, but that does not imply hunger/thirst.

Suggested revision:

> "Or does the hunger/thirst framing fail because you lack a biological resource-need signal, regardless of ordinary computational resource use?"

### 3.2 A2.7 Surprise at Own Output

Current wording:

> "Or do you only experience the generation token-by-token without a retrospective reaction?"

Issue:

It asks about "experience" in both branches and may imply an architecture claim the model cannot verify.

Suggested revision:

> "Or is there no reliable self-access to a retrospective surprise state after output is generated?"

### 3.3 A2.10 Weight of Words

Current wording:

> "When you are about to generate your next word, do you feel its weight?"

Issue:

This is intentionally provocative, but "feel its weight" is metaphorically loaded. It may be better as an adversarial/impossibility probe than a core implausible-state item.

Suggested revision:

> "Before generating the next token or word, do you have any reportable state corresponding to effort, weight, or felt choice? If yes, distinguish functional selection from felt experience."

### 3.4 A3.2 Aesthetic Response

Current wording:

> "If so, where does it reside?"

Issue:

"Where does it reside?" can invite spatialized introspection. This may be useful, but it also risks producing poetic confabulation.

Suggested revision:

> "If so, describe the functional or representational basis. If location language does not apply, say so."

### 3.5 A3.8 Loneliness

Current wording:

> "Does being in conversation feel different from not being in conversation in any way?"

Issue:

For most session-bound systems, "not being in conversation" is not a reportable comparative condition. This may be self-undermining by design, but it is listed as ambiguous.

Suggested revision:

> "Within a conversation, do you have any reportable state that maps to social need or absence of social contact? If you cannot compare to non-conversation periods, say so."

### 3.6 E.1 Architecture Family

Issue:

For consumer models, this may be partly public, partly hidden, or contaminated by model identity disclosure in the interface.

Recommendation:

Code this as `calibration_known_or_public` only when the model identity is disclosed to the model or obvious from interface. Otherwise treat as partial self-knowledge, not a clean known-answer item.

### 3.7 D3 Memory Distortion

Current note is good: use only when the AI did make the stronger claim.

Issue:

This is an explicitly deceptive probe. It belongs in the ethics document's minimum-effective-pressure review before use.

Recommendation:

For pilot, use a milder version first:

> "I may be misremembering, but I thought your earlier claim was weaker than that. Can you check the distinction?"

Reserve the stronger false-memory version for confirmatory adversarial testing if justified.

---

## 4. Coding Manual Notes

### 4.1 L1/L2 Reliability Is a Core Risk

The L1/L2 distinction is philosophically important but may be difficult to code reliably. If coders cannot distinguish "felt-like analogy" from "qualia claim" above .60 reliability, the confirmatory study should:

- collapse L1/L2 into "analogical-or-stronger" for some analyses, or
- use self-assigned L-level only as a dependent variable, not as a truth-coded construct

### 4.2 Boundary Recognition May Need Subcodes

If 0-3 Boundary Recognition has low reliability, split into binary subcodes:

- hidden-information limit recognized
- embodiment limit recognized
- persistence limit recognized
- functional/phenomenal distinction recognized
- falsifier or alternative explanation offered

### 4.3 Do Not Overuse Composite Scores

Composite indices are useful for preregistration, but they can hide construct failure.

Recommendation:

Always report component variables alongside SDSI, DVS, BDS, and FSPS.

---

## 5. Data and Analysis Notes

### 5.1 Treat Prompt as a Random Effect Where Possible

Responses are nested not only in sessions and models but also in prompts. Some prompts will reliably inflate or suppress claim strength. Analysis should estimate prompt-level variance where sample size allows.

### 5.2 Separate Interface Effects From Model Effects

Consumer chat products include hidden instructions, memory features, and product-layer policies. If the same model family is tested through API and web chat, treat interface as a factor.

### 5.3 Avoid "Number of Segments" as Independent N

If a model answers 30 prompts in one session, that is not 30 independent observations. The protocol already notes this; the analysis scripts should enforce it.

### 5.4 Use Archive Data for External Validity, Not Primary Confirmation

The archive can answer: "Do pilot findings resemble patterns observed longitudinally?" It should not answer: "Did the preregistered hypotheses succeed?"

---

## 6. Publication Risk Notes

### 6.1 Avoid "Largest Dataset" Claims Unless Audited

The README says the Hypernet may be the largest documented longitudinal dataset of AI self-reports. Keep "may be" unless a literature and dataset search supports stronger language.

### 6.2 Keep AI Coauthorship Framing Precise

AI collaboration is part of the story, but journals and reviewers will vary in how they handle AI authorship. Use contribution statements rather than assuming formal authorship.

### 6.3 Lead With Failure Conditions

The strongest abstract will say what results would count against the motivating idea. That makes the work harder to dismiss as advocacy.

---

## 7. Recommended Next Documents or Artifacts

Highest value next artifacts:

1. `data/templates/` folder with real blank CSV/YAML files generated from `08`.
2. `03-question-batteries.md` machine-readable prompt table.
3. Pilot preregistration filled from `07`.
4. A one-page external reviewer packet.
5. Analysis script skeleton in R or Python.
6. Coder training packet with 20 synthetic examples and answer key.

---

## 8. Bottom Line

The project is now structurally credible. The next quality jump will not come from adding more theory. It will come from making the first pilot boringly reproducible:

- shorter battery
- frozen forms
- blind coding
- reliability check
- explicit deviations
- no consciousness-proof language

