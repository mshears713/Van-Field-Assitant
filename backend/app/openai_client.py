"""OpenAI chat completions client — used only when OPENAI_API_KEY is set in .env."""
import time
from typing import Optional

import httpx

from .ollama_client import OllamaResponse

_API_URL = "https://api.openai.com/v1/chat/completions"


async def chat(
    api_key: str,
    model: str,
    messages: list,
    timeout: float = 60.0,
) -> OllamaResponse:
    start = time.monotonic()
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(_API_URL, headers=headers, json=payload)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        if r.status_code != 200:
            return OllamaResponse(
                ok=False,
                content=None,
                model=model,
                elapsed_ms=elapsed_ms,
                error=f"OpenAI returned HTTP {r.status_code}: {r.text[:300]}",
                error_type="http_error",
            )

        data = r.json()
        content = data["choices"][0]["message"]["content"]
        return OllamaResponse(ok=True, content=content, model=model, elapsed_ms=elapsed_ms)

    except httpx.ConnectError as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return OllamaResponse(
            ok=False,
            content=None,
            model=model,
            elapsed_ms=elapsed_ms,
            error=f"Cannot connect to OpenAI API: {exc}",
            error_type="connect_error",
        )
    except httpx.TimeoutException:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return OllamaResponse(
            ok=False,
            content=None,
            model=model,
            elapsed_ms=elapsed_ms,
            error=f"OpenAI request timed out after {timeout:.0f}s.",
            error_type="timeout",
        )
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return OllamaResponse(
            ok=False,
            content=None,
            model=model,
            elapsed_ms=elapsed_ms,
            error=str(exc),
            error_type="unknown",
        )
