# Postman API Configuration

Archivos de configuración de Postman para interactuar con la **Spectrum Leads API**.

## Archivos

### `SPECTRUM ENV.postman_environment.json`
Variables de entorno. Incluye:
- `BASE_URL` — URL base de la API (producción o local)
- `API_KEY` — Clave de autenticación (type: secret)
- `LOCAL_URL` — URL local para development

**Cómo usar:**
1. Abre Postman
2. Importa este archivo como Environment
3. Llena los valores vacíos:
   - `BASE_URL`: `https://agentsprod.redtec.ai/api/v1` (producción)
   - `API_KEY`: Tu clave API
   - `LOCAL_URL`: `http://localhost:8000/api/v1` (si usas local)

### `Spectrum API.postman_collection.json`
Colección de endpoints disponibles:
- **Health Test** — GET `/test/`
- **Create Lead - Produccion** — POST `/leads/`
- **Create Lead - Prueba** — POST `/leads/test`
- **Leads Stats** — GET `/leads/stats`
- **Get Leads** — GET `/logs/?from_date=...&to_date=...`

## Endpoints disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/test/` | Health check |
| POST | `/leads/` | Crear lead (producción) |
| POST | `/leads/test` | Crear lead de prueba |
| GET | `/leads/stats` | Estadísticas de leads |
| GET | `/logs/` | Obtener logs con filtros de fecha |

## Parámetros para `/logs/`

```
from_date=2026-05-23T00:00:00-06:00
to_date=2026-05-24T23:59:00-06:00
limit=200
ok=true (opcional)
manychat_tag_applied=true (opcional)
```

## Uso desde línea de comandos

```bash
# Health check
curl -X GET "{{BASE_URL}}/test/"

# Crear lead
curl -X POST "{{BASE_URL}}/leads/" \
  -H "api-key: {{API_KEY}}" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "telefono": "50241234567",
    "correo": "juan@example.com",
    "proyecto": "PVV",
    "observaciones": "Lead de prueba"
  }'

# Obtener leads del 26 de mayo
curl -X GET "{{BASE_URL}}/logs/?from_date=2026-05-26T00:00:00-06:00&to_date=2026-05-26T23:59:00-06:00&limit=500" \
  -H "api-key: {{API_KEY}}"
```

## Integración con scripts

Los datos que obtuviste (leads del 26 de mayo) provienen de esta API. Puedes:
1. Usar Postman para testing manual
2. Usar `curl` en scripts bash
3. Usar librerías como `requests` (Python) o `axios` (Node.js)

## Script Python: `fetch_leads.py`

Script automatizado para traer leads de la API sin usar MongoDB.

### Instalación

```bash
pip install requests
```

### Uso

**Traer leads del 26 de mayo:**
```bash
python3 fetch_leads.py --date 2026-05-26
```

**Rango de fechas:**
```bash
python3 fetch_leads.py --from-date 2026-05-20 --to-date 2026-05-26
```

**Exportar a CSV:**
```bash
python3 fetch_leads.py --date 2026-05-26 --csv leads_26mayo.csv
```

**Exportar a JSON:**
```bash
python3 fetch_leads.py --date 2026-05-26 --json leads_26mayo.json
```

**Hoy (defecto):**
```bash
python3 fetch_leads.py
```

### Output

El script retorna:
- ✅ Markdown formateado (consola)
- 📊 CSV o JSON (si especificas `--csv` o `--json`)
- 🔢 Conteo de leads únicos por proyecto

### Ventajas vs MongoDB

- ✅ No requiere conexión directa a MongoDB Atlas
- ✅ Más rápido para reportes puntuales
- ✅ Exporta directamente a CSV/JSON
- ✅ Evita problemas de DNS en scripts locales

### Configuración

Los valores están hardcodeados en el script:
```python
API_KEY = "wErMF6s31zCFVtnFDeFH"
BASE_URL = "https://leads-form-garoo.koyeb.app/api/v1"
```

Para cambiar, edita `fetch_leads.py` o usa variables de entorno:
```bash
export API_KEY="tu_clave"
export BASE_URL="https://..."
python3 fetch_leads.py --date 2026-05-26
```

---
**Última actualización:** 2026-05-27  
**Conexión:** Spectrum Leads API (REST HTTP)
