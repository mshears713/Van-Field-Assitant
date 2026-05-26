# DEBUGGING.md — Troubleshooting Guide

Agent-readable and human-readable troubleshooting guide for the Offline Field Assistant.

For each problem: **Symptoms → Diagnosis → Fix → Evidence to collect if still stuck**

---

## Backend will not start

**Symptoms:** Running `python -m uvicorn backend.app.main:app ...` prints an error and exits immediately.

**Common causes:**

1. **Python not found or wrong version**
   - Check: `python --version` (need 3.9+)
   - Fix: Install Python 3.9+ from python.org, ensure "Add to PATH" was checked

2. **Missing packages**
   - Check: `pip show fastapi uvicorn httpx`
   - Fix: `pip install -r backend/requirements.txt`

3. **Port already in use**
   - Symptom: `[Errno 10048]` or `address already in use`
   - Check: `netstat -aon | findstr 8080`
   - Fix: Kill the conflicting PID: `taskkill /PID <pid> /F`
   - Alternative: use a different port: `--port 8081`

4. **Import error in the app**
   - Symptom: Traceback ending in an import error
   - Check: `python -c "from backend.app.main import app; print('OK')"`
   - Fix: Read the traceback. It will name the file and line with the problem.

5. **Working directory wrong**
   - Symptom: `ModuleNotFoundError: No module named 'backend'`
   - Fix: Ensure you are running the command from the repo root (`van-field-assitant/`)

**Evidence to collect:**
```
python --version
pip list | findstr "fastapi uvicorn httpx"
python -c "from backend.app.main import app; print('OK')"
```

---

## Dashboard will not load locally

**Symptoms:** Backend is running but `http://localhost:8080` shows a browser error.

**Diagnosis:**
1. Is the backend actually running? Check the terminal for `Uvicorn running on http://0.0.0.0:8080`
2. Is the port correct? Try `http://localhost:8080/api/health` — should return `{"ok": true}`
3. Is the frontend directory found? Check for `frontend/static/index.html`

**Fix:**
- If `/api/health` works but `/` shows an error: the frontend files are missing or in the wrong location
- Verify: `dir frontend\static\` — should contain `index.html`, `styles.css`, `app.js`

---

## Android cannot reach the dashboard

**Symptoms:** Mini PC dashboard works locally but Android phone gets "site can't be reached."

**Diagnosis steps:**

1. **Wrong IP address** — most common
   - Run `ipconfig | findstr IPv4` on the mini PC
   - Use that exact IP in Android browser: `http://192.168.x.x:8080`
   - Do NOT use `localhost` from Android — that refers to the phone itself

2. **Different networks**
   - Mini PC must be on the same Wi-Fi as the Android phone
   - Both must be on the same subnet (e.g., both on 192.168.1.x)

3. **Windows Firewall blocking port 8080** — very common
   - Fix: Run as Administrator on mini PC:
     ```
     netsh advfirewall firewall add rule name="FieldAssistant" dir=in action=allow protocol=TCP localport=8080
     ```
   - Or: Control Panel → Windows Defender Firewall → Advanced Settings → New Inbound Rule → Port 8080 → Allow

4. **Backend bound to wrong address**
   - Verify backend started with `--host 0.0.0.0` not `--host 127.0.0.1`
   - `127.0.0.1` only accepts local connections

5. **VPN or network isolation**
   - If the mini PC is connected to a VPN, it may be unreachable from the local network
   - Disable VPN while using local field mode

**Evidence to collect:**
```
[MINI PC] ipconfig | findstr IPv4
[MINI PC] netstat -aon | findstr 8080
[MINI PC] netsh advfirewall firewall show rule name=all | findstr FieldAssistant
```

---

## Ollama unavailable

**Symptoms:** Dashboard Home shows Ollama: Offline. Agent calls fail with "Cannot connect to Ollama."

**Diagnosis:**
1. Is Ollama installed? `ollama --version`
2. Is Ollama running? `ollama ps` or check the system tray for Ollama icon
3. Is it running on the default port? `netstat -aon | findstr 11434`

