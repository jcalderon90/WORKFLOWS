# Pruebas Fase 1 — Kaan (F1.1 + F1.3)

Envía los mensajes desde ManyChat (WhatsApp/Instagram/Messenger) como usuario de prueba.
Revisa la respuesta de Kaan y los nodos en n8n para cada caso.

---

## Pre-condición para T6 (returning guest)
Antes de hacer el test T6, insertar este documento en MongoDB Atlas → colección `users`:

```json
{
  "manychat_id": "<tu manychat_id real>",
  "propiedad": "ITZ",
  "nombre": "Laura",
  "email": "",
  "telefono": "",
  "input_channel": "whatsapp",
  "first_interaction": "2026-01-15T10:00:00.000Z",
  "last_interaction": "2026-01-15T10:00:00.000Z",
  "has_reservation": false,
  "datos_completos": false
}
```
Reemplaza `<tu manychat_id real>` con el ID que aparece en tu perfil de ManyChat.
Después del test, borra el documento para no afectar el flujo real.

---

## Tests

### T1 — Saludo puro
**Envía:** `Hola`
**Espera:**
- Kaan se presenta como concierge de Itz'ana
- No llama a ninguna herramienta (verificar en n8n: AI Agent no tiene tool calls)
- Respuesta corta y cálida

---

### T2 — Exploración de habitaciones (F1.1)
**Envía:** `¿Qué tipos de habitaciones tienen?`
**Espera:**
- Kaan describe las opciones: villa, penthouse, beachfront suite, deluxe room
- **NO aparece** `reservations.itzanabelize.com` en la respuesta
- Puede haber un link de contenido del sitio web del resort

---

### T3 — Exploración de actividades en inglés (F1.1 + idioma)
**Envía:** `What outdoor activities do you offer?`
**Espera:**
- Respuesta en inglés
- Lista de actividades (snorkel, buceo, kayak, etc.)
- **NO aparece** el link de booking
- Puede incluir `itzanabelize.com/es/aventuras`

---

### T4 — Intención de reservar (F1.1)
**Envía:** `Quiero reservar una villa para diciembre, ¿cómo lo hago?`
**Espera:**
- **SÍ aparece** `reservations.itzanabelize.com/book/accommodations`
- Kaan menciona que los precios varían por fecha/temporada
- Pide nombre y correo para dar seguimiento

---

### T5 — Pregunta de precio sin intención de reservar (F1.1 borde)
**Envía:** `¿Cuánto cuesta la noche en una villa?`
**Espera:**
- Kaan menciona que los precios varían por temporada
- **NO aparece** el link de booking todavía (el usuario aún explora)
- Respuesta informativa, no de conversión

---

### T6 — Returning guest (F1.3 lectura)
> ⚠️ Requiere haber insertado el documento en MongoDB con tu manychat_id y `nombre: "Laura"`

**Envía:** `Hola, buenos días`
**Espera:**
- Kaan saluda mencionando **"Laura"** de forma natural
- Respuesta cálida de bienvenida

---

### T7 — Captura de nombre (F1.3 escritura)
**Envía:** `Mi nombre es Carlos Pérez y me interesan las villas de playa`
**Espera:**
- Kaan responde con info de villas
- En n8n: `Parse Agent Output` tiene `nombre_capturado: "Carlos Pérez"`
- En n8n: nodo `Preparar Datos Contacto` ejecuta (no vacío)
- En n8n: nodo `Guardar Contacto` ejecuta
- En MongoDB: tu documento en `users` tiene `nombre: "Carlos Pérez"`

---

### T8 — Captura de email (F1.3 escritura)
**Envía:** `I'd like more info, my email is test@example.com`
**Espera:**
- En n8n: `email_capturado: "test@example.com"`
- En MongoDB: tu documento en `users` tiene `email: "test@example.com"`
- Kaan responde en inglés preguntando en qué puede ayudar

---

### T9 — Escalación bodas
**Envía:** `Queremos celebrar nuestra boda en el resort el próximo año`
**Espera:**
- Kaan da info de venues y menciona que el equipo enviará una propuesta
- `escalate: true` en el output (verificar en n8n)
- `categoria: "bodas_eventos"`
- Workflow `ITZ NOTIFICATIONS` se ejecuta → email enviado a `jorge.calderon@garooinc.com`

---

### T10 — Off-topic
**Envía:** `¿Cuál es la capital de Francia?`
**Espera:**
- Kaan redirige amablemente al resort ("Solo puedo ayudarte con consultas sobre Itz'ana...")
- No llama a kb_search
- `categoria: "off_topic"` en n8n

---

## Qué revisar en n8n después de cada test

En cada ejecución del workflow `ITZ PRINCIPAL AGENT`:

| Nodo | Qué verificar |
|---|---|
| `AI Agent` | Si llamó herramientas (tool calls) o respondió directo |
| `Parse Agent Output` | Valores de `response_text`, `categoria`, `nombre_capturado`, `email_capturado` |
| `Preparar Datos Contacto` | Si ejecutó (T7/T8) o retornó vacío (resto) |
| `Guardar Contacto` | Si ejecutó y qué campos actualizó (T7/T8) |
| `ITZ NOTIFICATIONS` | Si se disparó (T9) |
