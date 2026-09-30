"""Vista 13: Catálogo de cultivos."""

from tests.conftest import payload_cultivo

URL = "/api/v1/cultivos"
ENTRAN = {"admin", "agricultor"}


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    await entrar_como(clave)
    r = await cliente.get(URL)
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_busca_y_filtra_por_tipo_de_ciclo(cliente, entrar_como, f):
    await entrar_como("agricultor")
    await f.cultivo("Maíz de prueba", tipo_ciclo="transitorio", tipo_renovacion=None)
    await f.cultivo("Café de prueba")
    assert (await cliente.get(URL, params={"q": "maíz"})).json()["total"] == 1
    assert (await cliente.get(URL, params={"tipo_ciclo": "permanente"})).json()["total"] == 1


async def test_crea_desde_la_vista_y_no_se_duplica(cliente, entrar_como):
    await entrar_como("agricultor")
    assert (await cliente.post(URL, json=payload_cultivo())).status_code == 201
    repetido = await cliente.post(URL, json=payload_cultivo())
    assert repetido.status_code == 409
    assert repetido.json()["error"] == "CULTIVO_DUPLICADO"


async def test_el_perfil_nuevo_se_puede_copiar_de_otro(cliente, entrar_como):
    await entrar_como("agricultor")
    origen = (await cliente.post(URL, json=payload_cultivo())).json()
    copia = payload_cultivo(nombre="Copia", fases=[], metodos=[], dosis=[], copiar_de=origen["id"])
    r = await cliente.post(URL, json=copia)
    assert len(r.json()["fases"]) == 2


async def test_la_pagina_tiene_tope(cliente, entrar_como):
    await entrar_como("agricultor")
    assert (await cliente.get(URL, params={"limit": 51})).status_code == 422
