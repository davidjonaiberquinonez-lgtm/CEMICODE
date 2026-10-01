# AGENTS.md — Protocolo CEMICODE (MIT)

Este archivo gobierna el enjambre. Todo agente debe obedecerlo.

## Roles
- `orchestrator` (primary, GDX Qwen): planifica, delega, no edita. Color #2563EB.
- `coder-dgx` (subagent, GDX Qwen): codigo local / respaldo. Color #0EA5E9.
- `reasoning-dgx` (subagent, GDX Qwen): arquitectura y debug, sin edicion. Color #7C3AED.
- `reviewer-zen` (subagent, GDX Qwen): QA con bash permitido, sin edicion. Cierre `PULIDO OK`. Color #FB7185.
- `flash-zen` (subagent, Zen Nemotron 3.5 Lightning Free): lectura rapida. Color #FBBF24.
- `ocr-zen` (subagent, Zen MiMo-V2.6-Flash Free): OCR, visual y frontend. Color #38BDF8.
- `apis-zen` (subagent, Zen Ling 3.0 Flash Fin Free): APIs, conexiones y estado. Color #A78BFA.
- `coder-zen` (subagent, Zen Muse Spark 1.3 Contributor Free): codigo principal. Color #34D399.

## Pool GDX + Zen (misma sesion)
GDX dirige y audita; Zen ejecuta. Ruta: lectura `@flash-zen` → visual `@ocr-zen`
→ conexiones `@apis-zen` → diseno `@reasoning-dgx` → codigo `@coder-zen`
(respaldo `@coder-dgx`) → QA `@reviewer-zen`. Repuesto free: `opencode/longcat-2.5-preview-free`.

## Invocacion
- Manual: `@coder-dgx ...`, `@reasoning-dgx ...`, `@reviewer-zen ...`
- Auto: orchestrator delega segun descripcion del agente.

## Reglas de acabado pulido
1. Cambios minimos, sin tocar `opencode-upstream/` salvo parche documentado.
2. Sin secretos en git: `.env`, `.cemicode/token.json` gitignored. Claves solo via entorno.
3. Toda respuesta de codigo cita archivo:linea cuando existe.
4. Verificacion minima antes de cerrar: `scripts/cemicode-chat.py` OK + `scripts/cemicode-auth.py status`.
5. Licencia MIT intacta.
