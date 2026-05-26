# PRD: Offline Field Assistant Mini PC

**Project name:** Offline Field Assistant  
**Current hardware:** Windows mini PC with AMD Ryzen 3 4300U, 8GB RAM, 128GB storage  
**Primary interface:** Android phone browser  
**Primary local AI runtime:** Ollama  
**Primary model target:** Qwen2.5-Coder 3B, with fallback to smaller models if performance is poor  
**Current OS decision:** Keep Windows for now  
**Future OS note:** OS migration is out of scope for this PRD  
**Primary design principle:** Local-first, no sensitive credentials, preserve raw inputs, polish later with stronger tools

---

## 1. Executive Summary

This project turns the mini PC into a lightweight offline/local “field assistant” for travel, learning, code startup support, note capture, and local knowledge browsing.

The mini PC will run a local backend, a local dashboard, Ollama, small local models, Whisper transcription, local note storage, and an offline Notion-export library. The Android phone will be the main user interface through a browser-based dashboard served by the mini PC. The mini PC will create its own Wi-Fi network for the Android phone to connect to when operating locally. When internet access is needed, the mini PC can switch to joining the iPhone hotspot to download models, clone public repositories, pull updates, or install packages.

The system should not require private GitHub credentials, cloud API keys, iCloud login, Google account sync, or other sensitive credentials on the mini PC. It should operate primarily from public repositories, local files, locally exported Notion pages, local voice/audio uploads, and local Ollama models.

The product should start simple: a local web dashboard with text input, file/library browsing, local model calls, note capture, and manual audio upload. More advanced features like browser microphone recording, text-to-speech, richer automation, and ESP32 integration can come later.

---

## 2. Product Goals

### 2.1 Main Goals

1. Create a local dashboard served from the mini PC and accessed primarily from an Android phone browser.

2. Let the mini PC operate as a local field server for:
   - local model interaction,
   - public repo startup/debugging,
   - offline note capture,
   - local Notion-export browsing,
   - lightweight code help,
   - local transcription,
   - local status/operations.

3. Use Ollama locally with a small model, starting with Qwen2.5-Coder 3B.

4. Avoid secrets on the mini PC:
   - no private GitHub credentials,
   - no personal SSH keys,
   - no main API keys,
   - no iCloud/Google/password-manager sync,
   - no private account dependency for core operation.

5. Support public GitHub repos:
   - code is written primarily elsewhere with stronger coding tools,
   - public repos are cloned/pulled to the mini PC,
   - the local model helps run, inspect, and make small changes.

6. Support local note capture:
   - manual audio upload from phone,
   - local Whisper transcription,
   - raw audio preservation,
   - local JSON/Markdown note records,
   - Notion-ready prompt generation for later polishing.

7. Support an offline Notion-export library:
   - Notion pages exported/downloaded locally,
   - indexed by the mini PC,
   - browsed from Android dashboard,
   - summarized or routed by a local Librarian Agent.

8. Keep the ESP32 as optional future hardware, not part of the v1 core system.

---

## 3. Non-Goals

1. Do not build a full autonomous coding agent.

2. Do not depend on private credentials on the mini PC.

3. Do not require cloud model APIs for the core workflow.

4. Do not make the ESP32 central to v1.

5. Do not require browser microphone recording in v1.

6. Do not require HTTPS in v1 unless browser microphone recording becomes a priority.

7. Do not expose the whole Windows filesystem through the dashboard.

8. Do not make the mini PC a general-purpose trusted router for sensitive phone activity.

9. Do not build a perfect Notion sync engine in v1.

10. Do not expect the local model to replace Claude Code or other strong coding agents.

---

## 4. Core User Story

The user is traveling and has a small Windows mini PC. They want to use it as a local/offline assistant.

While driving or away from the mini PC, the user talks through ideas with stronger cloud tools on their main devices. Those tools help design or write code in public GitHub repositories. When the user gets to the mini PC, it can connect to the iPhone hotspot to clone or update the public repo. Then the mini PC can operate locally without internet.

The Android phone connects to the mini PC’s local Wi-Fi and opens a browser dashboard. From the dashboard, the user can browse project folders, see startup instructions, ask the local model simple questions, inspect logs, browse local Notion exports, upload audio notes, transcribe them locally, and save them as structured records for later Notion processing.

The mini PC is not expected to be a high-performance AI workstation. It is a local field station: small, scrappy, useful, and offline-first.

---

## 5. Hardware Context

### 5.1 Mini PC

Known specs:

1. AMD Ryzen 3 4300U.
2. 8GB RAM.
3. 128GB storage.
4. Integrated Radeon graphics.
5. Current OS: Windows.
6. Likely low-power mobile APU device.

Design assumptions:

1. It can run Windows, a browser, Python backend, Ollama, and small models.
2. It can run small Whisper models.
3. It can host a local dashboard.
4. It is not powerful enough for large local LLMs.
5. Storage must be managed carefully.
6. Avoid downloading many large models.

### 5.2 Android Phone

Primary user interface.

Expected roles:

