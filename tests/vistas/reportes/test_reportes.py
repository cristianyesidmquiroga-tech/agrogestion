"""Vista 23: Reportes (índice)."""

URL = "/reportes"


async def test_todos_los_roles_entran(cliente, entrar_como, clave):
    await entrar_como(clave)
    assert (await cliente.get(URL)).status_code == 200


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_cada_reporte_dice_si_esta_disponible_y_por_que_no(cliente, entrar_como):
    await entrar_como("admin")
    reportes = {r["id"]: r for r in (await cliente.get(URL)).json()}
    assert set(reportes) >= {
        "indices",
        "cronograma",
        "eventos",
        "costos",
        "utilidad",
        "flujo-caja",
        "mano-obra",
        "procesos",
    }
    assert reportes["indices"]["disponible"] and reportes["indices"]["motivo"] is None
    assert not reportes["costos"]["disponible"] and reportes["costos"]["motivo"]


async def test_el_agricultor_no_ve_la_utilidad(cliente, entrar_como):
    await entrar_como("agricultor")
    assert "utilidad" not in {r["id"] for r in (await cliente.get(URL)).json()}


async def test_el_experto_no_ve_reportes(cliente, entrar_como):
    await entrar_como("experto")
    assert (await cliente.get(URL)).json() == []
