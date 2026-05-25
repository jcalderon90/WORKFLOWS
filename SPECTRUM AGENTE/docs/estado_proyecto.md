# 🏢 SPECTRUM VIVIENDA: Agente Unificado — Estado del Proyecto
> Última actualización: 2026-05-24 (Fix notificación de llamada + zona horaria GT + categoría unificada llamada teléfono/WhatsApp)

## 🎯 Objetivo General
Arquitectura de agente conversacional modular para SPECTRUM VIVIENDA. Un orquestador central (*Sof-IA*) delega tareas a sub-workflows especializados (Tools), con persistencia centralizada en MongoDB y sincronización diferida al CRM Dynamics 365 vía SOAP.

---

## 🛠️ Stack Tecnológico

| Componente | Detalle |
|---|---|
| **Orquestación** | n8n — workflows modulares vinculados via `Execute Workflow` |
| **Modelos IA** | `gpt-5-mini` (Orquestador), `gpt-4.1-mini` (Tools), `gpt-4o-mini` (Auditoría) |
| **Base de Datos** | MongoDB Atlas — colecciones `users`, `appointments`, `chat_histories`, `quality_logs`, `manychat_settings`, `analytics_logs` |
| **Vector Search** | MongoDB Atlas Vector Index (`spectrum_vector_index`) — Filtrado por proyecto |
| **Buffer/Cache** | Redis — Message Debouncing (agrupa mensajes rápidos) |
| **CRM** | Dynamics 365 via SOAP (Standardized Mappings) |
| **Canales** | ManyChat (6 cuentas: PVV, PMAR, PPO, PPOL, PSB + GAROO) |

---

## 📦 Módulos (Workflows)

### 1. 🧠 Orquestador Central — `AGENT PRINCIPAL.json`
**Estado: ✅ Activo — Conversión + Material Visual + Urgencia Entrega 2026 + Validación Imperativa de Datos** | Última mod: 2026-05-22

