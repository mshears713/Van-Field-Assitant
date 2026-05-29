import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _write_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(
    logs_dir: Path,
    event_type: str,
    status: str,
    details: str,
    error: Optional[str] = None,
) -> None:
    record: dict = {
        "timestamp": _now_iso(),
        "event_type": event_type,
        "status": status,
        "details": details,
    }
    if error:
        record["error"] = error
    _write_jsonl(logs_dir / "events.jsonl", record)


def log_agent_call(
    logs_dir: Path,
    agent_id: str,
    model: str,
    message: str,
    context: Optional[str],
    ok: bool,
    elapsed_ms: int,
    error: Optional[str] = None,
    error_type: Optional[str] = None,
) -> str:
    log_id = str(uuid.uuid4())[:8]
    record: dict = {
        "id": log_id,
        "timestamp": _now_iso(),
        "agent_id": agent_id,
        "model": model,
        "message_preview": message[:200],
        "context_preview": context[:200] if context else None,
        "ok": ok,
        "elapsed_ms": elapsed_ms,
        "error": error,
        "error_type": error_type,
    }
    _write_jsonl(logs_dir / "agent_calls.jsonl", record)
    return log_id


def read_recent_logs(logs_dir: Path, limit: int = 50) -> list:
    records: list = []
    for log_file in ("events.jsonl", "agent_calls.jsonl"):
        path = logs_dir / log_file
        if not path.exists():
            continue
        try:
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            records.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except OSError:
            pass
    records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return records[:limit]
