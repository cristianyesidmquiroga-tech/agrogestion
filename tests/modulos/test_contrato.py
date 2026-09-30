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
