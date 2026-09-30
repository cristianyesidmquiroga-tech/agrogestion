async def test_lee_las_noticias_vigentes(sesion):
    r = await sesion.get("/api/v1/noticias")
    assert r.status_code == 200
    assert r.json()["items"] == []
