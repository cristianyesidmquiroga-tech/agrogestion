from datetime import date

URL = "/api/v1/propagacion"


async def test_lleva_un_lote_de_vivero(sesion, yo, f):
    finca = await f.finca(yo)
    cultivo = await f.cultivo()
    cuerpo = {
        "finca_id": str(finca.id),
        "cultivo_id": str(cultivo.id),
        "metodo": "semilla",
        "fecha_inicio": date.today().isoformat(),
        "puestas": 100,
    }
    lote = (await sesion.post(URL, json=cuerpo)).json()["id"]
    r = await sesion.patch(f"{URL}/{lote}", json={"germinadas": 80, "listas": 70})
    assert r.json()["listas"] == 70
