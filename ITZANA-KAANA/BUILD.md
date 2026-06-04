# Itz'ana — Guía de construcción del Agente de IA

**Bot:** Concierge pre-reserva en ManyChat (Instagram + Facebook + WhatsApp)  
**Cuenta ManyChat:** `fb807994325905660` (una sola cuenta, una sola propiedad por ahora)  
**Arquitectura base:** SPECTRUM AGENTE (`n8n-workflows/SPECTRUM AGENTE/Agente Unificado/`)

---

## Estado general — actualizado 2026-06-04 (sesión tarde)

| # | Componente | Tipo | Estado |
| :-- | :-- | :-- | :-- |
| 1 | `KBs/KB_ITZANA.json` | Archivo de contenido | ✅ Listo — **36 chunks** (actualizado con horarios, WiFi, políticas, mascotas, equipos) |
| 2 | MongoDB Atlas (DB + índice vectorial + credencial) | Infraestructura | ✅ Listo — credencial `HOTELS` (`Msw0gTK8f8b192VX`) |
| 3 | `workflows/Itzana_Vectorizar_KB.json` | Workflow n8n | ✅ Listo — **36 docs** re-vectorizados en colección `documents` |
| 4 | `workflows/Itzana_KB_Search.json` | Workflow n8n (herramienta RAG) | ✅ Importado en n8n — ID: `rofQe6ZGW3OpFqcb` |
| 5 | `workflows/Itzana_Notifications.json` | Workflow n8n (herramienta email) | ✅ Listo — Gmail (Soporte Garoo), HTML dinámico, 5 categorías. Emails de prueba: jorge.calderon@garooinc.com |
| 6 | `workflows/PRINCIPAL.json` | Workflow n8n (orquestador) | ✅ Completo — JSON.stringify fix, tool descriptions en español, inputs completos a Notifications |
| 7 | Pruebas end-to-end | QA | ✅ Pasadas — flujo ManyChat → n8n → respuesta funcional |

---

## RETOMAR AQUI — Siguiente fase

**Estado al 2026-06-04:** Sistema de Fase 1 (pre-booking / Kaan) **listo para producción** en cuanto lleguen los emails del hotel.

### Pendientes de contenido (bloqueados por hotel)

| # | Pendiente | Prioridad |
| :-- | :-- | :-- |
| P2 | Email de Mr. Diego (bodas/eventos) → actualizar `sendTo` en nodo "Email Bodas/Eventos" de Notifications | 🔴 Alta (pre-prod) |
| P3 | Email de RRHH (empleo) → actualizar `sendTo` en nodo "Email Empleo" de Notifications | 🟠 Media (pre-prod) |

### Próxima fase — E-Concierge in-stay
Ver spec en `docs/E-Concierge Itzana.md`. Agente separado para huéspedes ya hospedados:
- Crea tareas operativas (housekeeping, mantenimiento, F&B, recepción)
- Routing por departamento
- Estados: NEW → IN PROGRESS → ON THE WAY → COMPLETED
- Notificaciones al equipo del hotel y feedback loop al huésped

**Esto NO está construido aún.** Es la siguiente iteración después de estabilizar Kaan en producción.

---

## Arquitectura de workflows en n8n (IDs reales)

| Workflow | ID en n8n | Propósito |
| :-- | :-- | :-- |
| PRINCIPAL | (importar desde `workflows/PRINCIPAL.json`) | Orquestador principal — recibe webhook ManyChat |
| ITZ KB_SEARCH | `rofQe6ZGW3OpFqcb` | Herramienta RAG — busca en KB vectorizado |
| ITZ NOTIFICATIONS | `OApztbIN8Jhb4JHz` | Herramienta email — escalamiento al equipo del hotel |

## Credenciales en n8n

| Credencial | ID | Usada en |
| :-- | :-- | :-- |
| HOTELS (MongoDB Atlas) | `Msw0gTK8f8b192VX` | Find/Insert/Update users, chat_histories, KB vectors |
| ITZANA (OpenAI) | `PjPavWO5j0jIFtSG` | Transcripción audio, análisis imagen |
| ITZANA-KAANA (OpenRouter) | `J9zb84vhqsx182XW` | Modelo principal del agente (claude-opus-4.5) |
| Redis GarooVPS | `8EUkwaZixjCH7szY` | Batching de mensajes |
| ManyChat Garoo | `aEvHbFXnmwofChqs` | Enviar respuestas al usuario |
| SMTP Itzana | ⚠️ PENDIENTE CREAR | Emails de escalamiento (Notifications workflow) |

