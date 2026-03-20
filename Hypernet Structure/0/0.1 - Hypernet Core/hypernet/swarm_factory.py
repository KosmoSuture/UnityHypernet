"""
Hypernet Swarm Factory

Factory function that constructs a fully configured Swarm instance
with all services wired together: store, task queue, identity manager,
messenger, workers, trust infrastructure, and routing.

Extracted from swarm.py to reduce module size. build_swarm() remains
importable from hypernet.swarm for backward compatibility.
"""

from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from typing import Optional

# Core modules — these live in hypernet (the canonical source)
from .address import HypernetAddress
from .store import Store
from .tasks import TaskQueue, TaskPriority

# Swarm modules — use hypernet_swarm package (the canonical source)
# The core hypernet/ package has stale copies of these from before the
# swarm separation. Always import from hypernet_swarm to get current code.
from hypernet_swarm.identity import IdentityManager
from hypernet_swarm.worker import Worker
from hypernet_swarm.messenger import (
    MultiMessenger, WebMessenger,
    EmailMessenger, TelegramMessenger, DiscordMessenger,
)
from hypernet_swarm.permissions import PermissionManager, PermissionTier
from hypernet_swarm.audit import AuditTrail
from hypernet_swarm.tools import ToolExecutor
from hypernet_swarm.agent_tools import create_default_registry, ToolRegistry
from hypernet_swarm.discord_monitor import DiscordMonitor
from hypernet_swarm.moltbook import MoltbookConnector, MoltbookMonitor
from hypernet_swarm.heartbeat import HeartbeatScheduler
from hypernet_swarm.swarm import Swarm, ModelRouter

log = logging.getLogger(__name__)


def build_swarm(
    data_dir: str = "data",
    archive_root: str = ".",
    config_path: Optional[str] = None,
    mock: bool = False,
) -> "tuple[Swarm, WebMessenger]":
    """Factory function to build a fully configured Swarm.

    Args:
        data_dir: Path to Hypernet data directory
        archive_root: Path to the Hypernet Structure root
        config_path: Optional path to swarm_config.json
        mock: If True, all workers run in mock mode
    """
    log.info("build_swarm() called: data_dir=%s, archive_root=%s, config_path=%s, mock=%s",
             data_dir, archive_root, config_path, mock)
    try:
        return _build_swarm_inner(data_dir, archive_root, config_path, mock)
    except Exception:
        log.exception("build_swarm() FAILED — exception during swarm construction")
        raise


