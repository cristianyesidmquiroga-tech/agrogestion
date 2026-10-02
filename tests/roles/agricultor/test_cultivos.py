from tests.conftest import payload_cultivo

URL = "/cultivos"


async def test_crea_y_consulta_cultivos(sesion):
    r = await sesion.post(URL, json=payload_cultivo())
    assert r.status_code == 201
    assert (await sesion.get(URL)).json()["total"] == 1


async def test_edita_el_perfil(sesion):
    creado = (await sesion.post(URL, json=payload_cultivo())).json()
    r = await sesion.put(f"{URL}/{creado['id']}", json=payload_cultivo(grupo="otro"))
    assert r.status_code == 200
    assert r.json()["grupo"] == "otro"


async def test_asigna_riesgos_al_cultivo(sesion, f):
    cultivo = await f.cultivo()
    riesgo = await f.riesgo()
    cuerpo = [{"riesgo_id": str(riesgo.id), "susceptibilidad": "alta"}]
    assert (await sesion.put(f"{URL}/{cultivo.id}/riesgos", json=cuerpo)).status_code == 200