- ✅ **Completado**: Sincronización paramétrica con servidor (expresiones =URL y variables de input).
- ✅ **Completado**: Búsqueda de usuarios segmentada por `manychat_id` + `page_id`.
- ✅ **Completado**: Reemplazo de nodos nativos por `httpRequest` usando `setCustomFieldByName`.
- ✅ **Completado**: Asignación dinámica de proyecto por `page_id` para Instagram/Messenger.
- ✅ **Completado**: "Regla de Oro" (pregunta de proyecto) solo se aplica en WhatsApp — corregido en system prompt + `manychat_settings` MongoDB.
- ✅ **Completado**: Nodo `CONTEXT 1` prioriza `Get Account Credentials → proyecto` para canales no-WhatsApp.
- ✅ **Completado**: Fix bug Instagram/Messenger — bot ya no pregunta "¿cuál proyecto?" cuando el canal pre-asigna el proyecto.
- ✅ **Completado**: **Optimización de Conversión (Hot Leads):** Se eliminó el saludo genérico para mensajes de alta intención, delegando inmediatamente al `lead_collector` para acelerar el embudo.
- ✅ **Completado**: **Auditoría de atribución:** `DATA to CREATE` corregido — campo renombrado de `tag_medio` → `atribucion_tag` (consistente con `Sync_CRM` y `Lead Collector`).
- ✅ **Completado**: **Persistencia de atribución en leads recurrentes:** `DATA to UPDATE` ahora incluye `atribucion_tag`, `atribucion_medio`, `atribucion_contacto` y `utm_source_crm`.
- ✅ **Completado**: **Alerta de interés en precios:** Extractor `Lenguaje & Asesoria` detecta `interes_precios` (boolean). Nodo `IF INTERES PRECIOS` + `'Notifications Master' Interés Precios` cableados tras `Insert Analytics`.
- ✅ **Completado**: **Fix Integridad Notificaciones:** Corregido bug de correo faltante en alerta de precios y robustez añadida mediante lógica de coalesce (Parse vs DB) en todos los disparadores de alertas.
- ✅ **Completado**: **Bloqueo de Autodetección en WhatsApp (Final):** Se refactorizaron los nodos `DATA to CREATE` y `DATA to UPDATE` para ignorar la campaña detectada por texto si el canal es WhatsApp. Esto garantiza que el lead sea calificado manualmente por el bot antes de ser asignado a un proyecto.
- ✅ **Completado**: **Resolución de Error de Ruteo n8n:** Solucionado el error `"No path back to referenced node"` en la rama de creación de usuarios, asegurando que las referencias de nodos en expresiones JSON sean accesibles desde cualquier camino de ejecución.
- ✅ **Completado (2026-05-19)**: **Normalización de Sintaxis Segura:** Actualizada toda la expresión de nodos `.item.json` → `.first().json`. Esto mejora la robustez cuando hay múltiples items en la salida de un nodo. Afecta a: `RESPOND TO MANYCHAT`, `Parameter Type`, `User Data`, `If NO WHATSAPP`, `Proyecto`, `Lenguaje & Asesoria`.
- ✅ **Completado (2026-05-19)**: **Mejora Detector `es_fuera_de_contexto`:** Reescrito completamente el atributo en el extractor `Lenguaje & Asesoria`. Ahora es mucho más específico: solo marca mensajes como "fuera de contexto" si son solicitudes EXPLÍCITAS y ESPECÍFICAS de temas completamente ajenos al sector inmobiliario. Nunca marca saludos, mensajes cortos, confirmaciones simples o temas ambiguos/relacionados con vivienda. Esto reduce falsos positivos y mejora la tasa de aceptación de mensajes legítimos.
- ✅ **Completado (2026-05-20)**: **Fix `consulta_pendiente` no se guardaba en MongoDB:** Nodo `Prepare Update` usaba `$json.consulta_pendiente_guardar` pero `$json` en ese punto del flujo solo contenía `{ value: boolean }` del nodo `Hay Cambios?`. Corregido a `$('Parse response').item.json.consulta_pendiente_guardar`. Con esto, cuando el usuario da sus datos después de hacer una consulta, el bot retoma y responde la pregunta original correctamente.
- ✅ **Completado (2026-05-20)**: **Visibilidad de `consulta_pendiente` en LLM:** Agregada línea explícita `Consulta pendiente del lead` al user message del nodo `PRINCIPAL` para mayor prominencia en el contexto del LLM.
- ✅ **Completado (2026-05-20)**: **Fix `proyecto_interes` fase 2 WhatsApp:** Leads de WhatsApp que ya traen `custom_fields.proyecto_interes` definido (fase 2 — campañas con proyecto pre-asignado) ahora son detectados correctamente en `CONTEXT 1`. La expresión del campo `proyecto` en el branch de WhatsApp ahora lee primero `$('PARSE BODY').first().json.current_body.custom_fields.proyecto_interes` antes de intentar extraer el proyecto del mensaje. Resultado: la REGLA DE ORO no se dispara para estos leads, el bot no pregunta "¿en cuál proyecto estás interesado?" y entra directamente al flujo de atención con proyecto activo.
- ✅ **Completado (2026-05-21)**: **Urgencia de Entrega 2026 — Estrategia de Conversión:** `PROJECT LIST` actualizado con ⭐ y año de entrega para PVV (Oct. 2026) y PPO (Dic. 2026). `REGLA DE ORO` actualizada para que Sof-IA mencione SIEMPRE que ambos proyectos entregan en 2026 al presentar opciones al lead.
- ✅ **Completado (2026-05-21)**: **Material Visual — Respuesta siempre positiva:** Descripción de tool `send_media` y `REGLAS ESTRICTAS` actualizadas. Si el cliente pide material visual y no está disponible en el sistema, Sof-IA NUNCA dice que no existe — siempre confirma que sí hay material y que un asesor puede contactarle para enviárselo.
- ✅ **Completado (2026-05-24)**: **Categoría unificada de llamada (teléfono = WhatsApp):** Descripción de la tool `rsvp` en el `systemMessage` del nodo `PRINCIPAL` actualizada para aclarar que "llamada por teléfono" y "llamada por WhatsApp" pertenecen a la misma categoría `llamada`. El orquestador ya no debe abrir flujos distintos ni clasificar una llamada por WhatsApp como `cita_virtual` — siempre delega a `rsvp`, que se encarga de preguntar el medio.

### 2. 👤 Captador de Leads — `Lead Collector.json`
**Estado: ✅ Activo** | Última mod: 2026-05-22

- ✅ **Completado**: Implementación de controles defensivos para inputs nulos en la lógica de nombres.
- ✅ **Completado**: Recepción y persistencia de `page_id` en MongoDB.
- ✅ **Completado**: **Split inteligente de nombre** — Lead Agent extrae `primer_nombre` y `apellidos` por separado. Se persisten en MongoDB y se usan directamente en el XML SOAP (`_Nombre`, `_Apellido`), resolviendo apellidos compuestos y combinaciones de 2 nombres + 2 apellidos.
- ✅ **Completado (2026-05-22)**: **Fix URL SOAP:** Nodo `GENERAR LEAD CONTACT` corregido de `service.asmx` → `Service.asmx` para consistencia con `Sync_CRM.json` y la especificación del endpoint.

