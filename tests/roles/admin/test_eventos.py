from datetime import date

URL = "/api/v1/eventos-adversos"


async def test_registra_y_consulta_eventos(sesion, yo, f):
    finca = await f.finca(yo)
    riesgo = await f.riesgo()
    cuerpo = {
        "finca_id": str(finca.id),
        "riesgo_id": str(riesgo.id),
        "inicio": date.today().isoformat(),
        "severidad": "severa",
    }
    assert (await sesion.post(URL, json=cuerpo)).status_code == 201
    assert (await sesion.get(URL)).json()["total"] == 1
