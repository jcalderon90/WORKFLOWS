# Skill: Spectrum Agente Unificado — Arquitectura y Extension Points

Úsalo cuando vayas a **agregar un nuevo tool, workflow, canal o proyecto**.
Para editar nodos → usa `spectrum-edit-debug`.
Para reglas SOAP/CRM/catálogos → usa `spectrum-business-rules`.

---

## § 1 — Arquitectura del sistema

```
ManyChat (6 páginas)
    │
    ▼ webhook
AGENT PRINCIPAL (orquestador, gpt-5-mini)
    │  Redis debounce 10s (agrupa mensajes rápidos)
    │  MongoDB: users, chat_histories
    │
    ├─ lead_collector ──→ Lead Collector.json   (captura name/email/phone → SOAP CRM)
    ├─ kb_search      ──→ KB SEARCH.json        (RAG Atlas Vector, filtro por proyecto)
    ├─ rsvp           ──→ RSVP.json             (citas → appointments + Notifications)
    └─ send_media     ──→ Send Media.json        (brochures/renders vía ManyChat API)

Sync_CRM.json         (scheduled ~15min, SOAP Dynamics 365, protección fase_2)
Notifications Master  (emails HTML: nuevo lead, precios, cita, escalación)
Analytics Centralizado (scheduled diario, métricas por usuario → MongoDB)
```

**Regla de oro del orquestador:** ningún tool excepto `lead_collector` es invocable antes de que el lead tenga nombre + email + teléfono. Gate en `systemMessage` del nodo `PRINCIPAL`.

### IDs n8n (producción en `agentsprod.redtec.ai`)

| Workflow | ID n8n |
|---|---|
| `AGENT PRINCIPAL.json` | `iXaptKTUXaXrP7aF` |
| `Lead Collector.json` | `SHPFhvoal7k1Rqf9` |
| `KB SEARCH.json` | `D3LKuNi6CmMIdvzg` |
| `RSVP.json` | `TjFPzHs5aimxILH7` |
| `Send Media.json` | `NtTiyrNy2LHimE7u` |
| `Sync_CRM.json` | `TTVNRX38pPoPmK2X` |
| `Notifications Master.json` | `r1Jf5vwrkBrT4dEu` |
| `Vectorizar los KBs.json` | `LLiVnT0M6xvDKive` |
| `Analytics Centralizado.json` | `0QfOxWdE9m07laqd` |

---

## § 2 — Agregar un nuevo tool al orquestador

1. **Crear el sub-workflow** en n8n. Debe aceptar un `START` webhook y devolver JSON con al menos:
   ```json
   { "response": "texto para el lead", "datos_completos": 0 }
   ```
2. **En `AGENT PRINCIPAL.json` → nodo `PRINCIPAL`:** agregar descripción del tool en `systemMessage` (sección de tools disponibles).
3. **Agregar nodo `Execute Workflow`** conectado al output de `PRINCIPAL`, configurado con el ID del nuevo workflow.
4. **En `Parse response`:** verificar que el parser maneje el output del nuevo tool (extender si devuelve campos extra).
5. **Registrar** el ID n8n en `CLAUDE.md` (tabla "Remote workflow IDs") y en `INDEX.md` (tabla `## ⚙️ Workflows`).

---

## § 3 — Agregar un nuevo canal / página de ManyChat

1. Insertar documento en colección `manychat_settings` de MongoDB:
   ```json
   { "page_id": "<ID_DE_PAGINA>", "api_key": "<TOKEN_MANYCHAT>", "proyecto": "CODIGO" }
   ```
2. Para Instagram/Messenger: el proyecto queda fijo por `page_id`. No se necesita Regla de Oro.
3. Para WhatsApp orgánico: verificar que el menú interactivo de la Regla de Oro esté activo.
4. Para WhatsApp fase_2 (Tribal): la campaña debe setear `custom_fields.proyecto_interes` antes del primer mensaje.

---

## § 4 — Agregar un nuevo proyecto inmobiliario

1. Crear `KBs/KB_<CODIGO>.json` con los chunks del proyecto. El campo `proyecto` en cada chunk debe ir en UPPERCASE.
2. Insertar entradas en `manychat_settings` para las páginas del nuevo proyecto.
3. Correr el workflow `Vectorizar los KBs` (`LLiVnT0M6xvDKive`) en n8n para indexar.
4. Actualizar `spectrum-business-rules` skill: agregar fila en tabla de proyectos (§ 3).
5. Actualizar `INDEX.md`: agregar fila en tabla `## 🧠 KBs`.

---

## § 5 — Tool output format (contrato entre sub-workflows y PRINCIPAL)

Todo sub-workflow invocado como tool debe devolver un objeto JSON que incluya:

```json
{
  "response": "string — texto que se enviará al lead",
  "datos_completos": 0,
  "proyecto": "PMAR"
}
```

- `response`: obligatorio. Es lo que `RESPOND TO MANYCHAT` envía.
- `datos_completos`: `1` cuando el lead ya tiene nombre+email+phone (usado por Lead Collector).
- `proyecto`: opcional. Si el tool detecta o confirma el proyecto activo, incluirlo para que `Parse response` lo persista.

Agregar campos extra es seguro. Cambiar `response` o `datos_completos` rompe `Parse response` en PRINCIPAL.

---

## § 6 — Patrones de integración n8n

**Execute Workflow (llamada a tool):**
- El nodo debe tener `Wait for sub-workflow completion: true`.
- Pasar `manychat_id`, `proyecto`, `query` como mínimo.
- El output del nodo llega como `.first().json` en el siguiente nodo.

**Expresiones: siempre `.first().json`, nunca `.item.json`**

**MongoDB update con campos dinámicos:**
El patrón `Hay Cambios?` + `FIELDS` genera la lista de campos a actualizar dinámicamente, omitiendo nulls. Reusar este patrón para nuevos nodos de actualización.

**Nodo `Code` en JavaScript:**
- Acceder al input: `const item = $input.first().json`
- Devolver: `return [{ json: { campo: valor } }]`
- Para múltiples items: `return items.map(i => ({ json: { ... } }))`