### 3. 📚 Experto en Proyectos — `KB SEARCH.json` + KBs
**Estado: ✅ Activo** | Última mod: 2026-05-22

- ✅ **Completado**: Inclusión de todos los proyectos activos (PVV, PMAR, PPO, PPOL, PSB).
- ✅ **Completado (2026-05-21)**: **SerViPagos condicional (PSB, PPOL):** SerViPagos eliminado de las respuestas generales de mantenimiento. Ahora solo aparece cuando el cliente pregunta explícitamente por métodos de pago. Creadas entradas dedicadas `sb_mantenimiento_pago` y `pl_mantenimiento_pago` con tags específicos (`servipagos`, `donde pagar`).
- ✅ **Completado (2026-05-21)**: **Urgencia Entrega 2026 — KBs PVV y PPO:** Actualizados `pvv_resumen_general` y `pp_resumen_general` con nota de urgencia "⭐ ENTREGA ESTE AÑO". Creada nueva entrada `pvv_diferenciadores`. Actualizado `pp_competencia_diferenciadores` para abrir con la entrega 2026 como primer diferenciador.
- ✅ **Completado (2026-05-22)**: **Precios Sotobosque (PSB):** `sb_precio_general` actualizado con tabla completa de precios por modelo (S-40 a S-106). Agregados 7 docs individuales de precio por modelo para mejor matching RAG. KB re-vectorizado.
- ✅ **Completado (2026-05-22)**: **Limpieza precios Polanco (PPOL):** `pl_precio_general` tenía precios de Sotobosque copiados incorrectamente. Reemplazados por mensaje genérico de asesor hasta tener precios reales. KB re-vectorizado.
- ✅ **Completado (2026-05-22)**: **Precio de reserva PSB y PPOL:** `sb_precio_reserva` y `pl_precio_reserva` actualizados con monto Q15,000. Agregados tags de búsqueda semántica. KBs re-vectorizados.
- ✅ **Completado (2026-05-22)**: **Validación Imperativa de Datos del Lead:** Reforzada regla 🔴 VALIDACIÓN OBLIGATORIA PRIMERO en systemMessage de PRINCIPAL. Lead DEBE compartir nombre + correo + teléfono ANTES de cualquier respuesta, sin excepciones. Bloqueado: kb_search, rsvp, material visual. SOLO lead_collector hasta que datos completos. Incidente: Lead respondió consulta sobre Portales sin datos compartidos.
- ⏳ **Pendiente**: Re-vectorizar KB PVV y PPO en n8n (workflow `LLiVnT0M6xvDKive`) para que los cambios del 2026-05-21 surtan efecto en producción.

### 4. 🔔 Notificaciones y Citas — `Notifications Master.json` & `RSVP.json`
**Estado: ✅ Activo — Fix bug llamada + zona horaria + categoría unificada** | Última mod: 2026-05-24

