from datetime import datetime, timezone

from fastapi import APIRouter

from ..config import config
from ..log_service import read_recent_logs
from ..ollama_client import check_availability

router = APIRouter()


@router.get("/status")
async def get_status() -> dict:
    ollama_ok = await check_availability(config.OLLAMA_BASE_URL, config.OLLAMA_CHECK_TIMEOUT)

    recent = read_recent_logs(config.LOGS_DIR, limit=1)
    last_event = recent[0].get("details", "No events recorded yet.") if recent else "No events recorded yet."

    return {
        "app_name": config.APP_NAME,
        "backend": {
            "ok": True,
            "version": config.APP_VERSION,
            "local_time": datetime.now(timezone.utc).isoformat(),
        },
        "network": {
            "mode": "unknown",
            "host": config.HOST,
            "port": config.PORT,
            "dashboard_url_hint": f"http://<mini-pc-ip>:{config.PORT}",
            "internet_check": "not_checked",
        },
        "ollama": {
            "available": ollama_ok,
            "base_url": config.OLLAMA_BASE_URL,
            "default_model": config.DEFAULT_MODEL,
            "fallback_model": config.FALLBACK_MODEL,
            "message": (
                "Ollama is reachable." if ollama_ok
                else "Ollama is not reachable. Start Ollama, then refresh."
            ),
        },
        "paths": {
            "workspace": str(config.WORKSPACE_DIR),
            "library": str(config.LIBRARY_DIR),
            "notes": str(config.NOTES_DIR),
            "logs": str(config.LOGS_DIR),
            "agents": str(config.AGENTS_DIR),
        },
        "last_event": last_event,
    }


@router.get("/health")
async def health_check() -> dict:
    return {"ok": True}
