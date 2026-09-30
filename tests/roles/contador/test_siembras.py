from datetime import date

URL = "/api/v1/siembras"


async def test_lee_las_siembras_de_su_finca(sesion, yo, f):
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo, estado="en_curso")
    assert (await sesion.get(URL)).json()["total"] == 1
    assert (await sesion.get(f"{URL}/{siembra.id}")).status_code == 200
    ciclo = (await sesion.get(f"{URL}/{siembra.id}/ciclos")).json()[0]["id"]
    assert (await sesion.get(f"/api/v1/ciclos/{ciclo}")).status_code == 200
    assert (await sesion.get(f"/api/v1/ciclos/{ciclo}/cronograma")).status_code == 200
    assert (await sesion.get(f"{URL}/{siembra.id}/indices")).status_code == 200


async def test_no_modifica_siembras(sesion, yo, f):
    finca, lote, cultivo = await f.escenario(yo)
    siembra = await f.siembra(finca, lote, cultivo)
    ciclo = (await sesion.get(f"{URL}/{siembra.id}/ciclos")).json()[0]["id"]
    intentos = [
        ("post", f"{URL}/{siembra.id}/iniciar", None),
        ("post", f"{URL}/{siembra.id}/cancelar", None),
        ("post", f"{URL}/{siembra.id}/renovar", None),
        ("post", f"{URL}/{siembra.id}/conteos", {"fecha": date.today().isoformat(), "vivas": 1}),
        ("post", f"/api/v1/ciclos/{ciclo}/cerrar", None),
    ]
    for metodo, url, cuerpo in intentos:
        r = await sesion.request(metodo, url, json=cuerpo)
        assert r.status_code == 403, url