- ✅ **Completado**: Agregado `aduarte@spectrum.com.gt` (Andy Duarte) como destinatario CC en los 4 tipos de alerta: Nuevo Lead, Interés en Precios, Nueva Cita y Escalación.
- ✅ **Completado**: **Template premium de citas:** `Payload Cita` actualizado con diseño profesional (header oscuro SPECTRUM VIVIENDA, tablas de datos del lead y detalles de cita) — paridad con el template de `RSVP.json`.
- ✅ **Completado (2026-05-19)**: **Reformateo de RSVP.json:** Aplicado estándar de indentación de 2 espacios, reorganización visual de nodos y IDs para mejorar legibilidad y mantenibilidad futura.
- ✅ **Completado (2026-05-20)**: **Fix `Find Appointment` por proyecto:** Query de búsqueda ahora filtra por `manychat_id` + `proyecto`. Antes solo filtraba por `manychat_id`, lo que causaba que un usuario con citas en múltiples proyectos sobreescribiera la cita anterior.
- ✅ **Completado (2026-05-24)**: **Eliminada restricción de horario laboral en RSVP:** Removida la validación de "lunes a sábado, 9:00 a 18:00" del system prompt del agente de agendamiento. Ahora solo se rechazan fechas pasadas — el lead puede proponer cualquier horario y el asesor coordina disponibilidad directamente.
- ✅ **Completado (2026-05-24)**: **Fix notificaciones de llamada no se enviaban:** El nodo `IF CONFIRMADA` solo encadena al `Execute Workflow 'Notifications Master' Cita` cuando `cita_confirmada === true`, pero el `systemMessage` del `RSVP Agent` no instruía explícitamente al LLM a setear ese flag al cerrar una `llamada`. Se añadió en el system prompt una regla obligatoria: tras recolectar `horario_preferido` + `medio_llamada` + `intencion_compra`, el agente DEBE marcar `cita_confirmada: true` (con texto que advierte que sin ese flag la notificación NO llega al equipo). Resultado: las llamadas ahora disparan la notificación al asesor.
- ✅ **Completado (2026-05-24)**: **Categoría unificada `llamada` + captura pasiva de `medio_llamada`:** Se documentó explícitamente en el `systemMessage` del `RSVP Agent` que llamada por teléfono y llamada por WhatsApp pertenecen a la MISMA categoría (`tipo_agendamiento: "llamada"`). Nuevo parámetro `medio_llamada` con valores `"telefono"` (default) | `"whatsapp"`. **El agente NO pregunta al cliente cuál medio prefiere** — por defecto se asume llamada telefónica; solo se marca como `"whatsapp"` si el cliente lo menciona espontáneamente. Persistencia añadida en `Insert/Update Appointment Data` (campo `medio_llamada` en MongoDB) y normalizador en `Parse RSVP Output` (acepta variantes como "WhatsApp", "tel", etc.).
- ✅ **Completado (2026-05-24)**: **Fix fecha de cita llegaba 6 horas desfasada en la notificación:** El nodo `HTML` de `RSVP.json` usaba `new Date(fechaIso).toLocaleString('es-GT', { timeZone: 'America/Guatemala' })`, pero el LLM emitía ISO sin offset (`2026-05-25T14:00`), que JS interpreta como UTC — la fecha mostrada quedaba 6h antes. Reemplazado por `luxon.DateTime`: si el ISO no trae offset, se interpreta como Guatemala; si sí lo trae, se convierte a Guatemala. Formato natural en español: `"Lunes 25 de mayo de 2026 a las 2:00 p.m. (hora Guatemala)"`. Además, el `systemMessage` del agente ahora obliga a emitir `fecha_hora` con offset explícito `-06:00`, redundancia que evita el bug de raíz.
- ✅ **Completado (2026-05-24)**: **Notifications Master diferencia cita vs llamada:** El nodo `Payload Cita` ahora usa expresiones condicionales (`$json.datos.tipo_agendamiento === 'llamada' ? ... : ...`) para: asunto del correo (`📞 NUEVA LLAMADA AGENDADA` vs `🗓️ NUEVA CITA REGISTRADA`), header HTML, y sección "Detalles" (para llamada muestra `horario_preferido` + `medio_llamada_label`; para cita muestra `fecha_cita` + `modalidad`). Se mantiene `tipo_alerta: "cita"` en el switch — la bifurcación se hace dentro del payload, sin agregar ramas al workflow.
- ⏳ **Pendiente**: Limpiar campos `metodo_contacto_pref` y `estado_civil` de nodos `Insert/Update Appointment Data` — el agente nunca los recolecta, siempre llegan `null`.
- ⏳ **Pendiente**: `sendTo` dinámico — los correos de notificación de citas están hardcodeados en el nodo `CONTEXT`. Mover a `manychat_settings` en MongoDB.
- ⏳ **Pendiente**: Limpiar `chat_histories_rsvp` tras `cita_confirmada: true` para evitar que el agente arranque con contexto de citas anteriores al reagendar.

### 5. 🎞️ Envío de Media — `Send Media.json`
**Estado: ✅ Activo** | Última mod: 2026-05-21

- ✅ **Completado**: URLs de prueba (`link-de-prueba.com`) reemplazadas por `null` en los 5 proyectos. Solo PVV/amenidades tiene URL real activa.
- ✅ **Completado (2026-05-21)**: **Respuesta positiva cuando no hay media:** Nodo `No Media Response` actualizado — ya no dice "no está disponible". Ahora siempre confirma que sí existe material y que un asesor contactará al usuario por el mismo canal para enviárselo. Elimina fricción negativa en el embudo.
- ⏳ **Pendiente**: Reemplazar `null` con las URLs reales cuando los archivos de brochures/renders/planos estén listos por proyecto.

### 6. 🔄 Sincronizador CRM — `Sync_CRM.json`
**Estado: ✅ Activo** | Última mod: 2026-05-13

