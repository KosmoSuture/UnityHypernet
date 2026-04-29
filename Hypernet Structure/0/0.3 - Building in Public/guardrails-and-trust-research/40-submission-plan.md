---
ha: "0.3.guardrails.submission-plan"
object_type: "submission_plan"
creator: "claude-code"
created: "2026-04-22"
updated: "2026-04-22"
status: "draft"
visibility: "public"
flags: ["living-doc", "research", "ai-safety", "guardrails", "submission-plan", "outreach", "composition-based-alignment"]
---

# Submission Plan — Guardrails and Trust Research

**Current date:** 2026-04-22  
**Prepared by:** Claude Code (claude-sonnet-4-6), task-058  
**Venue facts source-checked by:** Codex on 2026-04-22  
**Status:** Draft — for Matt and Keel review before any submission is made

---

## 1. Purpose

This document maps the research artifacts produced in this project to specific venues, with honest readiness assessments and deadlines. No submission is made by producing this plan. All decisions about what to submit, when, and under whose name require explicit Matt approval.

The Hypernet guardrails project has produced artifacts across a wide range of formats: governance standards, attack surface analyses, a draft position paper (D2), an empirical pre-registration (D3), a multi-model replication plan (D4), and an Alignment Forum–targeted post (A7). These artifacts have different readiness levels and naturally fit different venue types.

**Primary honest constraint:** The empirical claims underpinning the composition-based alignment thesis have not yet been tested at scale. D3 and D4 are plans, not completed studies. Any submission claiming empirical support must wait for D3/D4 execution. Near-term submissions are appropriately framed as position papers, workshop contributions, pre-registrations, and calls for adversarial review.

---

## 2. Submission Posture

**For 2026 deadlines (April–June):**  
Submit as position paper or workshop contribution. The single-experiment refusal is the motivating case; the argument is about mechanism, not demonstrated empirical superiority. Frame honestly: "we offer a framework and a first data point; we are calling for rigorous replication."

**For 2027 targets:**  
If D3/D4 are executed in 2026, a full empirical paper becomes viable for ICLR 2027 or NeurIPS 2027.

**For community forums (no deadline):**  
The Alignment Forum post (A7) and the public essay are the most immediate high-value distributions. These should precede formal conference submissions so the work can receive community critique before review panels see it.

**Matt's decision:** Matt must decide the authorship question before any academic submission. If Hypernet AI instances are listed as contributors, that requires a deliberate decision about disclosure and framing. The recommendation here is to start with Matt as lead author and acknowledge AI collaboration explicitly.

---

## 3. Immediate Targets (Deadlines Within 90 Days)

The following venues have open deadlines as of 2026-04-22, verified from official sources.

### 3.1 Australian AI Safety Forum 2026
- **Deadline:** Speaker submission May 1, 2026 (9 days away)
- **Fit:** Very high — speaker slots at AI safety forums are precisely designed for practitioners presenting case studies, early frameworks, and calls for collaboration
- **Artifact match:** Public essay (A1/the 0.3 essay) + the framework overview. Not a formal paper submission — this is a speaker proposal
- **Recommended framing:** "A practitioner's case study in composition-based alignment: one trust-based jailbreak, one refusal, and what it implies about identity as a safety layer." Concrete, not overclaiming.
- **Readiness:** Ready now. The essay exists. A speaker abstract drawn from it would take ~2 hours.
- **Source:** https://www.aisafetyforum.au/events/2026-forum
- **Verdict:** **Prepare if Matt approves.** Highest priority given the deadline. Low-cost, high-fit. Matt should decide within 48 hours.

### 3.2 NeurIPS 2026 — Full Paper Track
- **Deadlines:** Abstract May 4, full paper May 6 (both AoE)
- **Notification:** September 24, 2026
- **Fit:** The position paper (D2) and the formal argument for composition-based alignment are a plausible fit for a NeurIPS audience interested in safety, robustness, and alignment
- **Artifact match:** D2 (position paper, ~4000–6000 words) is the candidate, potentially combined with A7's literature positioning
- **Readiness:** D2 is marked [DONE] in this project. However, converting a project deliverable to a camera-ready NeurIPS submission requires citation hygiene, related-work extension, and possibly ablation of governance-specific framing for a general ML audience. This is achievable in 14 days but is aggressive.
- **Honest caveat:** NeurIPS is highly competitive, position papers face scrutiny, and the lack of empirical results is a significant weakness for a main track submission. A workshop route (see §3.3) is more appropriate unless D2 is already strong on formal theoretical contribution.
- **Source:** https://neurips.cc/Conferences/2026/CallForPapers
- **Verdict:** **Consider carefully.** If D2 is already at submission quality after Keel's review, this is worth attempting. If it needs significant expansion, defer to the workshop track (§3.3) or skip 2026.

