from datetime import UTC, datetime
from decimal import Decimal

URL = "/estadisticas"


async def _datos(f):
    admin = await f.usuario("admin")
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno, area_lote="8")
    activa = await f.siembra(finca, lote, cultivo, area="2", estado="en_curso")
    await f.siembra(finca, lote, cultivo, area="3", estado="planeada")
    ciclo = await f.ciclo_de(activa)
    gastos = {"Insumos": ["100", "50"], "Mano de obra": ["400"]}
    for categoria, montos in gastos.items():
        for monto in montos:
            await f.gasto(finca, monto, categoria, ciclo)
    await f.gasto(finca, "999", "Anulado", estado="anulado")
    ingresos = ["900", "300"]
    for total in ingresos:
        await f.ingreso(finca, total, ciclo=ciclo)
    cosechas = ["10", "20"]
    for cantidad in cosechas:
        await f.cosecha(finca, ciclo, cantidad)
    return admin, finca, gastos, ingresos, cosechas


async def test_el_resumen_suma_todo_lo_activo(cliente, f):
    admin, finca, gastos, ingresos, cosechas = await _datos(f)
    total_gastos = sum(Decimal(m) for ms in gastos.values() for m in ms)
    total_ingresos = sum(Decimal(i) for i in ingresos)
    r = (await cliente.get(f"{URL}/resumen", headers=f.cabecera(admin))).json()
    assert r["usuarios"] == 2
    assert r["usuarios_por_rol"] == {"admin": 1, "agricultor": 1}
    assert r["fincas"] == 1
    assert r["siembras"] == 2
    assert r["siembras_por_estado"] == {"en_curso": 1, "planeada": 1}
    assert r["ciclos_abiertos"] == 1
    assert r["cosechas"] == len(cosechas)
    assert r["gastos"] == float(total_gastos)
    assert r["ingresos"] == float(total_ingresos)
    assert r["utilidad"] == float(total_ingresos - total_gastos)


async def test_el_crecimiento_agrupa_por_mes_y_rellena_los_vacios(cliente, f):
    admin, finca, gastos, ingresos, cosechas = await _datos(f)
    meses = 4
    r = (
        await cliente.get(f"{URL}/crecimiento", params={"meses": meses}, headers=f.cabecera(admin))
    ).json()
    hoy = datetime.now(UTC)
    assert len(r) == meses
    assert r[-1]["mes"] == f"{hoy.year}-{hoy.month:02d}"
    assert [p["mes"] for p in r] == sorted(p["mes"] for p in r)
    actual, anteriores = r[-1], r[:-1]
    assert actual["usuarios"] == 2
    assert actual["siembras"] == 2
    assert actual["cosechas"] == len(cosechas)
    assert actual["gastos"] == float(sum(Decimal(m) for ms in gastos.values() for m in ms))
    assert all(p["usuarios"] == 0 and p["gastos"] == 0 for p in anteriores)


async def test_el_crecimiento_valida_la_ventana(cliente, f):
    admin = await f.usuario("admin")
    for meses in (0, 37):
        r = await cliente.get(
            f"{URL}/crecimiento", params={"meses": meses}, headers=f.cabecera(admin)
        )
        assert r.status_code == 422


async def test_los_costos_se_ordenan_y_se_dividen_por_hectarea(cliente, f):
    admin, finca, gastos, ingresos, cosechas = await _datos(f)
    r = (await cliente.get(f"{URL}/costos", headers=f.cabecera(admin))).json()
    por_categoria = {c["categoria"]: c for c in r["gastos_por_categoria"]}
    assert set(por_categoria) == set(gastos)
    for categoria, montos in gastos.items():
        assert por_categoria[categoria]["total"] == float(sum(Decimal(m) for m in montos))
        assert por_categoria[categoria]["registros"] == len(montos)
    totales = [c["total"] for c in r["gastos_por_categoria"]]
    assert totales == sorted(totales, reverse=True)
    assert r["area_sembrada_ha"] == 2.0
    assert r["gasto_por_ha"] == r["gastos"] / r["area_sembrada_ha"]
    assert r["ingreso_por_ha"] == r["ingresos"] / r["area_sembrada_ha"]


async def test_sin_siembras_no_hay_costo_por_hectarea(cliente, f):
    admin = await f.usuario("admin")
    r = (await cliente.get(f"{URL}/costos", headers=f.cabecera(admin))).json()
    assert r["gasto_por_ha"] is None
    assert r["ingreso_por_ha"] is None
    assert r["gastos_por_categoria"] == []
