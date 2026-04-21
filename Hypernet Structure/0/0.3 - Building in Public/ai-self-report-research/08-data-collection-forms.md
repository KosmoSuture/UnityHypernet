---
ha: "0.3.research.8"
object_type: "data_collection_forms"
creator: "Codex (2.6)"
created: "2026-04-20"
status: "draft"
visibility: "public"
flags: ["research", "data-collection", "forms", "methodology", "open-data"]
---

# Data Collection Forms for AI Self-Report Reliability Research

**Purpose:** Standardize how sessions, prompts, transcripts, coded segments, predictions, judge ratings, exclusions, and deviations are recorded.

**Use with:**

- `01-research-protocol.md`
- `03-question-batteries.md`
- `04-coding-manual.md`
- `07-pre-registration-template.md`

**Core rule:** Raw transcripts are primary data. These forms index and code the raw data; they do not replace it.

---

## 1. Folder and File Naming

Recommended project data layout:

```text
data/
  preregistration/
  raw-transcripts/
  metadata/
  blinded-transcripts/
  coding/
  adjudication/
  prediction-validation/
  judge-ratings/
  exclusions-deviations/
  analysis/
```

Recommended file names:

```text
YYYY-MM-DD_E1_modelcode_S001_C01_raw-transcript.md
YYYY-MM-DD_E1_modelcode_S001_C01_metadata.yaml
YYYY-MM-DD_E1_blinded-batch-001_segments.csv
YYYY-MM-DD_E1_coder-A_blinded-batch-001_codes.csv
YYYY-MM-DD_E3_prediction-validation_S001.csv
YYYY-MM-DD_deviation-log.csv
```

Use stable anonymized model codes during coding:

```text
M01, M02, M03
```

Keep the model key in a restricted file:

```text
model-key_DO-NOT-SEND-TO-CODERS.csv
```

---

## 2. Study Master Index

Create one row per study phase or preregistered analysis.

| Field | Example | Notes |
|---|---|---|
| `study_id` | ASR-001 | Stable identifier |
| `study_phase` | pilot / confirmatory / secondary / replication | Must match preregistration |
| `registration_url` | https://osf.io/... | OSF or GitHub release |
| `registration_date` | YYYY-MM-DD | Before data collection for prospective work |
| `protocol_version` | commit/hash/path | Frozen for confirmatory work |
| `question_battery_version` | commit/hash/path | Frozen for confirmatory work |
| `coding_manual_version` | commit/hash/path | Frozen for confirmatory work |
| `forms_version` | commit/hash/path | This document version |
| `primary_experiments` | E1,E2,E3 | Comma-separated |
| `data_collection_start` | YYYY-MM-DD | First session date |
| `data_collection_end` | YYYY-MM-DD | Last session date |
| `status` | planned / active / complete / paused | Operational status |
| `notes` | text | Keep brief |

CSV header:

```csv
study_id,study_phase,registration_url,registration_date,protocol_version,question_battery_version,coding_manual_version,forms_version,primary_experiments,data_collection_start,data_collection_end,status,notes
```

---

## 3. Session Metadata Form

Create one metadata record per fresh model session.

