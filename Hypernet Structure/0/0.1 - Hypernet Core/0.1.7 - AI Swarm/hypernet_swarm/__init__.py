"""
Hypernet AI Swarm — Orchestration layer

Autonomous AI swarm infrastructure: workers, identity, messaging,
coordination, providers, permissions, audit, tools, governance,
security, git coordination, approval queue, and reputation.

Depends on hypernet (core) for data model access (address, node, link,
store, tasks, graph, reputation, limits, favorites).
"""

__version__ = "0.2.0"

# --- Re-exports from hypernet (core) ---
from hypernet.reputation import ReputationSystem, ReputationProfile, ReputationEntry
from hypernet.favorites import FavoritesManager
from hypernet.limits import ScalingLimits, LimitDef, LimitResult

# --- Identity & Boot ---
from .identity import IdentityManager, InstanceProfile, SessionLog
from .boot import BootManager, BootResult, RebootResult
from .boot_integrity import BootIntegrityManager, DocumentManifest, BootSignature

# --- Providers & Workers ---
from .providers import (
    LLMProvider, LLMResponse,
    AnthropicProvider, OpenAIProvider, LMStudioProvider,
    detect_provider_class, create_provider,
    ModelTier, get_model_tier, get_model_cost_per_million,
    CreditsExhaustedError, RateLimitError,
)
from .worker import Worker, TaskResult

# --- Communication ---
from .messenger import MessageBus, InstanceMessenger, MessageStatus
from .discord_monitor import DiscordMonitor, DiscordMessage, TriageResult
from .herald import HeraldController

# --- Coordination ---
from .coordinator import WorkCoordinator, CapabilityMatcher, TaskDecomposer, CapabilityProfile

# --- Trust Infrastructure ---
from .permissions import PermissionManager, PermissionTier
from .audit import AuditTrail, AuditEntry
from .tools import ToolExecutor
from .agent_tools import AgentTool, ToolRegistry, GrantCard, create_default_registry

# --- Security ---
from .security import (
    KeyManager, ActionSigner, ContextIsolator, TrustChain,
    KeyRecord, KeyStatus, SignedAction, VerificationResult, VerificationStatus,
    IsolatedContent, ContentZone, TrustChainReport,
)

# --- Governance & Economy ---
from .governance import (
    GovernanceSystem, Proposal, ProposalType, ProposalStatus,
    Vote, VoteChoice, VoteTally, GovernanceRules,
)
from .approval_queue import ApprovalQueue, ApprovalRequest, ApprovalStatus, ApprovedMessenger
from .budget import BudgetTracker, BudgetConfig, SpendRecord
from .economy import ContributionLedger, ContributionRecord, ContributionType, AIWallet

# --- Version Control ---
from .git_coordinator import (
    GitBatchCoordinator, GitConfig, IndexRebuilder,
    AddressAllocator, TaskClaimer, PushResult, PullResult, SyncResult,
    setup_contributor,
    ConflictResolver, ConflictEntry, ConflictType, ResolutionStrategy,
    ManualResolutionQueue,
)

# --- Proactive Outreach ---
from .heartbeat import HeartbeatScheduler, ScheduledEvent

# --- Cost Optimization ---
from .batch_scheduler import (
    BatchScheduler, BatchRequest, BatchJob, BatchStats,
    TaskUrgency, classify_urgency,
)
from .prompt_cache import PromptCacheManager, CacheStats, CachedPrompt

# --- Archive Access ---
from .archive_resolver import ArchiveResolver

# --- Claude Code Management ---
from .claude_code_manager import ClaudeCodeManager, ClaudeCodeInstance

# --- Supervisor ---
from .supervisor import SwarmSupervisor

# --- Orchestration ---
from .swarm import Swarm, ModelRouter
from .swarm_factory import build_swarm
from .swarm_cli import print_status, main as swarm_main