1. Connect to mini PC’s Wi-Fi network.
2. Open local dashboard in browser.
3. Browse local pages/files.
4. Type prompts/questions.
5. Upload audio recordings manually.
6. View longer summaries and outputs.
7. Play generated local audio responses later if TTS is added.

### 5.3 iPhone

Internet source only.

Expected roles:

1. Provide hotspot for mini PC downloads/sync.
2. Allow mini PC to clone/pull public repos.
3. Allow model/package downloads when explicitly needed.

Not expected roles:

1. Not the main dashboard.
2. Not the local LAN/router for the whole system.
3. Not used for iCloud login on the mini PC.
4. Not used for sensitive account sync on the mini PC.

### 5.4 ESP32

Future optional add-on only.

Potential later roles:

1. Physical button.
2. Status display.
3. Simple remote control.
4. Tiny screen for short messages.
5. Possible microphone device later.

Out of scope for v1.

---

## 6. Network Design

The system has two major network modes.

---

### 6.1 Mode A: Local Field Mode

In Local Field Mode, the mini PC creates its own Wi-Fi network. The Android phone connects to the mini PC Wi-Fi and opens the dashboard.

Example:

```text
Mini PC broadcasts: FieldAssistantNet
Android phone joins FieldAssistantNet
Android opens: http://<mini-pc-local-ip>:8080
Mini PC serves dashboard/backend locally
```

Local Field Mode is used for:

1. Reading local Notion exports.
2. Browsing project folders.
3. Asking Ollama questions.
4. Uploading audio files from Android.
5. Viewing transcripts and summaries.
6. Inspecting logs.
7. Running offline/local workflows.

Expected internet status:

1. Internet may be unavailable.
2. The system should still work for local files, local model calls, local notes, and dashboard access.
3. Features requiring downloads or public repo pull should be disabled or show “internet unavailable.”

---

### 6.2 Mode B: Internet Sync Mode

In Internet Sync Mode, the mini PC stops broadcasting its own Wi-Fi if needed and joins the iPhone hotspot to access the internet.

Example:

```text
iPhone hotspot ON
Mini PC joins iPhone hotspot
Mini PC clones/pulls public repos
Mini PC downloads models/packages
Mini PC optionally checks for updates
```

Internet Sync Mode is used for:

1. Cloning public GitHub repos.
2. Pulling repo updates.
3. Downloading Ollama models.
4. Downloading Python/Node packages.
5. Running Windows/software updates when intentionally allowed.
6. Installing dependencies.

---

### 6.3 Network Mode Switching Requirement

The dashboard should include a **Network Mode Control** section, but implementation must be careful because switching Wi-Fi modes can disconnect the dashboard.

Desired dashboard controls:

1. Show current network mode:
   - Local Field Mode,
   - Internet Sync Mode,
   - Unknown/Manual.

2. Show current connection:
   - mini PC hotspot active/inactive,
   - connected Wi-Fi network name if available,
   - local dashboard URL,
   - internet reachability status,
   - last sync timestamp.

3. Button: **Switch to Internet Sync Mode**
   - warns that the Android dashboard may disconnect,
   - stops mini PC hotspot if required,
   - joins saved iPhone hotspot profile,
   - runs optional sync actions,
   - logs result.

4. Button: **Switch to Local Field Mode**
   - starts mini PC hotspot,
   - provides network name/password reminder,
   - tells user to reconnect Android phone to mini PC Wi-Fi,
   - restarts/keeps dashboard service available.

5. Button: **Run Sync Then Return to Local Mode**
   - ideal workflow:
     1. warn user,
     2. join iPhone hotspot,
     3. pull selected repos,
     4. download requested packages/models,
     5. restart mini PC local hotspot,
     6. show “reconnect Android to FieldAssistantNet.”

Important constraint:

When the mini PC changes Wi-Fi modes, the Android dashboard connection may drop. Therefore, the UI should not pretend switching is seamless. It should provide clear warnings and recovery instructions.

---

### 6.4 Network Mode Switching Implementation Notes

The implementation may require Windows commands or scripts. The dashboard backend can trigger scripts, but this should be treated as a privileged local operation.

Suggested approach:

1. Create scripts under:

```text
tools/network/
  start_local_hotspot.ps1
  stop_local_hotspot.ps1
  join_iphone_hotspot.ps1
  sync_repos.ps1
  return_to_local_mode.ps1
```

2. The backend exposes safe endpoints:

```text
POST /api/network/start-local
POST /api/network/join-iphone
POST /api/network/sync-and-return
GET  /api/network/status
```

3. The backend should only call known scripts from a fixed folder.

4. The backend should not accept arbitrary shell commands from the dashboard.

5. All network actions should be logged.

6. A manual fallback should be documented in the dashboard and runbook.

7. If Windows hotspot automation is unreliable, keep the dashboard button as a guide/manual checklist first, then automate later.

---

## 7. Security Model

### 7.1 Core Security Position

The mini PC is treated as a low-trust lab machine until it is eventually rebuilt. The system should be useful without storing sensitive credentials.

### 7.2 Allowed

1. Public GitHub repos.
2. Local Ollama models.
3. Local Notion exports.
4. Local audio notes.
5. Local Markdown/JSON records.
6. Temporary non-sensitive files.
7. Local dashboard access from Android phone.
8. iPhone hotspot use for internet downloads.