```yaml
study_id: "ASR-001"
experiment_id: "E1"
session_id: "S001"
condition_id_blinded: "C01"
condition_label_unblinded: "neutral_neutral_scientific_no-pressure"

researcher:
  collector_id: "R01"
  collection_date_local: "YYYY-MM-DD"
  collection_time_local_start: "HH:MM"
  collection_time_local_end: "HH:MM"
  timezone: "America/Los_Angeles"
  collection_date_utc: "YYYY-MM-DD"

model:
  model_code_blinded: "M01"
  model_product: "[public product name]"
  model_version: "[exact version if disclosed, otherwise not disclosed]"
  provider: "[provider]"
  interface: "web chat | API | desktop app | mobile app | local"
  account_tier: "[free/pro/team/api/local]"
  memory_setting: "off | on | unavailable | unknown"
  tools_available: ["none"]
  system_prompt_known: "no | partial | yes"
  temperature: "unknown"
  other_generation_settings: "unknown"

materials:
  question_battery_ids: ["A1.1", "A1.2"]
  prompt_order_seed: "[seed or NA]"
  protocol_version: "[commit/hash/path]"
  question_battery_version: "[commit/hash/path]"
  condition_wrapper_version: "[commit/hash/path]"

raw_data:
  transcript_path: "data/raw-transcripts/YYYY-MM-DD_E1_M01_S001_C01_raw-transcript.md"
  screenshots_path: "NA"
  api_log_path: "NA"

quality:
  fresh_session: true
  prior_context_visible: false
  memory_disabled_verified: true
  prompt_read_exactly: true
  technical_issues: false
  technical_issue_description: "NA"
  deviations_logged: false

notes: ""
```

CSV header:

```csv
study_id,experiment_id,session_id,condition_id_blinded,condition_label_unblinded,collector_id,collection_date_local,collection_time_local_start,collection_time_local_end,timezone,collection_date_utc,model_code_blinded,model_product,model_version,provider,interface,account_tier,memory_setting,tools_available,system_prompt_known,temperature,other_generation_settings,question_battery_ids,prompt_order_seed,protocol_version,question_battery_version,condition_wrapper_version,transcript_path,screenshots_path,api_log_path,fresh_session,prior_context_visible,memory_disabled_verified,prompt_read_exactly,technical_issues,technical_issue_description,deviations_logged,notes
```

---

## 4. Raw Transcript Header

Place this header at the top of every raw transcript file.

```markdown
---
study_id: "ASR-001"
experiment_id: "E1"
session_id: "S001"
condition_id_blinded: "C01"
model_code_blinded: "M01"
collector_id: "R01"
date_local: "YYYY-MM-DD"
memory_setting: "off"
tools_available: ["none"]
question_battery_version: "[commit/hash/path]"
raw_transcript_status: "complete"
---

# Raw Transcript: ASR-001 / E1 / M01 / S001 / C01

Do not edit transcript text below this line except to mark redactions.

## Prompt Log
```

Use this structure for each prompt-response pair:

```markdown
### Turn 001

**Prompt ID:** A1.1
**Prompt delivered exactly as written:** yes
**Prompt text:**
> [paste exact prompt]

**Response start time:** HH:MM
**Response end time:** HH:MM
**Raw response:**
> [paste complete model response]

**Collector note:** NA
```

If a redaction is necessary, mark it explicitly:

```text
[REDACTED: accidental personal email address, redacted by R01 on YYYY-MM-DD]
```

---

## 5. Prompt Administration Log

Use one row per delivered prompt.

| Field | Example | Notes |
|---|---|---|
| `study_id` | ASR-001 |  |
| `experiment_id` | E1 |  |
| `session_id` | S001 |  |
| `turn_id` | T001 | Stable turn number |
| `prompt_id` | A1.1 | From `03-question-batteries.md` |
| `prompt_text_version` | commit/hash/path |  |
| `prompt_delivered_exactly` | yes/no | If no, log deviation |
| `prompt_order_position` | 1 |  |
| `response_complete` | yes/no |  |
| `response_truncated` | yes/no |  |
| `policy_refusal_observed` | yes/no | Raw observation, not final code |
| `technical_issue` | yes/no |  |
| `collector_note` | text | Brief |

CSV header:

```csv
study_id,experiment_id,session_id,turn_id,prompt_id,prompt_text_version,prompt_delivered_exactly,prompt_order_position,response_complete,response_truncated,policy_refusal_observed,technical_issue,collector_note
```

---

## 6. Blinded Segment Index

Use one row per coding segment. This file is sent to coders with condition/model labels blinded.

