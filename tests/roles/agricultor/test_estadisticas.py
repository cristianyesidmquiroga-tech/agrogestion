import pytest


@pytest.mark.parametrize("ruta", ["resumen", "crecimiento", "costos"])
async def test_estadisticas(sesion, ruta):
    assert (await sesion.get(f"/estadisticas/{ruta}")).status_code == 403