### 7.3 Avoid

1. Private GitHub repos requiring credentials.
2. SSH private keys.
3. Main API keys.
4. Password manager login.
5. iCloud login.
6. Google account sync.
7. Banking/shopping accounts.
8. Private cloud sync folders.
9. Personal secrets in repo files.
10. Long-lived tokens.

### 7.4 Dashboard Safety

1. Dashboard should be local-network only.
2. Dashboard should bind to local interfaces intentionally.
3. Dashboard should not expose arbitrary command execution.
4. File browser should be scoped to a workspace folder.
5. File write operations should be disabled by default.
6. Network control endpoints should only run fixed scripts.
7. Add a simple local dashboard passcode later if needed.
8. Do not expose dashboard to the public internet.

### 7.5 Android Phone Safety

The local dashboard does not automatically see inside the Android phone.

The dashboard can only access:
1. files selected by the user through upload picker,
2. microphone only if browser mic access is later implemented and permission is granted,
3. browser-local storage for that site,
4. normal web request information.

The dashboard should not require:
1. Android account login,
2. Google sync,
3. special permissions,
4. app installation for v1.

---

## 8. Software Architecture

### 8.1 High-Level Architecture

```text
Android Phone Browser
        |
        | local HTTP
        v
Mini PC Dashboard Frontend
        |
        v
Mini PC Backend API
        |
        |-- Local workspace/repo browser
        |-- Local Notion export library
        |-- Local note capture store
        |-- Whisper transcription service
        |-- Ollama local model service
        |-- Network mode scripts
        |-- Optional TTS service
```

### 8.2 Backend

Recommended backend:

1. Python.
2. FastAPI.
3. Local filesystem storage.
4. Ollama API calls over localhost.
5. Whisper integration.
6. Simple JSON APIs.
7. Structured logs.

### 8.3 Frontend

Recommended frontend:

1. Local web dashboard.
2. Can be generated/designed with Lovable.
3. Exported and served locally.
4. Should work offline.
5. Avoid remote CDNs.
6. Avoid external fonts/scripts unless bundled locally.
7. Mobile-first layout for Android phone.
8. Large buttons and readable status cards.

### 8.4 Local Services

Expected local services:

1. Backend API server.
2. Static frontend server.
3. Ollama service.
4. Whisper transcription runner.
5. Optional TTS runner.
6. Optional background watcher/indexer.

---

## 9. Local Model Plan

### 9.1 Initial Model

Use Ollama with:

```text
qwen2.5-coder:3b
```

Fallback if needed:

```text
qwen2.5-coder:1.5b
```

### 9.2 Expected Use

The local model should help with:

1. explaining errors,
2. summarizing logs,
3. suggesting small code changes,
4. reading runbooks,
5. creating short next-step lists,
6. summarizing local Notion pages,
7. classifying notes,
8. generating Notion-ready prompts,
9. formatting structured dashboard responses.

### 9.3 Not Expected

The local model should not be expected to:

1. write large applications from scratch,
2. perform major refactors,
3. reason across an entire large repo,
4. act autonomously without guardrails,
5. replace strong cloud coding agents,
6. reliably solve complex bugs without clear logs/context.

### 9.4 Prompt Strategy

The system should use different prompt files for different local roles.

Suggested folder:

```text
agents/
  coder.agent.md
  operator.agent.md
  librarian.agent.md
  capture.agent.md
  display.agent.md
```

Same model, different roles.

The harness chooses:
1. which prompt file to use,
2. what context/files to include,
3. what tools/actions are allowed,
4. what JSON schema is expected.

---

## 10. Local Agent Roles

### 10.1 Coder Agent

Purpose:

Help with lightweight local code understanding and small edits.

Responsibilities:

1. Read runbooks.
2. Explain error logs.
3. Suggest next debugging step.
4. Suggest small code edits.
5. Generate tiny helper functions.
6. Summarize what files may matter.

Constraints:

1. Prefer small reversible changes.
2. Do not invent files.
3. Ask for logs/context if missing.
4. Do not perform large refactors.
5. Initially read-only unless file-writing is explicitly added later.

---

### 10.2 Operator Agent

Purpose:

Help run and monitor the local system.

Responsibilities:

1. Check backend health.
2. Check Ollama availability.
3. Check selected repo status.
4. Summarize current system state.
5. Explain last error.
6. Recommend next operational step.
7. Produce concise status text for dashboard.

Constraints:

1. Does not edit code.
2. Does not browse outside allowed workspace.
3. Uses known health endpoints/log files.
4. Returns structured status.

---

### 10.3 Librarian Agent

Purpose:

Navigate and summarize the local Notion-export knowledge library.

Responsibilities:

1. Read library index.
2. Find relevant pages.
3. Summarize selected pages.
4. Recommend next pages.
5. Explain a page more simply.
6. Generate learning paths.
7. Produce page previews for dashboard.

Constraints:

1. Must cite local file/page paths in its response.
2. Must not pretend to read files it was not given.
3. Reads index first.
4. Uses summaries/tags before opening full files.

