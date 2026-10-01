# Rebranding visual CEMICODE (UI real)

Por qué el portable actual se ve igual que OpenCode: `bin/cemicode.exe` es el
binario oficial renombrado. El branding de config (theme, agentes, provider)
sí aplica; el logo/título compilados no. Este documento cubre el cambio real.

## Qué cambia el parche (fuente: `scripts/apply-cemicode-branding.py`)

| Zona | Cambio |
|---|---|
| TUI logo (`tui/src/logo.ts`) | C en bloques + `CEMICODE CODING / AGENT · GDX SPARK / DGX · PULIDO OK` |
| TUI títulos (`tui/src/app.tsx`) | Terminal: `CEMICODE` y `CEMICODE \| <sesión>` |
| CLI (`opencode/src/index.ts`, `temporary.ts`) | `scriptName cemicode` en `--help` |
| CLI wordmark (`opencode/src/cli/ui.ts`) | No-TTY: `CEMICODE / CODING AGENT · GDX SPARK DGX` |
| CLI web (`opencode/src/cli/cmd/web.ts`) | describe + etiqueta `CEMICODE interface:` |
| Build (`opencode/script/build.ts`) | user-agent `cemicode/<ver>` (artefacto conserva nombre upstream; rename al empaquetar) |
| Web (`app/index.html`) | Título, favicon SVG+PNG, `cemicode.ico`, apple-touch, manifest propio, `theme-color` + fondo `#0B1220` |
| Web iconos (`cemicode-branding/icons/`) | Set PNG 16→512 + ICO multi-tamaño generados del SVG (Edge headless + Pillow); accesos `.lnk` e Inno usan `cemicode.ico` |
| Web (`app/src/entry.tsx`) | Icono notificaciones → `/cemicode-logo.svg` |
| Web watermark (`ui/.../wordmark-v2.tsx`) | Letras opencode → texto `CEMICODE` |
| Web logo (`ui/.../logo.tsx`) | Paths opencode → texto `CEMICODE` |
| Web tema (`ui/.../theme/context.tsx`) | Oscuro por defecto + theme built-in muestra `CEMICODE` |
| Web theme azul (`cemicode-branding/theme-cemicode-web.json` → `ui/.../theme/themes/cemicode.json`) | Theme completo en paleta marca, registrado en picker y por defecto |
| Canal (`OPENCODE_CHANNEL=prod` en CI) | Sin badge DEV, versión `0.0.0-prod-*` |

Regla AGENTS.md respetada: `opencode-upstream/` no se edita a mano; solo via
`python scripts/apply-cemicode-branding.py` (idempotente, verificado con `--check`).

## Cómo compilar el exe rebrandeado

Windows local falla (`zod/v4` en `@modelcontextprotocol/sdk` con bun 1.3.14/1.4.2).
Usar Linux:

```bash
cd CIME_CODE
python scripts/apply-cemicode-branding.py
cd opencode-upstream && bun install   # bun 1.3.14
cd packages/opencode && bun run script/build.ts --single
# → dist/cemicode-linux-x64/bin/opencode  (= cemicode rebrandeado)
```

O disparar el workflow `build-cemicode` (GitHub Actions, ubuntu-latest) que hace
todo y sube `CEMICODE-Portable-rebranded.zip`.

## Verificar sin compilar

```bash
python scripts/apply-cemicode-branding.py --check   # 9 reemplazos pendientes = OK
python scripts/check-cemicode-branding.py           # capa propia + estado upstream
```

## Fase 2 (no incluida)

Desktop Electron (`packages/desktop`: app id `ai.opencode.desktop`, menus i18n,
iconos por SO) requiere parches propios + firma Windows. Se hará tras validar
el TUI/web rebrandeado.

Licencia: MIT upstream intacta (`opencode-upstream/LICENSE`). Binario derivado
mantiene avisos y `Enjambre multi-agente sobre OpenCode (MIT)` en el wordmark.
