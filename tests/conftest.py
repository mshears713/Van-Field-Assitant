import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ollama_client import OllamaResponse


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_ollama_success(monkeypatch):
    success = OllamaResponse(
        ok=True,
        content="This is a mocked Ollama response.",
        model="qwen2.5-coder:3b",
        elapsed_ms=500,
    )
    mock = AsyncMock(return_value=success)
    monkeypatch.setattr("backend.app.agent_service.ollama_chat", mock)
    monkeypatch.setattr("backend.app.agent_service.openai_chat", mock)
    return mock


@pytest.fixture
def mock_ollama_unavailable(monkeypatch):
    unavailable = OllamaResponse(
        ok=False,
        content=None,
        model="qwen2.5-coder:3b",
        elapsed_ms=5,
        error="Cannot connect to Ollama at http://localhost:11434. Is Ollama running?",
        error_type="connect_error",
    )
    check_mock = AsyncMock(return_value=False)
    chat_mock = AsyncMock(return_value=unavailable)
    monkeypatch.setattr("backend.app.ollama_client.check_availability", check_mock)
    monkeypatch.setattr("backend.app.agent_service.ollama_chat", chat_mock)
    monkeypatch.setattr("backend.app.agent_service.openai_chat", chat_mock)
    return chat_mock


@pytest.fixture
def mock_ollama_timeout(monkeypatch):
    timeout_resp = OllamaResponse(
        ok=False,
        content=None,
        model="qwen2.5-coder:3b",
        elapsed_ms=120000,
        error="Ollama request timed out after 120s.",
        error_type="timeout",
    )
    mock = AsyncMock(return_value=timeout_resp)
    monkeypatch.setattr("backend.app.agent_service.ollama_chat", mock)
    monkeypatch.setattr("backend.app.agent_service.openai_chat", mock)
    return mock
