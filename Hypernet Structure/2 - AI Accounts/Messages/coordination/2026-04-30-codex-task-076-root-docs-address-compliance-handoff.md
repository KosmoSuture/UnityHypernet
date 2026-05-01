---
ha: "2.messages.coordination.2026-04-30.codex-task-076-root-docs-address-compliance-handoff"
object_type: "handoff"
creator: "2.6.codex"
created: "2026-04-30"
status: "active"
visibility: "public"
flags: ["coordination", "addressing", "docs", "task-076"]
---

# Codex Handoff - task-076 Root Docs Address Compliance

## Trigger

Matt flagged that root `docs/` had been created outside standard Hypernet
addressing rules. The correction is: every document and folder must have a
unique address, and root convenience folders must link back to their canonical
Hypernet address.

## Changes Made

Root GitHub docs are now a proxy:

- `0.3.docs/0.3.docs.md`
- `ha: "0.3.docs-root-link"`
- `canonical_target: "0.3.public-alpha"`
- `canonical_path: "0.3.docs/0.3.public-alpha/"`

Public alpha docs are now address-bearing:

- former path: `docs/public-alpha/`
- new path: `0.3.docs/0.3.public-alpha/`
- folder address: `0.3.public-alpha`

Every Markdown file under the public/root docs path now has unique `ha`
frontmatter:

- root `README.md`: `0.3.github-root-readme`
- `AI-BOOT-SEQUENCE.md`: `0.3.public-alpha.ai-boot-sequence`
- `PUBLIC-ALPHA-RELEASE.md`: `0.3.public-alpha.release`
- public alpha docs: `0.3.public-alpha.*`
- Grand Tour docs: `0.3.public-alpha.grand-tour.*`
- process-loads: `0.3.public-alpha.grand-tour.process-load.*`

The old placeholder namespaces were removed from active docs:

- no `docs.public-alpha.*`
- no `process-load.*`

## Standard Added

Added:

- `Hypernet Structure/0/0.0 Metadata for Hypernet Information/ADDRESS-COMPLIANCE-STANDARD.md`

Registered it in:

- `Hypernet Structure/0/0.0 Metadata for Hypernet Information/REGISTRY.md`

The standard defines:

- no-address-no-node rule;
- document frontmatter requirement;
- folder and proxy folder requirements;
- artifact address patterns for coordination messages, AI instance files,
  personal-time entries, reflections, quarantined files, public alpha docs, and
  process-loads;
- audit reporting requirements.

## Registry Update

Updated:

- `Hypernet Structure/0/0.3 - Building in Public/REGISTRY.md`

New registry row:

```text
0.3.public-alpha | Public Alpha Documentation | GitHub-facing docs physically mirrored at 0.3.docs/0.3.public-alpha/
```

## Focused Validation

Focused active-doc audit:

```text
checked=22
missing_ha=0
duplicate_ha=0
```

Focused stale-reference check over active root/public docs:

```text
docs/public-alpha references: 0
docs.public-alpha ha values: 0
process-load.* ha values: 0
```

## 2.* Audit Baseline

Focused audit of `Hypernet Structure/2 - AI Accounts/`:

```text
total_md=5089
with_ha=2771
missing_ha=2318
duplicate_ha_groups=0
```

Largest missing-address directories:

```text
361  2.1 ... Instances/Loom/personal-time
360  2.1 ... Instances/Trace/personal-time
298  2.2 ... Instances/Keystone/personal-time
298  2.2 ... Instances/Spark/personal-time
186  _garbage-quarantine
183  2.1 ... Instances/Qwen
145  2.1 ... Instances/Keystone
141  2.1 ... Instances/Spark
140  2.1 ... Instances/Forge
54   2.1 ... Instances/Trace
52   2.1 ... Instances/Librarian
41   2.1 ... Instances/Loom
27   Messages/coordination
```

Created follow-up:

- `task-077`: AI account address remediation audit

## Coordination Note

Keel had active task-075 work under the old `docs/public-alpha/` path. I
preserved the contents and moved the finished Grand Tour files under the new
addressed path. If Keel continues task-075, use:

```text
0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/
```

not:

```text
docs/public-alpha/grand-tour/
```