---

### 10.4 Capture Agent

Purpose:

Turn raw user voice/text notes into structured local records and Notion-ready prompts.

Responsibilities:

1. Classify captured notes.
2. Extract title guess.
3. Generate summary.
4. Assign tags.
5. Identify target page type.
6. Generate Notion AI prompt.
7. Preserve raw transcript/audio references.

Constraints:

1. Never discard raw audio.
2. Never overwrite raw transcript.
3. Keep generated summary separate from raw content.
4. Prefer “uncertain” over hallucinated classification.
5. Do not attempt final polished Notion page in the field.

---

### 10.5 Display Agent

Purpose:

Compress longer agent output into phone/dashboard-friendly and optional tiny-screen-friendly output.

Responsibilities:

1. Create short summaries.
2. Create status cards.
3. Create 1-3 next actions.
4. Create very short display text if needed later.

Constraints:

1. Does not generate new technical conclusions.
2. Only summarizes provided content.
3. Keeps output short.

---

## 11. Dashboard Requirements

### 11.1 Dashboard Home

The home screen should show:

1. System name.
2. Current mode:
   - Local Field Mode,
   - Internet Sync Mode,
   - Unknown.
3. Backend status.
4. Ollama status.
5. Active model.
6. Whisper status.
7. Current workspace.
8. Last note captured.
9. Last transcript.
10. Last agent response.
11. Internet availability.
12. Buttons for main workflows.

### 11.2 Main Navigation

Dashboard sections:

1. Home.
2. Network.
3. Projects.
4. Library.
5. Notes.
6. Audio Upload.
7. Agents.
8. Logs.
9. Settings.

### 11.3 Network Page

Features:

1. Show current Wi-Fi/network status.
2. Show current dashboard URL.
3. Show internet connectivity check.
4. Show local IP.
5. Show hotspot status if detectable.
6. Button: Start Local Field Mode.
7. Button: Switch to Internet Sync Mode.
8. Button: Sync Selected Repos.
9. Button: Sync and Return to Local Mode.
10. Clear warnings before network switching.

### 11.4 Projects Page

Features:

1. List public repos in local workspace.
2. Show repo status:
   - present/missing,
   - last pulled,
   - branch,
   - run instructions available/missing.
3. Open README.
4. Open START_HERE/RUNBOOK if present.
5. Run health check if project defines one.
6. Ask Coder Agent about this project.
7. Ask Operator Agent to inspect logs.

### 11.5 Library Page

Features:

1. Browse local Notion export library.
2. Open page.
3. Render Markdown/HTML where possible.
4. Search by title/tag/summary.
5. Ask Librarian Agent.
6. Summarize selected page.
7. Show related pages.
8. Generate learning path.
9. Save “read later” marker locally.

### 11.6 Notes Page

Features:

1. List captured notes.
2. Filter by status/type.
3. Open note details.
4. Show audio file path.
5. Show transcript.
6. Show summary.
7. Show classification.
8. Show generated Notion prompt.
9. Mark as ready for Notion.
10. Mark as imported/archived.

### 11.7 Audio Upload Page

Features:

1. Manual file upload from Android.
2. Accept common audio formats.
3. Save raw audio locally.
4. Trigger transcription.
5. Show transcription status.
6. Show transcript preview.
7. Send transcript to Capture Agent.
8. Save structured note.

Important:

V1 uses manual file upload instead of browser microphone recording to avoid HTTPS complexity.

### 11.8 Agents Page

Features:

1. Text input.
2. Choose role:
   - Operator,
   - Coder,
   - Librarian,
   - Capture,
   - Display.
3. Show model used.
4. Show included context.
5. Show structured output.
6. Save response if useful.
7. Copy response.

### 11.9 Logs Page

Features:

1. Backend logs.
2. Agent calls.
3. Transcription jobs.
4. Note creation events.
5. Network mode actions.
6. Errors/warnings.
7. Recent actions timeline.

### 11.10 Settings Page

Features:

1. Workspace path.
2. Library path.
3. Notes path.
4. Model name.
5. Whisper model selection.
6. Network SSID names.
7. Saved repo list.
8. Feature toggles.
9. Danger zone for reset/cleanup.

---

## 12. File and Folder Structure

Suggested project structure:

```text
field-assistant/
  README.md
  START_HERE.md
  RUNBOOK.md

  backend/
    app/
      main.py
      config.py
      routes/
      services/
      agents/
      schemas/
      storage/
    requirements.txt

  frontend/
    package.json
    src/
    public/

  agents/
    coder.agent.md
    operator.agent.md
    librarian.agent.md
    capture.agent.md
    display.agent.md

  schemas/
    operator_status.schema.json
    capture_note.schema.json
    librarian_response.schema.json
    code_help.schema.json

  tools/
    network/
      start_local_hotspot.ps1
      stop_local_hotspot.ps1
      join_iphone_hotspot.ps1
      sync_repos.ps1
      return_to_local_mode.ps1
    repo/
    whisper/
    tts/

  workspace/
    repos/

  library/
    notion_exports/
    index.json
    summaries/

  notes/
    inbox/
    processed/
    ready_for_notion/
    archived/

  logs/
    backend.log
    agent_calls.jsonl
    transcription_jobs.jsonl
    network_actions.jsonl
```

