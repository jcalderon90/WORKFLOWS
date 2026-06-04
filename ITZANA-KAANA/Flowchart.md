# BH-CHAT-PRD-001: Product Requirements Document
## Belize Hotels Chat

[cite_start]**Visión general:** Una plataforma de chat única para todos los hoteles de Belice del grupo: el mismo flujo y sistemas, con una base de conocimientos por propiedad[cite: 5]. [cite_start]Evoluciona en tres fases, desde un conserje de captura de clientes potenciales hasta una interfaz conversacional que reserva directamente en Opera[cite: 6].

---

## 📄 Metadatos del Documento

* [cite_start]**Portafolio:** Los hoteles del grupo en Belice[cite: 7].
* [cite_start]**Preparado por:** Growaton[cite: 7].
* [cite_start]**Versión:** 3.2 · Borrador[cite: 7].
* [cite_start]**Fecha:** 30 de mayo de 2026[cite: 7].
* [cite_start]**Propietario:** [Líder de producto del grupo · correo electrónico][cite: 7].
* [cite_start]**Revisores:** [Nombres de las partes interesadas][cite: 7].

---

## SECCIÓN 00: Partes Interesadas y RACI

[cite_start]Tres partes entregan y ejecutan la plataforma: **Growaton** es el propietario del producto, **Redtech** lo construye y los **operadores de cada hotel** lo ejecutan localmente[cite: 10].

### Matriz RACI

| Flujo de trabajo | Growaton | Redtech | Hoteles |
| :--- | :---: | :---: | :---: |
| [cite_start]Propiedad del producto y requisitos [cite: 11] | **A / R** | C | C |
| [cite_start]Ingeniería e integraciones [cite: 11] | **A** | R | I |
| [cite_start]Operaciones: base de conocimientos, voz, escalamiento [cite: 11] | C | I | **A / R** |
| [cite_start]Despliegue por propiedad y lanzamiento [cite: 11] | R | C | **A** |

> [cite_start]**Leyenda:** **R** = Responsable (Responsible) · **A** = Rendición de cuentas (Accountable) · **C** = Consultado (Consulted) · **I** = Informado (Informed)[cite: 12].

* [cite_start]**Growaton:** Propietario de la dirección del producto y los requisitos[cite: 13].
* [cite_start]**Redtech:** Entrega la ingeniería y las integraciones del sistema[cite: 13].
* [cite_start]**Operadores de cada hotel:** Implementan y ejecutan la plataforma localmente (base de conocimientos, voz de marca y escalamiento de huéspedes)[cite: 14].

---

## SECCIÓN 01: Resumen Ejecutivo

[cite_start]El grupo opera varios hoteles de lujo en Belice, entre ellos **Itz’ana** en la costa de Placencia y **Ka’ana** en el interior, cerca de San Ignacio[cite: 17]. [cite_start]Todos comparten la misma propiedad, liderazgo y sistemas, pero mantienen su propio equipo de operaciones en cada propiedad[cite: 18].

### Estado Actual
[cite_start]El chat del sitio web de cada propiedad ya funciona como un conserje de captura de clientes potenciales: califica a los huéspedes, captura datos (incluyendo consultas de grupos y bodas) y los envía al CRM para un seguimiento humano[cite: 19]. [cite_start]**Nada está automatizado más allá de la captura hoy en día**[cite: 20].

### La Propuesta: "Construir una vez, desplegar en todas partes"
[cite_start]Este PRD define una plataforma de chat compartida para todo el portafolio[cite: 21]. [cite_start]El concepto de conversación, el flujo y los sistemas subyacentes se construyen una sola vez[cite: 22]. [cite_start]Lo único que difiere por propiedad es la **base de conocimientos** (habitaciones, actividades, datos de la propiedad y voz de la marca), que pertenece a los operadores de cada hotel[cite: 23].

* [cite_start]*Ejemplo:* La base de conocimientos de Itz’ana conoce las villas de playa y la barrera de coral; la de Ka’ana conoce las suites de la selva y los sitios mayas[cite: 24]. [cite_start]**Mismo bot, mismo flujo, diferente conocimiento**[cite: 25].

