from httpx import AsyncClient

from tests.conftest import Fabrica


async def test_politica_es_publica_y_marca_su_estado(cliente: AsyncClient) -> None:
    r = await cliente.get("/api/v1/politica")
    assert r.status_code == 200
    assert r.json()["estado"] == "borrador"
    assert r.json()["datos_que_usamos"]


async def test_consentimiento(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    version = (await cliente.get("/api/v1/politica")).json()["version"]
    pendiente = await cliente.get("/api/v1/cuenta/consentimiento", headers=h)
    assert pendiente.status_code == 404
    assert pendiente.json()["error"] == "CONSENTIMIENTO_PENDIENTE"

    sin_aceptar = await cliente.post(
        "/api/v1/cuenta/consentimiento",
        json={"version_politica": version, "acepta_tratamiento": False},
        headers=h,
    )
    assert sin_aceptar.status_code == 422
    vieja = await cliente.post(
        "/api/v1/cuenta/consentimiento",
        json={"version_politica": "2000-01", "acepta_tratamiento": True},
        headers=h,
    )
    assert vieja.status_code == 409

    ok = await cliente.post(
        "/api/v1/cuenta/consentimiento",
        json={
            "version_politica": version,
            "acepta_tratamiento": True,
            "acepta_transferencia_ia": True,
        },
        headers=h,
    )
    assert ok.status_code == 201
    ultimo = await cliente.get("/api/v1/cuenta/consentimiento", headers=h)
    assert ultimo.json()["acepta_transferencia_ia"] is True
    assert ultimo.json()["version_politica"] == version
