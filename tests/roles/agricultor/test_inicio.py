async def test_abre_el_inicio(sesion):
    assert (await sesion.get("/inicio")).status_code == 200
