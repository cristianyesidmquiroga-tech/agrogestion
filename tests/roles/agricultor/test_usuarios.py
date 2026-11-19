async def test_perfiles_de_usuarios(sesion, f):
    otro = await f.usuario("agricultor")
    assert (await sesion.get("/usuarios")).status_code == 403
    assert (await sesion.get(f"/usuarios/{otro.id}")).status_code == 403
