"""End-to-end tests for the FastAPI app."""
import os
os.environ["LOCAL_MODE"] = "true"

from fastapi.testclient import TestClient
from src.api.main import app


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_submit_returns_review():
    payload = {
        "code": "def f(x):\n    y = 1\n    return x + y",
        "language": "python",
    }
    r = client.post("/submit", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "session_id" in body
    assert "quality_score" in body
    assert 1 <= body["quality_score"] <= 10
    assert "review" in body
    assert "issues" in body["review"]


def test_submit_flags_missing_docstring():
    payload = {
        "code": "def f(x):\n    return x",
        "language": "python",
    }
    r = client.post("/submit", json=payload)
    assert r.status_code == 200
    facts = r.json()["ast_facts"]
    assert any("no docstring" in f for f in facts)


def test_history_after_submit():
    # submit first
    client.post("/submit", json={"code": "x = 1", "language": "python"})
    r = client.get("/history")
    assert r.status_code == 200
    body = r.json()
    assert "sessions" in body
    assert isinstance(body["sessions"], list)
    assert len(body["sessions"]) >= 1
