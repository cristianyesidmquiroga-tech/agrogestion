from datetime import date, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Riesgo
from tests.conftest import Fabrica, payload_siembra

URL = "/api/v1/eventos-adversos"


async def riesgo(sesion: AsyncSession, nombre: str = "Helada", tipo: str = "clima") -> Riesgo:
    r = Riesgo(nombre=nombre, tipo=tipo, aplica_a="cultivo")
    sesion.add(r)
    await sesion.commit()
    return r


def evento(finca_id: object, riesgo_id: object, **extra: object) -> dict[str, object]:
    base: dict[str, object] = {
        "finca_id": str(finca_id),
        "riesgo_id": str(riesgo_id),
        "inicio": date.today().isoformat(),
        "severidad": "severa",
    }
    base.update(extra)
    return base


async def test_registrar_ver_y_actualizar_un_evento(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    h = f.cabecera(u)
    ries = await riesgo(sesion)
    r = await cliente.post(
        URL, json=evento(finca.id, ries.id, perdida_pct=40, perdida_estimada="1200000"), headers=h
    )
    assert r.status_code == 201
    assert r.json()["perdida_pct"] == 40.0
    evento_id = r.json()["id"]
    assert (await cliente.get(f"{URL}/{evento_id}", headers=h)).status_code == 200
    cambio = await cliente.patch(
        f"{URL}/{evento_id}", json={"severidad": "moderada", "notas": "Menos daño"}, headers=h
    )
    assert cambio.json()["severidad"] == "moderada"
    assert cambio.json()["perdida_pct"] == 40.0


async def test_validaciones_del_evento(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    h = f.cabecera(u)
    ries = await riesgo(sesion)
    ayer = (date.today() - timedelta(days=1)).isoformat()
    assert (
        await cliente.post(URL, json=evento(finca.id, ries.id, fin=ayer), headers=h)
    ).status_code == 422
    assert (
        await cliente.post(URL, json=evento(finca.id, ries.id, perdida_pct=101), headers=h)
    ).status_code == 422
    inexistente = await cliente.post(
        URL, json=evento(finca.id, "00000000-0000-0000-0000-000000000000"), headers=h
    )
    assert inexistente.status_code == 404
    assert inexistente.json()["error"] == "RIESGO_NO_ENCONTRADO"


async def test_siembra_de_otra_finca_no_se_liga(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    u = await f.usuario()
    finca_a, finca_b = await f.finca(u), await f.finca(u)
    lote = await f.lote(finca_b)
    cultivo = await f.cultivo()
    h = f.cabecera(u)
    siembra = (
        await cliente.post(
            "/api/v1/siembras", json=payload_siembra(finca_b.id, lote.id, cultivo.id), headers=h
        )
    ).json()
    ries = await riesgo(sesion)
    r = await cliente.post(
        URL, json=evento(finca_a.id, ries.id, siembra_id=siembra["id"]), headers=h
    )
    assert r.status_code == 422
    ok = await cliente.post(
        URL, json=evento(finca_b.id, ries.id, siembra_id=siembra["id"]), headers=h
    )
    assert ok.status_code == 201
    por_ciclo = await cliente.post(
        URL, json=evento(finca_b.id, ries.id, ciclo_id=siembra["ciclos"][0]["id"]), headers=h
    )
    assert por_ciclo.status_code == 201
    ciclo_ajeno = await cliente.post(
        URL, json=evento(finca_a.id, ries.id, ciclo_id=siembra["ciclos"][0]["id"]), headers=h
    )
    assert ciclo_ajeno.status_code == 422


async def test_aislamiento_y_filtros(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    dueno, intruso = await f.usuario(), await f.usuario()
    finca = await f.finca(dueno)
    h = f.cabecera(dueno)
    helada, plaga = await riesgo(sesion), await riesgo(sesion, "Plaga de prueba", "plaga")
    propio = (await cliente.post(URL, json=evento(finca.id, helada.id), headers=h)).json()["id"]
    await cliente.post(URL, json=evento(finca.id, plaga.id), headers=h)

    assert (await cliente.get(f"{URL}/{propio}", headers=f.cabecera(intruso))).status_code == 404
    assert (await cliente.get(URL, headers=f.cabecera(intruso))).json()["total"] == 0
    assert (
        await cliente.post(URL, json=evento(finca.id, helada.id), headers=f.cabecera(intruso))
    ).status_code == 404
    assert (await cliente.get(URL, headers=h)).json()["total"] == 2
    solo_plagas = await cliente.get(URL, params={"tipo": "plaga"}, headers=h)
    assert solo_plagas.json()["total"] == 1
