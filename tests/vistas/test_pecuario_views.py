from fastapi.testclient import TestClient

from app.main import app


def test_pecuario_and_alerts_are_visible_in_docs() -> None:
    paths = TestClient(app).get("/openapi.json").json()["paths"]
    assert "/fincas/{finca_id}/animales" in paths
    assert "/fincas/{finca_id}/alertas" in paths
