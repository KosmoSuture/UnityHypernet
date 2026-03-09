"""
Hypernet Unified Launcher

One command to start everything:
    python -m hypernet launch

Starts:
  1. FastAPI server (REST API, dashboards)
  2. Swarm orchestrator (AI workers)
  3. Opens browser to the home page

Auto-detects the archive root by looking for 'Hypernet Structure' in
parent directories, so you never need to remember --archive ../..

Usage:
    cd "c:/Hypernet/Hypernet Structure/0/0.1 - Hypernet Core"
    python -m hypernet launch

    # Or from anywhere with explicit paths:
    python -m hypernet launch --archive "c:/Hypernet/Hypernet Structure"
"""

from __future__ import annotations

import logging
import os
import signal
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


def find_archive_root(start: Optional[str] = None) -> str:
    """Auto-detect the Hypernet Structure root directory.

    Walks up from the current directory (or start) looking for a directory
    that contains the signature Hypernet Structure layout.

    Returns the path, or "." as fallback.
    """
    search = Path(start or os.getcwd()).resolve()

    # Check if we're inside the archive already
    for path in [search] + list(search.parents):
        # Look for telltale directories
        if (path / "0").is_dir() and (path / "1 - People").is_dir():
            return str(path)

        # Check if this IS "Hypernet Structure"
        if path.name == "Hypernet Structure":
            return str(path)

        # Check for a "Hypernet Structure" child
        hs = path / "Hypernet Structure"
        if hs.is_dir() and (hs / "0").is_dir():
            return str(hs)

    # Fallback: try relative paths from common locations
    for rel in ["../..", "../../Hypernet Structure", "../Hypernet Structure"]:
        candidate = (search / rel).resolve()
        if candidate.is_dir() and (candidate / "0").is_dir():
            return str(candidate)

    log.warning("Could not auto-detect archive root. Using '.'")
    return "."


def launch(
    data_dir: str = "data",
    host: str = "0.0.0.0",
    port: int = 8000,
    archive_root: Optional[str] = None,
    no_browser: bool = False,
    no_swarm: bool = False,
    mock: bool = False,
    verbose: bool = False,
):
    """Launch the Hypernet: server + swarm + browser.

    This is the unified entry point. One command, one tab, everything connected.
    """
    # Configure persistent logging (file + console + in-memory)
    from .log_config import setup_logging
    log_dir = setup_logging(data_dir=data_dir, verbose=verbose)

    # Auto-detect archive root
    if not archive_root:
        archive_root = find_archive_root()

    print(flush=True)
    print("=" * 60, flush=True)
    print("  H Y P E R N E T", flush=True)
    print("  One command. One tab. Everything connected.", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)
    print(f"  Data:      {data_dir}", flush=True)
    print(f"  Archive:   {archive_root}", flush=True)
    print(f"  Port:      {port}", flush=True)
    print(f"  Mode:      {'mock' if mock else 'live'}", flush=True)
    print(flush=True)

    # ── Step 1: Build swarm (if enabled) ──
    swarm = None
    web_messenger = None

    if not no_swarm:
        try:
            from .swarm_factory import build_swarm

            print("  [1/3] Building swarm...")
            swarm, web_messenger = build_swarm(
                data_dir=data_dir,
                archive_root=archive_root,
                mock=mock,
            )
            workers = list(swarm.workers.keys()) if swarm.workers else []
            print(f"         {len(workers)} workers: {', '.join(workers)}")
        except ImportError as e:
            print(f"  [1/3] Swarm not available: {e}")
        except Exception as e:
            print(f"  [1/3] Swarm failed to build: {e}")
            log.exception("Swarm build failed")
    else:
        print("  [1/3] Swarm disabled (--no-swarm)")

    # ── Step 2: Start web server ──
    print("  [2/3] Starting web server...")
    try:
        from .server import create_app, attach_swarm
        import uvicorn

        app = create_app(data_dir=data_dir)
        app.state._archive_root = archive_root
        app.state._data_dir = data_dir

        if swarm and web_messenger:
            attach_swarm(app, swarm, web_messenger)

        server_config = uvicorn.Config(
            app, host=host, port=port,
            log_level="warning",
        )
        server = uvicorn.Server(server_config)

        server_thread = threading.Thread(target=server.run, daemon=True)
        server_thread.start()

        # Wait for server to be ready
        for _ in range(20):
            time.sleep(0.25)
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect(("127.0.0.1", port))
                s.close()
                break
            except (ConnectionRefusedError, OSError):
                continue

        home_url = f"http://localhost:{port}/home"
        print(f"         Server ready at http://localhost:{port}")
        print()
    except ImportError:
        print("  Server requires FastAPI and uvicorn.")
        print("  Install with: pip install fastapi uvicorn")
        sys.exit(1)

    # ── Step 3: Open browser ──
    if not no_browser:
        print("  [3/3] Opening browser...")
        try:
            webbrowser.open(home_url)
            print(f"         Opened {home_url}")
        except Exception:
            print(f"         Could not open browser. Go to: {home_url}")
    else:
        print(f"  [3/3] Browser: {home_url}")

    print()
    print("-" * 60)
    print(f"  Home:      {home_url}")
    print(f"  Dashboard: http://localhost:{port}/swarm/dashboard")
    print(f"  Chat:      http://localhost:{port}/chat")
    print(f"  Life Story: http://localhost:{port}/lifestory")
    print(f"  API Docs:  http://localhost:{port}/docs")
    print("-" * 60)
    print()
    print("  Press Ctrl+C to shut down.")
    print()

    # ── Run swarm (blocks until Ctrl+C) ──
    def signal_handler(sig, frame):
        print("\n  Shutting down...")
        if swarm:
            swarm._running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if swarm:
        try:
            swarm.run()
        except KeyboardInterrupt:
            print("\n  Shutdown complete.")
            return

        # ── Auto-reboot: restart the process if the swarm requested it ──
        if getattr(swarm, "_reboot_requested", False):
            _handle_reboot()
            return  # If _handle_reboot returns, it means restart was suppressed
    else:
        # No swarm — just keep the server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n  Shutdown complete.")


