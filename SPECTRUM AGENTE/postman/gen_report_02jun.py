#!/usr/bin/env python3
import json, sys, csv, requests
from collections import defaultdict
from datetime import datetime, timedelta

API_KEY = "wErMF6s31zCFVtnFDeFH"
BASE_URL = "https://leads-form-garoo.koyeb.app/api/v1"

def utc_to_gt(utc_str):
    dt = datetime.fromisoformat(utc_str[:19])
    return (dt - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M')

def is_test(lead):
    name = lead.get('lead_name','').lower()
    email = lead.get('lead_email','').lower()
    return 'prueba' in name or 'test' in name or 'probando' in email

resp = requests.get(
    f"{BASE_URL}/logs/",
    params={'from_date': '2026-06-02T06:00:00', 'to_date': '2026-06-03T05:59:59', 'limit': 200},
    headers={'api-key': API_KEY},
    timeout=30
)
resp.raise_for_status()
data = resp.json()

items = data.get('items', [])
leads = [i for i in items if i.get('lead_name') and i.get('method') == 'POST' and not is_test(i)]

by_proj = defaultdict(list)
for l in leads:
    by_proj[l.get('lead_project', 'Unknown')].append(l)

summary = []
total_unique = 0
for proj in sorted(by_proj.keys()):
    seen = {}
    for l in by_proj[proj]:
        k = (l.get('lead_name','').strip().title(), l.get('lead_phone','').strip())
        if k not in seen:
            seen[k] = l
    unique = sorted(seen.values(), key=lambda x: x.get('created_at',''))
    tagged = [u for u in unique if u.get('manychat_tag_applied')]
    total_unique += len(unique)
    summary.append((proj, unique, tagged))

print('# Reporte Leads Fase 2 — 2 de Junio 2026\n')
print(f'**Total leads únicos:** {total_unique}')
print(f'**Proyectos:** {", ".join(p for p,_,_ in summary)}\n')
print('---')

for proj, unique, tagged in summary:
    print(f'\n## {proj}  ({len(unique)} leads · {len(tagged)} taggeados ManyChat)')
    for l in unique:
        tag = '✅' if l.get('manychat_tag_applied') else '⬜'
        print(f'  {tag} {l["lead_name"].title()} | {l["lead_phone"]} | {l["lead_email"]} | {utc_to_gt(l["created_at"])} GT')

print('\n---')
print('\nLeyenda: ✅ = taggeado en ManyChat | ⬜ = sin tag ManyChat')

output_file = 'postman/reportes fase 2/leads_fase2_02junio.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Proyecto','Nombre','Teléfono','Email','Hora GT','ManyChat Tag','Lead ID'])
    for proj, unique, _ in summary:
        for l in unique:
            writer.writerow([
                proj,
                l.get('lead_name','').title(),
                l.get('lead_phone',''),
                l.get('lead_email',''),
                utc_to_gt(l['created_at']) + ' GT',
                'Sí' if l.get('manychat_tag_applied') else 'No',
                l.get('lead_id','')
            ])
print(f'\n✅ CSV guardado: {output_file}')
