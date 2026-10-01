# AGENTS.md — Protocolo CEMICODE (MIT)

Este archivo gobierna el enjambre. Todo agente debe obedecerlo.

## Roles
- `orchestrator` (primary): planifica, delega, no edita. Color #2563EB.
- `coder-dgx` (subagent): implementa en DGX. Modelo `gdx-spark/Qwen3.6-35B-A3B`.
- `reasoning-dgx` (subagent): arquitectura y debug, sin edicion.
- `reviewer-zen` (subagent): QA con bash permitido, sin edicion. Cierre `PULIDO OK`.

## Invocacion
- Manual: `@coder-dgx ...`, `@reasoning-dgx ...`, `@reviewer-zen ...`
- Auto: orchestrator delega segun descripcion del agente.

## Reglas de acabado pulido
1. Cambios minimos, sin tocar `opencode-upstream/` salvo parche documentado.
2. Sin secretos en git: `.env`, `.cemicode/token.json` gitignored. Claves solo via entorno.
3. Toda respuesta de codigo cita archivo:linea cuando existe.
4. Verificacion minima antes de cerrar: `scripts/cemicode-chat.py` OK + `scripts/cemicode-auth.py status`.
5. Licencia MIT intacta.
