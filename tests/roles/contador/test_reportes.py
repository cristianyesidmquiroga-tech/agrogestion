async def test_ve_indices_y_tiempos_pero_no_eventos(sesion, yo, f):
    catalogo = {r["id"]: r for r in (await sesion.get("/reportes")).json()}
    assert "utilidad" in catalogo
    assert "eventos" not in catalogo
    await f.siembra(*await f.escenario(yo))
    assert (await sesion.get("/reportes/indices")).status_code == 200
    assert (await sesion.get("/reportes/cronograma")).status_code == 200
    assert (await sesion.get("/avisos")).status_code == 200
