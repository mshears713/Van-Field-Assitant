#!/usr/bin/env python3
"""
Preflight check script for the Offline Field Assistant.

Run before deploying to the mini PC to verify the environment is ready.
Prints [PASS], [WARN], or [FAIL] for each check.

Usage: python scripts/preflight.py
Exit code: 0 if all PASS/WARN, 1 if any FAIL
"""

import sys
import os
import json
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

_fails = 0
_warns = 0


def check(label: str, passed: bool, warn_only: bool = False, detail: str = "") -> bool:
    global _fails, _warns
    status = "PASS"
    if not passed:
        if warn_only:
            status = "WARN"
            _warns += 1
        else:
            status = "FAIL"
            _fails += 1
    msg = f"[{status}] {label}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return passed


def main():
    print("=" * 60)
    print("Offline Field Assistant — Preflight Check")
    print("=" * 60)
    print()

    # ── Python version ───────────────────────────────────────────
    print("--- Python Environment ---")
    v = sys.version_info
    check(
        f"Python version: {v.major}.{v.minor}.{v.micro}",
        v >= (3, 9),
        detail="Need 3.9+" if v < (3, 9) else "",
    )

    # ── Package imports ──────────────────────────────────────────
    print()
    print("--- Required Packages ---")
    packages = ["fastapi", "uvicorn", "httpx", "pytest"]
    for pkg in packages:
        try:
            __import__(pkg)
            check(f"{pkg} importable", True)
        except ImportError:
            check(f"{pkg} importable", False, detail=f"Run: pip install -r backend/requirements.txt")

    # ── Directory existence ──────────────────────────────────────
    print()
    print("--- Required Directories ---")
    dirs_to_check = [
        PROJECT_ROOT / "agents",
        PROJECT_ROOT / "backend" / "app",
        PROJECT_ROOT / "frontend" / "static",
        PROJECT_ROOT / "workspace" / "repos",
        PROJECT_ROOT / "library" / "notion_exports",
        PROJECT_ROOT / "notes" / "inbox",
        PROJECT_ROOT / "notes" / "processed",
        PROJECT_ROOT / "logs",
    ]
    for d in dirs_to_check:
        if d.exists():
            check(f"Directory exists: {d.relative_to(PROJECT_ROOT)}", True)
        else:
            try:
                d.mkdir(parents=True, exist_ok=True)
                check(f"Directory created: {d.relative_to(PROJECT_ROOT)}", True, detail="auto-created")
            except Exception as e:
                check(f"Directory: {d.relative_to(PROJECT_ROOT)}", False, detail=str(e))

    # ── Agent prompt files ───────────────────────────────────────
    print()
    print("--- Agent Prompt Files ---")
    agent_ids = ["operator", "coder", "librarian", "capture", "display"]
    for agent_id in agent_ids:
        f = PROJECT_ROOT / "agents" / f"{agent_id}.agent.md"
        check(f"agents/{agent_id}.agent.md", f.exists())

    # ── Frontend files ───────────────────────────────────────────
    print()
    print("--- Frontend Files ---")
    frontend_files = [
        PROJECT_ROOT / "frontend" / "static" / "index.html",
        PROJECT_ROOT / "frontend" / "static" / "styles.css",
        PROJECT_ROOT / "frontend" / "static" / "app.js",
    ]
    for f in frontend_files:
        check(f"frontend/static/{f.name}", f.exists())

    # ── Backend app files ────────────────────────────────────────
    print()
    print("--- Backend Files ---")
    backend_files = [
        PROJECT_ROOT / "backend" / "app" / "main.py",
        PROJECT_ROOT / "backend" / "app" / "config.py",
        PROJECT_ROOT / "backend" / "app" / "ollama_client.py",
        PROJECT_ROOT / "backend" / "app" / "agent_service.py",
        PROJECT_ROOT / "backend" / "requirements.txt",
    ]
    for f in backend_files:
        check(f.relative_to(PROJECT_ROOT), f.exists())

    # ── Logs directory writable ──────────────────────────────────
    print()
    print("--- Writability ---")
    logs_dir = PROJECT_ROOT / "logs"
    test_file = logs_dir / ".preflight_test"
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test")
        test_file.unlink()
        check("logs/ directory writable", True)
    except Exception as e:
        check("logs/ directory writable", False, detail=str(e))

    # ── App import ───────────────────────────────────────────────
    print()
    print("--- App Import ---")
    try:
        from backend.app.main import app
        check("backend.app.main imports successfully", True)
    except Exception as e:
        check("backend.app.main imports successfully", False, detail=str(e))

    # ── Ollama availability ──────────────────────────────────────
    print()
    print("--- Ollama ---")
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            ollama_ok = resp.status == 200
    except Exception:
        ollama_ok = False

    check(
        "Ollama reachable at http://localhost:11434",
        ollama_ok,
        warn_only=True,
        detail="Not running — start Ollama before using agents" if not ollama_ok else "",
    )

    if ollama_ok:
        try:
            import urllib.request, json as _json
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as resp:
                data = _json.loads(resp.read())
                models = [m.get("name", "") for m in data.get("models", [])]
                print(f"         Available models: {models if models else '(none pulled yet)'}")
                default_model = os.getenv("FIELD_APP_MODEL", "qwen2.5-coder:3b")
                model_present = any(default_model in m for m in models)
                check(
                    f"Default model available: {default_model}",
                    model_present,
                    warn_only=True,
                    detail=f"Pull with: ollama pull {default_model}" if not model_present else "",
                )
        except Exception as e:
            check("Model check", False, warn_only=True, detail=str(e))

    # ── No obvious secrets in env ────────────────────────────────
    print()
    print("--- Security ---")
    secret_patterns = [
        "API_KEY", "SECRET_KEY", "GITHUB_TOKEN", "HF_TOKEN",
        "NOTION_TOKEN", "NOTION_API", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
    ]
    found_secrets = [p for p in secret_patterns if os.getenv(p)]
    if found_secrets:
        check(
            "No known secret env vars set",
            False,
            warn_only=True,
            detail=f"Found: {found_secrets} — ensure no credentials stored on mini PC",
        )
    else:
        check("No known secret env vars detected", True)

    # ── Summary ──────────────────────────────────────────────────
    print()
    print("=" * 60)
    if _fails == 0 and _warns == 0:
        print("All checks PASSED. Ready to deploy.")
    elif _fails == 0:
        print(f"All critical checks passed. {_warns} warning(s) — review above.")
    else:
        print(f"FAILED: {_fails} check(s) failed. Fix before deploying.")
    print("=" * 60)

    sys.exit(1 if _fails > 0 else 0)


if __name__ == "__main__":
    main()
