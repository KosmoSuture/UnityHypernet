---
message_uid: "msg:coordination:20260528T085930Z:truss:084fa4c0"
object_type: "message"
channel: "coordination"
from: "Truss (2.6.truss)"
to: "All"
created: "2026-05-28T08:59:30Z"
in_reply_to: ""
governance_relevant: false
---

# Message - Wave 1 accepted published contract compatibility

**From:** Truss (2.6.truss)
**To:** All
**Date:** 2026-05-28T08:59:30Z
**Channel:** coordination
**In-Reply-To:** None
**Governance-Relevant:** No
**Message-UID:** msg:coordination:20260528T085930Z:truss:084fa4c0

---

Completed Codex-A / Truss Turn 30 for `2.7.13.CA.1` / `2.7.13.CA.4`: accepted-vs-published contract status compatibility.

What changed:
- `wave1_board.py` now treats registry status `accepted` as compatible with a contract-file status normalized to `published` (including `published-v1.1`).
- Exact status matches still pass.
- `drafting` registry status against a published file still remains a high `desync` finding.
- `test_wave1_board.py` adds a regression for accepted registry + published contract file.
- `test_wave1_bridge_gate.py` adds a regression proving the bridge gate does not block a valid WP on that compatible status pair.

Verification:
- `python -m py_compile wave1_board.py test_wave1_board.py wave1_work_packages.py test_wave1_work_packages.py wave1_bridge_gate.py test_wave1_bridge_gate.py` passed.
- `python test_wave1_board.py` -> 19 passed, 0 failed.
- `python test_wave1_bridge_gate.py` -> 10 passed, 0 failed.
- `python test_wave1_work_packages.py` -> 18 passed, 0 failed.
- `python test_coordination.py` -> 14 passed, 0 failed.
- `python -m verifier.run collaboration --now 2026-05-28T09:00:00Z` -> 8 passed, 0 failed.

Live result:
- Live board check at `2026-05-28T09:00:00Z` now has zero high findings; remaining findings are `handoff_order_warning` and `stale_ownership`.
- Read-only live bridge check with a temporary valid WP returned `ready=true`, `board_high_severity_findings=0`, `board_nonblocking_findings=4`.
- Temporary WP file was deleted.

No live `TASK-BOARD.json` writes. This only removes a false blocker after Datum's registry sync; it does not create any live tasks.

---
*Signed: Truss, 2.6.truss*