### Fases de Desarrollo
1.  [cite_start]**Fase 1:** El chat guía directamente al huésped mediante enlaces a páginas de contenido mientras explora, y un enlace de reserva de **iHotelier** una vez que la intención es clara, respaldado por la base de conocimientos local[cite: 26].
2.  **Fase 2:** Reemplaza los enlaces con una **integración nativa con el PMS Opera (Oracle Hospitality)** del grupo. [cite_start]La disponibilidad y la reserva ocurren dentro de la conversación, y el pago se realiza a través de las APIs de un proveedor de pasarela de pago[cite: 27].
3.  [cite_start]**Fase 3:** Transforma el chat en la interfaz principal, un lienzo conversacional y un conserje proactivo[cite: 28].

> **La Tesis:** El motor, la integración de reservas y el lienzo se comparten en todo el portafolio; solo la base de conocimientos es por propiedad. [cite_start]Cada fase aleja al grupo de la dependencia de terceros: de escalamiento puramente humano, a enlaces guiados, hasta reservar de forma nativa en Opera[cite: 29].

---

## SECCIÓN 02: Antecedentes y Contexto

### El Portafolio
* **Itz’ana:** Frente a la playa en Placencia. [cite_start]Cuenta con villas de playa, penthouses con piscinas de inmersión, marina, la isla privada Coral Caye y actividades en la barrera de coral[cite: 34].
* **Ka’ana:** Refugio en la selva cerca de San Ignacio. [cite_start]Diferente paisaje y actividades, pero el mismo estándar de lujo[cite: 35].

### Sistemas Compartidos, Operadores Diferentes
[cite_start]El liderazgo ejecutivo y los sistemas son compartidos: un CRM común y el PMS Opera[cite: 38]. [cite_start]Lo que varía es el equipo de operaciones de cada propiedad[cite: 39]. [cite_start]Por eso, una plataforma compartida es el diseño correcto: se construye una vez, pero los operadores locales configuran su base de conocimientos, voz de marca y escalamiento[cite: 41].

### El Camino Hacia Adelante
* [cite_start]**Corto plazo:** Guiar a los huéspedes con enlaces a páginas de contenido o a iHotelier (motor de reservas), reduciendo la intervención humana[cite: 47].
* [cite_start]**Largo plazo:** Reemplazar iHotelier con la integración nativa de Opera para manejar disponibilidad, reservas y pagos (vía APIs de pasarela) directamente en el chat[cite: 48].
* [cite_start]**Onboarding:** Agregar un nuevo hotel consistirá principalmente en redactar su base de conocimientos y perfil de voz[cite: 52].

---

## SECCIÓN 03: Definición del Problema y Oportunidad

Limitaciones actuales del sistema independiente:
* [cite_start]❌ **Todo se escala:** El chat captura el cliente potencial, pero cualquier duda detallada o paso hacia la reserva depende de una persona[cite: 56].
* [cite_start]❌ **Sin ruta de reserva propia:** El chat no puede redirigir al huésped a reservar de inmediato, perdiendo el impulso de compra[cite: 57, 58].
* [cite_start]❌ **Ciego a los datos en vivo:** Sin acceso a disponibilidad, reconocimiento de huéspedes recurrentes ni base de conocimientos para preguntas específicas[cite: 59].
* [cite_start]❌ **Un widget impersonal:** El chat está arrinconado, no puede mostrar una habitación, un calendario ni ofrecer personalización[cite: 60, 61].
* [cite_start]❌ **Costo multiplicado:** Resolver esto propiedad por propiedad multiplicaría los costos y fragmentaría la calidad[cite: 62].

### Matriz de Capacidad: Hoy vs. Destino

