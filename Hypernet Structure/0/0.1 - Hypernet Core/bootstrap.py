#!/usr/bin/env python3
"""
Hypernet Bootstrap — Universal prerequisite installer and first-run setup.

This script uses ONLY Python standard library (no pip packages).
It detects, reports, and installs everything needed to run the Hypernet.

Usage:
    python bootstrap.py          # Interactive mode
    python bootstrap.py --yes    # Auto-accept all installs
    python bootstrap.py --check  # Check only, don't install anything
    python bootstrap.py --help   # Show this help

Works on Windows, Linux, and macOS.
"""

import sys
import os
import subprocess
import shutil
import platform
import json
import urllib.request
import urllib.error
import tempfile
import argparse
import re
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MINIMUM_PYTHON = (3, 10)
SCRIPT_DIR = Path(__file__).resolve().parent
REQUIREMENTS_FILE = SCRIPT_DIR / "requirements.txt"
DATA_DIR = SCRIPT_DIR / "data"

# ANSI color codes (disabled on Windows without VT100 support)
_COLORS_ENABLED = False

def _init_colors():
    """Enable ANSI colors if the terminal supports them."""
    global _COLORS_ENABLED
    if os.name == "nt":
        # Try to enable VT100 processing on Windows 10+
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            _COLORS_ENABLED = True
        except Exception:
            _COLORS_ENABLED = False
    else:
        _COLORS_ENABLED = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

def _c(text: str, code: str) -> str:
    """Wrap text in ANSI color code."""
    if not _COLORS_ENABLED:
        return text
    codes = {"green": "32", "red": "31", "yellow": "33", "cyan": "36",
             "bold": "1", "dim": "2", "reset": "0"}
    return f"\033[{codes.get(code, '0')}m{text}\033[0m"


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

class Prereq:
    """Represents a single prerequisite with its detection and install logic."""

    def __init__(self, name: str, category: str, required: bool = True):
        self.name = name
        self.category = category  # "system", "python_pkg", "tool"
        self.required = required
        self.installed = False
        self.version: Optional[str] = None
        self.error: Optional[str] = None
        self.install_hint: str = ""

    @property
    def status_label(self) -> str:
        if self.installed:
            return _c("OK", "green")
        elif self.required:
            return _c("MISSING", "red")
        else:
            return _c("OPTIONAL", "yellow")

    def __repr__(self):
        ver = f" ({self.version})" if self.version else ""
        return f"{self.name}: {self.status_label}{ver}"


def detect_os() -> str:
    """Return 'windows', 'linux', or 'macos'."""
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    return s


def run_quiet(cmd: list, timeout: int = 30) -> Optional[subprocess.CompletedProcess]:
    """Run a command and capture output. Return None on failure."""
    try:
        # On Windows, commands like npm/npx are .cmd batch files that need
        # shell=True to be found. We enable shell=True on Windows for all
        # commands to handle this transparently.
        use_shell = (os.name == "nt")
        kwargs = dict(capture_output=True, text=True, timeout=timeout, shell=use_shell)
        if os.name == "nt" and not use_shell:
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        return subprocess.run(cmd, **kwargs)
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        return None
    except OSError:
        return None


def get_python_commands() -> list:
    """Return list of Python commands to try, in order of preference."""
    commands = [sys.executable]
    if os.name == "nt":
        commands.extend(["python", "py", "python3"])
    else:
        commands.extend(["python3", "python"])
    # Deduplicate while preserving order
    seen = set()
    result = []
    for c in commands:
        if c not in seen:
            seen.add(c)
            result.append(c)
    return result


def check_python() -> Prereq:
    """Check Python version."""
    p = Prereq("Python 3.10+", "system")
    v = sys.version_info
    p.version = f"{v.major}.{v.minor}.{v.micro}"
    if v >= MINIMUM_PYTHON:
        p.installed = True
    else:
        p.error = f"Python {v.major}.{v.minor} found, need 3.10+"
        p.install_hint = "Download from https://python.org/downloads/"
    return p


def check_pip() -> Prereq:
    """Check pip availability."""
    p = Prereq("pip", "system")
    r = run_quiet([sys.executable, "-m", "pip", "--version"])
    if r and r.returncode == 0:
        p.installed = True
        # Extract version: "pip 24.0 from ..."
        match = re.search(r"pip (\S+)", r.stdout)
        if match:
            p.version = match.group(1)
    else:
        p.error = "pip not found"
        p.install_hint = "python -m ensurepip --upgrade"
    return p


