"""
Hypernet Logging Configuration

Sets up persistent, rotating file-based logging so errors don't vanish
into the console void. Every WARNING and above gets written to disk.
The swarm can read its own errors. Humans can review them later.

Log files:
  data/logs/hypernet.log      — all INFO+ messages (rotates at 5MB, keeps 5)
  data/logs/errors.log        — WARNING+ only (rotates at 2MB, keeps 10)

API access:
  GET /logs/recent             — last N log entries
  GET /logs/errors             — recent errors only

Usage:
    from hypernet.log_config import setup_logging
    setup_logging(data_dir="data", verbose=False)
"""

from __future__ import annotations

import json
import logging
import os
import threading
from collections import deque
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


# In-memory ring buffer for API access
_recent_logs: deque = deque(maxlen=500)
_recent_errors: deque = deque(maxlen=200)
_log_lock = threading.Lock()


class InMemoryHandler(logging.Handler):
    """Captures log records to an in-memory ring buffer for API access."""

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            entry["exception"] = str(record.exc_info[1])

        with _log_lock:
            _recent_logs.append(entry)
            if record.levelno >= logging.WARNING:
                _recent_errors.append(entry)


def get_recent_logs(limit: int = 100, level: Optional[str] = None) -> list[dict]:
    """Get recent log entries from the in-memory buffer.

    Args:
        limit: Max entries to return
        level: Filter by level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    with _log_lock:
        entries = list(_recent_logs)

    if level:
        level_upper = level.upper()
        entries = [e for e in entries if e["level"] == level_upper]

    return entries[-limit:]


def get_recent_errors(limit: int = 50) -> list[dict]:
    """Get recent WARNING+ entries."""
    with _log_lock:
        return list(_recent_errors)[-limit:]


def setup_logging(
    data_dir: str = "data",
    verbose: bool = False,
    console: bool = True,
) -> Path:
    """Configure persistent file-based logging for the entire Hypernet.

    Call this ONCE at startup, before any other imports that use logging.

    Args:
        data_dir: Base data directory (logs go in data_dir/logs/)
        verbose: If True, console shows DEBUG; otherwise INFO
        console: If True, also log to console (default: True)

    Returns:
        Path to the log directory
    """
    log_dir = Path(data_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()

    # Don't add handlers if already configured (prevents duplicates on restart)
    if any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return log_dir

    root.setLevel(logging.DEBUG)

    # ── Format ──
    file_fmt = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_fmt = logging.Formatter(
        "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── File handler: all INFO+ messages ──
    main_log = log_dir / "hypernet.log"
    main_handler = RotatingFileHandler(
        main_log, maxBytes=5 * 1024 * 1024, backupCount=5,
        encoding="utf-8",
    )
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(file_fmt)
    root.addHandler(main_handler)

    # ── File handler: errors only (WARNING+) ──
    error_log = log_dir / "errors.log"
    error_handler = RotatingFileHandler(
        error_log, maxBytes=2 * 1024 * 1024, backupCount=10,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(file_fmt)
    root.addHandler(error_handler)

    # ── In-memory handler for API access ──
    mem_handler = InMemoryHandler()
    mem_handler.setLevel(logging.INFO)
    root.addHandler(mem_handler)

    # ── Console handler ──
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        console_handler.setFormatter(console_fmt)
        root.addHandler(console_handler)

    # Quiet noisy libraries
    for name in ["urllib3", "httpcore", "httpx", "asyncio", "uvicorn.access"]:
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.getLogger("hypernet").info(
        "Logging initialized: %s (main) + %s (errors)",
        main_log, error_log,
    )

    return log_dir
