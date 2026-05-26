# LOCAL_AGENT_CONTEXT.md — Compact Reference for Local Model

Version: 0.1.0 | Hardware: AMD Ryzen 3 4300U, 8GB RAM, 128GB, Windows | Model: qwen2.5-coder:3b

---

## App capabilities (implemented)

- FastAPI backend on 0.0.0.0:8080
- Mobile dashboard at http://<ip>:8080
- 5 agent roles: operator, coder, librarian, capture, display
- Agent chat via local Ollama (/api/agents/{id}/chat)
- JSONL logging: logs/agent_calls.jsonl + logs/events.jsonl
- System status: /api/status (Ollama availability, paths, last event)
- Placeholder routes: /api/projects, /api/library, /api/notes, /api/network/status, /api/settings

## App capabilities (scaffolded, NOT implemented)

- Repo workspace browsing (returns empty JSON with message)
- Notion library index browsing (returns empty JSON with message)
- Notes list (returns empty JSON with message)
- Audio upload (UI shows planned flow only)
- Network mode automation (manual checklist only)
- Settings editing (read-only)
- Whisper transcription (not built)
- Any cloud/internet feature (explicitly excluded)

---

## Exact endpoints

```
GET  /                           index.html dashboard
GET  /static/styles.css          CSS
GET  /static/app.js              JS
GET  /api/health                 {"ok": true}
GET  /api/status                 full status object
GET  /api/agents                 list of 5 agent definitions
POST /api/agents/{id}/chat       {message, context?, model?} → {ok, response/error, log_id, elapsed_ms}
GET  /api/logs/recent?limit=50   {ok, count, logs: [...]}
GET  /api/projects               placeholder
GET  /api/library                placeholder
GET  /api/notes                  placeholder
GET  /api/network/status         placeholder
GET  /api/settings               read-only config
```

## Agent IDs

`operator` `coder` `librarian` `capture` `display`

## Valid agent chat response shapes

Success:
```json
{"ok": true, "agent_id": "operator", "model": "qwen2.5-coder:3b", "response": "...", "log_id": "abc12345", "elapsed_ms": 1234}
```

Failure:
```json
{"ok": false, "agent_id": "operator", "model": "qwen2.5-coder:3b", "error": "...", "error_type": "connect_error", "recovery_hint": "...", "log_id": "...", "elapsed_ms": 5}
```

Error types: `connect_error`, `timeout`, `http_error`, `invalid_agent`, `missing_prompt`, `unknown`

---

## Key folders

```
agents/                 system prompt .md files (one per agent)
backend/app/            Python source code
frontend/static/        index.html, styles.css, app.js
workspace/repos/        for cloned public repos (no credentials)
library/notion_exports/ for copied Notion export files
library/index.json      library index (needs rebuild script)
notes/inbox/            new raw notes
notes/processed/        structured notes
notes/ready_for_notion/ notes for eventual Notion import
notes/archived/         older notes
logs/events.jsonl       backend events (startup, errors)
logs/agent_calls.jsonl  agent call history
```

---

## Startup sequence

1. `run_startup_checks()` creates missing dirs, checks agent files, pings Ollama
2. Startup event written to logs/events.jsonl
3. FastAPI starts serving on 0.0.0.0:8080
4. Dashboard available at /

If Ollama is unavailable at startup: backend still starts, Ollama shown as Offline in dashboard.

---

## Configuration (env vars → defaults)

```
FIELD_APP_HOST          → 0.0.0.0
FIELD_APP_PORT          → 8080
FIELD_APP_MODEL         → qwen2.5-coder:3b
FIELD_FALLBACK_MODEL    → qwen2.5-coder:1.5b
FIELD_OLLAMA_URL        → http://localhost:11434
FIELD_OLLAMA_CHECK_TIMEOUT → 3.0
FIELD_OLLAMA_CHAT_TIMEOUT  → 120.0
FIELD_WORKSPACE_PATH    → workspace
FIELD_LIBRARY_PATH      → library
FIELD_NOTES_PATH        → notes
FIELD_LOGS_PATH         → logs
FIELD_AGENTS_PATH       → agents
```

---

## Known failure modes

| Mode | Symptom | Recovery |
|------|---------|----------|
| Ollama not running | /api/status ollama.available=false | Run `ollama serve` |
| Model not pulled | agent chat returns http_error | `ollama pull qwen2.5-coder:3b` |
| Model timeout | error_type=timeout | Use fallback model or shorter prompt |
| Port in use | Backend won't start | `netstat -aon \| findstr 8080` then kill |
| Firewall blocking | Android can't reach dashboard | Add firewall rule for TCP 8080 |
| Wrong IP | Android gets "site can't be reached" | `ipconfig \| findstr IPv4` |
| Missing agent file | error_type=missing_prompt | Restore agents/*.agent.md from git |

---

## Security constraints

No credentials of any kind are stored here:
- No GitHub tokens, SSH keys, private repo access
- No Hugging Face login
- No Notion API keys
- No cloud API keys
- No passwords

Model provisioning: `ollama pull` over temporary internet OR GGUF sneakernet from trusted machine.
Notion content: export on trusted machine, copy files to library/notion_exports/ manually.

---

## Next likely development steps

1. Library index builder: scan library/notion_exports/, write library/index.json
2. Notes CRUD API: create note, list notes, move note between folders
3. Audio upload endpoint: save file to notes/inbox/, return file path
4. Whisper transcription: POST /api/notes/transcribe, calls local Whisper on audio file
5. Network status improvement: detect actual network mode, check internet
6. Repo listing: scan workspace/repos/, return list of repo names and basic info
