# Test Suite - Spectrum Agente Unificado

Script de pruebas automatizadas para simular conversaciones completas con el agente Sof-IA como si fuera un cliente real.

## 🚀 Uso rápido

```bash
# Ejecuta todos los escenarios (10 tests)
python3 scripts/test_agent.py

# Ejecuta un escenario específico
python3 scripts/test_agent.py --scenario saludo_inicial

# Lista todos los escenarios disponibles
python3 scripts/test_agent.py --list

# Modo verbose (más detalles)
python3 scripts/test_agent.py --scenario happy_path_completo --verbose
```

## 📋 Escenarios incluidos

| Nombre | Descripción |
|--------|-------------|
| `saludo_inicial` | Validar bienvenida sin datos previos |
| `happy_path_completo` | Conversación completa: saludo → datos → proyecto → consulta |
| `lead_sin_datos` | Verifica que se llame `lead_collector` cuando faltan datos |
| `fuera_de_contexto` | Valida guardrail para temas ajenos (código, recetas, etc.) |
| `mencion_proyecto_directo` | Usuario menciona proyecto en primer mensaje |
| `solicita_asesoria` | Usuario solicita hablar con asesor humano |
| `multiples_proyectos` | Zona ambigua: "Zona 15" (PVV o PSB) |
| `canal_instagram` | Prueba con canal Instagram (no WhatsApp) |
| `rsvp_flow` | Usuario quiere agendar una visita |
| `modismos_guatemaltecos` | Respuestas con modismos: "simón", "va", "nel" |

## ⚙️ Cómo funciona

1. **Genera un `user_id` único** para cada sesión de prueba
2. **Envía mensajes al webhook** `https://agentsprod.redtec.ai/webhook/spectrum-agent`
3. **Captura y analiza respuestas** del agente Sof-IA
4. **Valida palabras clave** en las respuestas (si están configuradas)
5. **Reporta resultados** con colores y timing

### Payload del webhook

El script construye automáticamente este formato:

```json
{
  "key": "test_abc12345",
  "body": {
    "id": "test_abc12345",
    "page_id": "page_spectrum_test",
    "custom_fields": {
      "canal_ingreso": "WhatsApp",
      "proyecto_interes": ""
    },
    "last_input_text": "mensaje del usuario",
    "whatsapp_phone": "+50212345678"
  }
}
```

## 📊 Output esperado

```
======================================================================
ESCENARIO: saludo_inicial
======================================================================

Descripción: Validar bienvenida sin datos previos
Canal: WhatsApp

User ID (sesión): test_a1b2c3d4

✅ [1/1] Usuario: "Hola"
   Respuesta (2340ms):
      respuesta: ¡Hola! Soy Sof-IA, asistente virtual de SPECTRUM...
      accion: saludar
      tools: []

======================================================================
RESUMEN: 1 pasados, 0 fallidos
======================================================================
```

## 🔧 Detalles técnicos

- **Lenguaje**: Python 3.6+
- **Dependencias**: Solo stdlib (urllib, json, time, uuid, sys, argparse)
- **Timeout**: 35 segundos (10s wait en flujo + 20s procesamiento + 5s margen)
- **User ID**: UUID único por sesión para no contaminar conversaciones
- **Limpieza**: Los datos se guardan en MongoDB/Redis de prueba (no se borran automáticamente)

## 🔍 Qué valida cada test

### `happy_path_completo`
- ✅ El agente responde al saludo
- ✅ Solicita datos cuando falta información
- ✅ Detecta proyecto mencionado por usuario
- ✅ Puede consultar KB sobre el proyecto

### `lead_sin_datos`
- ✅ Cuando faltan nombre/correo/teléfono → llama `lead_collector`
- ✅ Aunque el usuario pregunte sobre precios/info del proyecto

### `fuera_de_contexto`
- ✅ Rechaza solicitudes ajenas a inmobiliaria
- ✅ Redirige amablemente al tema de vivienda

### `multiples_proyectos`
- ✅ Si hay ambigüedad (ej: zona 15) → pregunta qué proyecto específico
- ✅ Zona 15 tiene dos: Parque Vista Verde (PVV) y Sotobosque (PSB)

### `rsvp_flow`
- ✅ Usuario puede agendar una cita/visita
- ✅ El agente llama al workflow `rsvp`

## 📌 Notas importantes

1. **El webhook responde síncronamente** — El flujo n8n procesa completamente y devuelve la respuesta en el mismo request
2. **Wait de 10 segundos** — El flujo acumula mensajes vía Redis antes de procesarlos (de ahí el timeout de 35s)
3. **No hay limpieza automática** — Los datos persisten en MongoDB para auditoría; puedes verificarlos en MongoDB Atlas
4. **Cada escenario usa un `user_id` diferente** — Para no contaminar conversaciones en sesiones anteriores

## 🎯 Cómo ejecutar desde otro sistema

Cualquier IA o desarrollador puede ejecutar:

```bash
cd "/Users/jorgecalderon/Desktop/PROYECTOS/WORKFLOWS/SPECTRUM AGENTE/Agente Unificado"
python3 scripts/test_agent.py
```

O solo un escenario:

```bash
python3 scripts/test_agent.py --scenario happy_path_completo
```

## ✅ Verificación post-test

Después de ejecutar, puedes verificar que todo funcionó:

1. **En MongoDB Atlas**: Accede a `Centralizado.users` y filtra por `manychat_id` que comience con `test_`
2. **En n8n**: Ve a `https://agentsprod.redtec.ai` → AGENT PRINCIPAL → Executions → Verifica que aparezcan las ejecuciones con tus `user_id`
3. **Revisa los logs**: Cada ejecución en n8n tiene logs detallados de qué pasó en cada nodo

## 🐛 Troubleshooting

### El webhook retorna error 500
- Verifica que la URL sea correcta: `https://agentsprod.redtec.ai/webhook/spectrum-agent`
- Chequea en n8n que el workflow esté activo

### Timeout (35 segundos)
- Es normal si hay mucho procesamiento de IA (OpenAI API latency)
- Aumenta el timeout en el script si es necesario

### Respuesta vacía o malformada
- El webhook está respondiendo pero el JSON es inválido
- Verifica en n8n que el nodo "PRINCIPAL" esté devolviendo un JSON válido

### Los datos no aparecen en MongoDB
- Espera 10-15 segundos (el "Wait" del flujo puede retrasar)
- Verifica que la conexión a MongoDB esté correcta en n8n

---

**Última actualización**: 2026-05-22  
**Autor**: Claude Code  
**Proyecto**: Spectrum Agente Unificado
