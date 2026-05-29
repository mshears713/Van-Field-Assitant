"""Tests: GET /api/logs/recent and log_service functions."""
import json
import tempfile
from pathlib import Path


def test_logs_recent_returns_200(client):
    r = client.get("/api/logs/recent")
    assert r.status_code == 200


def test_logs_recent_has_required_shape(client):
    data = client.get("/api/logs/recent").json()
    assert "ok" in data
    assert data["ok"] is True
    assert "count" in data
    assert "logs" in data
    assert isinstance(data["logs"], list)


def test_logs_recent_count_matches_logs_length(client):
    data = client.get("/api/logs/recent").json()
    assert data["count"] == len(data["logs"])


def test_logs_recent_limit_param(client):
    r = client.get("/api/logs/recent?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert len(data["logs"]) <= 5


def test_logs_recent_limit_too_large_rejected(client):
    r = client.get("/api/logs/recent?limit=9999")
    assert r.status_code == 422  # FastAPI validation error


def test_log_service_writes_event():
    from backend.app.log_service import log_event, read_recent_logs
    with tempfile.TemporaryDirectory() as tmp:
        logs_dir = Path(tmp)
        log_event(logs_dir, "test", "ok", "Test event details")
        records = read_recent_logs(logs_dir, limit=10)
        assert len(records) == 1
        assert records[0]["event_type"] == "test"
        assert records[0]["status"] == "ok"
        assert records[0]["details"] == "Test event details"


def test_log_service_writes_agent_call():
    from backend.app.log_service import log_agent_call, read_recent_logs
    with tempfile.TemporaryDirectory() as tmp:
        logs_dir = Path(tmp)
        log_id = log_agent_call(
            logs_dir, "operator", "qwen2.5-coder:3b",
            "Test message for agent", None,
            True, 500
        )
        assert log_id
        assert len(log_id) == 8
        records = read_recent_logs(logs_dir, limit=10)
        assert len(records) == 1
        assert records[0]["agent_id"] == "operator"
        assert records[0]["ok"] is True


def test_log_service_handles_empty_directory():
    from backend.app.log_service import read_recent_logs
    with tempfile.TemporaryDirectory() as tmp:
        logs_dir = Path(tmp)
        records = read_recent_logs(logs_dir, limit=10)
        assert records == []


def test_log_service_handles_nonexistent_directory():
    from backend.app.log_service import read_recent_logs
    from pathlib import Path
    records = read_recent_logs(Path("/nonexistent/path/to/logs"), limit=10)
    assert records == []


def test_log_service_message_preview_truncated():
    from backend.app.log_service import log_agent_call, read_recent_logs
    with tempfile.TemporaryDirectory() as tmp:
        logs_dir = Path(tmp)
        long_message = "x" * 500
        log_agent_call(logs_dir, "coder", "model", long_message, None, True, 100)
        records = read_recent_logs(logs_dir)
        assert len(records[0]["message_preview"]) <= 200
