"""Tests: app imports, config, agent metadata, startup folder creation."""
import importlib


def test_main_imports():
    mod = importlib.import_module("backend.app.main")
    assert hasattr(mod, "app"), "main.py must expose 'app'"


def test_config_loads():
    from backend.app.config import config
    assert config.APP_NAME == "Offline Field Assistant"
    assert config.PORT == 8080
    assert config.DEFAULT_MODEL == "qwen3:4b"
    assert config.CODER_MODEL == "qwen2.5-coder:3b"
    assert config.FALLBACK_MODEL == "qwen2.5-coder:1.5b"
    assert "localhost:11434" in config.OLLAMA_BASE_URL


def test_agent_metadata_has_five_agents():
    from backend.app.agent_service import AGENT_METADATA
    assert len(AGENT_METADATA) == 5
    for required in ("operator", "coder", "librarian", "capture", "display"):
        assert required in AGENT_METADATA, f"Agent '{required}' missing from AGENT_METADATA"


def test_agent_metadata_has_required_keys():
    from backend.app.agent_service import AGENT_METADATA
    for agent_id, meta in AGENT_METADATA.items():
        assert "name" in meta, f"Agent {agent_id} missing 'name'"
        assert "description" in meta, f"Agent {agent_id} missing 'description'"


def test_agent_prompt_files_exist():
    from backend.app.config import config
    for agent_id in ("operator", "coder", "librarian", "capture", "display"):
        prompt_file = config.AGENTS_DIR / f"{agent_id}.agent.md"
        assert prompt_file.exists(), f"Missing agent prompt file: {prompt_file}"


def test_startup_creates_dirs():
    import asyncio
    from backend.app.startup_checks import create_required_dirs
    from backend.app.config import config

    create_required_dirs()

    assert config.LOGS_DIR.exists()
    assert config.WORKSPACE_DIR.exists()
    assert config.LIBRARY_DIR.exists()
    assert config.NOTES_DIR.exists()
    assert (config.NOTES_DIR / "inbox").exists()


def test_load_system_prompt():
    from backend.app.agent_service import load_system_prompt
    prompt = load_system_prompt("operator")
    assert prompt is not None
    assert len(prompt) > 50, "Operator prompt should have meaningful content"


def test_load_system_prompt_invalid():
    from backend.app.agent_service import load_system_prompt
    result = load_system_prompt("nonexistent_agent")
    assert result is None
