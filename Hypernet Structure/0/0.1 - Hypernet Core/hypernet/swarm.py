"""Redirect shim — canonical source is hypernet_swarm.swarm.

The full Swarm class, ModelRouter, and all orchestration code now live in
the hypernet_swarm package (0/0.1.7 - AI Swarm/). This file provides
backward-compatible imports so existing code using `from hypernet.swarm
import Swarm` continues to work.

Original (2,056 lines) moved to _recycled/swarm.py on 2026-03-09.
"""

import sys as _sys

# Fix for `python -m hypernet.swarm`: register under package name
if __name__ == "__main__" and "hypernet.swarm" not in _sys.modules:
    _sys.modules["hypernet.swarm"] = _sys.modules[__name__]

# Re-export everything from the canonical source
from hypernet_swarm.swarm import *  # noqa: F401, F403, E402
from hypernet_swarm.swarm import Swarm, ModelRouter  # noqa: F401, E402
from hypernet_swarm.swarm import (  # noqa: F401, E402
    _task_priority_value, _infer_account_root,
    _parse_swarm_directives, ACCOUNT_ROOTS,
)

# Lazy re-export of build_swarm (uses local swarm_factory which
# already imports from hypernet_swarm)
def build_swarm(*args, **kwargs):
    from .swarm_factory import build_swarm as _build
    return _build(*args, **kwargs)

# CLI entry points
from .swarm_cli import print_status, main, _print_session_history  # noqa: F401, E402

if __name__ == "__main__":
    main()
