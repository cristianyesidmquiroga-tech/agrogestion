"""Vista 12: Vivero (propagación por semilla o esqueje)."""

from datetime import date

URL = "/api/v1/propagacion"
ENTRAN = {"admin", "agricultor"}


def nuevo(finca, cultivo, **extra):
    base = {
        "finca_id": str(finca.id),
        "cultivo_id": str(cultivo.id),
        "metodo": "semilla",
        "fecha_inicio": date.today().isoformat(),
        "puestas": 100,
    }
    base.update(extra)
    return base


async def test_acceso_segun_el_rol(cliente, entrar_como, clave):
    await entrar_como(clave)
    r = await cliente.get(URL)
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_crea_y_actualiza_el_lote(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca = await f.finca(yo)
    cultivo = await f.cultivo()
    lote = (await cliente.post(URL, json=nuevo(finca, cultivo))).json()["id"]
    r = await cliente.patch(f"{URL}/{lote}", json={"germinadas": 70, "listas": 60, "perdidas": 10})
    assert r.json()["germinadas"] == 70


async def test_no_acepta_numeros_que_no_cuadran(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca = await f.finca(yo)
    cultivo = await f.cultivo()
    lote = (await cliente.post(URL, json=nuevo(finca, cultivo))).json()["id"]
    assert (await cliente.patch(f"{URL}/{lote}", json={"germinadas": 101})).status_code == 422
    assert (
        await cliente.patch(f"{URL}/{lote}", json={"germinadas": 10, "listas": 11})
    ).status_code == 422


async def test_metodo_que_el_cultivo_no_admite(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca = await f.finca(yo)
    cultivo = await f.cultivo(metodos=("semilla",))
    r = await cliente.post(URL, json=nuevo(finca, cultivo, metodo="injerto"))
    assert r.json()["error"] == "METODO_NO_VALIDO"


async def test_pasa_las_plantas_listas_a_una_siembra(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote_tierra, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote_tierra, cultivo, plantas=10)
    lote = (await cliente.post(URL, json=nuevo(finca, cultivo))).json()["id"]
    await cliente.patch(f"{URL}/{lote}", json={"germinadas": 80, "listas": 60})
    r = await cliente.post(
        f"{URL}/{lote}/trasplante", json={"siembra_id": str(siembra.id), "cantidad": 40}
    )
    assert r.json()["trasplantadas"] == 40
    leida = await cliente.get(f"/api/v1/siembras/{siembra.id}")
    assert leida.json()["plantas_sembradas"] == 50
    demasiado = await cliente.post(
        f"{URL}/{lote}/trasplante", json={"siembra_id": str(siembra.id), "cantidad": 21}
    )
    assert demasiado.json()["error"] == "TRASPLANTE_INVALIDO"


async def test_no_se_ven_los_viveros_de_otros(cliente, entrar_como, f):
    await entrar_como("agricultor")
    otro = await f.usuario()
    finca = await f.finca(otro)
    cultivo = await f.cultivo()
    r = await cliente.post(URL, json=nuevo(finca, cultivo))
    assert r.status_code == 404
    assert (await cliente.get(URL)).json()["total"] == 0