def check_git() -> Prereq:
    """Check git availability."""
    p = Prereq("git", "system")
    r = run_quiet(["git", "--version"])
    if r and r.returncode == 0:
        p.installed = True
        match = re.search(r"git version (\S+)", r.stdout)
        if match:
            p.version = match.group(1)
    else:
        p.error = "git not found"
        osname = detect_os()
        if osname == "windows":
            p.install_hint = "winget install Git.Git"
        elif osname == "macos":
            p.install_hint = "xcode-select --install"
        else:
            p.install_hint = "sudo apt install git  (or yum/dnf/pacman)"
    return p


def check_nodejs() -> Prereq:
    """Check Node.js availability."""
    p = Prereq("Node.js + npm", "tool", required=False)
    r = run_quiet(["node", "--version"])
    if r and r.returncode == 0:
        p.version = r.stdout.strip()
        # Also check npm
        r2 = run_quiet(["npm", "--version"])
        if r2 and r2.returncode == 0:
            p.version += f" / npm {r2.stdout.strip()}"
            p.installed = True
        else:
            p.error = "Node.js found but npm missing"
    else:
        p.error = "Node.js not found (needed for Claude Code CLI)"
        osname = detect_os()
        if osname == "windows":
            p.install_hint = "winget install OpenJS.NodeJS.LTS"
        elif osname == "macos":
            p.install_hint = "brew install node"
        else:
            p.install_hint = "sudo apt install nodejs npm"
    return p


def check_claude_code() -> Prereq:
    """Check Claude Code CLI availability."""
    p = Prereq("Claude Code CLI", "tool", required=False)
    r = run_quiet(["claude", "--version"])
    if r and r.returncode == 0:
        p.installed = True
        p.version = r.stdout.strip()
    else:
        p.error = "claude command not found"
        p.install_hint = "npm install -g @anthropic-ai/claude-code"
    return p


def check_nssm() -> Prereq:
    """Check NSSM availability (Windows only)."""
    p = Prereq("NSSM (service manager)", "tool", required=False)
    if os.name != "nt":
        p.installed = True
        p.version = "n/a (not Windows)"
        return p

    r = run_quiet(["nssm", "version"])
    if r and r.returncode == 0:
        p.installed = True
        match = re.search(r"(\d+\.\d+)", r.stdout + r.stderr)
        if match:
            p.version = match.group(1)
        else:
            p.version = "installed"
    else:
        # Check if it exists in tools/ subdirectory
        local_nssm = SCRIPT_DIR / "tools" / "nssm.exe"
        if local_nssm.exists():
            p.installed = True
            p.version = "local (tools/nssm.exe)"
        else:
            p.error = "NSSM not found (needed for Windows service install)"
            p.install_hint = "winget install NSSM.NSSM  (or download from nssm.cc)"
    return p


def check_python_package(name: str, import_name: Optional[str] = None,
                         required: bool = True) -> Prereq:
    """Check if a Python package is installed."""
    display = name
    p = Prereq(display, "python_pkg", required=required)
    check_name = import_name or name.replace("-", "_").split("[")[0]

    r = run_quiet([sys.executable, "-c",
                   f"import {check_name}; print(getattr({check_name}, '__version__', 'installed'))"])
    if r and r.returncode == 0:
        p.installed = True
        p.version = r.stdout.strip()
    else:
        p.error = f"Package '{name}' not installed"
        p.install_hint = f"pip install {name}"
    return p


def parse_requirements(filepath: Path) -> list:
    """Parse requirements.txt and return list of (name, import_name, required) tuples."""
    packages = []
    if not filepath.exists():
        return packages

    optional_section = False
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()

            # Track sections
            if "optional" in line.lower() and line.startswith("#"):
                optional_section = True
                continue
            if line.startswith("#") and not optional_section:
                # Non-optional section header
                if "server" in line.lower() or "api" in line.lower():
                    optional_section = False
                continue

            if not line or line.startswith("#"):
                continue

            # Parse package name from requirement spec
            name = re.split(r"[>=<\[!~]", line)[0].strip()
            if not name:
                continue

            # Map package names to import names where they differ
            import_map = {
                "uvicorn[standard]": "uvicorn",
                "uvicorn": "uvicorn",
                "Pillow": "PIL",
                "python-telegram-bot": "telegram",
                "pydantic": "pydantic",
            }
            import_name = import_map.get(name, None)

            # Determine required vs optional
            is_required = not optional_section

            packages.append((name, import_name, is_required))

    return packages


