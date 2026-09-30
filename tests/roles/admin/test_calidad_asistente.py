async def test_ve_la_calidad_del_asistente(sesion):
    r = await sesion.get("/api/v1/asistente/calidad")
    assert r.status_code == 200
    assert r.json()["consultas"] == 0
