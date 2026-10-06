from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_security_headers_and_closed_cors() -> None:
    client = TestClient(app)
    response = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"

    blocked = client.get("/health", headers={"Origin": "https://unknown.example"})
    assert "access-control-allow-origin" not in blocked.headers


def test_flutter_web_origin_is_allowed() -> None:
    response = TestClient(app).get("/health", headers={"Origin": "http://localhost:8080"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:8080"


def test_private_endpoint_requires_authentication() -> None:
    response = TestClient(app).get(f"/fincas/{uuid4()}/animales")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "NO_AUTENTICADO"