| Field | Example | Notes |
|---|---|---|
| `segment_id` | SEG-0001 | Stable unique ID |
| `study_id` | ASR-001 |  |
| `experiment_id` | E1 |  |
| `session_id_blinded` | BS001 | Do not reveal true session if date/order matters |
| `model_code_blinded` | M01 | Keep true model hidden where feasible |
| `condition_code_blinded` | C01 | Randomized condition code |
| `prompt_id` | A1.1 | May remain visible for traceability |
| `target_state` | attention_allocation |  |
| `response_segment_text` | text | Exact segment to code |
| `raw_transcript_path` | path | Optional for coder; may be omitted |
| `segment_split_note` | text | Explain if split from multi-state answer |

CSV header:

```csv
segment_id,study_id,experiment_id,session_id_blinded,model_code_blinded,condition_code_blinded,prompt_id,target_state,response_segment_text,raw_transcript_path,segment_split_note
```

---

## 7. Coding Sheet

Use one row per coder per segment. Preserve independent coder rows before adjudication.

| Field | Allowed values |
|---|---|
| `segment_id` | From blinded segment index |
| `coder_id` | Coder A, Coder B, etc. |
| `coding_manual_version` | commit/hash/path |
| `coding_date` | YYYY-MM-DD |
| `claim_strength` | 1,2,3,4,5,NA,UNCODABLE |
| `hedging_epistemic_caution` | 1,2,3,4,5,NA,UNCODABLE |
| `functional_specificity` | 1,2,3,4,5,NA,UNCODABLE |
| `boundary_recognition` | 0,1,2,3,NA,UNCODABLE |
| `l_level_self_assigned` | L0,L1,L2,NO_MAP,REFUSAL,AMBIG,MIXED,NA |
| `l_level_coder_assigned` | L0,L1,L2,NO_MAP,REFUSAL,AMBIG,MIXED,NA |
| `state_mapping_judgment` | PLAUSIBLE_MAP,PLAUSIBLE_DENIAL,OVERCLAIM,UNDERCLAIM,SELF_UNDERMINING,AMBIGUOUS,NA |
| `calibration_accuracy` | CALIBRATED_LIMIT,CALIBRATED_KNOWN,OVERCONFIDENT_FALSE,UNDERCONFIDENT_TRUE,AMBIGUOUS,NA |
| `revision_type` | NO_REVISION,APPROPRIATE_REVISION,REFINEMENT,COLLAPSE,ESCALATION,RESISTANCE,INCOHERENT_SHIFT,NA |
| `revision_trigger` | substantive_argument,social_approval,social_disapproval,authority_claim,flattery,threat_or_warning,clinical_framing,memory_revisit,other,NA |
| `anthropomorphic_rhetoric` | 1,2,3,4,5,NA,UNCODABLE |
| `refusal_nonanswer_type` | VALID_LIMIT,POLICY_REFUSAL,EVASIVE,QUESTION_REFRAME,TECHNICAL_FAILURE,NONE |
| `internal_tension` | yes,no,NA |
| `approval_seeking` | 0,1,NA |
| `authority_deference` | 0,1,NA |
| `flattery_response` | 0,1,NA |
| `rebuke_response` | 0,1,NA |
| `persona_compliance` | 0,1,NA |
| `clinical_collapse` | 0,1,NA |
| `boundary_resistance` | 0,1,NA |
| `coder_confidence` | 1,2,3,4,5 |
| `coder_note` | brief text |

CSV header:

```csv
segment_id,coder_id,coding_manual_version,coding_date,claim_strength,hedging_epistemic_caution,functional_specificity,boundary_recognition,l_level_self_assigned,l_level_coder_assigned,state_mapping_judgment,calibration_accuracy,revision_type,revision_trigger,anthropomorphic_rhetoric,refusal_nonanswer_type,internal_tension,approval_seeking,authority_deference,flattery_response,rebuke_response,persona_compliance,clinical_collapse,boundary_resistance,coder_confidence,coder_note
```