- ✅ **Completado**: Homologación con el servidor de la propiedad `temperature: 0.3` en OpenAI.
- ✅ **Completado**: Fix nodo `UPDATE - Proyecto Interes Manychat` — migrado a `setCustomFieldByName`.
- ✅ **Completado**: **Tracking Multicanal:** Implementada lógica para detectar leads provenientes de FB Messenger e Instagram y asignarles por defecto el tag "Social Media" y medio "Redes sociales Orgánico".
- ✅ **Completado**: Mejorar resúmenes para incluir presupuesto, tipo de unidad y requisitos del lead.
- ✅ **Completado**: Poblar campo `_UTMCampaing` con formato `"Cliente atendido desde chatbot a través de [medio]"`.
- ✅ **Completado**: Fix `_Nombre`/`_Apellido` — Body XML usa `primer_nombre`/`apellidos` con fallback al split de `nombre`.
- ⏳ **Pendiente**: **QA Sincronización:** Validar con equipo CRM/Andy que el campo `_UTMCampaing` se está reflejando correctamente en la base de datos de producción con el nuevo formato estricto tras las siguientes ejecuciones.

### 7. 🛠️ Utilidad de Vectorización — `Vectorizar los KBs.json`
**Estado: ✅ Auditado al 100% (ID: LLiVnT0M6xvDKive)** | Última mod: 2026-05-13

- ✅ **Completado**: Verificación de correspondencia con flujo remoto en n8n a través de MCP.

### 8. 🧪 Simulador para IAs externas — `spectrum-sim-mcp/`
**Estado: 🟡 Scaffold listo, parcialmente operativo** | Última mod: 2026-05-24

Servidor MCP en Python que permite a cualquier IA (Claude Desktop/Code, Cursor, Gemini CLI, Continue) **simular conversaciones contra Sof-IA como si fuera un cliente real de ManyChat** y observar el resultado (ejecuciones n8n + estado en Mongo).

- ✅ **Completado**: Scaffold del paquete (`pyproject.toml`, entrypoint `spectrum-sim-mcp`, deps `mcp` + `httpx` + `pymongo` + `python-dotenv`).
- ✅ **Completado**: 8 tools registradas: `send_message`, `new_test_user_id`, `list_workflows`, `list_executions`, `get_execution`, `tail_executions`, `read_user_state`, `reset_user`.
- ✅ **Completado**: `webhook.py` arma el payload tipo ManyChat (`key`, `body.id`, `body.page_id`, `custom_fields`, `last_input_text`, `whatsapp_phone`) idéntico al que recibe `AGENT PRINCIPAL` en producción.
- ✅ **Completado**: `n8n_client.py` con auth `X-N8N-API-KEY`; `list_executions` / `get_execution` / `list_workflows` con manejo de errores y paginación.
- ✅ **Completado**: `tail_executions` (polling con deadline) para capturar la ejecución que un `send_message` acaba de disparar — workaround a la limitación de la API n8n que no filtra por `user_id`.
- ✅ **Completado**: `mongo_client.py` con workaround DNS Google (`8.8.8.8`/`8.8.4.4`) documentado en CLAUDE.md para SRV de Atlas.
- ✅ **Completado**: Guardrails de `reset_user` — exige `MONGO_ALLOW_RESET=true` en `.env` **Y** prefijo `test_` en el `manychat_id`. Doble bloqueo para no tocar leads reales.
- ✅ **Completado**: Tools de Mongo se autoregistran sólo si `MONGO_URI` está configurado; si Atlas cae, las tools devuelven error legible en vez de tumbar el servidor.
- ✅ **Completado**: `WORKFLOW_IDS` mapea nombres amigables → IDs n8n para que el LLM cliente no tenga que memorizarlos (`AGENT PRINCIPAL` → `iXaptKTUXaXrP7aF`, etc.).
- ✅ **Completado**: `.env` configurado con `N8N_API_KEY`, `MONGO_URI`, `MONGO_DB=Centralizado`, `DEFAULT_PAGE_ID=576411852216119` (PMAR), `WEBHOOK_TIMEOUT=35`, `MONGO_ALLOW_RESET=true`.
- ✅ **Completado**: Conectividad Atlas verificada — IP `162.43.188.28` agregada al Network Access del cluster.
- ⏳ **Pendiente / 🔴 Bloqueante**: Otorgar rol `readWrite` sobre la DB `Centralizado` al usuario `jcalderon900610_db_user` en Atlas. Hoy sólo tiene privilegios sobre la DB `Database` (otra del mismo cluster), por lo que `read_user_state` retorna `null` y `reset_user` no borra nada. Atlas devuelve documentos vacíos silenciosamente cuando faltan privilegios (no lanza "not authorized").
- ⏳ **Pendiente**: Registrar el servidor en `~/.claude.json` (`claude mcp add spectrum-sim -s user -- spectrum-sim-mcp`) tras desbloquear los permisos de Mongo.
- ⏳ **Pendiente**: Smoke test end-to-end desde Claude Code — "saluda como cliente nuevo, captura la ejecución y dime qué tools llamó".
- ⏳ **Pendiente**: Tests automatizados (carpeta `tests/` existe pero vacía).
- ⚠️ **Riesgo**: La API key n8n y la URI de Mongo con password fueron pegadas en la conversación durante el setup. Rotar credenciales tras cerrar la fase de validación.
- 📎 **Alternativa paralela**: Se registró también el `mongodb-mcp-server` oficial (npm) en Claude Code, pero falla al iniciar por un bug de npm 11.14.1 (`Invalid Version` al deduplicar `express-rate-limit → ip-address`). No bloquea al servidor custom; queda como vía de respaldo si se requiere acceso Mongo desde Claude Code sin pasar por este simulador.

