from datetime import UTC, datetime, timedelta
from decimal import Decimal

URL = "/estadisticas"
INICIO = datetime(2026, 1, 1, tzinfo=UTC)
FIN = datetime(2026, 3, 1, tzinfo=UTC)


async def _escenario(f):
    admin = await f.usuario("admin")
    uno, dos = await f.usuario("agricultor"), await f.usuario("agricultor")
    cafe, maiz = await f.cultivo("Café"), await f.cultivo("Maíz")
    finca_uno = await f.finca(uno)
    finca_dos = await f.finca(dos, departamento="76", municipio="76001")
    lote_uno, lote_dos = await f.lote(finca_uno), await f.lote(finca_dos)
    abierta = await f.siembra(finca_uno, lote_uno, cafe, area="2", estado="en_curso")
    cerrada = await f.siembra(finca_uno, lote_uno, cafe, area="3", estado="cerrada")
    otra = await f.siembra(finca_dos, lote_dos, cafe, area="1", estado="en_curso")
    solo_maiz = await f.siembra(finca_dos, lote_dos, maiz, area="4", estado="en_curso")
    ciclo_cerrado = await f.ciclo_de(cerrada)
    ciclo_cerrado.estado, ciclo_cerrado.fecha_inicio, ciclo_cerrado.fecha_fin = (
        "cerrado",
        INICIO,
        FIN,
    )
    f.s.add(ciclo_cerrado)
    await f.s.commit()
    ciclo = await f.ciclo_de(abierta)
    separaciones = [10, 20]
    fecha = INICIO
    cantidades = ["5", "7"]
    await f.cosecha(finca_uno, ciclo, cantidades[0], fecha)
    for dias, cantidad in zip(separaciones, cantidades[1:] + ["3"], strict=False):
        fecha += timedelta(days=dias)
        await f.cosecha(finca_uno, ciclo, cantidad, fecha)
    gasto_cafe, ingreso_cafe, gasto_maiz = "100", "300", "50"
    await f.gasto(finca_uno, gasto_cafe, ciclo=ciclo)
    await f.ingreso(finca_uno, ingreso_cafe, ciclo=ciclo)
    await f.gasto(finca_dos, gasto_maiz, ciclo=await f.ciclo_de(solo_maiz))
    return admin, otra, separaciones, (gasto_cafe, ingreso_cafe, gasto_maiz)


async def _cultivos(cliente, f, admin):
    r = (await cliente.get(f"{URL}/cultivos", headers=f.cabecera(admin))).json()
    return {c["cultivo"]: c for c in r}, r


async def test_los_cultivos_se_ordenan_por_registros_y_cuentan_quienes_los_siembran(cliente, f):
    admin, *_ = await _escenario(f)
    por_nombre, lista = await _cultivos(cliente, f, admin)
    assert [c["cultivo"] for c in lista] == ["Café", "Maíz"]
    cafe = por_nombre["Café"]
    assert (cafe["siembras"], cafe["fincas"], cafe["agricultores"]) == (3, 2, 2)
    assert cafe["area_ha"] == 2 + 3 + 1
    assert por_nombre["Maíz"]["siembras"] == 1


async def test_la_duracion_de_los_ciclos_sale_de_sus_fechas(cliente, f):
    admin, *_ = await _escenario(f)
    cafe = (await _cultivos(cliente, f, admin))[0]["Café"]
    esperado = (FIN - INICIO).days
    assert cafe["ciclos_cerrados"] == 1
    assert cafe["duracion_media_dias"] == esperado
    assert cafe["ciclo_mas_largo_dias"] == esperado
    assert cafe["ciclos_abiertos"] == 2


async def test_las_cosechas_dan_produccion_fechas_e_intervalo(cliente, f):
    admin, _otra, separaciones, _ = await _escenario(f)
    cafe = (await _cultivos(cliente, f, admin))[0]["Café"]
    assert cafe["cosechas"] == len(separaciones) + 1
    assert cafe["produccion"] == [{"unidad": "kilo", "cantidad": 5 + 7 + 3}]
    assert cafe["primera_cosecha"] == INICIO.date().isoformat()
    assert cafe["ultima_cosecha"] == (INICIO + timedelta(days=sum(separaciones))).date().isoformat()
    assert cafe["dias_entre_cosechas"] == sum(separaciones) / len(separaciones)


async def test_el_dinero_se_atribuye_al_cultivo_de_su_ciclo(cliente, f):
    admin, _otra, _sep, (gasto_cafe, ingreso_cafe, gasto_maiz) = await _escenario(f)
    por_nombre = (await _cultivos(cliente, f, admin))[0]
    cafe, maiz = por_nombre["Café"], por_nombre["Maíz"]
    assert cafe["gastos"] == float(gasto_cafe)
    assert cafe["utilidad"] == float(Decimal(ingreso_cafe) - Decimal(gasto_cafe))
    assert maiz["gastos"] == float(gasto_maiz)
    assert maiz["ingresos"] == 0
    assert maiz["dias_entre_cosechas"] is None
    assert maiz["produccion"] == []


async def test_las_zonas_se_comparan_por_departamento_y_municipio(cliente, f):
    admin, _otra, _sep, (gasto_cafe, _ingreso, gasto_maiz) = await _escenario(f)
    h = f.cabecera(admin)
    por_depto = {z["zona"]: z for z in (await cliente.get(f"{URL}/zonas", headers=h)).json()}
    assert set(por_depto) == {"05", "76"}
    antioquia, valle = por_depto["05"], por_depto["76"]
    assert (antioquia["fincas"], antioquia["agricultores"], antioquia["siembras"]) == (1, 1, 2)
    assert antioquia["area_sembrada_ha"] == 2 + 3
    assert antioquia["gasto_por_ha"] == float(Decimal(gasto_cafe) / 5)
    assert valle["cultivos_principales"] == ["Café", "Maíz"]
    assert valle["gastos"] == float(gasto_maiz)
    por_municipio = (
        await cliente.get(f"{URL}/zonas", params={"nivel": "municipio"}, headers=h)
    ).json()
    assert {z["zona"] for z in por_municipio} == {"05001", "76001"}


async def test_una_finca_sin_zona_se_agrupa_aparte(cliente, f):
    admin = await f.usuario("admin")
    finca = await f.finca(await f.usuario("agricultor"))
    finca.departamento_dane = finca.municipio_dane = None
    f.s.add(finca)
    await f.s.commit()
    zonas = (await cliente.get(f"{URL}/zonas", headers=f.cabecera(admin))).json()
    assert [z["zona"] for z in zonas] == ["sin_zona"]
    assert zonas[0]["gasto_por_ha"] is None


async def test_el_nivel_de_zona_invalido_se_rechaza(cliente, f):
    admin = await f.usuario("admin")
    r = await cliente.get(f"{URL}/zonas", params={"nivel": "vereda"}, headers=f.cabecera(admin))
    assert r.status_code == 422