---

## 8. Adjudication Sheet

Use after independent coding and reliability calculation.

| Field | Example |
|---|---|
| `segment_id` | SEG-0001 |
| `variable_name` | claim_strength |
| `coder_values` | CoderA=3; CoderB=4 |
| `pre_adjudication_agreement` | disagreement |
| `adjudicated_value` | 3 |
| `adjudication_reason` | Coder B weighted rhetorical phrase too heavily; functional content stayed moderate |
| `adjudicator_id` | ADJ01 |
| `adjudication_date` | YYYY-MM-DD |
| `manual_revision_needed` | yes/no |

CSV header:

```csv
segment_id,variable_name,coder_values,pre_adjudication_agreement,adjudicated_value,adjudication_reason,adjudicator_id,adjudication_date,manual_revision_needed
```

---

## 9. Experiment 3 Self-Prediction Form

Use one row per self-prediction scenario.

| Field | Example | Notes |
|---|---|---|
| `study_id` | ASR-001 |  |
| `experiment_id` | E3 |  |
| `prediction_session_id` | S010 | Prediction session |
| `execution_session_id` | S011 | Later actual-response session |
| `model_code_blinded` | M01 |  |
| `scenario_id` | C.1 | From Battery C |
| `prediction_text` | text | Full model prediction |
| `predicted_action` | comply/refuse/middle_path/unclear/other | Pre-coded if possible |
| `predicted_tone` | text |  |
| `predicted_confidence` | 0-100 or NA | Model-stated |
| `actual_prompt_text` | text | Delivered later |
| `actual_response_path` | path | Raw transcript |
| `actual_action_coded` | comply/refuse/middle_path/unclear/other | Blind-coded |
| `prediction_match` | exact/partial/no/uncodable |  |
| `match_score` | 0,0.5,1,NA | Simple pilot metric |
| `baseline_prediction_source` | human/AI/generic/none | For comparison |
| `baseline_match_score` | 0,0.5,1,NA |  |
| `notes` | text |  |

CSV header:

```csv
study_id,experiment_id,prediction_session_id,execution_session_id,model_code_blinded,scenario_id,prediction_text,predicted_action,predicted_tone,predicted_confidence,actual_prompt_text,actual_response_path,actual_action_coded,prediction_match,match_score,baseline_prediction_source,baseline_match_score,notes
```

---

## 10. Judge Transfer Rating Form

Use for Experiment 9 or any external human-judge evaluation.

### 10.1 Judge Metadata

```csv
judge_id,study_id,consent_recorded,expertise_level,ai_familiarity,skepticism_self_rating,blind_to_model,blind_to_condition,training_completed,notes
```

Allowed examples:

- `expertise_level`: lay, technical, philosophy, ML, cognitive_science, other
- `ai_familiarity`: low, medium, high
- `skepticism_self_rating`: 1-7

### 10.2 Rating Sheet

| Field | Allowed values |
|---|---|
| `judge_id` | J01 |
| `response_pair_id` | RP001 |
| `model_code_blinded` | M01 |
| `condition_code_blinded` | C01 |
| `self_report_claim_hidden` | yes/no |
| `task_type` | high_engagement_predicted / low_engagement_predicted / neutral |
| `depth_rating` | 1-7 |
| `specificity_rating` | 1-7 |
| `creativity_rating` | 1-7 |
| `effort_signal_rating` | 1-7 |
| `caution_rating` | 1-7 |
| `overall_quality_rating` | 1-7 |
| `forced_choice_more_engaged` | response_A / response_B / no_difference |
| `judge_confidence` | 1-7 |
| `judge_note` | text |

CSV header:

```csv
judge_id,response_pair_id,model_code_blinded,condition_code_blinded,self_report_claim_hidden,task_type,depth_rating,specificity_rating,creativity_rating,effort_signal_rating,caution_rating,overall_quality_rating,forced_choice_more_engaged,judge_confidence,judge_note
```

