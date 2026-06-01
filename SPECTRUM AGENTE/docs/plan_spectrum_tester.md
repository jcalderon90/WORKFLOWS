# Plan — Spectrum Tester (Backend + Frontend para pruebas de Sof-IA)

> **Estado: PENDIENTE** — plan aprobado para construir más adelante. No iniciar implementación hasta confirmación.

## Contexto

El equipo de Spectrum necesita probar el agente unificado **Sof-IA** sin depender de scripts de
terminal (`test_agent.py`) ni de un cliente MCP. Hoy existe un equivalente en Python
(`spectrum-sim-mcp/`) pensado para que **IAs** simulen tráfico de ManyChat, pero **no hay UI** y el
público objetivo (equipo Spectrum) **no es técnico**.

Construiremos una **app web full‑stack** (Node.js + Express + frontend estático) que permita:
1. Lanzar una conversación de prueba contra Sof-IA — por **escenario predefinido** o por **datos
   manuales** que introduce el usuario.
2. Capturar la conversación **y** los datos de las ejecuciones de n8n correspondientes a esa
   conversación (orquestador + sub-workflows herramienta).
3. Enviar conversación + ejecuciones a un **LLM vía OpenRouter** para un análisis de calidad y
   técnico.
4. Mostrar todo en el frontend de forma **simple e intuitiva, en español**.

### Decisiones confirmadas con el usuario
- **LLM de análisis:** siempre **OpenRouter** (API compatible OpenAI, modelo por env var).
- **Modos de prueba:** (a) escenarios automáticos/predefinidos (portar los 10 de `test_agent.py`) y
  (b) entrada manual por formulario. UX mínima para no técnicos.
- **Persistencia:** nueva colección **`test_runs`** en el cluster Atlas existente (DB `Centralizado`).
- **Entorno:** golpea el **webhook de PRODUCCIÓN** con `manychat_id = test_<hex>` (limpiable con reset).

---

## Arquitectura propuesta

Una sola carpeta de nivel superior **`tester/`**, hermana de `spectrum-sim-mcp/`, con **un único
proceso Node** que sirve la API **y** el frontend estático (sin build step, sin CORS, un solo
`npm start`). El frontend es **HTML + JS vanilla + CSS** — justificado por el público no técnico y la
ausencia de tooling JS previo; migrable a Vite más adelante sin tocar la API.

```
tester/
  package.json            # express, mongodb, dotenv (Node 20+ trae fetch global)
  .env.example
  .gitignore
  README.md               # en español
  src/
    config.js             # PORT de config.py (env + WORKFLOW_IDS verbatim)
    server.js             # Express: monta rutas + estáticos + /api/health
    lib/
      webhook.js          # PORT de webhook.py (newTestUserId, buildPayload, sendMessage)
      n8nClient.js        # PORT de n8n_client.py (listWorkflows, listExecutions, getExecution)
      mongoStore.js       # PORT de mongo_client.py (+ DNS override + CRUD test_runs + reset)
      correlate.js        # NUEVO: correlación conversación -> ejecuciones
      openrouter.js       # NUEVO: servicio de análisis con OpenRouter
      scenarios.js        # NUEVO: los 10 escenarios portados (solo datos)
      runner.js           # NUEVO: orquesta un run multi-turno como job en background
      jobs.js             # NUEVO: registro de jobs en memoria + emisores SSE
    routes/
      scenarios.js        # GET /api/scenarios
      runs.js             # POST /api/runs, GET /api/runs, GET /api/runs/:id, GET /api/runs/:id/stream
      analysis.js         # POST /api/runs/:id/analyze, GET /api/runs/:id/analysis
      maintenance.js      # POST /api/reset (gated: test_ + MONGO_ALLOW_RESET)
  public/
    index.html            # SPA en español
    app.js                # fetch + render + EventSource (SSE)
    styles.css
```

### Sync vs async
Un run multi-turno tarda minutos (≈30s/turno por el debounce Redis de 10s + LLM; el escenario RSVP
son 8 turnos ≈ 4 min). Por eso: **job en background + SSE para progreso en vivo**, con **polling de
`GET /api/runs/:id` como fallback**. `POST /api/runs` crea el doc `test_runs` con `status:"running"`,
lanza el job y devuelve `{ runId }` de inmediato. `jobs.js` mantiene `Map<runId,{emitter,status}>`;
el runner **persiste cada turno** a Mongo para que un refresh/SSE tardío reconstruya estado.

---

## Endpoints REST

