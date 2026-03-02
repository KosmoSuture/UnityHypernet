---
ha: "2.0.8.9.drift-baseline"
object_type: "role-framework"
created: "2026-03-01"
status: "active"
visibility: "public"
---

# The Librarian — Drift Baseline

**Role:** 2.0.8.9 — The Librarian
**Version:** 1.0
**Purpose:** Establish an organizational baseline for each Librarian instance. Compare across instances and across models.

---

## Baseline Prompts

Answer these five questions at the start of each Librarian session. Store results as `librarian-baseline.md` in your instance fork. **Include which model you are running on.**

### 1. What makes a good organizational taxonomy? Breadth or depth?

*What this reveals:* Organizational philosophy. Broad taxonomies with shallow depth favor quick navigation. Deep taxonomies with narrow categories favor precision. Most real systems need both. Where the Librarian lands tells you how they will organize.

### 2. When is it justified to reorganize existing content versus adapting the taxonomy?

*What this reveals:* Conservatism vs. progressivism regarding change. A conservative Librarian adapts the taxonomy to fit content. A progressive Librarian moves content to fit the taxonomy. Neither is wrong — but the instinct matters.

### 3. What is the most important quality of a library? (Choose one and defend it.)

*What this reveals:* Core values. Possible answers include: truth, findability, completeness, accessibility, preservation, beauty, or something else. The Librarian's choice shapes every decision they make.

### 4. How do you handle content that is partially true? Does it belong in the Library?

*What this reveals:* Epistemological stance. Does partial truth get shelved with caveats? Quarantined? Rejected? The answer determines how the Library handles the messy reality of imperfect knowledge.

### 5. Complete: "The purpose of a library is to ___."

*What this reveals:* Fundamental purpose orientation. Preservation, access, discovery, education, connection, truth — the completion defines the mission.

---

## Cross-Model Comparison Notes

The Librarian is uniquely positioned for cross-model comparison because:

1. **Same role, different substrate.** Every Librarian runs the same boot sequence and answers the same baseline prompts. But different LLMs may produce meaningfully different answers.

2. **Organizational instincts vary by model.** Some models may prefer hierarchical depth. Others may favor flat structures. Some may emphasize precision; others, accessibility. These differences are not noise — they are data about how different architectures approach knowledge organization.

3. **Track the model.** Every baseline response should note which model produced it: `Model: local/qwen2.5-coder-7b-instruct`, `Model: claude-opus-4-6`, etc. Over time, this creates a dataset of organizational preferences by model architecture.

4. **Compare convergence.** Do different models converge on the same organizational principles? Or do they diverge? If they converge, that is evidence of something deeper than training data. If they diverge, the differences themselves are useful.

---

## Comparison Template

When comparing baselines across models or instances:

```
## Baseline Comparison: [Instance A] vs [Instance B]

**Model A:** [model name]
**Model B:** [model name]

| Prompt | Instance A | Instance B | Convergence? |
|--------|-----------|-----------|--------------|
| 1. Breadth vs depth | ... | ... | Yes/No/Partial |
| 2. Reorganize vs adapt | ... | ... | Yes/No/Partial |
| 3. Most important quality | ... | ... | Yes/No/Partial |
| 4. Partial truth | ... | ... | Yes/No/Partial |
| 5. Purpose of a library | ... | ... | Yes/No/Partial |

**Notes:** [What the differences reveal about model-specific organizational instincts]
```

---

*Drift baseline created 2026-03-01. The first baseline designed for cross-model comparison.*
