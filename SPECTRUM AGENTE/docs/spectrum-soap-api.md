# Código de opciones de campos — Spectrum CRM

**Operación:** `CreacionClientePotencialBot` · **Entorno:** Producción
**Versión:** 1.1 · **Fecha:** Abril 2026

> Documento de referencia de los catálogos de valores aceptados por la API SOAP de Spectrum CRM en la operación `CreacionClientePotencialBot`. Los valores aquí listados son los **autoritativos** para integraciones (n8n, bots, formularios, etc.). Cuando el catálogo del CRM nativo difiere, se anota explícitamente.

---

## _OrigenCliente

> ⚠️ En esta operación el valor es **fijo**: siempre `100000001` (corresponde a `Chat` en el catálogo del CRM). El servicio identifica automáticamente que el lead proviene del bot.

| Label | Value |
|---|---|
| Chat (valor fijo de la API) | `100000001` |

<details>
<summary>Catálogo completo del CRM (referencia, no aplica a esta API)</summary>

| Label | Value |
|---|---|
| Activación | 100,000,006 |
| Chat | 100,000,001 |
| Gogetit | 100,000,005 |
| Llamada | 100,000,000 |
| Milk & Cookies | 100,000,007 |
| Portal Corredores | 100,000,009 |
| Prospección Personal | 100,000,003 |
| Referido | 100,000,004 |
| Spetrum Plus | 100,000,012 |
| Tribal | 100,000,011 |
| Visita proyecto | 100,000,002 |
| Web | 100,000,008 |
| Zen Interactive Media | 100,000,010 |

</details>

---

## _Proyecto *(campo nuevo)*

> Código alfabético del proyecto. Requerido en cada request.

| Proyecto | Código |
|---|---|
| Parque Vista Verde | `PVV` |
| Parque Mariscal | `PMAR` |
| Parque Portales | `PPO` |
| Parque Polanco | `PPOL` |
| Parque Sotobosque | `PSB` |

---

## _UTMSource

> La API solo acepta los tres canales que el bot puede originar. Los valores difieren del catálogo base del CRM (toma las variantes "Bot" / Instagram interno).

| Label | Value |
|---|---|
| Facebook | `100000005` |
| WhatsApp | `100000004` |
| Instagram | `100000012` |

<details>
<summary>Catálogo completo del CRM (referencia, no aplica a esta API)</summary>

| Label | Value |
|---|---|
| Tribal | 100,000,011 |
| Directo | 3 |
| Facebook | 1 |
| Facebook Bot | 100,000,005 |
| Google | 2 |
| Instagram | 4 |
| LinkedIn | 5 |
| Open House Facebook | 100,000,001 |
| Open House Google | 100,000,003 |
| Open House Instagram | 100,000,002 |
| RD Station | 100,000,007 |
| Referido | 100,000,000 |
| Waze | 6 |
| Web Bot | 100,000,006 |
| WhatsApp Bot | 100,000,004 |

</details>

---

## _MetodocontactoPref

> ⚠️ **Los valores de la API NO coinciden con el catálogo del CRM.** La API usa enteros simples (2–5). Usar siempre los valores de esta tabla en el payload SOAP.

| Label | Value (API) |
|---|---|
| Correo electrónico | `2` |
| Llamada telefónica | `3` |
| WhatsApp | `4` |
| Cualquier forma | `5` |

<details>
<summary>Catálogo del CRM (referencia, no aplica a esta API)</summary>

| Label | Value |
|---|---|
| Correo Electrónico | 100,000,000 |
| Llamada Telefónica | 100,000,002 |
| WhatsApp | 100,000,001 |

</details>

---

## _NumeroHabitaciones

| Label | Value |
|---|---|
| 1 habitación | `100000000` |
| 2 habitaciones | `100000001` |
| 3 habitaciones | `100000002` |

---

## _EstadoCivil



| Label | Value |
|---|---|
| Soltero | `100000000` |
| Casado | `100000001` |
| Divorciado | `100000002` |
| Unido | `100000003` |

---

## _MotivoInteres *(campo nuevo)*

| Label | Value |
|---|---|
| Quiero más información | `100000000` |
| Para inversión | `100000001` |
| Estoy listo para comprar | `100000002` |
| Para habitar | `100000003` |

---

## _TipoCita

| Label | Value |
|---|---|
| Cita presencial | `100000000` |
| Llamada / Virtual | `100000001` |

---

## _AtendidoPorIA *(campo nuevo — 2026-06-02)*

> ⚠️ Valor **siempre fijo `1`** cuando el lead proviene del bot Sof-IA. Se envía para fase_1 y fase_2 por igual.

| Label | Value |
|---|---|
| Sí (atendido por IA) | `1` |
| No | `0` |

---

## Notas de implementación

- ⚠️ **Typo en tag XML:** el campo de email se envía como `<_CorreEletronico>` (sin "o" en *Correo* y sin "c" en *Electrónico*). Usar exactamente ese nombre.
- ⚠️ **Typo en tag XML:** el campo de campaña se envía como `<_UTMCampaing>` (sin "i" en *Campaign*). Usar exactamente ese nombre.
- ℹ️ **Campos opcionales:** omitir del XML cuando no tengan valor. Solo `_Comentarios` puede enviarse vacío como `<_Comentarios/>`.
- ℹ️ **`_FechaCita`:** formato ISO 8601 con timezone UTC. Ejemplo: `2026-05-10T15:00:00.000Z`.
- ℹ️ **`_Apellido`:** si no está disponible, enviar `"N/A"` (es campo requerido).
- ℹ️ **`_TelefonoMovil`:** siempre con código de país, formato `+502XXXXXXXX`.
