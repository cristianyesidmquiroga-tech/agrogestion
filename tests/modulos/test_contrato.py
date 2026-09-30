from httpx import AsyncClient

ORIGEN_PERMITIDO = "http://localhost:3000"


async def test_cors_deja_pasar_un_origen_permitido(cliente: AsyncClient) -> None:
    r = await cliente.options(
        "/api/v1/cultivos",
        headers={
            "Origin": ORIGEN_PERMITIDO,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == ORIGEN_PERMITIDO


async def test_cors_no_deja_pasar_otros_origenes(cliente: AsyncClient) -> None:
    r = await cliente.options(
        "/api/v1/cultivos",
        headers={
            "Origin": "https://sitio-malicioso.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in r.headers


async def test_la_paginacion_responde_como_pide_la_guia(cliente: AsyncClient, f) -> None:
    usuario = await f.usuario()
    for n in range(3):
        await f.cultivo(f"Cultivo {n}")
    r = await cliente.get(
        "/api/v1/cultivos", params={"skip": 2, "limit": 2}, headers=f.cabecera(usuario)
    )
    assert set(r.json()) == {"items", "total", "page", "size", "has_more"}
    assert r.json()["page"] == 2
    assert r.json()["size"] == 2
    assert r.json()["has_more"] is False


async def test_todo_endpoint_documenta_sus_errores_y_tiene_resumen(cliente: AsyncClient) -> None:
    contrato = (await cliente.get("/openapi.json")).json()
    for ruta, metodos in contrato["paths"].items():
        for metodo, operacion in metodos.items():
            assert operacion.get("summary"), f"{metodo} {ruta} sin resumen"
            if ruta.startswith("/api/v1"):
                assert {"401", "403", "404", "409", "422"} <= set(operacion["responses"]), ruta


# ---------------------------------------------------------------- entregables para Flutter
def _contrato():
    from scripts import exportar_contrato

    return exportar_contrato


def test_los_entregables_estan_actualizados() -> None:
    assert _contrato().desactualizados() == [], "Corra: python -m scripts.exportar_contrato"


def test_todo_codigo_de_error_esta_en_el_contrato_movil() -> None:
    c = _contrato()
    texto = (c.DOCS / "mobile_api_contract.md").read_text(encoding="utf-8")
    for codigo in c.codigos_de_error():
        assert f"`{codigo}`" in texto, codigo


def test_el_contrato_movil_lista_cada_endpoint_con_su_rol() -> None:
    c = _contrato()
    app = c.create_app()
    texto = (c.DOCS / "mobile_api_contract.md").read_text(encoding="utf-8")
    for path, metodo, _ruta in c._rutas(app):
        assert f"| `{metodo.upper()}` | `{path}` |" in texto, (metodo, path)
    assert "| `POST` | `/api/v1/riesgos` | admin |" in texto
    assert "| `GET` | `/api/v1/glosario` | cualquier usuario con sesión |" in texto
    assert "| `GET` | `/health` | público |" in texto
    assert "| `GET` | `/api/v1/siembras` | admin, agricultor, contador |" in texto


def test_hay_una_clase_dart_por_esquema() -> None:
    import json

    c = _contrato()
    contrato = json.loads((c.DOCS / "openapi.json").read_text(encoding="utf-8"))
    dart = (c.DOCS / "dart" / "lib" / "modelos.dart").read_text(encoding="utf-8")
    for nombre in contrato["components"]["schemas"]:
        assert f"class {nombre.replace('_', '')} {{" in dart, nombre
    assert "ErrorRespuesta" in dart


def test_postman_cubre_todo_y_no_trae_credenciales() -> None:
    import json

    c = _contrato()
    texto = (c.DOCS / "AgroGestion_Postman_Collection.json").read_text(encoding="utf-8")
    coleccion = json.loads(texto)
    pedidos = [p for carpeta in coleccion["item"] for p in carpeta["item"]]
    assert len(pedidos) == len(c._rutas(c.create_app()))
    assert {v["key"]: v["value"] for v in coleccion["variable"]}["token"] == ""
    assert "password" not in texto.lower()
    assert "secret" not in texto.lower()
    publico = next(p for p in pedidos if p["request"]["url"]["raw"].endswith("/politica"))
    assert publico["request"]["auth"] == {"type": "noauth"}