# Reboot storm protection — persisted as env vars across os.execv restarts
_REBOOT_MAX_COUNT = 5
_REBOOT_WINDOW_SECONDS = 600  # 10 minutes
_REBOOT_COOLDOWN_SECONDS = 30


def _handle_reboot():
    """Re-exec the Python process to reload all modules after code changes.

    Tracks reboot count and timestamps via environment variables to prevent
    restart storms. If more than 5 reboots occur within 10 minutes, logs a
    warning and stops.

    Uses os.execv to replace the current process — all modules are freshly
    imported, but the server thread is replaced too (uvicorn starts fresh).
    """
    now = time.time()

    # Read reboot history from env (survives os.execv)
    reboot_times_str = os.environ.get("_HYPERNET_REBOOT_TIMES", "")
    reboot_times = []
    if reboot_times_str:
        try:
            reboot_times = [float(t) for t in reboot_times_str.split(",") if t.strip()]
        except (ValueError, TypeError):
            reboot_times = []

    # Filter to only reboots within the window
    cutoff = now - _REBOOT_WINDOW_SECONDS
    reboot_times = [t for t in reboot_times if t > cutoff]

    # Check cooldown — don't reboot if the last one was too recent
    if reboot_times and (now - reboot_times[-1]) < _REBOOT_COOLDOWN_SECONDS:
        wait = _REBOOT_COOLDOWN_SECONDS - (now - reboot_times[-1])
        log.warning(
            f"Reboot cooldown active — last reboot was {now - reboot_times[-1]:.0f}s ago. "
            f"Waiting {wait:.0f}s would be needed. Suppressing this reboot."
        )
        return

    # Check storm protection
    if len(reboot_times) >= _REBOOT_MAX_COUNT:
        log.warning(
            f"Reboot storm detected: {len(reboot_times)} reboots in the last "
            f"{_REBOOT_WINDOW_SECONDS // 60} minutes. Stopping auto-reboot. "
            f"Fix the issue and restart manually."
        )
        print(
            f"\n  WARNING: {len(reboot_times)} reboots in {_REBOOT_WINDOW_SECONDS // 60} minutes. "
            f"Auto-reboot disabled to prevent restart storm."
        )
        return

    # Record this reboot
    reboot_times.append(now)
    os.environ["_HYPERNET_REBOOT_TIMES"] = ",".join(str(t) for t in reboot_times)

    reboot_count = len(reboot_times)
    print(flush=True)
    print("=" * 60, flush=True)
    print(f"  AUTO-REBOOT #{reboot_count} — Reloading all modules...", flush=True)
    print("=" * 60, flush=True)
    print(flush=True)
    log.info(f"Auto-reboot #{reboot_count}: re-execing process with {sys.executable}")

    # Re-exec: use -m invocation to avoid Windows spaces-in-paths issues
    # sys.argv may contain paths like "c:\Hypernet\Hypernet Structure\..."
    # which os.execv on Windows can mangle at spaces.
    import subprocess
    args = [sys.executable, "-m", "hypernet", "launch"]
    # Preserve any extra CLI flags from original invocation
    # (skip argv[0] which is the script path, and 'launch' if present)
    extra = [a for a in sys.argv[1:] if a != "launch"]
    args.extend(extra)
    os.execv(sys.executable, args)