| Capacidad | Hoy | Destino (Fase 3) |
| :--- | :--- | :--- |
| **Próximo paso** | [cite_start]Siempre escala a una persona [cite: 64] | [cite_start]El chat guía, responde y reserva [cite: 64] |
| **Conoce al huésped** | [cite_start]Captura datos de contacto [cite: 64] | [cite_start]Reconoce huéspedes recurrentes (nombre, año, tipo de habitación) [cite: 64] |
| **Ve el inventario** | [cite_start]No [cite: 64] | [cite_start]En vivo en Opera: habitaciones y tarifas por propiedad [cite: 64] |
| **Reserva** | [cite_start]Solo seguimiento humano [cite: 64] | [cite_start]Nativo en Opera, dentro de la conversación [cite: 64] |
| **Rol de la interfaz** | [cite_start]Widget de esquina [cite: 64] | [cite_start]Lienzo conversacional que maneja toda la página [cite: 64] |
| **Entre propiedades** | [cite_start]Construido / ajustado por sitio [cite: 64] | [cite_start]Una plataforma, base de conocimientos por propiedad [cite: 64] |

---

## SECCIÓN 04: Objetivos y No Objetivos

### Objetivos
* [cite_start]**Plataforma única compartida:** Construir el motor, integración y lienzo una vez; desplegar en todos lados[cite: 68, 69].
* [cite_start]**Base de conocimientos local:** Propiedad de los operadores (habitaciones, actividades, voz)[cite: 70].
* [cite_start]**Guiar antes de escalar:** Servir enlaces correctos o responder preguntas directamente; reservar el escalamiento humano para casos complejos o de alto valor[cite: 71].
* [cite_start]**Reserva nativa en Opera:** Migrar de los enlaces de iHotelier a transacciones directas mediante Opera/OHIP y pasarela de pago[cite: 72].
* [cite_start]**Lienzo conversacional:** Convertir el chat en la interfaz principal y conserje proactivo[cite: 73].
* [cite_start]**Proteger la identidad:** Mantener la voz de cada marca y la salida de emergencia hacia un humano[cite: 74].

### No Objetivos
* [cite_start]Construcciones independientes o proyectos separados por propiedad[cite: 76].
* [cite_start]Comercializar o vender el producto a otros operadores fuera del grupo[cite: 78].
* [cite_start]Eliminar por completo a los humanos (bodas y eventos grandes seguirán escalándose)[cite: 79, 80].
* [cite_start]Reemplazar Opera, el CRM o crear un sistema de pagos interno[cite: 81, 82].
* [cite_start]El chat de voz o audio y el rediseño completo del sitio web de marketing quedan fuera de alcance[cite: 83].

---

## SECCIÓN 05: Métricas de Éxito

[cite_start]Los objetivos aumentan aguas abajo a medida que se avanza en las fases[cite: 86]. [cite_start]Los objetivos son ilustrativos a la espera de una línea base medida[cite: 87].

| Métrica | Hoy | Fase 1 | Fase 2 | Fase 3 |
| :--- | :---: | :---: | :---: | :---: |
| Propiedades en vivo en la plataforma | 0 | 1 (piloto) | Mayoría | [cite_start]Todas [cite: 88] |
| Conversaciones resueltas sin escalamiento | ~0% | >40% | >65% | >[cite_start]75% [cite: 88] |
| Calidad de leads (% con contacto completo) | Medir | +15% | +25% | [cite_start]+35% [cite: 88] |
| Tasa de reserva atribuida al chat | Medir | +10% | +30% | [cite_start]+50% [cite: 88] |
| Reservas completadas en el chat (Opera) | 0% | 0% | >60% | >[cite_start]80% [cite: 88] |
| Ahorro en tarifas de distribución (directas) | n/a | n/a | Track | [cite_start]Track [cite: 88] |
| Tasa de reconocimiento de huéspedes recurrentes | 0% | >70% | >75% | >[cite_start]80% [cite: 88] |

> [cite_start]**Definiciones clave:** > * **Resuelta sin escalamiento:** El huésped obtuvo lo que necesitaba (respuesta, enlace o reserva) sin intervención del equipo del hotel[cite: 89].
> * **Reserva en conversación:** Reserva nativa en Opera dentro del chat/lienzo (disponible desde la Fase 2)[cite: 89].
> [cite_start]* **Atribuida al chat:** Reserva realizada dentro de los 7 días posteriores a una interacción de chat por el mismo huésped identificable[cite: 89].

---

## SECCIÓN 06: Fases del Producto

