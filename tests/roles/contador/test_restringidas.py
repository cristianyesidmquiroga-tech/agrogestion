import pytest

VISTAS = [
    pytest.param("get", "/api/v1/cultivos", id="catalogo_cultivos"),
    pytest.param("get", "/api/v1/propagacion", id="vivero"),
    pytest.param("get", "/api/v1/eventos-adversos", id="eventos_adversos"),
    pytest.param("get", "/api/v1/riesgos", id="catalogo_riesgos"),
    pytest.param("post", "/api/v1/riesgos", id="agregar_riesgos"),
    pytest.param("post", "/api/v1/cultivos", id="crear_cultivo"),
    pytest.param("post", "/api/v1/propagacion", id="crear_vivero"),
    pytest.param("post", "/api/v1/eventos-adversos", id="registrar_evento"),
    pytest.param("get", "/api/v1/consultas", id="historial_consultas"),
    pytest.param("post", "/api/v1/consultas", id="consultar"),
    pytest.param("get", "/api/v1/reportes/eventos", id="reporte_eventos"),
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


@pytest.mark.parametrize(("metodo", "url"), VISTAS)
async def test_no_entra(sesion, metodo, url):
    r = await sesion.request(metodo, url, json={})
    assert r.status_code == 403
    assert r.json()["error"] == "SIN_PERMISO"
