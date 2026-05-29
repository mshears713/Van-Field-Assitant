#!/usr/bin/env python3
"""
Smoke test script for the Offline Field Assistant.

Tests that live API endpoints respond correctly.
Requires the backend to be running: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080

Usage:
  python scripts/smoke_test.py                # basic tests (no Ollama required)
  python scripts/smoke_test.py --with-ollama  # also test agent chat (requires Ollama + model)
  python scripts/smoke_test.py --base-url http://192.168.1.42:8080  # test remote host
"""

import sys
import json
import urllib.request
import urllib.error
import time
import argparse

_passes = 0
_fails = 0


def check(label: str, passed: bool, detail: str = "") -> bool:
    global _passes, _fails
    status = "PASS" if passed else "FAIL"
    if not passed:
        _fails += 1
    else:
        _passes += 1
    msg = f"[{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return passed


def get_json(url: str, timeout: float = 10.0):
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return None, None


def post_json(url: str, body: dict, timeout: float = 15.0):
    try:
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return None, None


def main():
    parser = argparse.ArgumentParser(description="Smoke test the Field Assistant backend.")
    parser.add_argument("--base-url", default="http://localhost:8080", help="Backend base URL")
    parser.add_argument("--with-ollama", action="store_true", help="Also test agent chat (requires Ollama)")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")

    print("=" * 60)
    print(f"Field Assistant Smoke Test — {base}")
    print("=" * 60)
    print()

    # ── Connectivity ─────────────────────────────────────────────
    print("--- Connectivity ---")
    status, data = get_json(f"{base}/api/health", timeout=5.0)
    if not check("GET /api/health returns 200", status == 200):
        print()
        print("FATAL: Cannot reach backend. Is it running?")
        print(f"Start with: python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080")
        sys.exit(1)
    check("/api/health returns ok=true", data and data.get("ok") is True)

    # ── Status ───────────────────────────────────────────────────
    print()
    print("--- Status API ---")
    status, data = get_json(f"{base}/api/status")
    check("GET /api/status returns 200", status == 200)
    if data:
        check("/api/status has app_name", "app_name" in data)
        check("/api/status has backend.ok=true", data.get("backend", {}).get("ok") is True)
        check("/api/status has ollama.available (bool)", isinstance(data.get("ollama", {}).get("available"), bool))
        check("/api/status has paths", "paths" in data)
        print(f"         Ollama available: {data.get('ollama', {}).get('available')}")
        print(f"         Model: {data.get('ollama', {}).get('default_model')}")

    # ── Agents ───────────────────────────────────────────────────
    print()
    print("--- Agents API ---")
    status, data = get_json(f"{base}/api/agents")
    check("GET /api/agents returns 200", status == 200)
    if data:
        agents = data.get("agents", [])
        check("GET /api/agents returns 5 agents", len(agents) == 5, detail=f"got {len(agents)}")
        ids = {a["agent_id"] for a in agents}
        for required in ("operator", "coder", "librarian", "capture", "display"):
            check(f"Agent '{required}' present", required in ids)

    # ── Invalid agent returns 404 ────────────────────────────────
    print()
    print("--- Error handling ---")
    status, _ = post_json(f"{base}/api/agents/nonexistent/chat", {"message": "test"})
    check("POST /api/agents/nonexistent/chat returns 404", status == 404, detail=f"got {status}")

    status, _ = post_json(f"{base}/api/agents/operator/chat", {"message": ""})
    check("POST with empty message returns 400", status == 400, detail=f"got {status}")

    # ── Logs ─────────────────────────────────────────────────────
    print()
    print("--- Logs API ---")
    status, data = get_json(f"{base}/api/logs/recent")
    check("GET /api/logs/recent returns 200", status == 200)
    if data:
        check("/api/logs/recent has logs list", isinstance(data.get("logs"), list))

    # ── Placeholder endpoints ────────────────────────────────────
    print()
    print("--- Placeholder Endpoints ---")
    placeholders = ["/api/projects", "/api/library", "/api/notes", "/api/network/status", "/api/settings"]
    for url in placeholders:
        status, data = get_json(f"{base}{url}")
        check(f"GET {url} returns 200", status == 200)

    # ── Dashboard HTML ───────────────────────────────────────────
    print()
    print("--- Dashboard ---")
    try:
        req = urllib.request.Request(f"{base}/")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            check("GET / returns HTML", "Field Assistant" in html)
    except Exception as e:
        check("GET / returns HTML", False, detail=str(e))

    # ── Agent chat (optional, requires Ollama) ───────────────────
    if args.with_ollama:
        print()
        print("--- Agent Chat (with Ollama) ---")
        print("  Sending test message to operator agent (may take 10-60s)...")
        t_start = time.time()
        status, data = post_json(
            f"{base}/api/agents/operator/chat",
            {"message": "Respond with exactly: SMOKE TEST OK"},
            timeout=90.0,
        )
        elapsed = time.time() - t_start
        check("POST /api/agents/operator/chat returns 200", status == 200)
        if data:
            check("Agent chat ok=true", data.get("ok") is True, detail=data.get("error", ""))
            if data.get("ok"):
                print(f"         Response in {elapsed:.1f}s: {str(data.get('response', ''))[:100]}")
                check("Response has log_id", "log_id" in data)

    # ── Summary ──────────────────────────────────────────────────
    print()
    print("=" * 60)
    total = _passes + _fails
    if _fails == 0:
        print(f"All {total} checks PASSED.")
    else:
        print(f"{_fails}/{total} checks FAILED. Review output above.")
    print("=" * 60)

    sys.exit(1 if _fails > 0 else 0)


if __name__ == "__main__":
    main()
