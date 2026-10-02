from httpx import AsyncClient


async def test_la_documentacion_siempre_tiene_fondo_blanco(cliente: AsyncClient) -> None:
    r = await cliente.get("/docs")
    assert r.status_code == 200
    assert 'name="color-scheme" content="light"' in r.text
    assert "background:#fff" in r.text
    assert "dark" not in r.text.lower().replace("color-scheme:light only", "")


async def test_la_documentacion_no_aparece_en_el_contrato(cliente: AsyncClient) -> None:
    contrato = (await cliente.get("/openapi.json")).json()
    assert "/docs" not in contrato["paths"]


async def test_redoc_esta_apagado(cliente: AsyncClient) -> None:
    assert (await cliente.get("/redoc")).status_code == 404
