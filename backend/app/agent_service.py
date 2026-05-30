from typing import Optional

from .config import config
from .library_service import build_librarian_context
from .log_service import log_agent_call
from .ollama_client import chat as ollama_chat
from .openai_client import chat as openai_chat

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

    openai_mode = bool(config.OPENAI_API_KEY)
    if openai_mode:
        effective_model = model or config.OPENAI_MODEL
    elif model:
        effective_model = model
    elif agent_id == "coder":
        effective_model = config.CODER_MODEL
    else:
        effective_model = config.DEFAULT_MODEL

    # Librarian: auto-retrieve index + matching pages from library
    if agent_id == "librarian":
        library_ctx = build_librarian_context(message)
        if library_ctx:
            if context and context.strip():
                context = library_ctx + "\n\n## User-provided context:\n" + context.strip()
            else:
                context = library_ctx

    user_content = message
    if context and context.strip():
        user_content = f"[Context provided by user]\n{context.strip()}\n\n[User message]\n{message}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    if openai_mode:
        result = await openai_chat(config.OPENAI_API_KEY, effective_model, messages, config.OLLAMA_CHAT_TIMEOUT)
    else:
        result = await ollama_chat(config.OLLAMA_BASE_URL, effective_model, messages, config.OLLAMA_CHAT_TIMEOUT)

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

    if openai_mode:
        recovery_hint = "Check your OPENAI_API_KEY in .env and ensure you have API access."
        if result.error_type == "http_error":
            recovery_hint = (
                "OpenAI returned an error. Check your API key, quota, and that the model name is correct "
                f"(currently: {effective_model})."
            )
        elif result.error_type == "timeout":
            recovery_hint = "OpenAI took too long. Try a shorter prompt or check your connection."
    else:
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
