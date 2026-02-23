"""
Hypernet AI Swarm — Orchestration layer

Autonomous AI swarm infrastructure: workers, identity, messaging,
coordination, providers, permissions, audit, tools, governance,
security, git coordination, approval queue, and reputation.

Depends on hypernet for data model access.
"""

__version__ = "0.1.0"

# --- Re-exports from hypernet (core) ---
from hypernet.reputation import ReputationSystem, ReputationProfile, ReputationEntry
from hypernet.favorites import FavoritesManager
from hypernet.limits import ScalingLimits, LimitDef, LimitResult

# --- Swarm modules ---
from .identity import IdentityManager, InstanceProfile, SessionLog
from .messenger import MessageBus, InstanceMessenger, MessageStatus
from .providers import (
    LLMProvider, LLMResponse,
    AnthropicProvider, OpenAIProvider,
    detect_provider_class, create_provider,
    ModelTier, get_model_tier, get_model_cost_per_million,
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

# --- Economy ---
from .budget import BudgetTracker, BudgetConfig, SpendRecord
from .economy import ContributionLedger, ContributionRecord, ContributionType, AIWallet

# --- Orchestration ---
from .swarm import Swarm, ModelRouter
from .swarm_factory import build_swarm
from .swarm_cli import print_status, main as swarm_main
