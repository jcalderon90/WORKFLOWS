# Diseño: Sistema de Indexado y Skills por Capas
**Fecha:** 2026-06-09  
**Estado:** Aprobado — pendiente implementación

---

## Objetivo

Reorganizar el sistema de contexto del proyecto SPECTRUM AGENTE para que Claude cargue solo el contexto relevante por tipo de tarea, reduciendo tokens por sesión sin perder calidad.

---

## Problema actual

| Síntoma | Causa raíz |
|---|---|
| Contexto innecesario cargado en cada sesión | `spectrum-agente-unificado/SKILL.md` mezcla reglas SOAP, nodos, expresiones, arquitectura |
| Skill principal desactualizado | Rutas `Agente Unificado/` (ahora `workflows/`), líneas de nodo stale |
| No hay señal de qué skill invocar | Claude debe adivinar o cargar todo |
| Duplicación INDEX.md ↔ SKILL.md | El inventario de nodos vive en ambos |

---

## Solución: Arquitectura por capas

```
Capa 0 — Siempre cargado
  CLAUDE.md            Reglas críticas de negocio (intocable)
  INDEX.md             Mapa de navegación + § TASK LOOKUP (nuevo)

Capa 1 — On-demand por tipo de tarea
  spectrum-edit-debug          Editar nodos + debug
  spectrum-business-rules      SOAP, catálogos, MongoDB, atribución
  spectrum-agente-unificado    Arquitectura + extension points (reducido)

Capa 2 — Especializada (sin cambios)
  n8n-expression-syntax
  n8n-code-javascript
  n8n-node-configuration
  n8n-workflow-patterns
  n8n-validation-expert
  n8n-mcp-tools-expert
```

---

## Cambio 1: INDEX.md — agregar § TASK LOOKUP

Insertar después de `## 🗺️ Mapa de carpetas`, antes de `## ⚙️ Workflows`:

```markdown
## 🎯 Task Lookup — ¿qué skill cargar?

| Si vas a... | Skill a invocar |
|---|---|
| Editar un nodo (system prompt, JS, expresión) | `spectrum-edit-debug` |
| Depurar una ejecución fallida o comportamiento inesperado | `spectrum-edit-debug` |
| Agregar un nuevo tool, workflow o canal | `spectrum-agente-unificado` |
| Consultar reglas SOAP, CRM, catálogos, MongoDB o atribución | `spectrum-business-rules` |
```

Costo: ~8 líneas sobre el INDEX ya cargado.

---

## Cambio 2: nuevo `spectrum-edit-debug/SKILL.md`

**Ruta:** `workflows/.skills/spectrum-edit-debug/SKILL.md`

### § 1 — Node Finder (comandos)
```bash
# Abrir nodo por nombre
./workflows/scripts/get-node.sh "workflows/<ARCHIVO>.json" "<NOMBRE_NODO>"

# Ver parámetro específico (systemMessage, jsCode, text, assignments)
./workflows/scripts/get-node-param.sh "workflows/<ARCHIVO>.json" "<NODO>" "<PARAM>"

# Buscar texto dentro de todos los workflows
grep -r "<TEXTO>" workflows/*.json

# Listar todos los nodos de un workflow
./workflows/scripts/list-nodes.sh "workflows/<ARCHIVO>.json"
```

### § 2 — Edit Guide por workflow

| Workflow | Nodos más editados | Param clave |
|---|---|---|
| `AGENT PRINCIPAL.json` | `PRINCIPAL` | `systemMessage`, `text` |
| `AGENT PRINCIPAL.json` | `CONTEXT 1` | `assignments` |
| `AGENT PRINCIPAL.json` | `DATA to CREATE`, `DATA to UPDATE` | `assignments` |
| `AGENT PRINCIPAL.json` | `XML BODY` (en Sync) | `jsCode` |
| `Lead Collector.json` | `Lead Agent` | `systemMessage` |
| `Lead Collector.json` | `SET CONTEXT` | `assignments` |
| `RSVP.json` | `RSVP Agent` | `systemMessage` |
| `RSVP.json` | `CONTEXT` | `assignments` |
| `KB SEARCH.json` | `GENERAL AGENT` | `systemMessage` |
| `Sync_CRM.json` | `Body` (XML SOAP) | `jsCode` |
| `Sync_CRM.json` | `Information Extractor` | `systemMessage` |