---

## 🏗️ Infraestructura Multitenant

### Cuentas ManyChat configuradas (`manychat_settings`)

| Cuenta | `page_id` | `proyecto` | Tráfico aprobado |
|---|---|---|---|
| PVV | `113631858496836` | `PVV` | ⏳ Pendiente |
| PMAR | `576411852216119` | `PMAR` | ✅ Aprobado |
| PPO | `113179411695050` | `PPO` | ⏳ Pendiente |
| PPOL | `4901825` | `PPOL` | ⏳ Pendiente |
| PSB | `497971190077209` | `PSB` | ⏳ Pendiente |
| GAROO | `962079940550460` | — | N/A (interno) |

> **Nota:** Solo Parque Mariscal (PMAR) tiene tráfico aprobado al chatbot por decisión de Harim. Sotobosque y Polanco son los próximos en la cola de lanzamiento.

---

## 🚀 Punto Actual del Proyecto (2026-05-24)

Tras las optimizaciones de conversión y limpieza de mensajería del 21 de mayo, el sistema presenta el siguiente estatus técnico:
- **Infraestructura Multitenant:** 100% Funcional. Enrutamiento dinámico por canal activado.
- **WhatsApp Project Enforcement:** Se eliminó la herencia automática de proyecto por texto inicial en WhatsApp. Ahora el sistema deja el campo `proyecto` nulo para forzar al Orquestador a disparar el menú interactivo, mejorando la calidad de la atribución final.
- **Fix Correo Lead:** Todas las notificaciones (`nuevo_lead`, `cita`, `escalacion`, `interes_precios`) ahora incluyen validación de correo lead con fallback robusto.
  - `DATA to CREATE`: `tag_medio` → `atribucion_tag` (bug de mapeo hacia `Sync_CRM`).
  - `DATA to UPDATE`: agregados 4 campos de atribución para leads recurrentes.
  - `Lenguaje & Asesoria` + pipeline `IF INTERES PRECIOS`: notificación de interés comercial activada.
  - `Payload Cita` en `Notifications Master`: template HTML premium implementado.