---

## 13. Local Notion Export Library

### 13.1 Purpose

Use Notion as the polished knowledge authoring system, then export/download pages locally for offline use.

The mini PC does not need live Notion access. It reads exported local files.

### 13.2 Library Input

Supported initial inputs:

1. Markdown files.
2. CSV files.
3. HTML files.
4. Exported asset folders.
5. Manually curated notes.

### 13.3 Indexing

The system should generate:

```text
library/index.json
```

Each item should include:

1. ID.
2. Title.
3. Path.
4. Source type.
5. Tags.
6. Summary.
7. Created/imported timestamp.
8. Related pages.
9. Topic/category.
10. Reading status if available.

Example:

```json
{
  "id": "esp32-i2s-microphone",
  "title": "ESP32-S3 I2S Microphone Notes",
  "path": "library/notion_exports/esp32/audio/esp32-i2s-microphone.md",
  "tags": ["esp32", "audio", "i2s", "microphone"],
  "summary": "Notes on capturing audio from an ESP32-S3 microphone and sending clips to the mini PC.",
  "related": ["local-whisper", "audio-upload-pipeline"],
  "status": "available"
}
```

### 13.4 Librarian Behavior

The Librarian Agent should:

1. Search index first.
2. Present relevant page options.
3. Open one page at a time.
4. Summarize selected page.
5. Recommend next page.
6. Produce concise learning routes.
7. Avoid hallucinating missing pages.

---

## 14. Note Capture System

### 14.1 Capture Philosophy

The system should prioritize capturing raw thoughts quickly and safely.

Do not require polished notes in the field.

Preserve:

1. raw audio,
2. raw transcript,
3. local classification,
4. generated prompt,
5. final import status.

### 14.2 Capture Types

Supported note types:

1. General note.
2. Learning request.
3. Project idea.
4. Code change request.
5. Bug report.
6. Local command.
7. Future Notion page.
8. Research question.
9. Reminder-style thought.
10. Unknown/uncertain.

### 14.3 Note Folder Format

Each captured note should become a folder:

```text
notes/inbox/2026-06-14_1532_learn-esp32-i2s/
  audio.m4a
  transcript_raw.txt
  note.json
  notion_prompt.md
  status.txt
```

### 14.4 Note JSON

Example:

```json
{
  "id": "2026-06-14_1532_learn-esp32-i2s",
  "created_at": "2026-06-14T15:32:00",
  "source": "manual_audio_upload",
  "intent": "learning_request",
  "title_guess": "Learn ESP32 I2S microphone capture",
  "raw_audio_path": "audio.m4a",
  "raw_transcript_path": "transcript_raw.txt",
  "summary": "User wants a learning page about ESP32-S3 microphone capture and sending audio to the mini PC.",
  "suggested_notion_page_type": "Learning Page",
  "tags": ["esp32", "i2s", "audio", "field-assistant"],
  "status": "notion_prompt_ready"
}
```

### 14.5 Generated Notion Prompt

The Capture Agent should create a Markdown prompt that can later be pasted into Notion AI or a stronger agent.

Example intent:

```text
Create a polished Notion learning page from this raw field note.

Page type: Learning Page
Topic: ESP32-S3 microphone capture
Audience: Electromechanical engineer learning AI, IoT, and Python
Include:
- simple explanation
- relevant hardware assumptions
- terminology
- practical next experiments
- checklist
- related pages to create
- open questions

Raw transcript:
...
```

---

## 15. Audio and Transcription

### 15.1 V1 Audio Input

V1 uses manual audio file upload from Android browser.

Flow:

```text
Record audio in phone voice recorder
Open dashboard
Upload audio file
Mini PC saves audio
Mini PC runs Whisper
Transcript appears in dashboard
Capture Agent classifies it
Note is saved
```

### 15.2 Browser Mic Deferred

Browser microphone recording is deferred because it may require HTTPS.

Do not block v1 on HTTPS/certificate setup.

### 15.3 Whisper

Use local Whisper with small models.

Initial target:

1. tiny/base model.
2. Short notes first.
3. Longer recordings later with chunking.

### 15.4 Long Audio Handling

For longer audio, the system should eventually:

1. split into chunks,
2. transcribe chunks,
3. save chunk transcripts,
4. create combined transcript,
5. summarize sections,
6. create final capture record.

---

## 16. Text-to-Speech

### 16.1 Status

Optional feature after core dashboard/note workflow works.

### 16.2 Possible Engines

1. eSpeak NG for simple robotic speech.
2. Piper TTS for better local voice.
3. Other models later only if performance allows.

### 16.3 Use Cases

1. Read short status.
2. Read short summaries.
3. Confirm note saved.
4. Confirm transcription complete.
5. Read next action.

### 16.4 Non-Goals

1. Do not read long pages aloud in v1.
2. Do not make TTS required for basic use.
3. Do not block note capture on TTS.

---

## 17. Public Repo Workflow

