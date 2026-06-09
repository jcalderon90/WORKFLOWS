// compare_remote.js — compara nodos y timestamps entre JSON remotos y locales
const fs = require('fs');
const path = require('path');

const TMPDIR = path.join(__dirname, '.remote_cache');
const BASE = path.join(__dirname, '..', 'Agente Unificado');

const WORKFLOWS = [
  { label: 'AGENT PRINCIPAL',     remote: 'agent_principal',     local: 'AGENT PRINCIPAL.json' },
  { label: 'Lead Collector',       remote: 'lead_collector',       local: 'Lead Collector.json' },
  { label: 'KB SEARCH',            remote: 'kb_search',            local: 'KB SEARCH.json' },
  { label: 'RSVP',                 remote: 'rsvp',                 local: 'RSVP.json' },
  { label: 'Send Media',           remote: 'send_media',           local: 'Send Media.json' },
  { label: 'Sync_CRM',             remote: 'sync_crm',             local: 'Sync_CRM.json' },
  { label: 'Notifications Master', remote: 'notifications_master', local: 'Notifications Master.json' },
  { label: 'Vectorizar KBs',       remote: 'vectorizar_kbs',       local: 'Vectorizar los KBs.json' },
];

const summary = [];

for (const wf of WORKFLOWS) {
  // Parse remote
  const rawRemote = JSON.parse(fs.readFileSync(path.join(TMPDIR, wf.remote + '.json'), 'utf8'));
  const rwf = rawRemote.result.content[0];
  const remoteWf = JSON.parse(rwf.text).workflow;
  const rNodes = (remoteWf.nodes || []).map(n => n.name).sort();

  // Parse local
  const localPath = path.join(BASE, wf.local);
  const lwf = JSON.parse(fs.readFileSync(localPath, 'utf8'));
  const lNodes = (lwf.nodes || []).map(n => n.name).sort();

  const onlyRemote = rNodes.filter(n => !lNodes.includes(n));
  const onlyLocal  = lNodes.filter(n => !rNodes.includes(n));

  const remoteUpdated = remoteWf.updatedAt;
  const localUpdated  = lwf.updatedAt || 'no-timestamp';

  const remoteTS = new Date(remoteUpdated).getTime();
  const localTS  = lwf.updatedAt ? new Date(lwf.updatedAt).getTime() : 0;

  let sync = '✅ SYNC';
  if (onlyRemote.length || onlyLocal.length) sync = '⚠️  DIFF';
  else if (remoteTS > localTS + 60000) sync = '🔼 REMOTO ADELANTADO';
  else if (localTS > remoteTS + 60000) sync = '⬇  LOCAL ADELANTADO';

  summary.push({ label: wf.label, sync, rCount: rNodes.length, lCount: lNodes.length,
                 onlyRemote, onlyLocal, remoteUpdated, localUpdated });
}

// Print table
console.log('\n╔══════════════════════════════════════════════════════════╗');
console.log('║   COMPARACIÓN LOCAL vs REMOTO  — 2026-06-08            ║');
console.log('╚══════════════════════════════════════════════════════════╝\n');

for (const r of summary) {
  console.log(`── ${r.label} ──`);
  console.log(`   Estado:  ${r.sync}`);
  console.log(`   Nodos:   LOCAL=${r.lCount}  REMOTO=${r.rCount}`);
  console.log(`   Updated: LOCAL  ${r.localUpdated}`);
  console.log(`            REMOTO ${r.remoteUpdated}`);
  if (r.onlyRemote.length) console.log(`   🆕 Solo REMOTO: ${r.onlyRemote.join(', ')}`);
  if (r.onlyLocal.length)  console.log(`   ⬇  Solo LOCAL:  ${r.onlyLocal.join(', ')}`);
  console.log('');
}
