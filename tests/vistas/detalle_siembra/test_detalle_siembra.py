"""Vista 9: Detalle de siembra (resumen, ciclos, plantas y tiempos)."""

from datetime import date

URL = "/api/v1/siembras"
ENTRAN = {"admin", "agricultor", "contador"}


async def test_acceso_segun_el_rol(cliente, entrar_como, f, clave):
    yo = await entrar_como(clave)
    siembra = await f.siembra(*await f.escenario(yo))
    r = await cliente.get(f"{URL}/{siembra.id}")
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente, f):
    yo = await f.usuario()
    siembra = await f.siembra(*await f.escenario(yo))
    assert (await cliente.get(f"{URL}/{siembra.id}")).status_code == 401


async def test_la_siembra_de_otro_no_se_abre(cliente, entrar_como, f):
    await entrar_como("agricultor")
    otro = await f.usuario()
    siembra = await f.siembra(*await f.escenario(otro))
    r = await cliente.get(f"{URL}/{siembra.id}")
    assert r.status_code == 404
    assert r.json()["error"] == "SIEMBRA_NO_ENCONTRADA"


async def test_pestana_ciclos(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo))
    ciclos = (await cliente.get(f"{URL}/{siembra.id}/ciclos")).json()
    assert [c["tipo"] for c in ciclos] == ["levante"]


async def test_pestana_plantas_solo_aplica_si_se_cuenta_por_planta(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    finca, lote, por_area = await f.escenario(yo, nombre="Por area", unidad_conteo="area")
    siembra = await f.siembra(finca, lote, por_area, plantas=None)
    r = await cliente.get(f"{URL}/{siembra.id}/indices")
    assert r.json()["indicadores"] == []
    assert "por área" in r.json()["aviso"]
    conteo = {"fecha": date.today().isoformat(), "vivas": 1}
    assert (await cliente.post(f"{URL}/{siembra.id}/conteos", json=conteo)).status_code == 422


async def test_cada_indice_trae_su_explicacion_y_su_fecha(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo), area="2", plantas=100)
    conteo = {"fecha": date.today().isoformat(), "vivas": 90, "muertas": 10}
    await cliente.post(f"{URL}/{siembra.id}/conteos", json=conteo)
    for indicador in (await cliente.get(f"{URL}/{siembra.id}/indices")).json()["indicadores"]:
        assert indicador["explicacion"]
        assert indicador["fecha_datos"] == date.today().isoformat()
        assert indicador["estado"] in {"bien", "atencion", "alerta", "informativo"}


async def test_pestana_tiempos(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra = await f.siembra(*await f.escenario(yo), estado="en_curso")
    ciclo = (await cliente.get(f"{URL}/{siembra.id}/ciclos")).json()[0]["id"]
    r = await cliente.get(f"/api/v1/ciclos/{ciclo}/cronograma")
    assert [x["fase"] for x in r.json()["fases"]] == ["preparacion", "siembra", "mantenimiento"]


async def test_renovar_no_aplica_a_un_cultivo_transitorio(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    escenario = await f.escenario(
        yo, nombre="Transitorio", tipo_ciclo="transitorio", tipo_renovacion=None
    )
    siembra = await f.siembra(*escenario, estado="en_curso")
    r = await cliente.post(f"{URL}/{siembra.id}/renovar")
    assert r.status_code == 422
    assert r.json()["error"] == "CICLO_TIPO_NO_VALIDO"
