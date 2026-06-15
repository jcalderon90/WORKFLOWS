# Guía de Pruebas — Kaan (Itz'ana) y Balam (Ka'ana)

**Para:** Equipo de pruebas  
**Canal:** Instagram DM / WhatsApp / Messenger (vía ManyChat)  
**Fecha:** Junio 2026

---

## ¿Qué es el bot?

Es un concierge virtual de pre-reserva. Su trabajo es:

1. Identificar al usuario (primera vez vs. huésped recurrente)
2. Capturar fechas, tamaño del grupo y tipo de viaje
3. Recomendar la habitación correcta según el perfil
4. Entregar un link de reserva pre-llenado con fechas y huéspedes
5. Escalar a un humano cuando sea necesario

**Kaan** atiende a Itz'ana Resort & Residences (Placencia).  
**Balam** atiende a Ka'ana Resort (San Ignacio).  
El mismo bot detecta cuál propiedad atender según el canal de ManyChat.

---

## Reglas generales de comportamiento

| Regla | Detalle |
|---|---|
| Idioma | Detecta el idioma del primer mensaje y lo mantiene todo el tiempo |
| Tono | Cálido, sofisticado, directo. Sin frases genéricas como "¡Claro que sí!" |
| Formato | Texto plano. Sin asteriscos ni markdown. Máximo ~500 caracteres por mensaje |
| Nunca inventa | Si no sabe algo, redirige al correo o teléfono del resort |
| Off-topic | No responde preguntas ajenas al resort. Redirige amablemente |
| No se identifica como IA | A menos que le pregunten directamente |

---

## Flujo esperado de una conversación completa

```
1. Saludo → el bot se presenta y pregunta si es primera vez
2. Primera vez / Recurrente → si recurrente, pide email/tel de registro
3. Fechas → ¿cuándo piensan venir?
4. Grupo → ¿cuántos adultos? ¿hay niños?
5. Recomendación → sugiere la habitación ideal según el perfil
6. Contacto → pide nombre y email/tel para seguimiento (opcional)
7. Decisión → ¿reservar, explorar o hablar con el equipo?
8. Link de reserva → con fechas y huéspedes pre-llenados
9. Actividades → ofrece información de actividades disponibles
```

El bot puede saltar pasos si el usuario ya da la información en su mensaje.

---

## Escenarios de prueba y comportamiento esperado

---

### 1. Saludo simple

**Mensaje:** `Hola`

**Respuesta esperada:**
> Hola, soy Kaan, tu concierge virtual de Itz'ana Resort & Residences. ¿Es tu primera vez con nosotros, o ya te has hospedado antes?

**Qué verificar:**
- ✅ Se presenta con el nombre correcto (Kaan / Balam)
- ✅ Menciona el resort correcto
- ✅ Pregunta si es primera vez
- ✅ NO llama al KB ni herramientas externas para un saludo

---

### 2. Consulta de habitaciones

**Mensaje:** `¿Qué habitaciones tienen?`

