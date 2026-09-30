async def test_abre_el_inicio(sesion):
    assert (await sesion.get("/api/v1/inicio")).status_code == 200
