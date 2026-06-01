# INDEX — Spectrum Vivienda (Sof-IA)

> **Mapa de navegación token-eficiente.** Lee esto PRIMERO para ubicar cualquier archivo/nodo
> sin escanear el repo. Reglas de negocio y gotchas viven en `CLAUDE.md`; este archivo dice
> **dónde está cada cosa**. La sección de nodos se regenera con `./scripts/build_index.sh`.
>
> Última actualización manual: 2026-06-01 (+ plan Tester Web `docs/plan_spectrum_tester.md`)

---

## 🗺️ Mapa de carpetas

| Ruta | Qué contiene |
|---|---|
| `Agente Unificado/*.json` | **11 workflows n8n** (fuente de verdad, se pushean al server) |
| `Agente Unificado/scripts/` | Test runner (`test_agent.py`) + helpers jq de inspección de nodos |
| `Agente Unificado/.skills/` | Skills de dominio + n8n (expresiones, nodos, validación, code nodes) |
| `KBs/*.json` | Knowledge bases fuente. Re-vectorizar tras editar (workflow `LLiVnT0M6xvDKive`) |
| `docs/` | Changelog vivo, catálogos SOAP, reportes, estrategia |
| `scripts/` | Comparadores Python + patchers JS de workflows + este `build_index.sh` |
| `spectrum-sim-mcp/` | Servidor MCP (Python) para simular tráfico ManyChat e inspeccionar n8n/Mongo |
| `tester/` | 📝 **PLANEADO (no creado)** — App web Node+Express+frontend para que el equipo Spectrum pruebe Sof-IA + análisis IA. Plan: `docs/plan_spectrum_tester.md` |
| `postman/` | Colección Postman + scripts fetch leads + reportes fase 2 (CSV) |
| `flujos de muestra Version anterior/` | Workflows legacy monolíticos — referencia, NO en producción |

---

## ⚙️ Workflows — propósito · ID remoto n8n

| Archivo | Propósito (1 línea) | ID n8n | Nodos |
|---|---|---|---|
| `AGENT PRINCIPAL.json` | Orquestador (gpt-5-mini). Clasifica intención y delega a tools vía Execute Workflow. **Gate de validación name+email+phone.** | `iXaptKTUXaXrP7aF` | 77 |
| `Lead Collector.json` | Captura name/email/phone, split primer_nombre/apellidos vía LLM, persiste a Mongo. Único tool llamable antes del gate. | `SHPFhvoal7k1Rqf9` | 16 |
| `KB SEARCH.json` | RAG sobre Mongo Atlas Vector Index, filtrado por `proyecto` (UPPERCASE). | `D3LKuNi6CmMIdvzg` | 8 |
| `RSVP.json` | Agenda citas. Escribe a `appointments`. Sin validación de horario hábil. | `TjFPzHs5aimxILH7` | 23 |
| `Send Media.json` | Brochures/renders. Siempre responde positivo aunque URL sea null. | `NtTiyrNy2LHimE7u` | 6 |
| `Sync_CRM.json` | Scheduled (~10–15 min). POST a Dynamics 365 SOAP. Construye `_UTMCampaing`. Protección atribución fase_2. | `TTVNRX38pPoPmK2X` | 32 |
| `Notifications Master.json` | Emails HTML (nuevo lead, interés precios, cita, escalación). Destinatarios hardcoded. | `r1Jf5vwrkBrT4dEu` | 10 |
| `Vectorizar los KBs.json` | Ingesta `KBs/*.json` a la colección vector. Correr tras editar un KB. | `LLiVnT0M6xvDKive` | 6 |
| `Analytics Centralizado.json` | 🆕 Scheduled. Agrega métricas diarias por usuario vía agente LLM → actualiza Mongo. | _sin desplegar/confirmar_ | 18 |
| `LEAD FASE 2.json` | 🆕 Scaffold. Webhook de entrada para leads fase 2 (Tribal). Aún 1 solo nodo. | _scaffold_ | 1 |
| `WEB FORM.json` | 🆕 Webhook de formulario web → inserta appointment + email Gmail con HTML. | _sin desplegar/confirmar_ | 6 |

> ⚠️ Los 3 workflows 🆕 (`Analytics Centralizado`, `LEAD FASE 2`, `WEB FORM`) no tienen ID
> remoto registrado en `CLAUDE.md`/`config.py`. Verificar en el server antes de asumir que
> están desplegados. `LEAD FASE 2.json` es un scaffold (solo webhook).

---

## 📂 Scripts

