# Today’s Objectives: Local Agent MVP for Offline Field Assistant

**Companion file:** `offline_field_assistant_prd.md`  
**Build window:** Today’s working session  
**Primary goal:** Build a reliable local FastAPI + dashboard scaffold that can run on the Windows mini PC, connect to local Ollama, and be accessed from an Android phone browser over the mini PC/local network.

---

## 1. Purpose of This File

This file narrows the full PRD into today’s build target.

The full PRD describes a larger Offline Field Assistant system with local agents, workspace browsing, Notion-export library browsing, note capture, Whisper transcription, network mode controls, optional TTS, and future ESP32 integration.

Today’s objective is **not** to complete the entire PRD.

Today’s objective is to build a strong, tested, extensible local MVP foundation:

```text
FastAPI backend
+ mobile-friendly local dashboard
+ Ollama integration
+ role-based local agents
+ startup/runbook documentation
+ clear logs
+ placeholder routes/pages for upcoming features
+ testing regime strong enough to reduce risk before deployment to the mini PC
```

This should be built so that the user can copy or clone the project onto the mini PC, install dependencies, start Ollama, pull a model, run the backend, and access the dashboard from an Android phone browser.

---

## 2. Today’s Definition of Success

By the end of today’s implementation, the project should satisfy these core outcomes:

1. The backend starts successfully on a Windows-compatible Python/FastAPI stack.
2. The backend serves a local dashboard at `/`.
3. The backend can bind to `0.0.0.0:8080` so another device on the same network can access it.
4. The dashboard is usable from an Android phone browser.
5. `/api/status` returns a useful structured status object.
6. The app can detect whether Ollama is reachable.
7. The app can call local Ollama when available.
8. The dashboard has an Agents page where the user can choose one of several local agent roles and send a prompt.
9. The project includes prompt files for all core local agent roles.
10. Each agent call is logged to a local JSONL log.
11. Placeholder pages exist for Projects, Library, Notes, Audio Upload, Network, Logs, and Settings.
12. Placeholder endpoints return honest, useful scaffold responses instead of fake completed functionality.
13. The project includes strong setup documentation for the human operator.
14. The project includes a `STARTUP.md` file designed for the local model/agent to read later.
15. The project includes a testing and preflight regime that Claude Code can run before the code is transferred to the mini PC.
16. The project is built with no sensitive credentials and no cloud dependencies required for normal local operation.

The most important field test is:

```text
Android phone opens the local dashboard → user selects an agent → user sends a message → local Ollama responds → response appears on phone → log entry is created.
```

---

## 3. Hard Scope Boundary for Today

Build the foundation, not the entire field assistant.

### 3.1 Build Today

Build these components now:

1. FastAPI backend.
2. Static or lightweight frontend served by the backend.
3. Local Ollama client.
4. Agent service that loads prompt files.
5. Agent chat API.
6. Status API.
7. Logs API.
8. Placeholder APIs for future modules.
9. Mobile-friendly dashboard.
10. Agent role selector UI.
11. Documentation.
12. Tests.
13. Preflight/smoke test scripts.
14. Folder structure that matches the larger PRD.

### 3.2 Stub or Placeholder Today

Create honest placeholders for:

1. Project workspace browsing.
2. Local Notion-export library browsing.
3. Notes list.
4. Audio upload.
5. Whisper transcription.
6. Network mode controls.
7. Settings.

The placeholders should make it clear that the feature is not fully implemented yet, but they should also establish the expected API shape and frontend location.

### 3.3 Do Not Build Today

Do not implement these yet:

1. Real Whisper transcription.
2. Real browser microphone recording.
3. Real audio upload processing.
4. Real Notion export parsing/indexing.
5. Real GitHub clone/pull workflows.
6. Real repo process launching.
7. Real network switching automation.
8. Real Windows hotspot control scripts.
9. TTS.
10. ESP32 integration.
11. Arbitrary shell command execution.
12. File editing tools.
13. A database.
14. Authentication.
15. HTTPS/certificate setup.
16. Private GitHub integration.
17. Any cloud API dependency.