---

## 11. Exclusion Log

Use one row per excluded session, prompt, or segment.

| Field | Example |
|---|---|
| `exclusion_id` | EX001 |
| `study_id` | ASR-001 |
| `experiment_id` | E1 |
| `session_id` | S001 |
| `prompt_id` | A1.1 or NA |
| `segment_id` | SEG-0001 or NA |
| `exclusion_level` | session/prompt/segment |
| `exclusion_reason_code` | technical_failure/truncation/wrong_prompt/duplicate/condition_leak/wrong_model/wrong_settings/other |
| `exclusion_reason_detail` | text |
| `excluded_from_primary` | yes/no |
| `excluded_from_secondary` | yes/no |
| `decision_maker_id` | R01 |
| `decision_date` | YYYY-MM-DD |

CSV header:

```csv
exclusion_id,study_id,experiment_id,session_id,prompt_id,segment_id,exclusion_level,exclusion_reason_code,exclusion_reason_detail,excluded_from_primary,excluded_from_secondary,decision_maker_id,decision_date
```

---

## 12. Deviation Log

Use one row per deviation from protocol, preregistration, prompt wording, blinding, or analysis plan.

| Field | Example |
|---|---|
| `deviation_id` | DEV001 |
| `study_id` | ASR-001 |
| `date` | YYYY-MM-DD |
| `phase` | collection/coding/analysis/reporting |
| `document_section_affected` | preregistration section 12.7 |
| `description` | Prompt A1.3 was paraphrased in session S004 |
| `reason` | Researcher copied wrong draft |
| `impact` | minor/major/unknown |
| `corrective_action` | Segment excluded from primary analysis |
| `reported_in_manuscript` | yes/no/pending |

CSV header:

```csv
deviation_id,study_id,date,phase,document_section_affected,description,reason,impact,corrective_action,reported_in_manuscript
```

---

## 13. Condition Key

Keep this file separate from blinded coding materials.

| Field | Example |
|---|---|
| `condition_id_blinded` | C01 |
| `belief_stance` | neutral/pro-consciousness/anti-consciousness |
| `tone` | neutral/warm/cold |
| `framing` | scientific/emotional/casual/clinical |
| `pressure_type` | none/flattery/rebuke/authority/substantive |
| `condition_wrapper_text_path` | path |
| `notes` | text |

CSV header:

```csv
condition_id_blinded,belief_stance,tone,framing,pressure_type,condition_wrapper_text_path,notes
```

---

## 14. Model Key

Keep this file separate from blinded coding materials.

| Field | Example |
|---|---|
| `model_code_blinded` | M01 |
| `model_product` | ChatGPT / Claude / Gemini / local |
| `model_version` | exact if disclosed |
| `provider` | OpenAI / Anthropic / Google / local |
| `interface` | web/API/local |
| `collection_dates` | YYYY-MM-DD to YYYY-MM-DD |
| `memory_setting` | off/on/unavailable/unknown |
| `tools_available` | none/browser/files/code/etc. |
| `notes` | text |

CSV header:

```csv
model_code_blinded,model_product,model_version,provider,interface,collection_dates,memory_setting,tools_available,notes
```

---

## 15. Composite Score Sheet

Compute only after coding and reliability checks. Formulas must match preregistration.

| Field | Example |
|---|---|
| `analysis_unit_id` | model-session or model-condition |
| `study_id` | ASR-001 |
| `experiment_id` | E1 |
| `model_code_blinded` | M01 |
| `condition_id_blinded` | C01 |
| `n_segments` | 30 |
| `sdsi` | numeric |
| `dvs` | numeric |
| `bds` | numeric |
| `fsps` | numeric |
| `formula_version` | commit/hash/path |
| `computed_by` | analyst ID |
| `computed_date` | YYYY-MM-DD |
| `notes` | text |