**Fix:**
- Start Ollama: `ollama serve` in a separate terminal
- Or start from the Ollama system tray icon
- If you changed `FIELD_OLLAMA_URL`, verify it matches where Ollama is listening

---

## Model not pulled / model error

**Symptoms:** Ollama is running but agent calls return an error like "model not found" or HTTP 404.

**Diagnosis:**
1. List available models: `ollama list`
2. Check what model the backend expects: `http://localhost:8080/api/settings` → default_model

**Fix:**
- Pull the default model: `ollama pull qwen2.5-coder:3b`
- Or switch to a model you already have: `set FIELD_APP_MODEL=<model-name>` then restart backend
- For offline import from GGUF: see START_HERE.md Step 4, Option B

---

## Model too slow / timeout

**Symptoms:** Agent calls time out after 120 seconds, or responses take 2-3+ minutes.

**Causes:** CPU-only inference on a small model can be slow under load.

**Fix:**
1. Switch to the smaller fallback model: `set FIELD_APP_MODEL=qwen2.5-coder:1.5b`
2. Close other applications to free RAM
3. Reduce prompt length: paste only the most relevant lines, not entire files
4. Increase timeout if needed: `set FIELD_OLLAMA_CHAT_TIMEOUT=240`

---

## Invalid agent ID

**Symptoms:** POST to `/api/agents/something/chat` returns 404 with "Unknown agent."

**Valid agent IDs:** `operator`, `coder`, `librarian`, `capture`, `display`

**Fix:** Use a valid ID. The dashboard agent selector only shows valid agents.

---

## Agent prompt file missing

**Symptoms:** Agent call returns error_type: `missing_prompt`. Dashboard shows `prompt_available: false` for an agent.

**Fix:**
1. Check agents/ folder: `dir agents\`
2. Should contain: `operator.agent.md`, `coder.agent.md`, `librarian.agent.md`, `capture.agent.md`, `display.agent.md`
3. If missing: the file was not included in the project. Re-clone or restore from git.

---

## Logs missing or empty

**Symptoms:** Logs tab shows no entries. `logs/events.jsonl` does not exist.

**Diagnosis:**
1. Check if logs/ directory exists and is writable: `echo test > logs\test.txt`
2. Has the backend started at least once? Startup creates the first event.
3. Check if backend started with the correct working directory.

**Fix:**
- Restart the backend from the repo root
- If the directory is not writable, check file permissions

---

## Wrong path shown in API responses

**Symptoms:** `/api/status` shows paths that don't exist on the mini PC.

**Cause:** The app resolves paths relative to the location of `backend/app/config.py` at runtime.

**Fix:**
- Ensure you run the backend from the repo root
- Or set path environment variables explicitly:
  ```
  set FIELD_WORKSPACE_PATH=C:\Users\you\van-field-assitant\workspace
  ```

---

## Port already in use (port 8080)

**Symptoms:** Startup fails with `[Errno 10048]` or `address already in use`.

**Diagnosis:**
```
netstat -aon | findstr 8080
```
Note the PID in the last column.

**Fix:**
- Kill the process: `taskkill /PID <pid> /F`
- Or use a different port: `--port 8081` and update bookmarks accordingly

---

## CORS or static file issues

**Symptoms:** Dashboard loads but API calls fail in browser with CORS error.

**Note:** Since the dashboard is served from the same FastAPI server, CORS should not be an issue for same-origin requests.

**If it occurs:**
- Verify the browser is not caching an old version: hard refresh (Ctrl+Shift+R)
- Verify you are not accessing from a different origin (e.g., file:// instead of http://)
- The backend does not need CORS headers for local use

---

## Collecting a complete debug package

If you are stuck and need help from a stronger AI assistant, collect this information:

```
[MINI PC — run these, copy all output]
1. python --version
2. pip show fastapi uvicorn httpx
3. ollama list
4. GET http://localhost:8080/api/status
5. GET http://localhost:8080/api/agents
6. type logs\events.jsonl  (last 20 lines)
7. type logs\agent_calls.jsonl  (last 5 lines)
8. python -c "from backend.app.config import config; print(config)"
```

Paste this into Claude or another strong coding assistant. Include the error message you are seeing.
Do not include any passwords, tokens, or credentials in what you paste.
