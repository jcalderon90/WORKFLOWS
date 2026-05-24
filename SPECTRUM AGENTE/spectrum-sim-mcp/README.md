# spectrum-sim-mcp

Servidor MCP que permite a cualquier IA (Claude Desktop/Code, Cursor, Gemini CLI con MCP, Continue) **simular conversaciones con el agente Sof-IA como si fuera un cliente real de ManyChat** y, además, **observar las ejecuciones de n8n** y el estado en MongoDB que esas conversaciones produjeron.

Es decir: la IA no sólo manda mensajes — también puede leer qué pasó dentro de los workflows.

---

## Tools que expondrá

| Tool | Qué hace |
|---|---|
| `spectrum.send_message` | POST al webhook `https://agentsprod.redtec.ai/webhook/spectrum-agent` con payload tipo ManyChat. Devuelve la respuesta sincrónica del orquestador. |
| `spectrum.list_executions` | Lista las ejecuciones recientes de un workflow (vía API n8n), filtrables por estado y por `user_id`. |
| `spectrum.get_execution` | Devuelve el detalle nodo-por-nodo de una ejecución específica: input/output de cada nodo, errores, timing. |
| `spectrum.tail_executions` | Polling sobre nuevas ejecuciones de un workflow desde un timestamp dado (para "ver en vivo" tras un `send_message`). |
| `spectrum.read_user_state` | Lectura de Mongo: documento `users`, `appointments`, últimas N entradas de `chat_histories`/`chat_histories_rsvp` para un `manychat_id`. |
| `spectrum.reset_user` | Borra los documentos de un usuario `test_*` en todas las colecciones (sólo permite prefijo `test_` por seguridad). |
| `spectrum.list_workflows` | Devuelve el mapa nombre → id de workflows en el servidor (atajo para no memorizar IDs). |

Todas las tools llevan validación de inputs y descripciones detalladas para que el modelo de la IA cliente entienda qué espera cada parámetro.

---

## Arquitectura

```
              MCP client (Claude/Gemini/etc)
                         │
                         │  JSON-RPC stdio
                         ▼
              spectrum-sim-mcp (este proyecto)
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Webhook n8n      n8n REST API     MongoDB Atlas
   (envío msg)      (executions)     (lectura state)
```

- **Webhook:** POST a `agentsprod.redtec.ai/webhook/spectrum-agent` — mismo flujo que ya usa `test_agent.py`.
- **n8n REST API:** `GET /api/v1/executions?workflowId=…` con header `X-N8N-API-KEY`.
- **Mongo:** conexión read-only directa a la base `Centralizado` para inspeccionar `users`, `appointments`, `chat_histories*`.

---

## Estructura

```
spectrum-sim-mcp/
├── README.md           ← este archivo
├── pyproject.toml      ← deps + entrypoint del servidor MCP
├── .env.example        ← variables que el servidor lee
├── src/spectrum_sim_mcp/
│   ├── server.py       ← MCP server (registra tools, despacha)
│   ├── n8n_client.py   ← wrapper REST n8n
│   ├── mongo_client.py ← wrapper Mongo (read-only + reset acotado a test_*)
│   ├── webhook.py      ← POST al webhook con payload tipo ManyChat
│   └── tools/          ← una tool por archivo
└── tests/              ← pruebas locales del servidor (no del agente)
```

---

## Instalación

Requiere Python 3.10+.

```powershell
cd "spectrum-sim-mcp"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env   # luego edita .env y completa N8N_API_KEY, MONGO_URI, DEFAULT_PAGE_ID
```

Verifica que arranca (debe quedarse esperando en stdio — Ctrl+C para salir):

```powershell
spectrum-sim-mcp
```

## Conectarlo desde una IA cliente

Todas las IAs MCP-compatibles usan el mismo patrón: añadir el comando al bloque `mcpServers` de su archivo de config.

### Claude Desktop / Claude Code

`%APPDATA%\Claude\claude_desktop_config.json` (Desktop) o `~/.claude.json` (Claude Code):

```json
{
  "mcpServers": {
    "spectrum-sim": {
      "command": "spectrum-sim-mcp",
      "env": {
        "N8N_BASE_URL": "https://agentsprod.redtec.ai",
        "N8N_WEBHOOK_URL": "https://agentsprod.redtec.ai/webhook/spectrum-agent",
        "N8N_API_KEY": "...",
        "MONGO_URI": "mongodb+srv://...",
        "MONGO_DB": "Centralizado",
        "DEFAULT_PAGE_ID": "page_spectrum_test",
        "MONGO_ALLOW_RESET": "true"
      }
    }
  }
}
```

Si prefieres mantener las credenciales en `.env`, omite el bloque `env` y deja que el servidor lo cargue.

### Cursor

`~/.cursor/mcp.json` (mismo shape que Claude Desktop).

### Gemini CLI

`~/.gemini/settings.json` → bajo la clave `mcpServers`, mismo shape.

### Continue (VS Code)

`~/.continue/config.json` → bajo `mcpServers`, mismo shape.

## Cómo lo usa la IA

Conversación típica:

> "Saluda al agente como cliente nuevo, espera la respuesta, dime qué herramientas se llamaron en la última ejecución y qué quedó en `users`."

La IA encadena:

1. `spectrum.new_test_user_id` → guarda el `user_id`.
2. `spectrum.send_message` con ese `user_id` y `text: "Hola"` → recibe la respuesta.
3. `spectrum.tail_executions` con `workflow: "AGENT PRINCIPAL"` → captura el id de la ejecución que ese mensaje disparó.
4. `spectrum.get_execution` con ese id → ve los nodos que corrieron y sus inputs/outputs.
5. `spectrum.read_user_state` con el `user_id` → ve qué se guardó en Mongo.
6. (opcional) `spectrum.reset_user` para dejar limpio.

## Limitaciones conocidas

- El webhook responde sincrónicamente tras ~10–35 s (Wait + procesamiento IA). Subir `WEBHOOK_TIMEOUT` si vas a usar prompts largos.
- `list_executions` de n8n no filtra por `user_id` nativamente — `tail_executions` resuelve el caso común (la ejecución que acabas de disparar), pero buscar la ejecución de un mensaje *del pasado* requiere leer payload por payload.
- `reset_user` borra docs en `users`, `appointments`, `chat_histories`, `chat_histories_rsvp`. No purga vector store ni logs de `analytics_logs` (intencional — son auditoría).

## Logs

El servidor escribe a `~/.spectrum-sim-mcp.log` (configurable con `SPECTRUM_MCP_LOG`). Si una tool falla, ahí encontrarás el stack trace completo; al cliente MCP sólo se le devuelve el mensaje resumido.
