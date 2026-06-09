# Send Media — Resumen de implementación y hallazgos

## Objetivo

Rediseñar el flujo `Send Media.json` para enviar multimedia real (videos Cloudinary, PDFs) en los 3 momentos gatillo definidos por Spectrum, en lugar de solo URLs de imagen estáticas.

---

## Cambios implementados en `Send Media.json`

### Nodo `Map Media Resources` — reescritura completa

**Antes:** base de datos vacía con una URL de imagen de prueba, detección de tipo por extensión simple, retornaba `url` + `objectType` como campos planos.

**Después:**
- Base de datos completa con Cloudinary URLs para `bienvenida`, `amenidad`, `avance_obra` y Google Drive para `plano`
- Función `buildMessages(url, canal, tipo)` que retorna un **array de mensajes** adaptado por canal
- Comportamiento diferenciado WhatsApp vs Instagram/Messenger para videos (ver sección de hallazgos)
- El `tipo` se pasa explícitamente a `buildMessages` para detectar PDFs aunque la URL no tenga extensión `.pdf`

### Nodo `Send API ManyChat` — cambio de body

**Antes:** `jsonBody` con un objeto estático de un mensaje.

**Después:** `specifyBody: "string"` con `JSON.stringify(...)` para pasar el array dinámico `messages`:
```
={{ JSON.stringify({ subscriber_id: ..., data: { version: 'v2', content: { type: canal, messages: messages } } }) }}
```

---

## Base de datos de URLs (`Map Media Resources`)

| Proyecto | bienvenida | amenidad | plano | avance_obra |
|---|---|---|---|---|
| PVV | ✅ Cloudinary | ✅ Cloudinary | ✅ Google Drive | ✅ Cloudinary |
| PMAR | ✅ Cloudinary | ✅ Cloudinary | ✅ Google Drive | — null |
| PPO | ✅ Cloudinary | ✅ Cloudinary | ✅ Google Drive | ✅ Cloudinary |
| PPOL | ✅ Cloudinary | ✅ Cloudinary | ✅ Google Drive | — null |
| PSB | ✅ Cloudinary | ✅ Cloudinary | ✅ Google Drive | — null |

**Cloudinary cloud name:** `dtmw4kwfo`

**Google Drive IDs (plano):**
- PVV: `1m7-eXU3Lw1xVRRsDvJ0B5Czxda4hFvGX`
- PMAR: `1fT3tPv0dYkzuJcnD8LJHC1GtDAyXbszN`
- PPO: `1FbmQA96iJW6uosODYPHWbzGXPxUoUlD-`
- PPOL: `1oQwk1TxDwwat9PgZPPPbUOqzrMLRUcOu`
- PSB: `1SfUniFrWxiaLcwKNV8nVxFK38vQADjbp`

URL directa (sin redirect): `https://drive.usercontent.google.com/download?id=FILE_ID&export=download`  
(No usar `drive.google.com/uc?export=download&id=...` — hace un 303 redirect que ManyChat no sigue)

---

## Hallazgos técnicos críticos

### WhatsApp no entrega videos via ManyChat `sendContent`

- `type: "video"` en `sendContent` → ManyChat devuelve `status: success` pero **WhatsApp no entrega nada**
- Confirmado empíricamente: imagen sí llega, video no
- Instagram y Messenger: `type: "video"` **sí funciona**

**Solución implementada para WhatsApp + video:**
Cloudinary auto-thumbnail: cambiar extensión `.mp4` → `.jpg` devuelve el primer frame como imagen.
```javascript
const thumbnail = url.replace(/\.(mp4|mov|avi|webm)$/i, '.jpg');
return [
  { type: 'image', url: thumbnail },
  { type: 'text', text: 'Ver video completo: ' + url }
];
```

### WhatsApp no entrega PDFs via ManyChat `sendContent`

Tipos probados para enviar PDFs en WhatsApp:

| Tipo | Resultado |
|---|---|
| `file` | `status: success` pero no llega — silencioso |
| `document` | Error explícito: `"Unsupported message type 'document' in DynamicBlock"` |

ManyChat's DynamicBlock (usado por `sendContent`) **no soporta envío de documentos PDF en WhatsApp**.

### Por qué los PDFs estaban en Cloudinary pero no servían

Los 5 PDFs de presentaciones subidos a Cloudinary tenían **"Envío bloqueado"** (control de entrega restringido a nivel de cuenta). No fue posible desbloquearlo desde la UI (error: "No se admite la operación de edición"). Se descartó Cloudinary para PDFs y se migró a Google Drive.

### Google Drive: usar `drive.usercontent.google.com`, no `drive.google.com/uc`

- `https://drive.google.com/uc?export=download&id=...` → 303 redirect
- `https://drive.usercontent.google.com/download?id=...&export=download` → 200 directo, `Content-Type: application/octet-stream`

ManyChat necesita la URL directa sin redirecciones.

---

## Estado pendiente

### PDFs en WhatsApp — decisión sin tomar

Dos opciones para enviar PDFs nativos en WhatsApp:

**Opción A — Texto con link (simple, funciona ya):**
```javascript
{ type: 'text', text: 'Presentacion de ' + proyecto + ': ' + url }
```
El usuario toca el enlace, se descarga el PDF en el browser. No es un adjunto nativo en WhatsApp.

**Opción B — ManyChat Flow con adjunto (nativo, más trabajo):**
1. Crear un Flow en ManyChat Flow Builder por proyecto
2. Agregar bloque de Documento y subir el PDF directamente a ManyChat (sin URL)
3. Usar `sendFlow` API con el flow NS correspondiente
4. Mantener 5 flows (uno por proyecto) actualizados si los PDFs cambian

### AGENT PRINCIPAL — actualización pendiente

El systemMessage y la descripción del tool `send_media` en `AGENT PRINCIPAL.json` **no han sido actualizados** para incluir:
- `tipo_media: "plano"` como tipo válido
- Los 3 momentos gatillo (incluyendo Momento 1 proactivo para `bienvenida`)

Sin este cambio, el agente no llamará `send_media` con `"plano"` ni de forma proactiva con `"bienvenida"`.

---

## Scripts de apoyo creados

Todos en `scripts/`:

| Script | Propósito |
|---|---|
| `fill_amenidad_urls.py` | Llenó URLs de amenidad (reemplazó URLs con caracteres codificados) |
| `fix_whatsapp_video.py` | Primera versión del fix WhatsApp video (thumbnail sin link) |
| `fix_whatsapp_video_link.py` | Fix final: thumbnail + link de texto para WhatsApp |
| `fill_urls.py` | Llenó URLs de bienvenida y avance_obra |
| `fill_plano_urls.py` | Llenó URLs de plano (Google Drive) |
| `fix_plano_detection.py` | Pasó `tipo` a `buildMessages` para detectar plano sin extensión `.pdf` |
| `fix_drive_urls.py` | Reemplazó URLs `drive.google.com/uc` por `drive.usercontent.google.com` |