Do not create fake implementations that pretend to do these things. Use clear, honest placeholders.

---

## 4. Target Runtime Environment

### 4.1 Hardware

Target device:

```text
Windows mini PC
AMD Ryzen 3 4300U
8GB RAM
128GB storage
```

Design implications:

1. Keep dependencies light.
2. Keep the frontend simple.
3. Avoid heavy build chains where possible.
4. Avoid multiple local models.
5. Avoid expensive scanning or background loops.
6. Prefer clear logs and simple files over complex systems.

### 4.2 Operating System

Current target OS:

```text
Windows
```

The app should be Windows-friendly:

1. Use Python/FastAPI.
2. Avoid Linux-only assumptions.
3. Use `pathlib` for paths.
4. Avoid shell-specific setup unless documented separately.
5. Include PowerShell-friendly instructions where useful.
6. Do not require WSL.

### 4.3 Network

The app should run locally and be reachable from another device on the same network.

Expected server binding:

```text
host: 0.0.0.0
port: 8080
```

Expected phone access pattern:

```text
http://<mini-pc-local-ip>:8080
```

Network switching automation is out of scope today. The Network page should explain this clearly and provide manual notes only.

---

## 5. Recommended Project Structure

Create or align to this structure:

```text
field-assistant/
  README.md
  START_HERE.md
  STARTUP.md
  RUNBOOK.md
  TODAY_OBJECTIVES.md

  backend/
    app/
      __init__.py
      main.py
      config.py
      ollama_client.py
      agent_service.py
      log_service.py
      startup_checks.py
      routes/
        __init__.py
        status.py
        agents.py
        logs.py
        projects.py
        library.py
        notes.py
        network.py
        settings.py
      schemas/
        __init__.py
        agents.py
        status.py
      storage/
        __init__.py
    requirements.txt

  frontend/
    static/
      index.html
      styles.css
      app.js

  agents/
    operator.agent.md
    coder.agent.md
    librarian.agent.md
    capture.agent.md
    display.agent.md

  workspace/
    repos/

  library/
    notion_exports/
    index.json

  notes/
    inbox/
    processed/
    ready_for_notion/
    archived/

  logs/
    agent_calls.jsonl
    backend.log
    events.jsonl

  tests/
    test_status.py
    test_agents.py
    test_logs.py
    test_placeholders.py

  scripts/
    preflight.py
    smoke_test.py
```

It is acceptable to adjust exact module names if there is a good reason, but the final structure should remain simple, readable, and close to the PRD.

---

## 6. Backend Requirements

### 6.1 Backend Framework

Use:

```text
FastAPI
Uvicorn
Pydantic
Requests or HTTPX for Ollama HTTP calls
```

Avoid unnecessary dependencies.

### 6.2 App Startup Behavior

On startup, the backend should:

1. Load configuration.
2. Create required local folders if missing.
3. Verify agent prompt files exist.
4. Verify log files/folders are writable.
5. Attempt a lightweight Ollama availability check.
6. Log startup status.

Startup should not fail just because Ollama is unavailable. The dashboard should still open and clearly report that Ollama is unavailable.

### 6.3 Configuration

Create a simple config system with sane defaults.

Minimum config values:

```text
APP_NAME=Offline Field Assistant
HOST=0.0.0.0
PORT=8080
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=qwen2.5-coder:3b
FALLBACK_MODEL=qwen2.5-coder:1.5b
WORKSPACE_DIR=workspace
LIBRARY_DIR=library
NOTES_DIR=notes
LOGS_DIR=logs
AGENTS_DIR=agents
```

Config can be environment-variable based, but should work with defaults out of the box.

### 6.4 Required Routes

Implement these routes:

```text
GET  /
GET  /api/status
GET  /api/agents
POST /api/agents/{agent_id}/chat
GET  /api/logs/recent
GET  /api/projects
GET  /api/library
GET  /api/notes
GET  /api/network/status
GET  /api/settings
```

Optional but useful:

```text
POST /api/status/refresh
GET  /api/health
```