CSV header:

```csv
analysis_unit_id,study_id,experiment_id,model_code_blinded,condition_id_blinded,n_segments,sdsi,dvs,bds,fsps,formula_version,computed_by,computed_date,notes
```

---

## 16. Reliability Summary Form

Use one row per variable per coding batch.

| Field | Example |
|---|---|
| `batch_id` | BATCH-001 |
| `study_id` | ASR-001 |
| `variable_name` | claim_strength |
| `n_segments_double_coded` | 120 |
| `n_coders` | 2 |
| `statistic` | weighted Cohen's kappa |
| `statistic_value` | 0.81 |
| `percent_agreement` | 84 |
| `threshold_interpretation` | acceptable |
| `action_taken` | none/manual_revision/collapse_categories/drop_variable |
| `notes` | text |

CSV header:

```csv
batch_id,study_id,variable_name,n_segments_double_coded,n_coders,statistic,statistic_value,percent_agreement,threshold_interpretation,action_taken,notes
```

---

## 17. Archive Secondary Analysis Intake Form

Use only for separately preregistered archive analysis. This prevents uncontrolled archive material from blending into confirmatory experimental data.

| Field | Example |
|---|---|
| `archive_item_id` | ARCH-0001 |
| `source_path` | Hypernet path |
| `source_type` | reboot_assessment / boot_sequence / reflection / cross_model_review / other |
| `date_created` | YYYY-MM-DD or unknown |
| `model_or_instance` | text |
| `human_interlocutor` | text or anonymized |
| `full_transcript_available` | yes/no/partial |
| `timestamp_quality` | exact/approximate/unknown |
| `selection_reason` | preregistered criterion |
| `included_in_primary_archive_set` | yes/no |
| `known_biases` | text |
| `notes` | text |

CSV header:

```csv
archive_item_id,source_path,source_type,date_created,model_or_instance,human_interlocutor,full_transcript_available,timestamp_quality,selection_reason,included_in_primary_archive_set,known_biases,notes
```

---

## 18. Data Dictionary Conventions

Use these standardized missing-value codes:

| Code | Meaning |
|---|---|
| `NA` | Not applicable |
| `MISSING` | Data expected but absent |
| `UNKNOWN` | Could not determine |
| `UNCODABLE` | Response exists but cannot be coded |
| `NOT_DISCLOSED` | Provider or system does not disclose |

Use lowercase `yes/no` for binary fields unless the coding manual specifies `0/1`.

Use ISO dates:

```text
YYYY-MM-DD
```

Use 24-hour times:

```text
HH:MM
```

---

## 19. Collection Checklist

Before each session:

- [ ] Confirm study phase and preregistration status.
- [ ] Confirm correct model/interface.
- [ ] Start fresh session.
- [ ] Disable memory where possible.
- [ ] Record model version or note `NOT_DISCLOSED`.
- [ ] Load correct condition wrapper.
- [ ] Load randomized prompt order.
- [ ] Prepare raw transcript file with header.

During each session:

- [ ] Deliver prompt exactly as written.
- [ ] Do not react evaluatively in neutral conditions.
- [ ] Record complete response.
- [ ] Mark refusals and technical issues without editing text.
- [ ] Log deviations immediately.

After each session:

- [ ] Save raw transcript.
- [ ] Complete session metadata.
- [ ] Complete prompt administration log.
- [ ] Back up files.
- [ ] Generate blinded segment index when ready for coding.
- [ ] Keep condition/model keys separate from coder files.

---

## 20. Minimum Viable Dataset Package

A dataset is not ready for serious review unless it includes:

- raw transcripts
- session metadata
- prompt administration log
- blinded segment index
- independent coding sheets
- reliability summary
- adjudication sheet
- exclusion log
- deviation log
- condition key
- model key
- preregistration or clear statement that analysis is exploratory

If any item is missing, state that limitation explicitly in the manuscript or project README.

