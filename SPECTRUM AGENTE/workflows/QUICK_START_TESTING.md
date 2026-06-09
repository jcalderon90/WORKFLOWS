# 🎯 Quick Start - Testing Spectrum Agente

## En 3 pasos puedes probar el sistema como un cliente real

### Paso 1: Abre terminal y navega al proyecto

```bash
cd "/Users/jorgecalderon/Desktop/PROYECTOS/WORKFLOWS/SPECTRUM AGENTE/Agente Unificado"
```

### Paso 2: Ejecuta el test que quieras

**Opción A: Lista todos los tests disponibles**
```bash
python3 scripts/test_agent.py --list
```

**Opción B: Ejecuta un test rápido (saludo)**
```bash
python3 scripts/test_agent.py --scenario saludo_inicial
```

**Opción C: Ejecuta la conversación completa (recomendado)**
```bash
python3 scripts/test_agent.py --scenario happy_path_completo
```

**Opción D: Ejecuta TODO (10 escenarios, ~10 minutos)**
```bash
python3 scripts/test_agent.py
```

### Paso 3: Verifica los resultados

El script mostrará:
- ✅ Mensajes que se enviaron
- ✅ Respuestas del agente Sof-IA
- ✅ Qué acciones ejecutó (lead_collector, kb_search, rsvp, etc.)
- ✅ Qué herramientas se usaron

---

## Ejemplo real: testing `happy_path_completo`

```bash
$ python3 scripts/test_agent.py --scenario happy_path_completo

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

✅ [2/4] Usuario: "Mi nombre es Juan Pérez, correo: juan@example.com, teléfono: +50299999999"
   Respuesta (1200ms):
      respuesta: ¡Gracias, Juan! Ahora que tengo tus datos...
      accion: aclarar
      tools: [lead_collector]

✅ [3/4] Usuario: "Me interesa Parque Vista Verde"
   Respuesta (890ms):
      respuesta: ¡Excelente! Parque Vista Verde es uno de nuestros...
      accion: consultar_proyecto
      tools: [kb_search]

✅ [4/4] Usuario: "¿Cuántos metros cuadrados tiene?"
   Respuesta (2150ms):
      respuesta: Los apartamentos de Vista Verde van desde...
      accion: consultar_proyecto
      tools: [kb_search]

======================================================================
RESUMEN: 4 pasados, 0 fallidos
======================================================================

✅ Todos los tests pasaron correctamente
```

---

## Qué se está probando

| Test | Valida que... |
|------|--------------|
| `saludo_inicial` | El agente responde amablemente a un "Hola" |
| `happy_path_completo` | Flujo completo: usuario → datos → proyecto → info |
| `lead_sin_datos` | Se solicita nombre/correo/teléfono si faltan |
| `fuera_de_contexto` | Se rechaza solicitudes de código, recetas, etc. |
| `mencion_proyecto_directo` | Detecta "Vista Verde", "Portales", etc. |
| `solicita_asesoria` | Escala a humano cuando se solicita |
| `multiples_proyectos` | Pregunta cuál si hay ambigüedad (zona 15) |
| `canal_instagram` | Funciona igual en Instagram que en WhatsApp |
| `rsvp_flow` | Permite agendar una visita/cita |
| `modismos_guatemaltecos` | Entiende "simón", "va", "nel", etc. |

---

## 💡 Preguntas frecuentes

### ¿Cuánto tarda?
- Un escenario: 30-40 segundos (incluye timeout de respuesta)
- Todos (10 escenarios): 5-8 minutos

### ¿Dónde se guardan los datos?
- En MongoDB Atlas (colección `users`)
- En Redis (cache temporal de mensajes)
- No se borran automáticamente (para auditoría)

### ¿Cómo veo los logs en n8n?
1. Ve a `https://agentsprod.redtec.ai`
2. Haz click en "AGENT PRINCIPAL"
3. Pestaña "Executions"
4. Verás una ejecución por cada mensaje enviado

### ¿Puedo correr los tests múltiples veces?
Sí, cada ejecución usa un `user_id` único, así que no se superponen.

### ¿Qué hago si algo falla?
1. Chequea que tengas internet
2. Verifica que `https://agentsprod.redtec.ai` esté accesible
3. Revisa los logs en n8n (pestaña Executions)
4. Lee el archivo `scripts/README_TEST_AGENT.md` para troubleshooting

---

## 🚀 Para cualquier IA o desarrollador

El script `scripts/test_agent.py` está diseñado para que **cualquier IA** pueda:
1. Ejecutarlo sin configuración adicional
2. Entender exactamente qué se está probando
3. Ver resultados claros con colores
4. Hacer debug de problemas

**Solo necesitas:**
- Python 3.6+
- Internet (para conectarse al webhook remoto)
- Terminal

---

## Ejemplo: Cómo usarlo en un contexto de IA

```python
# Cualquier IA puede ejecutar:
import subprocess
result = subprocess.run(
    ["python3", "scripts/test_agent.py", "--scenario", "saludo_inicial"],
    cwd="/Users/jorgecalderon/Desktop/PROYECTOS/WORKFLOWS/SPECTRUM AGENTE/Agente Unificado",
    capture_output=True,
    text=True
)
print(result.stdout)  # Ver salida con colores
```

---

**Documentación completa**: Ver `scripts/README_TEST_AGENT.md`  
**Última actualización**: 2026-05-22
