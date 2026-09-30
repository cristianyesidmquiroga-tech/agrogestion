"""Vista 24: Visor de reporte."""

from datetime import date

URL = "/api/v1/reportes"
ENTRAN = {
    "indices": {"admin", "agricultor", "contador"},
    "cronograma": {"admin", "agricultor", "contador"},
    "eventos": {"admin", "agricultor"},
}


async def test_acceso_segun_el_rol_y_el_reporte(cliente, entrar_como, clave):
    await entrar_como(clave)
    for reporte, roles in ENTRAN.items():
        r = await cliente.get(f"{URL}/{reporte}")
        assert r.status_code == (200 if clave in roles else 403), (clave, reporte)


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(f"{URL}/indices")).status_code == 401


async def test_los_indices_traen_explicacion_y_fecha(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo, area="2", plantas=100)
    await cliente.post(
        f"/api/v1/siembras/{siembra.id}/conteos",
        json={"fecha": date.today().isoformat(), "vivas": 90},
    )
    indicadores = (await cliente.get(f"{URL}/indices")).json()["siembras"][0]["indicadores"]
    assert indicadores
    for i in indicadores:
        assert i["explicacion"] and i["fecha_datos"] and i["estado"]


async def test_filtra_por_finca_y_no_abre_las_de_otros(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca = await f.finca(yo)
    ajena = await f.finca(await f.usuario())
    assert (
        await cliente.get(f"{URL}/cronograma", params={"finca_id": str(finca.id)})
    ).status_code == 200
    r = await cliente.get(f"{URL}/eventos", params={"finca_id": str(ajena.id)})
    assert r.status_code == 404


async def test_el_reporte_de_eventos_acepta_un_periodo(cliente, entrar_como):
    await entrar_como("agricultor")
    r = await cliente.get(f"{URL}/eventos", params={"desde": "2026-01-01", "hasta": "2026-12-31"})
    assert r.json()["desde"] == "2026-01-01"
    assert r.json()["hasta"] == "2026-12-31"
    assert (await cliente.get(f"{URL}/eventos", params={"desde": "no-es-fecha"})).status_code == 422
