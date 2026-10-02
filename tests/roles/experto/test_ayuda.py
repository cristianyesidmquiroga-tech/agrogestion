async def test_consulta_el_glosario(sesion):
    assert (await sesion.get("/glosario")).status_code == 200
