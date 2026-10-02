async def test_crea_fuentes_y_fichas_y_las_valida(sesion):
    fuente = (await sesion.post("/fuentes", json={"nombre": "Fuente A"})).json()
    manejo = {"tipo": "cultural", "descripcion": "Retirar hojas", "fuente_id": fuente["id"]}
    cuerpo = {
        "nombre": "Mancha",
        "tipo": "enfermedad",
        "sintomas": [{"descripcion": "Manchas amarillas"}],
        "manejos": [manejo],
    }
    ficha = (await sesion.post("/conocimiento", json=cuerpo)).json()
    r = await sesion.patch(
        f"/conocimiento/{ficha['id']}/estado",
        json={"estado": "validado", "observacion": "Revisada"},
    )
    assert r.json()["estado"] == "validado"
    assert len(r.json()["validaciones"]) == 1
    assert len((await sesion.get("/fuentes")).json()) == 1
    assert (await sesion.get("/reportes")).json() == []