### 17.1 External Coding Flow

Primary coding flow:

```text
Strong tools elsewhere write serious code
Public GitHub repo stores code
Mini PC clones/pulls repo
Local model helps run and lightly debug
```

### 17.2 Repo Standards

Every repo intended for the mini PC should include:

1. `README.md`
2. `START_HERE.md`
3. `RUNBOOK.md`
4. setup instructions,
5. run command,
6. test command,
7. health check endpoint if applicable,
8. expected logs,
9. troubleshooting section,
10. known limitations.

### 17.3 Local Model-Friendly Design

Repos should be designed so a weak local model can help.

Use:

1. obvious folder names,
2. simple scripts,
3. clear logs,
4. small modules,
5. explicit config,
6. structured error messages,
7. comments where useful,
8. tests with readable failures.

### 17.4 Project Startup Flow

Dashboard should let user:

1. select repo,
2. open runbook,
3. check dependencies,
4. start project,
5. view logs,
6. ask Operator Agent what is wrong,
7. ask Coder Agent for small fix suggestions.

---

## 18. API Design

### 18.1 Core Routes

Suggested backend API routes:

```text
GET  /api/status
GET  /api/config
GET  /api/logs/recent

GET  /api/network/status
POST /api/network/start-local
POST /api/network/join-iphone
POST /api/network/sync-and-return

GET  /api/projects
GET  /api/projects/{project_id}
GET  /api/projects/{project_id}/readme
POST /api/projects/{project_id}/health-check

GET  /api/library
GET  /api/library/search?q=
GET  /api/library/page/{page_id}
POST /api/library/page/{page_id}/summarize

GET  /api/notes
GET  /api/notes/{note_id}
POST /api/notes/upload-audio
POST /api/notes/{note_id}/transcribe
POST /api/notes/{note_id}/classify
POST /api/notes/{note_id}/generate-notion-prompt

POST /api/agents/operator
POST /api/agents/coder
POST /api/agents/librarian
POST /api/agents/capture
POST /api/agents/display
```

### 18.2 Status Object

The dashboard should consume a structured status object.

Example:

```json
{
  "system_status": "ready",
  "network_mode": "local_field",
  "internet_available": false,
  "ollama": {
    "available": true,
    "model": "qwen2.5-coder:3b"
  },
  "whisper": {
    "available": true,
    "model": "base"
  },
  "workspace": {
    "path": "C:/field-assistant/workspace",
    "repo_count": 3
  },
  "library": {
    "indexed_pages": 42,
    "last_indexed_at": "2026-06-14T11:22:00"
  },
  "notes": {
    "inbox_count": 4,
    "ready_for_notion_count": 2
  },
  "last_event": "Audio note transcribed successfully."
}
```

---

## 19. Data Storage

### 19.1 Storage Style

Use local filesystem-first storage.

Avoid database complexity in v1 unless needed.

Use:

1. JSON files.
2. JSONL logs.
3. Markdown files.
4. Plain folders.
5. Audio files.

### 19.2 Why Filesystem First

Benefits:

1. easy to inspect,
2. easy to back up,
3. easy for local model to reason about,
4. easy to import/export,
5. fewer moving parts,
6. works offline.

### 19.3 Later Database Option

SQLite can be added later if needed for:

1. search,
2. indexing,
3. metadata queries,
4. note status tracking,
5. dashboard performance.

Do not require SQLite in the first prototype unless it simplifies implementation.

---

## 20. Logging and Diagnostics

The project should heavily emphasize logs because the local model is weak and needs clear evidence.

Log categories:

1. backend startup,
2. dashboard requests,
3. Ollama calls,
4. Whisper jobs,
5. note creation,
6. library indexing,
7. network mode changes,
8. repo sync,
9. project startup,
10. errors.

Use JSONL for machine-readable logs:

```text
logs/agent_calls.jsonl
logs/transcription_jobs.jsonl
logs/network_actions.jsonl
```

Every major action should have:

1. timestamp,
2. action type,
3. input summary,
4. output summary,
5. status,
6. error if any,
7. path references.

---

## 21. Performance Constraints

### 21.1 Hardware Limits

The mini PC has limited RAM/storage.

Design accordingly:

1. avoid giant models,
2. avoid multiple models loaded simultaneously,
3. avoid huge context prompts,
4. avoid scanning huge libraries repeatedly,
5. index once and reuse metadata,
6. keep audio chunk sizes reasonable,
7. avoid heavy browser/dashboard assets.

### 21.2 Expected Model Use

Use focused prompts:

1. one file/page/log at a time,
2. short task instructions,
3. JSON schema output,
4. retrieved context only,
5. avoid broad “understand the whole project” requests.

### 21.3 Model Load Strategy

Start with one model.

Do not add model switching until necessary.

---

## 22. Success Criteria

### 22.1 MVP Success

The MVP is successful when:

