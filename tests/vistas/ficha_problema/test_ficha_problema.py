"""Vista 32: Ficha de problema."""

URL = "/conocimiento"


async def test_todos_los_roles_ven_una_ficha_validada(cliente, entrar_como, f, clave):
    ficha = await f.ficha()
    await entrar_como(clave)
    assert (await cliente.get(f"{URL}/{ficha.id}")).status_code == 200


async def test_sin_sesion_pide_iniciar_sesion(cliente, f):
    ficha = await f.ficha()
    assert (await cliente.get(f"{URL}/{ficha.id}")).status_code == 401


async def test_muestra_sintomas_manejo_fuente_y_aviso(cliente, entrar_como, f):
    ficha = await f.ficha(quimico=("Aplicar según la etiqueta", "Producto Registrado X"))
    await entrar_como("agricultor")
    r = (await cliente.get(f"{URL}/{ficha.id}")).json()
    assert r["sintomas"][0]["descripcion"]
    tipos = {m["tipo"] for m in r["manejos"]}
    assert tipos == {"cultural", "quimico"}
    assert all(m["fuente"]["nombre"] for m in r["manejos"])
    assert r["manejos"][1]["producto_ica"] == "Producto Registrado X"
    assert "no reemplaza a un técnico" in r["aviso"]
    assert r["validaciones"] == []


async def test_una_ficha_que_no_esta_validada_no_se_abre(cliente, entrar_como, f):
    borrador = await f.ficha(estado="borrador")
    await entrar_como("agricultor")
    r = await cliente.get(f"{URL}/{borrador.id}")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "PROBLEMA_NO_ENCONTRADO"


async def test_el_experto_si_ve_el_borrador_y_su_historial(cliente, entrar_como, f):
    borrador = await f.ficha(estado="borrador")
    await entrar_como("experto")
    r = await cliente.get(f"{URL}/{borrador.id}")
    assert r.status_code == 200
    assert r.json()["estado"] == "borrador"
