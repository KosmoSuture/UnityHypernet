"""
Live resource monitoring for the node agent.

Collects CPU, RAM, GPU, disk, battery, network stats at regular
intervals. Used for heartbeat messages and task scheduling decisions.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, asdict
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class ResourceSnapshot:
    """Point-in-time resource usage."""

    timestamp: float = 0.0
    cpu_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_free_gb: float = 0.0
    ram_percent: float = 0.0
    gpu_percent: Optional[float] = None
    gpu_memory_used_gb: Optional[float] = None
    gpu_memory_free_gb: Optional[float] = None
    disk_free_gb: float = 0.0
    battery_percent: Optional[float] = None
    battery_charging: Optional[bool] = None
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    temperature_c: Optional[float] = None
    process_count: int = 0

    def to_dict(self) -> dict:
        """Serialize for heartbeat message."""
        return asdict(self)

    @property
    def is_busy(self) -> bool:
        """Heuristic: is the device currently under heavy load?"""
        return self.cpu_percent > 80 or self.ram_percent > 90

    @property
    def is_low_battery(self) -> bool:
        """Is the device on low battery?"""
        if self.battery_percent is None:
            return False
        return self.battery_percent < 20 and not self.battery_charging


class ResourceMonitor:
    """Collects resource snapshots using psutil.

    If psutil is not installed, returns zero-filled snapshots.
    """

    def __init__(self) -> None:
        self._has_psutil = False
        try:
            import psutil
            self._psutil = psutil
            self._has_psutil = True
        except ImportError:
            self._psutil = None
            log.warning("psutil not available — resource monitoring will be limited")
        self._last_net = None
        self._last_net_time = 0.0

    def snapshot(self) -> ResourceSnapshot:
        """Take a resource snapshot. Never raises."""
        snap = ResourceSnapshot(timestamp=time.time())

        if not self._has_psutil:
            return snap

        try:
            # CPU
            snap.cpu_percent = self._psutil.cpu_percent(interval=0.1)

            # RAM
            mem = self._psutil.virtual_memory()
            snap.ram_used_gb = round((mem.total - mem.available) / (1024 ** 3), 2)
            snap.ram_free_gb = round(mem.available / (1024 ** 3), 2)
            snap.ram_percent = mem.percent

            # Disk
            try:
                import shutil
                usage = shutil.disk_usage("/")
                snap.disk_free_gb = round(usage.free / (1024 ** 3), 1)
            except Exception:
                try:
                    import shutil
                    usage = shutil.disk_usage("C:\\")
                    snap.disk_free_gb = round(usage.free / (1024 ** 3), 1)
                except Exception:
                    pass

            # Battery
            battery = self._psutil.sensors_battery()
            if battery:
                snap.battery_percent = battery.percent
                snap.battery_charging = battery.power_plugged

            # Temperature
            try:
                temps = self._psutil.sensors_temperatures()
                if temps:
                    # Get the first available CPU temperature
                    for name, entries in temps.items():
                        if entries:
                            snap.temperature_c = entries[0].current
                            break
            except (AttributeError, NotImplementedError):
                pass  # Not available on all platforms

            # Network I/O
            net = self._psutil.net_io_counters()
            snap.network_bytes_sent = net.bytes_sent
            snap.network_bytes_recv = net.bytes_recv

            # Process count
            snap.process_count = len(self._psutil.pids())

        except Exception as e:
            log.debug("Resource snapshot error: %s", e)

        return snap
