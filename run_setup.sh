#!/usr/bin/env bash

# ==============================================================================
# All-in-One Setup & Launcher for Raju's Royal Artifacts Shop (Linux / macOS)
# Checks prerequisites, sets up venv, installs deps, runs tests, and launches app.
# Usage: ./run_setup.sh
# ==============================================================================

set -e

echo "========================================================="
echo "  👳‍♂️ Raju's Royal Artifacts — All-in-One Linux/macOS    "
echo "========================================================="
echo ""

# 1. Prerequisite Check: Python 3
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[-] Error: python3 is not installed. Please install Python 3.10+."
    exit 1
fi

PY_VER=$(python3 --version)
echo "[+] Found $PY_VER"

# 2. Prerequisite Check: GEMINI_API_KEY
echo ""
echo "[2/5] Checking GEMINI_API_KEY..."

if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null || true
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "[!] GEMINI_API_KEY is not set."
    read -p "Please enter your Gemini API Key (or press Enter to skip): " USER_KEY
    if [ -n "$USER_KEY" ]; then
        export GEMINI_API_KEY="$USER_KEY"
        echo "GEMINI_API_KEY=$GEMINI_API_KEY" > .env
        echo "[+] Saved API key to .env file."
    fi
else
    echo "[+] GEMINI_API_KEY is configured."
fi

# 3. Virtual Environment & Dependencies
echo ""
echo "[3/5] Setting up Virtual Environment (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "[+] Created virtual environment."
fi

source .venv/bin/activate

echo "[+] Installing/Updating dependencies from requirements.txt..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "[+] Dependencies installed successfully."

# 4. Run Automated Tests
echo ""
echo "[4/5] Running automated unit tests (pytest)..."
export PYTHONPATH="."
pytest tests/test_agent.py || echo "[!] Warning: Some tests failed, continuing setup..."

# 5. Launch FastAPI Server & Open Browser
echo ""
echo "[5/5] Launching Raju's Shop Server at http://localhost:8000 ..."
echo "========================================================="
echo "👉 Press CTRL+C to stop the server."
echo "========================================================="

# Try opening default browser
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8000" &
elif command -v open &> /dev/null; then
    open "http://localhost:8000" &
fi

# Start uvicorn server
python3 -m uvicorn app.fast_api_app:app --host 0.0.0.0 --port 8000
