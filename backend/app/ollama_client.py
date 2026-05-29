import time
from dataclasses import dataclass, field
from typing import Optional

import httpx


@dataclass
class OllamaResponse:
    ok: bool
    content: Optional[str]
    model: str
    elapsed_ms: int
    error: Optional[str] = None
    error_type: Optional[str] = None


async def check_availability(base_url: str, timeout: float = 3.0) -> bool:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{base_url}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def list_models(base_url: str, timeout: float = 5.0) -> list:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{base_url}/api/tags")
            if r.status_code == 200:
                data = r.json()
                return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        pass
    return []


async def chat(
    base_url: str,
    model: str,
    messages: list,
    timeout: float = 120.0,
) -> OllamaResponse:
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
            }
            r = await client.post(f"{base_url}/api/chat", json=payload)
            elapsed_ms = int((time.monotonic() - start) * 1000)

            if r.status_code != 200:
                return OllamaResponse(
                    ok=False,
                    content=None,
                    model=model,
                    elapsed_ms=elapsed_ms,
                    error=f"Ollama returned HTTP {r.status_code}: {r.text[:200]}",
                    error_type="http_error",
                )

            data = r.json()
            content = data.get("message", {}).get("content", "")
            return OllamaResponse(ok=True, content=content, model=model, elapsed_ms=elapsed_ms)

    except httpx.ConnectError as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return OllamaResponse(
            ok=False,
            content=None,
            model=model,
            elapsed_ms=elapsed_ms,
            error=f"Cannot connect to Ollama at {base_url}. Is Ollama running?",
            error_type="connect_error",
        )
    except httpx.TimeoutException:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return OllamaResponse(
            ok=False,
            content=None,
            model=model,
            elapsed_ms=elapsed_ms,
            error=f"Ollama request timed out after {timeout:.0f}s.",
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