| Ruta | Qué hace |
|---|---|
| `scripts/build_index.sh` | Regenera la sección AUTO-NODES de este INDEX.md (jq) |
| `scripts/compare.py` | Diff de dos workflow JSON por nombre de nodo y parámetros (editar paths al final) |
| `scripts/report_mayo.py` | Reporte de leads de mayo |
| `scripts/sync_fix.py` | Fix/parche relacionado a Sync_CRM |
| `scripts/update_vectorizer.js` | Patcher JS del workflow Vectorizar KBs |
| `scripts/update_workflow.js` | Patcher JS genérico de workflows |
| `Agente Unificado/scripts/test_agent.py` | Test runner E2E contra webhook prod (`--list`, `--scenario`, suite) |
| `Agente Unificado/scripts/list-nodes.sh` | Lista nodos de un workflow |
| `Agente Unificado/scripts/get-node.sh` | Vuelca un nodo por nombre |
| `Agente Unificado/scripts/get-node-param.sh` | Vuelca un parámetro de un nodo (`systemMessage`, `jsCode`, etc.) |
| `Agente Unificado/scripts/search-nodes.sh` / `search.sh` / `find-all.sh` / `get-context.sh` | Helpers de búsqueda dentro de workflows |
| `Agente Unificado/scripts/run_tests.sh` | Lanza la suite de pruebas |
| `postman/fetch_leads.py` | Descarga leads vía API Postman |

---

## 📚 Docs

| Ruta | Qué contiene |
|---|---|
| `docs/estado_proyecto.md` | **Changelog vivo** — leer antes de cambios no triviales (explica el *por qué* de los quirks) |
| `docs/spectrum-soap-api.md` | Catálogos SOAP completos (códigos `_UTMSource`, `_OrigenCliente`, etc.) |
| `docs/auditoria_workflows_2026-05-25.md` | Auditoría de estado de workflows (deuda técnica, scaffolds) |
| `docs/comparativa_versiones.md` | Comparativa entre versiones de workflows |
| `docs/estrategia_captacion_whatsapp.md` | Estrategia de captación WhatsApp ("Regla de Oro") |
| `docs/reporte-fase2-mayo-2026.md` | Reporte de leads fase 2, mayo 2026 |
| `docs/plan_spectrum_tester.md` | 📝 **PLAN PENDIENTE** — Tester Web (Node+Express+frontend) para probar Sof-IA + análisis IA vía OpenRouter. Carpeta `tester/` aún no creada |
| `docs/Source Links_ Spectrum - Nuevo.csv` | Links fuente |

---

## 🧠 KBs (knowledge bases) — código de proyecto · # chunks

| Archivo | Código | Proyecto | Chunks |
|---|---|---|---|
| `KBs/KB PVV.json` | `PVV` | Parque Vista Verde ⭐ (entrega Oct 2026) | 33 |
| `KBs/KB PMAR.json` | `PMAR` | Parque Mariscal (único con tráfico aprobado) | 42 |
| `KBs/KB PPO.json` | `PPO` | Parque Portales ⭐ (entrega Dic 2026) | 42 |
| `KBs/KB PPOL.json` | `PPOL` | Parque Polanco | 29 |
| `KBs/KB PSB.json` | `PSB` | Parque Sotobosque | 43 |

Vector: colección `documents`, índice `spectrum_vector_index`, filtro por `proyecto` (UPPERCASE).

---

## 🐍 spectrum-sim-mcp (servidor MCP)

| Archivo | Rol |
|---|---|
| `src/spectrum_sim_mcp/server.py` | Define las 8 tools MCP (`send_message`, `read_user_state`, `reset_user`, …) |
| `src/spectrum_sim_mcp/webhook.py` | Construye el payload ManyChat (shape debe matchear lo que lee AGENT PRINCIPAL) |
| `src/spectrum_sim_mcp/n8n_client.py` | Cliente n8n API (`WORKFLOW_IDS` espejo de la tabla de arriba) |
| `src/spectrum_sim_mcp/mongo_client.py` | Cliente Mongo (guardrail `reset_user`: requiere `MONGO_ALLOW_RESET=true` + id `test_`) |
| `src/spectrum_sim_mcp/config.py` | Config + `WORKFLOW_IDS` |

---

## 🗃️ Colecciones MongoDB (resumen)

`users` · `appointments` (query por `manychat_id`+`proyecto`) · `chat_histories` · `chat_histories_rsvp`
· `manychat_settings` (page_id→proyecto) · `quality_logs` · `analytics_logs` · `documents` (vector).

---

## 🔎 Inventario de nodos por workflow (auto-generado)

> Para abrir un nodo concreto:
> `./Agente\ Unificado/scripts/get-node.sh "Agente Unificado/<archivo>.json" "<nombre nodo>"`

<!-- BEGIN AUTO-NODES -->
<!-- Generado por scripts/build_index.sh — NO editar a mano -->

