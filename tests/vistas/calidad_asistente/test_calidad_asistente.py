"""Vista 42: Calidad del asistente."""

URL = "/api/v1/asistente/calidad"


async def test_solo_el_admin_entra(cliente, entrar_como, clave):
    await entrar_como(clave)
    r = await cliente.get(URL)
    assert r.status_code == (200 if clave == "admin" else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_sin_valoraciones_lo_dice(cliente, entrar_como):
    await entrar_como("admin")
    r = (await cliente.get(URL)).json()
    assert r["porcentaje_que_sirvio"] is None
    assert r["aviso"]


async def test_mide_lo_que_sirvio(cliente, entrar_como, f):
    agricultor = await f.usuario("agricultor")
    siembra = await f.siembra(*await f.escenario(agricultor))
    from app.core.security import crear_token

    h = {"Authorization": f"Bearer {crear_token(agricultor.id)}"}
    ids = []
    for n in range(4):
        r = await cliente.post(
            "/api/v1/consultas",
            json={"siembra_id": str(siembra.id), "texto": f"Consulta {n} sobre las hojas"},
            headers=h,
        )
        ids.append(r.json()["id"])
    for consulta, valor in zip(ids, ["sirvio", "sirvio", "no_sirvio", "equivocado"], strict=True):
        await cliente.post(
            f"/api/v1/consultas/{consulta}/retroalimentacion", json={"valor": valor}, headers=h
        )
    await entrar_como("admin")
    r = (await cliente.get(URL)).json()
    assert (
        r["consultas"],
        r["con_valoracion"],
        r["sirvieron"],
        r["no_sirvieron"],
        r["equivocadas"],
    ) == (4, 4, 2, 1, 1)
    assert r["porcentaje_que_sirvio"] == 50.0
