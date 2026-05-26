"""Tests: all placeholder endpoints return valid, honest scaffold responses."""


def _check_placeholder(client, url):
    r = client.get(url)
    assert r.status_code == 200, f"{url} returned {r.status_code}"
    data = r.json()
    assert "ok" in data, f"{url} missing 'ok' key"
    assert data["ok"] is True, f"{url} ok is not True"
    assert "implemented" in data, f"{url} missing 'implemented' key"
    assert data["implemented"] is False, f"{url} implemented should be False"
    assert "message" in data, f"{url} missing 'message'"
    assert data["message"], f"{url} message is empty"
    return data


def test_projects_endpoint(client):
    data = _check_placeholder(client, "/api/projects")
    assert "workspace_dir" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_library_endpoint(client):
    data = _check_placeholder(client, "/api/library")
    assert "library_dir" in data
    assert "items" in data


def test_notes_endpoint(client):
    data = _check_placeholder(client, "/api/notes")
    assert "notes_dir" in data
    assert "items" in data


def test_network_status_endpoint(client):
    data = _check_placeholder(client, "/api/network/status")
    assert "host" in data
    assert "port" in data
    assert "manual_checklist" in data
    assert isinstance(data["manual_checklist"], list)
    assert len(data["manual_checklist"]) > 0


def test_settings_endpoint(client):
    r = client.get("/api/settings")
    assert r.status_code == 200
    data = r.json()
    assert "ok" in data
    assert data["ok"] is True
    assert "config" in data
    cfg = data["config"]
    for key in ("default_model", "ollama_base_url", "app_version"):
        assert key in cfg, f"Settings missing key: {key}"


def test_all_placeholder_return_json(client):
    urls = ["/api/projects", "/api/library", "/api/notes", "/api/network/status", "/api/settings"]
    for url in urls:
        r = client.get(url)
        assert r.headers["content-type"].startswith("application/json"), f"{url} not JSON"
