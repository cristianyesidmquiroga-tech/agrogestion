async def test_consulta_la_biblioteca(sesion, f):
    await f.ficha("Ficha validada", estado="validado")
    await f.ficha("Ficha en borrador", estado="borrador")
    r = await sesion.get("/conocimiento")
    assert r.status_code == 200
    assert [i["nombre"] for i in r.json()["items"]] == ["Ficha validada"]