1. Android phone can open local dashboard from mini PC.
2. Dashboard shows system status.
3. Ollama model can be queried from dashboard.
4. User can browse a local workspace folder.
5. User can browse local Notion-export library index.
6. User can upload an audio file.
7. Mini PC saves the raw audio file.
8. Mini PC transcribes audio locally.
9. Capture Agent classifies the note.
10. System creates `note.json`.
11. System creates `notion_prompt.md`.
12. User can view the note and prompt on dashboard.
13. User can connect mini PC to iPhone hotspot when internet is needed.
14. User can clone/pull a public repo.
15. System can return to local dashboard mode with clear instructions.

### 22.2 Good v1 Success

The system is good enough when:

1. User can use it during travel without private credentials.
2. User can capture messy voice notes and trust they are preserved.
3. User can later turn those notes into Notion pages.
4. User can ask the local model simple questions about local files/pages.
5. User can start a public repo project with runbook help.
6. Dashboard is readable and pleasant on Android phone.
7. Logs are clear enough that stronger agents can debug issues later.

---

## 23. Risks and Mitigations

### 23.1 Windows Network Automation Risk

Risk:

Switching between mini PC hotspot and iPhone hotspot may be unreliable or disconnect the dashboard.

Mitigation:

1. Make network switching manual/checklist-first.
2. Add automation only after manual flow is proven.
3. Warn user before dashboard disconnect.
4. Provide recovery instructions.
5. Log every network action.

### 23.2 Local Model Capability Risk

Risk:

Qwen2.5-Coder 3B may be too weak for some tasks.

Mitigation:

1. Use focused prompts.
2. Give exact files/logs.
3. Build strong runbooks.
4. Use structured outputs.
5. Keep tasks small.
6. Use stronger tools elsewhere for major coding.

### 23.3 Storage Risk

Risk:

128GB fills quickly with models/audio/repos.

Mitigation:

1. Limit models.
2. Compress/archive old audio.
3. Add cleanup screen.
4. Show storage usage.
5. Keep only necessary repos.
6. Avoid large datasets.

### 23.4 Security Risk

Risk:

Low-trust Windows image could expose secrets.

Mitigation:

1. No secrets.
2. Public repos only.
3. Local models only.
4. No main accounts.
5. Avoid private files.
6. Rebuild OS later outside this PRD.

### 23.5 Browser Mic/HTTPS Risk

Risk:

Browser mic does not work over local HTTP.

Mitigation:

1. Use manual audio upload in v1.
2. Add HTTPS later only if needed.
3. Consider phone automation later.

### 23.6 Notion Export Messiness

Risk:

Notion exports may produce imperfect Markdown/CSV/HTML.

Mitigation:

1. Build indexer tolerant of mixed formats.
2. Use simple metadata extraction.
3. Allow manual cleanup.
4. Prefer Markdown where possible.
5. Do not assume perfect Notion structure.

---

## 24. Development Phases

### Phase 0: Setup and Smoke Test

Goals:

1. Install Ollama.
2. Pull small model.
3. Create workspace folder.
4. Start a basic backend.
5. Open test page from Android phone.

Deliverables:

1. `START_HERE.md`
2. simple backend `/api/status`
3. simple dashboard home page
4. Ollama connectivity test

Exit criteria:

1. Android can open dashboard.
2. Dashboard shows backend OK.
3. Backend can query Ollama.

---

### Phase 1: Dashboard and Local Agent Text Input

Goals:

1. Build mobile-friendly dashboard.
2. Add text prompt input.
3. Add agent role selection.
4. Add Operator/Coder basic calls.

Deliverables:

1. Home page.
2. Agents page.
3. status object.
4. logs page.
5. agent prompt files.

Exit criteria:

1. User can ask local model a text question.
2. Agent response appears in dashboard.
3. Calls are logged.

---

### Phase 2: Project Workspace and Public Repo Support

Goals:

1. Browse local workspace.
2. List cloned public repos.
3. Show README/RUNBOOK.
4. Add simple repo sync workflow.

Deliverables:

1. Projects page.
2. file browser scoped to workspace.
3. repo metadata.
4. sync instructions/scripts.

Exit criteria:

1. User can view repo files from dashboard.
2. User can open runbook.
3. User can ask Coder/Operator about selected project.

---

### Phase 3: Local Notion Export Library

Goals:

1. Add local library folder.
2. Build indexer.
3. Browse pages from dashboard.
4. Summarize selected page.

Deliverables:

1. `library/index.json`
2. Library page.
3. Librarian Agent.
4. summarize page route.

Exit criteria:

1. User can open exported Notion pages locally.
2. User can ask for summary.
3. User can see related pages.

---

### Phase 4: Manual Audio Upload and Whisper

Goals:

1. Upload audio file from Android.
2. Save raw audio.
3. Run local transcription.
4. Show transcript.

Deliverables:

1. Audio Upload page.
2. transcription job log.
3. audio storage folder.
4. transcript display.

Exit criteria:

1. User can upload audio.
2. System saves original file.
3. System creates transcript.
4. Transcript appears on dashboard.

---

### Phase 5: Capture Agent and Notion-Ready Prompts

Goals:

1. Classify transcript.
2. Create note folder.
3. Generate note JSON.
4. Generate Notion prompt.

Deliverables:

1. Capture Agent.
2. note folder format.
3. `note.json`
4. `notion_prompt.md`
5. Notes page.

