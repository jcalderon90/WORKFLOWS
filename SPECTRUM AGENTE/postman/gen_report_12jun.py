#!/usr/bin/env python3
"""Reporte Leads Fase 2 — 12 de junio 2026 (MongoDB: users_fase_2 x users)"""
import sys
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from pymongo import MongoClient

sys.stdout.reconfigure(encoding='utf-8')

MONGO_URI = "mongodb+srv://jorgecalderon_db_user:hvV2fwG1dGcWVuAT@cluster0.es7z0bi.mongodb.net/?appName=Cluster0"
DB_NAME   = "Centralizado"

# Junio 12 GT 00:00–23:59 = Jun 12 06:00 UTC → Jun 13 05:59 UTC
FROM_UTC = datetime(2026, 6, 12, 6, 0, 0, tzinfo=timezone.utc)
TO_UTC   = datetime(2026, 6, 13, 5, 59, 59, tzinfo=timezone.utc)

def utc_to_gt_str(dt):
    gt = dt.replace(tzinfo=None) - timedelta(hours=6)
    return gt.strftime('%H:%M') + ' GT'

def last_int_str(s):
    # s = "2026-06-12T07:37:50.243-06:00" — tiempo ya en GT (offset -06:00)
    return s[11:16] + ' GT' if s else ''

client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)
db = client[DB_NAME]

leads_f2 = list(db.users_fase_2.find(
    {"first_interaction": {"$gte": FROM_UTC, "$lte": TO_UTC}},
    {"user_id": 1, "name": 1, "phone": 1, "email": 1, "project": 1,
     "first_interaction": 1, "out_of_time": 1}
).sort("first_interaction", 1))

phones = [l["phone"] for l in leads_f2 if l.get("phone")]
users_by_phone = {
    u["telefono"]: u
    for u in db.users.find(
        {"telefono": {"$in": phones}},
        {"telefono": 1, "last_interaction": 1, "nombre": 1}
    )
    if u.get("telefono")
}
client.close()

by_proj = defaultdict(list)
for l in leads_f2:
    by_proj[l.get("project", "Unknown")].append(l)

total     = len(leads_f2)
n_contest = sum(1 for l in leads_f2 if l.get("phone") in users_by_phone)
n_no      = total - n_contest
pct       = n_contest / total * 100 if total else 0

SEP = "=" * 80

def row(status, oot, name, phone, email, sent, ultima=""):
    slot   = " [!] " if oot else "     "
    line   = f"  [{status}]{slot}{name.title():<35} {phone:<14}   {email:<40} {sent}"
    return line + f"   ultima: {ultima}" if ultima else line

lines = [
    "REPORTE LEADS FASE 2 — 12 DE JUNIO 2026",
    "Fuente: MongoDB users_fase_2 x users (cruce por telefono)",
    f"Generado: {datetime.now().strftime('%Y-%m-%d')}",
    "",
    f"Total leads contactados : {total}",
    f"Contestaron al bot      : {n_contest:2d}  ({pct:.1f}%)",
    f"No contestaron          : {n_no:2d}  ({100-pct:.1f}%)",
    "",
    "[C] = contesto al bot   [ ] = no contesto   [!] = fuera de horario",
]

summary_rows = []

for proj in sorted(by_proj.keys()):
    proj_leads = sorted(by_proj[proj], key=lambda l: l["first_interaction"])
    contested  = [l for l in proj_leads if l.get("phone") in users_by_phone]
    not_cont   = [l for l in proj_leads if l.get("phone") not in users_by_phone]
    c, nc = len(contested), len(not_cont)

    hdr = f"{proj} — {len(proj_leads)} leads | {c} contestaron | {nc} no contestaron" \
          if c else f"{proj} — {len(proj_leads)} leads | 0 contestaron"
    lines += ["", SEP, hdr, SEP]

    if contested:
        lines.append("")
    for l in contested:
        u      = users_by_phone[l["phone"]]
        ultima = last_int_str(u.get("last_interaction", ""))
        lines.append(row("C", l.get("out_of_time"), l["name"],
                         l["phone"], l.get("email", ""),
                         utc_to_gt_str(l["first_interaction"]), ultima))

    if not_cont:
        lines.append("")
    for l in not_cont:
        lines.append(row(" ", l.get("out_of_time"), l["name"],
                         l["phone"], l.get("email", ""),
                         utc_to_gt_str(l["first_interaction"])))

    summary_rows.append((proj, len(proj_leads), c, nc))

lines += ["", SEP, "RESUMEN", SEP, ""]
lines.append(f"  {'Proyecto':<10} {'Total':>5}   {'Contestaron':>11}   {'No contest.':>11}   {'% respuesta':>11}")
for proj, tot, c, nc in summary_rows:
    pr = c / tot * 100 if tot else 0
    lines.append(f"  {proj:<10} {tot:>5}         {c:>4}            {nc:>4}          {pr:.1f}%")
tot_c   = sum(r[2] for r in summary_rows)
tot_nc  = sum(r[3] for r in summary_rows)
tot_all = tot_c + tot_nc
pr_all  = tot_c / tot_all * 100 if tot_all else 0
lines.append(f"  {'TOTAL':<10} {tot_all:>5}         {tot_c:>4}            {tot_nc:>4}          {pr_all:.1f}%")
lines.append("")

output = "\n".join(lines)
print(output)

out_file = "postman/reportes fase 2/leads_fase2_12junio.txt"
with open(out_file, "w", encoding="utf-8") as f:
    f.write(output + "\n")
print(f"\n✅ TXT guardado: {out_file}")
