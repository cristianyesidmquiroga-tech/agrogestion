"""Vista 2: Autorización de datos."""

URL_POLITICA = "/politica"
URL = "/cuenta/consentimiento"


async def test_la_politica_se_lee_sin_iniciar_sesion(cliente):
    r = await cliente.get(URL_POLITICA)
    assert r.status_code == 200
    assert r.json()["estado"] == "borrador"


async def test_aceptar_pide_sesion(cliente):
    r = await cliente.post(URL, json={"version_politica": "x", "acepta_tratamiento": True})
    assert r.status_code == 401


async def test_todos_los_roles_pueden_aceptar(cliente, entrar_como, clave):
    await entrar_como(clave)
    version = (await cliente.get(URL_POLITICA)).json()["version"]
    r = await cliente.post(URL, json={"version_politica": version, "acepta_tratamiento": True})
    assert r.status_code == 201


async def test_sin_aceptar_el_tratamiento_no_continua(cliente, entrar_como):
    await entrar_como("agricultor")
    version = (await cliente.get(URL_POLITICA)).json()["version"]
    r = await cliente.post(URL, json={"version_politica": version, "acepta_tratamiento": False})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "CONSENTIMIENTO_REQUERIDO"


async def test_la_autorizacion_de_ia_es_aparte(cliente, entrar_como):
    await entrar_como("agricultor")
    version = (await cliente.get(URL_POLITICA)).json()["version"]
    await cliente.post(URL, json={"version_politica": version, "acepta_tratamiento": True})
    ultimo = (await cliente.get(URL)).json()
    assert ultimo["acepta_transferencia_ia"] is False
