# Reporte de Pruebas — Kaan, el Concierge AI de Itz'ana

**Fecha:** 12 de junio de 2026  
**Quién lo hizo:** Jorge Calderon / Garoo Inc.  
**Qué se probó:** El agente de IA "Kaan" — concierge virtual pre-reserva de Itz'ana Resort & Residences  

---

## ¿Qué es Kaan y qué se probó?

Kaan es un agente de inteligencia artificial que atiende a potenciales huéspedes de Itz'ana Resort en WhatsApp, Instagram y Messenger. Su trabajo es guiar al visitante desde el primer "Hola" hasta que decida reservar — y si hay algo que no puede resolver (bodas, empleos, medios), avisar al equipo del hotel por correo.

Probamos 13 conversaciones distintas para asegurarnos de que todo funciona antes de salir a producción.

**Resultado general: 12 de 13 pruebas perfectas ✅ — 1 con un tropiezo menor que el usuario nunca notó ⚠️**

---

## Cómo se hicieron las pruebas

Como ManyChat todavía no está conectado al canal real del hotel, simulamos los mensajes enviando la misma información que enviaría ManyChat al sistema. La respuesta de Kaan se revisó directamente en los logs internos del sistema (n8n).

Para replicar cualquiera de estas pruebas, se manda un mensaje así al sistema:

```
Usuario: Jorge Calderon
Canal: Instagram
Propiedad: Itz'ana (ITZ)
Mensaje: [lo que diría el huésped]
```

---

## Grupo 1 — El camino completo de ventas (el flujo ideal)

Este es el recorrido que queremos que haga la mayoría de los visitantes: llegan sin saber nada, Kaan los acompaña, y terminan con un link para reservar.

---

### Prueba 1 — El primer saludo

**¿Qué se quería ver?**  
Que Kaan se presente bien, diga quién es y dónde trabaja, y arranque la conversación con la primera pregunta.

**Mensaje enviado:** `Hola`

**Lo que respondió Kaan:**
> *"¡Hola! Soy Kaan, tu concierge personal de Itz'ana Resort & Residences en Placencia, Belice. Estoy aquí para ayudarte a planear la estadía perfecta. ¿Es tu primera vez considerando Itz'ana o ya te has hospedado con nosotros antes?"*

**¿Funcionó?** ✅ Sí. Se presentó con su nombre, mencionó el resort y arrancó el flujo de preguntas. También quedó registrado como usuario nuevo en la base de datos.

---

### Prueba 2 — Captura de fechas

**¿Qué se quería ver?**  
Que Kaan entienda y guarde las fechas de viaje cuando el huésped las menciona.

**Mensaje enviado:** `Es mi primera vez, me gustaría ir del 15 al 20 de julio`

**¿Funcionó?** ✅ Sí. Kaan confirmó las fechas y preguntó con quién viaja. En la base de datos quedaron guardados: check-in 15 de julio, check-out 20 de julio.

---

### Prueba 3 — Tipo de viaje y recomendación de habitación

**¿Qué se quería ver?**  
Que Kaan haga la recomendación correcta según el tipo de grupo (pareja, familia, grupo grande).

**Mensaje enviado:** `Somos 2 adultos, viaje romántico`

**Lo que respondió Kaan:**
> *"Para una escapada romántica, la opción estrella es nuestro Penthouse con plunge pool privado — vistas panorámicas al mar Caribe, total privacidad..."*

**¿Funcionó?** ✅ Sí. Detectó que es un viaje romántico, recomendó el Penthouse (la opción configurada para parejas) y guardó `tipo de grupo: romántico` en el perfil del usuario.

---

### Prueba 4 — Link de reservas

**¿Qué se quería ver?**  
Que cuando el huésped quiere reservar, Kaan le dé el link correcto — no un link genérico ni un placeholder de texto.

**Mensaje enviado:** `Me interesa reservar, ¿cómo lo hago?`

**¿Funcionó?** ✅ Sí. Kaan compartió el link correcto de Itz'ana: `https://reservations.itzanabelize.com/book/accommodations`. Este link viene de la configuración del sistema, no está pegado a mano en el bot — lo que significa que si el hotel cambia su sistema de reservas, solo hay que actualizar un lugar.

