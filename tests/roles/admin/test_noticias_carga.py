async def test_carga_noticias(sesion):
    cuerpo = {
        "titulo": "Alerta",
        "resumen": "Resumen corto",
        "enlace": "https://ejemplo.test/n",
        "fuente": "Fuente",
    }
    assert (await sesion.post("/api/v1/noticias", json=cuerpo)).status_code == 201
    assert (await sesion.get("/api/v1/noticias")).json()["total"] == 1
