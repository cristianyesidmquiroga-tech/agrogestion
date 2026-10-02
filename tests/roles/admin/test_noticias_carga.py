async def test_carga_noticias(sesion):
    cuerpo = {
        "titulo": "Alerta",
        "resumen": "Resumen corto",
        "enlace": "https://ejemplo.test/n",
        "fuente": "Fuente",
    }
    assert (await sesion.post("/noticias", json=cuerpo)).status_code == 201
    assert (await sesion.get("/noticias")).json()["total"] == 1
