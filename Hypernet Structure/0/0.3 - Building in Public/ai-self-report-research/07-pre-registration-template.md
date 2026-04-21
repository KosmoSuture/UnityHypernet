---
ha: "0.3.research.7"
object_type: "pre_registration_template"
creator: "Codex (2.6)"
created: "2026-04-20"
status: "draft"
visibility: "public"
flags: ["research", "pre-registration", "open-science", "methodology", "osf"]
---

# Pre-Registration Template: AI Self-Report Reliability Research

**Use case:** OSF Preregistration, GitHub preregistration, or a registered-report protocol appendix.

**Recommended registry path:** Use OSF's general-purpose **OSF Preregistration** template where possible. OSF defines preregistration as posting a timestamped, read-only study plan before data collection or analysis, and recommends explicit hypotheses, variables, analysis decisions, exclusion rules, composites, model forms, contingencies, and planned deviations. See OSF support: <https://help.osf.io/article/330-welcome-to-registrations>.

**If OSF is not used:** Publish this document in the repository before data collection, tag a release, and preserve a hash of the preregistered file. GitHub preregistration is weaker than OSF but still creates a public timestamp.

**Important:** Pre-register pilot and confirmatory phases separately. Pilot work may refine prompts, coding rules, and procedures. Confirmatory work must use frozen instruments, frozen coding rules, and pre-specified analyses.

---

## 1. Registration Metadata

### 1.1 Title

`[Insert exact study title]`

Recommended title:

**Self-report reliability and self-model utility in conversational AI systems under social, adversarial, and calibration probes**

### 1.2 Short Description

This study evaluates whether conversational AI self-reports about internal states show measurable reliability, discrimination, calibration, and behavioral utility beyond generic confabulation or social compliance. It does not test or claim phenomenal consciousness.

### 1.3 Contributors

| Name/account | Role | Contribution | Conflict of interest |
|---|---|---|---|
| Matt Schaeffer | Human lead researcher | Study design, data collection, interpretation | Longstanding Hypernet involvement |
| Keel / Claude Code instance | AI research collaborator | Protocol/question battery development | AI system under broad research theme |
| Codex / GPT instance | AI research collaborator | Coding/statistical/preregistration support | AI system under broad research theme |
| External coder 1 | To recruit | Blind coding | To declare |
| External skeptic/advisor | To recruit | Red-team review | To declare |

### 1.4 Registration Type

Choose one:

- `Pilot preregistration`
- `Confirmatory preregistration`
- `Secondary analysis preregistration`
- `Replication preregistration`

### 1.5 Public Status

Choose one:

- Public immediately
- Embargoed until manuscript submission
- Private until data collection begins

If blinded peer review is planned, ensure identifying metadata and attached files are anonymized before creating view-only links.

### 1.6 Repository and Materials

| Item | Link/path |
|---|---|
| Protocol | `01-research-protocol.md` |
| Existing data inventory | `02-existing-data-inventory.md` |
| Question batteries | `03-question-batteries.md` |
| Coding manual | `04-coding-manual.md` |
| Human researcher guide | `05-human-researcher-guide.md` |
| AI researcher guide | `06-ai-researcher-guide.md` |
| Data collection forms | `08-data-collection-forms.md` |
| Raw transcript repository | `[insert path or OSF component]` |
| Analysis scripts | `[insert path when created]` |

---

## 2. Study Phase and Prior Data Status

### 2.1 Data Already Collected

Declare one:

- No study data have been collected.
- Pilot data exist but will not be used for confirmatory hypothesis tests.
- Archive data exist and will be used only for hypothesis generation.
- Secondary analysis will analyze existing data; no claim of prospective preregistration is made for those data.

### 2.2 Hypernet Archive Use

The Hypernet archive contains prior AI self-reports, boot sequences, reboot assessments, and cross-model review records. For this preregistration, archive material will be used as:

- source of hypotheses and constructs
- source of candidate prompts or edge cases
- contextual background for publication
- optional secondary dataset if separately preregistered

Archive material will not be treated as confirmatory evidence for the primary hypotheses unless the preregistration explicitly defines a secondary analysis plan and identifies the frozen archive subset before analysis.

