#!/usr/bin/env bash
# ============================================================
# Hypernet — First-Run Setup (Linux / macOS)
# ============================================================
#
# Usage:
#   chmod +x install.sh
#   ./install.sh
#
# This script checks for Python 3.10+, installs it if missing,
# then runs bootstrap.py to handle everything else.
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "  H Y P E R N E T"
echo "  ========================="
echo "  First-Run Setup"
echo ""

# -------------------------------------------------------
# Detect OS
# -------------------------------------------------------
OS="$(uname -s)"
case "$OS" in
    Linux)  OS_TYPE="linux" ;;
    Darwin) OS_TYPE="macos" ;;
    *)      OS_TYPE="unknown" ;;
esac

# -------------------------------------------------------
# Find a suitable Python 3.10+
# -------------------------------------------------------
find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
            local major minor
            major=$(echo "$ver" | cut -d. -f1)
            minor=$(echo "$ver" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON_CMD=""
if PYTHON_CMD=$(find_python); then
    echo "  Python found: $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))"
else
    echo "  Python 3.10+ not found. Attempting to install..."
    echo ""

    if [ "$OS_TYPE" = "linux" ]; then
        if command -v apt-get &>/dev/null; then
            echo "  Installing via apt..."
            sudo apt-get update -qq
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v dnf &>/dev/null; then
            echo "  Installing via dnf..."
            sudo dnf install -y python3 python3-pip
        elif command -v yum &>/dev/null; then
            echo "  Installing via yum..."
            sudo yum install -y python3 python3-pip
        elif command -v pacman &>/dev/null; then
            echo "  Installing via pacman..."
            sudo pacman -S --noconfirm python python-pip
        else
            echo "  ERROR: No supported package manager found."
            echo "  Please install Python 3.10+ manually and re-run this script."
            exit 1
        fi
    elif [ "$OS_TYPE" = "macos" ]; then
        if command -v brew &>/dev/null; then
            echo "  Installing via Homebrew..."
            brew install python@3.13
        else
            echo "  Homebrew not found. Install it first:"
            echo "    /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo ""
            echo "  Then run this script again."
            exit 1
        fi
    else
        echo "  ERROR: Unsupported operating system: $OS"
        echo "  Please install Python 3.10+ manually."
        exit 1
    fi

    # Try again after install
    if PYTHON_CMD=$(find_python); then
        echo "  Python installed: $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))"
    else
        echo ""
        echo "  ERROR: Python installation succeeded but 3.10+ not found."
        echo "  You may need to restart your shell or install a newer version."
        exit 1
    fi
fi

# -------------------------------------------------------
# Run bootstrap.py
# -------------------------------------------------------
echo ""
echo "  Running bootstrap..."
echo ""
cd "$SCRIPT_DIR"
"$PYTHON_CMD" bootstrap.py "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "  ============================================"
    echo "  Setup complete!"
    echo "  ============================================"
    echo ""
    echo "  To launch the Hypernet:"
    echo "    $PYTHON_CMD -m hypernet launch"
    echo ""
else
    echo "  Setup finished with errors (exit code $exit_code)."
    echo "  Check the output above and re-run if needed."
fi

exit $exit_code