#### AGENT PRINCIPAL.json (77 nodos)
RESPOND TO MANYCHAT · Parameter Type · User Data · No Operation, do nothing · If NO WHATSAPP · Proyecto · Lenguaje & Asesoria · Update User · Insert User · Find User · CONTEXT 1 · DATA to CREATE · DATA to UPDATE · If USER NOT EXIST · PARSE BODY · JOINNING MESSAGE · PROJECT LIST · Filter1 · DELETE MESSAGES · Wait · GET MESSAGE · SAVE MESSAGE · INPUT FINAL · audio input · image input · text input · HTTP IF AUDIO · ANALIZA IMAGEN · Aggregate · Sort · Merge · TRANSCRIBE AUDIO · ES AUDIO / IMAGEN · HTTP Request · ES ARCHIVO · Create Body · Webhook · MongoDB Chat Memory · PRINCIPAL · lead_collector · Parse response · If TIENE DATOS NUEVOS · Prepare Update · Hay Cambios? · Update User Lead · No Operation, do nothing1 · kb_search · rsvp · Filter IF TRANSFER · Insert Analytics · Calculate Respond Time · 'Notifications Master' Nuevos Leads · 'Notifications Master' Escalation · send_media · No Operation, do nothing2 · IF NUEVO LEAD · Find user by Phone · If NOT WHATSAPP · If NOT EXIST · Insert User Fase 2 · ID - Lead en Fase 2  · Extraer CAMPAIGN DATA · Get Account Credentials · UPDATE - Proyecto Interes · Filtrar Proyecto Existente · UPDATE - UTM Source · IF INTERES PRECIOS · 'Notifications Master' Interés Precios · IF FUERA DE CONTEXTO · OFF TOPIC - Respuesta · OFF TOPIC - Respond · OpenRouter Chat Model · DATA to CREATE FASE 2 · Update Lead FASE 2 · OpenRouter Chat Model1 · OpenRouter Chat Model2 · UPDATE - Proyecto Interes FASE 2

#### Analytics Centralizado.json (18 nodos)
Schedule Trigger · Edit Fields2 · Loop Over Items · Replace Me · Merge · ENCONTRAR USER DIARIO · USUARIO Y KEY · ENCONTRAR USUARIOS · AGENTE RESPUESTA · PARSEAR RESPUESTA · RESPUESTA AGENTE · CAMPOS COMPLETOS · PASEAR RESPUESTA · ACTUALIZAR USER · If · If1 · DIA ACTUAL · OpenRouter Chat Model

#### KB SEARCH.json (8 nodos)
START · Search Context · GENERAL AGENT · Code in JavaScript · Knowledge Base · RESPONSE · Embeddings OpenAI · OpenRouter Chat Model

#### LEAD FASE 2.json (1 nodos)
Webhook

#### Lead Collector.json (16 nodos)
START · SET CONTEXT · Lead Agent · MongoDB Chat Memory · Parse Response · GENERAR LEAD CONTACT · IF DATA COMPLETED · LEAD DATA · No Operation, do nothing · RESPONSE · PARSE BODY · Body · IF CRM OK · Update User · CRM Data · OpenRouter Chat Model

#### Notifications Master.json (10 nodos)
START · Switch Alerta · Payload Nuevo Lead · Payload Precios · Payload Cita · Payload Escalación · Send Gmail Notification · Edit Fields · IF Test User · Skip Test

#### RSVP.json (23 nodos)
START · CONTEXT · RSVP Agent · MongoDB Chat Memory · If TIENE FECHA · IF APPOINTMENT EXIST · Update Appointment Data · Insert Appointment Data · Update Appointment · Insert Appointment · 'Notifications Master' Cita · IF CONFIRMADA · RESPONSE 1 · NADA · RESPONSE FINAL · HTML · Parse RSVP Output · HTML PURO · Update User · reservation update · OpenRouter Chat Model · Find Appointment · Find User

#### Send Media.json (6 nodos)
Map Media Resources · IF Media Disponible · Send API ManyChat · Response To Agent · No Media Response · START

#### Sync_CRM.json (32 nodos)
Schedule Trigger · Loop Over Users · Messages · Merge · Find Appointment · Manychat User ID · Time-15min · Information Extractor · EXTRACTOR RESPONSE · GENERAR LEAD CONTACT · XML BODY · Body · PARSE BODY · No Operation, do nothing · Find Users to Sync · Chat Lead · Chat RSVP · Chat · Aggregate · LEAD · RSVP · PRINCIPAL · Quality Auditor · Build Quality Log · Insert quality_logs · Update Conversation Analysis · DATA to UPDATE · Find User Credentials · UPDATE - Proyecto Interes Manychat · Campos Usuario · OpenRouter Chat Model · OpenRouter Chat Model1

#### Vectorizar los KBs.json (6 nodos)
Embeddings OpenAI1 · Default Data Loader1 · Split Out · LISTA de CHUNKS · MongoDB Atlas Vector Store CHUNKS · When clicking ‘Execute workflow’

#### WEB FORM.json (6 nodos)
Webhook · Insert Appointment · APPOINTMENT · Send a message · Code in JavaScript · HTML

<!-- END AUTO-NODES -->
