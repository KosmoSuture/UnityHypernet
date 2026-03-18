"""
Hypernet System Tray Companion

Lightweight system tray icon that provides user-facing control of the
Hypernet Swarm service. Sits in the notification area and gives quick
access to the dashboard, service controls, and logs.

Features:
  - Hypernet icon in system tray (Windows, macOS, Linux via pystray)
  - Menu: Open Dashboard, Open Chat, Start/Stop Service, View Logs, Status
  - Toast notifications on swarm events (requires Windows 10+)
  - Auto-refresh service status every 10 seconds

Requirements:
  pip install pystray Pillow

Usage:
  python -m hypernet tray          # Start the tray companion
  python -m hypernet tray --port 8000  # Custom port

The tray companion can run alongside the swarm (whether launched via
`python -m hypernet launch` or running as a Windows service via NSSM).
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# Default dashboard URL
DEFAULT_PORT = 8000
REFRESH_INTERVAL = 10  # seconds between status checks


def _check_server_running(port: int = DEFAULT_PORT) -> bool:
    """Check if the Hypernet server is responding on the given port."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False


def _get_service_status() -> str:
    """Get the current service status as a human-readable string."""
    try:
        from .service import service_status
        info = service_status()
        if not info["installed"]:
            return "Not installed"
        status = info["status"]
        if status in ("SERVICE_RUNNING", "active"):
            return "Running (service)"
        elif status in ("SERVICE_STOPPED", "inactive"):
            return "Stopped"
        return status
    except Exception:
        return "Unknown"


