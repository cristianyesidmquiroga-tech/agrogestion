"""Vista 14: Ficha del cultivo."""

from tests.conftest import payload_cultivo

URL = "/cultivos"
ENTRAN = {"admin", "agricultor"}


async def test_acceso_segun_el_rol(cliente, entrar_como, f, clave):
    await entrar_como(clave)
    cultivo = await f.cultivo()
    r = await cliente.get(f"{URL}/{cultivo.id}")
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente, f):
    cultivo = await f.cultivo()
    assert (await cliente.get(f"{URL}/{cultivo.id}")).status_code == 401


async def test_muestra_las_fases_en_orden(cliente, entrar_como, f):
    await entrar_como("agricultor")
    cultivo = await f.cultivo()
    fases = (await cliente.get(f"{URL}/{cultivo.id}/fases")).json()
    assert [x["orden"] for x in fases] == [1, 2, 3]


async def test_las_pestanas_responden(cliente, entrar_como, f):
    await entrar_como("agricultor")
    cultivo = await f.cultivo(dosis=(("abono", "0.25", "kg", "planta"),))
    for pestana in ("fases", "metodos", "dosis", "riesgos"):
        assert (await cliente.get(f"{URL}/{cultivo.id}/{pestana}")).status_code == 200


async def test_lo_que_no_esta_validado_se_marca(cliente, entrar_como):
    await entrar_como("agricultor")
    creado = (await cliente.post(URL, json=payload_cultivo())).json()
    assert creado["por_validar"] is True
    assert all(d["por_validar"] for d in creado["dosis"])


async def test_editar_reemplaza_el_perfil(cliente, entrar_como):
    await entrar_como("agricultor")
    creado = (await cliente.post(URL, json=payload_cultivo())).json()
    nuevo = payload_cultivo(fases=[{"fase": "siembra", "orden": 1}], metodos=[], dosis=[])
    r = await cliente.put(f"{URL}/{creado['id']}", json=nuevo)
    assert [x["fase"] for x in r.json()["fases"]] == ["siembra"]


async def test_cultivo_inexistente(cliente, entrar_como):
    await entrar_como("agricultor")
    r = await cliente.get(f"{URL}/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "CULTIVO_NO_ENCONTRADO"
