# QUICK_REF — Itz'ana / Kaan
> Leer este archivo primero. Reemplaza leer BUILD.md + CLAUDE.md completos al inicio de sesión.
> Script de búsqueda: `.\scripts\search_context.ps1 -topic <tema>`

---

## Estado del proyecto
`BUILD.md` L9–44 · Estado componentes + pendientes del hotel (emails Mr. Diego y RRHH)

## Arquitectura / flujo general
`CLAUDE.md` L13–36 · Diagrama del chain: ManyChat → Webhook → Redis → AI Agent → ManyChat

## Credenciales n8n
`CLAUDE.md` L55–67

| Nombre | ID | Uso |
|---|---|---|
| HOTELS (MongoDB) | `Msw0gTK8f8b192VX` | users, chat_histories, KB vectors |
| ITZANA (OpenAI) | `PjPavWO5j0jIFtSG` | Audio Whisper, imagen GPT-4o |
| ITZANA-KAANA (OpenRouter) | `J9zb84vhqsx182XW` | Agente principal claude-opus-4.5 |
| Redis GarooVPS | `8EUkwaZixjCH7szY` | Batching mensajes |
| ManyChat Garoo | `aEvHbFXnmwofChqs` | Enviar respuestas |
| Gmail Soporte Garoo | `H8Qx7NlrthXmHUiy` | Emails escalamiento |
| Vectorizer KB | `LtzIKoi61tZvaeua` | Embeddings vectorización + búsqueda |

## Expresiones n8n
`CLAUDE.md` L87–95 · `={{ expr }}` puro · `=texto {{ campo }}` template · Code nodes sin `{{ }}`

---

## KB — 36 chunks por categoría
`KBs/KB_ITZANA.json` · Script: `search_context.ps1 -topic kb`

| Categoría | IDs |
|---|---|
| resort (2) | `itz_resort_general`, `itz_amenidades_resort` |
| alojamientos (10) | `itz_alojamiento_overview`, `itz_villa_1dorm`, `itz_villa_2dorm`, `itz_villa_3dorm`, `itz_servicios_villa`, `itz_penthouse_2hab`, `itz_penthouse_3hab`, `itz_beachfront_suite`, `itz_deluxe_room`, `itz_precios_reservas` |
| restaurantes (4) | `itz_restaurante_limilia`, `itz_restaurante_nadu`, `itz_bares_y_lounges`, `itz_horarios_fb` |
| actividades (5) | `itz_actividades_overview`, `itz_marina`, `itz_spa`, `itz_paquetes_promociones`, `itz_equipos_gratuitos` |
| bodas_eventos (5) | `itz_bodas_eventos_overview`, `itz_bodas_espacios`, `itz_bodas_catering`, `itz_bodas_open_bar`, `itz_bodas_contacto` |
| ubicacion_logistica (3) | `itz_ubicacion`, `itz_como_llegar`, `itz_transporte_local` |
| contacto (1) | `itz_contacto_general` |
| politicas_faq (6) | `itz_empleo`, `itz_colaboraciones_pr`, `itz_mascotas`, `itz_all_inclusive`, `itz_wifi`, `itz_politicas_generales`, `itz_gimnasio_sostenibilidad` |

**Actualizar KB:** editar `KBs/KB_ITZANA.json` → re-ejecutar `workflows/Itzana_Vectorizar_KB.json` en n8n

---

## Workflows — nodos por archivo
Script: `search_context.ps1 -topic workflow -name <nombre>`

**PRINCIPAL.json** (orquestador) — IDs de workflows: PRINCIPAL (main)
`Webhook → Create Body → PARSE BODY → ES ARCHIVO → [HTTP Request → ES AUDIO/IMAGEN → TRANSCRIBE AUDIO/ANALIZA IMAGEN] → [text/audio/image input] → Merge → Sort → Aggregate → INPUT FINAL → SAVE MESSAGE → Wait → GET MESSAGE → Filter1 → JOINNING MESSAGE → DELETE MESSAGES → Set Propiedad → Find User → If USER NOT EXIST → DATA to CREATE/UPDATE → Insert/Update User → User Data → AI Agent → Parse Agent Output → Parameter Type → Send to ManyChat`
Sub-nodos AI Agent: `OpenRouter Chat Model` · `MongoDB Chat Memory` · `Call 'ITZ KB_SEARCH'` · `notifications`

**Itzana_KB_Search.json** — ID: `rofQe6ZGW3OpFqcb`
`START → Search Context → Knowledge Base → Format Context → GENERAL AGENT → RESPONSE`
Sub-nodos: `Embeddings OpenAI` (ai_embedding) · `OpenAI Chat Model` (ai_languageModel)

**Itzana_Notifications.json** — ID: `OApztbIN8Jhb4JHz`
`START → Set Context → Switch Categoria → [Email Bodas/Eventos | Email PR | Email Empleo | Email Escalamiento | Email Reserva] → Send a message (Gmail)`
⚠️ Todos los sendTo = jorge.calderon@garooinc.com hasta recibir emails reales del hotel

**Itzana_Vectorizar_KB.json** (ejecutar una sola vez al actualizar KB)
`Manual Trigger → LISTA de CHUNKS → Split Out → MongoDB Atlas Vector Store CHUNKS`
Sub-nodos: `Default Data Loader` · `Embeddings OpenAI`

---

## Próxima fase — E-Concierge in-stay
`docs/E-Concierge Itzana.md` · Spec completa: tareas operativas, routing por departamento, estados, SLA
**No construido aún.** Empieza después de estabilizar Kaan en producción.

## PRD / visión del producto
`Flowchart.md` secciones 06–07 · 3 fases: KB+enlaces → Opera nativo → Canvas conversacional

---

## Skills disponibles
| Skill | Cuándo usarlo |
|---|---|
| `n8n-workflow-patterns` | Antes de diseñar nuevos workflows o patrones |
| `deep-research` | Investigar APIs externas (ManyChat, Opera/OHIP, pasarelas de pago) |
| `code-review` | Al modificar nodos Code JavaScript en n8n |
