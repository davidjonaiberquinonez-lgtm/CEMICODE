"""Aplica el rebranding visual CEMICODE sobre opencode-upstream (parche documentado).
Idempotente: si un reemplazo ya esta aplicado, lo omite.
Uso: python scripts/apply-cemicode-branding.py [--check]
No toca node_modules. Respeta AGENTS.md: upstream solo via este parche.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UP = ROOT / "opencode-upstream"

REPLACEMENTS = [
    # 1. TUI ASCII logo (packages/tui/src/logo.ts) — icono izq + CEMICODE der
    ("packages/tui/src/logo.ts",
     '  left: ["                   ", "█▀▀█ █▀▀█ █▀▀█ █▀▀▄", "█__█ █__█ █^^^ █__█", "▀▀▀▀ █▀▀▀ ▀▀▀▀ ▀~~▀"],\n'
     '  right: ["             ▄     ", "█▀▀▀ █▀▀█ █▀▀█ █▀▀█", "█___ █__█ █__█ █^^^", "▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀"],',
     '  left: ["                   ", " █▀▀▀▀▀▀▀▀▀▀▀█     ", " █                  ", "  ▀▀▀▀▀▀▀▀▀▀▀▀     "],\n'
     '  right: ["  ▄               ", "CEMICODE CODING   ", "AGENT · GDX SPARK ", "DGX · PULIDO OK   "], // CEMICODE rebrand'),
    # 2. CLI wordmark no-TTY (packages/opencode/src/cli/ui.ts)
    ("packages/opencode/src/cli/ui.ts",
     "const wordmark = [\n"
     "  `⠀                                ▄     `,\n"
     "  `█▀▀█ █▀▀█ █▀▀█ █▀▀▄ █▀▀▀ █▀▀█ █▀▀█ █▀▀█`,\n"
     "  `█  █ █  █ █▀▀▀ █  █ █    █  █ █  █ █▀▀▀`,\n"
     "  `▀▀▀▀ █▀▀▀ ▀▀▀▀ ▀  ▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀`,\n"
     "]",
     "const wordmark = [\n"
     "  `CEMICODE`,\n"
     "  `CODING AGENT · GDX SPARK DGX`,\n"
     "  `Enjambre multi-agente sobre OpenCode (MIT)`,\n"
     "  ``,\n"
     "] // CEMICODE rebrand"),
    # 3a. Web title (packages/app/index.html)
    ("packages/app/index.html",
     "<title>OpenCode</title>",
     "<title>CEMICODE \u2014 Coding Agent</title> <!-- CEMICODE rebrand -->"),
    # 3b. Web favicons -> assets CEMICODE (se copian en CI antes del build)
    ("packages/app/index.html",
     '<link rel="icon" type="image/png" href="/favicon-96x96-v3.png" sizes="96x96" />\n'
     '    <link rel="icon" type="image/svg+xml" href="/favicon-v3.svg" />\n'
     '    <link rel="shortcut icon" href="/favicon-v3.ico" />',
     '<link rel="icon" type="image/svg+xml" href="/cemicode-logo.svg" />\n'
     '    <link rel="icon" type="image/png" href="/favicon-96x96-v3.png" sizes="96x96" />\n'
     '    <link rel="shortcut icon" href="/favicon-v3.ico" /> <!-- CEMICODE rebrand -->'),
    # 3c. Web theme-color + fondo base -> azul oscuro marca
    ("packages/app/index.html",
     '<meta name="theme-color" content="#fafafa" />',
     '<meta name="theme-color" content="#0B1220" /> <!-- CEMICODE rebrand -->'),
    ("packages/app/index.html",
     '<html lang="en" style="background-color: var(--v2-background-bg-deep, #fafafa)">',
     '<html lang="en" style="background-color: var(--v2-background-bg-deep, #0B1220)"> <!-- CEMICODE rebrand -->'),
    # 4. Comando web describe (packages/opencode/src/cli/cmd/web.ts)
    ("packages/opencode/src/cli/cmd/web.ts",
     'describe: "start opencode server and open web interface",',
     'describe: "start cemicode server and open web interface", // CEMICODE rebrand'),
    # 5a. User-agent del binario compilado (packages/opencode/script/build.ts)
    ("packages/opencode/script/build.ts",
     "`--user-agent=opencode/${Script.version}`",
     "`--user-agent=cemicode/${Script.version}` // CEMICODE rebrand"),
    # 5b. Nombre del binario compilado -> cemicode-*
    ("packages/opencode/script/build.ts",
     "  const name = [\n    pkg.name,",
     '  const name = [\n    "cemicode", // CEMICODE rebrand (upstream: pkg.name)'),
]

WEB_ASSETS = [
    ("cemicode-branding/logo-cemicode.svg", "packages/app/public/cemicode-logo.svg"),
    ("cemicode-branding/logo-cemicode-horizontal.svg", "packages/app/public/cemicode-logo-horizontal.svg"),
]


def apply(check_only=False):
    errors = []
    for rel, old, new in REPLACEMENTS:
        p = UP / rel
        if not p.exists():
            errors.append(f"FALTA archivo: {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        if new in text:
            print(f"OK (ya aplicado): {rel}")
            continue
        if old not in text:
            errors.append(f"SIN COINCIDENCIA en {rel} — revisa version upstream")
            continue
        if check_only:
            print(f"PENDIENTE: {rel}")
        else:
            p.write_text(text.replace(old, new, 1), encoding="utf-8")
            print(f"APLICADO: {rel}")
    for src_rel, dst_rel in WEB_ASSETS:
        src, dst = ROOT / src_rel, UP / dst_rel
        if check_only:
            print(("OK asset: " if dst.exists() else "PENDIENTE asset: ") + dst_rel)
        elif src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
            print(f"ASSET: {dst_rel}")
        else:
            errors.append(f"FALTA asset origen: {src_rel}")
    if errors:
        print("\nERRORES:")
        for e in errors:
            print(" - " + e)
        return 1
    print("\nBranding CEMICODE OK.")
    return 0


if __name__ == "__main__":
    sys.exit(apply(check_only="--check" in sys.argv))
