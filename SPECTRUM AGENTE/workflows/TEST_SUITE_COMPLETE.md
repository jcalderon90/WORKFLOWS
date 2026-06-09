# ✅ Test Suite Completado

## Qué se ha creado

He construido un **sistema de pruebas automatizadas** que permite a cualquier IA o desarrollador simular conversaciones completas con el agente Sof-IA como si fuera un cliente real en WhatsApp/Instagram/Messenger.

### Archivos creados

1. **`scripts/test_agent.py`** (450 líneas)
   - Script principal de pruebas
   - Ejecutable, sin dependencias externas (solo stdlib)
   - 10 escenarios de prueba predefinidos
   - Output con colores y timing

2. **`scripts/README_TEST_AGENT.md`**
   - Documentación completa del script
   - Cómo funciona, qué valida, troubleshooting

3. **`QUICK_START_TESTING.md`**
   - Guía rápida en 3 pasos
   - Ejemplos de uso
   - FAQ

---

## 🚀 Cómo usar (super simple)

```bash
# Ir a la carpeta del proyecto
cd "/Users/jorgecalderon/Desktop/PROYECTOS/WORKFLOWS/SPECTRUM AGENTE/Agente Unificado"

# Ver qué tests hay disponibles
python3 scripts/test_agent.py --list

# Ejecutar una prueba rápida
python3 scripts/test_agent.py --scenario saludo_inicial

# Ejecutar la conversación completa (recomendado)
python3 scripts/test_agent.py --scenario happy_path_completo

# Ejecutar TODO (10 escenarios, ~8-10 minutos)
python3 scripts/test_agent.py
```

---

## 📋 Los 10 escenarios de prueba

| # | Nombre | Qué prueba |
|----|--------|-----------|
| 1️⃣ | `saludo_inicial` | Bienvenida sin datos previos |
| 2️⃣ | `happy_path_completo` | Conversación completa: saludo → datos → proyecto → consulta |
| 3️⃣ | `lead_sin_datos` | Valida que se llame `lead_collector` cuando faltan datos |
| 4️⃣ | `fuera_de_contexto` | Rechaza temas ajenos (código, recetas, medicina, etc.) |
| 5️⃣ | `mencion_proyecto_directo` | Usuario menciona proyecto en primer mensaje |
| 6️⃣ | `solicita_asesoria` | Escala correctamente a asesor humano |
| 7️⃣ | `multiples_proyectos` | Pregunta si hay ambigüedad ("zona 15" → PVV o PSB) |
| 8️⃣ | `canal_instagram` | Funciona igual en Instagram |
| 9️⃣ | `rsvp_flow` | Usuario puede agendar una cita/visita |
| 🔟 | `modismos_guatemaltecos` | Entiende "simón", "va", "nel", etc. |

---

## ⚙️ Cómo funciona

```
Usuario ejecuta script
    ↓
Para cada escenario:
    ├─ Genera user_id único (test_xxx)
    ├─ Construye payload JSON (mimics ManyChat)
    ├─ Envía POST a https://agentsprod.redtec.ai/webhook/spectrum-agent
    ├─ Espera respuesta (timeout 35 segundos)
    ├─ Valida palabras clave en respuesta
    ├─ Imprime resultados con colores
    └─ Pausa 2-3 segundos antes del siguiente
    
Resultado final:
    ├─ Resumen: X pasados, Y fallidos
    ├─ Datos guardados en MongoDB (para auditoría)
    └─ Executions visibles en n8n dashboard
```

---

## 💻 Ejemplo de output

```
======================================================================
ESCENARIO: happy_path_completo
======================================================================

Descripción: Conversación completa: saludo → datos → proyecto → consulta → cita
Canal: WhatsApp

User ID (sesión): test_a1b2c3d4

✅ [1/4] Usuario: "Hola, me interesa saber sobre los proyectos de Spectrum"
   Respuesta (2340ms):
      respuesta: ¡Hola! Soy Sof-IA, asistente virtual de SPECTRUM...
      accion: recolectar_lead
      tools: [lead_collector]

✅ [2/4] Usuario: "Mi nombre es Juan, correo: juan@example.com, teléfono: +50299999999"
   Respuesta (1200ms):
      respuesta: ¡Gracias, Juan! Ahora que tengo tus datos...
      accion: aclarar
      tools: [lead_collector]

✅ [3/4] Usuario: "Me interesa Parque Vista Verde"
   Respuesta (890ms):
      respuesta: ¡Excelente! Parque Vista Verde es uno de...
      accion: consultar_proyecto
      tools: [kb_search]

✅ [4/4] Usuario: "¿Cuántos metros cuadrados?"
   Respuesta (2150ms):
      respuesta: Los apartamentos van desde 45m² hasta...
      accion: consultar_proyecto
      tools: [kb_search]

======================================================================
RESUMEN: 4 pasados, 0 fallidos
======================================================================

✅ Todos los tests pasaron correctamente
```