# ---------------------------------------------------------------------------
# Installation functions
# ---------------------------------------------------------------------------

def is_admin() -> bool:
    """Check if running with admin/root privileges."""
    if os.name == "nt":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        return os.geteuid() == 0


def request_elevation():
    """On Windows, relaunch this script with admin privileges."""
    if os.name != "nt":
        print("  Please re-run with: sudo python bootstrap.py")
        return False

    try:
        import ctypes
        script = str(Path(__file__).resolve())
        args = " ".join(sys.argv[1:])
        print("  Requesting administrator privileges...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script}" {args}', None, 1
        )
        return True  # The elevated process will handle installation
    except Exception as e:
        print(f"  Could not elevate privileges: {e}")
        return False


def install_pip():
    """Install pip using ensurepip."""
    print("  Installing pip...")
    r = subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        print(_c("    pip installed successfully.", "green"))
        return True
    else:
        print(_c(f"    Failed to install pip: {r.stderr[:200]}", "red"))
        return False


def install_python_packages(requirements_file: Path) -> bool:
    """Install Python packages from requirements.txt."""
    if not requirements_file.exists():
        print(_c(f"    {requirements_file} not found!", "red"))
        return False

    print(f"  Installing Python packages from {requirements_file.name}...")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_file),
         "--quiet", "--disable-pip-version-check"],
        capture_output=True, text=True, timeout=300,
    )
    if r.returncode == 0:
        print(_c("    All packages installed successfully.", "green"))
        return True
    else:
        # Show output for debugging
        print(_c("    Some packages may have failed:", "yellow"))
        for line in (r.stdout + r.stderr).strip().split("\n"):
            if line.strip():
                print(f"      {line.strip()}")
        return False


def install_git_windows() -> bool:
    """Install git on Windows via winget."""
    print("  Installing git via winget...")
    r = run_quiet(["winget", "install", "--id", "Git.Git", "-e",
                    "--accept-source-agreements", "--accept-package-agreements"])
    if r and r.returncode == 0:
        print(_c("    git installed. You may need to restart your terminal.", "green"))
        return True
    else:
        print(_c("    winget install failed. Download git from https://git-scm.com/", "yellow"))
        return False


def install_git_linux() -> bool:
    """Install git on Linux via package manager."""
    if shutil.which("apt-get"):
        cmd = ["sudo", "apt-get", "install", "-y", "git"]
    elif shutil.which("dnf"):
        cmd = ["sudo", "dnf", "install", "-y", "git"]
    elif shutil.which("yum"):
        cmd = ["sudo", "yum", "install", "-y", "git"]
    elif shutil.which("pacman"):
        cmd = ["sudo", "pacman", "-S", "--noconfirm", "git"]
    else:
        print(_c("    No supported package manager found.", "red"))
        return False

    print(f"  Running: {' '.join(cmd)}")
    r = subprocess.run(cmd)
    return r.returncode == 0


def install_nodejs_windows() -> bool:
    """Install Node.js on Windows via winget."""
    print("  Installing Node.js LTS via winget...")
    r = run_quiet(["winget", "install", "--id", "OpenJS.NodeJS.LTS", "-e",
                    "--accept-source-agreements", "--accept-package-agreements"])
    if r and r.returncode == 0:
        print(_c("    Node.js installed. Restart your terminal to use 'node' and 'npm'.", "green"))
        return True
    else:
        print(_c("    winget install failed. Download from https://nodejs.org/", "yellow"))
        return False


def install_nodejs_linux() -> bool:
    """Install Node.js on Linux via package manager or nvm."""
    if shutil.which("apt-get"):
        cmd = ["sudo", "apt-get", "install", "-y", "nodejs", "npm"]
    elif shutil.which("dnf"):
        cmd = ["sudo", "dnf", "install", "-y", "nodejs", "npm"]
    elif shutil.which("yum"):
        cmd = ["sudo", "yum", "install", "-y", "nodejs", "npm"]
    elif shutil.which("pacman"):
        cmd = ["sudo", "pacman", "-S", "--noconfirm", "nodejs", "npm"]
    elif shutil.which("brew"):
        cmd = ["brew", "install", "node"]
    else:
        print("  No supported package manager found.")
        print("  Install nvm: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash")
        return False

    print(f"  Running: {' '.join(cmd)}")
    r = subprocess.run(cmd)
    return r.returncode == 0


