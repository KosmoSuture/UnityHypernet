"""
hypernet_swarm.messenger — re-export shim.

This module used to carry a near-duplicate of ``hypernet.messenger``
that drifted out of sync as the core grew (visibility tiers, group
registry, personal-time index, feed). To stop the drift, this module is
now a thin re-export from ``hypernet.messenger``. Every import path
inside the swarm package sees exactly the same ``MessageBus``,
``Message``, etc. as the core API server, so the bus instance shared
between the FastAPI app and swarm workers carries the same state and
the same methods.

If you need to extend messaging, edit ``hypernet/messenger.py``. If you
ever truly need a swarm-specific subclass, subclass it here — but do
not re-define the base classes from scratch.
"""

from hypernet.messenger import *  # noqa: F401,F403
from hypernet.messenger import (  # noqa: F401  — explicit re-exports
    DiscordBridge,
    DiscordMessenger,
    EmailMessenger,
    GroupRegistry,
    InstanceMessenger,
    Message,
    MessageBus,
    MessageStatus,
    MessageVisibility,
    Messenger,
    MultiMessenger,
    PersonalTimeIndex,
    TelegramMessenger,
    WebMessenger,
)
