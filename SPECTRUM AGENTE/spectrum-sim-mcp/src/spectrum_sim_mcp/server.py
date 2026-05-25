"""MCP server entry point — registra las tools y arranca el dispatch stdio.

Tools expuestas:
  • spectrum.send_message       — POST al webhook como si fuera ManyChat
  • spectrum.list_workflows     — atajo nombre → id de workflows en el servidor
  • spectrum.list_executions    — ejecuciones recientes de un workflow
  • spectrum.get_execution      — detalle nodo-por-nodo de una ejecución
  • spectrum.tail_executions    — polling de nuevas ejecuciones desde un timestamp
  • spectrum.read_user_state    — users / appointments / chat_histories de un manychat_id
  • spectrum.reset_user         — borra docs de un usuario test_* (gated)
  • spectrum.new_test_user_id   — utilidad: genera un manychat_id con prefijo test_
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import WORKFLOW_IDS, Config
from .mongo_client import MongoStore, ResetNotAllowedError
from .n8n_client import N8nApiError, N8nClient
from .webhook import new_test_user_id, send_message

LOG_PATH = Path(os.environ.get("SPECTRUM_MCP_LOG", Path.home() / ".spectrum-sim-mcp.log"))
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("spectrum-sim-mcp")


def _resolve_workflow_id(value: str) -> str:
    """Permite que el caller pase el nombre amigable o el id de n8n."""
    return WORKFLOW_IDS.get(value, value)


def _text(payload: Any) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]


def build_server(config: Config) -> tuple[Server, MongoStore | None]:
    n8n = N8nClient(config.n8n_base_url, config.n8n_api_key)
    mongo: MongoStore | None = None
    if config.mongo_enabled:
        mongo = MongoStore(config.mongo_uri, config.mongo_db, allow_reset=config.allow_reset)
    else:
        log.info("MONGO_URI vacío — tools de Mongo deshabilitadas")

    server: Server = Server("spectrum-sim-mcp")

    @server.list_tools()
    async def _list_tools() -> list[Tool]:
        tools: list[Tool] = [
            Tool(
                name="spectrum.send_message",
                description=(
                    "Envía un mensaje al webhook del orquestador Sof-IA como si fuera "
                    "ManyChat, y devuelve la respuesta sincrónica (incluye `respuesta`, "
                    "`accion` y herramientas usadas). El flujo tiene un Wait de ~10s; "
                    "espera hasta `WEBHOOK_TIMEOUT` segundos. Usa el mismo `user_id` "
                    "para encadenar mensajes en una misma conversación."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "manychat_id de la sesión. Usa el prefijo `test_` para que `reset_user` pueda limpiarlo después. Si lo omites, se genera uno automáticamente.",
                        },
                        "text": {"type": "string", "description": "Mensaje del usuario."},
                        "page_id": {
                            "type": "string",
                            "description": "page_id de ManyChat. Si lo omites se usa DEFAULT_PAGE_ID.",
                        },
                        "canal": {
                            "type": "string",
                            "enum": ["WhatsApp", "Instagram", "Messenger"],
                            "default": "WhatsApp",
                        },
                        "proyecto_interes": {
                            "type": "string",
                            "description": "Si quieres simular un lead phase-2 con proyecto pre-asignado (PVV, PMAR, PPO, PPOL, PSB), llénalo.",
                        },
                        "whatsapp_phone": {
                            "type": "string",
                            "description": "Teléfono con código de país, formato +502XXXXXXXX.",
                        },
                    },
                    "required": ["text"],
                },
            ),
            Tool(
                name="spectrum.new_test_user_id",
                description="Genera un manychat_id único con prefijo `test_` (compatible con reset_user).",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="spectrum.list_workflows",
                description="Lista workflows en el servidor n8n. Soporta filtrar por activos.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "active": {"type": "boolean", "description": "Solo workflows activos."},
                    },
                },
            ),
            Tool(
                name="spectrum.list_executions",
                description=(
                    "Lista ejecuciones recientes de un workflow. Acepta el nombre amigable "
                    "(ej: 'AGENT PRINCIPAL') o el id de n8n. Útil para encontrar la "
                    "ejecución correspondiente al `send_message` que acabas de hacer."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow": {
                            "type": "string",
                            "description": "Nombre o id del workflow.",
                            "default": "AGENT PRINCIPAL",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["error", "success", "waiting"],
                            "description": "Filtra por estado.",
                        },
                        "limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 250},
                    },
                },
            ),
            Tool(
                name="spectrum.get_execution",
                description=(
                    "Devuelve el detalle nodo-por-nodo de una ejecución: input/output de "
                    "cada nodo, errores y timing. Útil para entender qué herramientas "
                    "llamó el orquestador y con qué datos."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "execution_id": {"type": "string"},
                        "include_data": {"type": "boolean", "default": True},
                    },
                    "required": ["execution_id"],
                },
            ),
            Tool(
                name="spectrum.tail_executions",
                description=(
                    "Hace polling hasta que aparezca una ejecución nueva del workflow "
                    "indicado (más reciente que `since_iso`) o hasta agotar el tiempo. "
                    "Pensado para llamarse JUSTO DESPUÉS de `send_message` para capturar "
                    "la ejecución que ese mensaje disparó."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workflow": {"type": "string", "default": "AGENT PRINCIPAL"},
                        "since_iso": {
                            "type": "string",
                            "description": "Timestamp ISO 8601 — devuelve sólo ejecuciones startedAt > este valor. Si lo omites, usa el momento de llamada.",
                        },
                        "max_wait_seconds": {"type": "integer", "default": 30, "minimum": 1, "maximum": 120},
                        "poll_interval_seconds": {"type": "number", "default": 2.0},
                    },
                },
            ),
        ]
        if mongo is None:
            return tools
        tools += [
            Tool(
                name="spectrum.read_user_state",
                description=(
                    "Lee el estado en Mongo de un manychat_id: documento `users`, "
                    "appointments asociadas y últimas N entradas de chat_histories."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "manychat_id": {"type": "string"},
                        "page_id": {"type": "string", "description": "Opcional; restringe el match en `users`."},
                        "proyecto": {"type": "string", "description": "Opcional; filtra appointments por proyecto (UPPERCASE)."},
                        "history_kind": {
                            "type": "string",
                            "enum": ["main", "rsvp", "both"],
                            "default": "both",
                        },
                        "history_limit": {"type": "integer", "default": 10, "minimum": 1, "maximum": 100},
                    },
                    "required": ["manychat_id"],
                },
            ),
            Tool(
                name="spectrum.reset_user",
                description=(
                    "Borra documentos de un usuario test_* en `users`, `appointments`, "
                    "`chat_histories` y `chat_histories_rsvp`. Requiere "
                    "MONGO_ALLOW_RESET=true en .env y que el manychat_id empiece con "
                    "`test_` (por seguridad)."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {"manychat_id": {"type": "string"}},
                    "required": ["manychat_id"],
                },
            ),
        ]
        return tools

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        log.info("call_tool name=%s args_keys=%s", name, list(arguments.keys()))
        try:
            if name == "spectrum.send_message":
                user_id = arguments.get("user_id") or new_test_user_id()
                result = await send_message(
                    webhook_url=config.n8n_webhook_url,
                    timeout=config.webhook_timeout,
                    user_id=user_id,
                    text=arguments["text"],
                    page_id=arguments.get("page_id") or config.default_page_id,
                    canal=arguments.get("canal", "WhatsApp"),
                    proyecto_interes=arguments.get("proyecto_interes", ""),
                    whatsapp_phone=arguments.get("whatsapp_phone") or "+50212345678",
                )
                result["user_id"] = user_id
                return _text(result)

            if name == "spectrum.new_test_user_id":
                return _text({"user_id": new_test_user_id()})

            if name == "spectrum.list_workflows":
                items = await n8n.list_workflows(active=arguments.get("active"))
                summary = [
                    {"id": w.get("id"), "name": w.get("name"), "active": w.get("active")}
                    for w in items
                ]
                return _text({"workflows": summary, "count": len(summary)})

            if name == "spectrum.list_executions":
                workflow_id = _resolve_workflow_id(arguments.get("workflow", "AGENT PRINCIPAL"))
                data = await n8n.list_executions(
                    workflow_id=workflow_id,
                    status=arguments.get("status"),
                    limit=int(arguments.get("limit", 10)),
                )
                items = data.get("data", [])
                summary = [
                    {
                        "id": e.get("id"),
                        "workflowId": e.get("workflowId"),
                        "status": e.get("status") or ("finished" if e.get("finished") else "running"),
                        "mode": e.get("mode"),
                        "startedAt": e.get("startedAt"),
                        "stoppedAt": e.get("stoppedAt"),
                    }
                    for e in items
                ]
                return _text({"executions": summary, "nextCursor": data.get("nextCursor")})

            if name == "spectrum.get_execution":
                data = await n8n.get_execution(
                    arguments["execution_id"],
                    include_data=arguments.get("include_data", True),
                )
                return _text(data)

            if name == "spectrum.tail_executions":
                workflow_id = _resolve_workflow_id(arguments.get("workflow", "AGENT PRINCIPAL"))
                since_iso = arguments.get("since_iso") or datetime.now(timezone.utc).isoformat()
                since_dt = _parse_iso(since_iso)
                deadline = time.monotonic() + float(arguments.get("max_wait_seconds", 30))
                interval = float(arguments.get("poll_interval_seconds", 2.0))
                while True:
                    data = await n8n.list_executions(workflow_id=workflow_id, limit=10)
                    fresh = [
                        e
                        for e in data.get("data", [])
                        if e.get("startedAt") and _parse_iso(e["startedAt"]) > since_dt
                    ]
                    if fresh:
                        return _text({"executions": fresh, "matched": len(fresh)})
                    if time.monotonic() >= deadline:
                        return _text({"executions": [], "matched": 0, "timed_out": True})
                    await asyncio.sleep(interval)

            if name in ("spectrum.read_user_state", "spectrum.reset_user") and mongo is None:
                return _text({
                    "error": "MongoDB no está configurado. Define MONGO_URI en .env y reinicia el servidor."
                })

            if name == "spectrum.read_user_state":
                assert mongo is not None
                manychat_id = arguments["manychat_id"]
                history_kind = arguments.get("history_kind", "both")
                history_limit = int(arguments.get("history_limit", 10))
                state: dict[str, Any] = {
                    "user": mongo.get_user(manychat_id, arguments.get("page_id")),
                    "appointments": mongo.get_appointments(manychat_id, arguments.get("proyecto")),
                }
                if history_kind in ("main", "both"):
                    state["chat_histories"] = mongo.get_chat_history(
                        manychat_id, kind="main", limit=history_limit
                    )
                if history_kind in ("rsvp", "both"):
                    state["chat_histories_rsvp"] = mongo.get_chat_history(
                        manychat_id, kind="rsvp", limit=history_limit
                    )
                return _text(state)

            if name == "spectrum.reset_user":
                assert mongo is not None
                deleted = mongo.reset_test_user(arguments["manychat_id"])
                return _text({"deleted": deleted})

            return _text({"error": f"tool desconocida: {name}"})

        except N8nApiError as e:
            log.warning("n8n error: %s", e)
            return _text({"error": str(e), "status": e.status})
        except ResetNotAllowedError as e:
            return _text({"error": str(e)})
        except Exception as e:  # noqa: BLE001 — superficie hacia el cliente MCP
            log.exception("tool %s falló", name)
            return _text({"error": f"{type(e).__name__}: {e}"})

    return server, mongo


def _parse_iso(value: str) -> datetime:
    """ISO 8601 → datetime aware. n8n devuelve con 'Z' o '+00:00'."""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


async def _amain() -> None:
    try:
        config = Config.load()
    except RuntimeError as e:
        print(f"[spectrum-sim-mcp] config error: {e}", file=sys.stderr)
        sys.exit(2)
    server, mongo = build_server(config)
    log.info("starting spectrum-sim-mcp (n8n=%s, db=%s)", config.n8n_base_url, config.mongo_db)
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    finally:
        if mongo is not None:
            log.info("closing MongoDB connection")
            mongo.close()


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
