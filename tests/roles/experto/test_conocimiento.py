async def test_la_biblioteca_le_muestra_todos_los_estados(sesion, f):
    await f.ficha("Ficha validada", estado="validado")
    await f.ficha("Ficha en borrador", estado="borrador")
    r = await sesion.get("/api/v1/conocimiento")
    assert r.status_code == 200
    assert r.json()["total"] == 2
