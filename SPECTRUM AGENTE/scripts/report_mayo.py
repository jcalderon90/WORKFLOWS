#!/usr/bin/env python3
"""
Reporte mensual Fase 2: conversaciones y citas por proyecto.

Fuente de verdad Fase 2 = leads_logs (todos los registros) ∪ users(fase_2:true)

Conversaciones = distinct manychat_ids Fase 2 que tuvieron interacción en el mes,
  primero desde leads_logs (por lead_project + fecha), luego suplementado con
  users(fase_2:true) que tengan first_interaction en el mes y no estén en logs.

Citas = appointments del mes cuyo manychat_id pertenece al set Fase 2 completo.

Uso:
    python3 scripts/report_mayo.py             # mes actual
    python3 scripts/report_mayo.py 2026-05     # mes específico
"""

import sys
import os
from datetime import datetime, timezone

# ── DNS override ───────────────────────────────────────────────────────────
try:
    import dns.resolver
    dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
    dns.resolver.default_resolver.nameservers = ["8.8.8.8", "8.8.4.4"]
except Exception:
    pass

# ── Cargar .env desde spectrum-sim-mcp si MONGO_URI no está en el entorno ──
if not os.environ.get("MONGO_URI"):
    env_path = os.path.join(os.path.dirname(__file__), "..", "spectrum-sim-mcp", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    os.environ.setdefault(k.strip(), v.strip())

from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "")
if not MONGO_URI:
    print("ERROR: MONGO_URI no está configurado.")
    sys.exit(1)

# ── Mes a reportar ─────────────────────────────────────────────────────────
month = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m")
try:
    year, mon = map(int, month.split("-"))
except ValueError:
    print(f"ERROR: formato inválido '{month}'. Usa YYYY-MM (ej: 2026-05).")
    sys.exit(1)

start_dt = datetime(year, mon, 1, tzinfo=timezone.utc)
end_year, end_mon = (year + 1, 1) if mon == 12 else (year, mon + 1)
end_dt = datetime(end_year, end_mon, 1, tzinfo=timezone.utc)
PREFIX = month  # para regex sobre first_interaction (string ISO con offset -06:00)

# ── Conexión ───────────────────────────────────────────────────────────────
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10_000)
db = client[os.environ.get("MONGO_DB", "Centralizado")]

# ── Construir sets de IDs Fase 2 ───────────────────────────────────────────
# IDs desde leads_logs (todos los registros, sin filtro de fecha, para citas)
f2_ids_logs = {
    doc["manychat_subscriber_id"]
    for doc in db.leads_logs.find({}, {"manychat_subscriber_id": 1})
    if doc.get("manychat_subscriber_id")
}

# IDs desde users con fase_2: true (suplemento para los que no están en logs)
f2_ids_users_flag = {
    doc["manychat_id"]
    for doc in db.users.find({"fase_2": True}, {"manychat_id": 1})
    if doc.get("manychat_id")
}

all_f2_ids = list(f2_ids_logs | f2_ids_users_flag)

# ── Consultas por proyecto ─────────────────────────────────────────────────
PROJECTS = ["PMAR", "PPO", "PPOL", "PSB", "PVV"]
rows = []

for p in PROJECTS:
    # Conversaciones: distinct IDs en leads_logs para este proyecto en el mes
    logs_in_month = {
        doc["manychat_subscriber_id"]
        for doc in db.leads_logs.find(
            {"lead_project": p, "created_at": {"$gte": start_dt, "$lt": end_dt}},
            {"manychat_subscriber_id": 1}
        )
        if doc.get("manychat_subscriber_id")
    }

    # Suplemento: users(fase_2:true) con first_interaction en el mes, no en logs
    extra_ids = list(f2_ids_users_flag - logs_in_month)
    extra_convs = 0
    if extra_ids:
        extra_convs = db.users.count_documents({
            "manychat_id": {"$in": extra_ids},
            "proyecto": p,
            "first_interaction": {"$regex": f"^{PREFIX}"}
        })

    convs = len(logs_in_month) + extra_convs

    # Citas: appointments del mes para cualquier ID Fase 2 en este proyecto
    citas = db.appointments.count_documents({
        "proyecto": p,
        "manychat_id": {"$in": all_f2_ids},
        "created_at": {"$gte": start_dt, "$lt": end_dt}
    })

    rows.append((p, convs, citas))

# ── Salida ─────────────────────────────────────────────────────────────────
sep = "─" * 44
print(f"\n{sep}")
print(f"  SPECTRUM — Reporte {month} (Fase 2)")
print(f"  Fuente: leads_logs ∪ users(fase_2:true)")
print(f"  Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print(sep)
print(f"  {'Proyecto':<8}  {'Conversaciones':>14}  {'Citas':>6}")
print(f"  {'─'*8}  {'─'*14}  {'─'*6}")
total_c = total_a = 0
for p, c, a in rows:
    print(f"  {p:<8}  {c:>14}  {a:>6}")
    total_c += c
    total_a += a
print(f"  {'─'*8}  {'─'*14}  {'─'*6}")
print(f"  {'TOTAL':<8}  {total_c:>14}  {total_a:>6}")
print(f"  (IDs Fase 2 únicos: {len(all_f2_ids)})")
print(f"{sep}\n")

client.close()
