"""Vista: Panel de estadísticas (solo administrador)."""

RUTAS = [
    "resumen",
    "crecimiento",
    "costos",
    "cultivos",
    "zonas",
    "produccion",
    "siembras",
    "productores",
]


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    await entrar_como(clave)
    esperado = 200 if clave == "admin" else 403
    for ruta in RUTAS:
        assert (await cliente.get(f"/estadisticas/{ruta}")).status_code == esperado


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    for ruta in RUTAS:
        assert (await cliente.get(f"/estadisticas/{ruta}")).status_code == 401


async def test_el_panel_vacio_trae_ceros_y_no_falla(cliente, entrar_como):
    await entrar_como("admin")
    resumen = (await cliente.get("/estadisticas/resumen")).json()
    assert resumen["fincas"] == 0
    assert resumen["siembras"] == 0
    assert resumen["utilidad"] == 0


async def test_las_listas_vacias_no_fallan(cliente, entrar_como):
    await entrar_como("admin")
    for ruta in ("cultivos", "zonas"):
        assert (await cliente.get(f"/estadisticas/{ruta}")).json() == []


async def test_los_listados_paginados_vacios_traen_total_cero(cliente, entrar_como):
    await entrar_como("admin")
    for ruta in ("produccion", "siembras"):
        cuerpo = (await cliente.get(f"/estadisticas/{ruta}")).json()
        assert (cuerpo["items"], cuerpo["total"], cuerpo["has_more"]) == ([], 0, False)
    assert (await cliente.get("/estadisticas/productores")).json() == []
