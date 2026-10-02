"""Vista 31: Biblioteca de conocimiento."""

URL = "/conocimiento"


async def test_todos_los_roles_entran(cliente, entrar_como, clave):
    await entrar_como(clave)
    assert (await cliente.get(URL)).status_code == 200


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_muestra_solo_lo_validado_a_quien_no_revisa(cliente, entrar_como, f):
    await f.ficha("Validada", estado="validado")
    await f.ficha("Borrador", estado="borrador")
    await f.ficha("Retirada", estado="retirado")
    await entrar_como("agricultor")
    assert [i["nombre"] for i in (await cliente.get(URL)).json()["items"]] == ["Validada"]


async def test_busca_y_filtra(cliente, entrar_como, f):
    cultivo = await f.cultivo()
    await f.ficha("Roya", cultivo=cultivo, sintomas=("polvo naranja",))
    await f.ficha("Broca", sintomas=("perforaciones en el fruto",))
    await entrar_como("agricultor")
    assert (await cliente.get(URL, params={"q": "polvo"})).json()["total"] == 1
    assert (await cliente.get(URL, params={"cultivo_id": str(cultivo.id)})).json()["total"] == 1
    assert (await cliente.get(URL, params={"tipo": "plaga"})).json()["total"] == 0


async def test_pagina_con_tope(cliente, entrar_como):
    await entrar_como("agricultor")
    assert (await cliente.get(URL, params={"limit": 51})).status_code == 422
