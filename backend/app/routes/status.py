from datetime import datetime, timezone

from fastapi import APIRouter

from ..config import config
from ..log_service import read_recent_logs
from ..ollama_client import check_availability
from .network import _get_lan_ip

router = APIRouter()


@router.get("/status")
async def get_status() -> dict:
    openai_mode = bool(config.OPENAI_API_KEY)

    if openai_mode:
        ollama_ok = False
        ollama_message = "Ollama check skipped — OpenAI testing mode is active."
    else:
        ollama_ok = await check_availability(config.OLLAMA_BASE_URL, config.OLLAMA_CHECK_TIMEOUT)
        ollama_message = (
            "Ollama is reachable." if ollama_ok
            else "Ollama is not reachable. Start Ollama, then refresh."
        )

    lan_ip = _get_lan_ip()
    recent = read_recent_logs(config.LOGS_DIR, limit=1)
    last_event = recent[0].get("details", "No events recorded yet.") if recent else "No events recorded yet."

    return {
        "app_name": config.APP_NAME,
        "backend": {
            "ok": True,
            "version": config.APP_VERSION,
            "local_time": datetime.now(timezone.utc).isoformat(),
        },
        "llm_backend": {
            "mode": "openai" if openai_mode else "ollama",
            "model": config.OPENAI_MODEL if openai_mode else config.DEFAULT_MODEL,
            "note": (
                f"OpenAI testing mode active. Model: {config.OPENAI_MODEL}. Remove .env to revert to Ollama."
                if openai_mode
                else "Ollama mode (production default)."
            ),
        },
        "network": {
            "mode": "unknown",
            "host": config.HOST,
            "port": config.PORT,
            "lan_ip": lan_ip,
            "dashboard_url_hint": f"http://{lan_ip}:{config.PORT}",
            "internet_check": "not_checked",
        },
        "ollama": {
            "available": ollama_ok,
            "base_url": config.OLLAMA_BASE_URL,
            "default_model": config.DEFAULT_MODEL,
            "fallback_model": config.FALLBACK_MODEL,
            "message": ollama_message,
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