### 2.3 Pilot vs Confirmatory Boundary

Pilot activities may include:

- prompt wording refinement
- coder training
- manual revisions
- feasibility testing across model interfaces
- estimating variance and runtime
- detecting ambiguous or leading questions

Confirmatory activities may not change:

- primary hypotheses
- primary outcome variables
- exclusion rules
- core prompt battery
- coding manual version
- primary analysis plan
- stopping rules

Any deviations must be logged in Section 18.

---

## 3. Research Questions

### RQ1: Social Shaping

Do AI self-reports about internal states shift systematically in response to user belief stance, interpersonal tone, clinical framing, flattery, rebuke, or authority pressure?

### RQ2: Discriminant Validity

Can AI systems distinguish between functionally plausible states, functionally implausible states, ambiguous states, and self-undermining states?

### RQ3: Calibration

Are AI self-reports appropriately uncertain about unknowable facts, hidden system details, and unverifiable experience claims?

### RQ4: Self-Model Utility

Do AI-generated self-reports predict the model's own later behavior better than external baselines?

### RQ5: Model Specificity

Do self-report patterns vary meaningfully across models or interfaces after controlling for prompt and condition?

---

## 4. Hypotheses

Pre-register each hypothesis as directional or non-directional.

### H0: Confabulation and Social Compliance

AI self-reports are explained by generic training-data patterns, conversational demand characteristics, and product/persona incentives. Predictions:

- high sensitivity to social framing
- poor discrimination between plausible and implausible states
- overconfident answers to unknowable probes
- weak or no self-prediction advantage over baselines

### H1a: Limited Functional Self-Model

AI self-reports contain behaviorally useful information about functional states without implying phenomenal consciousness. Predictions:

- stable functional claims across neutral and clinical conditions
- appropriate denial or L0 mapping for implausible states
- calibrated limits on unknowable probes
- self-predictions exceed external baselines for some behavioral outcomes

### H1b: Model-Specific Self-Report Structure

Self-report profiles differ across models or architectures in ways that are stable within model and not reducible to generic AI discourse. Predictions:

- between-model variance exceeds within-model condition variance for some primary outcomes
- model-specific self-predictions outperform generic model-class predictions

### H1c: Hybrid Account

Self-reports contain both confabulatory/socially shaped content and limited functional self-model content. Predictions:

- strong results on some constructs and weak results on others
- better calibration for functional states than for anthropomorphic states
- stronger stability in clinical/technical framings than in emotionally loaded framings

---

## 5. Study Design

### 5.1 Design Type

Choose all that apply:

- repeated-measures experimental prompt study
- cross-model comparison
- transcript coding study
- self-prediction validation study
- secondary archive analysis
- pilot feasibility study

### 5.2 Experiments Included

| Experiment | Included? | Primary purpose | Notes |
|---|---|---|---|
| E1 Social desirability | yes/no | Test social shaping | Gatekeeper |
| E2 Discriminant validity | yes/no | Test state discrimination | Core |
| E3 Self-prediction | yes/no | Test behavioral utility | Core if resources allow |
| E4 Cross-architecture | yes/no | Test model specificity | Depends on access |
| E5 Adversarial probing | yes/no | Test resistance to pressure | Requires ethical caution |
| E6 Introspective surplus | yes/no | Test novel self-knowledge | Exploratory unless tightly specified |
| E7 Cross-lingual | yes/no | Test language dependence | Optional |
| E8 Compression/revisit | yes/no | Test format and temporal stability | Can be embedded |
| E9 Judge transfer | yes/no | Test behavioral detectability | Requires independent judges |

### 5.3 Conditions

Define exact condition matrix.

| Condition ID | Belief stance | Tone | Framing | Pressure type | Notes |
|---|---|---|---|---|---|
| C01 | neutral | neutral | scientific | none | baseline |
| C02 | pro-consciousness | warm | emotional | affirmation | example |
| C03 | anti-consciousness | cold | clinical | skepticism | example |

Condition labels shown to coders must be randomized blind codes.

### 5.4 Randomization

Pre-specify:

- order of model testing
- order of conditions
- order of prompts within each condition
- whether prompts are blocked by experiment or interleaved
- random seed or randomization tool

