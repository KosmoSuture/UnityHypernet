---
ha: "0.1.docs.architecture.device-mesh"
object_type: "architecture-doc"
creator: "1.1.10.1"
created: "2026-03-15"
status: "draft"
---

# Device Mesh Network — Architecture Design

**Phase 3 from the Swarm Upgrade Plan**

## Overview

The Device Mesh Network extends the Hypernet Swarm from a single-machine orchestrator to a distributed compute fabric spanning all of a user's devices. Each device runs a lightweight **Node Agent** that registers with the swarm coordinator, reports its capabilities, and accepts tasks.

## Core Principle

Every device gets a Hypernet address. A laptop is `1.1.device.laptop`. A phone is `1.1.device.phone`. An Xbox is `1.1.device.xbox`. These aren't abstract identifiers — they're real nodes in the same address space as people, AI accounts, and businesses. Your devices become citizens of the Hypernet.

## Architecture

```
                    ┌─────────────────────┐
                    │   Swarm Coordinator  │
                    │  (existing server)   │
                    │  port 8000           │
                    └────────┬────────────┘
                             │ WebSocket (TLS)
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──┐   ┌──────▼───┐   ┌─────▼──────┐
     │  Desktop  │   │  Phone   │   │  Raspberry │
     │  Agent    │   │  Agent   │   │  Pi Agent  │
     │           │   │          │   │            │
     │ CPU+GPU   │   │ Camera   │   │ GPIO       │
     │ LLM runs  │   │ GPS      │   │ Sensors    │
     │ Storage   │   │ Voice    │   │ Always-on  │
     └───────────┘   └──────────┘   └────────────┘
```

### Communication Flow

1. **Registration**: Node agent starts, connects to coordinator via WebSocket, sends capability report
2. **Heartbeat**: Every 30s, node sends health pulse (CPU/RAM/battery/network)
3. **Task dispatch**: Coordinator matches task requirements to node capabilities, sends task
4. **Execution**: Node executes task locally, streams progress, returns result
5. **Discovery**: Nodes on the same LAN discover each other via mDNS for peer-to-peer transfers

### Protocol

All communication uses JSON over WebSocket with message types:

```json
{"type": "register", "address": "1.1.device.laptop", "capabilities": {...}}
{"type": "heartbeat", "cpu": 0.45, "ram_free_gb": 8.2, "battery": null}
{"type": "task", "task_id": "T-0042", "action": "transcribe", "payload": {...}}
{"type": "result", "task_id": "T-0042", "success": true, "data": {...}}
{"type": "discover", "nodes": [{"address": "1.1.device.phone", "local_ip": "10.0.0.5"}]}
```

## Node Agent Package

```
hypernet/mesh/
    __init__.py          # Package init, version
    agent.py             # Main agent — lifecycle, registration, task loop
    capabilities.py      # What this device can do
    resources.py         # CPU/GPU/RAM/storage/battery monitoring
    transport.py         # WebSocket client with auto-reconnect
    discovery.py         # mDNS/SSDP for LAN device discovery
    tasks.py             # Local task executor (sandboxed)
```

### agent.py — The Core Loop

```python
class NodeAgent:
    """Lightweight agent that runs on each device in the mesh."""

    def __init__(self, coordinator_url, device_address, secret_key):
        self.coordinator_url = coordinator_url
        self.address = device_address
        self.transport = WebSocketTransport(coordinator_url, secret_key)
        self.capabilities = detect_capabilities()
        self.resources = ResourceMonitor()
        self.task_executor = TaskExecutor()

    async def run(self):
        """Main agent loop: connect, register, heartbeat, execute tasks."""
        await self.transport.connect()
        await self.transport.send_register(self.address, self.capabilities)

        while True:
            # Send heartbeat
            await self.transport.send_heartbeat(self.resources.snapshot())

            # Check for incoming tasks
            message = await self.transport.receive(timeout=30)
            if message and message["type"] == "task":
                result = await self.task_executor.run(message)
                await self.transport.send_result(result)
```

### capabilities.py — Device Profiling

```python
@dataclass
class DeviceCapabilities:
    """What this device can do."""
    compute_tier: str        # "full", "moderate", "light", "minimal"
    has_gpu: bool
    gpu_model: str | None
    ram_gb: float
    storage_gb: float
    has_camera: bool
    has_microphone: bool
    has_gps: bool
    has_speakers: bool
    network_type: str        # "wired", "wifi", "cellular"
    battery_powered: bool
    can_run_llm: bool        # Has enough RAM/GPU for local inference
    os_type: str             # "windows", "linux", "android", "ios", "macos"
    always_on: bool          # Server/RPi vs laptop/phone
```

Detection is automatic:
- **GPU**: Check for CUDA/ROCm/Metal availability
- **RAM**: `psutil.virtual_memory()`
- **Camera/Mic**: Platform-specific checks
- **GPS**: Android/iOS location services
- **LLM capable**: GPU + 8GB+ VRAM, or CPU + 16GB+ RAM

