# SPECTRUM VIVIENDA: Agente Unificado — Estado del Proyecto
> Última actualización: 2026-06-08 · Fuente de verdad: servidor n8n `agentsprod.redtec.ai`. Los JSON locales son copias manuales.

## Stack Tecnológico

| Componente | Detalle |
|---|---|
| **Orquestación** | n8n — workflows modulares vía `Execute Workflow` |
| **Modelos IA** | `gpt-5-mini` (Orquestador), `gpt-4.1-mini` (Tools), OpenRouter (Analytics/RSVP/KB) |
| **Base de Datos** | MongoDB Atlas — DB `Centralizado` |
| **Vector Search** | Atlas Vector Index `spectrum_vector_index` — filtrado por `proyecto` (UPPERCASE) |
| **Buffer/Cache** | Redis — Message Debouncing 10s |
| **CRM** | Dynamics 365 vía SOAP (`Service.asmx`) |
| **Canales** | ManyChat × 6 páginas (PVV, PMAR, PPO, PPOL, PSB + GAROO) |
| **MCP** | n8n MCP Server en `/mcp-server/http` — registrado en Claude Code (user scope) |

---

## Workflows — Estado actual

### 1. AGENT PRINCIPAL (`iXaptKTUXaXrP7aF`) — 76 nodos ✅ Activo

Orquestador central. Clasifica intención, aplica gate de validación obligatoria (name+email+phone antes de cualquier tool excepto `lead_collector`), enruta a sub-workflows.

**Comportamiento actual:**
- Multitenant: resuelve `proyecto` por `page_id` (IG/Messenger) o Regla de Oro (WhatsApp)
- WhatsApp con `custom_fields.proyecto_interes` pre-seteado (Fase 2) → omite Regla de Oro
- Leads Fase 2 (`fase_2: true`) no reciben saludo genérico
- Bloquea autodetección de campaña en WhatsApp para calificación manual
- Detecta `interes_precios` → dispara notificación a equipo
- Detecta audio/imagen → transcribe/analiza antes de procesar

**Pendientes:**
- ⏳ Ninguno activo

---

### 2. Lead Collector (`SHPFhvoal7k1Rqf9`) — 16 nodos ✅ Activo

Único tool invocable antes del gate. Captura name/email/phone, split LLM de `primer_nombre`/`apellidos`, persiste en MongoDB, registra en CRM vía SOAP al momento.

---

### 3. KB SEARCH (`D3LKuNi6CmMIdvzg`) — 8 nodos ✅ Activo

RAG sobre Atlas Vector Index. Filtra por `proyecto` (UPPERCASE). Retornado actualizado en servidor: 2026-06-04.

**KBs fuente:**

| Archivo | Código | Estado |
|---|---|---|
| `KBs/KB PVV.json` | `PVV` | Entrega Nov 2026. Jardín agotado. ⚠️ **Pendiente re-vectorizar** (cambios 2026-06-08 + 2026-06-09) |
| `KBs/KB PMAR.json` | `PMAR` | Único proyecto con tráfico aprobado. ⚠️ **Pendiente re-vectorizar** (cambios 2026-06-09) |
| `KBs/KB PPO.json` | `PPO` | Entrega Dic 2026. ⚠️ **Pendiente re-vectorizar** (cambios 2026-06-09) |
| `KBs/KB PPOL.json` | `PPOL` | Sin tráfico activo. ⚠️ **Pendiente re-vectorizar** (cambios 2026-06-09) |
| `KBs/KB PSB.json` | `PSB` | Sin tráfico activo. ⚠️ **Pendiente re-vectorizar** (cambios 2026-06-09) |

> ⚠️ Después de editar un KB, correr workflow `LLiVnT0M6xvDKive` en n8n para re-vectorizar.

---

### 4. RSVP (`TjFPzHs5aimxILH7`) — 23 nodos ✅ Activo

Agenda citas (presencial/virtual/llamada). Actualizado en servidor: 2026-06-06.

**Comportamiento actual:**
- Persistencia progresiva: crea appointment al elegir tipo, actualiza en cada turno
- Guard: `_FechaCita`/`_TipoCita` solo van al CRM cuando hay tipo + fecha
- Sin restricción de horario laboral (intencional)
- `medio_llamada`: asume teléfono, registra whatsapp solo si el lead lo menciona
- Múltiples opciones de horario → toma la primera; rangos → toma el inicio

**Pendientes intencionales (esperando instrucción de Spectrum):**
- ⏳ `metodo_contacto_pref` y `estado_civil` — dead code hasta que Spectrum solicite
- ⏳ Limpiar `chat_histories_rsvp` tras `cita_confirmada: true`
- ⏳ `sendTo` dinámico — correos de cita hardcodeados en nodo `CONTEXT`

---

### 5. Send Media (`NtTiyrNy2LHimE7u`) — 6 nodos ✅ Activo

Brochures/renders. Responde positivamente aunque URL sea `null` (siempre ofrece asesor).

**Pendiente:**
- ⏳ Reemplazar `null` con URLs reales cuando Dayrin entregue archivos por proyecto (solo PVV/amenidades tiene URL activa)

---

### 6. Sync_CRM (`TTVNRX38pPoPmK2X`) — 32 nodos ✅ Activo