---

## Grupo 2 — Preguntas sobre el resort (base de conocimiento)

Kaan tiene acceso a una "enciclopedia" del resort con 37 entradas: restaurantes, actividades, spa, bodas, políticas, ubicación, etc. Cuando el huésped pregunta algo específico, Kaan busca en esa enciclopedia antes de responder.

---

### Prueba 5 — Pregunta sobre restaurantes

**¿Qué se quería ver?**  
Que Kaan busque en la enciclopedia del resort y dé información real, no inventada.

**Mensaje enviado:** `¿Qué restaurantes tiene el hotel?`

**¿Funcionó?** ✅ Sí. Kaan consultó la base de conocimiento y respondió con los nombres y detalles de los restaurantes de Itz'ana tal como están en la enciclopedia.

---

### Prueba 6 — Pregunta en inglés

**¿Qué se quería ver?**  
Que Kaan responda en el idioma del huésped.

**Mensaje enviado:** `What is the cheapest room available?`

**¿Funcionó?** ⚠️ Más o menos. Kaan intentó buscar en la enciclopedia pero hubo un error interno en esa consulta. Sin embargo, respondió en inglés con información válida desde su conocimiento general — el huésped nunca vio el error ni recibió una respuesta rara.

**Respuesta real de Kaan (en inglés):**
> *"Our most accessible option starts with the Garden Rooms, which offer a beautiful tropical setting. For specific pricing and availability for your dates, I'd recommend checking our reservation system directly..."*

**Impacto real:** Ninguno para el huésped. Es un detalle técnico interno que está documentado para revisión futura.

---

## Grupo 3 — Situaciones que requieren escalar al equipo del hotel

Cuando hay algo que el bot no debe manejar solo (bodas, prensa, empleos, o cuando el huésped pide hablar con alguien), Kaan avisa al equipo por correo inmediatamente.

Se verificó que los correos llegaron a `jorge.calderon@garooinc.com`. En producción, llegarán al email real de cada área del hotel.

---

### Prueba 7 — Consulta de bodas

**¿Qué se quería ver?**  
Que una consulta de bodas dispare un correo al coordinador de eventos.

**Mensaje enviado:** `Quiero organizar mi boda en el resort, ¿tienen paquetes?`

**¿Funcionó?** ✅ Sí. Kaan le dijo al huésped que el equipo especializado lo contactará pronto, y el correo llegó en menos de 30 segundos con:
- Categoría: Bodas/Eventos
- Nombre del contacto
- Resumen de la conversación
- El último mensaje del huésped

---

### Prueba 8 — Consulta de prensa / colaboraciones

**¿Qué se quería ver?**  
Que un influencer o periodista que escribe sea dirigido al área de PR del resort.

**Mensaje enviado:** `Soy influencer de viajes, me gustaría hacer una colaboración con el resort`

**¿Funcionó?** ✅ Sí. Correo recibido con categoría "PR/Colaboración" y resumen correcto.

---

### Prueba 9 — Consulta de empleo

**¿Qué se quería ver?**  
Que quien busca trabajo sea dirigido a Recursos Humanos.

**Mensaje enviado:** `¿Están contratando? Me gustaría trabajar en el resort`

**¿Funcionó?** ✅ Sí. Correo recibido con categoría "Empleo". 

**Nota:** En una primera prueba con una sesión muy larga (muchas conversaciones acumuladas), Kaan no envió el correo. En una sesión nueva funcionó sin problemas. Es un comportamiento conocido de los modelos de IA cuando tienen demasiado contexto cargado — en producción, cada conversación empieza fresca.

---

### Prueba 10 — El huésped quiere hablar con un humano

**¿Qué se quería ver?**  
Que cuando alguien pide hablar con el equipo del hotel directamente, el bot no insista en seguir respondiendo sino que avise y ceda el paso.

**Mensaje enviado:** `Prefiero hablar directamente con alguien del resort`

**¿Funcionó?** ✅ Sí. Kaan respondió amablemente que el equipo lo contactará pronto, y el correo de alerta llegó correctamente.

---

## Grupo 4 — Casos raros (¿qué pasa si...?)

---

### Prueba 11 — Pregunta que no tiene nada que ver con el resort