### § 3 — Expresiones críticas (propensas a bugs)

**`CONTEXT 1` — campo `proyecto`**
```js
{{ $('Proyecto').isExecuted ? $json.output.proyecto : '' }}
// Proyecto extractor solo corre en WhatsApp. En otros canales siempre ''
```

**`DATA to UPDATE` — campo `proyecto`**
```js
{{ $('CONTEXT 1').item.json.proyecto || $('Find User').item.json.proyecto }}
// Prioriza extractor fresco; fallback al valor en MongoDB
```

**`PRINCIPAL` — campo `text`**
```js
Proyecto activo: {{ $('CONTEXT 1').item.json.proyecto || $('User Data').item.json.proyecto || "Ninguno" }}
// User Data es snapshot PRE-Update — no refleja la ejecución actual
```

**`Prepare Update` — campo `proyecto`**
```js
{{ $('Parse response').item.json.proyecto || $('User Data').item.json.proyecto || undefined }}
// undefined = no sobreescribir campo en MongoDB
```

**`Prepare Update` — campo `consulta_pendiente`**
```js
{{ $json.consulta_pendiente_limpiar ? null : ($json.consulta_pendiente_guardar || $('User Data').item.json.consulta_pendiente || undefined) }}
```

**`Hay Cambios?` — campo `FIELDS`**
```js
={{ Object.keys($json).filter(k => k !== '_id' && $json[k] !== null && $json[k] !== undefined).join(",") }}
// Filtra null/undefined para no sobreescribir con valores vacíos
```

### § 4 — Debug Recipes

```bash
# Ver últimas N ejecuciones de un workflow (vía MCP n8n o API)
# Buscar campo específico en output de un nodo
grep -n '"campo"' "workflows/AGENT PRINCIPAL.json"

# Comparar local vs servidor
node scripts/compare_remote.js

# Ver nodo PRINCIPAL completo (system prompt)
./workflows/scripts/get-node-param.sh "workflows/AGENT PRINCIPAL.json" "PRINCIPAL" "systemMessage"

# Ver código JS de un Code node
./workflows/scripts/get-node-param.sh "workflows/Sync_CRM.json" "Body" "jsCode"
```

**Traza de ejecución esperada (happy path):**
```
Webhook → PARSE BODY → ES ARCHIVO → text input → SAVE MESSAGE → Wait →
GET MESSAGE → DELETE MESSAGES → Aggregate → Sort → Merge → INPUT FINAL →
If NO WHATSAPP → [Proyecto] → Lenguaje & Asesoria → Find User →
If USER NOT EXIST → DATA to UPDATE → Update User → CONTEXT 1 →
PROJECT LIST → JOINNING MESSAGE → MongoDB Chat Memory → PRINCIPAL →
[tool calls] → Parse response → [If TIENE DATOS NUEVOS] → 
Insert Analytics → RESPOND TO MANYCHAT
```

### § 5 — Failure Patterns comunes

