async def test_agrega_riesgos_al_catalogo(sesion):
    r = await sesion.post(
        "/riesgos", json={"nombre": "Granizo", "tipo": "clima", "aplica_a": "cultivo"}
    )
    assert r.status_code == 201
    assert (await sesion.get("/riesgos")).json()[0]["nombre"] == "Granizo"
