# Skill: Spectrum Agente Unificado
Este skill contiene las reglas de negocio, mapeos técnicos y arquitectura del ecosistema de agentes de SPECTRUM VIVIENDA.

## 1. Arquitectura del Sistema
El sistema es una arquitectura multi-agente orquestada por n8n:
- **Orquestador (`Principal.json`):** Clasifica intenciones y delega a tools. Mantiene el flag `conversation_analysis` para control de sincronización.
- **Tools Specialized:** `lead_collector`, `kb_search`, `rsvp`, `send_media`.
- **Persistencia:** MongoDB Atlas (colecciones: `users`, `appointments`, `chat_histories*`).
- **Sincronización:** `Sync_CRM.json` ( SOAP Dynamics 365).

## 2. Reglas del CRM (SOAP API)
### Endpoint y Headers
- **URL:** `https://crm.spectrum.com.gt:8055/Spectrum_WS_GeneracionLead/Service.asmx`
- **SOAPAction:** `http://tempuri.org/CreacionClientePotencialBot`
- **Content-Type:** `text/xml; charset=utf-8`

### Campos Críticos (Typos Obligatorios)
- Correo principal: `<_CorreEletronico>`
- Campaña UTM: `<_UTMCampaing>`

### Lógica de Etiquetas Opcionales
- **Regla:** Solo se deben enviar etiquetas que tengan valor. Si el dato es nulo o vacío, la etiqueta debe omitirse completamente del XML (excepto `_Comentarios`).
- **Implementación:** Usar expresiones ternarias en n8n: `{{ $json.valor ? '<_Etiqueta>' + $json.valor + '</_Etiqueta>' : '' }}`.

## 3. Mapeo de Catálogos

### Proyectos (`_Proyecto`)
| Código Interno | Código CRM | Proyecto |
|---|---|---|
| `pvv` | `PVV` | Parque Vista Verde |
| `pm` | `PMAR` | Parque Mariscal |
| `pp` | `PPO` | Parque Portales |
| `polanco` | `PPOL` | Parque Polanco |
| `psb` | `PSB` | Parque Sotobosque |

### Estado Civil (`_EstadoCivil`)
- **Soltero:** `100000000`
- **Casado:** `100000001`
- **Divorciado:** `100000002`
- **Unido / Unión Libre:** `100000003`

### Número de Habitaciones (`_NumeroHabitaciones`)
- **1:** `100000000`
- **2:** `100000001`
- **3:** `100000002`

### Intención de Compra (`_MotivoInteres`)
- **Inversión (I):** `100000001`
- **Vivir (V):** `100000003`
- **Información General:** `100000000`

### Canales (`_UTMSource`)
- **WhatsApp:** `100000004`
- **Facebook:** `100000005`
- **Instagram:** `100000012`

## 4. Lógica de Sincronización Diferida (`Sync_CRM`)
1. **Trigger:** Schedule cada 10-15 minutos.
2. **Filtro Inactividad:** Busca leads con `last_interaction` < 15 minutos atrás y `conversation_analysis != true`.
3. **Enriquecimiento:** Usa un Information Extractor para generar `Resumen` y `Dudas` de la conversación antes de enviar al CRM.
4. **Control de Duplicidad:** Marca `conversation_analysis = true` tras el éxito del sync. El orquestador principal debe resetear este flag a `false` con cada nuevo mensaje del usuario.

## 5. Auditoría de Calidad
- **Colección:** `quality_logs`.
- **Proceso:** Corre tras el sync del CRM. Evalúa tono, uso de tools y avance en el funnel.

---

## 6. Índice de Nodos por Workflow

> Usar este índice para localizar un nodo sin grep ciego. Patrón: `grep -n '"name": "NOMBRE_NODO"' ARCHIVO.json`

### AGENT PRINCIPAL.json

