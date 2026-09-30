import pytest

from tests.conftest import payload_siembra

NO_ENTRA = [
    pytest.param("post", "/api/v1/riesgos", id="agregar_riesgos"),
    pytest.param("post", "/api/v1/noticias", id="cargar_noticias"),
    pytest.param("get", "/api/v1/asistente/calidad", id="calidad_asistente"),
    pytest.param("post", "/api/v1/conocimiento", id="crear_ficha"),
    pytest.param(
        "patch",
        "/api/v1/conocimiento/00000000-0000-0000-0000-000000000000/estado",
        id="validar_ficha",
    ),
    pytest.param("get", "/api/v1/fuentes", id="fuentes"),
    pytest.param("post", "/api/v1/fuentes", id="agregar_fuente"),
]


@pytest.mark.parametrize(("metodo", "url"), NO_ENTRA)
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


async def test_no_ve_las_consultas_de_otros(sesion, f):
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    siembra = await f.siembra(finca, lote, cultivo)
    r = await sesion.post(
        "/api/v1/consultas", json={"siembra_id": str(siembra.id), "texto": "Las hojas se ven mal"}
    )
    assert r.status_code == 404
