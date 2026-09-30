from datetime import date, timedelta

from httpx import AsyncClient

from tests.conftest import Fabrica, payload_siembra


async def preparar(cliente: AsyncClient, f: Fabrica, dosis=(), **cultivo):  # type: ignore[no-untyped-def]
    usuario = await f.usuario()
    finca = await f.finca(usuario)
    lote = await f.lote(finca)
    c = await f.cultivo(dosis=dosis, **cultivo)
    h = f.cabecera(usuario)
    creada = (
        await cliente.post(
            "/api/v1/siembras", json=payload_siembra(finca.id, lote.id, c.id), headers=h
        )
    ).json()
    return h, creada["id"], creada["ciclos"][0]["id"]


def conteo(**extra: object) -> dict[str, object]:
    base: dict[str, object] = {"fecha": date.today().isoformat(), "vivas": 90}
    base.update(extra)
    return base


async def test_registrar_y_listar_conteos(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, _ = await preparar(cliente, f)
    r = await cliente.post(
        f"/api/v1/siembras/{siembra}/conteos", json=conteo(muertas=10), headers=h
    )
    assert r.status_code == 201
    lista = await cliente.get(f"/api/v1/siembras/{siembra}/conteos", headers=h)
    assert len(lista.json()) == 1


async def test_las_vivas_no_superan_lo_sembrado(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, _ = await preparar(cliente, f)
    r = await cliente.post(f"/api/v1/siembras/{siembra}/conteos", json=conteo(vivas=101), headers=h)
    assert r.status_code == 422
    assert r.json()["error"] == "CONTEO_INVALIDO"
    con_resiembra = await cliente.post(
        f"/api/v1/siembras/{siembra}/conteos", json=conteo(vivas=105, resiembras=5), headers=h
    )
    assert con_resiembra.status_code == 201


async def test_la_fecha_del_conteo_no_puede_ser_futura(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, _ = await preparar(cliente, f)
    manana = (date.today() + timedelta(days=1)).isoformat()
    r = await cliente.post(
        f"/api/v1/siembras/{siembra}/conteos", json=conteo(fecha=manana), headers=h
    )
    assert r.status_code == 422


async def test_cultivo_por_area_no_se_cuenta_por_planta(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, _ = await preparar(cliente, f, nombre="Por area", unidad_conteo="area")
    r = await cliente.post(f"/api/v1/siembras/{siembra}/conteos", json=conteo(), headers=h)
    assert r.status_code == 422
    assert r.json()["error"] == "CONTEO_NO_APLICA"
    indices = await cliente.get(f"/api/v1/siembras/{siembra}/indices", headers=h)
    assert indices.json()["indicadores"] == []
    assert "por área" in indices.json()["aviso"]


async def test_indices_de_poblacion(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, _ = await preparar(cliente, f)
    sin_conteo = await cliente.get(f"/api/v1/siembras/{siembra}/indices", headers=h)
    assert sin_conteo.json()["indicadores"] == []
    assert "Cuente sus plantas" in sin_conteo.json()["aviso"]

    await cliente.post(f"/api/v1/siembras/{siembra}/conteos", json=conteo(vivas=90), headers=h)
    r = await cliente.get(f"/api/v1/siembras/{siembra}/indices", headers=h)
    densidad, perdidas = r.json()["indicadores"]
    assert densidad["valor"] == 45.0
    assert densidad["estado"] == "informativo"
    assert perdidas["valor"] == 10.0
    assert perdidas["fecha_datos"] == date.today().isoformat()
    assert r.json()["fecha_conteo"] == date.today().isoformat()
