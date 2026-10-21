import pytest


@pytest.mark.parametrize(
    "ruta",
    [
        "resumen",
        "crecimiento",
        "costos",
        "cultivos",
        "zonas",
        "produccion",
        "siembras",
        "productores",
    ],
)
async def test_estadisticas(sesion, ruta):
    assert (await sesion.get(f"/estadisticas/{ruta}")).status_code == 403
