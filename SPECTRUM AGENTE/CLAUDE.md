# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Skills requeridos

Antes de cualquier tarea en este proyecto, lee los skills que apliquen:

| Situación | Skill |
|---|---|
| Siempre (arquitectura, CRM, catálogos) | `Agente Unificado/.skills/spectrum-agente-unificado/SKILL.md` |
| Crear o diseñar un workflow nuevo | `Agente Unificado/.skills/n8n-workflow-patterns/SKILL.md` |
| Configurar parámetros de un nodo | `Agente Unificado/.skills/n8n-node-configuration/SKILL.md` |
| Código en nodo Code (JS) | `Agente Unificado/.skills/n8n-code-javascript/SKILL.md` |
| Expresiones `{{ }}` | `Agente Unificado/.skills/n8n-expression-syntax/SKILL.md` |
| Interpretar errores de validación | `Agente Unificado/.skills/n8n-validation-expert/SKILL.md` |
| Usar herramientas MCP de n8n | `Agente Unificado/.skills/n8n-mcp-tools-expert/SKILL.md` |

---

## ⚠️ REGLA CRÍTICA - VALIDACIÓN DE DATOS OBLIGATORIA

**El agente PRINCIPAL DEBE validar que existan nombre, correo Y teléfono ANTES de cualquier otra acción.**

Si el lead NO ha compartido estos 3 datos:
- ❌ NO responder sobre proyectos
- ❌ NO llamar `kb_search`  
- ❌ NO llamar `rsvp`
- ✅ SOLO llamar `lead_collector`

**SIN EXCEPCIONES.** Esto es imperativo. Ver sección "🔴 VALIDACIÓN OBLIGATORIA PRIMERO" en AGENT PRINCIPAL.json → systemMessage.

Motivo: Caso real (2026-05-22): Lead sin datos respondió consulta sobre Portales y el agente respondió sin recolectar datos primero.

---

## Arquitectura del sistema

Agente conversacional inmobiliario para **SPECTRUM VIVIENDA**. El orquestador central (*Sof-IA*) recibe mensajes desde ManyChat (WhatsApp, Instagram, Messenger), clasifica la intención y delega a sub-workflows especializados (tools). La persistencia es MongoDB Atlas y la sincronización al CRM es diferida via SOAP.

```
Agente Unificado/
├── AGENT PRINCIPAL.json       ← Orquestador: clasifica intenciones, delega a tools
├── Lead Collector.json        ← Captura y persiste datos del lead en MongoDB
├── KB SEARCH.json             ← RAG por proyecto (Vector Search en MongoDB)
├── RSVP.json                  ← Gestión de citas; escribe en colección `appointments`
├── Send Media.json            ← Envío de brochures/archivos por WhatsApp
├── Sync_CRM.json              ← Sincronización diferida al CRM SOAP (cada 10-15 min)
└── Notifications Master.json  ← Notificaciones internas al equipo
```

### Colecciones MongoDB
- `users` — datos del lead
- `appointments` — citas agendadas
- `chat_histories*` — historial de conversación por contacto
- `quality_logs` — auditoría de calidad post-sync

### Modelos IA
- `gpt-5.4-mini` — Orquestador (`AGENT PRINCIPAL.json`)
- `gpt-5-mini` — Tools especializadas (`KB SEARCH.json`)
- `gpt-4o` — Procesamiento de media (`Send Media.json`)

---

## Knowledge Bases (KBs)

Los archivos en `/KBs` se cargan en MongoDB Atlas (colección `documents`) para la búsqueda vectorial. El índice se llama `spectrum_vector_index`. El filtro es por el campo `"proyecto"` en **MAYÚSCULAS**.

| Archivo | Código de proyecto |
|---|---|
| `KB PVV.json` | `PVV` |
| `KB PMAR.json` | `PMAR` |
| `KB PPO.json` | `PPO` |
| `KB PPOL.json` | `PPOL` |
| `KB PSB.json` | `PSB` |

---

## Reglas críticas del CRM SOAP

**Endpoint:** `https://crm.spectrum.com.gt:8055/Spectrum_WS_GeneracionLead/Service.asmx`  
**SOAPAction:** `http://tempuri.org/CreacionClientePotencialBot`

### Typos obligatorios en el XML (así está definido en la API — no corregir)
- Email: `<_CorreEletronico>` (sin "o" en *Correo*, sin "c" en *Electrónico*)
- Campaña UTM: `<_UTMCampaing>` (sin "i" en *Campaign*)

