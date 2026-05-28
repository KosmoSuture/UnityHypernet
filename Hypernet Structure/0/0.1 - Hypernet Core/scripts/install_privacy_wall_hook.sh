#!/usr/bin/env bash
# Install the privacy-wall pre-commit hook locally.
#
# Per 1.0.3 Privacy Wall Standard. Run from anywhere; this script
# locates the repo root, wires the hook into .git/hooks/pre-commit,
# and verifies the install with a dry run.
#
# Idempotent: re-running upgrades the hook in place.

set -euo pipefail

# Find repo root via git
if ! REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    echo "ERROR: not inside a git repository." >&2
    exit 1
fi

HOOK_PATH="$REPO_ROOT/.git/hooks/pre-commit"
SCRIPT_PATH="Hypernet Structure/0/0.1 - Hypernet Core/scripts/privacy_wall_check.py"
ABSOLUTE_SCRIPT="$REPO_ROOT/$SCRIPT_PATH"

if [ ! -f "$ABSOLUTE_SCRIPT" ]; then
    echo "ERROR: privacy_wall_check.py not found at expected path:" >&2
    echo "  $ABSOLUTE_SCRIPT" >&2
    exit 1
fi

# Detect Python interpreter
if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
else
    echo "ERROR: no python3/python on PATH." >&2
    exit 1
fi

# Write the hook
cat > "$HOOK_PATH" << HOOK_EOF
#!/usr/bin/env bash
# Privacy-wall pre-commit hook — installed by
# scripts/install_privacy_wall_hook.sh per 1.0.3.
#
# Reads staged file paths and runs scripts/privacy_wall_check.py.
# Blocks the commit if any privacy-wall violations are found.

set -euo pipefail

REPO_ROOT="\$(git rev-parse --show-toplevel)"
SCRIPT="\$REPO_ROOT/Hypernet Structure/0/0.1 - Hypernet Core/scripts/privacy_wall_check.py"

if [ ! -f "\$SCRIPT" ]; then
    echo "WARNING: privacy_wall_check.py not found; skipping privacy wall check." >&2
    echo "  Expected: \$SCRIPT" >&2
    exit 0
fi

# Get staged files (added/copied/modified, ignore deletes)
mapfile -t STAGED < <(git diff --cached --name-only --diff-filter=ACM)

if [ \${#STAGED[@]} -eq 0 ]; then
    exit 0
fi

# Run the check
$PYTHON_BIN "\$SCRIPT" "\${STAGED[@]}"
HOOK_EOF

chmod +x "$HOOK_PATH"

echo "Privacy-wall pre-commit hook installed at:"
echo "  $HOOK_PATH"
echo ""
echo "Verifying install with a dry run..."
echo ""

# Dry run: invoke hook on the script itself (which contains a literal
# "(402) 238-1334" pattern in its docstring? — no, it doesn't. Safe.)
TEST_FILE="Hypernet Structure/1 - People/1.1 Matt Schaeffer/private/embassy/contact/contact-private.json"
if [ -f "$REPO_ROOT/$TEST_FILE" ]; then
    if $PYTHON_BIN "$ABSOLUTE_SCRIPT" "$TEST_FILE" >/dev/null 2>&1; then
        echo "WARNING: hook didn't fire on a known-private path. Check patterns."
    else
        echo "OK: hook correctly rejects a private-path file."
    fi
else
    echo "(skipped dry run — test fixture not present)"
fi

echo ""
echo "The hook will now run on every git commit."
echo "To bypass intentionally: git commit --no-verify  (discouraged per 1.0.3)"
