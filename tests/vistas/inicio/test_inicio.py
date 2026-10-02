"""Vista 4: Inicio."""

URL = "/inicio"


async def test_todos_los_roles_entran(cliente, entrar_como, clave):
    await entrar_como(clave)
    assert (await cliente.get(URL)).status_code == 200


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_trae_el_resumen_y_los_primeros_pasos(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    r = (await cliente.get(URL)).json()
    assert set(r) == {
        "fincas",
        "siembras_en_curso",
        "siembras_planeadas",
        "avisos",
        "eventos_recientes",
        "primeros_pasos",
    }
    assert r["primeros_pasos"]
    await f.siembra(*await f.escenario(yo))
    assert (await cliente.get(URL)).json()["siembras_planeadas"] == 1


async def test_los_avisos_salen_en_el_inicio(cliente, entrar_como, f):
    from datetime import date, timedelta

    yo = await entrar_como("agricultor")
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo, estado="en_curso")
    await f.s.refresh(siembra, attribute_names=["ciclos"])
    siembra.ciclos[0].fecha_inicio = date.today() - timedelta(days=12)
    await f.s.commit()
    await f.riesgo_de_cultivo(cultivo, await f.riesgo("Helada"), "siembra")
    avisos = (await cliente.get(URL)).json()["avisos"]
    assert [a["riesgo"] for a in avisos] == ["Helada"]
