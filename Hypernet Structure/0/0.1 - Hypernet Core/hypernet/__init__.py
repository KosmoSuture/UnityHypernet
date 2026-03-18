"""
Hypernet Core Library

Native implementation of the Hypernet data model using Hypernet Addresses (HA)
as the primary identifier system. No UUIDs, no SQL — the Hypernet is its own database.

Address format: [NODE_ADDRESS]:[RESOURCE]:[SUBSECTION]
  Node:       1.1.1.1.00001  = Person 1.1 > Media > Photos > Instance #1
  File:       1.1.1.1.00001:photo.jpg = File within that node
  Subsection: 1.1.1.1.00001:photo.jpg:exif = Subsection within the file
"""

__version__ = "0.9.1"

# ---- Auto-detect swarm package location ----
# The hypernet_swarm package lives at 0.1.7 - AI Swarm/ (sibling or child dir).
# Add it to sys.path so `import hypernet_swarm` works regardless of install method.
import sys as _sys
from pathlib import Path as _Path

_pkg_dir = _Path(__file__).parent
for _candidate in [
    _pkg_dir.parent / "0.1.7 - AI Swarm",          # New: child of 0.1
    _pkg_dir.parent.parent / "0.1.7 - AI Swarm",   # Legacy: sibling of 0.1
]:
    if _candidate.is_dir() and str(_candidate) not in _sys.path:
        _sys.path.insert(0, str(_candidate))
        break
del _pkg_dir, _candidate, _Path

# ---- Core data model ----
from .address import HypernetAddress
from .node import Node
from .link import Link, LinkRegistry, LinkStatus, seed_initial_links
from .store import Store
from .graph import Graph
from .tasks import TaskQueue, TaskStatus, TaskPriority
from .addressing import AddressValidator, AddressAuditor, AddressEnforcer
from .limits import ScalingLimits, LimitDef, LimitResult
from .reputation import ReputationSystem, ReputationProfile, ReputationEntry
from .favorites import FavoritesManager
from .frontmatter import parse_frontmatter, add_frontmatter, infer_metadata_from_path

# Swarm orchestration has been separated into the hypernet_swarm package (0.1.7).
# Import from hypernet_swarm for: Swarm, Worker, IdentityManager, providers,
# messenger, coordinator, governance, security, audit, tools, boot, etc.