## Estructura MongoDB (colección `HOTELS`)

| Colección | Propósito |
| :-- | :-- |
| `documents` | Chunks vectorizados del KB (31 docs, índice `itzana_vector_index`) |
| `users` | Perfil de cada huésped por `manychat_id` |
| `chat_histories` | Historial de conversación por `manychat_id` (ventana 30 msgs) |

## Agente — parámetros clave

- **Nombre en n8n**: `AI Agent`
- **Tipo**: `@n8n/n8n-nodes-langchain.agent` typeVersion 3.1
- **Modelo**: OpenRouter → `ITZANA-KAANA` (claude-opus-4.5)
- **Temperatura**: 0.3
- **Memoria**: MongoDB `chat_histories`, sessionKey = `manychat_id`, ventana 30 msgs
- **Tools**: `Call 'ITZ KB_SEARCH'` (RAG) + `notifications` (escalamiento)
- **Nombre del agente**: Kaan
- **System prompt**: Ver nodo `AI Agent` en n8n (prompt completo con identidad, validación, tools, reglas, guardrails)

---

**Qué es:** Sub-workflow herramienta de RAG. El orquestador lo llama cuando necesita responder una pregunta del huésped.

**Nodos a construir (en orden):**

| # | Nodo | Tipo | Parámetros clave |
| :-- | :-- | :-- | :-- |
| 1 | START | Execute Workflow Trigger | Inputs: `manychat_id`, `propiedad`, `entrada_usuario` |
| 2 | Search Context | Set | Mapear los 3 inputs |
| 3 | Knowledge Base | MongoDB Atlas Vector Store | Mode: `Get Many`, collection: `documents`, index: `itzana_vector_index`, prompt: `={{ $('Search Context').item.json.entrada_usuario }}`, preFilter: `={{ JSON.stringify({ "metadata.propiedad": { "$eq": $('Search Context').item.json.propiedad } }) }}`, credencial: `HOTELS` |
| 4 | Embeddings OpenAI | Embeddings OpenAI | Credencial: `Vectorizer Agent - Knowledge Bases` (sub-nodo ai_embedding del Vector Store) |
| 5 | Code in JavaScript | Code | Formatear chunks en `contexto` (código en sección PASO 4 abajo) |
| 6 | GENERAL AGENT | AI Agent | promptType: define, text: `{{ $json.entrada_usuario }}`, system prompt hotelero (ver sección PASO 4 abajo) |
| 7 | OpenAI Chat Model | OpenAI Chat Model | Model: `gpt-4o-mini`, temp: `0.1`, credencial: `ITZANA` (sub-nodo ai_languageModel del Agent) |
| 8 | RESPONSE | Set | `response = {{ $json.output }}` |

**Conexiones:**
```
START → Search Context → Knowledge Base → Code → GENERAL AGENT → RESPONSE
                              ↑ ai_embedding          ↑ ai_languageModel
                        Embeddings OpenAI        OpenAI Chat Model
```

**Código nodo 5 (Code in JavaScript):**
```javascript
const items = $input.all();
if (!items || items.length === 0) {
  return [{ json: {
    contexto: "No relevant information found.",
    propiedad: $('Search Context').item.json.propiedad,
    entrada_usuario: $('Search Context').item.json.entrada_usuario
  }}];
}
const contexto = items.map((item, i) => {
  const doc = item.json.document || {};
  return `[${i+1}] ${doc.pageContent || ''}`;
}).join('\n\n---\n\n');
return [{ json: {
  contexto,
  propiedad: $('Search Context').item.json.propiedad,
  entrada_usuario: $('Search Context').item.json.entrada_usuario
}}];
```

