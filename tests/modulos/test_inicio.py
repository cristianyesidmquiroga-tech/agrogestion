from datetime import date, timedelta

from httpx import AsyncClient

from app.models import EventoAdverso
from tests.conftest import Fabrica

URL = "/inicio"


async def test_sin_fincas_guia_los_primeros_pasos(cliente: AsyncClient, f: Fabrica) -> None:
    r = await cliente.get(URL, headers=f.cabecera(await f.usuario()))
    assert r.status_code == 200
    assert r.json()["fincas"] == 0
    assert r.json()["primeros_pasos"] == ["Pida que le asignen una finca para empezar."]


async def test_los_pasos_avanzan_con_los_datos(cliente: AsyncClient, f: Fabrica) -> None:
    usuario = await f.usuario()
    h = f.cabecera(usuario)
    finca = await f.finca(usuario)
    assert (await cliente.get(URL, headers=h)).json()["primeros_pasos"] == [
        "Registre los lotes de su finca."
    ]
    lote = await f.lote(finca)
    assert (await cliente.get(URL, headers=h)).json()["primeros_pasos"] == [
        "Planee su primera siembra."
    ]
    await f.siembra(finca, lote, await f.cultivo())
    assert (await cliente.get(URL, headers=h)).json()["primeros_pasos"] == []


async def test_cuenta_siembras_y_trae_los_eventos_recientes(
    cliente: AsyncClient, f: Fabrica
) -> None:
    usuario = await f.usuario()
    finca, lote, cultivo = await f.escenario(usuario, area_lote="10")
    await f.siembra(finca, lote, cultivo, estado="planeada")
    await f.siembra(finca, lote, cultivo, estado="en_curso")
    riesgo = await f.riesgo("Sequía")
    f.s.add(
        EventoAdverso(
            finca_id=finca.id, riesgo_id=riesgo.id, inicio=date.today(), severidad="severa"
        )
    )
    f.s.add(
        EventoAdverso(
            finca_id=finca.id,
            riesgo_id=riesgo.id,
            inicio=date.today() - timedelta(days=90),
            severidad="leve",
        )
    )
    await f.s.commit()
    r = (await cliente.get(URL, headers=f.cabecera(usuario))).json()
    assert r["fincas"] == 1
    assert r["siembras_planeadas"] == 1
    assert r["siembras_en_curso"] == 1
    assert [e["riesgo"] for e in r["eventos_recientes"]] == ["Sequía"]


async def test_no_mezcla_los_datos_de_otros(cliente: AsyncClient, f: Fabrica) -> None:
    dueno = await f.usuario()
    await f.siembra(*await f.escenario(dueno))
    r = (await cliente.get(URL, headers=f.cabecera(await f.usuario()))).json()
    assert r["siembras_planeadas"] == 0


async def test_el_experto_no_ve_pasos_de_finca(cliente: AsyncClient, f: Fabrica) -> None:
    r = await cliente.get(URL, headers=f.cabecera(await f.usuario("experto")))
    assert r.json()["primeros_pasos"] == []
