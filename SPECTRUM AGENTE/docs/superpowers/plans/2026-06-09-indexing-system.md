# Indexing System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganizar el sistema de contexto en 4 archivos (INDEX.md + 3 skills) para que Claude cargue solo lo relevante por tipo de tarea, reduciendo tokens sin perder calidad.

**Architecture:** Se agrega un § TASK LOOKUP al INDEX.md (siempre cargado) que indica qué skill invocar por tipo de tarea. Se crean 2 micro-skills nuevos (`spectrum-edit-debug`, `spectrum-business-rules`) y se reescribe el skill existente `spectrum-agente-unificado` eliminando contenido que migra a los nuevos skills.

**Tech Stack:** Markdown, bash scripts existentes en `workflows/scripts/`

---

## Archivos a crear / modificar

| Acción | Ruta |
|---|---|
| Modificar | `INDEX.md` — agregar § TASK LOOKUP después de § Mapa de carpetas |
| Crear | `workflows/.skills/spectrum-edit-debug/SKILL.md` |
| Crear | `workflows/.skills/spectrum-business-rules/SKILL.md` |
| Reescribir | `workflows/.skills/spectrum-agente-unificado/SKILL.md` |

---

## Task 1: § TASK LOOKUP en INDEX.md

**Files:**
- Modify: `INDEX.md` (insertar bloque después de la tabla `## 🗺️ Mapa de carpetas`, antes de `## ⚙️ Workflows`)

- [ ] **Step 1: Insertar la sección en INDEX.md**

Abrir `INDEX.md`. Después de la tabla del `## 🗺️ Mapa de carpetas` (línea que termina con `| \`flujos de muestra Version anterior/\` | ...`), insertar el siguiente bloque antes de la línea `---` que precede a `## ⚙️ Workflows`:

```markdown

---

## 🎯 Task Lookup — ¿qué skill cargar?

| Si vas a... | Skill a invocar |
|---|---|
| Editar un nodo (system prompt, JS, expresión) | `spectrum-edit-debug` |
| Depurar una ejecución fallida o comportamiento inesperado | `spectrum-edit-debug` |
| Agregar un nuevo tool, workflow o canal | `spectrum-agente-unificado` |
| Consultar reglas SOAP, CRM, catálogos, MongoDB o atribución | `spectrum-business-rules` |
```

- [ ] **Step 2: Verificar que la sección quedó en el lugar correcto**

```bash
grep -n "Task Lookup\|Mapa de carpetas\|Workflows" INDEX.md
```

Resultado esperado: líneas en orden — `Mapa de carpetas` → `Task Lookup` → `Workflows`.

- [ ] **Step 3: Commit**

```bash
git add INDEX.md
git commit -m "docs: agregar Task Lookup al INDEX para guiar carga de skills"
```

---

## Task 2: Crear `spectrum-edit-debug/SKILL.md`

**Files:**
- Create: `workflows/.skills/spectrum-edit-debug/SKILL.md`

- [ ] **Step 1: Crear el directorio**

```bash
mkdir -p "workflows/.skills/spectrum-edit-debug"
```

- [ ] **Step 2: Crear el archivo con contenido completo**

Crear `workflows/.skills/spectrum-edit-debug/SKILL.md` con el siguiente contenido exacto:

```markdown
# Skill: Spectrum — Edit & Debug

Úsalo cuando vayas a **editar nodos existentes** o **depurar ejecuciones**.
Para reglas de negocio / SOAP / catálogos → usa `spectrum-business-rules`.
Para agregar features nuevas → usa `spectrum-agente-unificado`.

---

## § 1 — Node Finder (comandos)

Todos los scripts están en `workflows/scripts/`. Ejecutar desde la raíz del repo.

```bash
# Listar todos los nodos de un workflow
./workflows/scripts/list-nodes.sh "workflows/<ARCHIVO>.json"

# Volcar un nodo completo por nombre
./workflows/scripts/get-node.sh "workflows/<ARCHIVO>.json" "<NOMBRE_NODO>"