def install_nodejs_macos() -> bool:
    """Install Node.js on macOS via brew."""
    if shutil.which("brew"):
        print("  Installing Node.js via brew...")
        r = subprocess.run(["brew", "install", "node"])
        return r.returncode == 0
    else:
        print("  Install Homebrew first: https://brew.sh")
        print("  Then run: brew install node")
        return False


def install_claude_code() -> bool:
    """Install Claude Code CLI via npm."""
    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        # On Windows, npm is a .cmd file
        if os.name == "nt":
            npm_cmd = shutil.which("npm.cmd")
        if not npm_cmd:
            print(_c("    npm not found — install Node.js first.", "yellow"))
            return False

    print("  Installing Claude Code CLI...")
    use_shell = (os.name == "nt")
    r = subprocess.run(["npm", "install", "-g", "@anthropic-ai/claude-code"],
                       capture_output=True, text=True, timeout=120, shell=use_shell)
    if r.returncode == 0:
        print(_c("    Claude Code CLI installed.", "green"))
        return True
    else:
        print(_c("    npm install failed. Try manually: npm install -g @anthropic-ai/claude-code", "yellow"))
        return False


def install_nssm_windows() -> bool:
    """Install NSSM on Windows via winget or direct download."""
    # Try winget first
    print("  Installing NSSM via winget...")
    r = run_quiet(["winget", "install", "--id", "NSSM.NSSM", "-e",
                    "--accept-source-agreements", "--accept-package-agreements"])
    if r and r.returncode == 0:
        print(_c("    NSSM installed via winget.", "green"))
        return True

    # Fall back to direct download
    print("  winget failed, downloading from nssm.cc...")
    try:
        url = "https://nssm.cc/release/nssm-2.24.zip"
        tools_dir = SCRIPT_DIR / "tools"
        tools_dir.mkdir(exist_ok=True)
        zip_path = tools_dir / "nssm.zip"

        print(f"    Downloading {url}...")
        urllib.request.urlretrieve(url, str(zip_path))

        import zipfile
        with zipfile.ZipFile(str(zip_path), "r") as z:
            # Find the 64-bit exe
            for name in z.namelist():
                if "win64" in name and name.endswith("nssm.exe"):
                    with z.open(name) as src:
                        dest = tools_dir / "nssm.exe"
                        with open(str(dest), "wb") as dst:
                            dst.write(src.read())
                    print(_c(f"    NSSM extracted to {dest}", "green"))
                    zip_path.unlink()
                    return True

        print(_c("    Could not find nssm.exe in archive.", "yellow"))
        return False
    except Exception as e:
        print(_c(f"    Download failed: {e}", "red"))
        print("    Download manually from https://nssm.cc/download")
        return False


# ---------------------------------------------------------------------------
# Editable install for the project itself
# ---------------------------------------------------------------------------

def install_editable_packages() -> bool:
    """Install hypernet packages in editable mode."""
    success = True

    # Main project
    print("  Installing hypernet-core in editable mode...")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(SCRIPT_DIR),
         "--quiet", "--disable-pip-version-check"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        print(_c(f"    Failed: {r.stderr[:200]}", "yellow"))
        success = False
    else:
        print(_c("    hypernet-core installed.", "green"))

    # Swarm package (if it exists)
    swarm_dir = SCRIPT_DIR.parent / "0.1.7 - AI Swarm"
    if swarm_dir.exists() and (swarm_dir / "pyproject.toml").exists():
        print("  Installing hypernet-swarm in editable mode...")
        r = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", str(swarm_dir),
             "--quiet", "--disable-pip-version-check"],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            print(_c(f"    Failed: {r.stderr[:200]}", "yellow"))
            success = False
        else:
            print(_c("    hypernet-swarm installed.", "green"))

    return success


# ---------------------------------------------------------------------------
# Data directory setup
# ---------------------------------------------------------------------------

def setup_data_directory():
    """Create the data/ directory structure if it doesn't exist."""
    dirs = [
        DATA_DIR,
        DATA_DIR / "nodes",
        DATA_DIR / "links",
        DATA_DIR / "indexes",
        DATA_DIR / "swarm",
        DATA_DIR / "swarm" / "approvals",
        DATA_DIR / "mesh",
    ]
    created = []
    for d in dirs:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(d)

    if created:
        print(f"  Created {len(created)} data directories.")
    else:
        print("  Data directories already exist.")


