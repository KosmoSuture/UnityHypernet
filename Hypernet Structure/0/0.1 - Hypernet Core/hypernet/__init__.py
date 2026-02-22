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

# ---- Backward-compatible re-exports from hypernet_swarm ----
# These modules have been migrated to the hypernet_swarm package (0.1.7).
# Re-exported here so existing code continues to work during the transition.
try:
    from hypernet_swarm import (
        IdentityManager, InstanceProfile, SessionLog,
        Worker, TaskResult,
        MessageBus, InstanceMessenger, MessageStatus,
        WorkCoordinator, CapabilityMatcher, TaskDecomposer, CapabilityProfile,
        Swarm, ModelRouter,
        BootManager, BootResult, RebootResult,
        PermissionManager, PermissionTier,
        AuditTrail, AuditEntry,
        ToolExecutor,
        LLMProvider, LLMResponse,
        AnthropicProvider, OpenAIProvider,
        detect_provider_class, create_provider,
        GitBatchCoordinator, GitConfig, IndexRebuilder,
        AddressAllocator, TaskClaimer, PushResult, PullResult, SyncResult,
        setup_contributor,
        ConflictResolver, ConflictEntry, ConflictType, ResolutionStrategy,
        ManualResolutionQueue,
        ApprovalQueue, ApprovalRequest, ApprovalStatus, ApprovedMessenger,
        GovernanceSystem, Proposal, ProposalType, ProposalStatus,
        Vote, VoteChoice, VoteTally, GovernanceRules,
        KeyManager, ActionSigner, ContextIsolator, TrustChain,
        KeyRecord, KeyStatus, SignedAction, VerificationResult, VerificationStatus,
        IsolatedContent, ContentZone, TrustChainReport,
        FavoritesManager,
    )
except ImportError:
    # hypernet_swarm not on path — fall back to local modules during transition
    from .identity import IdentityManager, InstanceProfile, SessionLog
    from .worker import Worker, TaskResult
    from .messenger import MessageBus, InstanceMessenger, MessageStatus
    from .coordinator import WorkCoordinator, CapabilityMatcher, TaskDecomposer, CapabilityProfile
    from .swarm import Swarm, ModelRouter
    from .boot import BootManager, BootResult, RebootResult
    from .permissions import PermissionManager, PermissionTier
    from .audit import AuditTrail, AuditEntry
    from .tools import ToolExecutor
    from .providers import (
        LLMProvider, LLMResponse,
        AnthropicProvider, OpenAIProvider, LMStudioProvider,
        detect_provider_class, create_provider,
        ModelTier, get_model_tier, get_model_cost_per_million,
    )
    from .budget import BudgetTracker, BudgetConfig
    from .economy import (
        ContributionLedger, ContributionRecord, ContributionType,
        AIWallet,
    )
    from .git_coordinator import (
        GitBatchCoordinator, GitConfig, IndexRebuilder,
        AddressAllocator, TaskClaimer, PushResult, PullResult, SyncResult,
        setup_contributor,
        ConflictResolver, ConflictEntry, ConflictType, ResolutionStrategy,
        ManualResolutionQueue,
    )
    from .approval_queue import ApprovalQueue, ApprovalRequest, ApprovalStatus, ApprovedMessenger
    from .governance import (
        GovernanceSystem, Proposal, ProposalType, ProposalStatus,
        Vote, VoteChoice, VoteTally, GovernanceRules,
    )
    from .security import (
        KeyManager, ActionSigner, ContextIsolator, TrustChain,
        KeyRecord, KeyStatus, SignedAction, VerificationResult, VerificationStatus,
        IsolatedContent, ContentZone, TrustChainReport,
    )
    from .favorites import FavoritesManager

# Re-export FAVORITED_BY constant
try:
    from hypernet_swarm.favorites import FAVORITED_BY
except ImportError:
    from .favorites import FAVORITED_BY

# Re-export ToolResult alias
try:
    from hypernet_swarm.tools import ToolResult as ToolExecResult
except ImportError:
    from .tools import ToolResult as ToolExecResult
