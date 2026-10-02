from datetime import date, timedelta

from httpx import AsyncClient

from tests.conftest import Fabrica

URL = "/avisos"


async def siembra_con_riesgo(
    f: Fabrica, dias_desde_inicio: int, fase_critica="siembra", dias_en_perfil=True
):
    usuario = await f.usuario()
    finca, lote, cultivo = await f.escenario(usuario)
    if not dias_en_perfil:
        for fase in cultivo.fases:
            fase.dias_estimados = None
        await f.s.commit()
    siembra = await f.siembra(finca, lote, cultivo, estado="en_curso")
    await f.s.refresh(siembra, attribute_names=["ciclos"])
    siembra.ciclos[0].fecha_inicio = date.today() - timedelta(days=dias_desde_inicio)
    await f.s.commit()
    riesgo = await f.riesgo("Helada")
    await f.riesgo_de_cultivo(cultivo, riesgo, fase_critica)
    return usuario, cultivo


async def test_avisa_el_riesgo_de_la_fase_actual(cliente: AsyncClient, f: Fabrica) -> None:
    # preparación dura 10 días y siembra 5: a los 12 días va en siembra
    usuario, cultivo = await siembra_con_riesgo(f, dias_desde_inicio=12)
    r = await cliente.get(URL, headers=f.cabecera(usuario))
    assert r.status_code == 200
    aviso = r.json()["avisos"][0]
    assert aviso["fase"] == "siembra"
    assert aviso["riesgo"] == "Helada"
    assert aviso["susceptibilidad"] == "alta"
    assert aviso["por_validar"] is True
    assert cultivo.nombre in aviso["texto"]
    assert "siembra" in aviso["texto"]
    assert r.json()["siembras_sin_calendario"] == 0


async def test_no_avisa_un_riesgo_de_otra_fase(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, _ = await siembra_con_riesgo(f, dias_desde_inicio=2, fase_critica="siembra")
    r = await cliente.get(URL, headers=f.cabecera(usuario))
    assert r.json()["avisos"] == []


async def test_sin_duracion_de_fases_lo_dice_y_no_inventa(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, _ = await siembra_con_riesgo(f, dias_desde_inicio=12, dias_en_perfil=False)
    r = await cliente.get(URL, headers=f.cabecera(usuario))
    assert r.json()["avisos"] == []
    assert r.json()["siembras_sin_calendario"] == 1
    assert "Falta cargar la duración" in r.json()["aviso"]


async def test_solo_avisa_de_sus_siembras(cliente: AsyncClient, f: Fabrica) -> None:
    await siembra_con_riesgo(f, dias_desde_inicio=12)
    otro = await f.usuario()
    r = await cliente.get(URL, headers=f.cabecera(otro))
    assert r.json()["avisos"] == []


async def test_una_siembra_planeada_no_genera_avisos(cliente: AsyncClient, f: Fabrica) -> None:
    usuario = await f.usuario()
    finca, lote, cultivo = await f.escenario(usuario)
    await f.siembra(finca, lote, cultivo, estado="planeada")
    await f.riesgo_de_cultivo(cultivo, await f.riesgo(), "siembra")
    assert (await cliente.get(URL, headers=f.cabecera(usuario))).json()["avisos"] == []