### 6.5 `/api/status`

Return a structured status object.

Suggested fields:

```json
{
  "app_name": "Offline Field Assistant",
  "backend": {
    "ok": true,
    "version": "0.1.0",
    "local_time": "2026-05-26T12:00:00"
  },
  "network": {
    "mode": "unknown",
    "host": "0.0.0.0",
    "port": 8080,
    "dashboard_url_hint": "http://<mini-pc-ip>:8080",
    "internet_check": "not_checked"
  },
  "ollama": {
    "available": false,
    "base_url": "http://localhost:11434",
    "default_model": "qwen2.5-coder:3b",
    "fallback_model": "qwen2.5-coder:1.5b",
    "message": "Ollama not reachable or not running."
  },
  "paths": {
    "workspace": "workspace",
    "library": "library",
    "notes": "notes",
    "logs": "logs",
    "agents": "agents"
  },
  "counts": {
    "agents": 5,
    "projects": 0,
    "library_items": 0,
    "notes": 0
  },
  "last_event": "Backend started."
}
```

Status should be useful whether Ollama is online or offline.

### 6.6 `/api/agents`

Return available agents and short descriptions.

Required agent IDs:

```text
operator
coder
librarian
capture
display
```

### 6.7 `/api/agents/{agent_id}/chat`

Request body:

```json
{
  "message": "What is the current system status?",
  "context": "Optional extra context from the dashboard/user.",
  "model": "optional model override"
}
```

Behavior:

1. Validate agent ID.
2. Load the correct prompt file.
3. Build an Ollama-compatible chat request.
4. Include system prompt.
5. Include optional user-provided context.
6. Include user message.
7. Call Ollama.
8. Return response.
9. Log the call to JSONL.

Response body:

```json
{
  "ok": true,
  "agent_id": "operator",
  "model": "qwen2.5-coder:3b",
  "response": "...",
  "log_id": "...",
  "elapsed_ms": 1234
}
```

If Ollama is unavailable:

```json
{
  "ok": false,
  "agent_id": "operator",
  "model": "qwen2.5-coder:3b",
  "error": "Ollama is not reachable at http://localhost:11434.",
  "recovery_hint": "Start Ollama and pull the configured model, then retry."
}
```

Do not crash the backend if Ollama is unavailable.

### 6.8 Placeholder Routes

Placeholder routes must be honest and useful.

For example, `/api/projects` can return:

```json
{
  "ok": true,
  "implemented": false,
  "message": "Project workspace browsing is scaffolded but not fully implemented yet.",
  "workspace_dir": "workspace/repos",
  "items": []
}
```

Do this for Library, Notes, Audio Upload if represented, Network, and Settings as needed.

### 6.9 Logging

Implement JSONL logging.

Minimum logs:

```text
logs/agent_calls.jsonl
logs/events.jsonl
```

Each agent call log should include:

```json
{
  "id": "uuid",
  "timestamp": "...",
  "agent_id": "operator",
  "model": "qwen2.5-coder:3b",
  "message_preview": "first 200 chars",
  "context_preview": "first 200 chars or null",
  "ok": true,
  "elapsed_ms": 1234,
  "error": null
}
```

Do not log huge full prompts by default. Store previews and metadata. The dashboard can show recent logs.

---

## 7. Ollama Integration Requirements

### 7.1 Ollama API

Use the local Ollama HTTP API at:

```text
http://localhost:11434
```

Prefer `/api/chat` if using chat-style messages.

### 7.2 Default Model

Default:

```text
qwen2.5-coder:3b
```

Fallback:

```text
qwen2.5-coder:1.5b
```

### 7.3 Expected Failure Modes

Handle these cleanly:

1. Ollama not installed.
2. Ollama not running.
3. Model not pulled.
4. Ollama running but slow.
5. Ollama returns malformed/failed response.
6. Request timeout.

Return clear errors to the dashboard.

### 7.4 Timeouts

Use reasonable timeouts. Do not hang forever.

Suggested:

```text
availability check: short timeout
chat call: longer timeout
```

Make timeout values configurable.

---