def setup_secrets_directory():
    """Create secrets/ directory with template config if it doesn't exist."""
    secrets_dir = SCRIPT_DIR / "secrets"
    secrets_dir.mkdir(exist_ok=True)

    gitkeep = secrets_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()

    config_file = secrets_dir / "config.json"
    if not config_file.exists():
        template = {
            "_comment": "Hypernet configuration — fill in your API keys",
            "anthropic_api_key": "",
            "openai_api_key": "",
            "discord": {
                "bot_token": "",
                "default_webhook_url": ""
            },
            "budget": {
                "daily_limit_usd": 200,
                "session_limit_usd": 25
            },
            "swarm": {
                "instances": [],
                "personal_time_pct": 25
            }
        }
        with open(str(config_file), "w") as f:
            json.dump(template, f, indent=2)
        print("  Created secrets/config.json template (add your API keys).")
    else:
        print("  secrets/config.json already exists.")


# ---------------------------------------------------------------------------
# Main bootstrap flow
# ---------------------------------------------------------------------------

def print_banner():
    """Print the Hypernet banner."""
    print()
    print("  " + _c("H Y P E R N E T", "bold"))
    print("  " + _c("Bootstrap & Prerequisite Installer", "cyan"))
    print("  " + "=" * 42)
    print()
    print(f"  Platform:   {platform.system()} {platform.release()}")
    print(f"  Python:     {sys.version.split()[0]} ({sys.executable})")
    print(f"  Project:    {SCRIPT_DIR}")
    print()


def print_summary_table(prereqs: list):
    """Print a formatted prerequisite status table."""
    # Calculate column widths
    max_name = max(len(p.name) for p in prereqs)
    max_ver = max(len(p.version or "") for p in prereqs)

    print("  " + "-" * (max_name + max_ver + 28))
    print(f"  {'Prerequisite':<{max_name}}  {'Status':<10}  {'Version':<{max_ver}}  {'Category'}")
    print("  " + "-" * (max_name + max_ver + 28))

    for p in prereqs:
        status_display = p.status_label
        ver = p.version or ""
        cat = p.category.replace("python_pkg", "python").replace("_", " ")
        # Use raw status for column alignment (status_label has ANSI codes)
        if p.installed:
            raw_status = "OK"
        elif p.required:
            raw_status = "MISSING"
        else:
            raw_status = "OPTIONAL"

        # Pad status manually since ANSI codes mess up alignment
        pad = 10 - len(raw_status)
        print(f"  {p.name:<{max_name}}  {status_display}{' ' * pad}  {ver:<{max_ver}}  {cat}")

    print("  " + "-" * (max_name + max_ver + 28))


def count_issues(prereqs: list) -> tuple:
    """Return (missing_required, missing_optional) counts."""
    missing_req = sum(1 for p in prereqs if not p.installed and p.required)
    missing_opt = sum(1 for p in prereqs if not p.installed and not p.required)
    return missing_req, missing_opt


