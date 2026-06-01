# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 🧭 RULE 0 — Consult INDEX.md before searching

**BEFORE using Grep / Glob / Explore (or any broad file search) to locate a workflow, node, script, doc, KB, or module, READ `INDEX.md` first.** It maps every file/node in the repo and is far cheaper than scanning. Only fall back to a real search when `INDEX.md` doesn't answer the question.

After adding/removing nodes or workflows, run `./scripts/build_index.sh` to refresh the node inventory — a stale index is worse than none. If you notice `INDEX.md` disagrees with reality, fix it (or regenerate) before relying on it.

---

## What this repo is

n8n workflow source for **SPECTRUM VIVIENDA** — a multitenant real-estate conversational agent (*Sof-IA*) deployed on `https://agentsprod.redtec.ai`. The local `.json` files are the authoritative workflow definitions; they are pushed to the n8n server via MCP. The server is the runtime; this repo is the source of truth.

The agent receives ManyChat traffic from 6 pages (WhatsApp / Instagram / Messenger across 5 real-estate projects + GAROO internal). A central orchestrator (`AGENT PRINCIPAL.json`) classifies intent and delegates to sub-workflows (tools). Persistence is MongoDB Atlas; CRM sync is deferred via SOAP.

---

## 🔴 CRITICAL RULE — Data validation gate

`AGENT PRINCIPAL.json` must NEVER call `kb_search`, `rsvp`, or `send_media` until the lead has shared **name + email + phone**. The only tool callable before that gate is `lead_collector`.

This is enforced in the `PRINCIPAL` node's `systemMessage` under "🔴 VALIDACIÓN OBLIGATORIA PRIMERO". If you edit that system prompt, **do not weaken this rule** — it was added to fix a real 2026-05-22 incident where the bot answered project questions to an anonymous lead.

---

## Architecture

```
Agente Unificado/
├── AGENT PRINCIPAL.json       ← Orchestrator (gpt-5-mini). Classifies intent, calls tools via Execute Workflow
├── Lead Collector.json        ← Captures name/email/phone, splits primer_nombre/apellidos via LLM, persists to MongoDB
├── KB SEARCH.json             ← RAG over MongoDB Atlas Vector Index, filtered by proyecto
├── RSVP.json                  ← Appointment booking. Writes to `appointments`. No business-hours validation
├── Send Media.json            ← Brochures/renders. Always responds positively even when URL is null
├── Sync_CRM.json              ← Scheduled (~10–15 min). Posts to Dynamics 365 SOAP. Builds _UTMCampaing summary
├── Notifications Master.json  ← HTML email alerts (new lead, price interest, appointment, escalation). Recipients hardcoded; not configurable per-page.
├── Vectorizar los KBs.json    ← Ingests KBs/*.json into the vector collection
├── Analytics Centralizado.json ← 🆕 Scheduled. Aggregates daily per-user metrics via an LLM agent → updates MongoDB
├── LEAD FASE 2.json           ← 🆕 Scaffold (single webhook). Inbound entrypoint for phase-2 (Tribal) leads — not yet built out
└── WEB FORM.json              ← 🆕 Web-form webhook → inserts appointment + sends Gmail HTML confirmation

KBs/                            ← Source-of-truth knowledge bases. Re-vectorize via the n8n workflow after editing
docs/                           ← Project state and reference docs
INDEX.md                        ← 🗺️ Navigation map of the whole repo (read first to locate files/nodes; regen with scripts/build_index.sh)
scripts/                        ← Python comparators and JS workflow patchers (root-level scripts/)
Agente Unificado/scripts/       ← Test runner + jq helpers (workflow-level scripts/)
spectrum-sim-mcp/               ← MCP server (Python) — lets external AIs simulate ManyChat traffic and read n8n/Mongo state
```

