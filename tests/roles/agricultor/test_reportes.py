async def test_ve_los_reportes_con_datos(sesion, yo, f):
    catalogo = (await sesion.get("/api/v1/reportes")).json()
    assert {"indices", "cronograma", "eventos"} <= {r["id"] for r in catalogo}
    await f.siembra(*await f.escenario(yo))
    for reporte in ("indices", "cronograma", "eventos"):
        assert (await sesion.get(f"/api/v1/reportes/{reporte}")).status_code == 200


async def test_ve_sus_avisos(sesion):
    r = await sesion.get("/api/v1/avisos")
    assert r.status_code == 200
    assert r.json()["avisos"] == []
