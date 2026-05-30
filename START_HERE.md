# START HERE — Offline Field Assistant Setup Guide

This is the complete setup guide for deploying the Offline Field Assistant on your Windows mini PC.

**Each step is labeled:**
- `[TRUSTED MACHINE]` — do this on your laptop/desktop
- `[COPY TO MINI PC]` — transfer files from trusted machine to mini PC
- `[MINI PC]` — run directly on the mini PC
- `[ANDROID]` — do this on your Android phone

---

## Prerequisites

**[MINI PC]** You need:
- Windows (any recent version)
- Python 3.9 or later — download from https://www.python.org (check "Add Python to PATH" during install)
- Git — download from https://git-scm.com (optional but recommended)

---

## Step 1: Get the project onto the mini PC

**Option A — git clone (easiest if you have internet on the mini PC temporarily):**

```
[MINI PC — internet needed briefly]
git clone https://github.com/mshears713/van-field-assitant.git
cd van-field-assitant
```

**Option B — copy from trusted machine:**

```
[TRUSTED MACHINE] Download or clone the repo as a ZIP
[COPY TO MINI PC] Copy the folder via USB drive or LAN file share
[MINI PC] Navigate to the copied folder
```

---

## Step 2: Install Python dependencies

```
[MINI PC]
cd van-field-assitant
pip install -r backend/requirements.txt
```

If pip is not found, try `python -m pip install -r backend/requirements.txt`.

---

## Step 3: Install Ollama

```
[MINI PC — internet needed briefly]
```

1. Open a browser on the mini PC.
2. Go to https://ollama.com
3. Download and install the Windows version.
4. No login or account required.

---

## Step 4: Pull the models

The assistant uses two models — one for general tasks, one for coding:

```
[MINI PC — internet needed briefly]
ollama pull qwen3:4b
ollama pull qwen2.5-coder:3b
```

- **qwen3:4b** — default model used by Operator, Librarian, Capture, and Display agents
- **qwen2.5-coder:3b** — used exclusively by the Coder agent

If storage is very tight, pull the smaller fallback instead:
```
ollama pull qwen2.5-coder:1.5b
```

**Option B — sneakernet / offline import (no internet on mini PC):**

```
[TRUSTED MACHINE]
1. Download GGUF files from Hugging Face or Ollama model hub
   (no login required for public models)
2. Copy the GGUF files to a USB drive

[COPY TO MINI PC]
3. Copy GGUF files from USB to mini PC, e.g.:
   C:\models\qwen3-4b.gguf
   C:\models\qwen2.5-coder-3b.gguf

[MINI PC]
4. Create a Modelfile for each (plain text):
   FROM C:\models\qwen3-4b.gguf

5. Import each:
   ollama create qwen3:4b -f Modelfile-qwen3
   ollama create qwen2.5-coder:3b -f Modelfile-coder
```

---

## Step 5: Start the backend

```
[MINI PC]
cd van-field-assitant
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
```

You should see output like:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

Keep this terminal open. The backend runs as long as this terminal is open.

**To start Ollama (if not already running as a service):**
```
[MINI PC — separate terminal]
ollama serve
```

---

## Step 6: Open the dashboard locally on the mini PC

```
[MINI PC]
Open a browser and go to: http://localhost:8080
```

You should see the Offline Field Assistant dashboard. Check the Home tab:
- Backend: Online (green)
- Ollama: Online (green) — if Ollama is running with a model pulled

---

## Step 7: Find the mini PC's local IP address

```
[MINI PC]
Open a terminal (PowerShell or Command Prompt) and run:
ipconfig | findstr IPv4
```

Look for an address like `192.168.x.x` or `10.0.x.x`. This is the IP address you will use from the Android phone.

---

## Step 8: Allow port 8080 through Windows Firewall

```
[MINI PC — run as Administrator]
netsh advfirewall firewall add rule name="FieldAssistant" dir=in action=allow protocol=TCP localport=8080
```

Or manually:
1. Open Windows Defender Firewall with Advanced Security
2. New Inbound Rule → Port → TCP → 8080 → Allow → All profiles → Name: FieldAssistant

---

## Step 9: Open from Android phone

```
[ANDROID]
1. Connect Android phone to the same Wi-Fi network as the mini PC
2. Open Chrome or any browser
3. Go to: http://<mini-pc-ip>:8080
   (replace <mini-pc-ip> with the IP from Step 7, e.g., http://192.168.1.42:8080)
```

---

## Step 10: First test

1. Tap the **Agents** tab
2. Select **Operator** from the agent selector
3. In the message box, type: `What should I check first on this system?`
4. Tap **Send**
5. Wait for the Ollama response (may take 10-30 seconds on first call)
6. Verify a response appears

If the response appears: setup is complete.

---

## Troubleshooting quick reference

| Problem | Quick fix |
|---------|-----------|
| Backend won't start | Check Python version, check requirements installed, check port not in use |
| Ollama shows Offline | Run `ollama serve` in a separate terminal |
| Model missing | Run `ollama pull qwen3:4b` and `ollama pull qwen2.5-coder:3b` |
| Android can't reach dashboard | Check same network, check Firewall (Step 8), check IP is correct |
| Port already in use | Run `netstat -aon \| findstr 8080` to find what's using it |
| Response is very slow | Try fallback: `set FIELD_APP_MODEL=qwen2.5-coder:1.5b` then restart backend |

See [RUNBOOK.md](RUNBOOK.md) for detailed procedures.  
See [DEBUGGING.md](DEBUGGING.md) for in-depth troubleshooting.

---

## Adding Notion library content

```
[TRUSTED MACHINE]
1. Open Notion, go to a page or database
2. Click ··· → Export → Markdown & CSV (or HTML)
3. Download the ZIP, extract it

[COPY TO MINI PC]
4. Copy the extracted folder contents into: van-field-assitant/library/notion_exports/
   (via USB drive, LAN share, or git commit to public repo)
```

5. Open the dashboard → **Library** tab — pages are indexed automatically on first load.
6. Go to **Agents → Librarian** and ask any question. Relevant pages are retrieved automatically — no manual paste needed.

No Notion API key, no Notion login, no credentials stored on the mini PC.
