"""Pagos pendientes (vista 17)."""

ENTRAN = {"admin", "agricultor", "contador"}


async def test_acceso_segun_el_rol(cliente, entrar_como, f, clave):
    yo = await entrar_como(clave)
    finca = await f.finca(yo)
    r = await cliente.get(f"/fincas/{finca.id}/jornales")
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente, f):
    yo = await f.usuario()
    finca = await f.finca(yo)
    assert (await cliente.get(f"/fincas/{finca.id}/jornales")).status_code == 401


async def test_la_finca_de_otro_no_se_abre(cliente, entrar_como, f):
    await entrar_como("agricultor")
    ajena = await f.finca(await f.usuario())
    r = await cliente.get(f"/fincas/{ajena.id}/jornales")
    assert r.status_code == 404
