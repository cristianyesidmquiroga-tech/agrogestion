from httpx import AsyncClient

from tests.conftest import Fabrica

URL = "/api/v1/cultivos"


async def test_riesgos_del_catalogo_y_del_cultivo(cliente: AsyncClient, f: Fabrica) -> None:
    admin, agricultor = await f.usuario("admin"), await f.usuario()
    nuevo = {"nombre": "Helada", "tipo": "clima", "aplica_a": "cultivo"}
    assert (
        await cliente.post("/api/v1/riesgos", json=nuevo, headers=f.cabecera(agricultor))
    ).status_code == 403
    creado = await cliente.post("/api/v1/riesgos", json=nuevo, headers=f.cabecera(admin))
    assert creado.status_code == 201
    assert (
        await cliente.post("/api/v1/riesgos", json=nuevo, headers=f.cabecera(admin))
    ).status_code == 409

    h = f.cabecera(agricultor)
    cultivo = await f.cultivo()
    riesgo_id = creado.json()["id"]
    cuerpo = [{"riesgo_id": riesgo_id, "fase_critica": "siembra", "susceptibilidad": "alta"}]
    r = await cliente.put(f"{URL}/{cultivo.id}/riesgos", json=cuerpo, headers=h)
    assert r.status_code == 200
    leido = await cliente.get(f"{URL}/{cultivo.id}/riesgos", headers=h)
    assert leido.json()[0]["susceptibilidad"] == "alta"
    repetido = await cliente.put(f"{URL}/{cultivo.id}/riesgos", json=cuerpo + cuerpo, headers=h)
    assert repetido.status_code == 409
    inexistente = [{"riesgo_id": "00000000-0000-0000-0000-000000000000", "susceptibilidad": "baja"}]
    assert (
        await cliente.put(f"{URL}/{cultivo.id}/riesgos", json=inexistente, headers=h)
    ).status_code == 404
