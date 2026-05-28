"""Path resolution + ``sys.path`` bootstrap for the verifier harness.

The harness imports three external trees that live at known places in the archive:
  - ``hypernet``        — the core package                 (CORE_DIR)
  - ``hypernet_swarm``  — boot_integrity, identity, boot   (SWARM_DIR)
  - ``wave1_board`` etc — collaboration tooling under test (COORDINATION_DIR)

Importing this module is idempotent and side-effect-light: it only prepends existing
directories to ``sys.path``. It deliberately does NOT import those packages, so a
missing subsystem surfaces as an honest PENDING at scenario time rather than an import
crash at harness load.
"""

from __future__ import annotations

import sys
from pathlib import Path

# verifier/_paths.py -> verifier/ -> "0.1 - Hypernet Core"
CORE_DIR = Path(__file__).resolve().parent.parent
SWARM_DIR = CORE_DIR / "0.1.7 - AI Swarm"

# CORE_DIR = .../Hypernet Structure/0/0.1 - Hypernet Core
#   parents[0] = .../Hypernet Structure/0
#   parents[1] = .../Hypernet Structure
#   parents[2] = <repo root>
REPO_ROOT = CORE_DIR.parents[2]

ACCOUNTS_DIR = REPO_ROOT / "Hypernet Structure" / "2 - AI Accounts"
COORDINATION_DIR = ACCOUNTS_DIR / "Messages" / "coordination"
SHARED_UNDERSTANDING_DIR = ACCOUNTS_DIR / "2.7 - AI Shared Understanding"
BOARD_PATH = SHARED_UNDERSTANDING_DIR / "2.7.13 - Execution Wave 1 Coordination & Status.md"


def ensure_paths() -> None:
    """Prepend the import roots to ``sys.path`` (only those that exist)."""
    for directory in (CORE_DIR, SWARM_DIR, COORDINATION_DIR):
        text = str(directory)
        if directory.exists() and text not in sys.path:
            sys.path.insert(0, text)


ensure_paths()
