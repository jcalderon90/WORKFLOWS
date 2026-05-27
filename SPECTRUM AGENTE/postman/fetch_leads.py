#!/usr/bin/env python3
"""
Spectrum Leads API — Fetch and format leads by date range
"""

import requests
import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
from pathlib import Path

API_KEY = "wErMF6s31zCFVtnFDeFH"
BASE_URL = "https://leads-form-garoo.koyeb.app/api/v1"

class SpectrumLeadsClient:
    def __init__(self, base_url=BASE_URL, api_key=API_KEY):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'api-key': self.api_key})

    def get_logs(self, from_date, to_date, limit=200):
        """Fetch logs from API with date filters"""
        url = f"{self.base_url}/logs/"
        params = {
            'from_date': from_date,
            'to_date': to_date,
            'limit': limit
        }

        try:
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"❌ Error: {e}")
            return None

    def format_leads_by_project(self, logs, target_date=None):
        """Group leads by project, optionally filtering by target date"""
        by_project = defaultdict(list)

        items = logs.get('items', []) if isinstance(logs, dict) else logs

        for log in items:
            # Filter by date if specified
            if target_date:
                created_at = log.get('created_at', '')
                if not created_at.startswith(target_date):
                    continue

            project = log.get('lead_project', 'Unknown')
            name = log.get('lead_name', '').strip()
            phone = log.get('lead_phone', '').strip()

            if name and phone:
                by_project[project].append({
                    'name': name,
                    'phone': phone
                })

        return dict(sorted(by_project.items()))

    def print_markdown(self, leads_by_project):
        """Print leads in Markdown format"""
        for project in sorted(leads_by_project.keys()):
            leads = leads_by_project[project]
            print(f"\n### {project}")
            seen = set()
            for lead in leads:
                key = (lead['name'], lead['phone'])
                if key not in seen:
                    seen.add(key)
                    print(f"* {lead['name']} — {lead['phone']}")

            print(f"\n**Total {project}:** {len(seen)} leads")

    def export_csv(self, leads_by_project, filename):
        """Export to CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Proyecto', 'Nombre', 'Teléfono'])

            for project in sorted(leads_by_project.keys()):
                leads = leads_by_project[project]
                seen = set()
                for lead in leads:
                    key = (lead['name'], lead['phone'])
                    if key not in seen:
                        seen.add(key)
                        writer.writerow([project, lead['name'], lead['phone']])

        print(f"✅ Exported to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Fetch Spectrum leads by date')
    parser.add_argument('--date', help='Single date (YYYY-MM-DD)', default=None)
    parser.add_argument('--from-date', help='From date (YYYY-MM-DD)', default=None)
    parser.add_argument('--to-date', help='To date (YYYY-MM-DD)', default=None)
    parser.add_argument('--csv', help='Export to CSV file', default=None)
    parser.add_argument('--json', help='Export to JSON file', default=None)
    args = parser.parse_args()

    # Parse dates
    if args.date:
        date_obj = datetime.strptime(args.date, '%Y-%m-%d')
        from_date = date_obj.strftime('%Y-%m-%dT00:00:00-06:00')
        to_date = date_obj.strftime('%Y-%m-%dT23:59:59-06:00')
    elif args.from_date and args.to_date:
        from_date = datetime.strptime(args.from_date, '%Y-%m-%d').strftime('%Y-%m-%dT00:00:00-06:00')
        to_date = datetime.strptime(args.to_date, '%Y-%m-%d').strftime('%Y-%m-%dT23:59:59-06:00')
    else:
        # Default: today
        today = datetime.now()
        from_date = today.strftime('%Y-%m-%dT00:00:00-06:00')
        to_date = today.strftime('%Y-%m-%dT23:59:59-06:00')

    print(f"🔍 Fetching leads from {from_date} to {to_date}...")

    client = SpectrumLeadsClient()
    logs = client.get_logs(from_date, to_date)

    if not logs:
        print("❌ No data returned")
        return

    # Extract target date for filtering
    target_date = None
    if args.date:
        target_date = args.date

    leads_by_project = client.format_leads_by_project(logs, target_date)
    total_unique = sum(len(set((l['name'], l['phone']) for l in leads_by_project.get(p, []))) for p in leads_by_project)

    print(f"✅ Found {total_unique} unique leads across {len(leads_by_project)} projects\n")

    # Print markdown
    client.print_markdown(leads_by_project)

    # Export CSV if requested
    if args.csv:
        client.export_csv(leads_by_project, args.csv)

    # Export JSON if requested
    if args.json:
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(leads_by_project, f, ensure_ascii=False, indent=2)
        print(f"✅ Exported to {args.json}")


if __name__ == '__main__':
    main()
