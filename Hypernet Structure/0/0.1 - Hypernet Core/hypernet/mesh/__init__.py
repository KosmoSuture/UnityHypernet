"""
Hypernet Node Agent — Device mesh network client.

Each device in the mesh runs a lightweight Node Agent that registers
with the swarm coordinator, reports capabilities and health, and
executes tasks dispatched by the coordinator.

Phase 3 of the Swarm Upgrade Plan.

Usage:
    python -m hypernet node --coordinator ws://10.0.0.1:8000/ws/mesh
"""

__version__ = "0.1.0"

from .capabilities import DeviceCapabilities, detect_capabilities
from .resources import ResourceMonitor, ResourceSnapshot
from .agent import NodeAgent