---

## 🔍 Qué verifica cada test

### `saludo_inicial`
- ✅ Agente responde al saludo
- ✅ No pide datos aún
- ✅ Identifica idioma

### `happy_path_completo`
- ✅ Conversación multi-turno funciona
- ✅ Datos se capturan correctamente
- ✅ Proyecto se detecta
- ✅ Se puede consultar KB del proyecto

### `lead_sin_datos`
- ✅ Si faltan datos → llama `lead_collector`
- ✅ INCLUSO si usuario pregunta sobre precios/info

### `fuera_de_contexto`
- ✅ Rechaza solicitudes ajenas (código, recetas, medicina)
- ✅ Redirige amablemente al tema

### `multiples_proyectos`
- ✅ Detecta ambigüedad correctamente
- ✅ Pregunta cuál proyecto específico

### `rsvp_flow`
- ✅ Usuario puede iniciar agendamiento
- ✅ Se capturan fecha/hora/tipo de contacto

---

## 📊 Quién puede usar esto

✅ **Desarrolladores** — Para QA antes de deployments  
✅ **DevOps** — Para monitoreo/healthchecks del agente  
✅ **Product Managers** — Para validar features sin cliente real  
✅ **Cualquier IA** — Script está diseñado para ser ejecutable por sistemas automáticos  
✅ **Clientes** — Demo interactivo del sistema sin ManyChat  

---

## 🎯 Casos de uso

### Caso 1: Quick smoke test (2 minutos)
```bash
python3 scripts/test_agent.py --scenario saludo_inicial
```
Verifica que el webhook esté respondiendo.

### Caso 2: Validar una feature nueva (5 minutos)
```bash
python3 scripts/test_agent.py --scenario happy_path_completo
```
Prueba la conversación completa.

### Caso 3: Full regression test (10 minutos)
```bash
python3 scripts/test_agent.py
```
Ejecuta todos los 10 escenarios.

### Caso 4: Debug de un problema (variable)
```bash
python3 scripts/test_agent.py --scenario lead_sin_datos --verbose
```
Modo verbose con detalles.

---

## 📞 Verificación post-test

Después de ejecutar, puedes verificar en:

### 1. **MongoDB Atlas** (datos persistidos)
```
URL: https://cloud.mongodb.com/
Base de datos: Centralizado
Colección: users
Filtro: { "manychat_id": { $regex: "^test_" } }
```

### 2. **n8n Dashboard** (executions)
```
URL: https://agentsprod.redtec.ai
Workflow: AGENT PRINCIPAL
Pestaña: Executions
Busca por: user_id que empiece con "test_"
```

### 3. **Redis** (cache temporal)
```
Keys que contienen: test_<user_id>
Nota: Se limpian automáticamente tras el flujo
```

---

## 🛠 Notas técnicas

- **Python**: 3.6+ (solo stdlib)
- **Dependencias**: Cero (urllib, json, time, uuid, sys, argparse están built-in)
- **Timeout**: 35 segundos por request (ajustable en línea 20 del script)
- **User ID**: UUID único por sesión (`test_<8-char-hex>`)
- **Limpieza**: Manual (datos persisten para auditoría)

---

## ✨ Beneficios

| Antes | Ahora |
|-------|-------|
| ❌ Necesitas cliente real (ManyChat, WhatsApp) | ✅ Script puro, sin dependencias externas |
| ❌ Manual (pruebas manuales toman horas) | ✅ Automatizado (10 escenarios en 10 min) |
| ❌ Difícil de debuggear | ✅ Output claro con timing y colores |
| ❌ Una IA no puede probar el sistema | ✅ Cualquier IA puede ejecutar el script |
| ❌ No hay registro de pruebas | ✅ Datos persistidos en MongoDB + logs en n8n |

---

## 📖 Documentación

- **Rápida**: Lee `QUICK_START_TESTING.md` (2 minutos)
- **Completa**: Lee `scripts/README_TEST_AGENT.md` (10 minutos)
- **Código**: `scripts/test_agent.py` (bien comentado)

---

## 🚀 Próximos pasos

1. **Hoy**: Ejecuta `python3 scripts/test_agent.py --scenario saludo_inicial`
2. **Luego**: Ejecuta `python3 scripts/test_agent.py --scenario happy_path_completo`
3. **Después**: Ejecuta el test suite completo `python3 scripts/test_agent.py`
4. **Finalmente**: Integra esto en tu CI/CD si lo deseas

---

**Creado por**: Claude Code  
**Fecha**: 2026-05-22  
**Proyecto**: Spectrum Agente Unificado  
**Estado**: ✅ Completado y probado
