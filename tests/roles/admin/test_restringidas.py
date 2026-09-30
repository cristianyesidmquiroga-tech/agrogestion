from tests.conftest import payload_siembra


async def test_ser_admin_no_abre_las_fincas_de_otros(sesion, f):
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    siembra = await f.siembra(finca, lote, cultivo)
    assert (await sesion.get(f"/api/v1/siembras/{siembra.id}")).status_code == 404
    assert (await sesion.get("/api/v1/siembras")).json()["total"] == 0
    r = await sesion.post("/api/v1/siembras", json=payload_siembra(finca.id, lote.id, cultivo.id))
    assert r.status_code == 404


async def test_ser_admin_no_lee_las_consultas_de_otros(sesion, f):
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    siembra = await f.siembra(finca, lote, cultivo)
    r = await sesion.post(
        "/api/v1/consultas", json={"siembra_id": str(siembra.id), "texto": "Las hojas se ven mal"}
    )
    assert r.status_code == 404
