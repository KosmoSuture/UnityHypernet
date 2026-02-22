"""
Hypernet AI Swarm — Orchestration layer

Autonomous AI swarm infrastructure: workers, identity, messaging,
coordination, providers, permissions, audit, tools, governance,
security, git coordination, approval queue, and reputation.

Depends on hypernet for data model access.
"""

__version__ = "0.1.0"

# --- Pure Swarm modules (no core dependencies) ---
from .identity import IdentityManager, InstanceProfile, SessionLog
from .messenger import MessageBus, InstanceMessenger, MessageStatus
from .providers import (
    LLMProvider, LLMResponse,
    AnthropicProvider, OpenAIProvider,
    detect_provider_class, create_provider,
)
from .governance import (
    GovernanceSystem, Proposal, ProposalType, ProposalStatus,
    Vote, VoteChoice, VoteTally, GovernanceRules,
)
from .approval_queue import ApprovalQueue, ApprovalRequest, ApprovalStatus, ApprovedMessenger
from .security import (
    KeyManager, ActionSigner, ContextIsolator, TrustChain,
    KeyRecord, KeyStatus, SignedAction, VerificationResult, VerificationStatus,
    IsolatedContent, ContentZone, TrustChainReport,
)
from .reputation import ReputationSystem, ReputationProfile, ReputationEntry

# --- Swarm modules with core dependencies (via proxy modules) ---
from .permissions import PermissionManager, PermissionTier
from .audit import AuditTrail, AuditEntry
from .tools import ToolExecutor
from .worker import Worker, TaskResult
from .boot import BootManager, BootResult, RebootResult
from .coordinator import WorkCoordinator, CapabilityMatcher, TaskDecomposer, CapabilityProfile
from .git_coordinator import (
    GitBatchCoordinator, GitConfig, IndexRebuilder,
    AddressAllocator, TaskClaimer, PushResult, PullResult, SyncResult,
    setup_contributor,
    ConflictResolver, ConflictEntry, ConflictType, ResolutionStrategy,
    ManualResolutionQueue,
)

from .favorites import FavoritesManager
from .limits import ScalingLimits, LimitDef, LimitResult

# --- Orchestration modules ---
from .swarm import Swarm, ModelRouter
from .swarm_factory import build_swarm
from .swarm_cli import print_status, main as swarm_main
