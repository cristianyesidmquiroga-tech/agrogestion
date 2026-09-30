from datetime import date

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


async def test_necesidad_de_insumos_por_planta_y_por_hectarea(
    cliente: AsyncClient, f: Fabrica
) -> None:
    dosis = (("abono", "0.25", "kg", "planta"), ("cal", "100", "kg", "hectarea"))
    h, siembra, ciclo = await preparar(cliente, f, dosis=dosis)
    antes = await cliente.get(f"/api/v1/ciclos/{ciclo}/necesidad-insumos", headers=h)
    por_planta = next(i for i in antes.json()["items"] if i["base"] == "planta")
    assert por_planta["cantidad_necesaria"] is None
    assert "Cuente las plantas" in por_planta["mensaje"]

    await cliente.post(f"/api/v1/siembras/{siembra}/conteos", json=conteo(vivas=80), headers=h)
    r = await cliente.get(f"/api/v1/ciclos/{ciclo}/necesidad-insumos", headers=h)
    cantidades = {i["insumo_tipo"]: i["cantidad_necesaria"] for i in r.json()["items"]}
    assert cantidades == {"abono": 20.0, "cal": 200.0}


async def test_sin_dosis_cargadas_lo_dice(cliente: AsyncClient, f: Fabrica) -> None:
    h, _, ciclo = await preparar(cliente, f)
    r = await cliente.get(f"/api/v1/ciclos/{ciclo}/necesidad-insumos", headers=h)
    assert r.json()["items"] == []
    assert "Falta cargar las dosis" in r.json()["aviso"]
