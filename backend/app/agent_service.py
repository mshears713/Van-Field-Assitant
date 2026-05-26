from typing import Optional

from .config import config
from .log_service import log_agent_call
from .ollama_client import chat

AGENT_METADATA: dict = {
    "operator": {
        "name": "Operator",
        "description": "Diagnose system state, explain startup errors, recommend 1-3 next actions.",
    },
    "coder": {
        "name": "Coder",
        "description": "Lightweight code help, error log interpretation, small reversible fixes.",
    },
    "librarian": {
        "name": "Librarian",
        "description": "Navigate local library and Notion exports. Cite local file paths.",
    },
    "capture": {
        "name": "Capture",
        "description": "Classify raw notes and transcripts into structured Notion-ready drafts.",
    },
    "display": {
        "name": "Display",
        "description": "Compress longer content into phone-friendly summaries and next actions.",
    },
}


def get_agents() -> list:
    return [
        {
            "agent_id": agent_id,
            "name": meta["name"],
            "description": meta["description"],
            "prompt_file": str(config.AGENTS_DIR / f"{agent_id}.agent.md"),
            "prompt_available": (config.AGENTS_DIR / f"{agent_id}.agent.md").exists(),
        }
        for agent_id, meta in AGENT_METADATA.items()
    ]


def load_system_prompt(agent_id: str) -> Optional[str]:
    prompt_path = config.AGENTS_DIR / f"{agent_id}.agent.md"
    if not prompt_path.exists():
        return None
    return prompt_path.read_text(encoding="utf-8").strip()


async def run_agent_chat(
    agent_id: str,
    message: str,
    context: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    if agent_id not in AGENT_METADATA:
        valid = ", ".join(AGENT_METADATA.keys())
        return {
            "ok": False,
            "agent_id": agent_id,
            "error": f"Unknown agent '{agent_id}'. Valid agents: {valid}.",
            "error_type": "invalid_agent",
        }

    system_prompt = load_system_prompt(agent_id)
    if not system_prompt:
        return {
            "ok": False,
            "agent_id": agent_id,
            "error": f"Prompt file for agent '{agent_id}' not found at {config.AGENTS_DIR / f'{agent_id}.agent.md'}.",
            "error_type": "missing_prompt",
        }

    effective_model = model or config.DEFAULT_MODEL

    user_content = message
    if context and context.strip():
        user_content = f"[Context provided by user]\n{context.strip()}\n\n[User message]\n{message}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    result = await chat(config.OLLAMA_BASE_URL, effective_model, messages, config.OLLAMA_CHAT_TIMEOUT)

    log_id = log_agent_call(
        config.LOGS_DIR,
        agent_id,
        effective_model,
        message,
        context,
        result.ok,
        result.elapsed_ms,
        result.error,
        result.error_type,
    )

    if result.ok:
        return {
            "ok": True,
            "agent_id": agent_id,
            "model": effective_model,
            "response": result.content,
            "log_id": log_id,
            "elapsed_ms": result.elapsed_ms,
        }

    recovery_hint = "Start Ollama and pull the configured model, then retry."
    if result.error_type == "timeout":
        recovery_hint = (
            "Ollama is running but took too long. "
            f"Try the fallback model ({config.FALLBACK_MODEL}) or a shorter prompt."
        )
    elif result.error_type == "http_error":
        recovery_hint = (
            "Ollama responded with an error. The model may not be pulled yet. "
            f"Run: ollama pull {effective_model}"
        )

    return {
        "ok": False,
        "agent_id": agent_id,
        "model": effective_model,
        "error": result.error,
        "error_type": result.error_type,
        "recovery_hint": recovery_hint,
        "log_id": log_id,
        "elapsed_ms": result.elapsed_ms,
    }
