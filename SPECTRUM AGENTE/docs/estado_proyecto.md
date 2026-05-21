# 🏢 SPECTRUM VIVIENDA: Agente Unificado — Estado del Proyecto
> Última actualización: 2026-05-20 (Fix consulta_pendiente + Fix RSVP por proyecto + Fix proyecto_interes fase 2 WhatsApp)

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
**Estado: ✅ Activo — Robustez de Expresiones + Mejora Inteligencia de Context** | Última mod: 2026-05-19

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

### 2. 👤 Captador de Leads — `Lead Collector.json`
**Estado: ✅ Activo** | Última mod: 2026-05-13

- ✅ **Completado**: Implementación de controles defensivos para inputs nulos en la lógica de nombres.
- ✅ **Completado**: Recepción y persistencia de `page_id` en MongoDB.
- ✅ **Completado**: **Split inteligente de nombre** — Lead Agent extrae `primer_nombre` y `apellidos` por separado. Se persisten en MongoDB y se usan directamente en el XML SOAP (`_Nombre`, `_Apellido`), resolviendo apellidos compuestos y combinaciones de 2 nombres + 2 apellidos.

### 3. 📚 Experto en Proyectos — `KB SEARCH.json`
**Estado: ✅ Activo y Auditado al 100%** | Última mod: 2026-05-13

- ✅ **Completado**: Inclusión de todos los proyectos activos (PVV, PMAR, PPO, PPOL, PSB).

### 4. 🔔 Notificaciones y Citas — `Notifications Master.json` & `RSVP.json`
**Estado: ✅ Activo** | Última mod: 2026-05-20

- ✅ **Completado**: Agregado `aduarte@spectrum.com.gt` (Andy Duarte) como destinatario CC en los 4 tipos de alerta: Nuevo Lead, Interés en Precios, Nueva Cita y Escalación.
- ✅ **Completado**: **Template premium de citas:** `Payload Cita` actualizado con diseño profesional (header oscuro SPECTRUM VIVIENDA, tablas de datos del lead y detalles de cita) — paridad con el template de `RSVP.json`.
- ✅ **Completado (2026-05-19)**: **Reformateo de RSVP.json:** Aplicado estándar de indentación de 2 espacios, reorganización visual de nodos y IDs para mejorar legibilidad y mantenibilidad futura.
- ✅ **Completado (2026-05-20)**: **Fix `Find Appointment` por proyecto:** Query de búsqueda ahora filtra por `manychat_id` + `proyecto`. Antes solo filtraba por `manychat_id`, lo que causaba que un usuario con citas en múltiples proyectos sobreescribiera la cita anterior.
- ⏳ **Pendiente**: Limpiar campos `metodo_contacto_pref` y `estado_civil` de nodos `Insert/Update Appointment Data` — el agente nunca los recolecta, siempre llegan `null`.
- ⏳ **Pendiente**: `sendTo` dinámico — los correos de notificación de citas están hardcodeados en el nodo `CONTEXT`. Mover a `manychat_settings` en MongoDB.
- ⏳ **Pendiente**: Limpiar `chat_histories_rsvp` tras `cita_confirmada: true` para evitar que el agente arranque con contexto de citas anteriores al reagendar.

### 5. 🎞️ Envío de Media — `Send Media.json`
**Estado: ✅ Activo y Auditado al 100%** | Última mod: 2026-05-13

- ✅ **Completado**: URLs de prueba (`link-de-prueba.com`) reemplazadas por `null` en los 5 proyectos. Solo PVV/amenidades tiene URL real activa.
- ✅ **Completado**: Lógica de fallback para media no disponible — nodo `IF Media Disponible` bifurca el flujo: si no hay URL, el agente ofrece al usuario 3 alternativas (asesor personal, visita a sala de ventas, llamada).
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

## 🚀 Punto Actual del Proyecto (2026-05-21)

 Tras las optimizaciones recientes y los fixes de robustez del 19 de mayo, el sistema presenta el siguiente estatus técnico:
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
- **Auditoría de Referencias (2026-05-21):** Validación completa de flujos reveló 0 problemas:
  - ✅ Todos los nodos referenciados existen
  - ✅ Campos enviados coinciden exactamente con los esperados
  - ✅ No hay referencias circulares ni campos huérfanos
  - ✅ Arquitectura de notificaciones es SEGURA y ROBUSTA

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