# Ver parámetro específico de un nodo
./workflows/scripts/get-node-param.sh "workflows/<ARCHIVO>.json" "<NODO>" "<PARAM>"
# Params más usados: systemMessage · jsCode · text · assignments · conditions

# Buscar texto dentro de todos los workflows
grep -rn "<TEXTO>" workflows/*.json

# Buscar en un workflow específico
grep -n "<TEXTO>" "workflows/AGENT PRINCIPAL.json"
```

---

## § 2 — Edit Guide por workflow

| Workflow | Nodos más editados | Param clave |
|---|---|---|
| `AGENT PRINCIPAL.json` | `PRINCIPAL` | `systemMessage`, `text` |
| `AGENT PRINCIPAL.json` | `CONTEXT 1` | `assignments` |
| `AGENT PRINCIPAL.json` | `DATA to CREATE`, `DATA to UPDATE` | `assignments` |
| `Lead Collector.json` | `Lead Agent` | `systemMessage` |
| `Lead Collector.json` | `SET CONTEXT` | `assignments` |
| `RSVP.json` | `RSVP Agent` | `systemMessage` |
| `RSVP.json` | `CONTEXT` | `assignments` |
| `KB SEARCH.json` | `GENERAL AGENT` | `systemMessage` |
| `Sync_CRM.json` | `Body` | `jsCode` (XML SOAP) |
| `Sync_CRM.json` | `Information Extractor` | `systemMessage` |

**Comandos rápidos para los nodos más editados:**
```bash
# System prompt del orquestador
./workflows/scripts/get-node-param.sh "workflows/AGENT PRINCIPAL.json" "PRINCIPAL" "systemMessage"

# XML SOAP de Sync_CRM
./workflows/scripts/get-node-param.sh "workflows/Sync_CRM.json" "Body" "jsCode"

# Contexto del Lead Collector
./workflows/scripts/get-node-param.sh "workflows/Lead Collector.json" "SET CONTEXT" "assignments"
```

---

## § 3 — Expresiones críticas (propensas a bugs)

**`CONTEXT 1` — campo `proyecto`**
```js
{{ $('Proyecto').isExecuted ? $json.output.proyecto : '' }}
```
> `Proyecto` extractor solo corre en WhatsApp. En otros canales siempre devuelve `''`.

**`DATA to UPDATE` — campo `proyecto`**
```js
{{ $('CONTEXT 1').item.json.proyecto || $('Find User').item.json.proyecto }}
```
> Prioriza extractor fresco; fallback al valor ya guardado en MongoDB.

**`PRINCIPAL` — campo `text`**
```js
Proyecto activo en sesión: {{ $('CONTEXT 1').item.json.proyecto || $('User Data').item.json.proyecto || "Ninguno" }}
```
> `User Data` es snapshot PRE-Update. No refleja cambios de la ejecución actual.

**`Prepare Update` — campo `proyecto`**
```js
{{ $('Parse response').item.json.proyecto || $('User Data').item.json.proyecto || undefined }}
```
> `undefined` = no sobreescribir el campo en MongoDB.

**`Prepare Update` — campo `consulta_pendiente`**
```js
{{ $json.consulta_pendiente_limpiar ? null : ($json.consulta_pendiente_guardar || $('User Data').item.json.consulta_pendiente || undefined) }}
```

**`Hay Cambios?` — campo `FIELDS`**
```js
={{ Object.keys($json).filter(k => k !== '_id' && $json[k] !== null && $json[k] !== undefined).join(",") }}
```
> Filtra `null` y `undefined` para no sobreescribir campos en MongoDB con valores vacíos.

**Regla global:** Usar siempre `.first().json` — nunca `.item.json`. El repo fue normalizado a `.first()` por robustez con outputs multi-item.

---

## § 4 — Debug Recipes

```bash
# Comparar workflow local vs servidor n8n
node scripts/compare_remote.js

# Correr smoke test contra producción (~35s por mensaje — Redis debounce 10s)
python3 workflows/scripts/test_agent.py --scenario saludo_inicial

# Ver todas las ejecuciones recientes de un workflow (vía MCP n8n)
# → usar mcp__n8n-mcp-server__search_executions con workflowId

# Buscar campo específico en un workflow
grep -n '"campo_buscado"' "workflows/AGENT PRINCIPAL.json"

# Ver qué nodos tiene un workflow
./workflows/scripts/list-nodes.sh "workflows/RSVP.json"
```

**Traza de ejecución esperada (happy path completo):**
```
Webhook → PARSE BODY → ES ARCHIVO → text input → SAVE MESSAGE → Wait (10s)
→ GET MESSAGE → DELETE MESSAGES → Aggregate → Sort → Merge → INPUT FINAL
→ If NO WHATSAPP → [Proyecto extractor] → Lenguaje & Asesoria
→ Find User → If USER NOT EXIST → DATA to UPDATE → Update User
→ CONTEXT 1 → PROJECT LIST → JOINNING MESSAGE
→ MongoDB Chat Memory → PRINCIPAL → [tool calls si aplica]
→ Parse response → [If TIENE DATOS NUEVOS → Prepare Update → Hay Cambios? → Update User Lead]
→ Insert Analytics → RESPOND TO MANYCHAT
```

---

## § 5 — Failure Patterns

| Síntoma | Causa probable | Fix |
|---|---|---|
| `"No path back to referenced node"` | Expresión referencia nodo fuera de la rama actual | Usar nodo Set intermedio o `$('nodo').isExecuted` guard |
| Campo MongoDB sobreescrito con `null` | `Hay Cambios?` no filtró el campo | Verificar que `Prepare Update` devuelva `undefined` (no `null`) para campos sin valor |
| SOAP responde error sin código claro | Tag opcional enviado vacío en vez de omitido | Cambiar a ternario: `{{ val ? '<_Tag>'+val+'</_Tag>' : '' }}` |
| Bot responde antes del gate de datos | `systemMessage` de `PRINCIPAL` debilitado | Restaurar sección "🔴 VALIDACIÓN OBLIGATORIA PRIMERO" completa |
| Webhook timeout en test local | Redis debounce de 10s | Usar timeout de 35s en test runner (ya configurado en `test_agent.py`) |
| `.item.json` falla con múltiples items | `.item` no es robusto con multi-output | Reemplazar `.item.json` → `.first().json` en todas las expresiones |
| Ejecución n8n no actualiza MongoDB | `FIELDS` vacío en `Hay Cambios?` | Verificar que `Prepare Update` produce al menos un campo no-null |
```

- [ ] **Step 3: Verificar que el archivo existe y tiene contenido**

```bash
wc -l "workflows/.skills/spectrum-edit-debug/SKILL.md"
```

Resultado esperado: más de 80 líneas.

- [ ] **Step 4: Commit**

```bash
git add "workflows/.skills/spectrum-edit-debug/SKILL.md"
git commit -m "feat: agregar skill spectrum-edit-debug (node finder, expresiones, debug recipes)"
```

---

## Task 3: Crear `spectrum-business-rules/SKILL.md`

**Files:**
- Create: `workflows/.skills/spectrum-business-rules/SKILL.md`

- [ ] **Step 1: Crear el directorio**

```bash
mkdir -p "workflows/.skills/spectrum-business-rules"
```

- [ ] **Step 2: Crear el archivo con contenido completo**

Crear `workflows/.skills/spectrum-business-rules/SKILL.md` con el siguiente contenido exacto:

```markdown
# Skill: Spectrum — Business Rules

Úsalo cuando necesites consultar **reglas SOAP/CRM, catálogos, MongoDB o lógica de atribución**.
Para editar nodos o depurar → usa `spectrum-edit-debug`.
Para agregar features → usa `spectrum-agente-unificado`.

---

## § 1 — Gate de validación (regla crítica)

`AGENT PRINCIPAL` **nunca** llama `kb_search`, `rsvp` ni `send_media` hasta que el lead haya compartido **nombre + email + teléfono**.

- Único tool invocable antes del gate: `lead_collector`
- Regla vive en el `systemMessage` del nodo `PRINCIPAL` bajo la sección "🔴 VALIDACIÓN OBLIGATORIA PRIMERO"
- **No debilitar esta regla** — fue agregada para corregir incidente 2026-05-22 donde el bot respondió preguntas de proyecto a un lead anónimo

---

## § 2 — SOAP Quick-Reference

```
Endpoint: https://crm.spectrum.com.gt:8055/Spectrum_WS_GeneracionLead/Service.asmx
SOAPAction: http://tempuri.org/CreacionClientePotencialBot
Content-Type: text/xml; charset=utf-8
```

### Typos obligatorios — NO corregir, son los tags reales del CRM

| Tag | Typo | Descripción |
|---|---|---|
| `<_CorreEletronico>` | Falta "o" en *Correo*, falta "c" en *Electrónico* | Email principal |
| `<_UTMCampaing>` | Falta "i" en *Campaign* | Campaña UTM |

### Campos requeridos (siempre presentes)
`_Proyecto` · `_Nombre` · `_Apellido` (usar `"N/A"` si desconocido) · `_TelefonoMovil` (con código país: `+502XXXXXXXX`) · `_CorreEletronico`

### Campos opcionales — omitir si null
Excepción: `_Comentarios` acepta vacío `<_Comentarios/>`.

Patrón para tag opcional:
```js
{{ $json.valor ? '<_Tag>' + $json.valor + '</_Tag>' : '' }}
```

### Formatos especiales
- `_FechaCita`: ISO 8601 UTC → `2026-05-10T15:00:00.000Z`
- `_UTMCampaing`: texto fijo → `"Cliente atendido desde chatbot a través de [medio]"`

---

## § 3 — Catálogos CRM

### Origen y atención
| Campo | Valor | Notas |
|---|---|---|
| `_OrigenCliente` | `100000001` | Chat — siempre este valor |
| `_AtendidoPorIA` | `1` | Siempre, fase_1 y fase_2 |

### Canal (`_UTMSource`)
| Canal | Valor |
|---|---|
| WhatsApp | `100000004` |
| Facebook | `100000005` |
| Instagram | `100000012` |

### Método de contacto (`_MetodocontactoPref`)
Usar enteros simples `2–5` — **NO** usar formato `100000xxx`.

### Estado civil (`_EstadoCivil`)
| Estado | Valor |
|---|---|
| Soltero | `100000000` |
| Casado | `100000001` |
| Divorciado | `100000002` |
| Unido / Unión Libre | `100000003` |

### Habitaciones (`_NumeroHabitaciones`)
| Hab. | Valor |
|---|---|
| 1 | `100000000` |
| 2 | `100000001` |
| 3 | `100000002` |

### Motivo de interés (`_MotivoInteres`)
| Motivo | Valor |
|---|---|
| Inversión | `100000001` |
| Vivir | `100000003` |
| Información General | `100000000` |

### Proyectos (`_Proyecto`)
| Código interno | Código CRM | Proyecto |
|---|---|---|
| `pvv` | `PVV` | Parque Vista Verde (entrega Nov 2026) |
| `pm` | `PMAR` | Parque Mariscal |
| `pp` | `PPO` | Parque Portales (entrega Dic 2026) |
| `polanco` | `PPOL` | Parque Polanco |
| `psb` | `PSB` | Parque Sotobosque |

---

## § 4 — Atribución: fase_1 vs fase_2

### fase_1 (leads orgánicos) — enviar todos los campos de atribución
```
_OrigenCliente · _UTMSource · _UTMCampaing · _MetodocontactoPref
atribucion_tag · atribucion_medio · atribucion_contacto · utm_source_crm
```
> El campo se llama `atribucion_tag` — el nombre anterior `tag_medio` fue renombrado. No reintroducir.

### fase_2 (leads Tribal pre-cargados, `fase_2: true`) — omitir atribución
```
_OrigenCliente ← OMITIR
_UTMSource     ← OMITIR
_UTMCampaing   ← OMITIR
_MetodocontactoPref ← OMITIR
```
Tribal ya tiene estos campos en CRM desde la pauta.

**Campos que sí se envían en fase_2:** `_Proyecto`, `_Nombre`, `_Apellido`, `_TelefonoMovil`, `_CorreEletronico`, `_FechaCita`/`_TipoCita` (si existen), `_ResumenConversacion`, `_DudasCliente`, `_CorreoSecundario` (si existe).

**Patrón en `Sync_CRM.json` nodo `Body`:**
```js
{{ !$('Loop Over Users').item.json.fase_2 ? '<_Campo>valor</_Campo>' : '' }}
```

### Regla de `_Comentarios`
Solo lo envía `Lead Collector.json` al registrar el lead. `Sync_CRM.json` **no** lo envía (eliminado 2026-05-27 para evitar duplicación).

### WhatsApp — supresión de campaña
En WhatsApp la autodetección de campaña UTM se suprime intencionalmente para que el bot califique el lead manualmente.

---

## § 5 — MongoDB

### Colecciones y keys de query

| Colección | Key de query | Propósito |
|---|---|---|
| `users` | `manychat_id` + `page_id` | Perfil del lead (un doc por manychat_id+page_id) |
| `appointments` | `manychat_id` + `proyecto` | Citas — un lead puede tener varias (uno por proyecto) |
| `chat_histories` | `sessionId = manychat_id` | Historial del orquestador |
| `chat_histories_lead` | `sessionId = manychat_id` | Historial de Lead Collector |
| `chat_histories_rsvp` | `sessionId = manychat_id` | Historial de RSVP |
| `manychat_settings` | `page_id` | Config por página: `api_key`, `proyecto` |
| `documents` | `proyecto` (UPPERCASE) | Chunks vectoriales. Índice: `spectrum_vector_index` |
| `quality_logs` | — | Auditoría post-sync |
| `analytics_logs` | `sessionId` | Telemetría de latencia y tool calls |

### Vector search
- Colección: `documents`
- Índice: `spectrum_vector_index`
- **Filtro obligatorio:** campo `proyecto` en UPPERCASE (`PVV`, `PMAR`, `PPO`, `PPOL`, `PSB`)
- Re-vectorizar después de editar un KB: correr workflow `LLiVnT0M6xvDKive` en n8n

### Resolución de DNS en scripts locales
Si ECONNREFUSED al conectar desde script local:
```js
import dns from 'dns'
dns.setServers(['8.8.8.8', '8.8.4.4'])
```

---

## § 6 — Channel Routing

| Canal | Cómo se resuelve `proyecto` |
|---|---|
| Instagram / Messenger | `page_id` → lookup en `manychat_settings` → proyecto pre-asignado |
| WhatsApp (orgánico) | Regla de Oro — menú interactivo para que el lead elija proyecto |
| WhatsApp (fase_2) | `custom_fields.proyecto_interes` pre-seteado por Tribal → omite Regla de Oro |

**Implementación:** nodo `CONTEXT 1` en `AGENT PRINCIPAL.json`.

**Resolución de `proyecto` en `CONTEXT 1`:**
```js
{{ $('Proyecto').isExecuted ? $json.output.proyecto : '' }}
```
`Proyecto` (information extractor) solo corre en WhatsApp. En otros canales el proyecto viene de `Find User` (MongoDB).
```

- [ ] **Step 3: Verificar que el archivo existe y tiene contenido**

```bash
wc -l "workflows/.skills/spectrum-business-rules/SKILL.md"
```

Resultado esperado: más de 100 líneas.

- [ ] **Step 4: Commit**

```bash
git add "workflows/.skills/spectrum-business-rules/SKILL.md"
git commit -m "feat: agregar skill spectrum-business-rules (SOAP, catálogos, MongoDB, atribución)"
```

---

## Task 4: Reescribir `spectrum-agente-unificado/SKILL.md`

**Files:**
- Rewrite: `workflows/.skills/spectrum-agente-unificado/SKILL.md`

El archivo actual mezcla contenido que ahora vive en los nuevos skills. Se reescribe para enfocarse solo en arquitectura y extension points.

- [ ] **Step 1: Reemplazar el contenido completo del archivo**

Reemplazar TODO el contenido de `workflows/.skills/spectrum-agente-unificado/SKILL.md` con:

```markdown
# Skill: Spectrum Agente Unificado — Arquitectura y Extension Points

Úsalo cuando vayas a **agregar un nuevo tool, workflow, canal o proyecto**.
Para editar nodos → usa `spectrum-edit-debug`.
Para reglas SOAP/CRM/catálogos → usa `spectrum-business-rules`.

---

## § 1 — Arquitectura del sistema

```
ManyChat (6 páginas)
    │
    ▼ webhook
AGENT PRINCIPAL (orquestador, gpt-5-mini)
    │  Redis debounce 10s (agrupa mensajes rápidos)
    │  MongoDB: users, chat_histories
    │
    ├─ lead_collector ──→ Lead Collector.json   (captura name/email/phone → SOAP CRM)
    ├─ kb_search      ──→ KB SEARCH.json        (RAG Atlas Vector, filtro por proyecto)
    ├─ rsvp           ──→ RSVP.json             (citas → appointments + Notifications)
    └─ send_media     ──→ Send Media.json        (brochures/renders vía ManyChat API)

Sync_CRM.json         (scheduled ~15min, SOAP Dynamics 365, protección fase_2)
Notifications Master  (emails HTML: nuevo lead, precios, cita, escalación)
Analytics Centralizado (scheduled diario, métricas por usuario → MongoDB)
```

**Regla de oro del orquestador:** ningún tool excepto `lead_collector` es invocable antes de que el lead tenga nombre + email + teléfono. Gate en `systemMessage` del nodo `PRINCIPAL`.

### IDs n8n (producción en `agentsprod.redtec.ai`)

| Workflow | ID n8n |
|---|---|
| `AGENT PRINCIPAL.json` | `iXaptKTUXaXrP7aF` |
| `Lead Collector.json` | `SHPFhvoal7k1Rqf9` |
| `KB SEARCH.json` | `D3LKuNi6CmMIdvzg` |
| `RSVP.json` | `TjFPzHs5aimxILH7` |
| `Send Media.json` | `NtTiyrNy2LHimE7u` |
| `Sync_CRM.json` | `TTVNRX38pPoPmK2X` |
| `Notifications Master.json` | `r1Jf5vwrkBrT4dEu` |
| `Vectorizar los KBs.json` | `LLiVnT0M6xvDKive` |
| `Analytics Centralizado.json` | `0QfOxWdE9m07laqd` |

---

## § 2 — Agregar un nuevo tool al orquestador

1. **Crear el sub-workflow** en n8n. Debe aceptar un `START` webhook y devolver JSON con al menos:
   ```json
   { "response": "texto para el lead", "datos_completos": 0 }
   ```
2. **En `AGENT PRINCIPAL.json` → nodo `PRINCIPAL`:** agregar descripción del tool en `systemMessage` (sección de tools disponibles).
3. **Agregar nodo `Execute Workflow`** conectado al output de `PRINCIPAL`, configurado con el ID del nuevo workflow.
4. **En `Parse response`:** verificar que el parser maneje el output del nuevo tool (extender si devuelve campos extra).
5. **Registrar** el ID n8n en `CLAUDE.md` (tabla "Remote workflow IDs") y en `INDEX.md` (tabla `## ⚙️ Workflows`).

---

## § 3 — Agregar un nuevo canal / página de ManyChat

1. Insertar documento en colección `manychat_settings` de MongoDB:
   ```json
   { "page_id": "<ID_DE_PAGINA>", "api_key": "<TOKEN_MANYCHAT>", "proyecto": "CODIGO" }
   ```
2. Para Instagram/Messenger: el proyecto queda fijo por `page_id`. No se necesita Regla de Oro.
3. Para WhatsApp orgánico: verificar que el menú interactivo de la Regla de Oro esté activo.
4. Para WhatsApp fase_2 (Tribal): la campaña debe setear `custom_fields.proyecto_interes` antes del primer mensaje.

---

## § 4 — Agregar un nuevo proyecto inmobiliario

1. Crear `KBs/KB_<CODIGO>.json` con los chunks del proyecto. El campo `proyecto` en cada chunk debe ir en UPPERCASE.
2. Insertar entradas en `manychat_settings` para las páginas del nuevo proyecto.
3. Correr el workflow `Vectorizar los KBs` (`LLiVnT0M6xvDKive`) en n8n para indexar.
4. Actualizar `spectrum-business-rules` skill: agregar fila en tabla de proyectos (§ 3).
5. Actualizar `INDEX.md`: agregar fila en tabla `## 🧠 KBs`.

---

## § 5 — Tool output format (contrato entre sub-workflows y PRINCIPAL)

Todo sub-workflow invocado como tool debe devolver un objeto JSON que incluya:

```json
{
  "response": "string — texto que se enviará al lead",
  "datos_completos": 0,
  "proyecto": "PMAR"
}
```

- `response`: obligatorio. Es lo que `RESPOND TO MANYCHAT` envía.
- `datos_completos`: `1` cuando el lead ya tiene nombre+email+phone (usado por Lead Collector).
- `proyecto`: opcional. Si el tool detecta o confirma el proyecto activo, incluirlo para que `Parse response` lo persista.

Agregar campos extra es seguro. Cambiar `response` o `datos_completos` rompe `Parse response` en PRINCIPAL.

---

## § 6 — Patrones de integración n8n

**Execute Workflow (llamada a tool):**
- El nodo debe tener `Wait for sub-workflow completion: true`.
- Pasar `manychat_id`, `proyecto`, `query` como mínimo.
- El output del nodo llega como `.first().json` en el siguiente nodo.

**Expresiones: siempre `.first().json`, nunca `.item.json`**

**MongoDB update con campos dinámicos:**
El patrón `Hay Cambios?` + `FIELDS` genera la lista de campos a actualizar dinámicamente, omitiendo nulls. Reusar este patrón para nuevos nodos de actualización.

**Nodo `Code` en JavaScript:**
- Acceder al input: `const item = $input.first().json`
- Devolver: `return [{ json: { campo: valor } }]`
- Para múltiples items: `return items.map(i => ({ json: { ... } }))`
```

- [ ] **Step 2: Verificar que el archivo fue reescrito**

```bash
wc -l "workflows/.skills/spectrum-agente-unificado/SKILL.md"
grep -n "§" "workflows/.skills/spectrum-agente-unificado/SKILL.md"
```

Resultado esperado: más de 80 líneas; grep muestra las 6 secciones (§ 1 a § 6).

- [ ] **Step 3: Verificar que NO quedan referencias a `Agente Unificado/`**

```bash
grep -n "Agente Unificado" "workflows/.skills/spectrum-agente-unificado/SKILL.md"
```

Resultado esperado: 0 resultados.

- [ ] **Step 4: Commit**

```bash
git add "workflows/.skills/spectrum-agente-unificado/SKILL.md"
git commit -m "refactor: reescribir spectrum-agente-unificado — arquitectura y extension points"
```

---

## Task 5: Verificación final

- [ ] **Step 1: Verificar que los 4 cambios están en git**

```bash
git log --oneline -5
```

Resultado esperado: 4 commits recientes con los mensajes de las tareas anteriores.

- [ ] **Step 2: Verificar que INDEX.md tiene la sección Task Lookup**

```bash
grep -A 8 "Task Lookup" INDEX.md
```

Resultado esperado: tabla con 4 filas de skills.

- [ ] **Step 3: Verificar que los 3 skills existen**

```bash
ls workflows/.skills/
```

Resultado esperado: `n8n-*` existentes + `spectrum-agente-unificado` + `spectrum-edit-debug` + `spectrum-business-rules`.

- [ ] **Step 4: Smoke test — buscar el skill de edición**

```bash
grep -n "Node Finder\|Edit Guide\|Failure Patterns" "workflows/.skills/spectrum-edit-debug/SKILL.md"
```

Resultado esperado: las 3 secciones aparecen.

- [ ] **Step 5: Smoke test — buscar el skill de reglas**

```bash
grep -n "Gate de validación\|Catálogos\|fase_2\|MongoDB" "workflows/.skills/spectrum-business-rules/SKILL.md"
```

Resultado esperado: las 4 secciones aparecen.
