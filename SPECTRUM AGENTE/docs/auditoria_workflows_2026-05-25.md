# Auditoría de Workflows — Estado 2026-05-25

## Resumen ejecutivo

Auditoría completa de los 8 workflows del Agente Unificado. **4 hallazgos críticos corregidos**. **14 hallazgos medios-bajos pendientes para sesión posterior**.

---

## ✅ CORREGIDO — Commit b4a13f4

### 1. Campos de atribución faltantes (CRÍTICO)

| Flujo | Campo faltante | Estado |
|---|---|---|
| `DATA to CREATE` | `atribucion_medio`, `atribucion_contacto` | ✅ Agregados |
| `DATA to CREATE FASE 2` | Todos (tag, medio, contacto, utm_source) | ✅ Agregados |

**Impacto:** Nuevos leads en Fase 2 ahora sincronizarán con CRM con datos de atribución completos.

---

### 2. Expresiones n8n críticas (CRÍTICO)

| Nodo | Problema | Solución | Archivo |
|---|---|---|---|
| `HTTP IF AUDIO` | `.item.json` en URL | → `.first().json` | AGENT PRINCIPAL |
| `PRINCIPAL` (systemMessage) | `.item.json` en Tel_sistema | → `.first().json` | AGENT PRINCIPAL |
| `Prepare Update` (×2) | `.item.json` en consulta_pendiente | → `.first().json` | AGENT PRINCIPAL |
| `ID - Lead en Fase 2` | `.item.json` en _id | → `.first().json` | AGENT PRINCIPAL |
| `DATA to CREATE FASE 2` | `.item.json` en manychat_id | → `.first().json` | AGENT PRINCIPAL |

**Impacto:** Evita fallos de ejecución cuando upstream devuelve múltiples ítems.

---

### 3. Teléfono sin código de país (ALTO)

| Campo | Problema | Solución | Archivo |
|---|---|---|---|
| `_TelefonoMovil` (Sync_CRM) | Sin `+502` | Concatenación defensiva: si no empieza con +502, agrega | Sync_CRM |

**Impacto:** Números sin prefijo país ahora se envían correctamente al CRM.

---

### 4. Documentación desactualizada (BAJO)

| Punto | Problema | Solución |
|---|---|---|
| `manychat_settings` en MongoDB | Mencionaba "notification recipients" | Aclarado: no existen, son hardcodeados |
| `Notifications Master.json` | No documentaba que destinatarios son fijos | Agregada nota: "Recipients hardcoded; not configurable per-page" |

---

## ✅ VERIFICADO — Todo correcto

### Reglas de validación
- ✅ "🔴 VALIDACIÓN OBLIGATORIA PRIMERO" en PRINCIPAL — intacta y correcta
- ✅ No se encontró campo obsoleto `tag_medio`

### Integraciones SOAP
- ✅ Endpoint: `Service.asmx` (S mayúscula)
- ✅ SOAPAction: `CreacionClientePotencialBot`
- ✅ Typos intencionales: `_CorreEletronico`, `_UTMCampaing` — presentes
- ✅ `_Apellido` con fallback `"N/A"`
- ✅ `_OrigenCliente` = `100000001`
- ✅ `_MetodocontactoPref` usa valores 2–5

### Workflows de soporte
- ✅ **Lead Collector**: persistencia MongoDB correcta, split LLM de nombre funciona, validación de datos completa
- ✅ **KB SEARCH**: filtra por proyecto (aunque sin normalización `.toUpperCase()` defensiva)
- ✅ **RSVP**: escribe a `appointments` correctamente, sin validación de horario comercial (intencional)
- ✅ **Send Media**: responde positivamente si URL es null
- ✅ **Notifications Master**: envía HTML, maneja 4 tipos, destinatarios hardcodeados (intencional)

### Persistencia MongoDB
- ✅ Filtro `conversation_analysis: false` + 15 min inactividad en Sync_CRM
- ✅ Flag `conversation_analysis: true` post-sync
- ✅ Colecciones correctas: `users`, `appointments`, `chat_histories`, etc.

