"""Tests: openai_client.chat with mocked HTTP."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_chat_success():
    from backend.app.openai_client import chat

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={
        "choices": [{"message": {"content": "Hello from OpenAI!"}}]
    })

    with patch("backend.app.openai_client.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        result = await chat("sk-test", "gpt-4o-mini", [{"role": "user", "content": "Hi"}])
        assert result.ok is True
        assert result.content == "Hello from OpenAI!"
        assert result.model == "gpt-4o-mini"
        assert result.elapsed_ms >= 0
        assert result.error is None


@pytest.mark.asyncio
async def test_chat_http_error():
    from backend.app.openai_client import chat

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Invalid API key"

    with patch("backend.app.openai_client.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        result = await chat("sk-bad", "gpt-4o-mini", [{"role": "user", "content": "Hi"}])
        assert result.ok is False
        assert result.error_type == "http_error"
        assert "401" in result.error
        assert result.content is None


@pytest.mark.asyncio
async def test_chat_connect_error():
    from backend.app.openai_client import chat
    import httpx

    with patch("backend.app.openai_client.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        mock_cls.return_value = mock_client

        result = await chat("sk-test", "gpt-4o-mini", [{"role": "user", "content": "Hi"}])
        assert result.ok is False
        assert result.error_type == "connect_error"
        assert result.content is None


@pytest.mark.asyncio
async def test_chat_timeout():
    from backend.app.openai_client import chat
    import httpx

    with patch("backend.app.openai_client.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        mock_cls.return_value = mock_client

        result = await chat("sk-test", "gpt-4o-mini", [{"role": "user", "content": "Hi"}])
        assert result.ok is False
        assert result.error_type == "timeout"
        assert result.content is None


@pytest.mark.asyncio
async def test_chat_never_raises():
    """chat() must return OllamaResponse, never raise."""
    from backend.app.openai_client import chat

    with patch("backend.app.openai_client.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(side_effect=Exception("unexpected"))
        mock_cls.return_value = mock_client

        result = await chat("sk-test", "gpt-4o-mini", [])
        assert result.ok is False
        assert result.error_type == "unknown"


@pytest.mark.asyncio
async def test_chat_sends_correct_headers():
    """Authorization header must include the api_key."""
    from backend.app.openai_client import chat

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json = MagicMock(return_value={
        "choices": [{"message": {"content": "ok"}}]
    })

    with patch("backend.app.openai_client.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_cls.return_value = mock_client

        await chat("sk-mykey", "gpt-4o-mini", [{"role": "user", "content": "Hi"}])

        call_kwargs = mock_client.post.call_args
        headers = call_kwargs.kwargs.get("headers", call_kwargs.args[1] if len(call_kwargs.args) > 1 else {})
        assert "Bearer sk-mykey" in headers.get("Authorization", "")
