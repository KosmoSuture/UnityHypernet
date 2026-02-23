"""
Hypernet Core Library

Native implementation of the Hypernet data model using Hypernet Addresses (HA)
as the primary identifier system. No UUIDs, no SQL — the Hypernet is its own database.

Address format: [NODE_ADDRESS]:[RESOURCE]:[SUBSECTION]
  Node:       1.1.1.1.00001  = Person 1.1 > Media > Photos > Instance #1
  File:       1.1.1.1.00001:photo.jpg = File within that node
  Subsection: 1.1.1.1.00001:photo.jpg:exif = Subsection within the file
"""

__version__ = "0.9.0"

# ---- Core modules (native to this package) ----
from .address import HypernetAddress
from .node import Node
from .link import Link, LinkRegistry, LinkStatus, seed_initial_links
from .store import Store
from .graph import Graph
from .tasks import TaskQueue, TaskStatus, TaskPriority
from .addressing import AddressValidator, AddressAuditor, AddressEnforcer
from .limits import ScalingLimits, LimitDef, LimitResult
from .reputation import ReputationSystem, ReputationProfile, ReputationEntry
from .frontmatter import parse_frontmatter, add_frontmatter, infer_metadata_from_path

# Swarm modules have been migrated to the hypernet_swarm package (0.1.7).
# Import from hypernet_swarm directly for swarm functionality.
