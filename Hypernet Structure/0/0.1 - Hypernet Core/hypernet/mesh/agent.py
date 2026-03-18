"""
Node Agent — the main loop that runs on each device in the mesh.

Connects to the swarm coordinator via WebSocket, registers device
capabilities, sends heartbeats, and executes dispatched tasks.

This is the Phase 3 entry point. Can be run standalone:
    python -m hypernet node --coordinator ws://10.0.0.1:8000/ws/mesh

Or programmatically:
    agent = NodeAgent(coordinator_url, device_address)
    asyncio.run(agent.run())
"""

from __future__ import annotations

import asyncio
import json
import logging
import secrets
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .capabilities import DeviceCapabilities, detect_capabilities
from .resources import ResourceMonitor, ResourceSnapshot

log = logging.getLogger(__name__)

# How often to send heartbeats (seconds)
HEARTBEAT_INTERVAL = 30

# How long to wait before reconnecting after disconnect
RECONNECT_BASE_DELAY = 1
RECONNECT_MAX_DELAY = 60


@dataclass
class NodeConfig:
    """Configuration for the node agent."""

    coordinator_url: str = "ws://localhost:8000/ws/mesh"
    device_address: str = ""       # Assigned by coordinator on first registration
    device_name: str = ""          # Human-readable name (e.g., "Matt's Laptop")
    secret_key: str = ""           # Shared secret for message signing
    state_path: str = ""           # Path to persist state (address, key, etc.)

    def save(self, path: Optional[str] = None) -> None:
        """Persist config to disk."""
        p = Path(path or self.state_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "coordinator_url": self.coordinator_url,
            "device_address": self.device_address,
            "device_name": self.device_name,
            "secret_key": self.secret_key,
        }
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str) -> NodeConfig:
        """Load config from disk."""
        p = Path(path)
        if not p.exists():
            return cls(state_path=path)
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(
            coordinator_url=data.get("coordinator_url", "ws://localhost:8000/ws/mesh"),
            device_address=data.get("device_address", ""),
            device_name=data.get("device_name", ""),
            secret_key=data.get("secret_key", ""),
            state_path=path,
        )


