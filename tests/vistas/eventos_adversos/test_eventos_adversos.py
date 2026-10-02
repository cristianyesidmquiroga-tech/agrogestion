"""Vista 25: Eventos adversos."""

from datetime import date

URL = "/eventos-adversos"
ENTRAN = {"admin", "agricultor"}


def evento(finca, riesgo, **extra):
    base = {
        "finca_id": str(finca.id),
        "riesgo_id": str(riesgo.id),
        "inicio": date.today().isoformat(),
        "severidad": "severa",
    }
    base.update(extra)
    return base


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    await entrar_como(clave)
    r = await cliente.get(URL)
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_registra_y_lista(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca = await f.finca(yo)
    riesgo = await f.riesgo()
    r = await cliente.post(
        URL, json=evento(finca, riesgo, perdida_pct=40, perdida_estimada="1200000")
    )
    assert r.status_code == 201
    assert (await cliente.get(URL)).json()["total"] == 1


async def test_filtra_por_tipo_de_riesgo(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca = await f.finca(yo)
    helada, plaga = await f.riesgo(), await f.riesgo("Plaga de prueba", "plaga")
    await cliente.post(URL, json=evento(finca, helada))
    await cliente.post(URL, json=evento(finca, plaga))
    assert (await cliente.get(URL, params={"tipo": "plaga"})).json()["total"] == 1


async def test_valida_lo_que_se_escribe(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca = await f.finca(yo)
    riesgo = await f.riesgo()
    assert (await cliente.post(URL, json=evento(finca, riesgo, perdida_pct=101))).status_code == 422
    assert (
        await cliente.post(URL, json=evento(finca, riesgo, fin="2000-01-01"))
    ).status_code == 422


async def test_no_registra_en_la_finca_de_otro(cliente, entrar_como, f):
    await entrar_como("agricultor")
    finca = await f.finca(await f.usuario())
    riesgo = await f.riesgo()
    assert (await cliente.post(URL, json=evento(finca, riesgo))).status_code == 404
