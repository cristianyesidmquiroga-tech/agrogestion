from datetime import UTC, datetime, timedelta
from decimal import Decimal

URL = "/estadisticas"
BASE = datetime(2026, 5, 1, tzinfo=UTC)


async def _escenario(f):
    admin = await f.usuario("admin")
    ana, beto = await f.usuario("agricultor"), await f.usuario("agricultor")
    cafe, maiz = await f.cultivo("Café"), await f.cultivo("Maíz")
    finca_ana = await f.finca(ana)
    finca_beto = await f.finca(beto, departamento="76", municipio="76001")
    lote_ana, lote_beto = await f.lote(finca_ana), await f.lote(finca_beto)
    siembra_cafe = await f.siembra(finca_ana, lote_ana, cafe, area="2", estado="en_curso")
    siembra_maiz = await f.siembra(finca_beto, lote_beto, maiz, area="1", estado="planeada")
    ciclo_cafe, ciclo_maiz = await f.ciclo_de(siembra_cafe), await f.ciclo_de(siembra_maiz)
    cantidades_ana = ["4", "6", "8"]
    for dias, cantidad in enumerate(cantidades_ana):
        await f.cosecha(finca_ana, ciclo_cafe, cantidad, BASE + timedelta(days=dias * 10))
    cantidad_beto = "50"
    await f.cosecha(finca_beto, ciclo_maiz, cantidad_beto, BASE)
    return admin, ana, beto, cafe, cantidades_ana, cantidad_beto


async def _pedir(cliente, f, admin, ruta, **params):
    return (await cliente.get(f"{URL}/{ruta}", params=params, headers=f.cabecera(admin))).json()


async def test_la_produccion_lista_cada_cosecha_con_su_fecha_y_productor(cliente, f):
    admin, ana, _beto, _cafe, cantidades, _ = await _escenario(f)
    r = await _pedir(cliente, f, admin, "produccion")
    assert r["total"] == len(cantidades) + 1
    fechas = [c["fecha"] for c in r["items"]]
    assert fechas == sorted(fechas, reverse=True)
    de_ana = [c for c in r["items"] if c["agricultor"] == ana.nombre]
    assert sorted(c["cantidad"] for c in de_ana) == sorted(float(c) for c in cantidades)
    assert all(c["zona"] == "05001" and c["cultivo"] == "Café" for c in de_ana)


async def test_la_produccion_se_filtra_por_cultivo_zona_y_fechas(cliente, f):
    admin, _ana, _beto, cafe, cantidades, cantidad_beto = await _escenario(f)
    por_cultivo = await _pedir(cliente, f, admin, "produccion", cultivo_id=str(cafe.id))
    assert por_cultivo["total"] == len(cantidades)
    por_depto = await _pedir(cliente, f, admin, "produccion", zona="76")
    assert [c["cantidad"] for c in por_depto["items"]] == [float(cantidad_beto)]
    por_municipio = await _pedir(cliente, f, admin, "produccion", zona="05001")
    assert por_municipio["total"] == len(cantidades)
    hasta = (BASE + timedelta(days=10)).date().isoformat()
    en_ventana = await _pedir(
        cliente, f, admin, "produccion", desde=BASE.date().isoformat(), hasta=hasta
    )
    assert en_ventana["total"] == 2 + 1


async def test_la_produccion_se_pagina(cliente, f):
    admin, *_ = await _escenario(f)
    r = await _pedir(cliente, f, admin, "produccion", limit=2)
    assert len(r["items"]) == 2
    assert r["has_more"] is True
    resto = await _pedir(cliente, f, admin, "produccion", limit=2, skip=2)
    assert len(resto["items"]) == r["total"] - 2


async def test_las_siembras_se_listan_con_zona_y_agricultor(cliente, f):
    admin, ana, beto, cafe, *_ = await _escenario(f)
    r = await _pedir(cliente, f, admin, "siembras")
    assert r["total"] == 2
    por_cultivo = {s["cultivo"]: s for s in r["items"]}
    assert por_cultivo["Café"]["estado"] == "en_curso"
    assert por_cultivo["Café"]["inicio_ciclo"] is not None
    assert por_cultivo["Maíz"]["inicio_ciclo"] is None
    assert por_cultivo["Maíz"]["zona"] == "76001"
    assert por_cultivo["Café"]["agricultor"] == ana.nombre
    assert por_cultivo["Maíz"]["agricultor"] == beto.nombre
    planeadas = await _pedir(cliente, f, admin, "siembras", estado="planeada")
    assert [s["cultivo"] for s in planeadas["items"]] == ["Maíz"]
    del_cafe = await _pedir(cliente, f, admin, "siembras", cultivo_id=str(cafe.id))
    assert del_cafe["total"] == 1


async def test_el_ranking_de_productores_ordena_por_cosechas(cliente, f):
    admin, ana, beto, _cafe, cantidades, cantidad_beto = await _escenario(f)
    r = await _pedir(cliente, f, admin, "productores")
    assert [p["usuario_id"] for p in r] == [str(ana.id), str(beto.id)]
    primero, segundo = r
    assert primero["cosechas"] == len(cantidades)
    assert primero["produccion"] == [
        {"unidad": "kilo", "cantidad": float(sum(Decimal(c) for c in cantidades))}
    ]
    assert primero["fincas"] == 1
    assert segundo["cosechas"] == 1
    assert segundo["ultima_cosecha"] == BASE.date().isoformat()


async def test_las_cosechas_anuladas_no_cuentan(cliente, f):
    admin, ana, *_ = await _escenario(f)
    antes = await _pedir(cliente, f, admin, "produccion")
    cosecha = await f.cosecha(await f.finca(ana), await f.ciclo_de(await _siembra(f, ana)), "99")
    cosecha.estado = "anulada"
    f.s.add(cosecha)
    await f.s.commit()
    assert (await _pedir(cliente, f, admin, "produccion"))["total"] == antes["total"]


async def _siembra(f, usuario):
    finca, lote, cultivo = await f.escenario(usuario)
    return await f.siembra(finca, lote, cultivo, estado="en_curso")


async def test_los_filtros_invalidos_se_rechazan(cliente, f):
    admin = await f.usuario("admin")
    h = f.cabecera(admin)
    assert (
        await cliente.get(f"{URL}/siembras", params={"estado": "x"}, headers=h)
    ).status_code == 422
    assert (
        await cliente.get(f"{URL}/produccion", params={"zona": "1"}, headers=h)
    ).status_code == 422
