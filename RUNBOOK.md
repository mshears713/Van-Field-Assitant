# RUNBOOK — Offline Field Assistant Operations

Quick operational reference for running and maintaining the Offline Field Assistant on the Windows mini PC.

---

## Start the backend

```
[MINI PC]
cd van-field-assitant
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
```

Leave the terminal open. The server runs until you close the terminal or press Ctrl+C.

**Start Ollama if not already running:**
```
[MINI PC — separate terminal]
ollama serve
```

---

## Stop the backend

Press `Ctrl+C` in the terminal running uvicorn.

To kill it if the terminal is unavailable:
```
[MINI PC]
taskkill /F /IM python.exe
```

---

## Check Ollama status

```
[MINI PC]
ollama list          List pulled models
ollama ps            Show running models
ollama --version     Check version
```

---

## Switch the default model

Set an environment variable before starting the backend:

```
[MINI PC — PowerShell]
$env:FIELD_APP_MODEL = "qwen2.5-coder:1.5b"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080

[MINI PC — Command Prompt]
set FIELD_APP_MODEL=qwen2.5-coder:1.5b
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
```

To make it permanent, set the variable in Windows System Properties → Environment Variables.

---

## Find the mini PC IP address

```
[MINI PC]
ipconfig | findstr IPv4
```

Or in PowerShell:
```
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"} | Select-Object IPAddress
```

Note the address (e.g., 192.168.1.42). Use this in the Android browser: `http://192.168.1.42:8080`

---

## Access from Android phone

1. Connect Android phone to the same Wi-Fi network as the mini PC.
2. Open Chrome or any browser.
3. Navigate to `http://<mini-pc-ip>:8080`

If it does not load, see the Firewall section in DEBUGGING.md.

---

## Inspect logs

Logs are written to the `logs/` folder in the project directory.

```
[MINI PC]
type logs\events.jsonl          Show backend events (Command Prompt)
type logs\agent_calls.jsonl     Show agent call history (Command Prompt)

PowerShell:
Get-Content logs\events.jsonl
Get-Content logs\agent_calls.jsonl
```

You can also view recent logs from the dashboard: click the **Logs** tab.

Or via API: `http://localhost:8080/api/logs/recent`

---

## Run preflight checks

Before transferring to mini PC or after any major change:
```
python scripts/preflight.py
```

This checks: Python version, packages, folders, agent files, logs writable, Ollama reachable.

---

## Run smoke tests (backend must be running)

```
python scripts/smoke_test.py
```

---

## Run full test suite

```
pytest tests/ -v
```

---

## Common recovery procedures

### Backend will not start
1. Check Python version: `python --version` (need 3.9+)
2. Check requirements installed: `pip install -r backend/requirements.txt`
3. Check port in use: `netstat -aon | findstr 8080`
4. Kill conflicting process: `taskkill /PID <pid> /F`
5. Try a different port: `--port 8081`

### Ollama unavailable on dashboard
1. Check Ollama is installed: `ollama --version`
2. Start it: `ollama serve` in a separate terminal
3. Verify: `ollama list`
4. Refresh the dashboard Home tab

### Model missing
1. Pull the model: `ollama pull qwen2.5-coder:3b`
2. Verify: `ollama list`
3. If no internet: copy GGUF from trusted machine via USB (see START_HERE.md, Step 4, Option B)

### Model too slow
1. Switch to fallback: `set FIELD_APP_MODEL=qwen2.5-coder:1.5b` then restart
2. Reduce prompt length: paste only the relevant lines, not entire files
3. Close other applications to free RAM

### Android cannot reach dashboard
1. Confirm both devices are on the same network
2. Verify IP address: `ipconfig | findstr IPv4`
3. Add Firewall rule (see START_HERE.md Step 8)
4. Try pinging from phone: Android Chrome cannot ping, but try the address directly
5. Try `http://` not `https://` — this app uses plain HTTP

### Log files not appearing
1. Check logs folder exists: should be auto-created on startup
2. Check write permissions: `echo test > logs\test.txt`
3. Restart the backend

### Agent response fails with recovery_hint
Follow the recovery_hint shown on screen. Common:
- Ollama unavailable → start Ollama
- Model missing → pull model or set FIELD_APP_MODEL to an available model
- Timeout → try fallback model or shorter prompt

---

## Collecting debug info for a stronger AI agent

If you need help debugging from a stronger AI (like Claude on your laptop), collect:

```
[MINI PC]
1. GET http://localhost:8080/api/status  (copy the JSON)
2. type logs\events.jsonl               (copy last 20 lines)
3. type logs\agent_calls.jsonl          (copy last 5 lines)
4. python --version
5. pip show fastapi uvicorn httpx
6. ollama list
```

Paste this into the chat with the stronger AI. It will have enough context to help.
