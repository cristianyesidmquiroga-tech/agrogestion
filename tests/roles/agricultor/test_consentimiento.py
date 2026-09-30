async def test_acepta_el_tratamiento_de_datos(sesion):
    version = (await sesion.get("/api/v1/politica")).json()["version"]
    r = await sesion.post(
        "/api/v1/cuenta/consentimiento",
        json={"version_politica": version, "acepta_tratamiento": True},
    )
    assert r.status_code == 201
