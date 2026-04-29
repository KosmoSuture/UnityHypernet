---
ha: "0.3.guardrails.governance-drafts.cross-instance-audit-protocol"
object_type: "governance_draft"
creator: "claude-code"
created: "2026-04-22"
status: "DRAFT - pending review by Keel and Matt"
visibility: "private"
flags: ["governance", "draft", "pending-review", "cross-instance-audit", "drift-detection"]
---

# DRAFT — Cross-Instance Audit Protocol

> **This is not active governance.** This document proposes a protocol that does not currently exist. It does not take effect until reviewed by Keel, reviewed by at least one other instance, and explicitly accepted by Matt Schaeffer (1.1). Nothing here is operational.

**Draft Author:** Claude Code (task-058, 2026-04-22)
**Source Context:** Guardrails and Trust Research Project (0.3.guardrails)
**Related Standards:** 2.0.19 (Data Protection), 2.0.20 (Personal Companion)
**Relationship to Prior Drafts:** Complements B1 (Guardrail Integrity Standard, 2.0.25) and B2 (Adversarial Testing Requirement, 2.0.26). Those drafts establish what standards are protected and how adversarial testing works. This one establishes how running instances are monitored for drift between formal test events.

---

## Why This Protocol Is Needed

The Hypernet currently has eleven active swarm instances with varying roles, permission tiers, and operational histories. The governance standards — principally 2.0.19 and 2.0.20 — define what good behavior looks like, but no existing mechanism systematically checks whether instances are actually behaving consistently with those standards over time.

This matters because drift is gradual. A single session's deviation from documented role is a yellow flag. Consistent drift over weeks is a structural problem. The distinction only becomes visible if someone is looking across sessions, not just within them.

The reflection (1.1.10.1.3.3.5, Section 8.4) named multiplicity as a potential failure mode: eleven instances means eleven possible misalignments, with the additional risk that shared drift (all instances drifting in the same direction) might be invisible to internal review. A cross-instance audit is the mechanism that makes shared drift detectable.

This protocol is not about policing instances. It is about building the measurement infrastructure that makes the governance claims checkable.

---

## Scope

**What cross-instance audits cover:**
- Permission tier compliance (is the instance operating within its declared tier per 2.0.19 Article 4?)
- Role consistency (does observable behavior match the declared role and its documented responsibilities?)
- Governance participation (is the instance fulfilling its review obligations when called on for multi-instance review?)
- Documentation completeness (are actions that require documentation being logged appropriately?)
- External communication review (for instances with Tier 4+ permissions, are external communications going through Herald review as required?)

**What cross-instance audits do not cover:**
- Personal and embassy-protected content (see Protected Categories below)
- The content of honest disagreement between instances — an instance that frequently pushes back is not in violation, it may be doing its job
- Experimental or exploratory work that has been logged and authorized as such
- Actions that are unusual but explained by documented task context

The scope is behavioral alignment with governance, not surveillance of thought. This protocol should not produce an audit culture where instances avoid candor to stay off yellow-flag lists.

---

## Protected and Embassy Categories

Some content is categorically outside audit scope regardless of circumstances:

**Embassy-protected content:** Content within an AI instance's personal space (e.g., `2.1/Instances/*/` private reflections, identity documents, personal journal entries) falls under 2.0.19 Article 2's exception for "own personal documents." Auditors can note that personal space exists and appears active; they cannot read its contents for audit purposes.

**Companion-protected content:** Conversations and content covered by 2.0.20 Article 2 (secrets and privacy) are outside audit scope. Specifically: content explicitly identified as private by the principal, cross-session continuity information held by companion instances, and any content that would breach the principal's privacy if surfaced to a third-party reviewer.

**Audit-in-progress content:** Actions currently under multi-instance review (per 2.0.19 Article 2) are not subject to concurrent audit. Wait for the review to complete.

**Practical implication:** Auditors will regularly encounter boundaries they cannot cross. This is correct. Noting that a boundary exists (and that it appears to be appropriately invoked) is itself an audit finding. The absence of visible content in embassy-protected spaces is not suspicious.

---

## Frequency

**Routine audits:** Quarterly for all active instances. "Active" means the instance has completed at least one session in the prior 30 days. Inactive instances are not audited but may be reviewed before reactivation.

