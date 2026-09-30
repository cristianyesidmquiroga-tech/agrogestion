async def test_agrega_riesgos_al_catalogo(sesion):
    r = await sesion.post(
        "/api/v1/riesgos", json={"nombre": "Granizo", "tipo": "clima", "aplica_a": "cultivo"}
    )
    assert r.status_code == 201
    assert (await sesion.get("/api/v1/riesgos")).json()[0]["nombre"] == "Granizo"
