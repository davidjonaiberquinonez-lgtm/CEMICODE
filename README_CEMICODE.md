# CEMICODE — Enjambre multi-agente sobre OpenCode + DGX GDX Spark

Proyecto pulido: OpenCode open-source (MIT, `opencode-upstream/`) + capa CEMICODE
(config, agentes, scripts, branding azul tech) + inferencia local DGX.

## Verificado 30-sep-2026
- `GET http://192.168.4.4:8000/v1/models` → 200, `Qwen3.6-35B-A3B`, `max_model_len` 131072, `owned_by` vllm
- `POST http://192.168.4.4:8100/auth/login` → 200, JWT `token_type bearer`, `expires_in` 43200

## Estructura
- `opencode.json` — provider `gdx-spark` (openai-compatible, baseURL DGX) + 4 agentes + permisos
- `.opencode/agents/` — orchestrator, coder-dgx, reasoning-dgx, reviewer-zen (markdown pulido)
- `scripts/cemicode-auth.py` — login JWT 8100 → `.cemicode/token.json` (gitignored)
- `scripts/cemicode-chat.py` — prueba chat vLLM 8000
- `cemicode-branding/` — theme azul oscuro + logo SVG (icono izquierda + logotipo derecha)
- `opencode-upstream/` — clon `--depth 1` de anomalyco/opencode (MIT, no tocar salvo parche)
- `Dockerfile` + `docker-compose.yml` — entorno aislado

## Uso rapido (Windows PowerShell)
```powershell
Copy-Item .env.example .env
# edita .env o exporta DGX_CLAVE solo local (no commitear)
python scripts/cemicode-chat.py --models
python scripts/cemicode-chat.py "explica en 1 linea que eres CEMICODE"
python scripts/cemicode-auth.py login
python scripts/cemicode-auth.py status
C:/Users/CALOJULIO/AppData/Roaming/npm/bun.cmd --version
```

## Flujo enjambre
1. Usuario → `orchestrator` (primary, no edita): plan + subtareas con criterios.
2. Diseno/debug → `@reasoning-dgx` (subagent, solo analisis).
3. Codigo → `@coder-dgx` (subagent, edita).
4. QA → `@reviewer-zen` (subagent, tests, dice PULIDO OK o reporta archivo:linea).

## Branding CEMICODE
- Layout oficial: icono a la izquierda + logotipo a la derecha `CEMIC{}DE / CODING AGENT`
- Icono: `cemicode-branding/logo-cemicode.svg` (64x64, C + E + engranaje + flecha)
- Horizontal: `cemicode-branding/logo-cemicode-horizontal.svg` (icono izq + texto der)
- Theme: `cemicode-branding/theme-cemicode.json` + `.opencode/themes/cemicode.json`
- Paleta mantenida: bg #0B1220 / surface #111C33 / primary #2563EB / accent #0EA5E9 / text #E6EDF7
- Rebranding visual real (logo/título compilados): ver `docs/REBRANDING-UI.md`
  (`patches/cemicode-ui-branding.patch` + workflow `build-cemicode`). El portable
  actual usa binario oficial renombrado; el exe rebrandeado se compila en Linux CI.

## Notas
- `opencode.json` usa claves actuales (`provider` singular, `agent` singular) segun docs opencode.ai.
- Upstream exige `bun@1.3.14`; local verificado `bun 1.4.2` OK para scripts (para `bun install` full del monorepo usa Docker o `bun 1.3.14`).
- Licencia MIT del repo original intacta en `opencode-upstream/LICENSE`.
