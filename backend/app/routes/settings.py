from fastapi import APIRouter

from ..config import config

router = APIRouter()


@router.get("/settings")
def get_settings() -> dict:
    return {
        "ok": True,
        "implemented": False,
        "message": "Settings are read-only in this version. Edit environment variables to change configuration.",
        "config": {
            "app_name": config.APP_NAME,
            "app_version": config.APP_VERSION,
            "host": config.HOST,
            "port": config.PORT,
            "ollama_base_url": config.OLLAMA_BASE_URL,
            "default_model": config.DEFAULT_MODEL,
            "fallback_model": config.FALLBACK_MODEL,
            "ollama_check_timeout_s": config.OLLAMA_CHECK_TIMEOUT,
            "ollama_chat_timeout_s": config.OLLAMA_CHAT_TIMEOUT,
            "workspace_dir": str(config.WORKSPACE_DIR),
            "library_dir": str(config.LIBRARY_DIR),
            "notes_dir": str(config.NOTES_DIR),
            "logs_dir": str(config.LOGS_DIR),
            "agents_dir": str(config.AGENTS_DIR),
            "frontend_dir": str(config.FRONTEND_DIR),
        },
        "env_vars": {
            "FIELD_APP_MODEL": "Override the default Ollama model.",
            "FIELD_FALLBACK_MODEL": "Override the fallback Ollama model.",
            "FIELD_OLLAMA_URL": "Override the Ollama base URL (default: http://localhost:11434).",
            "FIELD_APP_PORT": "Override the backend port (default: 8080).",
            "FIELD_APP_HOST": "Override the bind host (default: 0.0.0.0).",
            "FIELD_WORKSPACE_PATH": "Override workspace directory path.",
            "FIELD_LIBRARY_PATH": "Override library directory path.",
            "FIELD_NOTES_PATH": "Override notes directory path.",
            "FIELD_LOGS_PATH": "Override logs directory path.",
            "FIELD_AGENTS_PATH": "Override agents directory path.",
        },
    }