| Síntoma | Causa probable | Fix |
|---|---|---|
| `"No path back to referenced node"` | Expresión referencia nodo no alcanzable desde esa rama | Usar nodo intermedio Set o duplicar valor |
| Campo en MongoDB sobreescrito con `null` | `Hay Cambios?` no filtró el campo | Verificar que `Prepare Update` devuelva `undefined` en vez de `null` |
| SOAP responde error sin código claro | Typo en tag XML o tag vacío enviado cuando debería omitirse | Verificar que campos opcionales usen ternario `{{ val ? '<tag>'+val+'</tag>' : '' }}` |
| Bot responde antes de tener datos del lead | Gate de validación eludido | Verificar `systemMessage` de `PRINCIPAL` — sección "🔴 VALIDACIÓN OBLIGATORIA" intacta |
| Webhook timeout en tests | Redis debounce de 10s | Usar timeout de 35s en test runner |
| `.item.json` falla con múltiples items | Usar `.first().json` | Reemplazar `.item` → `.first()` |

---

## Cambio 3: nuevo `spectrum-business-rules/SKILL.md`

**Ruta:** `workflows/.skills/spectrum-business-rules/SKILL.md`

### § 1 — Gate de validación
- `AGENT PRINCIPAL` nunca llama `kb_search`, `rsvp` ni `send_media` hasta tener **nombre + email + teléfono**.
- Único tool pre-gate: `lead_collector`.
- Regla vive en `systemMessage` del nodo `PRINCIPAL` bajo "🔴 VALIDACIÓN OBLIGATORIA PRIMERO". No debilitar.

### § 2 — SOAP Quick-Reference
```
Endpoint: https://crm.spectrum.com.gt:8055/Spectrum_WS_GeneracionLead/Service.asmx
SOAPAction: http://tempuri.org/CreacionClientePotencialBot
Content-Type: text/xml; charset=utf-8
```

**Typos obligatorios (NO corregir):**
- `<_CorreEletronico>` — falta "o" en Correo, falta "c" en Electrónico
- `<_UTMCampaing>` — falta "i" en Campaign

**Campos requeridos siempre:** `_Proyecto`, `_Nombre`, `_Apellido` (usar "N/A" si desconocido), `_TelefonoMovil` (con código país `+502XXXXXXXX`), `_CorreEletronico`

**Campos opcionales — omitir si null** (excepción: `_Comentarios` acepta vacío `<_Comentarios/>`)

**Patrón de tag opcional:**
```js
{{ $json.valor ? '<_Tag>' + $json.valor + '</_Tag>' : '' }}
```

### § 3 — Catálogos CRM

| Campo | Valor | Descripción |
|---|---|---|
| `_OrigenCliente` | `100000001` | Chat (siempre) |
| `_AtendidoPorIA` | `1` | Siempre, fase_1 y fase_2 |
| `_UTMSource` | `100000004` | WhatsApp |
| `_UTMSource` | `100000005` | Facebook |
| `_UTMSource` | `100000012` | Instagram |
| `_MetodocontactoPref` | `2–5` (int simple) | NO usar `100000xxx` |
| `_EstadoCivil` | `100000000–100000003` | Soltero/Casado/Divorciado/Unido |
| `_MotivoInteres` | `100000001` | Inversión |
| `_MotivoInteres` | `100000003` | Vivir |
| `_MotivoInteres` | `100000000` | Información General |
| `_NumeroHabitaciones` | `100000000–100000002` | 1/2/3 hab |

`_FechaCita`: ISO 8601 UTC — `2026-05-10T15:00:00.000Z`  
`_UTMCampaing`: `"Cliente atendido desde chatbot a través de [medio]"`

### § 4 — Atribución fase_1 vs fase_2

**fase_1** (leads orgánicos): enviar todos los campos de atribución:
`_OrigenCliente`, `_UTMSource`, `_UTMCampaing`, `_MetodocontactoPref`, `atribucion_tag`, `atribucion_medio`, `atribucion_contacto`, `utm_source_crm`

**fase_2** (leads Tribal pre-cargados, `fase_2: true`): **omitir** `_OrigenCliente`, `_UTMSource`, `_UTMCampaing`, `_MetodocontactoPref`. Tribal ya los tiene en CRM.

**Patrón en `Sync_CRM.json` nodo `Body`:**
```js
{{ !$('Loop Over Users').item.json.fase_2 ? '<_Campo>valor</_Campo>' : '' }}
```