**Respuesta esperada (Itz'ana):**
> Tenemos varias opciones: Villas frente al mar (1, 2 o 3 habitaciones) con plunge pool privado y terraza; Penthouses en el último piso con vista al mar; Suite frente a la playa con terraza envolvente; y Habitaciones Deluxe junto a la piscina. Los precios varían por fecha y temporada. ¿Cuándo están pensando venir?

**Respuesta esperada (Ka'ana):**
> Ofrecemos suites y villas rodeadas de jungle: Balam Suite, Casita Suite, Master Suite con plunge pool privado, y Villas de 1 y 2 dormitorios con piscina privada. ¿Es tu primera vez con nosotros?

**Qué verificar:**
- ✅ Menciona habitaciones reales del resort (no inventadas)
- ✅ Termina con una pregunta para continuar el flujo
- ✅ No da precios exactos

---

### 3. Conversación completa con deeplink

**Secuencia de mensajes:**

| Turno | Usuario | Bot |
|---|---|---|
| 1 | `Hola` | Se presenta, pregunta si es primera vez |
| 2 | `Primera vez` | Pregunta fechas |
| 3 | `Del 10 al 15 de agosto` | Pregunta cuántos son |
| 4 | `Somos 2, una pareja` | Recomienda habitación romántica con descripción del KB |
| 5 | `Me interesa, mándame el link` | Envía deeplink con fechas + Adults=2 pre-llenados |

**Link esperado (Itz'ana):**
```
https://reservations.itzanabelize.com/book/accommodations
  ?HotelID=115719&DateIn=08/10/2026&DateOut=08/15/2026&Adults=2&Children=0
  &utm_source=kaan-chat&utm_medium=manychat&utm_campaign=itzana-f1
```

**Qué verificar:**
- ✅ Fechas correctas en el link
- ✅ Adults=2, Children=0
- ✅ HotelID correcto según propiedad (115719 ITZ / 115718 KAA)
- ✅ UTMs presentes

---

### 4. Familia con niños

**Secuencia:**

| Turno | Usuario | Bot |
|---|---|---|
| 1 | `Buenos días, quiero información` | Se presenta, pregunta si es primera vez |
| 2 | `Primera vez` | Pregunta fechas |
| 3 | `Julio, flexible` | Acepta y pregunta el grupo |
| 4 | `2 adultos y 2 niños` | Recomienda habitación familiar (Beach Villa / Villa 2BR) |

**Qué verificar:**
- ✅ Recomienda opción familiar, no romántica
- ✅ Captura niños correctamente (ninos=2)

---

### 5. Escalamiento — quiere hablar con alguien

**Mensaje:** `Quiero hablar con una persona`  
o: `¿Puedo hablar con alguien del equipo?`

**Respuesta esperada:**
> Te conecto con nuestro equipo ahora. ¿Deseas agregar algún detalle o tu número para que te llamen?

**Qué verificar:**
- ✅ No insiste en continuar la conversación
- ✅ El equipo recibe un email de escalamiento a `jorge.calderon@garooinc.com` (provisional)
- ✅ `escalate: true` en el output del agente

---

### 6. Bodas y eventos

**Mensaje:** `Quiero organizar una boda en el resort`

**Respuesta esperada:**
> ¡Qué emocionante! Cuéntame: ¿cuántos invitados aproximadamente, en qué época piensan celebrarla, y cuál es la mejor forma de contactarte? Nuestro especialista en eventos te contactará en un día hábil con una propuesta personalizada.

**Qué verificar:**
- ✅ Pide detalles del evento (invitados, fecha, contacto)
- ✅ No promete capacidad ni precios
- ✅ El equipo recibe email de bodas/eventos
- ✅ `categoria: bodas_eventos`

---

### 7. Idioma inglés

**Mensaje:** `Hi, what rooms do you have?`

**Respuesta esperada:**
> Hello! We offer Beachfront Villas (1–3BR) with private plunge pool, top-floor Penthouses with sea views, a Beachfront Suite, and Deluxe Rooms by the pool. Is this your first time with us, or have you stayed before?

**Qué verificar:**
- ✅ Responde completamente en inglés
- ✅ No mezcla idiomas
- ✅ Mantiene el inglés en toda la conversación

---

### 8. Pregunta off-topic

**Mensaje:** `¿Cuál es la capital de Francia?`  
o: `¿Me recomiendas un hotel en Cancún?`

**Respuesta esperada:**
> Solo puedo ayudarte con información sobre Itz'ana Resort & Residences. ¿Hay algo sobre el resort, habitaciones o actividades en lo que pueda ayudarte?

**Qué verificar:**
- ✅ NO responde la pregunta off-topic
- ✅ Redirige al resort
- ✅ `categoria: off_topic`

---

### 9. Pregunta que el bot no sabe responder

**Mensaje:** `¿Tienen disponibilidad para el 20 de julio?`  
o: `¿Cuánto cuesta la Villa frente al mar?`

**Respuesta esperada:**
> Para disponibilidad y precios exactos, lo mejor es contactar directamente al equipo: concierge@itzanabelize.com o +(501) 610-1329. También puedes revisar opciones en [link de reservas].

**Qué verificar:**
- ✅ No inventa precios ni disponibilidad
- ✅ Dirige al equipo o al IBE
- ✅ No hace promesas que no puede cumplir

---

## Señales de que algo está mal

| Síntoma | Problema probable |
|---|---|
| Responde como Kaan en canal Ka'ana (o viceversa) | Error de routing de propiedad |
| Inventa precios o fechas de disponibilidad | Alucinación del modelo — reportar con el mensaje exacto |
| El link no tiene fechas aunque el usuario las dio | Error en Parse Agent Output — revisar execution en n8n |
| No responde nada / timeout | Revisar ejecución en n8n (posible error de Redis o MongoDB) |
| Responde en español si el usuario escribió en inglés | Error de detección de idioma — reportar |
| Responde más de ~500 caracteres en un mensaje normal | Rompe el límite de estilo — reportar |

---

## Cómo reportar un problema

Al encontrar un comportamiento incorrecto, reportar:

1. **Propiedad:** ITZ o KAA
2. **Canal:** Instagram / WhatsApp / Messenger
3. **Mensaje exacto que envió el usuario**
4. **Respuesta que dio el bot** (screenshot)
5. **Qué debería haber respondido** (según esta guía)

Enviar a Jorge Calderón con el screenshot y hora del mensaje para cruzarlo con las ejecuciones en n8n.
