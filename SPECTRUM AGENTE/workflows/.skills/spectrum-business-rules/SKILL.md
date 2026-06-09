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