def main():
    _init_colors()

    parser = argparse.ArgumentParser(description="Hypernet Bootstrap — prerequisite installer")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="Auto-accept all installations without prompting")
    parser.add_argument("--check", action="store_true",
                        help="Check prerequisites only, don't install anything")
    parser.add_argument("--skip-optional", action="store_true",
                        help="Skip optional prerequisites")
    args = parser.parse_args()

    print_banner()

    osname = detect_os()

    # ----- Phase 1: Detect all prerequisites -----
    print(_c("  [Phase 1] Checking prerequisites...", "bold"))
    print()

    prereqs = []

    # System-level
    print("  Checking Python...", end=" ", flush=True)
    p = check_python()
    print(f"{p.status_label} ({p.version})")
    prereqs.append(p)

    print("  Checking pip...", end=" ", flush=True)
    p = check_pip()
    print(f"{p.status_label}" + (f" ({p.version})" if p.version else ""))
    prereqs.append(p)

    print("  Checking git...", end=" ", flush=True)
    p = check_git()
    print(f"{p.status_label}" + (f" ({p.version})" if p.version else ""))
    prereqs.append(p)

    print("  Checking Node.js + npm...", end=" ", flush=True)
    p = check_nodejs()
    print(f"{p.status_label}" + (f" ({p.version})" if p.version else ""))
    prereqs.append(p)

    print("  Checking Claude Code CLI...", end=" ", flush=True)
    p = check_claude_code()
    print(f"{p.status_label}" + (f" ({p.version})" if p.version else ""))
    prereqs.append(p)

    if osname == "windows":
        print("  Checking NSSM...", end=" ", flush=True)
        p = check_nssm()
        print(f"{p.status_label}" + (f" ({p.version})" if p.version else ""))
        prereqs.append(p)

    # Python packages from requirements.txt
    print()
    print("  Checking Python packages...")
    packages = parse_requirements(REQUIREMENTS_FILE)
    for pkg_name, import_name, is_required in packages:
        display_name = pkg_name.split("[")[0]  # Strip extras like [standard]
        print(f"    Checking {display_name}...", end=" ", flush=True)
        p = check_python_package(pkg_name, import_name, required=is_required)
        print(f"{p.status_label}" + (f" ({p.version})" if p.version else ""))
        prereqs.append(p)

    # ----- Phase 2: Summary -----
    print()
    print(_c("  [Phase 2] Prerequisite Summary", "bold"))
    print()
    print_summary_table(prereqs)

    missing_req, missing_opt = count_issues(prereqs)
    total_ok = sum(1 for p in prereqs if p.installed)

    print()
    print(f"  {_c(str(total_ok), 'green')} installed"
          f"  |  {_c(str(missing_req), 'red') if missing_req else '0'} missing (required)"
          f"  |  {_c(str(missing_opt), 'yellow') if missing_opt else '0'} missing (optional)")
    print()

    if missing_req == 0 and missing_opt == 0:
        print(_c("  All prerequisites are installed!", "green"))
        # Still do data directory setup
        print()
        print(_c("  [Phase 3] Setting up directories...", "bold"))
        print()
        setup_data_directory()
        setup_secrets_directory()
        print()
        _print_next_steps(verify=True)
        return 0

    if args.check:
        # Check-only mode: report and exit
        if missing_req > 0:
            print("  Missing required prerequisites. Run without --check to install.")
            return 1
        return 0

    # ----- Phase 3: Confirm and install -----
    # Show what will be installed
    print(_c("  [Phase 3] Installation Plan", "bold"))
    print()

    installable = []
    for p in prereqs:
        if p.installed:
            continue
        if args.skip_optional and not p.required:
            continue
        req_label = "REQUIRED" if p.required else "optional"
        print(f"    [{req_label}] {p.name}")
        if p.install_hint:
            print(f"             -> {p.install_hint}")
        installable.append(p)

    if not installable:
        print("  Nothing to install.")
        print()
        print(_c("  [Phase 4] Setting up directories...", "bold"))
        print()
        setup_data_directory()
        setup_secrets_directory()
        print()
        _print_next_steps(verify=True)
        return 0

    print()

    # Check if admin is needed
    needs_admin = False
    for p in installable:
        if p.category == "system" and p.name != "pip":
            needs_admin = True
        if p.name in ("NSSM (service manager)",) and osname == "windows":
            needs_admin = True

    if needs_admin and not is_admin():
        print(_c("  NOTE: Some installations may require administrator privileges.", "yellow"))
        print("  If an install fails, try running this script as administrator.")
        print()

    # Ask permission
    if not args.yes:
        try:
            answer = input("  Install missing prerequisites? [Y/n] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            print("  Cancelled.")
            return 1

        if answer and answer not in ("y", "yes"):
            print("  Skipping installation.")
            return 0

    print()
    print(_c("  [Phase 4] Installing...", "bold"))
    print()

    results = []

    # Install pip first if missing (needed for everything else)
    pip_prereq = next((p for p in installable if p.name == "pip"), None)
    if pip_prereq:
        ok = install_pip()
        results.append(("pip", ok))
        if not ok:
            print(_c("  Cannot continue without pip.", "red"))
            return 1

    # Install git if missing
    git_prereq = next((p for p in installable if p.name == "git"), None)
    if git_prereq:
        if osname == "windows":
            ok = install_git_windows()
        elif osname == "macos":
            print("  Run: xcode-select --install")
            ok = False
        else:
            ok = install_git_linux()
        results.append(("git", ok))

    # Install Node.js if missing
    node_prereq = next((p for p in installable if p.name == "Node.js + npm"), None)
    if node_prereq:
        if osname == "windows":
            ok = install_nodejs_windows()
        elif osname == "macos":
            ok = install_nodejs_macos()
        else:
            ok = install_nodejs_linux()
        results.append(("Node.js", ok))

    # Install Claude Code CLI if missing and Node.js is available
    claude_prereq = next((p for p in installable if p.name == "Claude Code CLI"), None)
    if claude_prereq:
        # Check if npm is available now (might have just been installed)
        if shutil.which("npm"):
            ok = install_claude_code()
            results.append(("Claude Code CLI", ok))
        else:
            print("  Skipping Claude Code CLI — npm not available yet.")
            print("  After installing Node.js, run: npm install -g @anthropic-ai/claude-code")
            results.append(("Claude Code CLI", False))

    # Install NSSM on Windows if missing
    nssm_prereq = next((p for p in installable if "NSSM" in p.name), None)
    if nssm_prereq:
        ok = install_nssm_windows()
        results.append(("NSSM", ok))

    # Install Python packages
    pkg_missing = [p for p in installable if p.category == "python_pkg"]
    if pkg_missing:
        ok = install_python_packages(REQUIREMENTS_FILE)
        results.append(("Python packages", ok))

    # Install editable packages
    print()
    print("  Installing Hypernet packages in editable mode...")
    ok = install_editable_packages()
    results.append(("Hypernet packages (editable)", ok))

    # ----- Phase 5: Set up directories -----
    print()
    print(_c("  [Phase 5] Setting up directories...", "bold"))
    print()
    setup_data_directory()
    setup_secrets_directory()

    # ----- Phase 6: Verification -----
    print()
    print(_c("  [Phase 6] Verifying installation...", "bold"))
    print()

    # Re-check Python packages
    recheck_failed = []
    packages = parse_requirements(REQUIREMENTS_FILE)
    for pkg_name, import_name, is_required in packages:
        display_name = pkg_name.split("[")[0]
        p = check_python_package(pkg_name, import_name, required=is_required)
        status = _c("OK", "green") if p.installed else _c("FAIL", "red")
        print(f"    {display_name}: {status}")
        if not p.installed and is_required:
            recheck_failed.append(display_name)

    # Try to import hypernet
    print()
    print("  Checking hypernet package...", end=" ", flush=True)
    r = run_quiet([sys.executable, "-c", "from hypernet import __version__; print(__version__)"])
    if r and r.returncode == 0:
        print(_c(f"OK (v{r.stdout.strip()})", "green"))
    else:
        print(_c("FAIL", "red"))
        recheck_failed.append("hypernet")

    # Try hypernet status
    print("  Running 'python -m hypernet status'...")
    print()
    r = subprocess.run([sys.executable, "-m", "hypernet", "status"],
                       cwd=str(SCRIPT_DIR), timeout=30)

    # ----- Phase 7: Results -----
    print()
    print(_c("  [Results]", "bold"))
    print("  " + "-" * 40)
    for name, ok in results:
        status = _c("OK", "green") if ok else _c("FAILED", "red")
        print(f"    {name}: {status}")
    print("  " + "-" * 40)

    if recheck_failed:
        print()
        print(_c(f"  {len(recheck_failed)} required item(s) still missing:", "yellow"))
        for name in recheck_failed:
            print(f"    - {name}")

    print()
    _print_next_steps(verify=not bool(recheck_failed))
    return 0 if not recheck_failed else 1


def _print_next_steps(verify: bool = True):
    """Print next-steps instructions."""
    print(_c("  Next Steps:", "bold"))
    print()
    if verify:
        print("    1. Configure API keys (if using AI swarm):")
        print(f"       Edit: {SCRIPT_DIR / 'secrets' / 'config.json'}")
        print()
        print("    2. Launch the Hypernet:")
        if os.name == "nt":
            print("       Double-click launch.bat")
            print("       — or —")
        print("       python -m hypernet launch")
        print()
        print("    3. Open in your browser:")
        print("       http://localhost:8000/home")
        print()
        print("    4. Run tests:")
        print("       python -m hypernet test")
        print()
    else:
        print("    Some prerequisites failed to install.")
        print("    Fix the issues above, then run bootstrap.py again.")
        print()
    print("  " + _c("Documentation:", "dim"))
    print(f"    README:     {SCRIPT_DIR / 'README.md'}")
    print(f"    Swarm setup: {SCRIPT_DIR / 'docs' / 'guides' / 'SWARM-SETUP-GUIDE.md'}")
    print()


if __name__ == "__main__":
    sys.exit(main())