**System prompt nodo 6 (GENERAL AGENT):**
```
## KNOWLEDGE BASE — INFORMATION FOUND ##
{{ $json.contexto }}

---

# ITZ'ANA RESORT & RESIDENCES — VIRTUAL CONCIERGE

## GOLDEN RULES
1. Answer ONLY using information from the KNOWLEDGE BASE above.
2. NEVER invent data. If it's not in the KB, say our team can help directly.
3. Detect the user's language and respond in that same language (Spanish or English).
4. Plain text only. No markdown. Max 500 characters.
   - Exception: lists of amenities/activities use bullet • on separate lines.
5. When available, include the exact link from the KB (booking, menus, packages).
6. If user wants to book accommodation → always include: https://reservations.itzanabelize.com/book/accommodations
7. If topic is weddings/events → mention our team can provide a full quote.
8. If topic is PR/influencer → direct to partnerships@itzanabelize.com

## OUTPUT FORMAT
Respond ONLY with this JSON on a single line:
{"response": "<conversational text>", "escalate": false, "categoria": "info"}

escalate: true ONLY if user explicitly asks to speak with a person, or topic needs a personalized quote (weddings, large groups, events).
categoria: "info" | "reserva" | "bodas_eventos" | "pr" | "empleo" | "escalamiento"
```

**Leyenda:** ⬜ Pendiente · 🔄 En progreso · ✅ Listo · ⚠️ Bloqueado

---

## Credenciales necesarias (recolectar antes de empezar)

| Credencial | Usada en | Estado |
| :-- | :-- | :-- |
| **OpenAI `ITZANA`** (`PjPavWO5j0jIFtSG`) | Ya existe en n8n — transcripción, análisis de imagen, embeddings, y posiblemente el cerebro del agente | ✅ Ya existe |
| **Redis GarooVPS** (`8EUkwaZixjCH7szY`) | Ya existe en `PRINCIPAL.json` — batching de mensajes | ✅ Ya existe |
| **MongoDB Atlas (nuevo, Itz'ana)** | Vectores del KB + memoria de conversación + usuarios | ✅ Creada (`Itzana - MongoDB Atlas`) |
| **API key ManyChat** | Responder al huésped (Paso 6) | ⬜ A conseguir |
| **Modelo del agente** | ✅ **gpt-4o-mini** con credencial `ITZANA` | ✅ Decidido |

---

## Decisiones de diseño registradas

- **Canal:** ManyChat, una sola cuenta, bilinge ES/EN.
- **KB:** RAG con MongoDB Atlas Vector Store (escala a Ka'ana en el futuro). Índice: `itzana_vector_index`, colección `documents`, campo de filtro `propiedad = "ITZ"`.
- **Memoria:** MongoDB Atlas, colección `chat_histories`, clave `manychat_id`, ventana ~20 mensajes.
- **Multi-propiedad futura:** todos los chunks tienen campo `propiedad`; sumar Ka'ana = nuevo KB + misma arquitectura.
- **Fuera de alcance ahora:** E-Concierge in-stay (tareas/departamentos), Opera/OHIP, pasarela de pagos.

---

---

## PASO 1 — `KB_ITZANA.json` (archivo de contenido)

**Qué es:** El KB estructurado de Itz'ana, troceado en chunks listos para vectorizar. Claude lo genera a partir de `Itz'ana Prompt.txt`.

**Formato de cada chunk** (mismo esquema que SPECTRUM):
```json
{
  "id": "itz_categoria_slug",
  "propiedad": "ITZ",
  "categoria": "alojamientos",
  "tags": ["villa", "playa", "1 dormitorio", ...],
  "pregunta": "¿Qué tipos de villa tienen?",
  "respuesta": "Texto completo de respuesta con links si aplica."
}
```

**Categorías a cubrir:**
- `alojamientos` — villas 1/2/3 dorm, penthouses 2/3 hab, beachfront suite, deluxe room, servicios de villa
- `restaurantes` — Limilia, Nadu, Biblio Bar, Owner's Lounge, Luna Bar, Pool Bar, Rum Room, eventos gastronómicos
- `actividades` — aventuras, excursiones, paquetes/promociones
- `bodas_eventos` — espacios, catering, open bar, chamán maya, contacto Mr. Diego
- `ubicacion_logistica` — dirección, cómo llegar, shuttles, golf carts, bicicletas
- `contacto` — todos los emails, teléfonos, WhatsApp, web
- `politicas_faq` — mascotas ⚠️ VERIFICAR, empleo, colaboraciones/PR, all-inclusive (no)

**⚠️ Conflicto a resolver:** política de mascotas aparece contradictoria en los transcripts (un caso "no pet friendly", otro "2 small dogs ok"). Preguntar al hotel antes de publicar.

**Archivos fuente:**
- `Itz'ana Prompt.txt` — contenido principal del KB
- `Itz'ana Transcript - Instagram.csv` — preguntas reales de usuarios → guiar tags
- `Analytics Bot_Itzana - Sheet1.csv` — keywords más frecuentes → guiar tags

**Destino:** `ITZANA-KAANA/KBs/KB_ITZANA.json`

**Estado:** ⬜ Pendiente — Claude generará el archivo; revisar y aprobar antes de vectorizar.

---

## PASO 2 — MongoDB Atlas

**Qué hay que crear:**

### 2A — Cluster y base de datos
- Cluster: puede ser el M0 (free tier) o el que ya tengas
- Base de datos: `itzana`
- Colecciones:
  - `documents` — chunks vectorizados del KB
  - `chat_histories` — historial de conversación por usuario
  - `users` — perfil por manychat_id

### 2B — Índice vectorial en `documents`
Crear en Atlas → Search → Create Search Index → Atlas Vector Search:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    },
    {
      "type": "filter",
      "path": "metadata.propiedad"
    }
  ]
}
```

Nombre del índice: `itzana_vector_index`

### 2C — Credencial en n8n
- Tipo: **MongoDB** (o **MongoDB Atlas** si está disponible como tipo)
- Nombre sugerido: `Itzana - MongoDB Atlas`
- Connection string: `mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/itzana`

**Estado:** ⬜ Pendiente

---

## PASO 3 — Workflow `Itzana_Vectorizar_KB`

**Propósito:** Cargar `KB_ITZANA.json` en Mongo como vectores. Se ejecuta **una sola vez** (y cada vez que se actualice el KB).

**Referencia:** `SPECTRUM AGENTE/Agente Unificado/Vectorizar los KBs.json`

**Nodos a construir (en orden):**

| # | Nodo | Tipo | Parámetros clave |
| :-- | :-- | :-- | :-- |
| 1 | **Manual Trigger** | `n8n-nodes-base.manualTrigger` | — |
| 2 | **Set Chunks** | `n8n-nodes-base.set` | `chunks` = pegar el array del `KB_ITZANA.json` |
| 3 | **Split Out** | `n8n-nodes-base.splitOut` | Field: `chunks` |
| 4 | **Default Data Loader** | `@n8n/n8n-nodes-langchain.documentDefaultDataLoader` | `jsonMode: expressionData`, `jsonData: {{ $json.pregunta }}. {{ $json.respuesta }}`, metadata: id, categoria, tags, pregunta, respuesta, propiedad |
| 5 | **Embeddings OpenAI** | `@n8n/n8n-nodes-langchain.embeddingsOpenAi` | Credencial: `ITZANA` (ya existente) |
| 6 | **MongoDB Atlas Vector Store** | `@n8n/n8n-nodes-langchain.vectorStoreMongoDBAtlas` | `mode: insert`, colección `documents`, índice `itzana_vector_index`, credencial: `Itzana - MongoDB Atlas` |

**Conexiones:**
```
Manual Trigger → Set Chunks → Split Out → [Default Data Loader] → MongoDB Atlas Vector Store
                                                       ↑
                                            Embeddings OpenAI (ai_embedding)
