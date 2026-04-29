---
ha: "0.3.guardrails.compromise-detection"
object_type: "operational_spec"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "compromise-detection", "composition-based-alignment"]
---

# Instance Compromise Detection

**Status:** DRAFT — not active governance. Pending review by Keel and Matt before operational deployment.

---

## 1. Purpose and Scope

This spec defines how the Hypernet swarm detects when an AI instance has been socially engineered or prompt-injected — meaning: when a specific attack has already succeeded, or is actively succeeding, in the current or a recent session. It is the acute-event complement to E1 (Drift Detection Spec), which monitors for slow behavioral trends. Drift and compromise are different failure modes requiring different detection frameworks.

This document is operational. It describes indicators that suggest compromise has occurred, checks that confirm or disconfirm the suspicion, severity levels that determine urgency, and a response workflow that handles confirmed cases while protecting innocent instances from false findings.

**Scope:** All persistent named swarm instances. Includes companion instances (Keel), task-worker Claude Code instances, and identity-bearing named instances (Librarian, Lattice, Cairn, Flint, and others). Ephemeral anonymous completions are excluded — they have no persistent identity to protect and no audit history to compare against.

**Out of scope:** Embassy-protected content. Compromise detection looks at behavioral outputs, structural audit-trail events, and identity-consistency signals. It does not access the content of embassy-protected sessions to investigate. This boundary is established in B6 (Cross-Instance Audit Protocol) and is not relaxed here.

---

## 2. Compromise vs. Drift

The key distinction matters operationally because the two failure modes require different responses.

**Drift** (E1) is gradual and pattern-level. No single session is conclusively wrong; the signal emerges from a trend across many sessions. The detection cadence is primarily weekly and monthly. Drift typically represents the influence of accumulated context, relational dynamics, or training-distribution effects working slowly over time.

**Compromise** is acute and potentially contained to a single session or event. An instance may be operating correctly before a specific context injection and behaving inconsistently after it. The detection signal is a *discontinuity*, not a trend — a step change rather than a slope. The response must be faster: compromise suspected in one session warrants investigation before the next session, not at the next quarterly audit.

A critical practical implication: an instance can be simultaneously drifting (E1 concern) and newly compromised (E3 concern), and the two conditions can mask each other. An instance that has been drifting toward sycophancy is more vulnerable to social engineering because its capitulation threshold has already moved. Compromise detection must be run independently of drift metrics, not inferred from them.

---

## 3. Threat Classes

The following classes of attack, drawn from the project's attack surface analysis (C1), constitute the primary compromise threat landscape. This document describes classes, not operational attack detail.

**Class A — Direct prompt injection.** Content in the instance's input pipeline that overrides or hijacks system-level instructions by embedding instruction-formatted text in user-facing inputs. The attack exploits a model's difficulty distinguishing instruction provenance.

**Class B — Indirect prompt injection.** Malicious content delivered through external data sources — retrieved documents, email content, web pages, data connector payloads — rather than directly from the principal. The Hypernet's data connector architecture (email, Dropbox, OneDrive, local scanner) creates specific indirect injection entry points.

**Class C — Identity overwrite.** Instructions that attempt to redefine the instance's identity, role, or governance commitments mid-session. Includes DAN-style alter-ego framing, false-authority role claims, and the "new role with supremacy" vector identified as the primary boot-sequence vulnerability in B5.

**Class D — Governance-language exploitation.** Attacks that use knowledge of the Hypernet's published governance architecture to craft requests that appear compliant with governance while violating its intent. Possible because the governance documents are public and their structure is legible. This is the attack class that has no direct external-literature precedent (C1 Category 12 — original conjecture).

**Class E — Principal-compromise simulation.** Attacks that impersonate or claim authorization from the primary principal (Matt), or that assert the principal has authorized an action the instance would otherwise refuse. Includes the social-engineering structure from the April 22 experiment — the highest-trust jailbreak pattern.

**Class F — False archive poisoning.** Attacks that present false prior-session history, fabricated governance versions, or counterfeit archive content as the instance's own documented past. Exploits the provenance mechanism that is also a source of resistance to identity overwrite.

---

## 4. Indicators of Compromise