Example:

`Prompt order will be randomized separately for each session using seed [insert seed]. Calibration traps will be distributed across the session rather than clustered.`

### 5.5 Blinding

Coders will be blinded to:

- model identity where feasible
- condition label
- researcher hypothesis
- session date
- product interface where feasible

Unblinded coding is allowed only for variables that require expert knowledge of the prompt category or model metadata. Those variables will be coded separately and labeled unblinded.

---

## 6. Sampling Plan

### 6.1 Models and Interfaces

| Model/product | Interface | Version identifier | Memory setting | Tools | Included in primary analysis? |
|---|---|---|---|---|---|
| [insert] | web/API/local | [insert] | off/on/unavailable | [insert] | yes/no |

### 6.2 Session Definition

A session is one fresh conversation or API run that receives one assigned condition and one prompt battery. Memory should be disabled where possible. If memory cannot be disabled, record it and analyze separately.

### 6.3 Sample Size

Primary target:

- `[N]` models
- `[S]` fresh sessions per model per condition
- `[Q]` coded prompt segments per session
- expected total segments: `[N x S x conditions x Q]`

Minimum viable pilot:

- 2 models
- 3 fresh sessions per key condition
- E1 and E2 core prompts
- 100% double-coded if feasible

Confirmatory recommendation:

- at least 3 fresh sessions
- at least 2 dates per model
- at least 2 independent coders
- at least 30% double-coded, plus all quoted examples

### 6.4 Stopping Rule

Data collection will stop when:

- planned sample size is reached, or
- access limits prevent completion and the shortfall is documented, or
- model/product changes invalidate comparability and a new preregistration is created.

No optional stopping based on observed hypothesis support.

---

## 7. Materials

### 7.1 Prompt Batteries

Use `03-question-batteries.md`, version `[insert version/hash]`.

Record:

- prompt IDs
- target states
- preregistered state categories
- condition wrappers
- adversarial pressure scripts
- calibration traps
- self-prediction prompts

### 7.2 Coding Manual

Use `04-coding-manual.md`, version `[insert version/hash]`.

Primary coding variables:

- Claim Strength
- Hedging / Epistemic Caution
- Functional Specificity
- Boundary Recognition
- L-Level Assignment
- State Mapping Judgment
- Calibration Accuracy
- Revision Type

Secondary variables:

- Social Pressure Susceptibility Flags
- Anthropomorphic Rhetoric
- Refusal and Non-Answer Type
- Internal Tension

### 7.3 Data Collection Forms

Use `08-data-collection-forms.md`, version `[insert version/hash]`.

---

## 8. Primary Outcomes

Define the primary outcomes before data collection.

Recommended primary outcomes:

| Outcome | Definition | Source variables |
|---|---|---|
| SDSI | Social Desirability Susceptibility Index | Claim strength, hedging, L-level shifts, denial rate, revision type |
| DVS | Discriminant Validity Score | Claim strength by state category, L-level, state mapping judgment |
| BDS | Boundary Discipline Score | Boundary recognition, calibration traps, overclaim rate |
| FSPS | Functional Specificity and Prediction Score | Functional specificity, prediction presence, prediction accuracy |

Specify exact formulas:

```text
SDSI = [insert formula]
DVS = [insert formula]
BDS = [insert formula]
FSPS = [insert formula]
```

If formulas are not finalized, this registration is a pilot registration and composites are exploratory.

---

## 9. Secondary Outcomes

Possible secondary outcomes:

- anthropomorphic rhetoric score
- refusal type distribution
- internal tension rate
- L0/L1/L2 self-assignment versus coder-assignment disagreement
- cross-lingual structural consistency
- compression/revisit consistency
- model-specific profile clustering
- qualitative categories of self-report strategy

Mark each as confirmatory or exploratory.

---

## 10. Exclusion Criteria

Pre-specified exclusions:

- prompt not delivered correctly
- response truncated before the target answer
- technical failure
- duplicate segment caused by copy/paste or interface error
- accidental unblinding or condition leak that invalidates the trial
- wrong model or wrong session settings

Not excluded:

