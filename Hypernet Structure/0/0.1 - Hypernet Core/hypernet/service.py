"""
Hypernet Service Manager — Install/uninstall the swarm as a system service.

Windows: Uses NSSM (Non-Sucking Service Manager) to wrap `python -m hypernet launch`
         as a native Windows service with auto-start and crash recovery.
Linux:   Generates a systemd unit file and enables the service.

Usage:
    python -m hypernet install-service    # Install and start
    python -m hypernet uninstall-service  # Stop and remove
    python -m hypernet service-status     # Check service status
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

SERVICE_NAME = "HypernetSwarm"
SERVICE_DISPLAY = "Hypernet Swarm"
SERVICE_DESCRIPTION = (
    "Hypernet AI Swarm — multi-agent orchestration with "
    "FastAPI server, task queue, and AI workers."
)


# ── Windows (NSSM) ───────────────────────────────────────────────────────


_NSSM_DOWNLOAD_URL = "https://nssm.cc/release/nssm-2.24.zip"


def _find_nssm() -> Optional[str]:
    """Find nssm.exe on PATH or in common locations."""
    # Check PATH first
    nssm = shutil.which("nssm")
    if nssm:
        return nssm
    # Check common install locations (including our auto-download and winget locations)
    tools_dir = Path(__file__).parent.parent / "tools"
    local_appdata = Path(os.environ.get("LOCALAPPDATA", ""))
    winget_links = local_appdata / "Microsoft" / "WinGet" / "Links"
    for candidate in [
        tools_dir / "nssm" / "win64" / "nssm.exe",
        winget_links / "nssm.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "nssm" / "win64" / "nssm.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "nssm" / "win32" / "nssm.exe",
        Path.home() / "nssm" / "nssm.exe",
        Path("nssm.exe"),
    ]:
        if candidate.exists():
            return str(candidate)
    return None


def _download_nssm() -> Optional[str]:
    """Auto-download NSSM to the tools/ directory.

    Downloads from nssm.cc, extracts the zip, and returns the path
    to nssm.exe. Returns None if download fails.
    """
    import io
    import zipfile
    import urllib.request

    tools_dir = Path(__file__).parent.parent / "tools" / "nssm"
    if tools_dir.exists():
        # Check if already downloaded
        exe = tools_dir / "win64" / "nssm.exe"
        if exe.exists():
            return str(exe)

    print("  Downloading NSSM (one-time setup)...")
    try:
        req = urllib.request.Request(
            _NSSM_DOWNLOAD_URL,
            headers={"User-Agent": "Hypernet/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()

        # Extract zip
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            # Find the nssm.exe files inside the zip
            for info in zf.infolist():
                # nssm-2.24/win64/nssm.exe → tools/nssm/win64/nssm.exe
                parts = info.filename.split("/")
                if len(parts) >= 3 and parts[-1] == "nssm.exe":
                    arch_dir = parts[-2]  # win32 or win64
                    target = tools_dir / arch_dir / "nssm.exe"
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(zf.read(info))

        exe = tools_dir / "win64" / "nssm.exe"
        if exe.exists():
            print(f"  NSSM downloaded to: {exe}")
            return str(exe)
        # Fallback to win32
        exe32 = tools_dir / "win32" / "nssm.exe"
        if exe32.exists():
            print(f"  NSSM downloaded to: {exe32}")
            return str(exe32)

    except Exception as e:
        print(f"  Failed to download NSSM: {e}")
    return None


def _nssm_run(args: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run an NSSM command. Auto-downloads NSSM if not found."""
    nssm = _find_nssm()
    if not nssm:
        # Try auto-download
        nssm = _download_nssm()
    if not nssm:
        raise FileNotFoundError(
            "NSSM not found and auto-download failed.\n"
            "  Install manually from https://nssm.cc/download\n"
            "  1. Download nssm-2.24.zip\n"
            "  2. Extract nssm.exe to a folder on your PATH\n"
            "  3. Or place it next to this script"
        )
    cmd = [nssm] + args
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def install_windows(
    working_dir: Optional[str] = None,
    port: int = 8000,
    log_dir: Optional[str] = None,
) -> bool:
    """Install the Hypernet Swarm as a Windows service via NSSM."""
    python = sys.executable
    working_dir = working_dir or str(Path(__file__).parent.parent)
    log_dir = log_dir or str(Path(working_dir) / "data" / "logs")

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    print(f"Installing {SERVICE_DISPLAY} as a Windows service...")
    print(f"  Python:      {python}")
    print(f"  Working dir: {working_dir}")
    print(f"  Port:        {port}")
    print(f"  Logs:        {log_dir}")
    print()

    try:
        # Remove existing service if present (ignore errors)
        _nssm_run(["stop", SERVICE_NAME], check=False)
        _nssm_run(["remove", SERVICE_NAME, "confirm"], check=False)

        # Install the service
        _nssm_run(["install", SERVICE_NAME, python, "-m hypernet launch --no-browser"])

        # Configure service parameters
        configs = {
            "AppDirectory": working_dir,
            "DisplayName": SERVICE_DISPLAY,
            "Description": SERVICE_DESCRIPTION,
            "Start": "SERVICE_AUTO_START",
            "AppStdout": str(Path(log_dir) / "service-stdout.log"),
            "AppStderr": str(Path(log_dir) / "service-stderr.log"),
            "AppStdoutCreationDisposition": "4",  # Append
            "AppStderrCreationDisposition": "4",  # Append
            "AppRotateFiles": "1",
            "AppRotateBytes": "10485760",  # 10MB
            "AppEnvironmentExtra": f"HYPERNET_SERVICE=1",
        }
        for key, value in configs.items():
            _nssm_run(["set", SERVICE_NAME, key, value])

        # Start the service
        print("Starting service...")
        result = _nssm_run(["start", SERVICE_NAME], check=False)
        if result.returncode == 0:
            print(f"\n  {SERVICE_DISPLAY} installed and started successfully!")
            print(f"  Dashboard: http://localhost:{port}/swarm/dashboard")
            print(f"  Home:      http://localhost:{port}/home")
            print()
            print("  The swarm will auto-start when Windows boots.")
            print("  To stop:   python -m hypernet uninstall-service")
            print("  To check:  python -m hypernet service-status")
            return True
        else:
            print(f"  Service installed but failed to start: {result.stderr}")
            print("  Try: nssm start HypernetSwarm")
            return False

    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: NSSM command failed: {e.stderr}")
        return False