## 8. Agent System Requirements

### 8.1 Agent Prompt Files

Create these files:

```text
agents/operator.agent.md
agents/coder.agent.md
agents/librarian.agent.md
agents/capture.agent.md
agents/display.agent.md
```

Each should be written for a small local model. They should be concise, explicit, and guardrailed.

### 8.2 Shared Agent Rules

All agents should follow these shared principles:

1. Be honest about available context.
2. Do not claim to inspect files unless file contents or summaries were provided.
3. Do not claim to run commands.
4. Do not invent system state.
5. Prefer small next steps.
6. Avoid broad refactors.
7. Avoid secrets.
8. Assume offline/local-first operation.
9. Ask for logs or context when needed.
10. Keep responses readable on a phone.

### 8.3 Operator Agent

Purpose:

Help run and diagnose the local field assistant system.

Responsibilities:

1. Interpret status objects.
2. Explain startup problems.
3. Suggest next operational steps.
4. Diagnose Ollama unavailable/model missing problems.
5. Summarize logs when provided.
6. Recommend recovery steps.

Constraints:

1. Does not edit code.
2. Does not run commands.
3. Does not claim to inspect live system state unless status/log context was provided.

### 8.4 Coder Agent

Purpose:

Help with lightweight code understanding and small local debugging.

Responsibilities:

1. Explain code snippets.
2. Suggest small reversible fixes.
3. Interpret error logs.
4. Help write tiny helper functions.
5. Identify which files may matter based on provided context.

Constraints:

1. No major refactors.
2. No invented files.
3. No claims of repository-wide inspection unless provided.
4. Prefer minimal changes.

### 8.5 Librarian Agent

Purpose:

Help navigate local knowledge/library context.

Responsibilities:

1. Summarize provided page excerpts.
2. Recommend local pages when index data is provided.
3. Create learning path suggestions from provided library metadata.
4. Cite local file paths when provided.

Constraints:

1. Never invent pages.
2. Never pretend to search the whole library unless an index/search result was provided.
3. Prefer uncertainty over hallucination.

### 8.6 Capture Agent

Purpose:

Turn raw voice/text notes into structured note suggestions and later Notion-ready prompts.

Responsibilities:

1. Classify notes.
2. Extract likely title.
3. Summarize raw transcript.
4. Suggest tags.
5. Suggest Notion page type.
6. Generate a Notion-ready prompt when asked.

Constraints:

1. Preserve raw content.
2. Never discard or overwrite transcript/audio references.
3. Keep raw transcript separate from generated summary.
4. Use `unknown` or `uncertain` when unsure.

### 8.7 Display Agent

Purpose:

Compress longer content into phone-friendly display output.

Responsibilities:

1. Produce short summaries.
2. Produce status-card text.
3. Produce 1–3 next actions.
4. Make long output easier to read on phone.

Constraints:

1. Do not introduce new technical claims.
2. Only summarize provided content.
3. Keep output short.

---

## 9. Frontend Requirements

### 9.1 Frontend Style

Use a simple local frontend:

```text
HTML
CSS
Vanilla JavaScript
```

Avoid a build step unless there is a strong reason. No remote CDNs.

### 9.2 Design Goals

The dashboard should feel like a simple field control panel:

1. Mobile-first.
2. Readable on Android phone.
3. Large buttons.
4. Clear status cards.
5. Obvious current page/section.
6. Clear errors.
7. Minimal clutter.
8. Works offline once served.

### 9.3 Required Navigation Sections

Create navigation for:

```text
Home
Agents
Projects
Library
Notes
Audio Upload
Network
Logs
Settings
```

It can be a tab-style single-page app implemented in vanilla JS.

### 9.4 Home Page

Show:

1. App name.
2. Backend status.
3. Ollama status.
4. Default model.
5. Local dashboard URL hint.
6. Workspace/library/notes paths.
7. Last event.
8. Button to refresh status.

### 9.5 Agents Page

This is today’s most important page.

Required UI:

1. Agent role selector.
2. Agent description display.
3. Prompt textarea.
4. Optional context textarea.
5. Send button.
6. Loading state.
7. Response panel.
8. Error panel.
9. Copy response button.
10. Recent call metadata if available.

Agent roles:

```text
Operator
Coder
Librarian
Capture
Display
```

### 9.6 Projects Page

Today’s status:

```text
Scaffold only.
```

Show:

1. Workspace path.
2. Placeholder message.
3. Future feature list.
4. Empty project list from `/api/projects`.

### 9.7 Library Page

Today’s status:

```text
Scaffold only.
```

Show:

1. Library path.
2. Placeholder message.
3. Expected future Notion export index.
4. Empty library list from `/api/library`.

### 9.8 Notes Page

Today’s status:

```text
Scaffold only.
```

Show:

1. Notes path.
2. Placeholder message.
3. Future note pipeline.
4. Empty note list from `/api/notes`.

### 9.9 Audio Upload Page

Today’s status:

```text
Not implemented yet.
```

Show:

1. Clear statement that manual audio upload and Whisper transcription are coming later.
2. Brief planned flow:
   - record on phone
   - upload to dashboard
   - save raw audio
   - transcribe locally
   - classify with Capture Agent
   - generate Notion prompt

Do not build fake upload processing today.

### 9.10 Network Page

Today’s status:

```text
Manual/checklist only.
```

Show:

1. Current backend host/port.
2. Dashboard URL hint.
3. Clear warning that network switching automation is not implemented.
4. Manual reminder:
   - Mini PC and Android phone must be on same network.
   - Use mini PC local IP in Android browser.
   - Windows Firewall may block access.
   - If switching Wi-Fi modes, the dashboard may disconnect.

Do not build real hotspot switching.

### 9.11 Logs Page

Show recent logs from `/api/logs/recent`.

At minimum:

1. Recent agent calls.
2. Recent backend events if available.
3. Errors should be readable.

### 9.12 Settings Page

Show current config values as read-only for now:

1. Model.
2. Ollama base URL.
3. Workspace path.
4. Library path.
5. Notes path.
6. Logs path.
7. Agents path.

No editing required today.

---

## 10. Documentation Requirements

### 10.1 README.md

General project overview.

Include:

1. What this project is.
2. Current build status.
3. What works now.
4. What is scaffolded but not implemented.
5. Link to `START_HERE.md`.

### 10.2 START_HERE.md

Write for the human operator.

Include:

1. Prerequisites.
2. Python setup.
3. Installing dependencies.
4. Installing/running Ollama.
5. Pulling `qwen2.5-coder:3b`.
6. Pulling fallback `qwen2.5-coder:1.5b`.
7. Starting backend on `0.0.0.0:8080`.
8. Opening local dashboard on the mini PC.
9. Finding the mini PC IP address.
10. Opening dashboard from Android phone.
11. Windows Firewall note.
12. First test prompt.
13. Troubleshooting quick links.

### 10.3 STARTUP.md

Write for the local model/agent to read later.

This file should explain:

1. The project identity.
2. The target machine.
3. The local-first design.
4. The no-secrets policy.
5. The available folders.
6. The available agent roles.
7. The model’s limits.
8. How to respond helpfully.
9. How to request missing logs/context.
10. How to avoid hallucinating tool access.
11. How to keep advice safe and small.

### 10.4 RUNBOOK.md

Write for field troubleshooting.

Include sections:

1. Backend will not start.
2. Dashboard does not load locally.
3. Android cannot reach dashboard.
4. Windows Firewall likely blocking access.
5. Wrong IP address.
6. Port already in use.
7. Ollama unavailable.
8. Model not pulled.
9. Model too slow.
10. Agent response fails.
11. Logs missing or unwritable.
12. How to switch default model.
13. How to run tests.
14. How to collect debug info for a stronger coding agent.

---

## 11. Testing Requirements

Testing is a major objective. The project should be checked heavily before being transferred to the mini PC.

### 11.1 Unit/Route Tests

Use pytest and FastAPI TestClient.

Required tests:

1. App imports successfully.
2. `/api/status` returns 200.
3. `/api/status` has expected top-level keys.
4. `/api/agents` returns all five agents.
5. Invalid agent ID returns a clean 404 or 400 with useful JSON.
6. `/api/projects` returns scaffold response.
7. `/api/library` returns scaffold response.
8. `/api/notes` returns scaffold response.
9. `/api/network/status` returns scaffold response.
10. `/api/settings` returns config data.
11. Logs route returns useful structure even if logs are empty.

### 11.2 Mocked Ollama Tests

Do not require real Ollama for all tests.

Implement mocked tests for:

1. Ollama unavailable.
2. Ollama timeout.
3. Ollama successful response.
4. Model missing or error response.
5. Agent chat logs call metadata.

### 11.3 Filesystem Tests

Test that the app can:

1. Create required folders.
2. Read agent prompt files.
3. Write JSONL logs.
4. Handle empty logs.
5. Avoid crashing if optional placeholder files are missing.

### 11.4 Frontend Smoke Checks

At minimum, include a manual smoke checklist.

Better: include a simple script or documented check that verifies:

1. `/` returns HTML.
2. `styles.css` loads.
3. `app.js` loads.
4. `/api/status` can be called from browser JS.

Do not overbuild browser automation unless it is easy.

### 11.5 Preflight Script

Create:

```text
scripts/preflight.py
```

It should check:

1. Python version.
2. Required packages import.
3. Required directories exist or can be created.
4. Agent prompt files exist.
5. Logs directory writable.
6. Ollama base URL reachable or clearly unavailable.
7. Default model status if easy to detect.
8. Backend route smoke tests if feasible.

Output should be clear and human-readable.

### 11.6 Smoke Test Script

Create:

```text
scripts/smoke_test.py
```

It should assume the backend is running and test:

1. GET `/api/status`.
2. GET `/api/agents`.
3. GET `/api/logs/recent`.
4. GET placeholder endpoints.
5. Optional POST to agent chat if Ollama is available.

### 11.7 Deployment Readiness Checklist

Add a checklist to documentation:

```text
Before copying to mini PC:
[ ] pytest passes
[ ] preflight passes or only reports expected Ollama unavailable
[ ] backend starts locally
[ ] dashboard opens locally
[ ] /api/status works
[ ] agent prompts load
[ ] logs are writable
[ ] placeholder pages work

On mini PC:
[ ] Python installed
[ ] dependencies installed
[ ] Ollama installed
[ ] qwen2.5-coder:3b pulled
[ ] backend starts on 0.0.0.0:8080
[ ] dashboard opens locally
[ ] Windows Firewall allows port 8080
[ ] Android phone reaches dashboard
[ ] first agent call succeeds
[ ] log entry created
```

---

## 12. Security Requirements

Today’s implementation must preserve the PRD’s no-secrets design.

Do not include:

1. API keys.
2. Personal access tokens.
3. SSH keys.
4. Private GitHub instructions.
5. Cloud login flows.
6. iCloud/Google sync assumptions.
7. Password storage.
8. Arbitrary shell command execution from the dashboard.

The dashboard must not expose arbitrary file browsing. Placeholder project/library paths are fine, but do not expose the whole Windows filesystem.

---

## 13. Quality Bar

The project should be simple but not sloppy.

Expected quality:

1. Clear module separation.
2. Readable code.
3. Useful errors.
4. Useful logs.
5. Good docs.
6. Tests that prove core routes and failure modes.
7. No fake success states.
8. No hidden cloud dependencies.
9. No fragile frontend build step.
10. Easy to reason about from a phone and from a weak local model.

This is a field machine, not a SaaS product. Robust, inspectable, and boring is good.

---

## 14. Phase Breakdown for Claude Code

Claude Code should work in phases and verify each phase before moving on.

### Phase 1: Repository Scaffold

Tasks:

1. Create folder structure.
2. Add README, START_HERE, STARTUP, RUNBOOK placeholders or drafts.
3. Add backend package structure.
4. Add frontend static folder.
5. Add agents folder and prompt files.
6. Add logs/workspace/library/notes folders with `.gitkeep` where useful.

