import os
from pathlib import Path
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Resolve repo root: backend/app/ -> backend/ -> repo root
_HERE = Path(__file__).parent
BASE_DIR: Path = _HERE.parent.parent

# Load .env if present — silently no-ops when the file doesn't exist
load_dotenv(BASE_DIR / ".env")


@dataclass
class Config:
    APP_NAME: str = "Offline Field Assistant"
    APP_VERSION: str = field(default_factory=lambda: os.getenv("FIELD_APP_VERSION", "0.1.0"))

    HOST: str = field(default_factory=lambda: os.getenv("FIELD_APP_HOST", "0.0.0.0"))
    PORT: int = field(default_factory=lambda: int(os.getenv("FIELD_APP_PORT", "8080")))

    OLLAMA_BASE_URL: str = field(default_factory=lambda: os.getenv("FIELD_OLLAMA_URL", "http://localhost:11434"))
    DEFAULT_MODEL: str = field(default_factory=lambda: os.getenv("FIELD_APP_MODEL", "qwen3:4b"))
    CODER_MODEL: str = field(default_factory=lambda: os.getenv("FIELD_CODER_MODEL", "qwen2.5-coder:3b"))
    FALLBACK_MODEL: str = field(default_factory=lambda: os.getenv("FIELD_FALLBACK_MODEL", "qwen2.5-coder:1.5b"))

    OLLAMA_CHECK_TIMEOUT: float = field(default_factory=lambda: float(os.getenv("FIELD_OLLAMA_CHECK_TIMEOUT", "3.0")))
    OLLAMA_CHAT_TIMEOUT: float = field(default_factory=lambda: float(os.getenv("FIELD_OLLAMA_CHAT_TIMEOUT", "120.0")))

    # OpenAI testing mode — populated from .env, absent in production
    OPENAI_API_KEY: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    OPENAI_MODEL: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

    WORKSPACE_DIR: Path = field(default_factory=lambda: BASE_DIR / os.getenv("FIELD_WORKSPACE_PATH", "workspace"))
    LIBRARY_DIR: Path = field(default_factory=lambda: BASE_DIR / os.getenv("FIELD_LIBRARY_PATH", "library"))
    NOTES_DIR: Path = field(default_factory=lambda: BASE_DIR / os.getenv("FIELD_NOTES_PATH", "notes"))
    LOGS_DIR: Path = field(default_factory=lambda: BASE_DIR / os.getenv("FIELD_LOGS_PATH", "logs"))
    AGENTS_DIR: Path = field(default_factory=lambda: BASE_DIR / os.getenv("FIELD_AGENTS_PATH", "agents"))

    FRONTEND_DIR: Path = field(default_factory=lambda: BASE_DIR / "frontend" / "static")


config = Config()
