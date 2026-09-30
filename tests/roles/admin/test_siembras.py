from datetime import date

from tests.conftest import payload_siembra

URL = "/api/v1/siembras"


async def test_planea_inicia_y_cancela(sesion, yo, f):
    finca, lote, cultivo = await f.escenario(yo)
    creada = await sesion.post(URL, json=payload_siembra(finca.id, lote.id, cultivo.id))
    assert creada.status_code == 201
    siembra = creada.json()["id"]
    assert (await sesion.post(f"{URL}/{siembra}/iniciar")).json()["estado"] == "en_curso"
    assert (await sesion.post(f"{URL}/{siembra}/cancelar")).json()["estado"] == "cancelada"


async def test_cuenta_plantas_y_ve_los_indices(sesion, yo, f):
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo, area="2", plantas=100)
    conteo = {"fecha": date.today().isoformat(), "vivas": 90}
    assert (await sesion.post(f"{URL}/{siembra.id}/conteos", json=conteo)).status_code == 201
    indices = (await sesion.get(f"{URL}/{siembra.id}/indices")).json()
    assert indices["indicadores"][0]["valor"] == 45.0


async def test_cierra_un_ciclo_con_motivo(sesion, yo, f):
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo, estado="en_curso")
    ciclo = (await sesion.get(f"{URL}/{siembra.id}/ciclos")).json()[0]["id"]
    r = await sesion.post(
        f"/api/v1/ciclos/{ciclo}/cerrar", json={"motivo_perdida": "Pérdida total"}
    )
    assert r.status_code == 200
    assert r.json()["estado"] == "cerrado"
