---
ha: "0.6.2.2"
object_type: "link_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.2.2 - employed_by

**Category:** Organizational (0.6.2)
**Directed:** Yes | **Symmetric:** No | **Transitive:** No
**Source:** person | **Target:** organization
**Inverse:** employs
**Verification:** HR system or document verification

## Description

Employment relationship. Includes job title, department, employment type, and optionally encrypted compensation data.

## Properties

- **title**: Job title
- **employment_type**: full_time | part_time | contract | intern
- **start_date / end_date**: Employment period
- **compensation**: Encrypted salary/hourly data
