#!/data/data/com.termux/files/usr/bin/bash
# relay_console -- fresh Termux setup, one shot.
# Paste this whole block into Termux, or download and run: bash setup_termux.sh
set -e

echo "[1/6] Updating packages..."
pkg update -y && pkg upgrade -y

echo "[2/6] Installing python, rust, git..."
pkg install -y python rust git

echo "[3/6] Cloning relay_console (adjust URL/path if not using git)..."
# If you already have the project files (e.g. pasted from the zip), skip this
# step and cd into the existing projects/relay_console directory instead.
if [ ! -d "socrates_llmos" ]; then
  echo "  No existing socrates_llmos/ found -- place your project files here manually,"
  echo "  or replace this block with your actual git clone / unzip command."
fi
cd socrates_llmos/projects/relay_console || { echo "relay_console not found -- cd there manually and re-run from step 4"; exit 1; }

echo "[4/6] Installing Python dependencies (this is the slow step -- pydantic-core compiles via rust)..."
pip install -r requirements.txt

echo "[5/6] Setting up .env (empty template -- fill in your own keys, never share this file)..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Created .env from template. Edit it now: nano .env"
else
  echo "  .env already exists, leaving it alone."
fi

echo "[6/6] Done. To launch:"
echo "  uvicorn backend.main:app --reload --port 8420 --host 127.0.0.1"
echo "Then open http://localhost:8420 in your browser."
echo ""
echo "For long sync sessions, also run: termux-wake-lock"
