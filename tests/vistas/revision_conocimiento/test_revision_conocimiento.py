"""Vista 33: Revisión de conocimiento."""

URL = "/conocimiento"
ENTRAN = {"admin", "experto"}
FICHA = {
    "nombre": "Mancha",
    "tipo": "enfermedad",
    "sintomas": [{"descripcion": "Manchas amarillas"}],
    "manejos": [],
}


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    await entrar_como(clave)
    r = await cliente.post(URL, json=FICHA)
    assert r.status_code == (201 if clave in ENTRAN else 403)
    fuentes = await cliente.get("/fuentes")
    assert fuentes.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.post(URL, json=FICHA)).status_code == 401


async def test_lista_por_estado(cliente, entrar_como, f):
    await f.ficha("Validada", estado="validado")
    await f.ficha("Borrador", estado="borrador")
    await f.ficha("Retirada", estado="retirado")
    await entrar_como("experto")
    for estado, nombre in [
        ("borrador", "Borrador"),
        ("validado", "Validada"),
        ("retirado", "Retirada"),
    ]:
        r = await cliente.get(URL, params={"estado": estado})
        assert [i["nombre"] for i in r.json()["items"]] == [nombre]


async def test_validar_y_retirar(cliente, entrar_como, f):
    await entrar_como("experto")
    fuente = (await cliente.post("/fuentes", json={"nombre": "Fuente A"})).json()
    manejo = {"tipo": "cultural", "descripcion": "Retirar hojas", "fuente_id": fuente["id"]}
    ficha = (await cliente.post(URL, json={**FICHA, "manejos": [manejo]})).json()
    validada = await cliente.patch(f"{URL}/{ficha['id']}/estado", json={"estado": "validado"})
    assert validada.json()["estado"] == "validado"
    retirada = await cliente.patch(
        f"{URL}/{ficha['id']}/estado", json={"estado": "retirado", "observacion": "Desactualizada"}
    )
    assert retirada.json()["estado"] == "retirado"
    assert [v["estado"] for v in retirada.json()["validaciones"]] == ["validado", "retirado"]


async def test_no_se_valida_una_ficha_incompleta(cliente, entrar_como):
    await entrar_como("experto")
    ficha = (await cliente.post(URL, json={**FICHA, "sintomas": []})).json()
    r = await cliente.patch(f"{URL}/{ficha['id']}/estado", json={"estado": "validado"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "FICHA_INCOMPLETA"


async def test_un_manejo_quimico_sin_producto_no_se_guarda(cliente, entrar_como):
    await entrar_como("experto")
    manejo = {"tipo": "quimico", "descripcion": "Aplicar fungicida"}
    assert (await cliente.post(URL, json={**FICHA, "manejos": [manejo]})).status_code == 422
