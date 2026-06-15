# Pendientes — Estado al 2026-06-14

Snapshot tras sesión de fixes técnicos: bugs eliminados, workflows publicados en n8n, RAG validado en producción. Lo que sigue es mayormente externo (hotel + ManyChat) o limpieza menor.

---

## 🔴 Bloqueantes externos

| # | Pendiente | Owner | Notas |
|---|---|---|---|
| P1 | Email Mr. Diego (bodas/eventos) | Itz'ana | Todas las categorías de `Itzana_Notifications` van a `jorge.calderon@garooinc.com` |
| P2 | Email RRHH (empleo) | Itz'ana | Template tiene nota `⚠️ Reemplaza el destinatario con email de RRHH` |
| P3 | Webhook ManyChat ITZ con `hoteles_propiedad: "ITZ"` | Garoo + Itz'ana | Bloqueante para flujo real con usuarios |
| K5 | E2E test de Balam (Ka'ana) | Garoo | Falta probar con `propiedad: "KAA"` |
| K6 | Webhook ManyChat KAA con `hoteles_propiedad: "KAA"` | Garoo + Ka'ana | Bloqueante igual a P3 |
| P6 | RoomTypeID Itz'ana del hotel/TravelClick | Itz'ana IT | KAA ya tiene (555466/532468/555465); ITZ → `null` en deep link (ver `roomCodeMap` en `Parse Agent Output`) |

---

## 🟠 KB content gaps

### Itz'ana
- ❌ Coral Caye - Private Island (CORAL)
- ❌ One Bedroom Marina Villa (NA1B)
- ❌ Two Bedroom Marina Villa (NA2B)
- ❌ Three Bedroom Marina Villa (NA3B)
- ❌ Four Bedroom Marina Villa (NA4B)
- ⚠️ Pet policy: hay chunk (`itz_mascotas`) que dice "not pet-friendly", pero CLAUDE.md marca como ⚠️ — confirmar con hotel

### Ambos KBs (Itz'ana + Ka'ana)
- ⚠️ Accesibilidad / ADA — no cubierto
- ⚠️ Restricciones alimentarias (vegano, alergias, kosher) — no cubierto
- ⚠️ Política de cancelación / seguro de viaje — no cubierto
- ⚠️ Amenidades para niños (más allá de "babysitter") — no cubierto
- ⚠️ Costos detallados spa/transfer — mencionados sin precios

---

## 🟡 Deuda técnica (no crítica)

| Item | Severidad | Notas |
|---|---|---|
| Nodos huérfanos en `Itzana_KB_Search` | Bajo | `GENERAL AGENT` + `Property Config` quedaron desconectados tras el bypass. No se ejecutan. Limpieza visual. |
| Nodo huérfano en `Itzana_Vectorizar_KB` | Bajo | `Edit Fields` era el branch alternativo del drop, ahora obsoleto. |
| `GENERAL AGENT` v1.7 con config inválida | Medio | `promptType: "define"` + `text` no permitidos según validator de n8n MCP. Si reconectas, falla. Para reactivar habría que migrar a typeVersion compatible. |
| Mongo posible drift | Bajo | El `Delete documents` previo devolvió `deletedCount: 0` — los 37 chunks nuevos dominan en similaridad pero pueden quedar docs viejos con esquema distinto. |
| `Delete documents` hardcoded a Itz'ana | Bajo | Filter usa `{{ $json.categorias.itzana }}` = "ITZ". Para Ka'ana hay que parametrizar (o duplicar workflow). |

---

## 🟢 Mejoras opcionales

- **Limpiar test data MongoDB** antes de go-live (`users` con `manychat_id`: `1623941319`, `test_clean_2026`, `test_jorge_2026`, `6a2f4f17...`)
- **Logging/métricas**: longitud de respuesta, tasa de escalamiento por categoría, latencia Redis/agent
- **Re-correr suite de tests** en `docs/PRUEBAS_FASE1.md` con el agente corregido y registrar resultados
- **Verificar nodo "Send to ManyChat"** no esté `disabled: true` en producción (P4 en BUILD.md)
- **Llenar KB gaps** (accesibilidad/dietético/cancelación) — sería un nuevo chunk `politicas_faq` por propiedad

---

## ✅ Estado validado (no requiere acción)

Funcionalidad confirmada en producción (execution `122255`, 2026-06-15):

- Webhook → Redis batch (1s) → User upsert → Property Config → AI Agent → Parse → Mongo update
- Extracción correcta de fechas (con año futuro), adultos, niños, grupo_tipo
- Deep links iHotelier con datos reales del usuario (`Adults=4&Children=2&DateIn=07/20/2026...`)
- RAG funcional — 37 chunks ITZ vectorizados, vector search devuelve chunks relevantes
- Multi-propiedad dinámico (Property Config ITZ vs KAA)
- Multi-canal routing (instagram/messenger/whatsapp)
- Persistencia usuarios en Mongo
- Memoria conversacional (30 mensajes window)
- Escalamiento por categoría (5 categorías × email template)
- Audio/imagen processing (Whisper + GPT-4o vision)

---

## 🎯 Orden recomendado de acción

1. **Hotel:** obtener emails Diego + RRHH (P1, P2)
2. **Hotel IT:** RoomTypeID Itz'ana (P6)
3. **Garoo:** configurar webhook ManyChat ITZ (P3) — desbloquea pruebas reales
4. **Garoo:** probar Ka'ana (K5) — mismo engine, distinta propiedad
5. **Garoo + Ka'ana:** webhook ManyChat KAA (K6)
6. **Pre-go-live:** limpiar test data Mongo + verificar "Send to ManyChat" enabled
7. **Continuo:** llenar KB gaps cuando el hotel mande info

---

## Referencias

- Spec completa: `BUILD.md`
- Guía técnica: `CLAUDE.md`
- Tests Fase 1: `docs/PRUEBAS_FASE1.md`
- Workflows: `workflows/PRINCIPAL.json`, `workflows/Itzana_KB_Search.json`, `workflows/Itzana_Notifications.json`, `workflows/Itzana_Vectorizar_KB.json`
- KBs: `KBs/KB_ITZANA.json` (37 chunks), `KBs/KB_KAANA.json` (21 chunks)
