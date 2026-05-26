# TESTING.md — Testing and Preflight Procedures

Complete testing guide for the Offline Field Assistant MVP.

---

## Automated test suite (pytest)

### Run all tests

```
[MINI PC or dev machine]
cd van-field-assitant
pytest tests/ -v
```

### What is tested

| Test file | What it covers |
|-----------|----------------|
| `tests/test_app_imports.py` | App imports, config loads, AGENT_METADATA has 5 keys |
| `tests/test_status_api.py` | /api/status shape, required keys, types |
| `tests/test_agents_api.py` | Agent list (5 agents), invalid ID (404), chat success (mocked), chat Ollama unavailable (mocked), empty message (400) |
| `tests/test_placeholder_apis.py` | All 5 placeholder endpoints return 200, ok=true, implemented=false |
| `tests/test_logs_api.py` | /api/logs/recent returns {ok, count, logs} shape |
| `tests/test_ollama_client.py` | Ollama unavailable → ok=False + error_type, timeout → timeout error_type, success → ok=True with content |

### Mocking strategy

Tests use `unittest.mock.AsyncMock` to patch Ollama calls. Tests do NOT require Ollama to be running.

Two fixtures in `conftest.py`:
- `mock_ollama_success` — patches `backend.app.ollama_client.chat` with a successful response
- `mock_ollama_unavailable` — patches `check_availability` to return False

---

## Preflight script

Checks the environment before deploying to the mini PC.

```
[MINI PC or dev machine]
python scripts/preflight.py
```

**Output format:**
```
[PASS] Python version: 3.11.x
[PASS] fastapi importable
[PASS] uvicorn importable
[PASS] httpx importable
[PASS] Directory exists: workspace/repos
...
[WARN] Ollama not reachable at http://localhost:11434 — start Ollama before using agents
[PASS] All 5 agent prompt files found
```

**Exit codes:**
- 0: All checks passed (PASS or WARN)
- 1: One or more FAIL checks

WARN is acceptable for Ollama unavailable (expected if Ollama is not running during pre-deploy check).

---

## Smoke test script (live backend required)

Tests that live endpoints respond correctly. Backend must be running.

```
[Start backend first]
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080

[Separate terminal]
python scripts/smoke_test.py

[With Ollama running, also test agent chat]
python scripts/smoke_test.py --with-ollama
```

---

## Manual acceptance checklist

Run through these before transferring to mini PC:

**On dev machine (before transfer):**
```
[ ] pytest tests/ -v passes with no failures
[ ] python scripts/preflight.py shows no FAIL results
[ ] python -c "from backend.app.main import app; print('OK')" succeeds
[ ] backend starts: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
[ ] http://localhost:8080 opens and shows dashboard
[ ] http://localhost:8080/api/status returns valid JSON
[ ] http://localhost:8080/api/agents returns 5 agents
[ ] http://localhost:8080/api/health returns {"ok": true}
[ ] Agents page loads with all 5 agents in selector
[ ] Agent call works if Ollama is running (or fails cleanly if not)
[ ] Logs tab shows entries after a failed or successful call
[ ] All placeholder pages (Projects, Library, Notes, Audio, Network, Settings) load without error
[ ] No API call fails with a 500 error
[ ] No external CDN requests in browser network tab
```

**On mini PC (after transfer):**
```
[ ] pip install -r backend/requirements.txt succeeds
[ ] python scripts/preflight.py shows no FAIL
[ ] backend starts on 0.0.0.0:8080
[ ] http://localhost:8080 opens on mini PC
[ ] Windows Firewall rule added for port 8080
[ ] ipconfig shows a local IP
[ ] Android phone connects to same network
[ ] http://<mini-pc-ip>:8080 opens on Android
[ ] Agent tab: Operator agent → "What should I check first?" → response received
[ ] logs/events.jsonl has entries after startup
[ ] logs/agent_calls.jsonl has entries after first agent call
```

---

## Android phone LAN test

1. Find mini PC IP: `ipconfig | findstr IPv4`
2. On Android: open Chrome or Firefox
3. Enter URL: `http://192.168.x.x:8080` (replace with actual IP)
4. Verify:
   - Dashboard loads (not a connection error)
   - Navigation tabs are visible and scrollable
   - Home tab shows system status
   - Agents tab loads agent selector
   - Send a test message: "Hello, what can you do?" with Operator agent
   - Response appears or clear error is shown
5. If it does not load: see DEBUGGING.md § "Android cannot reach the dashboard"

---

## Windows Firewall check

To verify the firewall rule was applied:
```
[MINI PC]
netsh advfirewall firewall show rule name="FieldAssistant"
```

Expected output includes `Action: Allow` and `LocalPort: 8080`.

If not shown, add it:
```
netsh advfirewall firewall add rule name="FieldAssistant" dir=in action=allow protocol=TCP localport=8080
```

---

## Deployment readiness checklist

Final check before handoff to mini PC:

```
Pre-transfer:
[ ] pytest passes
[ ] preflight passes (Ollama WARN is acceptable)
[ ] backend starts locally
[ ] dashboard opens locally
[ ] /api/status works
[ ] all agent prompt files present
[ ] logs are writable (check after startup)
[ ] placeholder pages return valid JSON
[ ] No secrets, tokens, or credentials anywhere in the codebase
[ ] No external CDN links in index.html

On mini PC:
[ ] Python 3.9+ installed
[ ] pip install -r backend/requirements.txt succeeds
[ ] Ollama installed (ollama --version works)
[ ] qwen2.5-coder:3b pulled (ollama list shows it)
[ ] Backend starts on 0.0.0.0:8080
[ ] Dashboard opens at http://localhost:8080
[ ] Windows Firewall allows TCP 8080 inbound
[ ] Android phone reaches http://<mini-pc-ip>:8080
[ ] First agent call succeeds (Operator: "Hello")
[ ] Log entry created in logs/agent_calls.jsonl
```
