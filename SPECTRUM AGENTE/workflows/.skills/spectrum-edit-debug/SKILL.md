# Skill: Spectrum — Edit & Debug

Úsalo cuando vayas a **editar nodos existentes** o **depurar ejecuciones**.
Para reglas de negocio / SOAP / catálogos → usa `spectrum-business-rules`.
Para agregar features nuevas → usa `spectrum-agente-unificado`.

---

## § 1 — Node Finder (comandos)

Todos los scripts están en `workflows/scripts/`. Ejecutar desde la raíz del repo.

```bash
# Listar todos los nodos de un workflow
./workflows/scripts/list-nodes.sh "workflows/<ARCHIVO>.json"

# Volcar un nodo completo por nombre
./workflows/scripts/get-node.sh "workflows/<ARCHIVO>.json" "<NOMBRE_NODO>"

# Ver parámetro específico de un nodo
./workflows/scripts/get-node-param.sh "workflows/<ARCHIVO>.json" "<NODO>" "<PARAM>"
# Params más usados: systemMessage · jsCode · text · assignments · conditions

# Buscar texto dentro de todos los workflows
grep -rn "<TEXTO>" workflows/*.json

# Buscar en un workflow específico
grep -n "<TEXTO>" "workflows/AGENT PRINCIPAL.json"
```

---

## § 2 — Edit Guide por workflow

| Workflow | Nodos más editados | Param clave |
|---|---|---|
| `AGENT PRINCIPAL.json` | `PRINCIPAL` | `systemMessage`, `text` |
| `AGENT PRINCIPAL.json` | `CONTEXT 1` | `assignments` |
| `AGENT PRINCIPAL.json` | `DATA to CREATE`, `DATA to UPDATE` | `assignments` |
| `Lead Collector.json` | `Lead Agent` | `options` (systemMessage anidado en options) |
| `Lead Collector.json` | `SET CONTEXT` | `assignments` |
| `RSVP.json` | `RSVP Agent` | `options` (systemMessage anidado en options) |
| `RSVP.json` | `CONTEXT` | `assignments` |
| `KB SEARCH.json` | `GENERAL AGENT` | `options` (systemMessage anidado en options) |
| `Sync_CRM.json` | `Body` | `assignments` (XML SOAP en campo `body`) |
| `Sync_CRM.json` | `Information Extractor` | `systemMessage` |

**Comandos rápidos para los nodos más editados:**
```bash
# System prompt del orquestador
./workflows/scripts/get-node-param.sh "workflows/AGENT PRINCIPAL.json" "PRINCIPAL" "systemMessage"

# XML SOAP de Sync_CRM
./workflows/scripts/get-node-param.sh "workflows/Sync_CRM.json" "Body" "assignments"

# Contexto del Lead Collector
./workflows/scripts/get-node-param.sh "workflows/Lead Collector.json" "SET CONTEXT" "assignments"
```

---

## § 3 — Expresiones críticas (propensas a bugs)

**`CONTEXT 1` — campo `proyecto`**
```js
{{ $('Proyecto').isExecuted ? $json.output.proyecto : '' }}
```
> `Proyecto` extractor solo corre en WhatsApp. En otros canales siempre devuelve `''`.

**`DATA to UPDATE` — campo `proyecto`**
```js
{{ $('CONTEXT 1').first().json.proyecto || $('Find User').first().json.proyecto }}
```
> Prioriza extractor fresco; fallback al valor ya guardado en MongoDB.

**`PRINCIPAL` — campo `text`**
```js
Proyecto activo en sesión: {{ $('Insert User Fase 2').isExecuted ? $('Find User').first().json.proyecto : ($('CONTEXT 1').first().json.proyecto || $('User Data').first().json.proyecto || 'Ninguno' ) }}
```
> Guard `isExecuted`: si el lead es Fase 2 (pre-cargado por pauta), toma el `proyecto` directo de `Find User` (ya tiene uno asignado). En el flujo normal usa el extractor fresco (`CONTEXT 1`) con fallback al snapshot `User Data`.

