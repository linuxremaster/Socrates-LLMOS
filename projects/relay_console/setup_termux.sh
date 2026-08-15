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

echo "[6/6] Done."
echo ""
echo "--- Optional: auto-start Tailscale + relay, drop X11/XFCE ---"
echo "If you have xfce4/x11-repo/vnc packages installed for viewing a"
echo "browser in Termux -- you don't need them. Open your phone's own"
echo "browser to http://localhost:8420 directly; this frontend is the"
echo "admin console. Remove them with: pkg uninstall xfce4 x11-repo"
echo ""
echo "For auto-start (Tailscale + relay, no manual launch each session):"
echo "  pkg install termux-services tailscale"
echo "  mkdir -p \$PREFIX/var/service/tailscaled/log"
echo "  cat > \$PREFIX/var/service/tailscaled/run <<'EOF'"
echo "#!/data/data/com.termux/files/usr/bin/sh"
echo "exec tailscaled"
echo "EOF"
echo "  chmod +x \$PREFIX/var/service/tailscaled/run"
echo "  sv-enable tailscaled"
echo "  mkdir -p \$PREFIX/var/service/relay/log"
echo "  cat > \$PREFIX/var/service/relay/run <<'EOF'"
echo "#!/data/data/com.termux/files/usr/bin/sh"
echo "cd ~/socrates_llmos/projects/relay_console"
echo "exec uvicorn backend.main:app --port 8420 --host 127.0.0.1"
echo "EOF"
echo "  chmod +x \$PREFIX/var/service/relay/run"
echo "  sv-enable relay"
echo ""
echo "Both then start automatically whenever Termux launches -- no"
echo "manual uvicorn/tailscale commands needed. Run 'tailscale up' once"
echo "manually first to authenticate; after that it's automatic."
echo "For surviving a full phone reboot too, install the separate"
echo "Termux:Boot app (F-Droid) -- ask if you want that step added."
