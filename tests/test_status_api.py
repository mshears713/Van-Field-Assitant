"""Tests: GET /api/status and GET /api/health."""
from unittest.mock import AsyncMock


def test_health_check(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


def test_status_returns_200(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    r = client.get("/api/status")
    assert r.status_code == 200


def test_status_has_required_top_level_keys(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    data = client.get("/api/status").json()
    for key in ("app_name", "backend", "network", "ollama", "paths", "last_event"):
        assert key in data, f"Missing top-level key: {key}"


def test_status_backend_ok_is_true(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    data = client.get("/api/status").json()
    assert data["backend"]["ok"] is True


def test_status_backend_has_version(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    data = client.get("/api/status").json()
    assert "version" in data["backend"]
    assert data["backend"]["version"]


def test_status_ollama_available_is_bool(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    data = client.get("/api/status").json()
    assert isinstance(data["ollama"]["available"], bool)


def test_status_ollama_available_true_when_online(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=True))
    data = client.get("/api/status").json()
    assert data["ollama"]["available"] is True


def test_status_paths_has_required_keys(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    data = client.get("/api/status").json()
    for key in ("workspace", "library", "notes", "logs", "agents"):
        assert key in data["paths"], f"Missing path key: {key}"


def test_status_network_has_required_keys(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    data = client.get("/api/status").json()
    for key in ("mode", "host", "port"):
        assert key in data["network"], f"Missing network key: {key}"


def test_status_has_app_name(client, monkeypatch):
    monkeypatch.setattr("backend.app.routes.status.check_availability", AsyncMock(return_value=False))
    data = client.get("/api/status").json()
    assert data["app_name"] == "Offline Field Assistant"
