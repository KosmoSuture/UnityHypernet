"""
Device capability detection.

Auto-detects what the current device can do: GPU, camera, microphone,
storage, network type, LLM capability, etc. Used during node registration
to tell the coordinator what tasks this device can handle.
"""

from __future__ import annotations

import logging
import os
import platform
import shutil
import sys
from dataclasses import dataclass, asdict
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class DeviceCapabilities:
    """What this device can do."""

    compute_tier: str = "light"         # "full", "moderate", "light", "minimal"
    has_gpu: bool = False
    gpu_model: Optional[str] = None
    gpu_vram_gb: Optional[float] = None
    cpu_cores: int = 1
    ram_gb: float = 0.0
    storage_free_gb: float = 0.0
    has_camera: bool = False
    has_microphone: bool = False
    has_gps: bool = False
    has_speakers: bool = False
    network_type: str = "unknown"       # "wired", "wifi", "cellular"
    battery_powered: bool = False
    can_run_llm: bool = False
    os_type: str = "unknown"
    os_version: str = ""
    hostname: str = ""
    always_on: bool = False             # Server/RPi vs laptop/phone
    python_version: str = ""

    def to_dict(self) -> dict:
        """Serialize for registration message."""
        return asdict(self)


def detect_capabilities() -> DeviceCapabilities:
    """Auto-detect device capabilities. Best-effort — never raises."""
    caps = DeviceCapabilities()

    # Basic system info
    caps.os_type = _detect_os_type()
    caps.os_version = platform.version()
    caps.hostname = platform.node()
    caps.python_version = platform.python_version()

    # CPU
    try:
        caps.cpu_cores = os.cpu_count() or 1
    except Exception:
        pass

    # RAM
    try:
        import psutil
        mem = psutil.virtual_memory()
        caps.ram_gb = round(mem.total / (1024 ** 3), 1)
    except ImportError:
        log.debug("psutil not available — RAM detection skipped")
    except Exception:
        pass

    # Storage
    try:
        usage = shutil.disk_usage("/")
        caps.storage_free_gb = round(usage.free / (1024 ** 3), 1)
    except Exception:
        try:
            usage = shutil.disk_usage("C:\\")
            caps.storage_free_gb = round(usage.free / (1024 ** 3), 1)
        except Exception:
            pass

    # GPU (CUDA check)
    caps.has_gpu, caps.gpu_model, caps.gpu_vram_gb = _detect_gpu()

    # Compute tier
    caps.compute_tier = _compute_tier(caps)

    # LLM capability: GPU with 8GB+ VRAM or CPU with 16GB+ RAM
    if caps.has_gpu and caps.gpu_vram_gb and caps.gpu_vram_gb >= 6:
        caps.can_run_llm = True
    elif caps.ram_gb >= 16:
        caps.can_run_llm = True

    # Battery
    try:
        import psutil
        battery = psutil.sensors_battery()
        caps.battery_powered = battery is not None
    except Exception:
        pass

    # Always-on heuristic: not battery-powered + server-class OS
    caps.always_on = not caps.battery_powered

    # Network type (heuristic)
    caps.network_type = _detect_network_type()

    log.info(
        "Device capabilities: %s, %d cores, %.1f GB RAM, GPU=%s, LLM=%s",
        caps.compute_tier, caps.cpu_cores, caps.ram_gb,
        caps.gpu_model or "none", caps.can_run_llm,
    )
    return caps


def _detect_os_type() -> str:
    """Detect the operating system type."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        # Check for Android (Termux)
        if "ANDROID_ROOT" in os.environ or "TERMUX_VERSION" in os.environ:
            return "android"
        return "linux"
    elif system == "darwin":
        return "macos"
    return system


def _detect_gpu() -> tuple[bool, Optional[str], Optional[float]]:
    """Try to detect GPU. Returns (has_gpu, model, vram_gb)."""
    # Try torch first (most reliable)
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_mem / (1024 ** 3)
            return True, name, round(vram, 1)
    except ImportError:
        pass
    except Exception:
        pass

    # Try nvidia-smi
    try:
        import subprocess
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            parts = result.stdout.strip().split(",")
            name = parts[0].strip()
            vram_mb = float(parts[1].strip())
            return True, name, round(vram_mb / 1024, 1)
    except Exception:
        pass

    return False, None, None


def _compute_tier(caps: DeviceCapabilities) -> str:
    """Classify the device's compute capability."""
    if caps.has_gpu and caps.ram_gb >= 16:
        return "full"
    elif caps.ram_gb >= 8 and caps.cpu_cores >= 4:
        return "moderate"
    elif caps.ram_gb >= 4:
        return "light"
    return "minimal"


def _detect_network_type() -> str:
    """Best-effort network type detection."""
    try:
        import psutil
        stats = psutil.net_if_stats()
        for name, info in stats.items():
            if not info.isup:
                continue
            name_lower = name.lower()
            if "eth" in name_lower or "enp" in name_lower:
                return "wired"
            if "wlan" in name_lower or "wi-fi" in name_lower or "wifi" in name_lower:
                return "wifi"
            if "wwan" in name_lower or "rmnet" in name_lower:
                return "cellular"
    except Exception:
        pass
    return "unknown"
