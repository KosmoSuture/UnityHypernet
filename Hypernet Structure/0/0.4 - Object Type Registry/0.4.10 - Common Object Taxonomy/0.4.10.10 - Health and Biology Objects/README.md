---
ha: "0.4.10.10"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# 0.4.10.10 - Health and Biology Objects

Biological, medical, wellness, and environmental records.

## Object Types

| Address | Type | Purpose |
|---|---|---|
| `0.4.10.10.1` | Biological Entity | An organism, sample, species, or biological unit. |
| `0.4.10.10.2` | Health Profile | A consent-scoped person health profile. |
| `0.4.10.10.3` | Medical Record | A clinical record, visit note, diagnosis, or health document. |
| `0.4.10.10.4` | Medication | A prescribed or consumed drug, supplement, or treatment. |
| `0.4.10.10.5` | Lab Result | A laboratory test result with method, units, and reference range. |
| `0.4.10.10.6` | Symptom | A reported or observed health symptom. |
| `0.4.10.10.7` | Procedure | A medical, biological, or care procedure. |
| `0.4.10.10.8` | Care Plan | A treatment or wellness plan with goals and interventions. |
| `0.4.10.10.9` | Food Item | A consumable item, ingredient, meal, or nutrition record. |
| `0.4.10.10.10` | Environmental Reading | A measurement of environmental context affecting people or systems. |

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
