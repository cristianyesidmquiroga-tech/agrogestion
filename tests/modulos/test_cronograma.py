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
        await cliente.post("/siembras", json=payload_siembra(finca.id, lote.id, c.id), headers=h)
    ).json()
    return h, creada["id"], creada["ciclos"][0]["id"]


def conteo(**extra: object) -> dict[str, object]:
    base: dict[str, object] = {"fecha": date.today().isoformat(), "vivas": 90}
    base.update(extra)
    return base


async def test_cronograma_calcula_fechas_desde_el_inicio(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, ciclo = await preparar(cliente, f)
    antes = await cliente.get(f"/ciclos/{ciclo}/cronograma", headers=h)
    assert antes.json()["fases"][0]["inicio_plan"] is None
    assert "cuando el ciclo inicia" in antes.json()["aviso"]

    inicio = date(2026, 1, 1)
    await cliente.post(
        f"/siembras/{siembra}/iniciar", json={"fecha_inicio": inicio.isoformat()}, headers=h
    )
    r = await cliente.get(f"/ciclos/{ciclo}/cronograma", headers=h)
    fases = r.json()["fases"]
    assert [x["fase"] for x in fases] == ["preparacion", "siembra", "mantenimiento"]
    assert fases[0]["inicio_plan"] == "2026-01-01"
    assert fases[0]["fin_plan"] == "2026-01-11"
    assert fases[1]["inicio_plan"] == "2026-01-11"
    assert fases[1]["fin_plan"] == "2026-01-16"
    assert fases[0]["inicio_real"] is None
