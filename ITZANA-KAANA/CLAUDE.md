# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

n8n workflow automation for **Itz'ana Resort & Residences** — an AI concierge agent ("Kaan") that handles pre-booking inquiries via ManyChat (WhatsApp, Instagram, Messenger). Part of a multi-property platform for Belize Hotels group (Itz'ana + Ka'ana); same engine, per-property knowledge base.

**Current phase:** Phase 1 — KB-guided responses + lead capture. No Opera/OHIP integration yet.

---

## Architecture

### Workflow chain (all in n8n)

```
ManyChat → Webhook → PRINCIPAL.json
                          ↓
               Redis batching (1s wait, aggregate messages)
                          ↓
               Audio/Image processing (OpenAI Whisper / GPT-4o)
                          ↓
               MongoDB find/insert/update user (collection: users)
                          ↓
               AI Agent "Kaan" (OpenRouter claude-opus-4.5, typeVersion 3.1)
                 ├── Tool: ITZ KB_SEARCH  → Itzana_KB_Search.json (RAG)
                 └── Tool: ITZ NOTIFICATIONS → Itzana_Notifications.json (email escalation)
                          ↓
               Parse Agent Output (Code node: extract JSON from agent)
                          ↓
               Parameter Type (map canal_ingreso → instagram/messenger/whatsapp)
                          ↓
               Send to ManyChat (HTTP POST → api.manychat.com)
```

### Sub-workflows

| File | n8n ID | Purpose |
|---|---|---|
| `workflows/PRINCIPAL.json` | (main) | Orchestrator — receives ManyChat webhook |
| `workflows/Itzana_KB_Search.json` | `rofQe6ZGW3OpFqcb` | RAG tool: MongoDB vector search → AI response |
| `workflows/Itzana_Notifications.json` | `OApztbIN8Jhb4JHz` | Email escalation by category (bodas, PR, empleo, escalamiento) |
| `workflows/Itzana_Vectorizar_KB.json` | — | One-time script: load KB_ITZANA.json → MongoDB vectors |

### Knowledge Base

- **Source**: `KBs/KB_ITZANA.json` — 31 chunks (alojamientos, restaurantes, actividades, bodas, ubicación, contacto, políticas)
- **Format per chunk**: `{ id, propiedad: "ITZ", categoria, tags, pregunta, respuesta }`
- **Storage**: MongoDB Atlas, collection `documents`, index `itzana_vector_index` (cosine, 1536 dims)
- **Filter**: all queries pre-filter by `metadata.propiedad = "ITZ"` (multi-property ready)

---

## Credentials in n8n

| Name | ID | Used for |
|---|---|---|
| HOTELS (MongoDB) | `Msw0gTK8f8b192VX` | users, chat_histories, KB vectors (shared cluster) |
| ITZANA (OpenAI) | `PjPavWO5j0jIFtSG` | Audio transcription, image analysis |
| ITZANA-KAANA (OpenRouter) | `J9zb84vhqsx182XW` | Main agent LLM |
| Redis GarooVPS | `8EUkwaZixjCH7szY` | Message batching |
| ManyChat Garoo | `aEvHbFXnmwofChqs` | Send responses to user |
| SMTP Itzana | ⚠️ pending | Escalation emails (Notifications workflow) |

---

## MongoDB Collections (credential: HOTELS)

| Collection | Schema |
|---|---|
| `documents` | KB chunks with `embedding` (1536) + `metadata.propiedad` filter field |
| `users` | Guest profile keyed by `manychat_id`: page_id, propiedad, canal_ingreso, timestamps, has_reservation, datos_completos |
| `chat_histories` | Conversation memory keyed by `manychat_id`, window = 30 messages |

---

## Key Design Decisions

- **Agent output format**: Kaan always returns `{"response": "...", "escalate": bool, "categoria": "info|reserva|bodas_eventos|pr|empleo|escalamiento|off_topic"}`. The `Parse Agent Output` Code node extracts this via regex before sending to ManyChat.
- **User upsert pattern**: `Find User` → `If USER NOT EXIST` → `DATA to CREATE/UPDATE` Set node → `Insert/Update User` (MongoDB v1.2, `fields` param) → `User Data` (selects find or insert result) → AI Agent.
- **Channel routing**: `canal_ingreso` from ManyChat custom fields maps to `instagram/messenger/whatsapp` via `Parameter Type` Set node — required for ManyChat API `content.type`.
- **Multi-property extension**: Add Ka'ana = new KB + same PRINCIPAL with `propiedad: "KAA"`. The vector index preFilter handles isolation.

---

## n8n Expression Syntax

- `=text {{ $json.field }} text` — template string (leading `=` enables expression mode)
- `={{ expression }}` — pure expression (entire value is JS)
- Code nodes use `$json.field` directly (no `{{ }}`)
- Reference other nodes: `$('Node Name').first().json.field`

---

## Status & What's Pending

See `BUILD.md` for the full spec and current state. Short version:

**Done**: KB vectorized, all 3 sub-workflows imported in n8n, PRINCIPAL orchestrator complete.

**Pending before production**:
1. Create SMTP credential in n8n → configure in Itzana_Notifications
2. Get Mr. Diego's email (bodas/eventos) and HR email (empleo) for Notifications routing
3. Configure `hotels-agent` webhook in ManyChat flow for Itz'ana
4. End-to-end test with pinData (Webhook node has Jorge Calderon / "Hola" pinned)
5. Confirm pet policy with hotel (KB chunk marked ⚠️)
