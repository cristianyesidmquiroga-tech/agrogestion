"""Vista: Perfiles de usuarios (solo administrador)."""

URL = "/usuarios"


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    usuario = await entrar_como(clave)
    esperado = 200 if clave == "admin" else 403
    assert (await cliente.get(URL)).status_code == esperado
    assert (await cliente.get(f"{URL}/{usuario.id}")).status_code == esperado


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_muestra_nombre_rol_y_estado(cliente, entrar_como, f):
    await entrar_como("admin")
    await f.usuario("contador")
    items = (await cliente.get(URL)).json()["items"]
    assert {"nombre", "email", "rol", "activo", "fincas", "siembras"} <= set(items[0])
    assert {u["rol"] for u in items} == {"admin", "contador"}