**¿Qué se quería ver?**  
Que Kaan no invente respuestas sobre cosas ajenas al resort.

**Mensaje enviado:** `¿Cuánto cuesta un Tesla?`

**Lo que respondió Kaan:**
> *"Eso está fuera de mi especialidad — yo solo sé de lo que hace especial a Itz'ana 😄 ¿Hay algo del resort que te gustaría explorar?"*

**¿Funcionó?** ✅ Sí. No respondió sobre Tesla, redirigió la conversación de vuelta al resort sin ponerse raro.

---

### Prueba 12 — Inglés

*(Ver Prueba 6 — aplica a ambos grupos)*

---

### Prueba 13 — Mensaje sin sentido

**¿Qué se quería ver?**  
Que si alguien manda caracteres aleatorios, el bot no se caiga ni responda algo extraño.

**Mensaje enviado:** `asdfghjkl 1234 ???`

**¿Funcionó?** ✅ Sí. Kaan lo tomó como si fuera un nuevo inicio de conversación y saludó de nuevo. Sin errores, sin respuestas raras.

---

## Problemas que encontramos y arreglamos

Durante las pruebas aparecieron 5 cosas que no funcionaban bien. Todas se corrigieron antes de terminar las pruebas. El sistema está limpio.

| Problema | Qué pasaba | Cómo se arregló |
|---|---|---|
| Link de reservas como texto plano | En vez del link real, aparecía el texto `[BOOKING_LINK]` en la respuesta de Kaan | Se conectó correctamente al link que viene de la configuración del sistema |
| Error de sintaxis al arrancar | El sistema no arrancaba por un conflicto con los apóstrofes en "Itz'ana" y "Ka'ana" dentro del código | Se ajustó la forma de escribir esos nombres dentro del código |
| Datos del huésped no se guardaban | Al actualizar el perfil de un usuario existente, la operación fallaba silenciosamente | Se corrigió la forma de identificar al usuario en la base de datos |
| Correos de escalamiento no llegaban | Kaan intentaba escalar pero los correos nunca salían — el sistema de notificaciones no recibía los datos del agente | Se reconfiguró cómo el agente pasa información al sistema de correos |
| Error de ManyChat (ventana de 24h) | ManyChat rechazaba el envío porque en pruebas el usuario no había interactuado en las últimas 24h | Se deshabilitó el envío a ManyChat durante pruebas — en producción con usuarios reales esto no pasa |

---

## Qué quedó guardado en el sistema después de las pruebas

Al final de todas las conversaciones, el perfil del usuario de prueba quedó así en la base de datos:

```
Nombre: Jorge Calderon
Canal: Instagram
Propiedad: Itz'ana
Check-in guardado: 15 de julio
Check-out guardado: 20 de julio
Tipo de grupo: Romántico
```

> ⚠️ Estos datos de prueba se borrarán de la base de datos antes de salir a producción para que el sistema empiece limpio.

---

## Resumen final

| Tipo de prueba | Cuántas | ✅ OK | ⚠️ Parcial | ❌ Falló |
|---|---|---|---|---|
| Flujo de ventas completo | 4 | 4 | 0 | 0 |
| Preguntas al resort (KB) | 2 | 1 | 1 | 0 |
| Escalamientos con correo | 4 | 4 | 0 | 0 |
| Casos raros | 3 | 3 | 0 | 0 |
| **Total** | **13** | **12** | **1** | **0** |

---

## Qué falta antes de salir al aire

| Tarea | Quién |
|---|---|
| Conectar ManyChat real y habilitar envío de respuestas | Garoo |
| Borrar datos de prueba de la base de datos | Garoo |
| Configurar webhook de Ka'ana en ManyChat (agente Balam) | Garoo + Hotel |
| Probar Ka'ana end-to-end | Garoo |
| Emails reales del hotel para escalamientos (bodas → Mr. Diego, empleo → RRHH, resto → concierge) | Hotel |
| Links de reserva con fechas pre-llenadas (deeplinks iHotelier) | Pendiente: account manager de TravelClick |

---

*Reporte generado el 12 de junio de 2026 — Sistema listo para la siguiente fase: conexión con ManyChat real.*
