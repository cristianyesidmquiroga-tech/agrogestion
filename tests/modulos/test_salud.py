import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_app


@pytest.mark.asyncio
async def test_health_responde_ok() -> None:
    transporte = ASGITransport(app=create_app())
    async with AsyncClient(transport=transporte, base_url="http://test") as cliente:
        respuesta = await cliente.get("/health")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["status"] == "ok"
    assert "service" in cuerpo
    assert "version" in cuerpo