### `setCustomFieldByName` ManyChat
- ✅ Ambos usos en PRINCIPAL van por httpRequest (no nodos legados)

---

## ⏳ PENDIENTE — Retomar sesión posterior

### Paso 3 — `.item.json` → `.first().json` en flujos de soporte (MEDIO)

**Por qué:** Técnicamente prohibido por CLAUDE.md. Riesgo real si nodos upstream devuelven múltiples ítems.

| Flujo | Ocurrencias | Prioridad |
|---|---|---|
| `Lead Collector.json` | ~15 | Media (nodos Code pueden traer múltiples items) |
| `RSVP.json` | ~12 | Alta (Find Appointment puede devolver múltiples docs) |
| `KB SEARCH.json` | 4 | Baja |
| `Send Media.json` | 8 | Baja |
| `Sync_CRM.json` | Masivo (~30+) | Alta (Loop procesa batch de usuarios) |

**Estimación:** ~1 hora para todos los reemplazos.

---

### Mejoras defensivas no críticas

| Flujo | Mejora | Razón | Prioridad |
|---|---|---|---|
| `KB SEARCH.json` | Agregar `.toUpperCase()` al proyecto | Normalizar si caller envía en minúsculas | Baja |
| `Lead Collector.json` | Estandarizar entre `$json` y referencias explícitas en nodo "Body" | Claridad; `$json` puede apuntar al ítem incorrecto | Baja |

---

## Archivos afectados

```
✅ AGENT PRINCIPAL.json       — ACTUALIZADO (48 líneas)
✅ Sync_CRM.json              — ACTUALIZADO (1 línea)
✅ CLAUDE.md                  — ACTUALIZADO (2 líneas)
⏳ Lead Collector.json        — SIN CAMBIOS (retomar: .item.json)
⏳ RSVP.json                  — SIN CAMBIOS (retomar: .item.json)
⏳ KB SEARCH.json             — SIN CAMBIOS (retomar: .item.json + .toUpperCase())
⏳ Send Media.json            — SIN CAMBIOS (retomar: .item.json)
✅ Notifications Master.json  — VERIFICADO (sin cambios necesarios)
✅ Vectorizar los KBs.json    — VERIFICADO (sin cambios necesarios)
```

---

## Commit

```
b4a13f4 fix: Auditoría y correcciones críticas de workflows

**Paso 1 — Campos de atribución:**
- Agregados atribucion_medio y atribucion_contacto a DATA to CREATE
- Agregados los 4 campos de atribución a DATA to CREATE FASE 2

**Paso 2 — .item.json críticos en AGENT PRINCIPAL:**
- 5 reemplazos de .item.json → .first().json en nodos críticos

**Paso 4 — _TelefonoMovil en Sync_CRM:**
- Agregada concatenación defensiva de +502

**Paso 5 — CLAUDE.md:**
- Aclarado que Notifications Master usa destinatarios hardcodeados
```

---

## Próximos pasos

1. **En n8n:** Pushear cambios de AGENT PRINCIPAL.json y Sync_CRM.json a producción
2. **Testing:** Correr `python3 scripts/test_agent.py --scenario happy_path_completo` para validar atribución end-to-end
3. **MongoDB:** Verificar que nuevos documentos en `users` incluyan los 4 campos de atribución
4. **Retomar sesión:** Hacer Paso 3 (`.item.json` en flujos de soporte)

---

## Notas

- CLAUDE.md menciona que `.first().json` es la norma pero aún hay ~50+ usos de `.item.json` en los flujos. Esto no es un bug inmediato (funcionan con 1 ítem) pero es deuda técnica.
- La regla "🔴 VALIDACIÓN OBLIGATORIA PRIMERO" está íntegra — muy bien custodiada.
- No se encontraron referencias rotas ("No path back to referenced node") en ningún workflow.
- Todos los typos SOAP intencionales están en su lugar.

---

**Auditoría completada:** 2026-05-25 16:45 UTC  
**Auditor:** Claude Code  
**Método:** Exploración exhaustiva + verificación manual contra CLAUDE.md