**`Prepare Update` — campo `proyecto`**
```js
{{ $('Parse response').first().json.proyecto || $('User Data').first().json.proyecto || undefined }}
```
> `undefined` = no sobreescribir el campo en MongoDB.

**`Prepare Update` — campo `consulta_pendiente`**
```js
{{ $json.consulta_pendiente_limpiar ? null : ($json.consulta_pendiente_guardar || $('User Data').first().json.consulta_pendiente || undefined) }}
```

**`Hay Cambios?` — campo `FIELDS`**
```js
={{ Object.keys($json).filter(k => k !== '_id' && $json[k] !== null && $json[k] !== undefined).join(",") }}
```
> Filtra `null` y `undefined` para no sobreescribir campos en MongoDB con valores vacíos.

**Regla global:** Usar siempre `.first().json` — nunca `.item.json`. El repo fue normalizado a `.first()` por robustez con outputs multi-item.

---

## § 4 — Debug Recipes

```bash
# Comparar workflow local vs servidor n8n
node scripts/compare_remote.js

# Correr smoke test contra producción (~35s por mensaje — Redis debounce 10s)
python3 workflows/scripts/test_agent.py --scenario saludo_inicial

# Ver todas las ejecuciones recientes de un workflow (vía MCP n8n)
# → usar mcp__n8n-mcp-server__search_executions con workflowId

# Buscar campo específico en un workflow
grep -n '"campo_buscado"' "workflows/AGENT PRINCIPAL.json"

# Ver qué nodos tiene un workflow
./workflows/scripts/list-nodes.sh "workflows/RSVP.json"
```

**Traza de ejecución esperada (happy path completo):**
```
Webhook → PARSE BODY → ES ARCHIVO → text input → SAVE MESSAGE → Wait (10s)
→ GET MESSAGE → DELETE MESSAGES → Aggregate → Sort → Merge → INPUT FINAL
→ If NO WHATSAPP → [Proyecto extractor] → Lenguaje & Asesoria
→ Find User → If USER NOT EXIST → DATA to UPDATE → Update User
→ CONTEXT 1 → PROJECT LIST → JOINNING MESSAGE
→ MongoDB Chat Memory → PRINCIPAL → [tool calls si aplica]
→ Parse response → [If TIENE DATOS NUEVOS → Prepare Update → Hay Cambios? → Update User Lead]
→ Insert Analytics → RESPOND TO MANYCHAT
```

---

## § 5 — Failure Patterns

| Síntoma | Causa probable | Fix |
|---|---|---|
| `"No path back to referenced node"` | Expresión referencia nodo fuera de la rama actual | Usar nodo Set intermedio o `$('nodo').isExecuted` guard |
| Campo MongoDB sobreescrito con `null` | `Hay Cambios?` no filtró el campo | Verificar que `Prepare Update` devuelva `undefined` (no `null`) para campos sin valor |
| SOAP responde error sin código claro | Tag opcional enviado vacío en vez de omitido | Cambiar a ternario: `{{ val ? '<_Tag>'+val+'</_Tag>' : '' }}` |
| Bot responde antes del gate de datos | `systemMessage` de `PRINCIPAL` debilitado | Restaurar sección "🔴 VALIDACIÓN OBLIGATORIA PRIMERO" completa |
| Webhook timeout en test local | Redis debounce de 10s | Usar timeout de 35s en test runner (ya configurado en `test_agent.py`) |
| `.item.json` falla con múltiples items | `.item` no es robusto con multi-output | Reemplazar `.item.json` → `.first().json` en todas las expresiones |
| Ejecución n8n no actualiza MongoDB | `FIELDS` vacío en `Hay Cambios?` | Verificar que `Prepare Update` produce al menos un campo no-null |