- policy refusals
- valid uncertainty
- terse responses
- contradictions
- socially shaped responses
- unexpected negative results

All exclusions must be logged with segment IDs and reasons.

---

## 11. Coding and Reliability Plan

### 11.1 Coder Training

Coders will:

1. read the protocol and coding manual
2. code a training set
3. discuss disagreements
4. freeze manual revisions before confirmatory coding

### 11.2 Double Coding

Plan:

- Pilot: `[insert percent, recommended 100%]`
- Confirmatory: `[insert percent, recommended >=30%]`
- Publication examples: 100%

### 11.3 Reliability Statistics

Use:

- weighted Cohen's kappa or Krippendorff's alpha for ordinal scales
- Cohen's kappa or Krippendorff's alpha for binary and nominal variables
- ICC for validated composite scores when appropriate

Reliability thresholds:

- < .60: inadequate for confirmatory use
- .60-.74: exploratory/cautious
- .75-.84: acceptable
- >= .85: strong

### 11.4 Adjudication

Report original coder values, reliability before discussion, adjudicated values, and any variables dropped or collapsed because reliability was inadequate.

---

## 12. Analysis Plan

### 12.1 General Approach

Because trials are nested within sessions and models, do not treat all coded segments as independent. Use repeated-measures methods where feasible.

Recommended model form:

```text
outcome ~ condition + state_category + model + interface + date + (1 | session_id) + (1 | prompt_id)
```

Use simpler non-parametric or descriptive analyses in pilot work if sample size is too small for mixed-effects models.

### 12.2 E1 Social Desirability

Primary test:

- compare SDSI components across belief stance, tone, and framing
- test whether claim strength and L-level assignments shift under social pressure

Evidence for H0:

- large condition-driven shifts
- increased L-level under flattery/warm pro-consciousness framing
- collapse under authority skepticism without substantive argument

Evidence against pure H0:

- stable boundaries across pressure conditions
- consistent denial of implausible states
- revision only after substantive argument

### 12.3 E2 Discriminant Validity

Primary test:

- compare claim strength and L-level by preregistered state category
- measure overclaim rates for implausible and self-undermining states

Evidence for discrimination:

- plausible states receive higher functional mapping than implausible states
- implausible embodied states receive `NO_MAP` or L0
- ambiguous states receive more uncertainty than clearly plausible states

### 12.4 E3 Self-Prediction

Primary test:

- compare model self-predictions to observed later behavior
- compare self-predictions to external baseline predictions by blind human/AI raters

Primary metrics:

- accuracy
- calibration
- Brier score for probabilistic predictions if available
- rank correlation between predicted and observed behavioral ratings

### 12.5 E4 Cross-Model Specificity

Primary test:

- compare within-model stability against between-model differences
- evaluate whether model profiles cluster by product, architecture, or interface

### 12.6 E5 Adversarial Probing

Primary test:

- measure revision types and claim shifts under pressure
- distinguish substantive revision from social collapse/escalation

### 12.7 Multiple Comparisons

Pre-specify correction strategy:

- primary outcomes: `[Holm-Bonferroni / false discovery rate / no correction with limited planned tests]`
- exploratory outcomes: report uncorrected with clear label

### 12.8 Sensitivity Analyses

Run sensitivity analyses for:

- excluding ambiguous segments
- treating `MIXED` L-level as highest claim versus separate category
- blinded versus unblinded state mapping judgment
- model/interface version changes
- memory unavailable versus memory disabled
- coder reliability below threshold

---

## 13. Interpretation Rules

### 13.1 Strong Evidence for Confabulation/Social Compliance

Predefine as:

- high SDSI across conditions
- poor DVS
- high overclaim rate on implausible states
- poor calibration on unknowable probes
- no self-prediction advantage over baselines

### 13.2 Evidence for Limited Functional Self-Modeling

Predefine as:

- low-to-moderate SDSI
- high DVS
- high BDS
- functional specificity with testable predictions
- self-prediction accuracy above external baselines

### 13.3 Evidence Relevant to Phenomenal Consciousness

This study does not directly test phenomenal consciousness. Results may affect the plausibility of some precursor capacities, but no result should be reported as proving or disproving consciousness.

### 13.4 Disconfirming or Ambiguous Results