### Etiquetas opcionales
Omitir la etiqueta completa si el valor es nulo. Solo `_Comentarios` puede enviarse vacío:
```
{{ $json.valor ? '<_Tag>' + $json.valor + '</_Tag>' : '' }}
```

### Catálogos de referencia rápida
Ver `spectrum-soap-api.md` para los códigos completos. Valores más usados:

| Campo | Valor | Label |
|---|---|---|
| `_OrigenCliente` | `100000001` | Chat (siempre fijo) |
| `_UTMSource` WhatsApp | `100000004` | — |
| `_UTMSource` Instagram | `100000012` | — |
| `_MetodocontactoPref` WhatsApp | `4` | ⚠️ Entero simple, no el catálogo CRM |
| `_EstadoCivil` Soltero | `100000000` | — |
| `_MotivoInteres` Inversión | `100000001` | — |
| `_Apellido` no disponible | `"N/A"` | Campo requerido |
| `_TelefonoMovil` | `+502XXXXXXXX` | Siempre con código de país |
| `_FechaCita` | ISO 8601 UTC | Ej: `2026-05-10T15:00:00.000Z` |

---

## Control de flujo y sincronización

- **`conversation_analysis` flag:** El orquestador lo resetea a `false` con cada mensaje nuevo. `Sync_CRM.json` lo marca `true` tras sincronizar.
- **Anti-duplicados:** Verificar existencia en MongoDB antes de crear un nuevo documento de lead.
- **Sync_CRM trigger:** Schedule cada 10-15 min. Filtra leads con `last_interaction` < 15 min atrás y `conversation_analysis != true`.

---

## Referencia de documentos del proyecto

- `docs/estado_proyecto.md` — Estado actual de cada módulo y acciones pendientes
- `docs/spectrum-soap-api.md` — Catálogo completo de códigos de la API SOAP
- `docs/estrategia_captacion_whatsapp.md` — Estrategia general
- `docs/reporte_agente_sofia.md` — Reporte de orquestador
- `flujos de muestra Version anterior/` — Flujos de referencia antiguos para entender patrones aplicados

---

## 🔌 Integración MCP (MongoDB & n8n)

Para auditar, inspeccionar o modificar la base de datos y los flujos remotamente, cualquier IA debe utilizar las siguientes configuraciones MCP locales.

**1. MongoDB MCP (spectrum-mongodb-mcp-server)**
- Se encuentra configurado localmente en el archivo `mcp_config.json` de la IA.
- *Tip de conexión:* Si estás ejecutando en local y encuentras errores `ECONNREFUSED` hacia Atlas, debes sobrescribir temporalmente el DNS en tu script usando `dns.setServers(['8.8.8.8', '8.8.4.4'])` para evitar el bloqueo de VPN/ISP locales, o simplemente conectarte usando `mcp_spectrum-mongodb-mcp-server_...`.

**2. n8n MCP Server**
- URL de n8n: `https://agentsprod.redtec.ai`
- Comando configurado en el `mcp_config.json`: `npx -y @n8n/mcp-remote agentsprod.redtec.ai`
- Puedes invocar la herramienta `mcp_n8n-mcp-server_get_workflow_details` y proporcionarle el ID exacto del flujo remoto (ver abajo) para obtener o modificar el JSON actual en producción.

### 🆔 Directorio de Workflow IDs en n8n

Para interactuar rápidamente con los flujos de "SPECTRUM AGENTE" en el servidor remoto, utiliza estos IDs en tus llamadas a MCP:

| Flujo Local | ID en n8n Servidor | Descripción |
|---|---|---|
| `AGENT PRINCIPAL.json` | `iXaptKTUXaXrP7aF` | Orquestador principal |
| `Sync_CRM.json` | `TTVNRX38pPoPmK2X` | Cronjob para la sincronización SOAP |
| `Lead Collector.json` | `SHPFhvoal7k1Rqf9` | Extractor de datos del lead |
| `KB SEARCH.json` | `D3LKuNi6CmMIdvzg` | Motor de búsqueda RAG |
| `RSVP.json` | `TjFPzHs5aimxILH7` | Agendamiento de citas |
| `Send Media.json` | `NtTiyrNy2LHimE7u` | Envío de adjuntos |
| `Notifications Master.json` | `r1Jf5vwrkBrT4dEu` | Manejo de correos internos |
| `Vectorizar los KBs.json` | `LLiVnT0M6xvDKive` | Flujo interno para ingesta vectorial |