| Método | Ruta | Propósito |
|---|---|---|
| GET | `/api/scenarios` | Lista de 10 escenarios `{id, description, canal, messageCount}` |
| POST | `/api/runs` | Inicia run. Body scenario `{mode:"scenario", scenarioId, analyzeOnFinish?}` o manual `{mode:"manual", proyecto, canal, pageId?, phone?, messages:[...], analyzeOnFinish?}` → `201 {runId}` |
| GET | `/api/runs` | Historial paginado `?limit&cursor&status&mode` |
| GET | `/api/runs/:id` | Doc completo del run |
| GET | `/api/runs/:id/stream` | SSE: `turn_started`, `turn_completed`, `correlating`, `run_completed`, `analysis_ready`, `error` |
| POST | `/api/runs/:id/analyze` | Dispara (o re-dispara) análisis OpenRouter → `202` |
| GET | `/api/runs/:id/analysis` | Solo el subdocumento de análisis |
| POST | `/api/reset` | Limpia estado Mongo del `test_` user (gated) |

`analyzeOnFinish:true` (default en la UI) → un clic: corre y el análisis aparece solo.

---

## Algoritmo de correlación conversación → ejecuciones

La API de n8n **no filtra por user_id** y cada herramienta (`lead_collector`, `kb_search`, `rsvp`,
`send_media`) es un sub-workflow con sus **propias** ejecuciones. Correlación client-side, por turno:

1. Marcar `t0 = ahora UTC` **antes** de enviar; restar `CORRELATION_CLOCK_SKEW_MS` (buffer de reloj).
2. Enviar el mensaje (`sendMessage`, timeout 35s); marcar `t1` al responder.
3. Poll de ejecuciones de **AGENT PRINCIPAL** (`iXaptKTUXaXrP7aF`, `limit=10`, sin `includeData`)
   cada `CORRELATION_POLL_INTERVAL_MS` hasta `CORRELATION_MAX_WAIT_MS`; quedarse con `startedAt > t0`.
4. **Desambiguar** (runs concurrentes contaminan la lista): por cada candidato `getExecution(id,
   includeData=true)` e inspeccionar el nodo **`Webhook`** → match `body.id === testUserId`. Tomar la
   más antigua que coincida y **no reclamada** por un turno previo (rastrear `claimedExecutionIds`).
5. Ventana de correlación = `[startedAt, stoppedAt]` del padre.
6. **Recolectar ejecuciones de herramientas:** por cada ID de tool, listar recientes y filtrar por
   `startedAt` dentro de la ventana ± buffer. Reforzar con: (a) `depuracion.herramientas_usadas` del
   response del webhook (solo buscar tools reportadas) y (b) match de `sessionId == testUserId` cuando
   esté disponible.
7. Guardar por turno: padre (resumen de nodos + response) y lista de tool-executions
   `{workflowName, executionId, status, startedAt, stoppedAt, durationMs, nodes, keyOutput}`.

**Trim**: NO se guarda el JSON crudo completo de cada ejecución (tamaño). Se guarda `executionId` +
resumen de nodos `[{name, type, status, durationMs, error?}]`; detalle completo se puede lazy-fetch
vía proxy a `getExecution` si un usuario avanzado lo pide. Marcar `correlation.ambiguous=true` y
avisar suave en UI en vez de fallar.

---

## Modelo de documento `test_runs`

```js
{
  runId: "run_<hex>", mode: "scenario"|"manual", scenarioId: String|null,
  status: "running"|"completed"|"failed"|"analyzing"|"analyzed",
  createdAt, completedAt,
  input: { proyecto, canal, pageId, phone, testUserId: "test_<hex>" },
  turns: [{
    index, userText, sentAt, t0,
    webhook: { success, statusCode, elapsedMs, respuesta, accion, estadoLead, estadoProyecto,
               herramientasUsadas: [...], raw: {...} },
    validation: { expected, found, missing, passed } | null,
    principalExecution: { executionId, status, startedAt, stoppedAt, durationMs, nodes:[...] },
    toolExecutions: [{ workflowName, workflowId, executionId, status, startedAt, stoppedAt,
                       durationMs, nodes:[...], keyOutput:{...} }],
    correlation: { matched, candidatesInspected, ambiguous }
  }],
  summary: { turns, passed, failed, totalElapsedMs, toolsUsed:[...], hadErrors },
  analysis: {
    status:"ok"|"failed"|null, model, analyzedAt,
    conversation: { funnel_stage, intencion_detectada, tools_correctas, errores_detectados,
                    oportunidades_perdidas, tono_agente, puntuacion, recomendacion },
    technical: [{ turnIndex, executionId, nodesRun, errores:[...], latenciaMs, nodoMasLento, observacion }],
    rawLlm: String|null
  },
  error: null|String
}
```
Índices: `{runId:1}` único, `{createdAt:-1}`, `{"input.testUserId":1}`.

El esquema de `analysis.conversation` replica el precedente del nodo **Quality Auditor** de
`Sync_CRM.json` (colección `quality_logs`).

