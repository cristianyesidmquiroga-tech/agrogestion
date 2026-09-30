"""Vista 8: Mis siembras."""

from tests.conftest import payload_siembra

URL = "/api/v1/siembras"
ENTRAN = {"admin", "agricultor", "contador"}


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    await entrar_como(clave)
    r = await cliente.get(URL)
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_solo_aparecen_las_siembras_propias(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    otro = await f.usuario("agricultor")
    await f.siembra(*await f.escenario(yo))
    await f.siembra(*await f.escenario(otro))
    assert (await cliente.get(URL)).json()["total"] == 1


async def test_filtra_por_estado(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote, cultivo = await f.escenario(yo, area_lote="10")
    await f.siembra(finca, lote, cultivo, estado="planeada")
    await f.siembra(finca, lote, cultivo, estado="en_curso")
    assert (await cliente.get(URL, params={"estado": "en_curso"})).json()["total"] == 1
    assert (await cliente.get(URL, params={"estado": "cerrada"})).json()["total"] == 0


async def test_pagina_con_tope(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote, cultivo = await f.escenario(yo, area_lote="10")
    for _ in range(3):
        await f.siembra(finca, lote, cultivo)
    r = (await cliente.get(URL, params={"limit": 2})).json()
    assert len(r["items"]) == 2
    assert r["has_more"] is True
    assert (await cliente.get(URL, params={"limit": 51})).status_code == 422


async def test_planear_desde_la_vista(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote, cultivo = await f.escenario(yo)
    r = await cliente.post(URL, json=payload_siembra(finca.id, lote.id, cultivo.id))
    assert r.status_code == 201
    assert r.json()["ciclos"][0]["tipo"] == "levante"


async def test_no_cabe_mas_de_lo_que_tiene_el_lote(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote, cultivo = await f.escenario(yo, area_lote="1")
    r = await cliente.post(URL, json=payload_siembra(finca.id, lote.id, cultivo.id, area_ha=2))
    assert r.json()["error"] == "AREA_SUPERA_LOTE"
