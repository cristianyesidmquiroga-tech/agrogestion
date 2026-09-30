from httpx import AsyncClient

from tests.conftest import Fabrica, payload_siembra

RUTA = "/api/v1/cultivos"


async def test_usuario_no_ve_la_siembra_de_otra_finca(cliente: AsyncClient, f: Fabrica) -> None:
    dueno, intruso = await f.usuario(), await f.usuario()
    finca = await f.finca(dueno)
    lote = await f.lote(finca)
    cultivo = await f.cultivo()
    r = await cliente.post(
        "/api/v1/siembras",
        json=payload_siembra(finca.id, lote.id, cultivo.id),
        headers=f.cabecera(dueno),
    )
    assert r.status_code == 201
    siembra_id = r.json()["id"]

    ajeno = await cliente.get(f"/api/v1/siembras/{siembra_id}", headers=f.cabecera(intruso))
    assert ajeno.status_code == 404
    lista = await cliente.get("/api/v1/siembras", headers=f.cabecera(intruso))
    assert lista.json()["total"] == 0
    crear = await cliente.post(
        "/api/v1/siembras",
        json=payload_siembra(finca.id, lote.id, cultivo.id),
        headers=f.cabecera(intruso),
    )
    assert crear.status_code == 404