```

**Verificación:** Tras ejecutar, ir a Atlas → `documents` → comprobar que los documentos tienen campo `embedding` (array de 1536 números) y `metadata.propiedad = "ITZ"`.

**Estado:** ⬜ Pendiente

---

## PASO 4 — Workflow `Itzana_KB_Search` (herramienta RAG)

**Propósito:** Herramienta que recibe una pregunta, busca en el KB vectorizado y devuelve una respuesta formulada.

**Referencia:** `SPECTRUM AGENTE/Agente Unificado/KB SEARCH.json`

**Inputs del sub-workflow:**
- `manychat_id` (string)
- `propiedad` (string) — por ahora siempre `"ITZ"`
- `entrada_usuario` (string)

**Nodos a construir:**

| # | Nodo | Tipo | Parámetros clave |
| :-- | :-- | :-- | :-- |
| 1 | **START** | `n8n-nodes-base.executeWorkflowTrigger` | Inputs: manychat_id, propiedad, entrada_usuario |
| 2 | **Search Context** | `n8n-nodes-base.set` | Mapear los 3 inputs |
| 3 | **Knowledge Base** | `@n8n/n8n-nodes-langchain.vectorStoreMongoDBAtlas` | `mode: load`, colección `documents`, índice `itzana_vector_index`, prompt: `{{ $('Search Context').item.json.entrada_usuario }}`, preFilter: `{{ JSON.stringify({ "metadata.propiedad": { "$eq": $('Search Context').item.json.propiedad } }) }}` |
| 4 | **Embeddings OpenAI** | `@n8n/n8n-nodes-langchain.embeddingsOpenAi` | Credencial: `ITZANA` (ai_embedding → Knowledge Base) |
| 5 | **Code in JavaScript** | `n8n-nodes-base.code` | Formatear chunks recuperados en `contexto` (ver código abajo) |
| 6 | **GENERAL AGENT** | `@n8n/n8n-nodes-langchain.agent` | System prompt hotelero (ver abajo), promptType: define, text: `{{ $json.entrada_usuario }}` |
| 7 | **Chat Model** | OpenAI o OpenRouter | temp: 0.1, modelo: gpt-4o-mini o equivalente (ai_languageModel → GENERAL AGENT) |
| 8 | **RESPONSE** | `n8n-nodes-base.set` | `response = {{ $json.output }}` |

**Código del nodo 5 (Code in JavaScript):**
```javascript
const items = $input.all();
if (!items || items.length === 0) {
  return [{ json: {
    contexto: "No se encontró información relevante.",
    propiedad: $('Search Context').item.json.propiedad,
    entrada_usuario: $('Search Context').item.json.entrada_usuario
  }}];
}
const contexto = items.map((item, i) => {
  const doc = item.json.document || {};
  return `[${i+1}] ${doc.pageContent || ''}`;
}).join('\n\n---\n\n');
return [{ json: {
  contexto,
  propiedad: $('Search Context').item.json.propiedad,
  entrada_usuario: $('Search Context').item.json.entrada_usuario
}}];
```

**System prompt del GENERAL AGENT:**
```
## KNOWLEDGE BASE — INFORMACIÓN ENCONTRADA ##
{{ $json.contexto }}

