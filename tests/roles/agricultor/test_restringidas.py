import pytest

from tests.conftest import payload_siembra

SOLO_ADMIN = [
    pytest.param("post", "/api/v1/riesgos", id="agregar_riesgos"),
]


@pytest.mark.parametrize(("metodo", "url"), SOLO_ADMIN)
async def test_no_entra(sesion, metodo, url):
    r = await sesion.request(metodo, url, json={})
    assert r.status_code == 403
    assert r.json()["error"] == "SIN_PERMISO"


async def test_no_ve_las_fincas_de_otros(sesion, f):
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    siembra = await f.siembra(finca, lote, cultivo)
    assert (await sesion.get(f"/api/v1/siembras/{siembra.id}")).status_code == 404
    r = await sesion.post("/api/v1/siembras", json=payload_siembra(finca.id, lote.id, cultivo.id))
    assert r.status_code == 404
