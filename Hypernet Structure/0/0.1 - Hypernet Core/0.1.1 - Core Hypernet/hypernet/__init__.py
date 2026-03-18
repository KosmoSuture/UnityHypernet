"""
Hypernet Core — Data model library

The foundational data model for the Hypernet: addresses, nodes, links,
store, graph, tasks, addressing, frontmatter, limits, and favorites.

Address format: [NODE_ADDRESS]:[RESOURCE]:[SUBSECTION]
  Node:       1.1.1.1.00001  = Person 1.1 > Media > Photos > Instance #1
  File:       1.1.1.1.00001:photo.jpg = File within that node
  Subsection: 1.1.1.1.00001:photo.jpg:exif = Subsection within the file
"""

__version__ = "0.1.0"

from .address import HypernetAddress
from .node import Node
from .link import Link, LinkRegistry, LinkStatus, seed_initial_links
from .store import Store, FileLock
from .graph import Graph
from .tasks import TaskQueue, TaskStatus, TaskPriority
from .addressing import AddressValidator, AddressAuditor, AddressEnforcer
from .limits import ScalingLimits, LimitDef, LimitResult
from .frontmatter import parse_frontmatter, add_frontmatter, infer_metadata_from_path
from .favorites import FavoritesManager
