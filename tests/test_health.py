from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_invalid_token_has_consistent_error() -> None:
    response = TestClient(app).get("/auth/me", headers={"Authorization": "Bearer altered"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "TOKEN_INVALIDO"
