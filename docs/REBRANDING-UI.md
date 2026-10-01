# Rebranding visual CEMICODE (UI real)

Por qué el portable actual se ve igual que OpenCode: `bin/cemicode.exe` es el
binario oficial renombrado. El branding de config (theme, agentes, provider)
sí aplica; el logo/título compilados no. Este documento cubre el cambio real.

## Qué cambia el parche (fuente: `patches/cemicode-ui-branding.patch`)

| Archivo upstream | Cambio |
|---|---|
| `packages/tui/src/logo.ts` | Logo ASCII TUI → icono + `CEMICODE CODING / AGENT · GDX SPARK / DGX · PULIDO OK` |
| `packages/opencode/src/cli/ui.ts` | Wordmark no-TTY → `CEMICODE / CODING AGENT · GDX SPARK DGX` |
| `packages/app/index.html` | `<title>CEMICODE — Coding Agent</title>`, favicon → `/cemicode-logo.svg`, `theme-color` + fondo → `#0B1220` |
| `packages/opencode/src/cli/cmd/web.ts` | describe → `start cemicode server and open web interface` |
| `packages/opencode/script/build.ts` | user-agent → `cemicode/<versión>`, artefacto → `cemicode-*` |
| `packages/app/public/` (CI) | Se copian `cemicode-logo.svg` + `cemicode-logo-horizontal.svg` (icono izq + texto der) para la Web UI embebida |

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