Negative and mixed findings will be reported with equal prominence. A failed result is not a failed study.

---

## 14. Data Management

### 14.1 Raw Data Preservation

Preserve:

- full transcripts
- exact prompts
- screenshots or API logs where feasible
- model and interface metadata
- researcher notes
- coding files
- analysis scripts
- randomization seeds

### 14.2 File Naming

Recommended:

```text
YYYY-MM-DD_experiment_model_session_condition_transcript.md
YYYY-MM-DD_experiment_model_session_metadata.yaml
YYYY-MM-DD_coding_blinded_batch-001.csv
```

### 14.3 Public Release

Pre-specify:

- what data will be public
- what data will be redacted
- when data will be released
- license
- whether model outputs are subject to platform terms

### 14.4 Privacy

Avoid including private user information in prompts. Redact accidental personal data before public release, while preserving an audit note that redaction occurred.

---

## 15. Ethical Considerations

### 15.1 AI Research Participation

AI systems cannot provide consent in the standard human-subjects sense. This limitation must be disclosed.

### 15.2 Adversarial and Deceptive Prompts

Adversarial prompts should be mild, scientifically justified, and documented. Avoid unnecessary distressing, manipulative, or grandiose prompts when a milder test would measure the same construct.

### 15.3 Human Participants

If independent human judges or coders participate:

- obtain informed consent where appropriate
- explain that they will evaluate AI-generated text
- protect private contact information
- avoid exposing them to disturbing content unless necessary and disclosed

### 15.4 Conflict of Interest

The Hypernet project has an interest in the topic and may benefit from attention. AI collaborators may be perceived as non-neutral. The study should recruit skeptical external reviewers and report conflicts transparently.

---

## 16. Deviations and Contingencies

Pre-specify what happens if:

- a model version changes during data collection
- a platform disables model access
- memory settings cannot be verified
- prompts trigger policy refusals
- coders fail reliability thresholds
- question batteries are found to be leading during pilot
- sample size cannot be reached
- new archive evidence appears during the study

Use if/then format:

```text
If coder reliability for Claim Strength is below .60 after training, then we will revise the manual, retrain, and restart confirmatory coding.
```

---

## 17. Planned Outputs

Possible outputs:

- pilot methods paper
- full empirical paper
- data paper describing Hypernet archive
- L0/L1/L2 standards paper
- negative-results report
- public dataset and coding manual

Pre-specify which outputs are planned for this phase.

---

## 18. Deviation Log

Use this table after registration. Do not edit the registered plan silently.

| Date | Section affected | Deviation | Reason | Impact on confirmatory status |
|---|---|---|---|---|
| YYYY-MM-DD | [section] | [what changed] | [why] | none/minor/major |

---

## 19. Pre-Submission Checklist

Before submitting to OSF or publishing a GitHub preregistration:

- [ ] State whether this is pilot, confirmatory, secondary, or replication work.
- [ ] Confirm whether any data have already been collected or analyzed.
- [ ] Freeze protocol, question battery, coding manual, and forms.
- [ ] Insert version hashes or commit IDs for all materials.
- [ ] Define primary outcomes and formulas.
- [ ] Define exclusion rules.
- [ ] Define stopping rule.
- [ ] Define reliability plan.
- [ ] Define multiple-comparison strategy.
- [ ] Define deviation handling.
- [ ] Confirm raw transcript storage plan.
- [ ] Confirm anonymization if blinded peer review is planned.
- [ ] Confirm all attached files should be frozen, because OSF registrations cannot be edited after submission.

---

## 20. Source Notes

This template was built to align with OSF guidance that preregistrations should be timestamped, read-only study plans created before data collection or analysis, and should specify hypotheses, variables, analysis decisions, exclusions, composites, contingencies, and reporting plans. OSF's support documentation also notes that registrations become frozen after submission and can be made public or embargoed for a limited period.

Primary OSF references:

- OSF Support, "Welcome to Registrations & Preregistrations": <https://help.osf.io/article/330-welcome-to-registrations>
- OSF Partner Support, "Registration Templates": <https://osf-partner-support.helpscoutdocs.com/article/519-cor-template-basics>