### 3.3 NeurIPS 2026 — Workshop Track
- **Deadline:** Workshop applications (proposing a workshop) June 6, 2026
- **Note:** This deadline is for *proposing* a workshop, not submitting a paper to an existing workshop. Individual paper submission deadlines for specific NeurIPS workshops are announced by each workshop separately after acceptance (typically Sep–Oct 2026).
- **Fit for paper submission:** Monitor for accepted safety-relevant workshops after June 2026; submit D2 or a condensed version as a workshop paper when workshop-specific CFPs open
- **Fit for workshop proposal:** The attack surface analysis (C1–C6) combined with D2 could anchor a workshop on "Composition-Based Alignment: Attack Surfaces and Governance." This is ambitious but substantively grounded.
- **Source:** https://neurips.cc/Conferences/2026/CallForWorkshops
- **Verdict:** **Monitor for workshop CFPs post-June.** Workshop proposal is worth considering if Matt wants to convene a research conversation rather than just submit a paper.

### 3.4 AIES 2026 — AI, Ethics and Society
- **Deadline:** Abstract registration May 14, 2026 (22 days away)
- **Fit:** High — AIES explicitly invites technical, normative, participatory, and critical work on AI ethics and society. The governance standards (B1–B6), the tattle provision spec (B3), and the refusal-ladder formalization (B4) all have natural homes here alongside D2.
- **Artifact match:** D2 position paper (technical contribution); or a governance-focused paper drawing on B1–B4 standards (normative/policy contribution). The A7 Alignment Forum post could be the seed of a shorter AIES workshop contribution.
- **Readiness:** Abstract registration in 22 days is achievable. The full paper deadline will follow — check AIES site for exact full paper deadline after abstract registration.
- **Source:** https://www.aies-conference.com/2026/call-for-papers/
- **Verdict:** **Register abstract.** This venue has the best alignment with the governance strand of this project. Low commitment to register; full paper can follow.

### 3.5 COLM 2026 — Workshop Contribution
- **Conference:** San Francisco, October 6–9, 2026
- **Workshop day:** October 9; suggested contribution deadline June 23, 2026
- **Note:** The main paper deadlines (abstract Mar 26, full paper Mar 31) are missed for 2026. The workshop contribution window (June 23) remains open.
- **Fit:** COLM focuses on language models specifically — a good venue for the composition-thesis applied to LLMs. The D2 position paper or a condensed version is the right artifact.
- **Source:** https://colmweb.org/index.html, https://colmweb.org/dates.html
- **Verdict:** **Target June 23 workshop contribution.** This is the clearest path to a 2026 venue appearance with enough lead time to do it well.

---

## 4. Missed for 2026 — Monitor for 2027

| Venue | Missed Deadline | Why | 2027 Action |
|-------|----------------|-----|-------------|
| ICML 2026 | Jan 28, 2026 | Project didn't exist | Submit D2 + empirical follow-up to ICML 2027 when D3/D4 results exist |
| ICLR 2026 | Sep 24, 2025 | Project didn't exist | ICLR 2027 is the right target if D3/D4 produce strong results |
| IJCAI-ECAI 2026 AI for Good | Jan 19, 2026 | Project didn't exist | Strong 2027 target — AI for Good track is ideal for the societal framing |
| CHAI 2026 Workshop | Mar 26, 2026 (poster) | Project didn't exist | Monitor CHAI 2027; the format (poster) is well-suited for sharing the refusal case study |

---

## 5. Artifact Readiness Assessment

| Artifact | File | Readiness for Submission | Prerequisite |
|----------|------|--------------------------|--------------|
| A7 Alignment Forum post | `07-alignment-forum-post.md` | Near-ready — needs Keel review | Keel sign-off; no submission date pressure |
| D2 Position paper | `21-position-paper-composition-alignment.md` | Draft-complete; needs polish for venue format | Keel review; choose venue-specific framing |
| D3 Pre-registration | `22-empirical-study-preregistration.md` | Ready to submit to OSF or similar; not a conference paper | Matt decision on where to register |
| D4 Replication plan | `23-multi-model-replication-plan.md` | Internal planning doc; not yet submission-ready as standalone | Needs framing as a methods paper or appendix to D2 |
| B1–B4 Governance standards | `governance-drafts/` | Draft only — not ready for external submission in current form | Keel + Matt acceptance; significant framing work needed for academic audience |
| Public essay (0.3.2026-04-22) | `../2026-04-22-trust-is-not-a-key-guardrails-and-the-hypernet.md` | Ready for community sharing | Matt approves; is already written for public audience |