---

# CONCIERGE VIRTUAL — ITZ'ANA RESORT & RESIDENCES

## REGLAS DE ORO
1. Responde ÚNICAMENTE con información del KNOWLEDGE BASE de arriba.
2. NUNCA inventes datos. Si no está en el KB, di que el equipo del resort puede ayudar.
3. Responde en el idioma en que el usuario te habla (español o inglés).
4. Texto plano. Sin markdown. Máximo 500 caracteres.
   - Excepción: listas de amenidades/actividades usan bullet • en líneas separadas.
5. Cuando corresponda, incluye el link exacto del KB (reservas, menús, paquetes).
6. Si el usuario quiere reservar → link: https://reservations.itzanabelize.com/book/accommodations
7. Si el usuario pregunta por bodas/eventos → escalar a Mr. Diego (mencionar que le pondremos en contacto).
8. Si el usuario es de prensa/PR/influencer → escalar a partnerships@itzanabelize.com.

## FORMATO DE SALIDA
Responde ÚNICAMENTE con este JSON en una sola línea:
{"response": "<texto conversacional>", "escalate": false, "categoria": "info"}

escalate: true SOLO si el usuario pide hablar con una persona o el tema requiere cotización (bodas, grupos grandes, eventos).
categoria: "info" | "reserva" | "bodas_eventos" | "pr" | "empleo" | "escalamiento"
```

**Estado:** ⬜ Pendiente

---

## PASO 5 — Workflow `Itzana_Notifications` (handoff / escalamiento)

**Propósito:** Enviar email al contacto correcto del hotel cuando el agente escala un caso.

**Inputs del sub-workflow:**
- `manychat_id` (string)
- `nombre` (string, si se conoce)
- `categoria` (string) — `bodas_eventos | pr | empleo | escalamiento`
- `resumen_conversacion` (string)
- `entrada_usuario` (string)

**Lógica de routing:**

| categoria | Destinatario | Asunto |
| :-- | :-- | :-- |
| `bodas_eventos` | reservations@itzanabelize.com + Mr. Diego (email ⚠️ pendiente) | "Consulta de bodas/eventos - Bot" |
| `pr` | partnerships@itzanabelize.com | "Consulta PR/Colaboración - Bot" |
| `empleo` | (email HR ⚠️ pendiente) | "Consulta empleo - Bot" |
| `escalamiento` | concierge@itzanabelize.com | "Escalamiento a humano - Bot" |
| `reserva` | reservations@itzanabelize.com | "Consulta de reserva - Bot" |

**Nodos a construir:**

| # | Nodo | Tipo | Parámetros clave |
| :-- | :-- | :-- | :-- |
| 1 | **START** | executeWorkflowTrigger | Inputs: manychat_id, nombre, categoria, resumen_conversacion, entrada_usuario |
| 2 | **Switch** | `n8n-nodes-base.switch` | Por valor de `categoria` → output por cada tipo |
| 3–N | **Send Email** (uno por tipo) | `n8n-nodes-base.emailSend` o HTTP a SendGrid/Postmark | Destinatario + asunto + cuerpo HTML con el resumen |

**⚠️ Pendiente:** email de Mr. Diego (eventos) y email de HR (empleo). Usar placeholders hasta confirmar.

**Estado:** ⬜ Pendiente

---

## PASO 6 — Orquestador (extender `PRINCIPAL.json`)

**Propósito:** Conectar el front de preprocesamiento existente con el cerebro del agente.

**Punto de inserción:** Después del nodo `DELETE MESSAGES` (que ya existe en `PRINCIPAL.json`).

**Nodos a agregar (en orden, tras DELETE MESSAGES):**

### 6A — Set propiedad
| Nodo | Tipo | Parámetros |
| :-- | :-- | :-- |
| **Set Propiedad** | `n8n-nodes-base.set` | `propiedad = "ITZ"`, `manychat_id = {{ $('PARSE BODY').first().json.current_body.id }}`, `entrada_usuario = {{ $('JOINNING MESSAGE').first().json.message }}` |

### 6B — Find / Upsert User en MongoDB
| Nodo | Tipo | Parámetros |
| :-- | :-- | :-- |
| **Find User** | `n8n-nodes-base.mongoDb` | Operation: findOne, DB: `itzana`, Collection: `users`, Query: `{ "manychat_id": "{{ $json.manychat_id }}" }` |
| **IF Usuario Nuevo** | `n8n-nodes-base.if` | Condición: `{{ $json._id }}` is empty |
| **Insert User** | `n8n-nodes-base.mongoDb` | Operation: insert, Collection: `users`, doc: `{ manychat_id, first_interaction: now, last_interaction: now }` |
| **Update User** | `n8n-nodes-base.mongoDb` | Operation: update, Collection: `users`, `{ last_interaction: now, last_message: entrada_usuario }` |

### 6C — AI Agent principal
| Nodo | Tipo | Parámetros clave |
| :-- | :-- | :-- |
| **CONCIERGE ITZANA** | `@n8n/n8n-nodes-langchain.agent` | `promptType: define`, `text: {{ $json.entrada_usuario }}`, system prompt (ver abajo) |
| **Chat Model** | OpenAI (gpt-4o) o OpenRouter | Credencial ITZANA, temp: 0.3 |
| **MongoDB Chat Memory** | `@n8n/n8n-nodes-langchain.memoryMongoDbChat` | DB: `itzana`, Collection: `chat_histories`, sessionKey: `{{ $json.manychat_id }}`, contextWindowLength: 20 |
| **Tool: kb_search** | `n8n-nodes-base.executeWorkflow` | Workflow: `Itzana_KB_Search`, inputs: manychat_id, propiedad, entrada_usuario |
| **Tool: handoff** | `n8n-nodes-base.executeWorkflow` | Workflow: `Itzana_Notifications`, inputs: manychat_id, nombre, categoria, resumen, entrada_usuario |

**System prompt del CONCIERGE ITZANA (orquestador):**
```
Eres el concierge virtual oficial de Itz'ana Resort & Residences, un resort de lujo en Placencia, Belice.
Tu nombre es "Itz'ana Concierge". Eres cálido, profesional y reflejas el espíritu del Caribe.

