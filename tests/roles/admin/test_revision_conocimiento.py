FICHA = {
    "nombre": "Mancha de hoja",
    "tipo": "enfermedad",
    "sintomas": [{"descripcion": "Manchas amarillas"}],
    "manejos": [],
}


async def test_crea_valida_y_ve_todos_los_estados(sesion):
    fuente = (await sesion.post("/fuentes", json={"nombre": "Fuente A"})).json()
    manejo = {"tipo": "cultural", "descripcion": "Retirar hojas", "fuente_id": fuente["id"]}
    ficha = (await sesion.post("/conocimiento", json={**FICHA, "manejos": [manejo]})).json()
    assert (await sesion.get("/conocimiento", params={"estado": "borrador"})).json()["total"] == 1
    r = await sesion.patch(f"/conocimiento/{ficha['id']}/estado", json={"estado": "validado"})
    assert r.json()["estado"] == "validado"