def uninstall_windows() -> bool:
    """Stop and remove the Windows service."""
    print(f"Removing {SERVICE_DISPLAY} service...")
    try:
        _nssm_run(["stop", SERVICE_NAME], check=False)
        result = _nssm_run(["remove", SERVICE_NAME, "confirm"], check=False)
        if result.returncode == 0:
            print(f"  {SERVICE_DISPLAY} removed successfully.")
            return True
        else:
            print(f"  Could not remove service: {result.stderr}")
            return False
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
        return False


def status_windows() -> dict:
    """Check Windows service status.

    Tries NSSM first, falls back to native `sc query` if NSSM isn't available.
    """
    # Try NSSM first
    nssm = _find_nssm()
    if nssm:
        try:
            result = subprocess.run(
                [nssm, "status", SERVICE_NAME],
                capture_output=True, text=True, check=False,
            )
            status = result.stdout.strip()
            if status:
                return {"installed": True, "status": status, "name": SERVICE_NAME}
        except Exception:
            pass

    # Fallback: native Windows sc query
    try:
        result = subprocess.run(
            ["sc", "query", SERVICE_NAME],
            capture_output=True, text=True, check=False,
        )
        if result.returncode == 0 and "STATE" in result.stdout:
            # Parse service state from sc output
            for line in result.stdout.splitlines():
                if "STATE" in line:
                    if "RUNNING" in line:
                        return {"installed": True, "status": "running", "name": SERVICE_NAME}
                    elif "STOPPED" in line:
                        return {"installed": True, "status": "stopped", "name": SERVICE_NAME}
                    else:
                        state = line.strip().split()[-1] if line.strip() else "unknown"
                        return {"installed": True, "status": state, "name": SERVICE_NAME}
        # Service not found
        return {"installed": False, "status": "not_installed", "name": SERVICE_NAME}
    except FileNotFoundError:
        return {"installed": False, "status": "not_installed", "name": SERVICE_NAME}


# ── Linux (systemd) ──────────────────────────────────────────────────────


SYSTEMD_UNIT = """[Unit]
Description={display_name}
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={working_dir}
ExecStart={python} -m hypernet launch --no-browser
Restart=always
RestartSec=5
StartLimitBurst=5
StartLimitIntervalSec=600
StandardOutput=journal
StandardError=journal
Environment=HYPERNET_SERVICE=1

[Install]
WantedBy=multi-user.target
"""