#### Entrada y batching (Redis)
| Nodo | Línea aprox. | Rol |
|---|---|---|
| `Webhook` | 1085 | Punto de entrada desde ManyChat |
| `PARSE BODY` | 540 | Extrae `message`, `input_channel`, `phone` del payload |
| `ES ARCHIVO` | 1055 | Clasifica tipo de input (texto / audio / imagen / archivo) |
| `ES AUDIO / IMAGEN` | 999 | Bifurcación audio vs imagen |
| `HTTP IF AUDIO` | 826 | Llama a Whisper para transcripción |
| `TRANSCRIBE AUDIO` | 951 | Transcribe audio a texto |
| `ANALIZA IMAGEN` | 849 | Extrae texto de imágenes con visión |
| `text input` / `audio input` / `image input` | 812 / 754 / 783 | Normaliza el mensaje a `{mensaje, hora_llegada}` |
| `SAVE MESSAGE` / `GET MESSAGE` / `DELETE MESSAGES` | 696 / 674 / 639 | Buffer Redis para batching de mensajes |
| `Wait` | 658 | Ventana de espera del batching |
| `Aggregate` / `Sort` / `Merge` | 903 / 923 / 936 | Consolida mensajes del buffer |
| `INPUT FINAL` | 725 | Mensaje final consolidado listo para procesar |

#### Gestión de usuario (MongoDB)
| Nodo | Línea aprox. | Rol |
|---|---|---|
| `Find User` | 259 | Consulta MongoDB por `manychat_id` |
| `If USER NOT EXIST` | 525 | Bifurca: crear usuario nuevo vs actualizar existente |
| `DATA to CREATE` | 402 | Prepara documento completo para usuario nuevo. Campo de atribución: `atribucion_tag` (no `tag_medio`) |
| `DATA to UPDATE` | 491 | Prepara objeto de actualización PRE-agente. Incluye `atribucion_tag`, `atribucion_medio`, `atribucion_contacto`, `utm_source_crm` |
| `Insert User` | 238 | Crea documento en colección `users` |
| `Update User` | 216 | Actualiza usuario con datos PRE-agente (extractores) |
| `User Data` | 74 | **Snapshot PRE-Update** del usuario → `Find User \|\| Insert User` |

> ⚠️ `User Data` es un snapshot tomado ANTES de que `Update User` corra. No refleja los cambios de la ejecución actual.

#### Extractores y contexto
| Nodo | Línea aprox. | Rol |
|---|---|---|
| `If NO WHATSAPP` | 118 | Bifurca WhatsApp (con extractor de proyecto) vs otros canales |
| `Proyecto` | 140 | `informationExtractor`: detecta proyecto del mensaje (**solo WhatsApp**). `required: false` |
| `Lenguaje & Asesoria` | 169 | `informationExtractor`: detecta idioma, flag de asesoría y `interes_precios` (boolean — solo `true` si el usuario pregunta EXPLÍCITAMENTE por precio, cuota, mensualidad o plan de pago; `false` para preguntas generales de proyecto) |
| `CONTEXT 1` | 313 | Ensambla contexto para el agente: `proyecto`, `consulta_pendiente`, `entrada_usuario`, `canal` |
| `PROJECT LIST` | 592 | Set con catálogo de proyectos (`proyectos`, `proyectos_nombre`) |
| `JOINNING MESSAGE` | 563 | Espera a que `Insert User` / `Update User` terminen |

#### Agente principal y tools
| Nodo | Línea aprox. | Rol |
|---|---|---|
| `MongoDB Chat Memory` | 1103 | Historial de conversación. `sessionId = manychat_id` |
| `OpenAI Chat Model` | 1129 | LLM del orquestador |
| `PRINCIPAL` | 1152 | Agente Sof-IA. Contiene `text` (contexto lead) y `systemMessage` |
| `lead_collector` | 1280 | Tool: recolecta nombre, correo, teléfono |
| `kb_search` | 1516 | Tool: RAG sobre la KB del proyecto |
| `rsvp` | 1623 | Tool: agenda citas |
| `send_media` | 1899 | Tool: envía brochures/imágenes por ManyChat |

#### Post-agente: parseo y persistencia
| Nodo | Línea aprox. | Rol |
|---|---|---|
| `Parse response` | 1293 | Parsea JSON del output del agente → extrae `proyecto`, `datos_completos`, `consulta_pendiente_*`, `respuesta` |
| `If TIENE DATOS NUEVOS` | 1327 | ¿El agente detectó nuevos datos del lead? |
| `Prepare Update` | 1398 | Arma objeto POST-agente para actualizar MongoDB |
| `Hay Cambios?` | 1421 | Genera `FIELDS` dinámico. Filtra `null` y `undefined` |
| `Update User Lead` | 1438 | Escribe datos post-agente en colección `users` |