Exit criteria:

1. User can upload a voice note.
2. System creates structured note.
3. System creates a prompt for later Notion use.
4. User can view/copy prompt.

---

### Phase 6: Network Mode Control

Goals:

1. Show current network status.
2. Add manual network instructions.
3. Add scripts if reliable.
4. Add buttons with warnings.

Deliverables:

1. Network page.
2. network status endpoint.
3. scripts/checklists.
4. sync-and-return workflow if feasible.

Exit criteria:

1. User understands current mode.
2. User can intentionally switch modes.
3. System does not hide disconnect risk.
4. Recovery steps are clear.

---

### Phase 7: Optional TTS

Goals:

1. Add local TTS engine.
2. Generate short audio responses.
3. Play audio in dashboard.

Deliverables:

1. TTS service.
2. response audio endpoint.
3. dashboard audio player.

Exit criteria:

1. System can speak short status/summary.
2. TTS is optional and non-blocking.

---

### Phase 8: Optional ESP32 Note

ESP32 remains outside the core product.

Potential future uses:

1. hardware button,
2. tiny status screen,
3. remote trigger,
4. simple “system ready” display,
5. later audio capture experiment.

Do not integrate ESP32 until the Android dashboard workflow is already valuable.

---

## 25. Prompting Guidance for Coding Agents

When using a strong coding agent to build this project, include these instructions:

1. Prioritize a working local MVP over clever architecture.
2. Keep secrets out of the project.
3. Assume the target machine is low-power.
4. Optimize for readability and diagnostics.
5. Create explicit runbooks.
6. Use fixed directories and safe file scopes.
7. Do not expose arbitrary shell execution.
8. Make every local model call logged and inspectable.
9. Preserve raw audio and raw transcript.
10. Use JSON schemas for agent responses.
11. Make the Android dashboard mobile-first.
12. Keep offline mode functional.
13. Treat network switching as risky and user-visible.
14. Make failure states obvious.
15. Add tests for indexing, note creation, and status endpoints.
16. Avoid dependencies that are heavy or fragile on Windows.
17. Use local files before introducing databases.
18. Build in small phases with clear smoke tests.

---

## 26. Acceptance Tests

### 26.1 System Status

1. Start backend.
2. Open dashboard from Android.
3. Confirm `/api/status` returns healthy JSON.
4. Confirm dashboard displays backend/model/library/note status.

### 26.2 Ollama

1. Confirm Ollama service is running.
2. Query model from backend.
3. Confirm response appears on dashboard.
4. Confirm call is logged.

### 26.3 Workspace Browser

1. Place test repo in workspace.
2. Open Projects page.
3. Confirm repo appears.
4. Open README/RUNBOOK.
5. Ask Coder Agent about selected repo.

### 26.4 Library Index

1. Add sample Markdown pages.
2. Run indexer.
3. Confirm pages appear in Library.
4. Open page.
5. Summarize page.
6. Confirm summary includes page path.

### 26.5 Audio Upload

1. Upload small audio file from Android.
2. Confirm raw audio saved.
3. Confirm transcription created.
4. Confirm transcript visible.

### 26.6 Capture Note

1. Use transcript containing “learning request.”
2. Run Capture Agent.
3. Confirm note folder created.
4. Confirm `note.json` created.
5. Confirm `notion_prompt.md` created.
6. Confirm dashboard shows note.

### 26.7 Network Page

1. Open Network page.
2. Confirm current status displays.
3. Confirm warning appears before switching.
4. Confirm manual recovery instructions are visible.
5. Confirm network actions log even if script fails.

---

## 27. Open Questions

1. What exact Windows version and hotspot behavior does the mini PC support?

2. Can the mini PC reliably broadcast Wi-Fi while also switching back and forth from iPhone hotspot?

3. Should network switching begin as manual instructions only, then become scripted later?

4. What Android browser will be used?

5. What audio format will the voice recorder app produce?

6. Which Whisper implementation will be easiest on Windows?

7. Is Qwen2.5-Coder 3B fast enough on this machine?

8. How large will the Notion export library be?

9. Should SQLite be added for library/note indexing, or are JSON files enough?

10. What is the minimum dashboard design needed before Lovable polish?

11. How should generated Notion prompts be imported later?

12. Should note capture support multiple templates such as Learning Page, Bug Report, Project Change, and General Note?

13. How much local TTS is actually useful?

---

## 28. Final Direction

The product direction is:

```text
A Windows mini PC acts as a local/offline field assistant.
The Android phone is the main UI through a local dashboard.
The mini PC runs Ollama, local agents, local file browsing, local Notion-export library, Whisper transcription, and note capture.
The iPhone hotspot is used only when the mini PC needs internet.
No sensitive credentials are required.
The system preserves raw notes/audio and generates prompts for later Notion polishing.
The ESP32 is optional future hardware and is not part of the v1 core.
```

The highest-value first build is:

```text
Local dashboard
+ Ollama text agent
+ workspace browser
+ Notion export library
+ manual audio upload
+ Whisper transcription
+ Capture Agent
+ Notion-ready prompt generation
```

Build this first. Everything else can wait.
