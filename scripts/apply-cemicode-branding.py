"""Aplica el rebranding visual CEMICODE sobre opencode-upstream (parche documentado).
Idempotente: si un reemplazo ya esta aplicado, lo omite.
Uso: python scripts/apply-cemicode-branding.py [--check]
No toca node_modules. Respeta AGENTS.md: upstream solo via este parche.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UP = ROOT / "opencode-upstream"

# (rel, old, new) literales. Si old aparece N veces, se reemplazan las N.
REPLACEMENTS = [
    # 1. TUI ASCII logo (packages/tui/src/logo.ts) — C bloque izq + CEMICODE der.
    # Anchos exactos: izq 19, der 18. Sin _ ^ ~ , (chars especiales del renderer).
    ("packages/tui/src/logo.ts",
     '  left: ["                   ", "█▀▀█ █▀▀█ █▀▀█ █▀▀▄", "█__█ █__█ █^^^ █__█", "▀▀▀▀ █▀▀▀ ▀▀▀▀ ▀~~▀"],\n'
     '  right: ["             ▄     ", "█▀▀▀ █▀▀█ █▀▀█ █▀▀█", "█___ █__█ █__█ █^^^", "▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀"],',
     '  left: ["                   ", "    ████████       ", "    ███            ", "    ████████       "],\n'
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
    # 3b. Iconos web completos CEMICODE (se copian en CI antes del build)
    ("packages/app/index.html",
     '<link rel="icon" type="image/png" href="/favicon-96x96-v3.png" sizes="96x96" />\n'
     '    <link rel="icon" type="image/svg+xml" href="/favicon-v3.svg" />\n'
     '    <link rel="shortcut icon" href="/favicon-v3.ico" />\n'
     '    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-v3.png" />\n'
     '    <link rel="manifest" href="/site.webmanifest" />',
     '<link rel="icon" type="image/svg+xml" href="/cemicode-logo.svg" />\n'
     '    <link rel="icon" type="image/png" href="/cemicode-favicon-96.png" sizes="96x96" />\n'
     '    <link rel="shortcut icon" href="/cemicode.ico" />\n'
     '    <link rel="apple-touch-icon" sizes="180x180" href="/cemicode-apple-touch-icon.png" />\n'
     '    <link rel="manifest" href="/cemicode.webmanifest" /> <!-- CEMICODE rebrand -->'),
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
    # 5. User-agent del binario compilado (packages/opencode/script/build.ts)
    # NOTA: NO se renombra el artefacto aqui: `target: name.replace(pkg.name,"bun")`
    # exige que el nombre contenga "opencode". El renombre a cemicode lo hace
    # el workflow / empaquetado al copiar el binario. Solo cambia el user-agent.
    # (sin comentario inline: va dentro del array execArgv y lo romperia)
    ("packages/opencode/script/build.ts",
     "`--user-agent=opencode/${Script.version}`",
     "`--user-agent=cemicode/${Script.version}`"),
    # 6. Nombre de programa CLI (packages/opencode/src/index.ts + temporary.ts)
    ("packages/opencode/src/index.ts",
     '.scriptName("opencode")',
     '.scriptName("cemicode") // CEMICODE rebrand'),
    ("packages/opencode/src/index.ts",
     'if (!text.startsWith("opencode "))',
     'if (!text.startsWith("cemicode "))'),
    ("packages/opencode/src/temporary.ts",
     '.scriptName("opencode")',
     '.scriptName("cemicode") // CEMICODE rebrand'),
    # 7. Titulo de terminal TUI (packages/tui/src/app.tsx)
    ("packages/tui/src/app.tsx",
     'renderer.setTerminalTitle("OpenCode")',
     'renderer.setTerminalTitle("CEMICODE") // CEMICODE rebrand'),
    ("packages/tui/src/app.tsx",
     "renderer.setTerminalTitle(`OC | ${title}`)",
     "renderer.setTerminalTitle(`CEMICODE | ${title}`) // CEMICODE rebrand"),
    ("packages/tui/src/app.tsx",
     "renderer.setTerminalTitle(`OC | ${route.data.id}`)",
     "renderer.setTerminalTitle(`CEMICODE | ${route.data.id}`) // CEMICODE rebrand"),
    # 8. Etiqueta de comando web (packages/opencode/src/cli/cmd/web.ts)
    # (sin comentario inline: el resto de la linea son argumentos del println)
    ("packages/opencode/src/cli/cmd/web.ts",
     '"  Web interface:    "',
     '"  CEMICODE interface: "'),
    # 9. Icono de notificaciones web (packages/app/src/entry.tsx)
    ("packages/app/src/entry.tsx",
     'icon: "https://opencode.ai/favicon-96x96-v3.png",',
     'icon: "/cemicode-logo.svg", // CEMICODE rebrand'),
    # 10. Tema oscuro por defecto en web (packages/ui/src/theme/context.tsx)
    ("packages/ui/src/theme/context.tsx",
     'const colorScheme = (read(STORAGE_KEYS.COLOR_SCHEME) as ColorScheme | null) ?? "system"',
     'const colorScheme = (read(STORAGE_KEYS.COLOR_SCHEME) as ColorScheme | null) ?? "dark" // CEMICODE rebrand: oscuro por defecto'),
    ("packages/ui/src/theme/context.tsx",
     'const savedScheme = (read(STORAGE_KEYS.COLOR_SCHEME) as ColorScheme | null) ?? "system"',
     'const savedScheme = (read(STORAGE_KEYS.COLOR_SCHEME) as ColorScheme | null) ?? "dark" // CEMICODE rebrand: oscuro por defecto'),
    # 11. Nombre del theme built-in en el picker (packages/ui/src/theme/context.tsx)
    ("packages/ui/src/theme/context.tsx",
     'opencode: "OpenCode",',
     'opencode: "CEMICODE", // CEMICODE rebrand'),
    # 14. Registrar theme CEMICODE en el picker (packages/ui/src/theme/context.tsx)
    ("packages/ui/src/theme/context.tsx",
     '  "catppuccin-macchiato": "Catppuccin Macchiato",',
     '  "catppuccin-macchiato": "Catppuccin Macchiato",\n'
     '  cemicode: "CEMICODE", // CEMICODE rebrand'),
    # 15. Theme CEMICODE por defecto (packages/ui/src/theme/context.tsx)
    ("packages/ui/src/theme/context.tsx",
     'const themeId = normalize(read(STORAGE_KEYS.THEME_ID) ?? props.defaultTheme) ?? "oc-2"',
     'const themeId = normalize(read(STORAGE_KEYS.THEME_ID) ?? props.defaultTheme) ?? "cemicode" // CEMICODE rebrand: azul por defecto'),
    ("packages/ui/src/theme/context.tsx",
     'const savedTheme = normalize(rawTheme ?? props.defaultTheme) ?? "oc-2"',
     'const savedTheme = normalize(rawTheme ?? props.defaultTheme) ?? "cemicode" // CEMICODE rebrand: azul por defecto'),
]

# (origen_repo, destino_upstream) para el theme web completo.
THEME_ASSETS = [
    ("cemicode-branding/theme-cemicode-web.json", "packages/ui/src/theme/themes/cemicode.json"),
]

# (rel, patron_regex, reemplazo, marca_nueva, marca_vieja_para_check)
# Para bloques grandes (watermark SVG, Logo) donde el literal es fragil.
REGEX_REPLACEMENTS = [
    # 12. Watermark gigante new-session (packages/ui/src/v2/components/wordmark-v2.tsx)
    # Las 8 letras "opencode" en paths -> texto CEMICODE ajustado al viewBox.
    ("packages/ui/src/v2/components/wordmark-v2.tsx",
     r'<g opacity="0\.16">.*?</g>',
     '<g opacity="0.16">\n'
     '            <text x="8" y="108" font-family="Arial, Helvetica, sans-serif" font-size="100" '
     'font-weight="900" letter-spacing="4" textLength="704" lengthAdjust="spacingAndGlyphs" '
     'fill="currentColor">CEMICODE</text>\n'
     '          </g>',
     "CEMICODE</text>",
     "M55.3846 36.4286H18.4615V91.7143H55.3846V36.4286Z"),
    # 13. Logo web (packages/ui/src/components/logo.tsx) -> texto CEMICODE.
    ("packages/ui/src/components/logo.tsx",
     r'export const Logo = \(props: \{ class\?: string \}\) => \{.*?\n\}',
     'export const Logo = (props: { class?: string }) => {\n'
     '  return (\n'
     '    <svg\n'
     '      xmlns="http://www.w3.org/2000/svg"\n'
     '      viewBox="0 0 240 44"\n'
     '      fill="none"\n'
     '      classList={{ [props.class ?? ""]: !!props.class }}\n'
     '    >\n'
     '      <text x="4" y="33" font-family="ui-monospace, SFMono-Regular, Menlo, monospace" '
     'font-size="32" font-weight="700" letter-spacing="3" fill="var(--icon-base)">\n'
     '        CEMICODE\n'
     '      </text>\n'
     '    </svg>\n'
     '  )\n'
     '} // CEMICODE rebrand',
     "CEMICODE\n",
     "M18 30H6V18H18V30Z"),
]

WEB_ASSETS = [
    ("cemicode-branding/logo-cemicode.svg", "packages/app/public/cemicode-logo.svg"),
    ("cemicode-branding/logo-cemicode-horizontal.svg", "packages/app/public/cemicode-logo-horizontal.svg"),
    ("cemicode-branding/icons/favicon-16.png", "packages/app/public/cemicode-favicon-16.png"),
    ("cemicode-branding/icons/favicon-32.png", "packages/app/public/cemicode-favicon-32.png"),
    ("cemicode-branding/icons/favicon-48.png", "packages/app/public/cemicode-favicon-48.png"),
    ("cemicode-branding/icons/favicon-96.png", "packages/app/public/cemicode-favicon-96.png"),
    ("cemicode-branding/icons/apple-touch-icon.png", "packages/app/public/cemicode-apple-touch-icon.png"),
    ("cemicode-branding/icons/icon-192.png", "packages/app/public/cemicode-icon-192.png"),
    ("cemicode-branding/icons/icon-512.png", "packages/app/public/cemicode-icon-512.png"),
    ("cemicode-branding/icons/cemicode.ico", "packages/app/public/cemicode.ico"),
    ("cemicode-branding/cemicode.webmanifest", "packages/app/public/cemicode.webmanifest"),
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
            n = text.count(new)
            print(f"OK (ya aplicado x{n}): {rel}")
            continue
        n = text.count(old)
        if n == 0:
            errors.append(f"SIN COINCIDENCIA en {rel} — revisa version upstream")
            continue
        if check_only:
            print(f"PENDIENTE x{n}: {rel}")
        else:
            p.write_text(text.replace(old, new), encoding="utf-8")
            print(f"APLICADO x{n}: {rel}")
    for rel, pattern, repl, new_mark, old_mark in REGEX_REPLACEMENTS:
        p = UP / rel
        if not p.exists():
            errors.append(f"FALTA archivo: {rel}")
            continue
        text = p.read_text(encoding="utf-8")
        if new_mark in text:
            print(f"OK (ya aplicado): {rel}")
            continue
        if old_mark not in text:
            errors.append(f"SIN COINCIDENCIA (regex) en {rel} — revisa version upstream")
            continue
        if check_only:
            print(f"PENDIENTE (regex): {rel}")
        else:
            text2, n = re.subn(pattern, lambda _m: repl, text, count=1, flags=re.DOTALL)
            if n == 0:
                errors.append(f"REGEX no mato en {rel}")
                continue
            p.write_text(text2, encoding="utf-8")
            print(f"APLICADO (regex): {rel}")
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
    for src_rel, dst_rel in THEME_ASSETS:
        src, dst = ROOT / src_rel, UP / dst_rel
        if check_only:
            print(("OK theme: " if dst.exists() else "PENDIENTE theme: ") + dst_rel)
        elif src.exists():
            # valida JSON antes de copiar
            import json as _json
            _json.loads(src.read_text(encoding="utf-8"))
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
            print(f"THEME: {dst_rel}")
        else:
            errors.append(f"FALTA theme origen: {src_rel}")
    if errors:
        print("\nERRORES:")
        for e in errors:
            print(" - " + e)
        return 1
    print("\nBranding CEMICODE OK.")
    return 0


if __name__ == "__main__":
    sys.exit(apply(check_only="--check" in sys.argv))
