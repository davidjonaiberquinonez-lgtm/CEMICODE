"""CEMICODE auth helper — DGX GDX Spark JWT (puerto 8100).
Uso:
  python scripts/cemicode-auth.py login
  python scripts/cemicode-auth.py status
Lee DGX_* desde entorno o .env local. Guarda token en .cemicode/token.json (gitignored).
NUNCA imprime la clave.
"""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / os.environ.get("CEMICODE_TOKEN_CACHE", ".cemicode/token.json")

def load_dotenv():
    envf = ROOT / ".env"
    if envf.exists():
        for line in envf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

def login():
    load_dotenv()
    base = os.environ.get("DGX_AUTH_BASE", "http://192.168.4.4:8100")
    sub = os.environ.get("DGX_AUTH_SUB", "cemicode")
    rol = os.environ.get("DGX_AUTH_ROL", "TECNOLOGIA")
    clave = os.environ.get("DGX_CLAVE", "")
    if not clave:
        print("ERROR: falta DGX_CLAVE en entorno o .env local. Ver .env.example", file=sys.stderr)
        return 2
    payload = json.dumps({"sub": sub, "rol": rol, "clave": clave}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/auth/login", data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"ERROR auth HTTP {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR conexion {base}: {e!r}", file=sys.stderr)
        return 1
    data["_obtenido"] = int(time.time())
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"OK token guardado en {CACHE} expires_in={data.get('expires_in')}")
    return 0

def status():
    if not CACHE.exists():
        print("SIN TOKEN — ejecuta: python scripts/cemicode-auth.py login")
        return 1
    data = json.loads(CACHE.read_text(encoding="utf-8"))
    age = int(time.time()) - data.get("_obtenido", 0)
    ttl = data.get("expires_in", 43200) - age
    print(f"token_type={data.get('token_type')} ttl_restante_seg={ttl} sub_ok=True")
    return 0 if ttl > 60 else 2

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    sys.exit(login() if cmd == "login" else status())