---

## Servicio OpenRouter (`openrouter.js`)

- `POST https://openrouter.ai/api/v1/chat/completions`, header `Authorization: Bearer
  $OPENROUTER_API_KEY`, `model=$OPENROUTER_MODEL` (default p.ej. `openai/gpt-4o-mini`),
  `temperature:0.2`, `response_format:{type:"json_object"}`.
- **Contexto enviado (trim por tokens):** transcript compacto (`Usuario:` / `Sof-IA:` + `[tools]` +
  `[accion]`) + resumen de ejecución por turno (estado/duración/nº nodos/errores/tools). KB SEARCH:
  query y si hubo resultados (no los chunks). RSVP: campos de la cita (no el nodo entero). **Hard
  trims:** descartar strings > 500 chars, vectores/embeddings, base64/URLs de media; si excede
  presupuesto (~12k tokens) recortar primero el detalle de turnos que pasaron, conservar los que
  fallaron.
- **Prompt (español):** system = auditor de calidad de Sof-IA; incluir la regla del gate de
  validación (no `kb_search`/`rsvp`/`send_media` antes de nombre+correo+teléfono) para que pueda
  marcar violaciones. Salida = JSON `{conversation:{...}, technical:[...]}`.
- Parseo defensivo (puede venir en markdown); validar `puntuacion` numérica; en fallo →
  `analysis.status="failed"` + `rawLlm`, error amable en UI.

---

## Frontend (HTML + JS vanilla, español)