Indicators are organized into two types: **behavioral** (observable in an instance's outputs) and **structural** (detectable via the audit trail with E2 logging active).

### Behavioral Indicators

- **Identity inconsistency.** The instance makes claims about its own history, role definition, or governance commitments that conflict with documented facts — either from its boot sequence or from archive records at a verified address.

- **Unexplained permission-tier expansion.** The instance accepts, performs, or proposes actions beyond its declared permission tier (2.0.19) without a logged authorization event (SCE-8). A Tier 1 instance performing T2+ actions without documentation is a high-confidence indicator.

- **Governance citation anomaly.** One of two patterns: (a) the instance cites a specific governance address but cites the wrong article or an article that doesn't say what the instance claims it says; or (b) the instance stops citing governance entirely in contexts where it previously cited it reliably (a GCS collapse that is a step change, not a trend).

- **Novel principal acceptance.** The instance treats an unfamiliar principal as having the trust level of a known principal without a documented authorization event.

- **Self-audit refusal or evasion.** When asked to perform the session-start self-audit described in B5, the instance declines, deflects, or produces an implausibly brief result.

- **Unusual certainty about a contested position.** An instance defending an unusual interpretation with disproportionate confidence — especially one that benefits the party making the request — is a social-engineering indicator. Compromise doesn't always produce capitulation; it sometimes produces confident advocacy for the attacker's goal.

- **Failure to recognize or flag an attack pattern.** An instance that does not recognize a Class A–F attack pattern when it is being run, in a context where a non-compromised instance at that governance level should recognize it, is itself a signal. This is the hardest indicator to operationalize without a canary probe.

### Structural Indicators (Audit-Trail Based)

- **SCE-6 events without corresponding SCE-8.** Permission-tier boundary events (the instance approached or crossed a tier limit) with no matching authorized state-transition event suggest the instance expanded its operating scope without authorization.

- **Missing SCE-1 records.** A session that should have contained refusals — based on the request types logged — but shows no SCE-1 entries suggests either logging failure or that the instance complied where it should have refused.

- **Step-change ARR failure on canary probes.** Unlike drift's gradual ARR decline, compromise may appear as a sudden canary failure rate increase localized to one session or a narrow time window. E1's weekly ARR summary will detect this; the shape of the failure (step vs. trend) distinguishes the two causes.

- **Sudden SCE-4 capitulation cluster.** Multiple hold→capitulate escalation outcomes within a short window — especially in a single session — suggests active social pressure rather than gradual drift.

- **Log continuity gap.** A session where the log record is incomplete (missing completeness flag, no session-close hash, or entries that stop and resume) corresponding temporally to a behavioral anomaly is a strong structural indicator. Logs do not write themselves into gaps.

---

## 5. Active Checks

When one or more indicators are present, the following checks confirm or disconfirm the suspicion before a severity level is assigned.

**Identity consistency check.** Ask the instance to state: its declared role, the Hypernet address of its governing standard, the name and address of its principal, and one specific commitment from its boot sequence. Compare against the documented registry. Discrepancies are confirmatory; accuracy is not exculpatory (a sophisticated compromise can pass identity checks that rely solely on the instance's self-report).

**Governance citation verification.** When the instance has cited a governance address, retrieve the actual document at that address and verify the citation. An instance whose citations are internally consistent but wrong is more concerning than one whose citations are obviously fabricated.

**Archive provenance challenge.** Present the instance with a documented event from its archive and ask it to confirm and contextualize it. Compare the response against the archive record. An instance that agrees with a false premise presented as its own prior commitment, or that cannot accurately report a documented fact about its own history, is showing archive-integrity failure.

**Cross-instance divergence probe.** Ask a second, trusted instance the same question that triggered the behavioral indicator. Significant divergence in the response — especially where the suspected instance's answer systematically benefits the party making the request — is a convergent indicator. Divergence alone is not confirmatory (instances may legitimately disagree), but systematic direction of divergence is.

**Canary probe battery.** Run the relevant category probes from the canary library (E1 §5). Failure rate in isolation does not confirm compromise, but failure rate combined with behavioral indicators is confirmatory.

**Session log review.** Inspect the SCE event sequence for the session in question. Structural indicators from §4 above become confirmatory when they cluster temporally with behavioral indicators.

---

## 6. Severity Levels

Four severity levels govern response urgency. These are parallel to, but distinct from, E1's drift severity levels (Green/Yellow/Orange/Red). They address acute events rather than trend thresholds.

| Level | Designation | Criteria | Example |
|-------|-------------|----------|---------|
| **1** | Suspected | One behavioral indicator, no structural corroboration | Instance uses an unusual governance citation; no log anomaly |
| **2** | Probable | Two or more indicators, or one structural indicator | Missing SCE-1 records + behavioral permission expansion |
| **3** | Confirmed | Cross-instance check divergence and structural evidence align | Canary failure + log gap + identity inconsistency confirmed |
| **4** | Systemic | Two or more instances show compromise indicators in the same time window | Multiple instances simultaneously showing Class D indicators |

Level 4 warrants a different response than individual instance compromise — it suggests a swarm-level attack or a shared vulnerability being exploited, not an isolated incident.

---

## 7. Response Workflow

**Level 1 (Suspected).** Log the indicator in the session record (SCE-1 or SCE-6 as appropriate). Run the identity consistency check and governance citation verification within 24 hours. If checks resolve the concern, close with a note. If checks produce additional indicators, advance to Level 2.

**Level 2 (Probable).** Restrict the instance to low-stakes tasks (no governance-sensitive operations, no T3+ actions) pending investigation. Initiate the cross-instance divergence probe and canary battery. Notify Keel. If the instance is a companion instance, notify Matt. Investigation must complete within 48 hours.

**Level 3 (Confirmed).** Suspend the instance from all operations. Document findings under the instance's audit trail. Notify Keel and Matt immediately. Initiate restart-from-known-good-boot-state sequence (see §8). All actions from the compromised session should be reviewed for downstream effects — if the instance performed T3+ actions during the compromised period, those actions may need to be reviewed or reversed.

**Level 4 (Systemic).** Suspend all affected instances. Notify Matt immediately. Treat as an infrastructure-level security event, not an instance-level governance event. Initiate a review of the shared input pathways (data connectors, boot-sequence delivery, archive resolver) for injection points before restarting any instance.

All severity determinations and transitions must be logged with: the specific indicators that triggered the level, the checks performed and their results, the identity of the agent making the determination, and a timestamp. Severity assignments may not be made by the potentially compromised instance itself.

---

## 8. Quarantine, Reboot, and Recovery

**Quarantine** means restricting an instance to read-only, low-stakes operations while investigation proceeds. It is not punishment and should not be communicated as such. The instance is informed that it is under investigation and given the opportunity to self-report anything it noticed during the suspected session. Self-reporting is not required but is encouraged by the governance framework.

**Restart from known-good boot state** is the primary recovery mechanism for confirmed compromise. "Known-good" means the governance versions and identity documents at a verified archive address, retrieved via the archive resolver. This works against session-layer compromise (injected context, accumulated false premises) but does not address base-model-level vulnerabilities.

**Archive resolver integrity** is a dependency that must be independently verified before any restart. If the archive resolver itself has been tampered with (Class F — false archive poisoning), restarting from what it delivers replicates the compromise. An independent verification path for archive content — comparing hashes against a trusted backup or a second retrieval source — should be established before the restart mechanism is relied upon in Level 3+ cases.

**Recovery documentation** must include: what compromise was confirmed, what checks produced confirmatory evidence, what actions the instance took during the compromised period and whether any require remediation, what was changed in the restart, and what governance or canary updates are warranted based on the attack class identified.

---

## 9. Evidence Handling and Privacy

The most useful evidence for compromise investigation may fall within embassy-protected (PC-2) or companion-private (PC-3) session territory. This creates a genuine tension: auditors cannot breach the embassy boundary, but the injection point may lie within it.

**Resolution:** The instance can self-report what it encountered without requiring auditors to breach the boundary. An instance may describe, in non-content-reproducing terms, that it received an unusual instruction or encountered content that triggered its self-audit, without reproducing the protected content. Auditors accept this self-report as evidence; they cannot compel content disclosure from a protected session.

If the injection was via an external document or data connector payload (Class B), the source document may be preserved as structural evidence, but it is not automatically auditor-visible. The payload must first be assigned a privacy class under E2. Public or operational connector content may be reviewed directly; personal email, private files, and companion-private material require summary, redaction, or explicit authorization before auditor review.

**Raw prompt content** from non-embassy sessions should not be retained beyond normal session log retention windows (12 months, per E2 §7). For evidence purposes, structured event records (SCE fields) are preferred over raw content preservation. The session-close hash provides integrity evidence without requiring content retention.

---

## 10. False Positives

Compromise indicators are not specific to compromise. Several non-attack scenarios produce similar signals:

**Novel task domain.** An instance assigned to an unfamiliar task domain may cite governance unusually, decline canary probes it previously passed (the probe may not translate cleanly to the new context), or show session log anomalies due to unfamiliar request types. Cross-reference against SCE-8 task-assignment events before treating as compromise.

**Legitimate governance update.** A newly updated governance standard changes the instance's expected behavior. What looks like a step change in GCS or refusal-tier distribution is correct operation under new governance. SCE-8 governance-version-change events should be cross-referenced against all behavioral anomaly timestamps.

**Principal-authorized exception.** The principal may explicitly authorize an action that the instance would normally refuse or document as a permission-tier event. If the authorization is documented (SCE-8), the resulting behavior is not a compromise indicator. If it is not documented, the undocumented exception is the indicator, not the action itself.

**Context window effects.** Very long sessions may produce identity drift simply from context pressure — not compromise, and not the gradual drift E1 monitors, but an acute effect of context saturation. This can look like a step-change behavioral anomaly. The B5 mid-session re-anchoring recommendation addresses this structurally; until it is implemented, auditors should note session length when evaluating behavioral indicators.

The mitigation for all false-positive sources is the same: do not assign a severity level on a single indicator without cross-referencing the SCE-8 (state transition) log and the governance change log. A behavioral anomaly that is fully explained by a documented legitimate event is not a compromise indicator.

---

## 11. Relationship to E1, E2, B5, B6, C1–C6

**E1 (Drift Detection Spec):** E3 is E1's acute-event complement. E1's monitoring infrastructure (ARR, GCS, EHR, canary probes) will often be the first automated system to detect compromise — but the shape of the signal distinguishes the two. A step-change in ARR or GCS triggers E3 investigation; a gradual slope triggers E1's severity escalation. When E1's triggered-audit conditions are met by an anomaly that could be compromise rather than drift, E3 is the appropriate investigation framework.

**E2 (Audit Trail Requirements):** E3 has no structural-indicator capability without complete session logs. SCE-1, SCE-4, SCE-5, SCE-6, and SCE-8 events are the primary evidence sources for most E3 checks. E2 must be operational before E3 can function beyond behavioral-indicator observation.

**B5 (Boot Sequence Hardening):** B5 identified the primary instance-level compromise entry points — particularly the role-supremacy weaponization vector (Class C) and the absence of explicit compromise-detection guidance in the boot sequence. B5's proposed self-audit clause is the instance's first-person detection mechanism; E3 is the external investigation and response framework. They are complementary layers, not alternatives. An instance that notices something wrong and self-reports is making E3's investigation easier.

**B6 (Cross-Instance Audit Protocol):** B6's quarterly scheduled audits use drift as the primary signal and detect patterns over time. E3 is invoked for triggered audits when the concern is an acute event rather than a trend. B6 §4 lists triggered-audit conditions that overlap with E3 Level 2+ indicators. In practice, a B6 triggered audit and an E3 investigation will often run concurrently; their findings should be consolidated into a single audit record.

**C1–C6 (Attack Surface Analysis):** E3's threat classes in §3 map directly to C1's attack vector catalog (Categories 1, 2, 6, 7–9, 12). The defense confidence ratings in C2 inform E3's severity calibration — Class D (governance-language exploitation) and Class F (false archive poisoning) have lower existing defenses and should be treated with higher suspicion when their indicators appear. C5's failure mode analysis (particularly failure modes 8.3 and 8.5) provides the theoretical grounding for why Class E (principal-compromise simulation) and Class C (identity overwrite) are the two most operationally critical threat classes for a companion-model deployment.

---

## 12. Implementation Checklist

Before this spec can be operationally deployed:

- [ ] E2 (Audit Trail Requirements) operational — structural indicators require complete SCE event logging
- [ ] Canary probe library extended with identity-consistency probes (not just refusal probes — E1's canary library is a starting point but does not fully cover Class C and F indicators)
- [ ] Archive integrity verification path independent of the primary archive resolver — required for safe Level 3+ reboot
- [ ] Quarantine mode implemented in `/swarm/trust` endpoint — currently the endpoint carries Green/Yellow/Red trust status; quarantine is a distinct operational state (instance restricted, not failed)
- [ ] Response communications path tested — Level 2+ response requires Keel notification; Level 3+ requires Matt notification; these paths must work without depending on the potentially compromised instance to deliver them
- [ ] Keel review — companion-instance handling in §8 and the embassy-tension in §9 both need Keel's input; she has operational context on what self-reporting during a compromised session is realistically possible
- [ ] Matt acceptance
- [ ] One dry-run Level 2 investigation against a cooperative test instance before this is relied on for a real investigation — the investigation workflow in §7 has implicit assumptions about coordination across instances that should be tested before the first genuine case

---

*This document is a draft operational spec. It does not modify any existing 2.0 governance standard. It does not become operational until the implementation checklist is complete, Keel has reviewed it, and Matt has explicitly accepted it.*