Scheduled (~15 min). Sincroniza leads idle con Dynamics 365 SOAP. Actualizado en servidor: 2026-06-03.

**Comportamiento actual:**
- Leads Fase 1: envía todos los campos de atribución
- Leads Fase 2 (`fase_2: true`): omite `_OrigenCliente`, `_UTMSource`, `_UTMCampaing`, `_MetodocontactoPref`
- `_FechaCita`/`_TipoCita`: guard — solo si appointment tiene tipo + fecha
- `Campos Usuario`: tiene `continueOnFail: true` (robustez añadida en servidor)
- `_Comentarios`: solo en Lead Collector (no en Sync_CRM)

**Pendiente:**
- ⏳ QA con Andy: confirmar que `_UTMCampaing` se refleja correctamente y leads Fase 2 no reciben sobrescritura de atribución

---

### 7. Notifications Master (`r1Jf5vwrkBrT4dEu`) — 10 nodos ✅ Activo

Emails HTML para 4 tipos de alerta. Actualizado en servidor: 2026-06-08.

**Destinatarios actuales (estado en n8n):**

| Alerta | `sendTo` |
|---|---|
| Nuevo Lead | `jorge.menzel@garooinc.com`, `fernando.ortiz@garooinc.com` |
| Interés Precios | `jorge.menzel@garooinc.com`, `fernando.ortiz@garooinc.com` |
| Nueva Cita | `jorge.menzel`, `hpalma`, `vramirez`, `lrivas`, `dmartinez`, `aduarte` @spectrum, `fernando.ortiz@garooinc.com` |
| Escalación | *(vacío — no llega a nadie)* |

---

### 8. Vectorizar KBs (`LLiVnT0M6xvDKive`) — 6 nodos ✅ Activo (ejecución manual)

Ingesta `KBs/*.json` al vector store. Actualizado en servidor: 2026-06-08.

---

### 9. Analytics Centralizado (`0QfOxWdE9m07laqd`) — 18 nodos ✅ Activo

Pipeline diario. Analiza conversaciones → persiste `emotion_detectada`, `palabra_clave`, `resumen_breve` en `users`. Actualizado en servidor: 2026-05-25.

---

### 10. WEB FORM — 6 nodos 🟡 No desplegado

Webhook `POST /webform` → inserta en `appointments_website` + Gmail a `jorge.calderon@garooinc.com`.

- ⏳ Definir destinatarios finales (falta Andy/equipo Spectrum)
- ⏳ Validación de campos requeridos
- ⏳ Subir a n8n (sin ID remoto)
- ⏳ Coordinar con Tribal para formulario actualizado

---

### 11. LEAD FASE 2 — 1 nodo 🟡 Scaffold

Solo webhook. Sin lógica.

- ⏳ Definir alcance (nutrición/retargeting)
- ⏳ Implementar y subir a n8n

---

## Infraestructura Multitenant

| Cuenta | `page_id` | `proyecto` | Tráfico aprobado |
|---|---|---|---|
| PVV | `113631858496836` | `PVV` | ⏳ Pendiente |
| PMAR | `576411852216119` | `PMAR` | ✅ Aprobado |
| PPO | `113179411695050` | `PPO` | ⏳ Pendiente |
| PPOL | `605454969327692` | `PPOL` | ✅ Aprobado |
| PSB | `497971190077209` | `PSB` | ✅ Aprobado |
| GAROO | `962079940550460` | — | N/A (interno) |

---

## Pendientes activos

### 🔴 Urgente

_(Sin pendientes urgentes al 2026-06-08)_

### 🟡 Corto plazo (bloqueados por terceros)

| # | Tarea | Bloqueante |
|---|---|---|
| 1 | **URLs media** en `Send Media.json` — llenar `null` con URLs reales | Dayrin entregue archivos |
| 2 | **WEB FORM** — deploy + destinatarios finales | Tribal entregue form actualizado |
| 3 | **Templates prellenados por fuente** (QR/web/anuncios) | Dayrin embebe URLs; Normita genera QRs |

### 🟢 Mediano plazo

| # | Tarea | Notas |
|---|---|---|
| 4 | **spectrum-sim-mcp** — rol `readWrite` en Atlas para `jcalderon900610_db_user` sobre DB `Centralizado`; luego smoke test E2E | Bloqueado por Atlas permissions |
| 5 | **Tester Web** (`tester/`) — plan en `docs/plan_spectrum_tester.md` | No iniciar hasta confirmación |

### 🔵 Continuo

| Tarea | Responsable |
|---|---|
| QA diario de conversaciones | Andy |
| Monitoreo `analytics_logs` | Jorge |

---

## Equipo

| Persona | Rol |
|---|---|
| **Harim** | Director — aprobaciones de tráfico y estrategia |
| **Jorge** | Implementación técnica — chatbot, workflows, integraciones |
| **Andy Duarte** (`aduarte@spectrum.com.gt`) | QA + administración CRM |
| **Dayrin** | Marketing — URLs de campañas |
| **Normita** | Operaciones — QR codes |
| **Tribal** | Agencia — formulario web, integración Zapier |
| **Fernando Ortiz** (`fernando.ortiz@garooinc.com`) | GAROO — recibe alertas Nuevo Lead / Precios |