**Channel routing:** `manychat_settings` (MongoDB) maps `page_id` → `proyecto`. For Instagram/Messenger the project is pre-assigned by `page_id`; for WhatsApp the "Regla de Oro" interactive menu fires unless `custom_fields.proyecto_interes` is pre-set (phase-2 campaign leads). The `CONTEXT 1` node in `AGENT PRINCIPAL.json` implements this resolution order.

**Message debouncing:** Redis groups rapid messages (10s wait) before the orchestrator processes them — that's why webhook tests need a ~35s timeout.

**Deferred CRM sync:** Leads are flagged with `conversation_analysis: false` on each new message; `Sync_CRM.json` runs on schedule, picks up leads idle >10–15 min, generates the summary, posts to SOAP, then sets `conversation_analysis: true`.

---

## MongoDB collections

| Collection | Purpose |
|---|---|
| `users` | Lead profile (one doc per `manychat_id` + `page_id`) |
| `appointments` | RSVP bookings. **Query by `manychat_id` + `proyecto`** — a user can have appointments across multiple projects |
| `chat_histories` | Orchestrator memory |
| `chat_histories_rsvp` | RSVP agent memory (separate from above) |
| `manychat_settings` | Per-page config: `page_id`, `api_key`, `proyecto` |
| `quality_logs` | Post-sync audit |
| `analytics_logs` | Latency + tool-call telemetry |
| `documents` (vector) | KB chunks. Index: `spectrum_vector_index`. **Filter by `proyecto` field in UPPERCASE.** |

KB → project code mapping:

| File | Code |
|---|---|
| `KBs/KB PVV.json` | `PVV` (Parque Vista Verde — ⭐ entrega Oct. 2026) |
| `KBs/KB PMAR.json` | `PMAR` (Parque Mariscal — only project with approved traffic) |
| `KBs/KB PPO.json` | `PPO` (Parque Portales — ⭐ entrega Dic. 2026) |
| `KBs/KB PPOL.json` | `PPOL` (Parque Polanco) |
| `KBs/KB PSB.json` | `PSB` (Parque Sotobosque) |

After editing a KB, re-run the `Vectorizar los KBs` workflow on the server (ID `LLiVnT0M6xvDKive`) so changes hit production.

---

## SOAP CRM — non-obvious rules

**Endpoint:** `https://crm.spectrum.com.gt:8055/Spectrum_WS_GeneracionLead/Service.asmx` (note **`Service.asmx`** — capital S; lowercase `service.asmx` was a bug fixed 2026-05-22).
**SOAPAction:** `http://tempuri.org/CreacionClientePotencialBot`

### XML tag typos — these are intentional, do NOT "fix" them
- Email tag: `<_CorreEletronico>` — missing "o" in *Correo*, missing "c" in *Electrónico*
- Campaign tag: `<_UTMCampaing>` — missing "i" in *Campaign*

### Field rules
- Omit optional tags entirely when null. Only `_Comentarios` accepts empty (`<_Comentarios/>`).
- `_Apellido` is required — send `"N/A"` if unknown. `Lead Collector` splits names via LLM into `primer_nombre` / `apellidos` to avoid this fallback.
- `_TelefonoMovil` must include country code: `+502XXXXXXXX`.
- `_FechaCita` is ISO 8601 UTC: `2026-05-10T15:00:00.000Z`.
- `_UTMCampaing` format is strict: `"Cliente atendido desde chatbot a través de [medio]"`.

