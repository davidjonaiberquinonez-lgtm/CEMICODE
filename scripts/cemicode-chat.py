"""CEMICODE chat probe — verifica vLLM OpenAI-compatible en DGX.
Uso:
  python scripts/cemicode-chat.py "explica en 1 linea que eres CEMICODE"
  python scripts/cemicode-chat.py --models
"""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def safe_print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        print(str(s).encode("cp1252", errors="replace").decode("cp1252"))

def load_dotenv():
    envf = Path(__file__).resolve().parents[1] / ".env"
    if envf.exists():
        for line in envf.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

load_dotenv()
BASE = os.environ.get("DGX_LLM_BASE", "http://192.168.4.4:8000/v1")
MODEL = os.environ.get("DGX_LLM_MODEL", "Qwen3.6-35B-A3B")

def req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE.rstrip("/") + path, data=data,
        headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:1000]}", file=sys.stderr)
        sys.exit(1)

if len(sys.argv) >= 2 and sys.argv[1] == "--models":
    safe_print(json.dumps(req("GET", "/models"), indent=2, ensure_ascii=False)[:3000])
else:
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Responde en una linea: eres CEMICODE sobre GDX Spark, di PULIDO OK."
    out = req("POST", "/chat/completions", {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Eres CEMICODE, asistente tecnico conciso sobre GDX Spark DGX. Responde directo, sin rodeos."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 2000,
    })
    try:
        msg = out["choices"][0]["message"]
        content = msg.get("content")
        if content:
            safe_print(content)
        else:
            # Qwen3 via vLLM 0.28 devuelve thinking en msg["reasoning"]; con max_tokens corto hace finish length
            reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
            safe_print(f"[sin content directo | finish={out['choices'][0].get('finish_reason')}] reasoning parcial:\n{reasoning[:1500]}")
            safe_print(json.dumps(out, indent=2, ensure_ascii=False)[:2000])
    except Exception:
        safe_print(json.dumps(out, indent=2, ensure_ascii=False)[:3000])