class NodeAgent:
    """Lightweight agent that runs on each device in the mesh.

    Lifecycle:
        1. Connect to coordinator via WebSocket
        2. Send registration with device capabilities
        3. Receive assigned address (or confirm existing)
        4. Enter main loop: heartbeat + task execution
        5. On disconnect: auto-reconnect with exponential backoff
    """

    def __init__(
        self,
        config: NodeConfig,
        capabilities: Optional[DeviceCapabilities] = None,
    ) -> None:
        self.config = config
        self.capabilities = capabilities or detect_capabilities()
        self.resources = ResourceMonitor()
        self._ws = None
        self._running = False
        self._reconnect_delay = RECONNECT_BASE_DELAY
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._connected_since: Optional[float] = None

        # Generate secret key if not set
        if not self.config.secret_key:
            self.config.secret_key = secrets.token_urlsafe(32)
            if self.config.state_path:
                self.config.save()

    async def run(self) -> None:
        """Main agent loop. Runs forever (auto-reconnects)."""
        self._running = True
        log.info(
            "Node agent starting: coordinator=%s, device=%s",
            self.config.coordinator_url,
            self.config.device_address or "(new device)",
        )

        while self._running:
            try:
                await self._connect_and_loop()
            except Exception as e:
                log.warning("Connection lost: %s", e)
                self._connected_since = None

            if not self._running:
                break

            # Exponential backoff
            log.info("Reconnecting in %ds...", self._reconnect_delay)
            await asyncio.sleep(self._reconnect_delay)
            self._reconnect_delay = min(
                self._reconnect_delay * 2,
                RECONNECT_MAX_DELAY,
            )

    async def _connect_and_loop(self) -> None:
        """Connect to coordinator and run heartbeat/task loop."""
        try:
            import websockets
        except ImportError:
            log.error(
                "websockets package required: pip install websockets"
            )
            self._running = False
            return

        async with websockets.connect(self.config.coordinator_url) as ws:
            self._ws = ws
            self._connected_since = time.time()
            self._reconnect_delay = RECONNECT_BASE_DELAY
            log.info("Connected to coordinator")

            # Register
            await self._send({
                "type": "register",
                "address": self.config.device_address,
                "name": self.config.device_name,
                "capabilities": self.capabilities.to_dict(),
            })

            # Wait for registration response
            response = await asyncio.wait_for(ws.recv(), timeout=10)
            msg = json.loads(response)
            if msg.get("type") == "registered":
                assigned_addr = msg.get("address", self.config.device_address)
                if assigned_addr and assigned_addr != self.config.device_address:
                    self.config.device_address = assigned_addr
                    if self.config.state_path:
                        self.config.save()
                    log.info("Assigned address: %s", assigned_addr)
                else:
                    log.info("Registration confirmed: %s", self.config.device_address)

            # Main loop: heartbeat + listen for tasks
            last_heartbeat = 0.0
            while self._running:
                now = time.time()

                # Send heartbeat
                if now - last_heartbeat >= HEARTBEAT_INTERVAL:
                    snapshot = self.resources.snapshot()
                    await self._send({
                        "type": "heartbeat",
                        "address": self.config.device_address,
                        "resources": snapshot.to_dict(),
                    })
                    last_heartbeat = now

                # Listen for incoming messages (tasks, commands)
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=5)
                    msg = json.loads(raw)
                    await self._handle_message(msg)
                except asyncio.TimeoutError:
                    continue  # Normal — no message this cycle

    async def _handle_message(self, msg: dict) -> None:
        """Handle an incoming message from the coordinator."""
        msg_type = msg.get("type", "")

        if msg_type == "task":
            await self._execute_task(msg)
        elif msg_type == "ping":
            await self._send({"type": "pong", "address": self.config.device_address})
        elif msg_type == "revoke":
            log.warning("Device revoked by coordinator! Shutting down.")
            self._running = False
        elif msg_type == "config_update":
            log.info("Config update received: %s", msg.get("updates", {}))
        else:
            log.debug("Unknown message type: %s", msg_type)

    async def _execute_task(self, msg: dict) -> None:
        """Execute a task dispatched by the coordinator."""
        task_id = msg.get("task_id", "unknown")
        action = msg.get("action", "")
        payload = msg.get("payload", {})

        log.info("Executing task %s: %s", task_id, action)

        try:
            # Task execution is pluggable — override _run_action for custom actions
            result = await self._run_action(action, payload)
            await self._send({
                "type": "result",
                "task_id": task_id,
                "success": True,
                "data": result,
            })
            self._tasks_completed += 1
        except Exception as e:
            log.error("Task %s failed: %s", task_id, e)
            await self._send({
                "type": "result",
                "task_id": task_id,
                "success": False,
                "error": str(e),
            })
            self._tasks_failed += 1

    async def _run_action(self, action: str, payload: dict) -> Any:
        """Execute a specific action. Override for custom device actions."""
        # Built-in actions
        if action == "ping":
            return {"pong": True, "timestamp": time.time()}
        elif action == "capabilities":
            return self.capabilities.to_dict()
        elif action == "resources":
            return self.resources.snapshot().to_dict()
        elif action == "health":
            snap = self.resources.snapshot()
            return {
                "device": self.config.device_address,
                "uptime_s": time.time() - (self._connected_since or time.time()),
                "tasks_completed": self._tasks_completed,
                "tasks_failed": self._tasks_failed,
                "cpu_percent": snap.cpu_percent,
                "ram_percent": snap.ram_percent,
                "battery": snap.battery_percent,
            }
        else:
            raise ValueError(f"Unknown action: {action}")

    async def _send(self, msg: dict) -> None:
        """Send a message to the coordinator."""
        if self._ws:
            await self._ws.send(json.dumps(msg))

    def stop(self) -> None:
        """Signal the agent to stop."""
        self._running = False

    @property
    def status(self) -> dict:
        """Current agent status."""
        return {
            "address": self.config.device_address,
            "connected": self._connected_since is not None,
            "connected_since": self._connected_since,
            "tasks_completed": self._tasks_completed,
            "tasks_failed": self._tasks_failed,
            "capabilities": self.capabilities.to_dict(),
        }