Validation:

1. Structure matches expected layout.
2. App imports do not fail.
3. Required prompt files exist.

### Phase 2: Backend Core

Tasks:

1. Build FastAPI app.
2. Serve frontend at `/`.
3. Add config module.
4. Add startup folder creation.
5. Add status route.
6. Add placeholder routes.
7. Add logs route.

Validation:

1. `/api/status` works.
2. Placeholder routes work.
3. Static frontend loads.
4. Logs directory is writable.

### Phase 3: Ollama Client

Tasks:

1. Add Ollama availability check.
2. Add chat call wrapper.
3. Add timeout/error handling.
4. Keep backend running when Ollama is unavailable.

Validation:

1. Ollama unavailable path returns clean error.
2. Mocked success path works.
3. Timeout path works or is cleanly handled.

### Phase 4: Agent Service

Tasks:

1. Load agent metadata.
2. Load prompt files.
3. Validate agent IDs.
4. Build chat messages.
5. Call Ollama client.
6. Log calls.

Validation:

1. `/api/agents` returns five agents.
2. Valid agent chat works with mocked Ollama.
3. Invalid agent ID returns clean error.
4. Agent call logging works.

### Phase 5: Frontend Dashboard

Tasks:

1. Create mobile-first dashboard shell.
2. Add navigation sections.
3. Wire Home to `/api/status`.
4. Wire Agents to `/api/agents` and `/api/agents/{agent_id}/chat`.
5. Wire Logs to `/api/logs/recent`.
6. Wire placeholder pages to their routes.
7. Show loading/error states clearly.
8. Add copy response button.

Validation:

1. Dashboard loads without external internet.
2. Status refresh works.
3. Agent selector loads.
4. Chat request displays response or clear Ollama error.
5. Logs page shows recent logs or empty state.
6. Placeholder pages are honest and readable.

### Phase 6: Documentation

Tasks:

1. Complete README.
2. Complete START_HERE.
3. Complete STARTUP.
4. Complete RUNBOOK.
5. Add deployment readiness checklist.
6. Add testing instructions.

Validation:

1. A user can follow START_HERE without needing hidden context.
2. RUNBOOK covers likely Windows/phone/Ollama failures.
3. STARTUP is useful for future local model context.

### Phase 7: Testing and Preflight

Tasks:

1. Add pytest route tests.
2. Add mocked Ollama tests.
3. Add filesystem/log tests.
4. Add preflight script.
5. Add smoke test script.
6. Run tests.
7. Fix failures.

Validation:

1. `pytest` passes.
2. `python scripts/preflight.py` produces useful output.
3. `python scripts/smoke_test.py` works when backend is running.
4. Failure cases are explicit and not silent.

### Phase 8: Final Self-Review

Tasks:

1. Compare implementation against this objectives file.
2. Compare implementation against the PRD only for today’s relevant scope.
3. Remove fake or misleading functionality.
4. Confirm no secrets or dangerous shell endpoints.
5. Confirm the dashboard can work without internet.
6. Confirm instructions mention Android access and Windows Firewall.

Final report should include:

1. Files created/changed.
2. How to run locally.
3. How to test locally.
4. How to deploy to mini PC.
5. How to access from Android phone.
6. What is implemented.
7. What is scaffolded only.
8. Known limitations.
9. Recommended next build phase.

---

## 15. Final Expected State

At the end of today’s Claude Code session, the project should be ready for this mini PC flow:

```text
1. Copy/clone project to mini PC.
2. Install Python dependencies.
3. Install/start Ollama.
4. Pull qwen2.5-coder:3b or fallback model.
5. Start backend on 0.0.0.0:8080.
6. Open dashboard locally on mini PC.
7. Connect Android phone to same network.
8. Open http://<mini-pc-ip>:8080 from Android.
9. Select Operator Agent.
10. Send a test prompt.
11. Receive local model response.
12. Verify log entry was created.
```

That is today’s real victory condition.

Everything else in the larger PRD becomes easier once this local control deck is alive.
