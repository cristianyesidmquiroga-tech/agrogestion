from datetime import date

from httpx import AsyncClient

from tests.conftest import Fabrica, payload_siembra

URL = "/api/v1/propagacion"


def nuevo(finca_id: object, cultivo_id: object, **extra: object) -> dict[str, object]:
    base: dict[str, object] = {
        "finca_id": str(finca_id),
        "cultivo_id": str(cultivo_id),
        "metodo": "semilla",
        "fecha_inicio": date.today().isoformat(),
        "puestas": 100,
    }
    base.update(extra)
    return base


async def test_crear_y_actualizar_un_lote_de_vivero(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    cultivo = await f.cultivo()
    h = f.cabecera(u)
    r = await cliente.post(URL, json=nuevo(finca.id, cultivo.id), headers=h)
    assert r.status_code == 201
    lote = r.json()["id"]
    ok = await cliente.patch(
        f"{URL}/{lote}", json={"germinadas": 70, "listas": 60, "perdidas": 10}, headers=h
    )
    assert ok.status_code == 200
    assert ok.json()["listas"] == 60


async def test_reglas_de_germinacion(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    cultivo = await f.cultivo()
    h = f.cabecera(u)
    lote = (await cliente.post(URL, json=nuevo(finca.id, cultivo.id), headers=h)).json()["id"]
    demasiadas = await cliente.patch(f"{URL}/{lote}", json={"germinadas": 101}, headers=h)
    assert demasiadas.status_code == 422
    listas = await cliente.patch(f"{URL}/{lote}", json={"germinadas": 50, "listas": 51}, headers=h)
    assert listas.status_code == 422


async def test_metodo_fuera_del_perfil(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    cultivo = await f.cultivo(metodos=("semilla",))
    r = await cliente.post(
        URL, json=nuevo(finca.id, cultivo.id, metodo="injerto"), headers=f.cabecera(u)
    )
    assert r.status_code == 422


async def test_trasplante_suma_plantas_a_la_siembra(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    lote_tierra = await f.lote(finca)
    cultivo = await f.cultivo()
    h = f.cabecera(u)
    siembra = (
        await cliente.post(
            "/api/v1/siembras",
            json=payload_siembra(finca.id, lote_tierra.id, cultivo.id, plantas_sembradas=10),
            headers=h,
        )
    ).json()
    vivero = (await cliente.post(URL, json=nuevo(finca.id, cultivo.id), headers=h)).json()["id"]
    await cliente.patch(f"{URL}/{vivero}", json={"germinadas": 80, "listas": 60}, headers=h)

    demasiado = await cliente.post(
        f"{URL}/{vivero}/trasplante", json={"siembra_id": siembra["id"], "cantidad": 61}, headers=h
    )
    assert demasiado.status_code == 422
    ok = await cliente.post(
        f"{URL}/{vivero}/trasplante", json={"siembra_id": siembra["id"], "cantidad": 40}, headers=h
    )
    assert ok.status_code == 200
    assert ok.json()["trasplantadas"] == 40
    leida = await cliente.get(f"/api/v1/siembras/{siembra['id']}", headers=h)
    assert leida.json()["plantas_sembradas"] == 50
    resto = await cliente.post(
        f"{URL}/{vivero}/trasplante", json={"siembra_id": siembra["id"], "cantidad": 21}, headers=h
    )
    assert resto.status_code == 422


async def test_no_se_toca_el_vivero_de_otra_finca(cliente: AsyncClient, f: Fabrica) -> None:
    dueno, intruso = await f.usuario(), await f.usuario()
    finca = await f.finca(dueno)
    cultivo = await f.cultivo()
    lote = (
        await cliente.post(URL, json=nuevo(finca.id, cultivo.id), headers=f.cabecera(dueno))
    ).json()["id"]
    r = await cliente.patch(f"{URL}/{lote}", json={"germinadas": 1}, headers=f.cabecera(intruso))
    assert r.status_code == 404
    lista = await cliente.get(URL, headers=f.cabecera(intruso))
    assert lista.json()["total"] == 0