def _create_icon_image(running: bool = False):
    """Create a simple Hypernet icon.

    Green "H" on dark background when running, gray when stopped.
    """
    from PIL import Image, ImageDraw, ImageFont

    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle
    bg_color = (34, 139, 34, 230) if running else (100, 100, 100, 200)
    draw.ellipse([2, 2, size - 2, size - 2], fill=bg_color)

    # "H" letter — try platform-appropriate fonts, fall back gracefully
    text_color = (255, 255, 255, 255)
    font = None
    font_candidates = [
        "arial.ttf",           # Windows
        "Arial.ttf",           # macOS
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux (Debian/Ubuntu)
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",              # Linux (Arch)
        "/System/Library/Fonts/Helvetica.ttc",                    # macOS fallback
    ]
    for font_path in font_candidates:
        try:
            font = ImageFont.truetype(font_path, 36)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default(size=28)

    # Center the H
    bbox = draw.textbbox((0, 0), "H", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2
    y = (size - th) // 2 - 2
    draw.text((x, y), "H", fill=text_color, font=font)

    return img


def run_tray(port: int = DEFAULT_PORT):
    """Run the system tray companion.

    Blocks until the user clicks Quit.
    """
    try:
        import pystray
        from pystray import MenuItem, Menu
    except ImportError:
        print("System tray requires pystray and Pillow.")
        print("Install with: pip install pystray Pillow")
        sys.exit(1)

    # State
    current_status = {"running": False, "service": "Unknown"}

    def update_status():
        """Refresh status in background."""
        while True:
            try:
                current_status["running"] = _check_server_running(port)
                current_status["service"] = _get_service_status()
                # Update icon based on status
                if hasattr(icon, "icon"):
                    icon.icon = _create_icon_image(current_status["running"])
            except Exception:
                pass
            time.sleep(REFRESH_INTERVAL)

    def open_dashboard(icon_ref, item):
        webbrowser.open(f"http://localhost:{port}/swarm/dashboard")

    def open_home(icon_ref, item):
        webbrowser.open(f"http://localhost:{port}/home")

    def open_chat(icon_ref, item):
        webbrowser.open(f"http://localhost:{port}/chat")

    def open_lifestory(icon_ref, item):
        webbrowser.open(f"http://localhost:{port}/lifestory")

    def open_vr(icon_ref, item):
        webbrowser.open(f"http://localhost:{port}/vr")

    def start_service(icon_ref, item):
        """Start the swarm service or launch directly."""
        try:
            from .service import service_status as svc_status
            info = svc_status()
            if info["installed"]:
                if sys.platform == "win32":
                    subprocess.run(
                        ["nssm", "start", "HypernetSwarm"],
                        capture_output=True,
                    )
                else:
                    subprocess.run(
                        ["systemctl", "start", "hypernet-swarm"],
                        capture_output=True,
                    )
            else:
                # No service installed — launch directly
                core_dir = Path(__file__).parent.parent
                subprocess.Popen(
                    [sys.executable, "-m", "hypernet", "launch", "--no-browser"],
                    cwd=str(core_dir),
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
        except Exception as e:
            log.error(f"Failed to start service: {e}")

    def stop_service(icon_ref, item):
        """Stop the swarm service."""
        try:
            from .service import service_status as svc_status
            info = svc_status()
            if info["installed"]:
                if sys.platform == "win32":
                    subprocess.run(
                        ["nssm", "stop", "HypernetSwarm"],
                        capture_output=True,
                    )
                else:
                    subprocess.run(
                        ["systemctl", "stop", "hypernet-swarm"],
                        capture_output=True,
                    )
            else:
                # Try to kill the process by port
                if sys.platform == "win32":
                    subprocess.run(
                        ["powershell", "-Command",
                         f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | "
                         f"ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force }}"],
                        capture_output=True,
                    )
        except Exception as e:
            log.error(f"Failed to stop service: {e}")

    def open_logs(icon_ref, item):
        """Open the log directory in file explorer."""
        log_dir = Path(__file__).parent.parent / "data" / "logs"
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(log_dir))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(log_dir)])
        else:
            subprocess.run(["xdg-open", str(log_dir)])

    def install_service_action(icon_ref, item):
        """Install the swarm as a system service."""
        try:
            from .service import install_service
            install_service()
        except Exception as e:
            log.error(f"Failed to install service: {e}")

    def toggle_autostart(icon_ref, item):
        """Add/remove tray from Windows Startup folder."""
        if sys.platform != "win32":
            return
        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        shortcut_path = startup_dir / "Hypernet Tray.bat"
        if shortcut_path.exists():
            shortcut_path.unlink()
        else:
            core_dir = Path(__file__).parent.parent
            shortcut_path.write_text(
                f'@echo off\r\n'
                f'cd /d "{core_dir}"\r\n'
                f'start /min "" python -m hypernet tray\r\n',
                encoding="utf-8",
            )

    def autostart_checked(item):
        """Check if autostart is enabled."""
        if sys.platform != "win32":
            return False
        startup_dir = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        return (startup_dir / "Hypernet Tray.bat").exists()

    def show_status(icon_ref, item):
        """Show current status (displayed as disabled menu item)."""
        pass

    def on_quit(icon_ref, item):
        icon_ref.stop()

    def status_text(item):
        """Dynamic menu text showing current status."""
        running = current_status["running"]
        svc = current_status["service"]
        if running:
            return f"Status: Running ({svc})"
        return f"Status: Stopped ({svc})"

    def is_running(item):
        return current_status["running"]

    def is_stopped(item):
        return not current_status["running"]

    # Build menu
    menu = Menu(
        MenuItem(status_text, show_status, enabled=False),
        Menu.SEPARATOR,
        MenuItem("Open Home", open_home, default=True),
        MenuItem("Open Dashboard", open_dashboard),
        MenuItem("Open Chat", open_chat),
        MenuItem("Life Story", open_lifestory),
        MenuItem("VR Browser", open_vr),
        Menu.SEPARATOR,
        MenuItem("Start Swarm", start_service, visible=is_stopped),
        MenuItem("Stop Swarm", stop_service, visible=is_running),
        Menu.SEPARATOR,
        MenuItem("View Logs", open_logs),
        MenuItem("Install as Service", install_service_action),
        MenuItem("Start with Windows", toggle_autostart, checked=autostart_checked),
        Menu.SEPARATOR,
        MenuItem("Quit Tray", on_quit),
    )

    # Create icon
    is_running_now = _check_server_running(port)
    current_status["running"] = is_running_now
    icon = pystray.Icon(
        "hypernet",
        _create_icon_image(is_running_now),
        "Hypernet Swarm",
        menu,
    )

    # Start status refresh thread
    status_thread = threading.Thread(target=update_status, daemon=True)
    status_thread.start()

    # Run (blocks until quit)
    icon.run()
