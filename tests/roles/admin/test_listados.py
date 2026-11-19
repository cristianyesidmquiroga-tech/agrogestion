import pytest

LISTADOS = ["jornales", "insumos", "procesos"]


@pytest.mark.parametrize("listado", LISTADOS)
async def test_ve_los_listados_de_su_finca(sesion, f, yo, listado):
    finca = await f.finca(yo)
    r = await sesion.get(f"/fincas/{finca.id}/{listado}")
    assert r.status_code == 200
    assert r.json() == []


async def test_ve_lo_que_puede_usar_en_su_perfil(sesion):
    perfil = (await sesion.get("/auth/me")).json()
    rutas = {p["ruta"] for p in perfil["permisos"]}
    assert "/fincas/{finca_id}/jornales" in rutas
    assert "/fincas/{finca_id}/insumos" in rutas
    assert "/fincas/{finca_id}/procesos" in rutas
