async def test_consulta_el_glosario(sesion):
    assert (await sesion.get("/api/v1/glosario")).status_code == 200
