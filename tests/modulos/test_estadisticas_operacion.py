from datetime import UTC, datetime, timedelta
from decimal import Decimal

URL = "/estadisticas"
INICIO = datetime(2026, 3, 1, tzinfo=UTC)


async def _pedir(cliente, f, ruta):
    admin = await f.usuario("admin")
    return (await cliente.get(f"{URL}/{ruta}", headers=f.cabecera(admin))).json()


async def _finca_con_ciclo(f, **zona):
    dueno = await f.usuario("agricultor")
    finca = await f.finca(dueno, **zona)
    lote = await f.lote(finca)
    siembra = await f.siembra(finca, lote, await f.cultivo(), estado="en_curso")
    return finca, await f.ciclo_de(siembra)


async def test_la_mano_de_obra_separa_pendiente_y_pagado_por_zona(cliente, f):
    finca_uno, ciclo_uno = await _finca_con_ciclo(f)
    finca_dos, ciclo_dos = await _finca_con_ciclo(f, departamento="76", municipio="76001")
    await f.trabajador(finca_uno, "jornalero")
    await f.trabajador(finca_uno, "fijo")
    await f.trabajador(finca_dos, "jornalero")
    await f.trabajador(finca_dos, "fijo", estado="inactivo")
    pendientes = ["100", "50"]
    pagados = ["400"]
    for dia, total in enumerate(pendientes):
        await f.jornal(finca_uno, ciclo_uno, total, dia=dia)
    await f.jornal(finca_uno, ciclo_uno, pagados[0], estado="pagado", modalidad="destajo", dia=9)
    await f.jornal(finca_dos, ciclo_dos, "70")
    r = await _pedir(cliente, f, "mano-de-obra")
    assert r["trabajadores"] == 3
    assert r["trabajadores_por_tipo"] == {"jornalero": 2, "fijo": 1}
    assert r["jornales"] == len(pendientes) + len(pagados) + 1
    assert r["jornales_pendientes"] == len(pendientes) + 1
    assert r["total_pendiente"] == float(sum(Decimal(p) for p in pendientes) + 70)
    assert r["jornales_pagados"] == len(pagados)
    assert r["total_pagado"] == float(sum(Decimal(p) for p in pagados))
    modalidades = {m["categoria"]: m for m in r["por_modalidad"]}
    assert modalidades["destajo"]["total"] == float(pagados[0])
    assert [m["total"] for m in r["por_modalidad"]] == sorted(
        (m["total"] for m in r["por_modalidad"]), reverse=True
    )
    zonas = {z["zona"]: z for z in r["por_zona"]}
    assert set(zonas) == {"05", "76"}
    assert zonas["05"]["trabajadores"] == 2
    assert zonas["05"]["pagado"] == float(pagados[0])
    assert zonas["76"]["pendiente"] == 70.0
    assert sum(z["pendiente"] + z["pagado"] for z in r["por_zona"]) == (
        r["total_pendiente"] + r["total_pagado"]
    )


async def test_la_mano_de_obra_vacia_trae_ceros(cliente, f):
    r = await _pedir(cliente, f, "mano-de-obra")
    assert (r["trabajadores"], r["jornales"], r["total_pendiente"]) == (0, 0, 0)
    assert r["por_zona"] == []


async def test_el_inventario_cuenta_agotados_consumos_y_los_mas_usados(cliente, f):
    finca, _ = await _finca_con_ciclo(f)
    urea = await f.insumo(finca, "Urea", "bulto", "0")
    cal = await f.insumo(finca, "Cal", "bulto", "30")
    semilla = await f.insumo(finca, "Semilla", "kilo", "5")
    entradas = [("100", "3000"), ("50", "1500")]
    for cantidad, costo in entradas:
        await f.movimiento(finca, urea, "entrada", cantidad, costo)
    consumos = {urea: ["60", "40"], cal: ["10"], semilla: ["2"]}
    for insumo, cantidades in consumos.items():
        for cantidad in cantidades:
            await f.movimiento(finca, insumo, "consumo", cantidad)
    r = await _pedir(cliente, f, "inventario")
    assert r["insumos"] == 3
    assert r["agotados"] == 1
    assert r["entradas"] == len(entradas)
    assert r["costo_entradas"] == float(sum(Decimal(c) for _, c in entradas))
    assert r["consumos"] == sum(len(c) for c in consumos.values())
    unidades = {u["unidad"]: u for u in r["por_unidad"]}
    assert unidades["bulto"]["insumos"] == 2
    assert unidades["bulto"]["existencia"] == 30.0
    ranking = [(i["nombre"], i["consumido"]) for i in r["mas_consumidos"]]
    assert ranking[0] == ("Urea", float(sum(Decimal(c) for c in consumos[urea])))
    assert [c for _, c in ranking] == sorted((c for _, c in ranking), reverse=True)


async def test_el_inventario_vacio_trae_ceros(cliente, f):
    r = await _pedir(cliente, f, "inventario")
    assert (r["insumos"], r["agotados"], r["consumos"], r["mas_consumidos"]) == (0, 0, 0, [])


async def test_los_procesos_miden_duracion_origen_y_retrasos(cliente, f):
    finca, _ = await _finca_con_ciclo(f)
    dias_secado = 6
    secado = await f.proceso(finca, "Café seco", INICIO, INICIO + timedelta(days=dias_secado))
    await f.proceso(finca, "Café seco", INICIO, origen="comprada")
    await f.proceso(finca, "Panela", INICIO, INICIO + timedelta(days=2))
    estimado = 3
    await f.etapa(secado, estimado, INICIO, INICIO + timedelta(days=estimado + 1))
    await f.etapa(secado, estimado, INICIO, INICIO + timedelta(days=estimado - 1))
    await f.etapa(secado, estimado, INICIO)
    r = await _pedir(cliente, f, "procesos")
    assert (r["procesos"], r["finalizados"], r["en_curso"]) == (3, 2, 1)
    assert r["duracion_media_dias"] == (dias_secado + 2) / 2
    assert r["por_origen"] == {"propia": 2, "comprada": 1}
    assert (r["etapas"], r["etapas_finalizadas"], r["etapas_con_retraso"]) == (3, 2, 1)
    productos = {p["producto"]: p for p in r["por_producto"]}
    assert productos["Café seco"]["procesos"] == 2
    assert productos["Café seco"]["duracion_media_dias"] == dias_secado
    assert productos["Panela"]["finalizados"] == 1
    assert r["por_producto"][0]["producto"] == "Café seco"


async def test_los_procesos_vacios_no_tienen_duracion(cliente, f):
    r = await _pedir(cliente, f, "procesos")
    assert (r["procesos"], r["duracion_media_dias"], r["por_producto"]) == (0, None, [])