#### Notificaciones y analítica
| Nodo | Línea aprox. | Rol |
|---|---|---|
| `IF NUEVO LEAD` | 1954 | ¿Es el primer mensaje del lead? |
| `'Notifications Master' Nuevos Leads` | 1777 | Notifica al equipo sobre leads nuevos |
| `'Notifications Master' Escalation` | 1829 | Notifica escalación a asesor humano |
| `Calculate Respond Time` | 1725 | Calcula tiempo de respuesta |
| `Insert Analytics` | 1672 | Graba log en MongoDB (`sessionId`, `response_time`, `proyecto`, `canal`) |
| `IF INTERES PRECIOS` | — | Evalúa `Lenguaje & Asesoria → output.interes_precios`. Se ejecuta tras `Insert Analytics` (siempre corre) |
| `'Notifications Master' Interés Precios` | — | Notifica interés comercial. Payload: `proyecto`, `nombre_lead`, `telefono_lead`, `ultima_consulta` |
| `RESPOND TO MANYCHAT` | 30 | Envía respuesta final a ManyChat |

---

### Lead Collector.json

| Nodo | Línea aprox. | Rol |
|---|---|---|
| `START` | 44 | Recibe parámetros del orquestador: `query`, `manychat_id`, `mongo_id`, `canal`, `tel_sistema`, `nombre`, `correo`, `telefono`, `proyecto` |
| `SET CONTEXT` | 121 | Ensambla contexto para el Lead Agent (incluye `tel_sistema` para ESCENARIO 3) |
| `MongoDB Chat Memory` | 183 | Historial de conversación. `sessionId = manychat_id` |
| `OpenAI Chat Model` | 160 | LLM del Lead Agent |
| `Lead Agent` | 138 | Agente de recolección. Contiene los ESCENARIOS (1, 2, 3) y reglas de `tel_sistema` |
| `Parse Response` | 202 | Parsea JSON: `nombre`, `correo`, `telefono`, `datos_completos`, `transferir_agente`, `response` |
| `IF DATA COMPLETED` | 289 | Bifurca: `transferir_agente = 1` (datos completos) vs continuar recolección |
| `LEAD DATA` | 336 | Prepara payload de retorno cuando datos están completos |
| `RESPONSE` | 370 | Devuelve respuesta parcial cuando faltan datos |
| `Update User` | 424 | Actualiza `nombre`, `correo`, `telefono` en MongoDB |
| `CRM Data` | 459 | Prepara datos para el CRM SOAP |
| `GENERAR LEAD CONTACT` | 234 | Llama a la API SOAP de Dynamics 365 |

---

## 7. Expresiones Críticas (propensas a bugs)

Estas expresiones contienen lógica no trivial. Verificar antes de modificar nodos relacionados.

### `CONTEXT 1` — campo `proyecto` (línea ~298)
```js
{{ $('Proyecto').isExecuted ? $json.output.proyecto : '' }}
```
> `Proyecto` extractor solo corre en WhatsApp. En otros canales, `CONTEXT 1.proyecto` siempre es `''`.

### `DATA to UPDATE` — campo `proyecto` (línea ~422)
```js
{{ $('CONTEXT 1').item.json.proyecto || $('Find User').item.json.proyecto }}
```
> Prioriza el proyecto detectado en este mensaje; si no hay, usa el que ya estaba en MongoDB.

### Agente `PRINCIPAL` — campo `text` y `systemMessage` (línea ~1140)
```js
Proyecto activo en sesión: {{ $('CONTEXT 1').item.json.proyecto || $('User Data').item.json.proyecto || "Ninguno" }}
```
> `User Data` es snapshot PRE-Update. `CONTEXT 1` tiene el valor fresco del extractor. El OR garantiza fallback.

### `Prepare Update` — campo `proyecto` (línea ~1383)
```js
{{ $('Parse response').item.json.proyecto || $('User Data').item.json.proyecto || undefined }}
```
> Si el agente no detectó proyecto Y User Data está vacío, devuelve `undefined` para no sobreescribir.

### `Prepare Update` — campo `consulta_pendiente` (línea ~1377)
```js
{{ $json.consulta_pendiente_limpiar ? null : ($json.consulta_pendiente_guardar || $('User Data').item.json.consulta_pendiente || undefined) }}
```

### `Hay Cambios?` — campo `FIELDS` (línea ~1421)
```js
={{ Object.keys($json).filter(k => k !== '_id' && $json[k] !== null && $json[k] !== undefined).join(",") }}
```
> El filtro `!== null && !== undefined` evita sobreescribir campos en MongoDB con valores vacíos.