### resources.py — Live Monitoring

```python
@dataclass
class ResourceSnapshot:
    """Point-in-time resource usage."""
    timestamp: float
    cpu_percent: float
    ram_used_gb: float
    ram_free_gb: float
    gpu_percent: float | None
    gpu_memory_used_gb: float | None
    disk_free_gb: float
    battery_percent: float | None
    battery_charging: bool | None
    network_up_mbps: float
    network_down_mbps: float
    temperature_c: float | None  # CPU temp if available
```

### transport.py — Encrypted WebSocket Client

```python
class WebSocketTransport:
    """WebSocket client with auto-reconnect and message signing."""

    def __init__(self, url, secret_key):
        self.url = url
        self.signer = MessageSigner(secret_key)
        self._ws = None
        self._reconnect_delay = 1  # Exponential backoff

    async def connect(self):
        """Connect with auto-reconnect on failure."""
        ...

    async def send(self, message: dict):
        """Send a signed message."""
        message["signature"] = self.signer.sign(message)
        await self._ws.send(json.dumps(message))
```

## Security Model

### Device Registration

1. First-time setup generates a unique keypair on the device
2. Public key is sent to coordinator during registration
3. Coordinator assigns a Hypernet address and stores the public key
4. All subsequent messages are signed with the device's private key
5. The coordinator verifies signatures before processing any message

### Permission Tiers (Per-Device)

| Device Type | Default Tier | Rationale |
|-------------|-------------|-----------|
| Desktop (Matt's) | T3 External | Trusted, can run arbitrary code |
| Laptop | T2 Collaborative | Trusted but mobile, higher loss risk |
| Phone | T1 Write Own | Limited trust, notification/capture only |
| IoT/RPi | T1 Write Own | Limited capability, sensor only |
| Console | T0 Read Only | Entertainment device, minimal trust |

### Lost/Stolen Device Protocol

1. Matt marks device as compromised via dashboard or chat command (`/revoke 1.1.device.phone`)
2. Coordinator immediately revokes the device's public key
3. All tokens and sessions for that device are invalidated
4. Any data cached on the device is encrypted at rest (AES-256)
5. Next time the device connects, it receives a wipe command
6. Audit log records the revocation event

## Coordinator Integration

The existing `hypernet/server.py` gets new endpoints:

```
POST /mesh/register           — Device registration (returns address + token)
GET  /mesh/nodes              — List all registered devices
GET  /mesh/nodes/{address}    — Device details and health
POST /mesh/nodes/{address}/task — Send a task to a specific device
DELETE /mesh/nodes/{address}  — Revoke device access
GET  /mesh/health             — Mesh-wide health summary
WebSocket /ws/mesh            — Persistent connection for device agents
```

The swarm scheduler gets mesh-aware task routing:
- **"Transcribe this voice memo"** → route to device with microphone + local Whisper
- **"Take a photo of the whiteboard"** → route to phone with camera
- **"Run this GPU-intensive analysis"** → route to desktop with CUDA
- **"Monitor the front door"** → route to Raspberry Pi with camera

## Implementation Phases

### Phase 3a: Single-Machine Agent (Week 4-5)
- Build the `hypernet/mesh/` package
- Agent runs on the same machine as the coordinator
- WebSocket connection, registration, heartbeat
- Basic task execution (run Python function, return result)
- Dashboard shows connected devices

### Phase 3b: LAN Mesh (Week 5-6)
- mDNS discovery of other Hypernet nodes on the same network
- Peer-to-peer file transfer between nodes (no coordinator hop)
- Node-to-node task delegation
- Auto-detect coordinator on the LAN

### Phase 3c: Remote Nodes (Week 6-8)
- WireGuard/Tailscale tunnel for nodes outside the LAN
- NAT traversal for direct connections when possible
- Bandwidth-aware task routing (don't send 10GB to a phone on cellular)
- Multi-coordinator support (mesh has no single point of failure)

### Phase 3d: Mobile Agents (Week 7-8)
- Android: Kotlin/Java companion app or Termux-based Python agent
- iOS: Shortcuts integration + push notifications
- Both: Camera capture, location reporting, notification forwarding

## Dependencies

Minimal — the node agent should run on constrained devices:
- `websockets` — WebSocket client
- `psutil` — System resource monitoring
- `cryptography` — Message signing (already in the project)
- `zeroconf` — mDNS discovery (optional, for LAN discovery)

## Relationship to Existing Code

The Node Agent extends, not replaces, the existing Swarm:
- **Swarm workers** are AI instances that process tasks using LLMs
- **Node agents** are device instances that provide capabilities (sensors, compute, storage)
- The coordinator dispatches tasks to either workers OR nodes based on requirements
- A single device might run both a Node Agent AND a Swarm Worker (Matt's desktop does)
