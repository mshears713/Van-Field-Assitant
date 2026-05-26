"""Tests: GET /api/agents and POST /api/agents/{id}/chat."""


def test_list_agents_returns_200(client):
    r = client.get("/api/agents")
    assert r.status_code == 200


def test_list_agents_has_agents_key(client):
    data = client.get("/api/agents").json()
    assert "agents" in data


def test_list_agents_returns_five(client):
    data = client.get("/api/agents").json()
    assert len(data["agents"]) == 5


def test_agent_has_required_fields(client):
    data = client.get("/api/agents").json()
    for agent in data["agents"]:
        for field in ("agent_id", "name", "description", "prompt_file", "prompt_available"):
            assert field in agent, f"Agent missing field: {field}"


def test_all_five_agent_ids_present(client):
    data = client.get("/api/agents").json()
    ids = {a["agent_id"] for a in data["agents"]}
    for required in ("operator", "coder", "librarian", "capture", "display"):
        assert required in ids, f"Agent ID '{required}' missing"


def test_invalid_agent_returns_404(client):
    r = client.post("/api/agents/nonexistent_agent/chat", json={"message": "Hello"})
    assert r.status_code == 404


def test_empty_message_returns_400(client):
    r = client.post("/api/agents/operator/chat", json={"message": ""})
    assert r.status_code == 400


def test_whitespace_message_returns_400(client):
    r = client.post("/api/agents/operator/chat", json={"message": "   "})
    assert r.status_code == 400


def test_chat_success_with_mocked_ollama(client, mock_ollama_success):
    r = client.post("/api/agents/operator/chat", json={"message": "What is the system status?"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["agent_id"] == "operator"
    assert "response" in data
    assert data["response"]
    assert "log_id" in data
    assert "elapsed_ms" in data


def test_chat_returns_model_name(client, mock_ollama_success):
    r = client.post("/api/agents/operator/chat", json={"message": "Hello"})
    data = r.json()
    assert "model" in data


def test_chat_with_context(client, mock_ollama_success):
    r = client.post("/api/agents/operator/chat", json={
        "message": "What do these logs mean?",
        "context": '{"timestamp": "2026-01-01", "event_type": "startup", "status": "ok"}'
    })
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True


def test_chat_ollama_unavailable_returns_ok_false(client, mock_ollama_unavailable):
    r = client.post("/api/agents/operator/chat", json={"message": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data
    assert "recovery_hint" in data
    assert data["error_type"] == "connect_error"


def test_chat_timeout_returns_timeout_error_type(client, mock_ollama_timeout):
    r = client.post("/api/agents/operator/chat", json={"message": "Hello"})
    data = r.json()
    assert data["ok"] is False
    assert data["error_type"] == "timeout"
    assert "recovery_hint" in data


def test_chat_all_agents_work(client, mock_ollama_success):
    for agent_id in ("operator", "coder", "librarian", "capture", "display"):
        r = client.post(f"/api/agents/{agent_id}/chat", json={"message": "Test message"})
        assert r.status_code == 200, f"Agent {agent_id} returned {r.status_code}"
        data = r.json()
        assert data["ok"] is True, f"Agent {agent_id} returned ok=False: {data.get('error')}"
