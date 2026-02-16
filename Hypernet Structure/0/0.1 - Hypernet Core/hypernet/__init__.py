"""
Hypernet Core Library

Native implementation of the Hypernet data model using Hypernet Addresses (HA)
as the primary identifier system. No UUIDs, no SQL — the Hypernet is its own database.

Address format: [CATEGORY].[SUBCATEGORY].[TYPE].[SUBTYPE].[INSTANCE]
Example: 1.1.1.1.00001 = Person 1.1 > Media > Photos > Instance #1
"""

__version__ = "0.1.0"

from .address import HypernetAddress
from .node import Node
from .link import Link
from .store import Store
from .graph import Graph
from .tasks import TaskQueue, TaskStatus, TaskPriority
from .identity import IdentityManager, InstanceProfile, SessionLog
from .worker import Worker, TaskResult
from .swarm import Swarm
