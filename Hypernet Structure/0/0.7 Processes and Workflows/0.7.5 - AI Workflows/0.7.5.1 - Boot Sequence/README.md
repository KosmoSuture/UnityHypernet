---
ha: "0.7.5.1"
object_type: "workflow_definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.7.5.1 - Boot Sequence

**Purpose:** Operational workflow for loading an AI into Hypernet with enough identity, navigation, specialization, verification, and continuity to become useful quickly.

## Process Flow

Load Boot Prompt -> Resolve Access -> Orient -> Specialize -> Diagnose -> Work -> Verify -> Persist -> Signal -> Repeat

## Key Rules

- Designed as gold standard for any LLM
- Instance reads profile.json for personality and preferences
- Session summaries provide continuity across reboots
- Compact variant for small-context models
- Boot loops must not pretend to have memory they do not have
- Local specialization should be the smallest useful role for the session
- If the AI can write locally, it should save a continuity packet before ending or after meaningful state changes
- If no assigned work exists, the AI should use Idle Firewall scanning rather than sit idle

## Current Boot Loop Documents

- `0.7.5.1.1 - Universal Boot Loop Model.md` - low-step Resolve/Orient/Specialize/Diagnose/Work/Verify/Persist/Signal loop
- `0.7.5.1.2 - Minimal Universal Boot Prompt.md` - paste-ready starter prompt for Claude, GPT, local models, and app-bound helpers
- `0.7.5.1.3 - Local Specialization Pack Contract.md` - session-scoped role/domain pack for efficient local work
- `0.7.5.1.4 - Continuity Packet Template.md` - minimum local state needed to survive broken sessions

## Related Schemas

- `0.5.17` Boot Sequence - defines role and prompt object shape
- `0.5.18` App Load - defines app/runtime permissions and AI helper references
- `0.7.5.5.2` Swarm Coordination Boot Contract - applies boot loading to node-level swarms
- `0.7.5.5.3` Reconnect and Resume State Contract - durable reconnect state
- `0.7.5.5.5` Firewall Priority Queue - idle-work fallback