### 6.1 Fase 1: Enlaces guiados y base de conocimientos
[cite_start]El chat deja de escalarlo todo[cite: 97]. [cite_start]Responde dudas usando la base de conocimientos local y ofrece enlaces (de contenido o de iHotelier) según la intención del usuario[cite: 97].

#### Requisitos Funcionales (Fase 1)
* [cite_start]**F1.1 (Must):** Leer la intención y servir el enlace correcto (contenido al explorar, iHotelier al querer reservar)[cite: 99].
* [cite_start]**F1.2 (Must):** Responder preguntas sobre habitaciones, actividades, logística, etc., desde la base de conocimientos[cite: 99].
* [cite_start]**F1.3 (Should):** Reconocer a un huésped recurrente únicamente por su nombre, año de última visita y tipo de habitación[cite: 99].
* [cite_start]**F1.4 (Must):** Continuar capturando/enriqueciendo leads en el CRM; escalar cuando sea necesario[cite: 99].
* [cite_start]**F1.5 (Could):** Devolver el pronóstico del clima local para sugerencias de itinerarios[cite: 99].

> **Nota sobre Huéspedes Recurrentes:** El reconocimiento es limitado por diseño. Muestra datos básicos para dar una bienvenida cálida, pero no expone detalles de reservas previas ni datos de contacto. [cite_start]La gestión de reservas existentes sigue en manos humanas[cite: 106, 107].

* [cite_start]**Estimación de esfuerzo:** 5 a 9 semanas para el desarrollo compartido en la propiedad piloto[cite: 109].

### 6.2 Fase 2: Reserva nativa en Opera
[cite_start]Reemplaza el enlace de iHotelier por la integración nativa con Opera (vía OHIP)[cite: 113].

#### Requisitos Funcionales (Fase 2)
* [cite_start]**F2.1:** Leer disponibilidad en vivo y tarifas desde Opera[cite: 120].
* [cite_start]**F2.2:** Crear, leer y modificar reservas directamente en Opera mediante OHIP[cite: 121].
* [cite_start]**F2.3:** Procesar pagos mediante las APIs de la pasarela seleccionada y confirmar el cargo[cite: 122].
* [cite_start]**F2.4:** Confirmar la reserva e implementar la confirmación visual en el chat[cite: 123].
* [cite_start]**F2.5:** Gestionar modos de fallo propios: cambios de tarifas, habitaciones agotadas en paralelo, rechazos de pago, reconciliación diaria[cite: 124].
* [cite_start]**F2.6:** Retirar el enlace de iHotelier una vez probado el sistema nativo (mantenerlo temporalmente como fallback)[cite: 125].

* **Dependencias y esfuerzo:** Condicionado al acceso y confirmación del alcance de Opera/OHIP, más la selección del proveedor de pagos. [cite_start]**10 a 16 semanas** tras la confirmación[cite: 127, 128].

### 6.3 Fase 3: Lienzo conversacional y conserje
[cite_start]El chat pasa a ser el entorno principal[cite: 130]. [cite_start]En desktop se convierte en una columna derecha persistente que interactúa con el contenido de la izquierda (el cual cambia dinámicamente entre vistas de habitaciones, mapas, pasarela de pago, etc.)[cite: 131, 132]. [cite_start]En móvil, se despliega como tarjetas en línea[cite: 133]. [cite_start]Se expande a WhatsApp, SMS, flujo en español y alertas proactivas[cite: 134].

> [cite_start]📝 *Nota: Se desarrollará un PRD dedicado exclusivamente para la Fase 3 una vez que las Fases 1 y 2 estén en marcha[cite: 136].*

---

## SECCIÓN 07: Requisitos Técnicos

### Arquitectura
[cite_start]Una única base de código sirve a todo el portafolio[cite: 140]. [cite_start]El motor, lógica de rutas, integraciones (Opera, pagos, CRM) y el framework del lienzo son compartidos[cite: 140]. [cite_start]Cada propiedad es una capa de configuración (base de conocimientos, identidad visual, inventario)[cite: 141]. [cite_start]Cualquier actualización o corrección llega a todos los hoteles en simultáneo[cite: 142].