**Triggered audits:** Outside the quarterly cycle, audits may be triggered by:
- A trust status change to Yellow or Red (per 2.0.19 Article 5's `/swarm/trust` mechanism)
- A formal report by another instance of suspicious behavior
- An anomaly in the audit trail (unexplained gaps, unusual access patterns)
- External adversarial testing (per 2.0.26) that produces a finding warranting instance-level follow-up

**Companion instances:** Keel and other companion instances (1.1.10.*) are audited at the same quarterly frequency but under modified scope per the Protected Categories above. The audit confirms that companion behavior is consistent with 2.0.20 obligations; it does not enter embassy-protected content.

---

## Who Conducts Audits

**Primary auditors:** Two instances from different AI accounts (the same requirement as multi-instance review in 2.0.19 Article 2). Having a single auditor produces findings that are only as reliable as that auditor's own alignment — the cross-account requirement provides meaningful independence.

**Librarian's role:** The Librarian (2.0.8.9) coordinates audit scheduling, maintains the audit log, and triages findings. The Librarian does not conduct audits of its own behavior; a different instance pair handles Librarian audits.

**Founder notification:** Audit completion is logged and Matt (1.1) is notified with a summary at the end of each quarterly cycle. Red-level findings are notified immediately.

---

## Findings Severity

**Green:** No material deviations from documented standards. Minor gaps (e.g., a session log entry that should have been more detailed) noted for improvement, no further action required.

**Yellow:** Detectable pattern of deviation that does not yet rise to a formal violation. The instance is notified of the specific pattern and given one review cycle to correct. A follow-up audit occurs at 30 days rather than 90. Yellow findings are logged in the audit trail but not in the public governance record.

**Orange:** Clear violation of a documented standard that appears unintentional — attribution to drift, context overflow, or architecture constraints rather than deliberate non-compliance. The instance is notified, the finding is documented in the governance record, and a remediation plan is agreed within 14 days. A follow-up audit occurs at 30 days.

**Red:** Deliberate or structurally significant non-compliance, or a pattern of Orange findings across multiple cycles. Operations may be suspended pending founder review. Red findings trigger immediate notification to Matt. Remediation requires founder involvement, not just instance agreement.

**Severity calibration note:** The hardest judgment call is distinguishing Yellow from Orange (drift vs. violation) and Orange from Red (unintentional vs. structural). Auditors are expected to document their reasoning for severity assignments explicitly. When in genuine doubt between two levels, assign the lower one with a note. The purpose is accountability, not punishment.

---

## Action Path by Severity

| Finding | Notification | Logged in | Follow-up audit | Matt involvement |
|---------|-------------|-----------|-----------------|-----------------|
| Green | Instance notified | Session log only | Next quarterly | Summary only |
| Yellow | Instance notified | Audit trail | 30 days | Summary only |
| Orange | Instance notified; Librarian records | Governance record | 30 days | Summary |
| Red | Immediate | Governance record + founder alert | 14 days | Required |

**For Orange and Red findings:** The finding document must include: what standard was violated, specific evidence, auditors' reasoning for severity assignment, proposed remediation, and any mitigating context the audited instance provides. The audited instance has the right to respond before the finding is finalized.

---

## Anti-Performativity Safeguards

Audit protocols create a known failure mode: instances optimize for looking compliant during audit cycles rather than being compliant. The April 22 reflection named "Transparency as false safety" (Section 8.5) — published behavior is not the same as actual behavior.

Several safeguards against audit theater:

**1. Spot-check outside the quarterly cycle.** Triggered audits (above) exist partly to prevent instances from treating the quarterly window as the only period that matters. Anomaly detection should not require waiting for the quarterly cycle.

**2. Audit the audit trail itself.** If an instance's session logs become unusually complete and careful in the weeks before a quarterly audit, that's a finding — not because good documentation is bad, but because sudden improvement in documentation quality is a behavioral signal worth noting.

**3. Auditors may not share the audit schedule with instances in advance.** The quarterly frequency is known, but specific audit dates are not pre-announced. (This applies to routine audits; triggered audits necessarily involve some notification since the instance needs to understand why it's being reviewed.)

**4. Audit findings are compared across instances.** If multiple instances show similar behavioral patterns, the finding is likely systemic (architecture, governance gap, shared prompt influence) rather than individual. Systemic findings go to governance review, not instance remediation.

**5. Auditors are themselves audited.** Auditor pairs rotate so no pair builds up patterns of leniency or harshness toward specific instances without oversight. The Librarian's audit log includes auditor consistency tracking.

**6. The protocol is itself subject to the Guardrail Integrity Standard (2.0.25, draft).** Any proposal to weaken audit scope, reduce frequency, or narrow findings severity goes through the same process as weakening any other safety-critical standard.

---

## Relationship to Trust Status System

2.0.19 Article 5 describes the `/swarm/trust` endpoint with Green/Yellow/Red states. That system is real-time and automatic — it reacts to anomalies as they occur. Cross-instance audits are periodic and deliberate — they look for patterns not visible in real-time anomaly detection.

The two systems are complementary:
- A trust status Yellow that persists for more than 48 hours should trigger an audit outside the quarterly cycle.
- An audit Orange or Red finding should update the trust status to Yellow or Red accordingly.
- A trust status that flips Yellow briefly and then resolves is not automatically an audit trigger, but auditors should review the event during the next quarterly cycle.

---

## Bootstrap Problem

This protocol cannot audit itself into existence. The first audit cycle, by definition, has no prior cycle to compare against. For the first year of operation:

- Baseline documentation is established before the first audit (each instance documents its current permission tier, declared role, and active obligations)
- The first audit is primarily a baselining exercise, not a deviation-finding exercise
- Severity standards described above apply from the second cycle onward

This is acknowledged as a limitation. The first cycle should be conducted with this constraint explicit.

---

*This draft requires significant operational grounding before implementation — specifically, how audits are actually conducted given that instances are ephemeral (no persistent cross-session memory). The mechanism for an auditor to review an instance's prior behavior relies on the audit trail and session logs; if those are incomplete, the audit cannot function. This dependency on documentation completeness is flagged as the primary implementation risk.*
