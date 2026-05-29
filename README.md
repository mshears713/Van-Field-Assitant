# Offline Field Assistant

A local-first AI assistant that runs on a Windows mini PC and is controlled from an Android phone browser.

**Version:** 0.1.0 (MVP)  
**Backend:** FastAPI + Python  
**AI Runtime:** Ollama (local, no internet required for inference)  
**Default Model:** qwen2.5-coder:3b  
**Primary Interface:** Android phone browser over local LAN  
**Design Principle:** Local-first, offline-first, no secrets, no cloud dependencies  

---

## What works now (v0.1.0)

- FastAPI backend serving the dashboard and API
- Mobile-friendly dashboard with 9 sections
- 5 local agent roles: Operator, Coder, Librarian, Capture, Display
- Agent chat via local Ollama (text in, text out)
- Structured status API (`/api/status`)
- JSONL logging for all agent calls and backend events
- Placeholder routes for Projects, Library, Notes, Network, Settings

## What is scaffolded (not yet implemented)

- Project workspace browsing (folder exists, no repo listing yet)
- Notion export library indexing (folder exists, no index builder yet)
- Notes list and capture pipeline (folders exist, no UI pipeline yet)
- Audio upload and local Whisper transcription
- Network mode switching automation

## What is not built yet

Whisper, browser microphone, audio processing, Notion parsing, GitHub workflows,
TTS, ESP32, database, authentication, HTTPS, arbitrary shell execution.

---

## Quick start

See [START_HERE.md](START_HERE.md) for the complete setup guide.

**Minimum steps:**
```
# [MINI PC] Install dependencies
pip install -r backend/requirements.txt

# [MINI PC] Start Ollama and pull the model
ollama pull qwen2.5-coder:3b

# [MINI PC] Start the backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080

# [MINI PC] Open in browser
http://localhost:8080

# [ANDROID] Open in Android browser
http://<mini-pc-ip>:8080
```

## Key files

| File | Purpose |
|------|---------|
| `START_HERE.md` | Complete human install guide |
| `STARTUP.md` | Context file for the local model to read at startup |
| `RUNBOOK.md` | Field troubleshooting procedures |
| `DEBUGGING.md` | Detailed debugging guide |
| `LOCAL_AGENT_CONTEXT.md` | Compact machine-readable reference |
| `TESTING.md` | Testing and preflight procedures |
| `backend/app/main.py` | FastAPI application entry point |
| `agents/*.agent.md` | System prompts for each agent role |
| `frontend/static/` | Dashboard HTML/CSS/JS |
| `logs/` | JSONL log files (created on startup) |

## Project structure

```
Van-Field-Assitant/
├── backend/app/         FastAPI application
├── frontend/static/     Dashboard HTML/CSS/JS
├── agents/              Agent prompt files
├── workspace/repos/     For cloning public repos
├── library/             Notion exports and index
├── notes/               Note capture pipeline folders
├── logs/                JSONL log files
├── tests/               pytest test suite
└── scripts/             preflight.py and smoke_test.py
```

## PRD

Full product requirements: [offline_field_assistant_prd.md](offline_field_assistant_prd.md)  
Today's build objectives: [todays_objectives_local_agent_mvp.md](todays_objectives_local_agent_mvp.md)
