"""Verifica el rebranding CEMICODE sin modificar nada.
Estados validos por archivo: PENDIENTE (upstream intacto, parche listo para CI)
o APLICADO (parche ya aplicado en este clon). Falla solo si hay deriva
(ni el texto original ni el rebrandeado coinciden).
Uso: python scripts/check-cemicode-branding.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "apply_branding", str(ROOT / "scripts" / "apply-cemicode-branding.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
REPLACEMENTS, WEB_ASSETS = _mod.REPLACEMENTS, _mod.WEB_ASSETS
REGEX_REPLACEMENTS = _mod.REGEX_REPLACEMENTS

fails, pending, applied = [], 0, 0
for rel, old, new in REPLACEMENTS:
    p = ROOT / "opencode-upstream" / rel
    if not p.exists():
        fails.append(f"{rel}: falta archivo upstream")
        continue
    text = p.read_text(encoding="utf-8")
    if new in text:
        applied += 1
        print(f"APLICADO  | {rel}")
    elif old in text:
        pending += 1
        print(f"PENDIENTE | {rel} (upstream intacto, CI lo aplica)")
    else:
        fails.append(f"{rel}: deriva upstream (ni original ni parche coinciden)")

for rel, _pattern, _repl, new_mark, old_mark in REGEX_REPLACEMENTS:
    p = ROOT / "opencode-upstream" / rel
    if not p.exists():
        fails.append(f"{rel}: falta archivo upstream")
        continue
    text = p.read_text(encoding="utf-8")
    if new_mark in text:
        applied += 1
        print(f"APLICADO  | {rel} (regex)")
    elif old_mark in text:
        pending += 1
        print(f"PENDIENTE | {rel} (regex, upstream intacto, CI lo aplica)")
    else:
        fails.append(f"{rel}: deriva upstream (regex sin coincidencia)")

for src_rel, dst_rel in WEB_ASSETS:
    ok = (ROOT / src_rel).exists()
    print(("OK  " if ok else "FAIL") + f" | asset origen [{src_rel}]")
    if not ok:
        fails.append(f"asset: {src_rel}")

for rel in ["patches/cemicode-ui-branding.patch",
            ".github/workflows/build-cemicode.yml",
            "docs/REBRANDING-UI.md"]:
    ok = (ROOT / rel).exists()
    print(("OK  " if ok else "FAIL") + f" | capa propia [{rel}]")
    if not ok:
        fails.append(f"capa: {rel}")

print(f"\nResumen: {applied} aplicados, {pending} pendientes, {len(fails)} fallos.")
sys.exit(1 if fails else 0)