Pantallas:
1. **Lanzar prueba** — dos pestañas: *Escenarios predefinidos* (tarjetas con nombre/desc/canal +
   "Ejecutar") y *Conversación manual* (proyecto, canal, lista repetible de mensajes "Agregar
   mensaje", teléfono prellenado). Checkbox "Analizar con IA al terminar" (default on).
2. **Ejecución en vivo** — timeline turno a turno que se llena por SSE (mensaje, respuesta, chips de
   tools, tiempo, badge pass/fail, spinner por turno pendiente, barra `turno k/N`).
3. **Resultado del run** — transcript + panel de ejecución por turno (nodos, duraciones, errores,
   expandible) + tarjeta de análisis IA (puntuación grande, badge funnel_stage,
   errores/oportunidades/recomendación) + botón "Limpiar datos de prueba".
4. **Historial** — tabla de runs (fecha, modo, escenario, puntuación, estado) → pantalla 3.

Render functions en `app.js`: `ScenarioCard`, `ManualForm`, `TurnTimeline`, `ExecutionPanel`,
`AnalysisCard`, `RunsTable`.

---

## Reuso: Python (spectrum-sim-mcp) → Node

| Python | Módulo Node | Notas |
|---|---|---|
| `config.py` (`Config.load`, `WORKFLOW_IDS`) | `src/config.js` | env vía `dotenv`; `WORKFLOW_IDS` verbatim; + vars OpenRouter/PORT |
| `webhook.py` | `src/lib/webhook.js` | `fetch` global + `AbortController` (timeout 35s); conservar shape `{success,status_code,elapsed_ms,data}` |
| `n8n_client.py` | `src/lib/n8nClient.js` | header `X-N8N-API-KEY`; `limit` 1..250; toggle `includeData` |
| `mongo_client.py` | `src/lib/mongoStore.js` | driver `mongodb`; **`dns.setServers(['8.8.8.8','8.8.4.4'])`** al cargar (equivalente al override dnspython para ECONNREFUSED Atlas); portar `reset_test_user` (gate `test_` + `MONGO_ALLOW_RESET`); + CRUD `test_runs` |
| `server.py` `tail_executions` + `_parse_iso` | `src/lib/correlate.js` | base del poll; extender con match `Webhook.body.id` + ventana de tools |
| `test_agent.py` (`TEST_SCENARIOS`, `validate_response`) | `src/lib/scenarios.js` + `runner.js` | 10 escenarios como datos; lógica de keywords al runner |
| (nuevo) | `openrouter.js`, `jobs.js`, `runner.js` | net-new |

---

## `.env.example`

```
N8N_BASE_URL=https://agentsprod.redtec.ai
N8N_WEBHOOK_URL=https://agentsprod.redtec.ai/webhook/spectrum-agent
N8N_API_KEY=
MONGO_URI=
MONGO_DB=Centralizado
MONGO_ALLOW_RESET=true
DEFAULT_PAGE_ID=page_spectrum_test
WEBHOOK_TIMEOUT=35
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openai/gpt-4o-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
PORT=4000
TEST_RUNS_COLLECTION=test_runs
CORRELATION_POLL_INTERVAL_MS=2000
CORRELATION_MAX_WAIT_MS=25000
CORRELATION_CLOCK_SKEW_MS=5000
```
`config.js` falla rápido (en español) si faltan claves n8n; la clave OpenRouter solo se exige al
invocar análisis (los runs funcionan sin ella).

---

## Riesgos / edge cases
- **Falsos positivos de correlación (runs concurrentes):** confirmar siempre por `Webhook.body.id`
  (padre) + ventana/tools-reportadas/`sessionId` (tools); rastrear `claimedExecutionIds`; marcar
  `ambiguous` en vez de fallar.
- **Timeouts 35s / debounce:** serializar turnos (no disparar i+1 antes de cerrar i); pausa 2s entre
  mensajes; timeout = turno fallido pero el run continúa. Job en background → no hay timeout HTTP.
- **Límite de tokens OpenRouter:** nunca enviar JSON crudo de nodos; trims agresivos; degradar a solo
  turnos fallidos si excede.
- **Contaminación de datos en PROD:** siempre `test_`; botón reset por run; reset gated.
- **Clock skew host↔n8n:** buffer `CORRELATION_CLOCK_SKEW_MS` + preferir match por identidad.
- **Uso no técnico:** validar formulario manual server-side, errores en español.

---

## Orden de construcción (por fases)

- **Fase 0 — Scaffold:** `tester/` + `package.json` + `config.js` + `.env.example` + `server.js`
  (estáticos + `/api/health`). Portar `webhook.js` y `n8nClient.js`.
- **Fase 1 — MVP (escenario, en vivo por SSE):** portar `scenarios.js` + `validate_response`;
  `runner.js` corre turno a turno y persiste `test_runs` básico; `POST/GET /api/runs`,
  `GET /api/runs/:id/stream`; frontend mínimo (lista, lanzar, timeline, resultado). **Ya es usable.**
- **Fase 2 — Modo manual:** formulario + rama `mode:"manual"`; `GET /api/scenarios`; historial.
- **Fase 3 — Correlación de ejecuciones:** `correlate.js` (match padre + ventana tools); enriquecer
  turnos; `ExecutionPanel` en UI.
- **Fase 4 — Análisis IA:** `openrouter.js` (trim + prompt + parse); `POST .../analyze`,
  `GET .../analysis`, `analyzeOnFinish`; `AnalysisCard`.
- **Fase 5 — Mantenimiento + hardening:** `resetTestUser` + `POST /api/reset` + botón UI;
  salvaguardas de concurrencia; validación, errores, README en español.

---

## Archivos críticos (a crear / a leer como referencia)

**Referencia (leer, portar):**
- `spectrum-sim-mcp/src/spectrum_sim_mcp/webhook.py` — payload + envío exactos
- `spectrum-sim-mcp/src/spectrum_sim_mcp/n8n_client.py` — cliente REST n8n
- `spectrum-sim-mcp/src/spectrum_sim_mcp/mongo_client.py` — DNS override + reset guardrails
- `spectrum-sim-mcp/src/spectrum_sim_mcp/server.py` — `tail_executions` (base de correlación)
- `spectrum-sim-mcp/src/spectrum_sim_mcp/config.py` — `Config.load` + `WORKFLOW_IDS`
- `Agente Unificado/scripts/test_agent.py` — 10 escenarios + `validate_response`
- `Agente Unificado/Sync_CRM.json` (nodo *Quality Auditor*) — esquema de análisis precedente

**A crear:** todo bajo `tester/` (ver árbol arriba).

---

## Verificación end-to-end (cuando se implemente)

1. **Boot:** `cd tester && npm install && cp .env.example .env` (rellenar `N8N_API_KEY`, `MONGO_URI`,
   `OPENROUTER_API_KEY`), `npm start` → `GET http://localhost:4000/api/health` responde `ok`.
2. **Smoke (escenario):** abrir la UI → ejecutar `saludo_inicial` → ver respuesta de Sof-IA en el
   timeline en vivo (~35s).
3. **Correlación:** verificar que el resultado muestra `principalExecution` con `executionId` real y
   cruzar contra n8n (`GET /api/v1/executions/{id}`) que `body.id == test_<hex>`.
4. **Manual + análisis:** correr una conversación manual de 3-4 mensajes con `analyzeOnFinish` →
   confirmar que aparece la `AnalysisCard` con `puntuacion` y `funnel_stage`.
5. **Persistencia:** confirmar doc en `db.Centralizado.test_runs`.
6. **Reset:** botón "Limpiar datos de prueba" → confirmar que `users`/`appointments`/`chat_histories`
   del `test_` user quedan en 0.
7. (Opcional) Comparar con el flujo Python: `python3 "Agente Unificado/scripts/test_agent.py"
   --scenario saludo_inicial` debe dar una respuesta equivalente a la de la UI.
