from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_log_rule_based():
    response = client.post(
        "/analyze-log",
        json={
            "log_text": """
Run npm test
npm ERR! Cannot find module 'vite'
Error: Process completed with exit code 1.
"""
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "rule-based"
    assert body["confidence"] in ["low", "medium", "high"]
    assert body["error_lines"]
