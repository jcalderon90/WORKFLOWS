#!/usr/bin/env python3
"""
Backfill page_id en documentos de usuarios fase_2 que no lo tienen.

Causa: DATA to CREATE FASE 2 en AGENT PRINCIPAL no guardaba page_id.
Fix aplicado el 2026-06-05. Este script parchea los documentos existentes.

Uso:
  python postman/backfill_page_id.py          # dry-run (solo muestra qué cambiaría)
  python postman/backfill_page_id.py --apply  # aplica los cambios
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb+srv://jorgecalderon_db_user:hvV2fwG1dGcWVuAT@cluster0.es7z0bi.mongodb.net/?appName=Cluster0"
DB_NAME = "Centralizado"

# page_id de WhatsApp Business (único para todos los proyectos)
# Confirmado en documentos de Julia Orozco, Sucely Galeano, Katherine Lemus, Paula Rivera, etc.
WHATSAPP_PAGE_ID = "113631858496836"

def main():
    dry_run = "--apply" not in sys.argv
    if dry_run:
        print("DRY-RUN — no se modificará nada. Usa --apply para aplicar.\n")
    else:
        print("MODO APPLY — se aplicarán los cambios.\n")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users = db["users"]
    settings = db["manychat_settings"]

    # Mapeo page_id → canal desde manychat_settings para referencia
    print("=== manychat_settings (referencia) ===")
    for s in settings.find({}, {"page_id": 1, "proyecto": 1, "_id": 0}):
        print(f"  page_id={s.get('page_id')} → proyecto={s.get('proyecto')}")
    print()

    # Buscar usuarios sin page_id
    sin_page_id = list(users.find(
        {"page_id": {"$exists": False}},
        {"manychat_id": 1, "nombre": 1, "proyecto": 1, "input_channel": 1, "fase_2": 1, "datos_completos": 1}
    ))

    print(f"=== Usuarios sin page_id: {len(sin_page_id)} ===")

    whatsapp_users = []
    otros = []

    for u in sin_page_id:
        canal = u.get("input_channel", "?")
        fase = u.get("fase_2", False)
        nombre = u.get("nombre", "?")
        proyecto = u.get("proyecto", "?")
        mid = u.get("manychat_id", "?")

        if canal == "whatsapp":
            whatsapp_users.append(u)
            tag = "[FASE 2]" if fase else "[NORMAL]"
            print(f"  {tag} {nombre} | {proyecto} | {mid} → page_id={WHATSAPP_PAGE_ID}")
        else:
            otros.append(u)
            print(f"  [SKIP canal={canal}] {nombre} | {proyecto} | {mid}")

    print(f"\nA actualizar (WhatsApp): {len(whatsapp_users)}")
    print(f"Sin acción (otro canal o sin canal): {len(otros)}")

    if not whatsapp_users:
        print("\nNada que actualizar.")
        return

    if dry_run:
        print("\n[DRY-RUN] No se hicieron cambios. Ejecuta con --apply para aplicar.")
        return

    # Aplicar
    ids = [u["_id"] for u in whatsapp_users]
    result = users.update_many(
        {"_id": {"$in": ids}},
        {"$set": {"page_id": WHATSAPP_PAGE_ID}}
    )
    print(f"\n✅ Actualizados: {result.modified_count} documentos con page_id={WHATSAPP_PAGE_ID}")
    print(f"   Timestamp: {datetime.utcnow().isoformat()}")

    client.close()

if __name__ == "__main__":
    main()
