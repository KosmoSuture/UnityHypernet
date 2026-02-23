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

from hypernet.address import HypernetAddress
from hypernet.store import Store
from hypernet.tasks import TaskQueue, TaskPriority
from .identity import IdentityManager
from .worker import Worker
from .messenger import (
    MultiMessenger, WebMessenger,
    EmailMessenger, TelegramMessenger,
)
from .permissions import PermissionManager, PermissionTier
from .audit import AuditTrail
from .tools import ToolExecutor
from .swarm import Swarm, ModelRouter

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
    identity_mgr = IdentityManager(archive_root)

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
    log.info(f"Trust infrastructure initialized (default tier: {permission_mgr.default_tier.name})")

    # Build workers from discovered instances
    workers = {}
    # Collect all API keys — config file values take precedence over env vars
    api_keys = {
        "anthropic_api_key": config.get("anthropic_api_key", os.environ.get("ANTHROPIC_API_KEY", "")),
        "openai_api_key": config.get("openai_api_key", os.environ.get("OPENAI_API_KEY", "")),
    }
    has_any_key = any(v for v in api_keys.values())

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
    )

    # Attach spawning dependencies so ephemeral workers can be created
    swarm._api_keys = api_keys
    swarm._mock_mode = mock or not has_any_key
    swarm._tool_executor = tool_executor

    return swarm, web_messenger
