#!/bin/bash
# Install all Aesthetic Lens dependencies into a local .venv
# (inside the skill directory — follows wherever the skill is installed)

set -e
cd "$(dirname "$0")/.."  # skill root

VENV_DIR=".venv"

# health check: exists + python + cv2 importable
_venv_healthy() {
    [ -d "$VENV_DIR" ] || return 1
    local py="$VENV_DIR/Scripts/python.exe"
    [ -f "$py" ] || py="$VENV_DIR/bin/python"
    [ -f "$py" ] || return 1
    "$py" -c "import cv2" 2>/dev/null && return 0
    return 1
}

if _venv_healthy; then
    echo "♻️  $VENV_DIR ready, reusing."
else
    [ -d "$VENV_DIR" ] && rm -rf "$VENV_DIR" && echo "🗑️  Removed broken $VENV_DIR"
    echo "📦 Creating virtual environment ..."
    python3 -m venv --without-venvlaunchers "$VENV_DIR" 2>/dev/null \
        || python -m venv --without-venvlaunchers "$VENV_DIR" 2>/dev/null \
        || python3 -m venv "$VENV_DIR" 2>/dev/null \
        || python -m venv "$VENV_DIR"
fi

# activate
if [ -f "$VENV_DIR/Scripts/activate" ]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Aesthetic Lens dependencies installed successfully"
