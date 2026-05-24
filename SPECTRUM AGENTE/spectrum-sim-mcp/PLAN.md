# Plan de implementación

## Fase 0 — Pre-requisitos (humanos)

- [ ] Generar **API key n8n** en `agentsprod.redtec.ai` → Settings → API → Create API key. Guardar en `.env`.
- [ ] Obtener **MONGO_URI** con un usuario que pueda leer `Centralizado.*` y borrar docs `test_*`. Idealmente un usuario dedicado al sandbox.
- [ ] Confirmar `DEFAULT_PAGE_ID` — usar uno que exista en `manychat_settings` (probablemente el de GAROO o un page_id de prueba).

## Fase 1 — Esqueleto del servidor MCP

- [ ] `pyproject.toml` con deps: `mcp`, `httpx`, `pymongo`, `python-dotenv`, `pydantic`.
- [ ] `server.py` con `mcp.server.Server`, registro de tools y dispatch stdio.
- [ ] Smoke test: cliente MCP local (mcp inspector) lista los tools.

## Fase 2 — Cliente n8n

- [ ] `n8n_client.py` con métodos: `list_executions(workflow_id, limit, status)`, `get_execution(id, include_data)`, `list_workflows()`.
- [ ] Manejo de paginación (`nextCursor`) y errores (401, 404).
- [ ] Tests contra el servidor real (con executions reales).

## Fase 3 — Cliente Mongo

- [ ] `mongo_client.py` con: `get_user`, `get_appointments`, `get_chat_history`, `reset_test_user`.
- [ ] **Guardrail crítico:** `reset_test_user` rechaza cualquier `manychat_id` que no empiece con `test_`.

## Fase 4 — Webhook

- [ ] `webhook.py` con `send_message(user_id, text, page_id, canal, proyecto?, whatsapp_phone?)`.
- [ ] Construye payload tipo ManyChat (ver `test_agent.py` como referencia).
- [ ] Timeout configurable, manejo de respuesta JSON malformada.

## Fase 5 — Tools MCP

Cada tool en `tools/*.py`, registrada por `server.py`:

- [ ] `send_message`
- [ ] `list_executions`
- [ ] `get_execution`
- [ ] `tail_executions` (loop con polling + límite de tiempo)
- [ ] `read_user_state`
- [ ] `reset_user`
- [ ] `list_workflows`

## Fase 6 — Empaquetado y consumo desde IAs cliente

- [ ] Entry point en `pyproject.toml`: `spectrum-sim-mcp = "spectrum_sim_mcp.server:main"`.
- [ ] Instrucciones de instalación en `README.md` para Claude Desktop, Claude Code, Cursor y Gemini CLI (sección `mcpServers` de su config).
- [ ] Script `mcp_dev.sh` para correr el servidor con stdio + logs en archivo (debug).

## Fase 7 — Validación

- [ ] Escenario manual end-to-end: desde Claude Code, pedirle "saluda al agente como cliente nuevo, espera la respuesta, dime qué tools se llamaron en la última ejecución y qué documento se creó en `users`."
- [ ] La IA debería poder cumplirlo sin más contexto que las descripciones de las tools.

---

## Decisiones aún abiertas

1. **Runtime: Python vs Node.** Python encaja con `test_agent.py` y la stack del repo; Node es la referencia oficial de MCP. Recomendación: **Python** (reutilizar conocimiento del equipo, menos toolchain nueva).
2. **Lectura de Mongo: directa o vía un workflow n8n auxiliar.** Directa es más rápida pero requiere distribuir credenciales Mongo. Vía workflow es más seguro pero añade latencia. Recomendación: **directa** con usuario dedicado de read-mostly.
3. **`reset_user` opcional o requerido.** Si lo dejamos opcional, podemos arrancar sin permisos de escritura en Mongo. Recomendación: opcional, gated por `MONGO_ALLOW_RESET=true` en `.env`.
