#!/data/data/com.termux/files/usr/bin/bash
# relay_console -- fresh Termux setup, one shot.
# Paste this whole block into Termux, or download and run: bash setup_termux.sh
set -e

echo "[1/5] Updating packages..."
pkg update -y && pkg upgrade -y

echo "[2/5] Installing python, rust, git, tailscale..."
pkg install -y python rust git tailscale-termux

echo "[3/5] Cloning relay_console (adjust URL/path if not using git)..."
if [ ! -d "socrates_llmos" ]; then
  echo "  No existing socrates_llmos/ found -- place your project files here manually,"
  echo "  or replace this block with your actual git clone / unzip command."
fi
cd socrates_llmos/projects/relay_console || { echo "relay_console not found -- cd there manually and re-run from step 4"; exit 1; }

echo "[4/5] Installing Python dependencies (this is the slow step -- pydantic-core compiles via rust)..."
pip install -r requirements.txt

echo "[5/5] Setting up .env (empty template -- fill in your own keys, never share this file)..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Created .env from template. Edit it now: nano .env"
else
  echo "  .env already exists, leaving it alone."
fi

echo ""
echo "--- Auto-start on open, auto-stop on close (no widgets, no Termux:Boot) ---"
echo "If you have xfce4/x11-repo/vnc packages installed for viewing a browser"
echo "in Termux -- you don't need them. Open your phone's own browser to"
echo "http://localhost:8420 directly; this frontend IS the admin console."
echo "Remove them with: pkg uninstall xfce4 x11-repo"
echo ""
echo "Run this once to wire auto-start/stop into your shell startup:"
cat << 'EOF'

cat >> ~/.bashrc << 'BASHRC'

# --- relay_console auto-start (skip if already running this session) ---
if [ -z "$RELAY_CONSOLE_STARTED" ]; then
  export RELAY_CONSOLE_STARTED=1
  tailscale up >/dev/null 2>&1 &
  (cd ~/socrates_llmos/projects/relay_console && \
    uvicorn backend.main:app --port 8420 --host 127.0.0.1 >/tmp/relay.log 2>&1 &)
  echo "relay_console starting -- open http://localhost:8420"
fi
BASHRC

EOF
echo ""
echo "That's it. Opening the Termux app runs this automatically on every new"
echo "session. Closing/killing the Termux app kills these as child processes"
echo "-- no persistent background daemon, no widget, no Termux:Boot needed."
echo ""
echo "One-time only: run 'tailscale up' manually first to authenticate via"
echo "browser login. After that, the auto-start line above just reconnects."
echo ""
echo "Caveat: Android can still kill the app in the background under memory"
echo "pressure, same as any app -- 'close' isn't the only way this stops."
