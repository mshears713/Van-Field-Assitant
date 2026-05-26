from pathlib import Path
from typing import Optional

from .config import config
from .log_service import log_event
from .ollama_client import check_availability

_REQUIRED_DIRS = [
    config.WORKSPACE_DIR / "repos",
    config.LIBRARY_DIR / "notion_exports",
    config.NOTES_DIR / "inbox",
    config.NOTES_DIR / "processed",
    config.NOTES_DIR / "ready_for_notion",
    config.NOTES_DIR / "archived",
    config.LOGS_DIR,
    config.AGENTS_DIR,
]

_REQUIRED_AGENT_FILES = [
    config.AGENTS_DIR / "operator.agent.md",
    config.AGENTS_DIR / "coder.agent.md",
    config.AGENTS_DIR / "librarian.agent.md",
    config.AGENTS_DIR / "capture.agent.md",
    config.AGENTS_DIR / "display.agent.md",
]


def create_required_dirs() -> None:
    for d in _REQUIRED_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def check_agent_files() -> list[str]:
    return [str(f) for f in _REQUIRED_AGENT_FILES if not f.exists()]


async def run_startup_checks() -> dict:
    create_required_dirs()

    missing_agents = check_agent_files()

    ollama_ok = await check_availability(config.OLLAMA_BASE_URL, config.OLLAMA_CHECK_TIMEOUT)
    ollama_status = "available" if ollama_ok else "unavailable"

    if missing_agents:
        log_event(
            config.LOGS_DIR,
            "startup",
            "warn",
            f"Backend started. Ollama: {ollama_status}. Model: {config.DEFAULT_MODEL}. "
            f"Missing agent files: {missing_agents}",
        )
    else:
        log_event(
            config.LOGS_DIR,
            "startup",
            "ok",
            f"Backend started. Ollama: {ollama_status}. Model: {config.DEFAULT_MODEL}. "
            f"All agent files present.",
        )

    return {
        "ollama_available": ollama_ok,
        "missing_agent_files": missing_agents,
    }
