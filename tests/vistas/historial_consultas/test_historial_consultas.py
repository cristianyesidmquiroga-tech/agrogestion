"""Vista 39: Historial de consultas."""

URL = "/api/v1/consultas"
ENTRAN = {"admin", "agricultor"}


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    await entrar_como(clave)
    r = await cliente.get(URL)
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_lista_solo_lo_mio_y_busca(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo))
    for texto in ("Las hojas tienen manchas amarillas", "El fruto tiene perforaciones"):
        await cliente.post(URL, json={"siembra_id": str(siembra.id), "texto": texto})
    assert (await cliente.get(URL)).json()["total"] == 2
    uno = (await cliente.get(URL, params={"q": "perforaciones"})).json()
    assert uno["total"] == 1
    assert uno["items"][0]["pregunta"] == "El fruto tiene perforaciones"
    assert uno["items"][0]["valoracion"] is None


async def test_la_lista_pagina(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo))
    for n in range(3):
        await cliente.post(
            URL, json={"siembra_id": str(siembra.id), "texto": f"Consulta numero {n} sobre hojas"}
        )
    r = (await cliente.get(URL, params={"limit": 2})).json()
    assert len(r["items"]) == 2
    assert r["has_more"] is True


async def test_otro_no_ve_mis_consultas(cliente, entrar_como, f):
    dueno = await f.usuario()
    siembra = await f.siembra(*await f.escenario(dueno))
    from app.core.security import crear_token

    await cliente.post(
        URL,
        json={"siembra_id": str(siembra.id), "texto": "Las hojas se ven mal"},
        headers={"Authorization": f"Bearer {crear_token(dueno.id)}"},
    )
    await entrar_como("agricultor")
    assert (await cliente.get(URL)).json()["total"] == 0