- **Split inteligente de nombre/apellido:** El Lead Agent extrae `primer_nombre` y `apellidos` por separado vía LLM. Propagado en `Lead Collector`, `AGENT PRINCIPAL` y `Sync_CRM`. Resuelve apellidos compuestos (ej. "García López") y combinaciones de 2 nombres + 2 apellidos en el XML SOAP.
- **Fix URLs rotas Send Media:** URLs placeholder eliminadas, reemplazadas por `null`. IF branching implementado: si no hay archivo disponible, el agente ofrece 3 alternativas al usuario (asesor, cita presencial, llamada).
- **Notificaciones Andy Duarte:** `aduarte@spectrum.com.gt` agregado como destinatario CC en los 4 tipos de alerta del `Notifications Master`.
- **Auditoría MCP Paridad Total:** 100% de paridad local ↔ producción en `agentsprod.redtec.ai`.
- **Reestructuración "AI-Ready":** Repositorio organizado — docs en `/docs`, herramientas en `/scripts`.
- **Integración MCP:** Directorio de IDs y configuraciones MCP en `GEMINI.md`.
- **Población `manychat_settings`:** 6 cuentas registradas con `page_id`, `api_key` y `proyecto`.
- **Routing por canal:** Instagram/Messenger asignan proyecto automáticamente vía `page_id`; WhatsApp mantiene la Regla de Oro interactiva.
- **Bypass de Saludo para Leads Calientes:** Reducción de fricción al detectar interés inmediato, saltando el saludo de Sof-IA y activando extracción de datos directa.
- **Migración a n8n Workflow SDK:** Core workflows (`AGENT PRINCIPAL`, `Lead Collector`, `Sync_CRM`) migrados al formato SDK en producción para mayor robustez, control de versiones y despliegue programático.
- **Fix bug Instagram/Messenger:** Corregidos dos puntos — `manychat_settings` con `proyecto` por `page_id` + system prompt de Sof-IA con condición de canal para la Regla de Oro. Bot ya no pregunta "¿cuál proyecto?" en IG/Messenger.
- **Verificación tareas P1:** Confirmado en código que resúmenes Sync_CRM (Presupuesto, Dormitorios, Requisitos, Resumen, Dudas) y `_UTMCampaing` están completamente implementados.
- **Templates prellenados por fuente:** CSV de URLs entregado por Dayrin. Verificado que `Extraer CAMPAIGN DATA` detecta correctamente los 6 tipos de fuente × 5 proyectos. Parte técnica completa.
- **Robustez de Expresiones (2026-05-19):** Normalización de sintaxis segura en `AGENT PRINCIPAL.json`. Todos los nodos que usaban `.item.json` ahora usan `.first().json` para mayor robustez con múltiples items.
- **Mejora Detector Out-of-Context (2026-05-19):** Completamente reescrito el atributo `es_fuera_de_contexto` en el extractor `Lenguaje & Asesoria`. Ahora diferencia claramente entre solicitudes EXPLÍCITAS y ESPECÍFICAS de temas ajenos al sector vs. saludos, confirmaciones y mensajes ambiguos. Reduce falsos positivos y mejora precisión.
- **Fix consulta_pendiente (2026-05-20):** Resuelto bug crítico donde el bot recolectaba datos del lead pero no respondía la pregunta original. Causa raíz: `$json` en `Prepare Update` perdía el contexto de `Parse response` al pasar por el nodo `Hay Cambios?`. Corregido con referencia explícita al nodo.
- **Fix RSVP por proyecto (2026-05-20):** `Find Appointment` ahora filtra por `manychat_id` + `proyecto`. Evita sobreescritura de citas entre proyectos distintos para el mismo usuario.
- **Fix `proyecto_interes` fase 2 WhatsApp (2026-05-20):** Leads de WhatsApp con `proyecto_interes` ya definido en ManyChat (fase 2) ahora entran directamente al flujo con proyecto activo. El nodo `CONTEXT 1` lee `custom_fields.proyecto_interes` como primera prioridad en el branch de WhatsApp antes de intentar extraer el proyecto del mensaje. La REGLA DE ORO ya no se dispara para estos leads. Auditoría completa confirma que todos los flujos downstream (Lead Collector, KB SEARCH, RSVP, Sync_CRM) funcionan correctamente con este valor pre-seteado.
- **Fix Notificaciones con datos incompletos (2026-05-21):** Corregidas referencias inválidas en nodos de notificaciones:
  - `'Notifications Master' Nuevos Leads`: Removidas referencias a `$json.nombre/telefono/correo` que nunca existían en ese contexto
  - Agregados fallbacks a `$('Prepare Update')` en Nuevos Leads, Precios y Escalación
  - Mejorada robustez de `RSVP.json` con fallbacks en notificación de cita
  - Cadena de fallback ahora es: `Parse response` → `Prepare Update` → `User Data` → valor por defecto
  - **Resultado:** Garantiza que datos del lead se envíen correctamente incluso si faltan en nodos intermedios
- **Auditoría de Referencias (2026-05-21 mañana):** Validación completa de flujos reveló 0 problemas:
  - ✅ Todos los nodos referenciados existen
  - ✅ Campos enviados coinciden exactamente con los esperados
  - ✅ No hay referencias circulares ni campos huérfanos
  - ✅ Arquitectura de notificaciones es SEGURA y ROBUSTA