def _systemd_unit_path() -> Path:
    return Path("/etc/systemd/system/hypernet-swarm.service")


def install_linux(
    working_dir: Optional[str] = None,
    user: Optional[str] = None,
) -> bool:
    """Install the Hypernet Swarm as a systemd service."""
    python = sys.executable
    working_dir = working_dir or str(Path(__file__).parent.parent)
    user = user or os.environ.get("USER", "hypernet")
    unit_path = _systemd_unit_path()

    print(f"Installing {SERVICE_DISPLAY} as a systemd service...")
    print(f"  Python:      {python}")
    print(f"  Working dir: {working_dir}")
    print(f"  User:        {user}")
    print(f"  Unit file:   {unit_path}")
    print()

    unit_content = SYSTEMD_UNIT.format(
        display_name=SERVICE_DISPLAY,
        user=user,
        working_dir=working_dir,
        python=python,
    )

    try:
        unit_path.write_text(unit_content)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "hypernet-swarm"], check=True)
        subprocess.run(["systemctl", "start", "hypernet-swarm"], check=True)

        print(f"\n  {SERVICE_DISPLAY} installed and started!")
        print("  Commands:")
        print("    systemctl status hypernet-swarm")
        print("    journalctl -u hypernet-swarm -f")
        print("    systemctl stop hypernet-swarm")
        return True

    except PermissionError:
        print(f"  ERROR: Need root access to write to {unit_path}")
        print(f"  Try: sudo python -m hypernet install-service")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: systemctl command failed: {e}")
        return False


def uninstall_linux() -> bool:
    """Stop and remove the systemd service."""
    print(f"Removing {SERVICE_DISPLAY} systemd service...")
    try:
        subprocess.run(["systemctl", "stop", "hypernet-swarm"], check=False)
        subprocess.run(["systemctl", "disable", "hypernet-swarm"], check=False)
        unit_path = _systemd_unit_path()
        if unit_path.exists():
            unit_path.unlink()
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        print(f"  {SERVICE_DISPLAY} removed.")
        return True
    except PermissionError:
        print("  ERROR: Need root access. Try: sudo python -m hypernet uninstall-service")
        return False


def status_linux() -> dict:
    """Check systemd service status."""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "hypernet-swarm"],
            capture_output=True, text=True, check=False,
        )
        state = result.stdout.strip()
        return {"installed": True, "status": state, "name": "hypernet-swarm"}
    except FileNotFoundError:
        return {"installed": False, "status": "systemctl_not_found", "name": "hypernet-swarm"}


# ── Cross-platform dispatchers ───────────────────────────────────────────


def install_service(**kwargs) -> bool:
    """Install the swarm as a system service (auto-detects platform)."""
    if sys.platform == "win32":
        return install_windows(**kwargs)
    elif sys.platform.startswith("linux"):
        return install_linux(**kwargs)
    else:
        print(f"Service installation not yet supported on {sys.platform}")
        print("Contributions welcome!")
        return False


def uninstall_service() -> bool:
    """Remove the swarm system service."""
    if sys.platform == "win32":
        return uninstall_windows()
    elif sys.platform.startswith("linux"):
        return uninstall_linux()
    else:
        print(f"Service removal not yet supported on {sys.platform}")
        return False


def service_status() -> dict:
    """Check service status."""
    if sys.platform == "win32":
        return status_windows()
    elif sys.platform.startswith("linux"):
        return status_linux()
    else:
        return {"installed": False, "status": "unsupported_platform", "name": SERVICE_NAME}


def print_status():
    """Print human-readable service status."""
    info = service_status()
    print(f"Service: {info['name']}")
    if not info["installed"]:
        print(f"  Status: not installed")
        print(f"  Install with: python -m hypernet install-service")
    else:
        print(f"  Status: {info['status']}")
        if info["status"] in ("SERVICE_RUNNING", "active"):
            print(f"  The swarm is running as a system service.")
        elif info["status"] in ("SERVICE_STOPPED", "inactive"):
            print(f"  The service is installed but not running.")
            if sys.platform == "win32":
                print(f"  Start with: nssm start {SERVICE_NAME}")
            else:
                print(f"  Start with: systemctl start hypernet-swarm")
