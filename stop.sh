#!/data/data/com.termux/files/usr/bin/bash
# Ghost RAT - Stop - Developed Adibhai

cd "$(dirname "$0")"
echo "[*] Sab process band kar raha hoon..."
pkill -f "termux-server/server.py" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
pkill -f "cloudflared" 2>/dev/null
termux-wake-unlock 2>/dev/null
echo "[✓] Band."