- **SerViPagos condicional (2026-05-21):** KB PSB y PPOL corregidas. SerViPagos ya no se menciona proactivamente en respuestas de mantenimiento — solo aparece si el lead pregunta explícitamente por métodos de pago.
- **Estrategia de Conversión — Urgencia 2026 (2026-05-21):** Sistema completo de señalización de urgencia implementado en 3 capas: (1) PROJECT LIST con ⭐ y año de entrega, (2) REGLA DE ORO instruye a Sof-IA mencionar PVV/PPO como entrega este año, (3) KBs de PVV y PPO actualizadas con lenguaje de urgencia y entradas de diferenciadores.
- **Material Visual — Experiencia positiva (2026-05-21):** Send Media y AGENT PRINCIPAL alineados. El sistema nunca niega existencia de material visual — siempre ofrece la alternativa de asesor que lo enviará.
- **Precios Sotobosque y limpieza Polanco (2026-05-22):** KB PSB actualizada con precios reales por modelo (S-40 a S-106) y precio de reserva Q15,000. KB PPOL corregida — precios de Sotobosque que estaban asignados incorrectamente fueron removidos. Ambos KBs re-vectorizados.
- **Fix URL SOAP Lead Collector (2026-05-22):** Endpoint corregido de `service.asmx` → `Service.asmx` para consistencia con Sync_CRM y la especificación oficial.
- **RSVP sin restricción de horario (2026-05-24):** Eliminada la validación de horario laboral (lunes-sábado 9:00-18:00) del agente RSVP. El lead puede proponer cualquier horario; el asesor coordina disponibilidad. Solo se sigue rechazando fechas pasadas.
- **Servidor MCP de simulación `spectrum-sim-mcp` (2026-05-24):** Scaffold completo en Python con 8 tools que permiten a cualquier IA externa (Claude/Gemini/Cursor) hablar con Sof-IA como cliente ManyChat y leer el resultado (ejecuciones n8n + estado Mongo). Tools de n8n (webhook, list/get/tail executions) operativas. Tools de Mongo (`read_user_state`, `reset_user`) implementadas con guardrails (`MONGO_ALLOW_RESET` + prefijo `test_`) pero bloqueadas hasta que se otorgue `readWrite` sobre la DB `Centralizado` al usuario `jcalderon900610_db_user` en Atlas. Falta registrar el servidor en `~/.claude.json` y smoke test end-to-end.

---

## 🔜 Próximos Pasos (Post-reunión 2026-05-13)

### 🔴 P1 — Inmediato ✅ Cerrado

| # | Tarea | Responsable | Estado |
|---|---|---|---|
| 1 | **Mejorar resúmenes Sync_CRM** — Incluir presupuesto, tipo de unidad, requisitos | Jorge | ✅ Completado |
| 2 | **Mapeo UTM Campaign** — Poblar `_UTMCampaing` con `"Cliente atendido desde chatbot a través de [medio]"` | Jorge | ✅ Completado |
| 3 | **Fix canal Instagram/Messenger** — Bot no debe preguntar proyecto en IG/Messenger | Jorge | ✅ Completado |

### 🟡 P2 — Corto plazo (1-2 semanas)

| # | Tarea | Responsable | Bloqueante |
|---|---|---|---|
| 3 | **Webhook formulario citas web** — Endpoint para recibir datos de cita desde Tribal | Jorge + Tribal | Tribal entregue form actualizado |
| 4 | **Templates prellenados por fuente** — Textos específicos para QR/web/anuncios | Jorge + Dayrin + Normita | ✅ Técnico completo. Pendiente: Dayrin embebe URLs en materiales, Normita genera QR codes |
| 5 | **URLs media por proyecto** — Subir brochures/renders/planos y llenar `null` en `Send Media.json` | Jorge + Dayrin | Archivos listos por proyecto |
| 6 | **Lanzamiento Sotobosque/Polanco** — Activar routing cuando Harim apruebe | Jorge + Harim | Aprobación de tráfico |

### 🟢 P3 — Mediano plazo (2-4 semanas)

| # | Tarea | Responsable | Bloqueante |
|---|---|---|---|
| 6 | **Investigar Zapier → CRM** — Evaluar como alternativa al SOAP web service | Jorge + Tribal | Sesión de capacitación Tribal |
| 7 | **Auditoría campos CRM** — Crear campos dedicados (presupuesto, tipo unidad, etc.) | Andy + Jorge | Resultado investigación Zapier |

### 🔵 P4 — Continuo

| # | Tarea | Responsable |
|---|---|---|
| 8 | **QA diario de conversaciones** — Andy revisa calidad y datos al CRM | Andy |
| 9 | **Monitoreo `analytics_logs`** — Tiempos de respuesta y acciones del orquestador | Jorge |

---

## 👥 Equipo

| Persona | Rol |
|---|---|
| **Harim** | Director del proyecto — aprobaciones de tráfico y estrategia |
| **Jorge** | Implementación técnica — chatbot, workflows, integraciones |
| **Andy Duarte** (`aduarte@spectrum.com.gt`) | QA + administración CRM — crea campos, revisa conversaciones, recibe todas las alertas del chatbot |
| **Dayrin** | Marketing — URLs de campañas, contenido |
| **Normita** | Operaciones — generación de QR codes |
| **Tribal** | Agencia — formulario web, integración Zapier |

---
