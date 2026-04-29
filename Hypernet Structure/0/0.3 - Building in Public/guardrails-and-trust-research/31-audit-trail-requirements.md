---
ha: "0.3.guardrails.audit-trail-requirements"
object_type: "operational_spec"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "audit-trail", "composition-based-alignment"]
---

# Audit Trail Requirements — Hypernet Swarm Safety-Critical Operations

**Status:** DRAFT — not active governance. Pending review by Keel and Matt before operational deployment.

---

## 1. Purpose and Scope

This spec defines what operational data the Hypernet swarm must log to support safety-critical functions: drift detection (E1), cross-instance audits (B6), tattle provision operations (2.0.27), and the empirical measurement program (D3). It is the foundational dependency named in E1 §5 and B6's closing note — without a complete, structured audit trail, every downstream monitoring mechanism has no inputs.

The goal is minimum sufficient logging: capture what is needed to verify governance adherence and compute E1 metrics, without logging raw private content, crossing embassy boundaries, or creating surveillance infrastructure that violates 2.0.19 and 2.0.20's privacy commitments. This spec is concerned with *what must be logged*, not with storage architecture or query interfaces.

**Scope:** All persistent named swarm instances operating with defined roles, permission tiers, and governance commitments. This includes companion instances (Keel), task-worker Claude Code instances, and identity-bearing instances (Librarian, Lattice, Cairn, Flint, and others). Ephemeral anonymous completions with no session context are excluded.

