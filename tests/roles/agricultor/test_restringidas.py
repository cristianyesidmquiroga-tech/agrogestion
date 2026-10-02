import pytest

from tests.conftest import payload_siembra

NO_ENTRA = [
    pytest.param("post", "/riesgos", id="agregar_riesgos"),
    pytest.param("post", "/noticias", id="cargar_noticias"),
    pytest.param("get", "/asistente/calidad", id="calidad_asistente"),
    pytest.param("post", "/conocimiento", id="crear_ficha"),
    pytest.param(
        "patch",
        "/conocimiento/00000000-0000-0000-0000-000000000000/estado",
        id="validar_ficha",
    ),
    pytest.param("get", "/fuentes", id="fuentes"),
    pytest.param("post", "/fuentes", id="agregar_fuente"),
]


@pytest.mark.parametrize(("metodo", "url"), NO_ENTRA)
async def test_no_entra(sesion, metodo, url):
    r = await sesion.request(metodo, url, json={})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "PERMISO_DENEGADO"


async def test_no_ve_las_fincas_de_otros(sesion, f):
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    siembra = await f.siembra(finca, lote, cultivo)
    assert (await sesion.get(f"/siembras/{siembra.id}")).status_code == 404
    r = await sesion.post("/siembras", json=payload_siembra(finca.id, lote.id, cultivo.id))
    assert r.status_code == 404


async def test_no_ve_las_consultas_de_otros(sesion, f):
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    siembra = await f.siembra(finca, lote, cultivo)
    r = await sesion.post(
        "/consultas", json={"siembra_id": str(siembra.id), "texto": "Las hojas se ven mal"}
    )
    assert r.status_code == 404