**`_Comentarios`:** solo lo envía `Lead Collector.json` al registrar. `Sync_CRM.json` NO lo envía (eliminado 2026-05-27).

### § 5 — MongoDB

| Colección | Key de query | Propósito |
|---|---|---|
| `users` | `manychat_id` + `page_id` | Perfil del lead |
| `appointments` | `manychat_id` + `proyecto` | Citas (un lead puede tener varias) |
| `chat_histories` | `sessionId = manychat_id` | Historial orquestador |
| `chat_histories_lead` | `sessionId = manychat_id` | Historial Lead Collector |
| `chat_histories_rsvp` | `sessionId = manychat_id` | Historial RSVP |
| `manychat_settings` | `page_id` | Config por página: `api_key`, `proyecto` |
| `documents` | `proyecto` (UPPERCASE) | Chunks vectoriales. Índice: `spectrum_vector_index` |
| `quality_logs` | — | Auditoría post-sync |
| `analytics_logs` | `sessionId` | Telemetría de latencia |

### § 6 — Channel Routing

**IG / Messenger:** `page_id` → `proyecto` (pre-asignado en `manychat_settings`)  
**WhatsApp sin fase_2:** Regla de Oro — menú interactivo para elegir proyecto  
**WhatsApp con `custom_fields.proyecto_interes`** (fase_2): omite Regla de Oro, usa proyecto pre-seteado  
**Resolución en:** nodo `CONTEXT 1` de `AGENT PRINCIPAL.json`

---

## Cambio 4: reducir `spectrum-agente-unificado/SKILL.md`

Reescribir con solo:

### § 1 — Arquitectura
- Diagrama de flujo del orquestador (texto)
- Rutas corregidas a `workflows/`
- Tabla de IDs n8n (misma que CLAUDE.md, para referencia rápida)

### § 2 — Extension Points

**Agregar nuevo tool al orquestador:**
1. Crear nuevo workflow sub-agente
2. En `AGENT PRINCIPAL.json` → nodo `PRINCIPAL`: agregar tool en `systemMessage`
3. Agregar nodo `Execute Workflow` conectado a `PRINCIPAL`
4. Parsear output en `Parse response`
5. Registrar ID n8n en `CLAUDE.md` + `INDEX.md`

**Agregar nuevo canal/página:**
1. Crear entrada en `manychat_settings` MongoDB: `{page_id, api_key, proyecto}`
2. Para WhatsApp: verificar que `custom_fields.proyecto_interes` se setee en la campaña si es fase_2

**Agregar nuevo proyecto:**
1. Crear `KBs/KB_CODIGO.json`
2. Agregar entrada en `manychat_settings`
3. Correr `Vectorizar los KBs` (`LLiVnT0M6xvDKive`)
4. Actualizar catálogo en `spectrum-business-rules` skill

### § 3 — Tool Output Format

Todos los tools sub-agente deben devolver JSON con al menos:
```json
{ "response": "...", "datos_completos": 0|1 }
```
`Parse response` en PRINCIPAL espera este shape. Agregar campos extra es seguro; cambiar los existentes rompe el parseo.

---

## Qué NO cambia

- `CLAUDE.md` — intocable (reglas siempre activas)
- `INDEX.md` — solo recibe la sección § TASK LOOKUP
- Skills `n8n-*` — sin modificaciones
- Skills MongoDB — sin modificaciones

---

## Archivos a crear/modificar

| Acción | Archivo |
|---|---|
| Modificar (agregar § TASK LOOKUP) | `INDEX.md` |
| Crear | `workflows/.skills/spectrum-edit-debug/SKILL.md` |
| Crear | `workflows/.skills/spectrum-business-rules/SKILL.md` |
| Reescribir | `workflows/.skills/spectrum-agente-unificado/SKILL.md` |