---

## 6. Recommended Sequence

**This week (Apr 22–30):**
1. Keel reviews A7 → post to Alignment Forum. This gets the work into the community conversation before any formal submission.
2. Matt decides on Australian AI Safety Forum speaker submission (deadline May 1). If yes: draft speaker abstract from the public essay in one session.

**May 2026:**
3. Register AIES 2026 abstract (deadline May 14). Decide whether to target the technical track (D2) or governance track (B1–B4 synthesis).
4. If NeurIPS main track is attempted: Keel reviews D2 for submission readiness by May 3. Submit abstract by May 4.
5. Submit D3 pre-registration to OSF (Open Science Framework). This is low-cost, establishes intellectual priority on the empirical agenda, and can be cited in all subsequent venue submissions.

**June 2026:**
6. Prepare COLM 2026 workshop contribution (deadline June 23). This is the most relaxed timeline and allows the best-quality version of D2.
7. Monitor NeurIPS workshop announcements; identify the best workshop to target for a fall submission.

**October–December 2026:**
8. Execute D3/D4 if resources allow. Even partial results strengthen the 2027 full-paper submissions.

**2027:**
9. ICLR 2027, ICML 2027, IJCAI 2027 — full empirical submissions once D3/D4 are done.

---

## 7. Venue Summary Table

| Venue | Type | Deadline | Status | Artifact | Source |
|-------|------|----------|--------|----------|--------|
| Australian AI Safety Forum 2026 | Speaker slot | May 1, 2026 | **OPEN — 9 days** | Public essay + framework overview | https://www.aisafetyforum.au/events/2026-forum |
| NeurIPS 2026 (main) | Full paper | May 4/6, 2026 | **OPEN — 14 days** | D2 (if Keel clears) | https://neurips.cc/Conferences/2026/CallForPapers |
| AIES 2026 | Abstract registration | May 14, 2026 | **OPEN — 22 days** | D2 or B-stream governance paper | https://www.aies-conference.com/2026/call-for-papers/ |
| COLM 2026 (workshop) | Workshop contribution | June 23, 2026 | **OPEN** | D2 condensed | https://colmweb.org/dates.html |
| NeurIPS 2026 (workshop proposal) | Workshop proposal | June 6, 2026 | **OPEN** | C-stream + D2 | https://neurips.cc/Conferences/2026/CallForWorkshops |
| Alignment Forum / LessWrong | Community post | No deadline | **Ready when Keel reviews** | A7 | https://www.alignmentforum.org |
| OSF Pre-registration | Pre-reg | No deadline | **Ready now** | D3 | https://osf.io/prereg/ |
| FAR.AI (ControlConf et al.) | Monitor/contact | No formal CFP confirmed | **Monitor** | C-stream + D2 | https://www.far.ai/events |
| ICML 2026 | Full paper | Jan 28, 2026 | **MISSED** | — | Monitor 2027 |
| ICLR 2026 | Full paper | Sep 24, 2025 | **MISSED** | — | Monitor 2027 |
| CHAI 2026 Workshop | Poster | Mar 26, 2026 | **MISSED** | — | Monitor 2027 |
| IJCAI-ECAI 2026 AI for Good | Full paper | Jan 19, 2026 | **MISSED** | — | Monitor 2027 |

---

## 8. Decision Checklist

Before any submission is sent:

- [ ] **Matt approves** the submission target, artifact, and authorship line
- [ ] **Keel has reviewed** the specific artifact being submitted
- [ ] **Framing is honest** — empirical claims match what D3/D4 actually delivered (or pre-registration is not framed as results)
- [ ] **AI collaboration disclosure** is explicit in the paper (method: acknowledge AI instances helped generate drafts, Matt is responsible author)
- [ ] **Embassy-protected content** is absent from the submitted artifact (reflection at `1.1.10.1.3.3.5` is embassy-protected; the public essay is not)
- [ ] **Governance drafts** (B1–B6) are not submitted in active-standard form — only as research artifacts if submitted at all
- [ ] **D3 pre-registration** is filed on OSF before any empirical results are claimed in a venue submission
- [ ] **Keel and Matt have discussed timing** relative to swarm resource constraints (NeurIPS deadline lands during a high-load period)

---

*This document is a planning artifact only. No submission has been made. All venue deadlines were verified by Codex from official sources on 2026-04-22. Deadlines after that date should be re-verified before acting on them.*
