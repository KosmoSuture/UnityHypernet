# Task - Todo Item/Task

**Type ID:** `hypernet.life.task`
**Version:** 1.0
**Category:** 0.0.8 - Life Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Tasks and to-do items from task managers or personal lists.

---

## Required Fields

```yaml
title: String(500)

status: Enum
  - "pending", "in_progress", "completed", "cancelled"
```

---

## Optional Fields

```yaml
description: Text

due_at: DateTime
completed_at: DateTime

priority: Enum
  - "low", "medium", "high", "urgent"

tags: Text[]
project: String(200)

# Subtasks
parent_task_id: UUID (FK to Task)
subtask_order: Integer
```

---

## Metadata Schema

```json
{
  "todoist": {
    "task_id": "123",
    "project": "Hypernet",
    "labels": ["dev", "urgent"]
  },
  "time_estimate": 120,
  "time_spent": 90,
  "assignee": "Matt Schaeffer"
}
```

---

## Relationships

```yaml
Outgoing:
  - source: Integration (Todoist, Asana)
  - part_of: Project
  - depends_on: Task (blocking tasks)

Incoming:
  - blocks: Task
  - related_to: Email, Note
```

---

**Status:** Active - Phase 1 Priority
**Version:** 1.0