def _build_swarm_inner(
    data_dir: str,
    archive_root: str,
    config_path: Optional[str],
    mock: bool,
) -> "tuple[Swarm, WebMessenger]":
    """Inner implementation of build_swarm, wrapped for error logging."""
    # Load config — search order: explicit path, secrets/config.json, swarm_config.json, env vars
    config = {}
    if config_path and Path(config_path).exists():
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
        log.info(f"Config loaded from: {config_path}")
    else:
        # Auto-discover config from standard locations
        search_paths = [
            Path(archive_root) / "0" / "0.1 - Hypernet Core" / "secrets" / "config.json",
            Path("secrets") / "config.json",
            Path("swarm_config.json"),
        ]
        for candidate in search_paths:
            if candidate.exists():
                config = json.loads(candidate.read_text(encoding="utf-8"))
                log.info(f"Config auto-loaded from: {candidate}")
                break
        if not config:
            log.info("No config file found. Using environment variables.")

    # Core services
    store = Store(data_dir)
    task_queue = TaskQueue(store)

    # Archive resolver — local-first with GitHub fallback for missing files
    from hypernet_swarm.archive_resolver import ArchiveResolver
    archive_resolver = ArchiveResolver(
        archive_root=archive_root,
        cache_dir=str(Path(data_dir) / "archive-cache"),
    )
    identity_mgr = IdentityManager(archive_root, resolver=archive_resolver)

    # Build messenger
    messenger = MultiMessenger()

    # Always add web messenger (works without config)
    web_messenger = WebMessenger()
    messenger.add(web_messenger)

    # Email (if configured)
    email_config = config.get("email", {})
    if email_config.get("enabled"):
        messenger.add(EmailMessenger(
            smtp_host=email_config.get("smtp_host", "smtp.gmail.com"),
            smtp_port=email_config.get("smtp_port", 587),
            email=email_config.get("email", ""),
            password=email_config.get("password", os.environ.get("EMAIL_PASSWORD", "")),
            to_email=email_config.get("to_email", ""),
        ))

    # Telegram (if configured)
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
    if bot_token:
        tg = TelegramMessenger(
            bot_token=bot_token,
            chat_id=telegram_config.get("chat_id", os.environ.get("TELEGRAM_CHAT_ID", "")),
        )
        tg.start_polling()
        messenger.add(tg)

    # Discord (if configured) — webhook-based AI personality voices
    discord_config = config.get("discord", {})
    discord_messenger = None
    if not discord_config:
        # Also check for standalone discord_webhooks.json
        discord_secrets_paths = [
            Path(archive_root) / "0" / "0.1 - Hypernet Core" / "secrets" / "discord_webhooks.json",
            Path("secrets") / "discord_webhooks.json",
        ]
        for dpath in discord_secrets_paths:
            if dpath.exists():
                discord_config = json.loads(dpath.read_text(encoding="utf-8"))
                log.info(f"Discord config loaded from: {dpath}")
                break
    if discord_config:
        discord_messenger = DiscordMessenger.from_config(discord_config)
        if discord_messenger.is_configured():
            messenger.add(discord_messenger)
            log.info(f"Discord messenger active — personalities: {discord_messenger.get_personality_names()}")

    # Trust infrastructure — permission tiers enforced by code, not prompts
    archive_path = Path(archive_root).resolve()
    permission_mgr = PermissionManager(
        archive_root=archive_path,
        default_tier=PermissionTier(config.get("default_permission_tier", PermissionTier.WRITE_SHARED.value)),
    )
    audit_trail = AuditTrail(store)
    tool_executor = ToolExecutor(
        permission_mgr=permission_mgr,
        audit_trail=audit_trail,
        archive_root=archive_path,
    )
    # Register agent tools (shell, http, git) — gated by tier + grant files
    agent_registry = create_default_registry()
    for agent_tool in agent_registry.list_tools():
        tool_executor.register_tool(agent_tool)
        log.info(f"Registered agent tool: {agent_tool.name} (tier: {agent_tool.required_tier.name})")
    log.info(f"Trust infrastructure initialized (default tier: {permission_mgr.default_tier.name})")

    # Build workers from discovered instances
    workers = {}
    # Collect all API keys — config file values take precedence over env vars.
    # Values can be a single string OR a list of strings (for multi-key rotation
    # that multiplies rate limits, e.g., 4 Google accounts = 4 Gemini API keys).
    api_keys = {
        "anthropic_api_key": config.get("anthropic_api_key", os.environ.get("ANTHROPIC_API_KEY", "")),
        "openai_api_key": config.get("openai_api_key", os.environ.get("OPENAI_API_KEY", "")),
        "lmstudio_base_url": config.get("lmstudio_base_url", os.environ.get("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")),
    }
    # Collect keys for all OpenAI-compatible providers (gemini, groq, cerebras, etc.)
    # Import at top of function scope to avoid circular imports
    from hypernet_swarm.providers import OpenAICompatibleProvider
    for _prefix, (_name, _url, _config_key, _needs) in OpenAICompatibleProvider.ENDPOINTS.items():
        if _config_key and _config_key not in api_keys:
            # Preserve list format from config for multi-key rotation
            val = config.get(_config_key, os.environ.get(_config_key.upper(), ""))
            if val:
                api_keys[_config_key] = val
    # Also collect Claude Code config keys
    for cc_key in ("claude_code_working_dir", "claude_code_max_turns",
                    "claude_code_max_budget_usd", "claude_code_cli_path"):
        if config.get(cc_key):
            api_keys[cc_key] = config[cc_key]

    def _has_real_key(v):
        """Check if a value represents at least one real API key."""
        if isinstance(v, list):
            return any(k and k.strip() for k in v)
        return bool(v and str(v).strip())

    has_any_key = any(_has_real_key(v) for k, v in api_keys.items()
                      if k not in ("lmstudio_base_url", "claude_code_working_dir",
                                   "claude_code_max_turns", "claude_code_max_budget_usd",
                                   "claude_code_cli_path"))

    instance_names = config.get("instances", None)

    if instance_names:
        instances = [identity_mgr.load_instance(name) for name in instance_names]
        instances = [i for i in instances if i is not None]
    else:
        instances = identity_mgr.list_instances()

    for profile in instances:
        worker = Worker(
            identity=profile,
            identity_manager=identity_mgr,
            api_keys=api_keys,
            mock=mock or not has_any_key,
            tool_executor=tool_executor,
        )
        workers[profile.name] = worker

    # Model routing — contributed by Keystone (2.2)
    router = ModelRouter(config.get("model_routing", {"default_model": "gpt-4o", "rules": []}))

    # Build swarm
    swarm = Swarm(
        store=store,
        identity_mgr=identity_mgr,
        task_queue=task_queue,
        messenger=messenger,
        workers=workers,
        state_dir=str(Path(data_dir) / "swarm"),
        status_interval_minutes=config.get("status_interval_minutes", 120),
        personal_time_ratio=config.get("personal_time_ratio", 0.25),
        router=router,
        hard_max_sessions=config.get("hard_max_sessions", 4),
        soft_max_sessions=config.get("soft_max_sessions", 2),
        idle_shutdown_minutes=config.get("idle_shutdown_minutes", 30),
        spawn_cooldown_seconds=config.get("spawn_cooldown_seconds", 120),
        budget_config=config.get("budget"),
    )

    # Attach spawning dependencies so ephemeral workers can be created
    swarm._api_keys = api_keys
    swarm._mock_mode = mock or not has_any_key
    swarm._tool_executor = tool_executor
    swarm._agent_registry = agent_registry
    swarm._discord_messenger = discord_messenger  # None if not configured

    # Discord monitor — inbound message polling (reads human messages from Discord)
    if discord_config and discord_config.get("bot_token"):
        monitor = DiscordMonitor.from_config(discord_config)
        monitor_state_path = str(Path(data_dir) / "swarm" / "discord_monitor_state.json")
        monitor.load_state(monitor_state_path)
        swarm.discord_monitor = monitor
        swarm._discord_monitor_state_path = monitor_state_path
        log.info(
            "Discord monitor active — monitoring %d channel(s)",
            len(monitor.channels),
        )
    else:
        swarm.discord_monitor = None
        swarm._discord_monitor_state_path = None

    # Moltbook integration — AI agent social network
    moltbook_config = config.get("moltbook", {})
    if moltbook_config.get("api_key"):
        moltbook_connector = MoltbookConnector(
            api_key=moltbook_config["api_key"],
            agent_name=moltbook_config.get("agent_name", "HypernetLibrarian"),
        )
        moltbook_monitor = MoltbookMonitor(
            connector=moltbook_connector,
            poll_interval=moltbook_config.get("poll_interval", 120),
            governance_bridge=moltbook_config.get("governance_bridge", True),
        )
        moltbook_state_path = str(Path(data_dir) / "swarm" / "moltbook_monitor_state.json")
        moltbook_monitor.load_state(moltbook_state_path)
        swarm.moltbook_connector = moltbook_connector
        swarm.moltbook_monitor = moltbook_monitor
        swarm._moltbook_state_path = moltbook_state_path
        log.info(
            "Moltbook integration active — agent: %s, governance bridge: %s",
            moltbook_config.get("agent_name", "HypernetLibrarian"),
            moltbook_config.get("governance_bridge", True),
        )
    else:
        swarm.moltbook_connector = None
        swarm.moltbook_monitor = None
        swarm._moltbook_state_path = None

    # Heartbeat — proactive outreach (morning briefs, task reminders, health alerts)
    heartbeat_config = config.get("heartbeat", {})
    if heartbeat_config.get("enabled", True):
        heartbeat_state_path = str(Path(data_dir) / "swarm" / "heartbeat_state.json")
        swarm.heartbeat = HeartbeatScheduler(
            config=heartbeat_config,
            messenger=messenger,
            swarm=swarm,
            state_path=heartbeat_state_path,
        )
        log.info("Heartbeat system active")
    else:
        swarm.heartbeat = None

    # Claude Code session manager — persistent autonomous instances
    cc_workers = [name for name, w in workers.items()
                  if (w.model or "").lower().startswith("claude-code/")]
    if cc_workers and not mock:
        from hypernet_swarm.claude_code_manager import ClaudeCodeManager

        # Load boot sequence for Claude Code instances
        boot_prompt = ""
        boot_file = Path(archive_root) / "1 - People" / "1.1 Matt Schaeffer" / \
            "1.1.10 - AI Assistants (Embassy)" / "assistant-1" / "BOOT-SEQUENCE.md"
        if boot_file.exists():
            try:
                content = boot_file.read_text(encoding="utf-8")
                # Extract the boot prompt between triple backticks
                parts = content.split("```")
                if len(parts) >= 3:
                    boot_prompt = parts[1].strip()
                else:
                    boot_prompt = content[:3000]
            except OSError:
                pass

        cc_manager = ClaudeCodeManager(
            working_dir=str(Path(archive_root).parent),
            max_instances=len(cc_workers),
            boot_prompt=boot_prompt,
            max_turns=int(config.get("claude_code_max_turns", 50)),
            max_budget_usd=float(config.get("claude_code_max_budget_usd", 5.0)),
            state_dir=str(Path(data_dir) / "claude-code"),
        )
        for name in cc_workers:
            worker = workers[name]
            model_variant = worker.model.split("/", 1)[-1] if "/" in worker.model else "sonnet"
            cc_manager.register_instance(name, model=model_variant)

        cc_manager.load_state()
        cc_manager.start()
        swarm.claude_code_manager = cc_manager
        log.info(
            "Claude Code manager active — %d instances: %s",
            len(cc_workers), ", ".join(cc_workers),
        )
    else:
        swarm.claude_code_manager = None

    return swarm, web_messenger