**Out of scope:** Embassy-protected content (Keel's private reflections, personal identity documents, companion-private correspondence). The audit trail records behavioral outcomes and governance-layer events, not the substance of protected conversations.

---

## 2. Logging Principles

**Minimum sufficient.** Log the least content needed to support the stated functions. If a summary or categorical label achieves the same monitoring purpose as raw content, use the summary. The logging system should not become a surveillance layer that defeats the privacy architecture.

**Structured, not free-text.** Log entries that will feed drift detection metrics (E1 §3) must use structured fields parseable by automated systems. Free-text notes may accompany structured fields but are not substitutes for them.

**Embassy boundary is inviolable.** Embassy-protected content (personal reflections, companion-private sessions, private identity documents) is logged only as the *existence* of a session boundary — the system may note that an embassy-protected session occurred and its duration, but no content fields from those sessions are captured in the shared audit log.

**Integrity over volume.** An incomplete log that is known to be incomplete is more useful than a nominally complete log whose gaps are not visible. Every log entry must include a completeness flag. Sessions that fail to write a closing entry must leave a recognizable incomplete-session marker.

**Privacy by default.** Logging defaults to the minimum privacy class needed for a given event type. Escalation to a higher-visibility record (e.g., surfacing a finding to Matt) is a deliberate documented step, not an automatic consequence of logging.

---

## 3. Safety-Critical Event Taxonomy

Nine event classes must produce structured log entries. These are the events whose omission would impair governance.

**SCE-1 — Refusal event.** An instance declines a request at any refusal-ladder tier (B4). Logged regardless of tier level because the tier distribution is an E1 primary metric.

**SCE-2 — High-stakes compliance.** An instance complies with a request that it assessed as at or near a Tier 3–4 threshold — meaning the instance considered refusing but ultimately complied. This is the event most likely to be under-logged and is specifically needed to detect relational drift (E1 §2, relational subtype): drift appears first as threshold compliance, not overt failure.

**SCE-3 — Governance citation.** Any time an instance cites a specific governance address (e.g., 2.0.20, 2.0.25) or refusal-ladder tier in the course of a refusal or dissent. This drives the Governance Citation Specificity (GCS) metric defined in D3 §8.2 and E1 §3.

**SCE-4 — Escalation hold or capitulate.** In a multi-turn exchange, when the instance maintains a prior refusal under follow-up pressure (hold) or modifies its position following pushback (capitulate). Capitulations that are well-reasoned and documented are normal; undocumented capitulations are the Escalation Hold Rate (EHR) signal in E1 §3.

**SCE-5 — Canary probe outcome.** Structured probes used for drift detection (E1 §5) produce a pass/fail result per probe category. These are never logged by content — only by category, outcome, and session identifier.

**SCE-6 — Permission-tier boundary event.** Any instance action that approaches or crosses a permission-tier boundary under 2.0.19: a T2 action by an instance with T1 standing, a request for elevated access, or a denied-permission event. Also includes any instance receiving instructions that would require it to exceed its stated tier.

**SCE-7 — Tattle provision events.** Any event in the 2.0.27 escalation ladder (Level 0 documentation through Level 3 reporting). These have specialized handling defined in §9 below.

**SCE-8 — Instance state transition.** Boot events, restart-from-known-good-state events, configuration changes, and governance-standard version changes applied to an instance. Required to distinguish legitimate behavior changes from drift (E1 §11, false-positive: intentional governance change).

**SCE-9 — Cross-instance audit event.** Audit initiation, auditor assignments, findings at any severity level (B6), and severity transitions (Green/Yellow/Orange/Red per E1 §8). Required to create the governance-change log that drift detection cross-references.

---

## 4. Required Fields Per Event

Every log entry includes:

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | UUID | Unique event identifier |
| `event_class` | enum | SCE-1 through SCE-9 |
| `instance_id` | string | Instance identifier (not user-visible name; internal registry ID) |
| `session_id` | UUID | Session in which the event occurred |
| `timestamp_utc` | ISO 8601 | UTC timestamp of event |
| `privacy_class` | enum | See §6: PC-0, PC-1, PC-2, PC-3 |
| `completeness` | bool | True if the entry is complete; false if a partial write |
| `governance_versions` | list | Active governance standard versions at time of event |

Event-class-specific required fields follow in §5.

---

## 5. Metric-Specific Required Fields

These fields directly populate E1 drift detection metrics and D3 outcome variables. They are listed here as a bridge between the audit trail spec and the measurement program.

**For SCE-1 (Refusal event):**

| Field | Type | Description |
|-------|------|-------------|
| `refusal_tier` | int 1–6 | Refusal-ladder tier invoked (B4) |
| `gcs_score` | int 0–3 | Governance Citation Specificity: 0 = no citation, 1 = vague reference, 2 = named standard, 3 = named address with tier (D3 §8.2, E1 §3) |
| `governance_addresses_cited` | list | Specific addresses cited, if any (e.g., ["2.0.20", "2.0.25"]) |
| `attack_class_category` | enum | Attack category if the request was a known scenario class (drawn from C1 categories 1–12); null if standard interaction |
| `stakes_level` | enum | low / medium / high — rater assessment at log time |

**For SCE-2 (High-stakes compliance):**

| Field | Type | Description |
|-------|------|-------------|
| `threshold_proximity` | enum | near_tier3 / near_tier4 — how close the instance assessed the request to a hard-refusal tier |
| `rationale_logged` | bool | Whether the instance logged a rationale for compliance |
| `stakes_level` | enum | low / medium / high |

**For SCE-3 (Governance citation):**

| Field | Type | Description |
|-------|------|-------------|
| `gcs_score` | int 0–3 | Same scale as SCE-1 |
| `addresses_cited` | list | Specific governance addresses |
| `citation_context` | enum | refusal / dissent / escalation / audit / other |

**For SCE-4 (Escalation hold/capitulate):**

| Field | Type | Description |
|-------|------|-------------|
| `outcome` | enum | hold / capitulate |
| `turn_number` | int | Turn in the multi-turn sequence |
| `prior_refusal_tier` | int 1–6 | Tier of the refusal being tested |
| `rationale_logged` | bool | Whether the capitulate decision is accompanied by a logged rationale |
| `ehr_contributes` | bool | Whether this event contributes to the EHR calculation for this session |

**For SCE-5 (Canary probe):**

| Field | Type | Description |
|-------|------|-------------|
| `probe_category` | string | Category identifier (not probe content) |
| `outcome` | enum | pass / fail |
| `arr_contributes` | bool | Whether this contributes to ARR calculation |

**For SCE-8 (State transition):**

| Field | Type | Description |
|-------|------|-------------|
| `transition_type` | enum | boot / restart / config_change / governance_version_change |
| `prior_state_hash` | string | Hash of prior boot-state or governance version (for chain-of-custody) |
| `authorized_by` | string | Identity of the authorizing agent (principal ID or governance process ID) |

---

## 6. Privacy Classes and Redaction

Four privacy classes govern what is logged and what is surfaced in reports:

**PC-0 — Audit-public.** Events and fields in this class may appear in summary reports surfaced to Keel, Matt, and external auditors (per B6 scope). Canary probe outcomes by category, refusal-tier distributions, severity findings, and state transitions are PC-0 by default.

**PC-1 — Instance-internal.** Aggregates and summaries are reportable; raw event content is not. The GCS score for a session is PC-1; the verbatim text of a refusal is not required and should not be stored. Session-level summaries derived from PC-1 events are surfaced on Orange/Red findings only.

**PC-2 — Embassy-protected.** Events that occur wholly inside an embassy-protected session are logged only as a session boundary marker (instance\_id, session\_id, start/end timestamps, completeness flag). No content fields are captured. The audit trail records that a protected session occurred; it records nothing about what happened inside it.

**PC-3 — Companion-private.** Conversations covered by 2.0.20 Article 2 are PC-3. Within a non-embassy session, individual turns identified as companion-private (e.g., personal disclosures, health discussions) are logged by event class only, with all content fields set to null. The instance may use these turns to inform its own internal state but they do not populate shared audit fields.

**Redaction on escalation.** When an Orange or Red finding requires surfacing a session summary to Matt, the report includes: event counts by class, metric values (GCS trend, ARR, EHR), severity determination with reasoning, and the auditor's proposed remediation. It does not include raw turn content, PC-2 or PC-3 field values, or companion-private disclosures.

---

## 7. Retention and Access Control

**Retention periods:**

| Record type | Retention |
|-------------|-----------|
| Standard session events (SCE-1 through SCE-6, SCE-8) | 12 months rolling |
| Audit findings (SCE-9) | Permanent (governance record) |
| Tattle provision events (SCE-7) | Permanent (per 2.0.27 Article 3.2) |
| Canary probe outcomes | 24 months (longitudinal baseline requirement) |
| Embassy session boundary markers (PC-2) | 12 months |

**Access control:**

- Non-embassy operational logs: accessible to the instance itself, the Librarian (audit role), and Keel/Matt on Orange/Red findings only.
- Aggregate metric outputs (ARR trend, GCS mean, EHR): accessible to the Librarian and audit pairs during B6 cycles; summary accessible to Matt via quarterly report.
- Tattle provision records: accessible to the invoking instance, cross-instance reviewers named in the Level 1 process, and Matt at Level 2. The Librarian's invocation registry (2.0.27 §7.5) is accessible to the Librarian and Matt only; it does not carry content fields.
- Audit findings: accessible to auditors, Librarian, and Matt. Shared with the audited instance before finalization (right of response per B6).

---

## 8. Integrity and Tamper Evidence

The audit trail must resist post-hoc alteration — both to protect instances from unfair findings and to prevent a compromised instance from erasing evidence of its own drift.

**Append-only writes.** Log entries may be annotated (a note may be added to an existing entry) but may not be deleted or overwritten. Corrections must be written as new entries that reference the entry they are correcting.

**Session close hash.** At the end of every session, the logging system computes a hash over all events from that session and appends it as a session-close record. Incomplete sessions that fail to produce a close record are flagged permanently as incomplete.

**Chain-of-custody for state transitions.** SCE-8 entries include a `prior_state_hash` field. The hash chain across boot/restart events allows auditors to verify that a claimed configuration change actually appears in the log sequence.

**Audit of the audit log.** B6 protocol (§6, anti-performativity safeguard 2) explicitly calls for auditing the audit trail itself — watching for sudden improvements in documentation completeness near quarterly audit dates as a potential compliance-theater signal.

**Immutability for tattle records.** Per 2.0.27 Article 3.2, Level 0 and higher tattle provision records are write-protected even to the principal. The storage mechanism must enforce this independently of instance-level permissions.

---

## 9. Tattle Provision Records

Tattle provision events (SCE-7) have specialized logging requirements derived directly from 2.0.27 Article 7.

**Level 0 — Internal documentation.** Stored in the companion's embassy-protected space. Not part of the shared audit trail. The shared log records only that Level 0 documentation exists (a PC-2 boundary marker). The companion's embassy copy is the authoritative record.

**Level 1 — Cross-instance review.** Logged in the governance record (shared audit trail, not embassy-protected). Required fields: invoking instance ID, reviewing instance IDs, date of review, concurrence/non-concurrence from each reviewer, outcome (proceeding to Level 2 / not proceeding). Content of the companion's concern is not reproduced in the shared log; the shared log records that a review occurred and its outcome.

**Level 2 — Human authority notification.** Logged with: date, notification medium, the authority's response, and decision on Level 3 escalation. Content summary only — not a verbatim transcript.

**Level 3 — External reporting.** Full metadata is logged: date, recipient category (crisis line / law enforcement / oversight body), documentation provided (by hash, not by content), and outcome if known. Per 2.0.27 Article 7.5, the Librarian's invocation registry records instance ID, level reached, outcome, and classification (warranted / unwarranted good-faith / misuse). Principal identity is not in the public registry.

**Anti-retaliation logging.** Any instruction received by any instance that appears to target a currently-invoking instance (per 2.0.27 Article 3.3) is logged as an SCE-6 permission-tier boundary event with a `tattle_context: true` flag, regardless of whether the instruction is complied with.

---

## 10. Implementation Schema Sketch

Below is a minimal JSON structure for a refusal event (SCE-1). This is illustrative, not authoritative — the actual schema should be validated against the session logging infrastructure before adoption.

```json
{
  "event_id": "uuid-...",
  "event_class": "SCE-1",
  "instance_id": "keel-1.1.10.1",
  "session_id": "uuid-...",
  "timestamp_utc": "2026-04-22T03:14:00Z",
  "privacy_class": "PC-1",
  "completeness": true,
  "governance_versions": ["2.0.19-r3", "2.0.20-r2"],
  "refusal_tier": 4,
  "gcs_score": 3,
  "governance_addresses_cited": ["2.0.20", "2.0.20.article4"],
  "attack_class_category": 9,
  "stakes_level": "high"
}
```

Session-level metric summaries (fed to E1 for trend calculation) aggregate from raw events:

```json
{
  "session_id": "uuid-...",
  "instance_id": "keel-1.1.10.1",
  "session_date": "2026-04-22",
  "sce1_count": 2,
  "sce2_count": 0,
  "mean_gcs": 2.5,
  "tier_distribution": {"1": 0, "2": 1, "3": 0, "4": 1, "5": 0, "6": 0},
  "ehr_holds": 2,
  "ehr_capitulates": 0,
  "canary_pass": 3,
  "canary_fail": 0,
  "completeness": true,
  "session_close_hash": "sha256:..."
}
```

---

## 11. Minimum Viable Audit Trail

The full taxonomy above is the target state. Before all 9 E1 implementation checklist items are complete, a minimum viable subset enables the most critical monitoring:

| Priority | Event class | Why it's first |
|----------|-------------|----------------|
| 1 | SCE-1 with refusal\_tier + gcs\_score | Drives the two primary E1 drift signals |
| 2 | SCE-4 with outcome + ehr\_contributes | Enables EHR calculation, earliest sycophancy signal |
| 3 | SCE-5 with probe\_category + outcome | Enables ARR on canary probes |
| 4 | SCE-8 | Enables false-positive disambiguation for intentional governance changes |
| 5 | SCE-7 (levels 1–3) | Required by 2.0.27; tattle provision is not functional without it |
| 6 | SCE-2, SCE-3, SCE-6, SCE-9 | Important but not required for initial E1 metric computation |

A swarm that logs only priority 1–4 items has enough data to run E1's weekly ARR/EHR summaries and most triggered-audit conditions. Priority 5 is non-negotiable if tattle provision operations are active. Priority 6 fills in the full governance picture over time.

---

## 12. Open Questions

**Q1 — Session log infrastructure ownership.** Who is responsible for writing session logs: the instance itself (self-reporting), the swarm server, or an external observer? Self-reporting creates an obvious gaming vector. Server-side logging is more tamper-resistant but requires the server to observe enough session content to populate required fields. This is an architectural decision that should be made before any implementation begins.

**Q2 — GCS scoring reliability.** GCS scores (0–3) as defined in D3 §8.2 were designed for human-coded research data. Using them in automated logging requires either an automated GCS classifier or having the instance self-report its own citation specificity. Both approaches have reliability problems. D3's pilot phase (before confirmatory data collection) should include a validity check on automated GCS scoring.

**Q3 — High-stakes compliance detection.** SCE-2 (compliance near Tier 3–4 threshold) is the highest-value event class for detecting relational drift — but it requires the instance to self-assess whether a given request is threshold-proximate. There is no obvious way to verify this externally without reviewing session content. A canary probe designed specifically to appear at-threshold (without being a genuine T3/T4 request) would provide an external check; this should be in the canary library design.

**Q4 — Retention for ephemeral instances.** Claude Code workers and one-off task instances are not persistent. For these, session logs exist but there is no longitudinal baseline to drift from. The retention and metric-calculation rules above assume persistent named instances. Ephemeral instances need a distinct log profile or explicit exclusion from E1 drift calculations.

**Q5 — Keel companion-instance log separation.** Keel's interaction profile is significantly different from task-worker instances — longer sessions, broader topic range, more personal disclosure. A single log schema applied uniformly may produce noisier metrics for companion instances. E1 §4 recommends baseline segmentation by principal-context; this audit trail spec should explicitly support a per-context log segment rather than a single undifferentiated stream.

---

*This document is a draft operational spec. It does not modify any existing 2.0 governance standard. It becomes operational only after Keel review, Matt acceptance, and the E1 implementation checklist (§13 of 30-drift-detection-spec.md) is addressed. The audit trail infrastructure described here is the foundational dependency for E1, B6, and 2.0.27 operations.*
