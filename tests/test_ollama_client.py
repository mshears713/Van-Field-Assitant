"""Tests: ollama_client functions with mocked HTTP."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_check_availability_returns_true_on_200():
    from backend.app.ollama_client import check_availability

    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("backend.app.ollama_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await check_availability("http://localhost:11434", timeout=3.0)
        assert result is True


@pytest.mark.asyncio
async def test_check_availability_returns_false_on_connection_error():
    from backend.app.ollama_client import check_availability
    import httpx

    with patch("backend.app.ollama_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("connection refused"))
        mock_client_class.return_value = mock_client

        result = await check_availability("http://localhost:11434", timeout=3.0)
        assert result is False


@pytest.mark.asyncio
async def test_chat_success():
    from backend.app.ollama_client import chat, OllamaResponse

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={
        "message": {"content": "Hello from Ollama!"}
    })

    with patch("backend.app.ollama_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await chat("http://localhost:11434", "qwen2.5-coder:3b", [{"role": "user", "content": "Hi"}])
        assert result.ok is True
        assert result.content == "Hello from Ollama!"
        assert result.model == "qwen2.5-coder:3b"
        assert result.elapsed_ms >= 0
        assert result.error is None


@pytest.mark.asyncio
async def test_chat_connect_error():
    from backend.app.ollama_client import chat
    import httpx

    with patch("backend.app.ollama_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_client_class.return_value = mock_client

        result = await chat("http://localhost:11434", "qwen2.5-coder:3b", [{"role": "user", "content": "Hi"}])
        assert result.ok is False
        assert result.error_type == "connect_error"
        assert result.content is None
        assert "Ollama" in result.error


@pytest.mark.asyncio
async def test_chat_timeout():
    from backend.app.ollama_client import chat
    import httpx

    with patch("backend.app.ollama_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_client_class.return_value = mock_client

        result = await chat("http://localhost:11434", "qwen2.5-coder:3b", [{"role": "user", "content": "Hi"}])
        assert result.ok is False
        assert result.error_type == "timeout"
        assert result.content is None


@pytest.mark.asyncio
async def test_chat_http_error():
    from backend.app.ollama_client import chat

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "model not found"

    with patch("backend.app.ollama_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value = mock_client

        result = await chat("http://localhost:11434", "qwen2.5-coder:3b", [{"role": "user", "content": "Hi"}])
        assert result.ok is False
        assert result.error_type == "http_error"
        assert "404" in result.error


@pytest.mark.asyncio
async def test_chat_never_raises():
    """chat() must return OllamaResponse, never raise, even for unexpected errors."""
    from backend.app.ollama_client import chat

    with patch("backend.app.ollama_client.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=Exception("unexpected error"))
        mock_client_class.return_value = mock_client

        result = await chat("http://localhost:11434", "qwen2.5-coder:3b", [])
        assert result.ok is False
        assert result.error_type == "unknown"