### Catalog values (most-used)
`_OrigenCliente` is **always** `100000001` (Chat).
`_UTMSource`: WhatsApp `100000004`, Instagram `100000012`, Facebook `100000005`.
`_MetodocontactoPref` uses simple ints `2–5` (NOT the CRM's `100000xxx` catalog).

Full catalogs in `docs/spectrum-soap-api.md`.

### Attribution fields
Both `DATA to CREATE` and `DATA to UPDATE` (in `AGENT PRINCIPAL.json`) must populate `atribucion_tag`, `atribucion_medio`, `atribucion_contacto`, `utm_source_crm` — the older `tag_medio` name is a renamed field, do not reintroduce it. On WhatsApp the auto-detected campaign is intentionally suppressed so the bot qualifies the lead manually.

### Phase 2 Lead Protection (Tribal pre-loaded leads)
**For leads where `fase_2: true`** (pre-loaded by Tribal campaigns with existing CRM records):

**Sync_CRM.json OMITS these attribution fields** (Tribal has them already):
- `_OrigenCliente` ← **Omitted entirely**
- `_UTMSource` ← **Omitted entirely**
- `_UTMCampaing` ← **Omitted entirely**
- `_MetodocontactoPref` ← **Omitted entirely**

**Sync_CRM.json SENDS these fields for Phase 2** (only if they have values):
- **Required (always):** `_Proyecto`, `_Nombre`, `_Apellido`, `_TelefonoMovil`, `_CorreEletronico`
- **Updates (if exist):** `_FechaCita`, `_TipoCita`
- **New data (if exist):** `_ResumenConversacion`, `_DudasCliente`
- **Optional (if exist):** `_CorreoSecundario`

`_NumeroHabitaciones`, `_EstadoCivil` y `_MotivoInteres` **NO se envían como campos SOAP para fase_2** — Tribal ya los tiene en CRM desde la pauta. Se incluyen en el texto de `_ResumenConversacion`.

**Prevent SOAP field duplication:**
- `_Comentarios` is sent ONLY by `Lead Collector.json` (at registration). `Sync_CRM.json` does NOT send comments (removed 2026-05-27).

Implementation: All Phase 2 checks use `{{ !$('Loop Over Users').item.json.fase_2 ? ... : '' }}` pattern in the XML body of `Sync_CRM.json` nodo `Body`.

---

## Remote workflow IDs (for n8n MCP)

When calling MCP tools against `agentsprod.redtec.ai`:

| Local file | n8n ID |
|---|---|
| `AGENT PRINCIPAL.json` | `iXaptKTUXaXrP7aF` |
| `Sync_CRM.json` | `TTVNRX38pPoPmK2X` |
| `Lead Collector.json` | `SHPFhvoal7k1Rqf9` |
| `KB SEARCH.json` | `D3LKuNi6CmMIdvzg` |
| `RSVP.json` | `TjFPzHs5aimxILH7` |
| `Send Media.json` | `NtTiyrNy2LHimE7u` |
| `Notifications Master.json` | `r1Jf5vwrkBrT4dEu` |
| `Vectorizar los KBs.json` | `LLiVnT0M6xvDKive` |
| `Analytics Centralizado.json` | _no registrado — verificar en server_ |
| `LEAD FASE 2.json` | _no registrado — scaffold_ |
| `WEB FORM.json` | _no registrado — verificar en server_ |

> The last three are recent additions; their remote IDs aren't confirmed. Check the server (and mirror into `spectrum-sim-mcp/config.py` `WORKFLOW_IDS`) before assuming they're deployed.

If you hit `ECONNREFUSED` connecting to MongoDB Atlas from a local script, override DNS in-process: `dns.setServers(['8.8.8.8', '8.8.4.4'])`.

---

## Commands

### End-to-end testing (hits production webhook)
```bash
cd "Agente Unificado"
python3 scripts/test_agent.py --list                            # show 10 scenarios
python3 scripts/test_agent.py --scenario saludo_inicial         # smoke test (~35s)
python3 scripts/test_agent.py --scenario happy_path_completo    # multi-turn conversation
python3 scripts/test_agent.py                                   # full suite (~10 min)
```
Each run uses a fresh `test_<hex>` user_id; data persists in MongoDB for auditing. The 35s per-message timeout accounts for the Redis 10s debounce wait.

### Workflow inspection (jq required)
```bash
./Agente\ Unificado/scripts/list-nodes.sh "Agente Unificado/AGENT PRINCIPAL.json"
./Agente\ Unificado/scripts/get-node.sh "Agente Unificado/AGENT PRINCIPAL.json" "PRINCIPAL"
./Agente\ Unificado/scripts/get-node-param.sh "Agente Unificado/AGENT PRINCIPAL.json" "PRINCIPAL" "systemMessage"
```
Useful params: `systemMessage`, `text`, `jsCode`, `assignments`, `conditions`.

### Local-vs-remote diff
`scripts/compare.py` diffs two workflow JSONs by node name and parameters — edit the hardcoded paths at the bottom before running.

### Simulator MCP server (`spectrum-sim-mcp/`)
Python MCP server that exposes 8 tools so any MCP-compatible AI (Claude Desktop/Code, Cursor, Gemini CLI) can talk to Sof-IA as if it were ManyChat AND inspect the resulting n8n executions + Mongo state.

```powershell
cd spectrum-sim-mcp
py -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env       # fill N8N_API_KEY, MONGO_URI, DEFAULT_PAGE_ID
spectrum-sim-mcp                  # arranca stdio (Ctrl+C para salir)
```

Tools: `send_message`, `new_test_user_id`, `list_workflows`, `list_executions`, `get_execution`, `tail_executions`, `read_user_state`, `reset_user`.

**Guardrails:**
- `reset_user` requires `MONGO_ALLOW_RESET=true` AND the `manychat_id` must start with `test_`. Both checks are mandatory — never weaken.
- Mongo tools auto-skip registration when `MONGO_URI` is empty.
- The `webhook.py` payload shape must match what `AGENT PRINCIPAL` reads (`body.id`, `body.page_id`, `body.custom_fields`, `body.last_input_text`, `body.whatsapp_phone`).

`WORKFLOW_IDS` in `config.py` mirrors the table above — keep them in sync if a workflow ID changes on the server.

---

## Editing workflow JSON — gotchas

- **Use `.first().json` not `.item.json`** in expressions. The codebase was normalized to `.first()` for robustness with multi-item outputs. Don't reintroduce `.item`.
- **Expression references must be reachable from every execution path.** n8n raises `"No path back to referenced node"` if a JSON expression references a node not on the current branch — restructure or duplicate the value into a node that IS reachable.
- **`$json` loses upstream context across Set/IF nodes.** If you need a field from an earlier node (e.g. `Parse response`), use the explicit form `$('Parse response').first().json.field` rather than `$json.field`.
- **`setCustomFieldByName` via httpRequest** is the standardized way to update ManyChat fields — don't use legacy ManyChat nodes.
- **Indentation: 2 spaces** in workflow JSONs (RSVP was reformatted to this standard 2026-05-19; new edits should follow it).

---

## Project state and skills

- `INDEX.md` (repo root) — **navigation map: read first to locate any file/node/module without scanning the repo.** Per-workflow node inventory auto-regenerates via `./scripts/build_index.sh` (run it after adding/removing nodes or workflows).
- `docs/estado_proyecto.md` is the living changelog — read it before making non-trivial changes; it explains *why* current quirks exist.
- `docs/spectrum-soap-api.md` — full SOAP catalogs.
- `docs/auditoria_workflows_2026-05-25.md`, `docs/comparativa_versiones.md`, `docs/estrategia_captacion_whatsapp.md`, `docs/reporte-fase2-mayo-2026.md` — audit, version comparison, WhatsApp capture strategy, and phase-2 May report.
- `Agente Unificado/.skills/spectrum-agente-unificado/SKILL.md` — domain context skill (read first for any task).
- `.skills_n8n/` and `Agente Unificado/.skills/` — n8n-specific skills (expression syntax, node configuration, validation, MCP tools, code nodes). Consult the matching skill when writing the corresponding kind of n8n content.
- `flujos de muestra Version anterior/` — legacy monolithic workflows kept for pattern reference, NOT in production.
