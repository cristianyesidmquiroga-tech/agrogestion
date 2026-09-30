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
    pytest.param("get", "/api/v1/siembras", id="mis_siembras"),
    pytest.param("post", "/api/v1/siembras", id="planear_siembra"),
    pytest.param("get", "/api/v1/avisos", id="avisos"),
    pytest.param("get", "/api/v1/reportes/indices", id="reporte_indices"),
    pytest.param("get", "/api/v1/reportes/cronograma", id="reporte_cronograma"),
]


@pytest.mark.parametrize(("metodo", "url"), VISTAS)
async def test_no_entra(sesion, metodo, url):
    r = await sesion.request(metodo, url, json={})
    assert r.status_code == 403
    assert r.json()["error"] == "SIN_PERMISO"
