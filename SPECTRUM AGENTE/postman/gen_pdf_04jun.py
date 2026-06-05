#!/usr/bin/env python3
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
from collections import defaultdict
from datetime import datetime, timedelta
from fpdf import FPDF

API_KEY = "wErMF6s31zCFVtnFDeFH"
BASE_URL = "https://leads-form-garoo.koyeb.app/api/v1"

# --- Data fetch ---
resp = requests.get(
    f"{BASE_URL}/logs/",
    params={'from_date': '2026-06-04T06:00:00', 'to_date': '2026-06-05T05:59:59', 'limit': 200},
    headers={'api-key': API_KEY},
    timeout=30
)
resp.raise_for_status()
items = resp.json().get('items', [])

def is_test(lead):
    n = lead.get('lead_name','').lower()
    e = lead.get('lead_email','').lower()
    return 'prueba' in n or 'test' in n or 'probando' in e

def utc_to_gt(s):
    dt = datetime.fromisoformat(s[:19]) - timedelta(hours=6)
    return dt.strftime('%d/%m %H:%M')

leads = [i for i in items if i.get('lead_name') and i.get('method') == 'POST' and not is_test(i)]

by_proj = defaultdict(list)
for l in leads:
    by_proj[l.get('lead_project','Unknown')].append(l)

summary = []
total_unique = 0
for proj in sorted(by_proj.keys()):
    seen = {}
    for l in by_proj[proj]:
        k = (l.get('lead_name','').strip().title(), l.get('lead_phone','').strip())
        if k not in seen:
            seen[k] = l
    unique = sorted(seen.values(), key=lambda x: x.get('created_at',''))
    total_unique += len(unique)
    summary.append((proj, unique))

# --- PDF ---
BRAND_GREEN = (39, 174, 96)
DARK       = (30, 30, 30)
MID_GRAY   = (100, 100, 100)
LIGHT_GRAY = (245, 245, 245)
WHITE      = (255, 255, 255)

class PDF(FPDF):
    def header(self):
        self.set_fill_color(*BRAND_GREEN)
        self.rect(0, 0, 210, 18, 'F')
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*WHITE)
        self.set_xy(10, 4)
        self.cell(0, 10, 'SPECTRUM VIVIENDA  |  Reporte Leads Fase 2  |  4 Junio 2026', align='L')
        self.set_text_color(*DARK)
        self.ln(14)

    def footer(self):
        self.set_y(-12)
        self.set_font('Helvetica', '', 7)
        self.set_text_color(*MID_GRAY)
        self.cell(0, 6, f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M")}  |  Fuente: Spectrum Leads API', align='L')
        self.cell(0, 6, f'Pag. {self.page_no()}', align='R')

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# --- Summary box ---
pdf.set_font('Helvetica', 'B', 18)
pdf.set_text_color(*DARK)
pdf.cell(0, 10, 'Reporte Leads Fase 2', ln=True)
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(*MID_GRAY)
pdf.cell(0, 5, '4 de Junio 2026  (hora Guatemala, UTC-6)', ln=True)
pdf.ln(4)

# KPI cards
card_w = 37
card_h = 20
card_x = [10, 52, 94, 136, 178]
kpi_labels = ['Total leads', 'PMAR', 'PPO', 'PPOL', 'PSB/PVV']
proj_totals = {p: len(u) for p,u in summary}
kpi_values = [
    str(total_unique),
    str(proj_totals.get('PMAR', 0)),
    str(proj_totals.get('PPO', 0)),
    str(proj_totals.get('PPOL', 0)),
    str(proj_totals.get('PSB', 0) + proj_totals.get('PVV', 0)),
]
y0 = pdf.get_y()
for i, (lbl, val) in enumerate(zip(kpi_labels, kpi_values)):
    x = card_x[i]
    pdf.set_fill_color(*LIGHT_GRAY)
    pdf.rect(x, y0, card_w, card_h, 'F')
    pdf.set_fill_color(*BRAND_GREEN)
    pdf.rect(x, y0, card_w, 3, 'F')
    pdf.set_xy(x, y0 + 4)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(*BRAND_GREEN)
    pdf.cell(card_w, 8, val, align='C')
    pdf.set_xy(x, y0 + 12)
    pdf.set_font('Helvetica', '', 7)
    pdf.set_text_color(*MID_GRAY)
    pdf.cell(card_w, 5, lbl, align='C')

pdf.set_y(y0 + card_h + 8)

# --- Per-project tables ---
col_w = [52, 34, 68, 26]  # Nombre, Teléfono, Email, Hora
headers = ['Nombre', 'Teléfono', 'Email', 'Hora GT']
TABLE_W = sum(col_w)  # 180

for proj, unique in summary:
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(*WHITE)
    pdf.set_fill_color(*BRAND_GREEN)
    pdf.cell(TABLE_W, 7, f'  {proj}   ({len(unique)} leads)', ln=True, fill=True)

    # Header row
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_text_color(*WHITE)
    pdf.set_fill_color(*DARK)
    for w, h in zip(col_w, headers):
        pdf.cell(w, 5, f' {h}', fill=True)
    pdf.ln()

    # Data rows
    pdf.set_font('Helvetica', '', 7)
    for idx, l in enumerate(unique):
        bg = WHITE if idx % 2 == 0 else LIGHT_GRAY
        pdf.set_fill_color(*bg)
        pdf.set_text_color(*DARK)

        name = l.get('lead_name','').title()[:30].encode('latin-1', errors='replace').decode('latin-1')
        phone = l.get('lead_phone','')
        email = l.get('lead_email','')[:38]
        hora = utc_to_gt(l.get('created_at',''))

        row_h = 5
        pdf.cell(col_w[0], row_h, f' {name}', fill=True)
        pdf.cell(col_w[1], row_h, f' {phone}', fill=True)
        pdf.cell(col_w[2], row_h, f' {email}', fill=True)
        pdf.cell(col_w[3], row_h, f' {hora}', fill=True)
        pdf.ln()

    pdf.ln(5)


out = 'postman/reportes fase 2/leads_fase2_04junio.pdf'
pdf.output(out)
print(f'PDF generado: {out}')
