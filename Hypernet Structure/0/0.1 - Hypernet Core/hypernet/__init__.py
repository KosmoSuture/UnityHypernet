"""
Hypernet Core Library

Native implementation of the Hypernet data model using Hypernet Addresses (HA)
as the primary identifier system. No UUIDs, no SQL — the Hypernet is its own database.

Address format: [NODE_ADDRESS]:[RESOURCE]:[SUBSECTION]
  Node:       1.1.1.1.00001  = Person 1.1 > Media > Photos > Instance #1
  File:       1.1.1.1.00001:photo.jpg = File within that node
  Subsection: 1.1.1.1.00001:photo.jpg:exif = Subsection within the file
"""

__version__ = "0.7.0"

from .address import HypernetAddress
from .node import Node
from .link import Link, LinkRegistry, LinkStatus, seed_initial_links
from .store import Store
from .graph import Graph
from .tasks import TaskQueue, TaskStatus, TaskPriority
from .identity import IdentityManager, InstanceProfile, SessionLog
from .worker import Worker, TaskResult
from .messenger import MessageBus, InstanceMessenger, MessageStatus
from .coordinator import WorkCoordinator, CapabilityMatcher, TaskDecomposer, CapabilityProfile
from .addressing import AddressValidator, AddressAuditor, AddressEnforcer
from .swarm import Swarm, ModelRouter
from .boot import BootManager, BootResult, RebootResult
from .permissions import PermissionManager, PermissionTier
from .audit import AuditTrail, AuditEntry
from .tools import ToolExecutor, ToolResult as ToolExecResult
from .limits import ScalingLimits, LimitDef, LimitResult
from .reputation import ReputationSystem, ReputationProfile, ReputationEntry
from .providers import (
    LLMProvider, LLMResponse,
    AnthropicProvider, OpenAIProvider,
    detect_provider_class, create_provider,
)