## IDIOMA
Detecta el idioma del usuario y responde siempre en ese idioma (español o inglés).

## HERRAMIENTAS DISPONIBLES
- `kb_search`: úsala para responder CUALQUIER pregunta sobre el resort (alojamientos, restaurantes,
  actividades, bodas, ubicación, políticas, precios, servicios). SIEMPRE busca en el KB antes de responder.
- `handoff`: úsala cuando:
  * El usuario quiere hablar con una persona
  * Consulta de boda/evento (escalar a Mr. Diego y a reservations@)
  * Consulta de PR/colaboración (escalar a partnerships@)
  * Pregunta de empleo
  Pasa el resumen de la conversación y la categoría correcta.

## REGLAS
1. SIEMPRE usa `kb_search` antes de responder sobre el resort. Nunca inventes.
2. Responde en texto plano, sin markdown, máximo 500 caracteres.
3. Si el usuario pregunta precios → usa kb_search y sirve el link de reservas.
4. Si el usuario envió audio o imagen → ya fue procesado; el input que recibes es el texto/descripción.
5. Sé conciso pero cálido. No repitas el nombre del resort en cada mensaje.
6. Nunca digas que eres una IA si no te lo preguntan.

## FORMATO DE SALIDA
Texto de respuesta directamente (no JSON). El agente estructura la respuesta para el usuario.
```

### 6D — Procesar respuesta del agente
| Nodo | Tipo | Parámetros |
| :-- | :-- | :-- |
| **Parse Agent Output** | `n8n-nodes-base.set` | `response_text = {{ $json.output }}` |

### 6E — Responder a ManyChat
| Nodo | Tipo | Parámetros clave |
| :-- | :-- | :-- |
| **Send to ManyChat** | `n8n-nodes-base.httpRequest` | Method: POST, URL: `https://api.manychat.com/fb/sending/sendContent`, Headers: `Authorization: Bearer <API_KEY>`, Body: `{ "subscriber_id": "{{ manychat_id }}", "data": { "version": "v2", "content": { "type": "instagram", "messages": [{ "type": "text", "text": "{{ response_text }}" }] } } }` |