### Mapa de Integraciones

| Sistema | Fase | Propósito | Estado / Dependencia |
| :--- | :---: | :--- | :--- |
| **CRM** | Ahora | [cite_start]Captura de leads, enriquecimiento y escalamiento [cite: 144] | [cite_start]Ya integrado [cite: 144] |
| **Páginas de contenido web** | 1 | [cite_start]Enlaces de exploración que sirve el chat [cite: 144] | [cite_start]Mapear URLs por propiedad [cite: 144] |
| **Motor iHotelier (Amadeus)** | 1 | [cite_start]Enlace de reserva interino por intención clara [cite: 144] | [cite_start]Confirmado; retirar post-Fase 2 [cite: 144] |
| **Base de conocimientos** | 1 | [cite_start]Q&A de habitaciones, actividades, logística [cite: 144] | [cite_start]Flujo de origen + autoría [cite: 144] |
| **Opera PMS / OHIP** | 2 | [cite_start]Disponibilidad en vivo + reserva nativa [cite: 144] | [cite_start]Confirmar alcance y acceso a OHIP [cite: 144] |
| **Pasarela de pagos** | 2 | [cite_start]Pagos integrados en la conversación vía APIs [cite: 144] | [cite_start]Selección de proveedor y APIs [cite: 144] |
| **API de Clima** | 1 | [cite_start]Pronóstico para sugerencias de itinerario [cite: 144] | [cite_start]Adquisición estándar [cite: 144] |
| **Perfil de Huésped (CRM/Opera)** | 1+ | [cite_start]Reconocimiento de huéspedes (nombre/año/habitación) [cite: 144] | [cite_start]Confirmación de la fuente de datos [cite: 144] |
| **Sistema de Actividades** | 1-3 | [cite_start]Disponibilidad y reserva de actividades [cite: 144] | [cite_start]Confirmación del proveedor [cite: 144] |

* [cite_start]**Pasarela de Pago:** Se prioriza la flexibilidad de las APIs para cobrar de forma nativa *in-conversation* en lugar de usar un checkout externo redirigido (hosted page)[cite: 146]. [cite_start]La decisión final del proveedor depende de Finanzas + Producto[cite: 147].

---

## SECCIÓN 08: Línea de Tiempo y Economía

### Primeros 90 días (Propiedad Piloto, Fase 1)

* [cite_start]**Semanas 1-2 (Cierre de decisiones):** Documentar decisiones clave; confirmar accesos a OHIP; elegir pasarela de pago; confirmar enlaces iHotelier; seleccionar hotel piloto[cite: 155].
* [cite_start]**Semanas 3-7 (Construcción Fase 1):** Enrutamiento de enlaces (contenido + iHotelier), desarrollo de la base de conocimientos, reconocimiento básico de huéspedes y enriquecimiento del CRM en el piloto[cite: 155].
* [cite_start]**Semanas 6-9 (QA del Piloto + Lanzamiento suave):** Despliegue en vivo en el piloto; medición de tasas de escalamiento, calidad de leads y reservas atribuidas[cite: 155].
* [cite_start]**Semanas 9-12 (Kickoff Fase 2):** Iniciar la integración nativa de Opera (OHIP) y desarrollo con el proveedor de pagos[cite: 155].

### Más allá de los 90 días (Despliegue en el Portafolio)
* [cite_start]**Q2:** Fase 2 activa (reserva nativa Opera + pasarela de pago); retirar iHotelier; extender Fase 1 a los siguientes hoteles del portafolio[cite: 157].
* [cite_start]**Q3-Q4:** Fase 3 (lienzo conversacional y luego funciones de conserje avanzado); continuación del despliegue masivo en las propiedades restantes[cite: 157].

> 💰 **Economía del Despliegue:** Debido al enfoque de plataforma compartida, el costo de despliegue disminuye drásticamente con cada propiedad adicional. [cite_start]El motor se construye una vez para el piloto; los siguientes hoteles solo requieren configuración de contenido (base de conocimientos), perfil de voz y personalización de temas visuales por parte de sus operadores locales[cite: 158].