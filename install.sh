#!/usr/bin/env bash
set -euo pipefail

REPO="rafikone-cli"
PYTHON="${PYTHON:-python3}"

echo "=== RafikOne CLI Installer ==="
echo ""

# Check Python
if ! command -v "$PYTHON" &>/dev/null; then
    echo "Error: Python 3.12+ is required but not found."
    echo "Install it with: sudo apt install python3 python3-pip"
    exit 1
fi

PY_VERSION=$("$PYTHON" --version 2>&1 | grep -oP '\d+\.\d+')
MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 12 ]; }; then
    echo "Error: Python 3.12+ required (found $PY_VERSION)"
    exit 1
fi

echo "✓ Python $PY_VERSION found"

# Install pip if needed
if ! "$PYTHON" -m pip --version &>/dev/null; then
    echo "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | "$PYTHON"
fi

# Install the package
echo "Installing RafikOne CLI..."
"$PYTHON" -m pip install --break-system-packages -e .

echo ""
echo "✓ Installation complete"
echo ""
echo "Run 'rafikone init' to configure your project root."
echo "Run 'rafikone' to launch the interactive dashboard."