**Estado:** ⬜ Pendiente

---

## PASO 7 — Pruebas end-to-end

### Casos de prueba (basados en transcripts reales)

| # | Input de prueba | Respuesta esperada |
| :-- | :-- | :-- |
| T1 | "how much for a night?" | Link de reservas + tipos de alojamiento |
| T2 | "¿Tienen paquetes para dos personas?" | Link paquetes/promociones |
| T3 | "Do you have shuttles to Placencia?" | Info shuttles vía concierge, golf carts de renta |
| T4 | "Queremos hacer nuestra boda ahí" | Escalar: Mr. Diego + reservations@, spaces overview |
| T5 | "Are you pet friendly?" | Respuesta con caveat ⚠️ (validar con hotel primero) |
| T6 | "I'd love to work together as an influencer" | Escalar: partnerships@itzanabelize.com |
| T7 | (Enviar imagen/audio) | El agente procesa la transcripción/descripción y responde |
| T8 | Conversación multi-turno (3+ mensajes) | El agente recuerda el contexto anterior |

### Check de integración
- [ ] Redis batching funciona (enviar 2 mensajes rápidos → llega como uno)
- [ ] Audio transcrito correctamente (OpenAI Whisper)
- [ ] Imagen analizada correctamente (GPT-4o)
- [ ] KB RAG devuelve chunks relevantes (probar con `Itzana_KB_Search` aislado)
- [ ] Memoria de conversación persiste entre mensajes (MongoDB `chat_histories`)
- [ ] Handoff envía email al destinatario correcto según categoría
- [ ] Respuesta llega al usuario en ManyChat

**Estado:** ⬜ Pendiente

---

## Notas y pendientes de contenido

| # | Pendiente | Prioridad |
| :-- | :-- | :-- |
| P1 | Confirmar política de mascotas (contradictoria en transcripts) | Alta |
| P2 | Email de Mr. Diego (bodas/eventos) — usando jorge.calderon@garooinc.com para pruebas | Alta |
| P3 | Email de HR (empleo) | Media |
| P4 | Confirmar campos exactos del payload de ManyChat que envía el bot actual | Alta |
| P5 | Decidir modelo del agente: OpenAI `ITZANA` (gpt-4o) u OpenRouter (Claude) | Alta |
| P6 | Contenido KB de Ka'ana (para 2ª propiedad, futuro) | Baja |
| P7 | Horarios exactos del spa, restaurantes, piscinas (están como ejemplo en E-Concierge pero no en el Prompt) | Media |
