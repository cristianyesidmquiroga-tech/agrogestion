import pytest

VISTAS = [
    pytest.param("get", "/cultivos", id="catalogo_cultivos"),
    pytest.param("get", "/propagacion", id="vivero"),
    pytest.param("get", "/eventos-adversos", id="eventos_adversos"),
    pytest.param("get", "/riesgos", id="catalogo_riesgos"),
    pytest.param("post", "/riesgos", id="agregar_riesgos"),
    pytest.param("post", "/cultivos", id="crear_cultivo"),
    pytest.param("post", "/propagacion", id="crear_vivero"),
    pytest.param("post", "/eventos-adversos", id="registrar_evento"),
    pytest.param("get", "/consultas", id="historial_consultas"),
    pytest.param("post", "/consultas", id="consultar"),
    pytest.param("get", "/reportes/eventos", id="reporte_eventos"),
    pytest.param("post", "/noticias", id="cargar_noticias"),
    pytest.param("get", "/asistente/calidad", id="calidad_asistente"),
    pytest.param("get", "/siembras", id="mis_siembras"),
    pytest.param("post", "/siembras", id="planear_siembra"),
    pytest.param("get", "/avisos", id="avisos"),
    pytest.param("get", "/reportes/indices", id="reporte_indices"),
    pytest.param("get", "/reportes/cronograma", id="reporte_cronograma"),
    pytest.param(
        "get", "/fincas/00000000-0000-0000-0000-000000000000/jornales", id="pagos_pendientes"
    ),
    pytest.param("get", "/fincas/00000000-0000-0000-0000-000000000000/insumos", id="inventario"),
    pytest.param("get", "/fincas/00000000-0000-0000-0000-000000000000/procesos", id="procesos"),
]


@pytest.mark.parametrize(("metodo", "url"), VISTAS)
async def test_no_entra(sesion, metodo, url):
    r = await sesion.request(metodo, url, json={})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "PERMISO_DENEGADO"
