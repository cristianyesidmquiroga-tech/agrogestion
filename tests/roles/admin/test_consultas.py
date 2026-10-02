async def test_consulta_al_asistente_y_ve_su_historial(sesion, yo, f):
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo)
    await f.ficha("Mancha amarilla", cultivo=cultivo)
    cuerpo = {"siembra_id": str(siembra.id), "texto": "Las hojas tienen manchas amarillas"}
    r = await sesion.post("/consultas", json=cuerpo)
    assert r.status_code == 201
    consulta = r.json()["id"]
    assert (await sesion.get("/consultas")).json()["total"] == 1
    assert (await sesion.get(f"/consultas/{consulta}")).status_code == 200
    valorada = await sesion.post(
        f"/consultas/{consulta}/retroalimentacion", json={"valor": "sirvio"}
    )
    assert valorada.status_code == 201
