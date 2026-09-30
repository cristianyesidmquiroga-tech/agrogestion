from datetime import date, timedelta

from httpx import AsyncClient

from app.models import EventoAdverso
from tests.conftest import Fabrica

URL = "/api/v1/reportes"


async def test_el_catalogo_depende_del_rol(cliente: AsyncClient, f: Fabrica) -> None:
    async def ids(rol):
        r = await cliente.get(URL, headers=f.cabecera(await f.usuario(rol)))
        return {x["id"]: x for x in r.json()}

    agricultor = await ids("agricultor")
    assert "utilidad" not in agricultor
    assert agricultor["indices"]["disponible"] is True
    assert agricultor["costos"]["disponible"] is False
    assert "módulo de dinero" in agricultor["costos"]["motivo"]
    contador = await ids("contador")
    assert "utilidad" in contador
    assert "eventos" not in contador
    assert await ids("experto") == {}


async def test_indices_de_mis_siembras(cliente: AsyncClient, f: Fabrica) -> None:
    usuario = await f.usuario()
    h = f.cabecera(usuario)
    finca, lote, cultivo = await f.escenario(usuario)
    siembra = await f.siembra(finca, lote, cultivo, area="2", plantas=100)
    sin_conteo = (await cliente.get(f"{URL}/indices", headers=h)).json()["siembras"][0]
    assert sin_conteo["indicadores"] == []
    assert "Cuente sus plantas" in sin_conteo["aviso"]
    await cliente.post(
        f"/api/v1/siembras/{siembra.id}/conteos",
        json={"fecha": date.today().isoformat(), "vivas": 90},
        headers=h,
    )
    r = (await cliente.get(f"{URL}/indices", headers=h)).json()["siembras"][0]
    assert r["cultivo"] == cultivo.nombre
    assert r["indicadores"][0]["valor"] == 45.0


async def test_indices_filtra_por_finca_y_protege_las_ajenas(
    cliente: AsyncClient, f: Fabrica
) -> None:
    usuario = await f.usuario()
    h = f.cabecera(usuario)
    finca, lote, cultivo = await f.escenario(usuario)
    await f.siembra(finca, lote, cultivo)
    assert (
        len(
            (
                await cliente.get(f"{URL}/indices", params={"finca_id": str(finca.id)}, headers=h)
            ).json()["siembras"]
        )
        == 1
    )
    ajena = await f.finca(await f.usuario())
    r = await cliente.get(f"{URL}/indices", params={"finca_id": str(ajena.id)}, headers=h)
    assert r.status_code == 404
    assert r.json()["error"] == "FINCA_NO_ENCONTRADA"


async def test_cronograma_de_mis_ciclos(cliente: AsyncClient, f: Fabrica) -> None:
    usuario = await f.usuario()
    finca, lote, cultivo = await f.escenario(usuario)
    siembra = await f.siembra(finca, lote, cultivo, estado="en_curso")
    await f.s.refresh(siembra, attribute_names=["ciclos"])
    siembra.ciclos[0].fecha_inicio = date.today() - timedelta(days=12)
    await f.s.commit()
    r = (await cliente.get(f"{URL}/cronograma", headers=f.cabecera(usuario))).json()["ciclos"][0]
    assert r["fase_actual"] == "siembra"
    assert r["fases_planeadas"] == 3
    assert (
        r["fecha_fin_planeada"]
        == (date.today() - timedelta(days=12) + timedelta(days=45)).isoformat()
    )


async def test_cronograma_de_un_ciclo_sin_iniciar(cliente: AsyncClient, f: Fabrica) -> None:
    usuario = await f.usuario()
    await f.siembra(*await f.escenario(usuario))
    r = (await cliente.get(f"{URL}/cronograma", headers=f.cabecera(usuario))).json()["ciclos"][0]
    assert r["fase_actual"] is None
    assert r["aviso"] == "El ciclo aún no inicia."


async def test_reporte_de_eventos(cliente: AsyncClient, f: Fabrica) -> None:
    usuario = await f.usuario()
    finca = await f.finca(usuario)
    helada, plaga = await f.riesgo("Helada"), await f.riesgo("Plaga de prueba", "plaga")
    hoy = date.today()
    for riesgo, severidad, pct, perdida in [
        (helada, "severa", 40, "1000000"),
        (helada, "leve", 10, "200000"),
        (plaga, "moderada", None, None),
    ]:
        f.s.add(
            EventoAdverso(
                finca_id=finca.id,
                riesgo_id=riesgo.id,
                inicio=hoy,
                severidad=severidad,
                perdida_pct=pct,
                perdida_estimada=perdida,
            )
        )
    f.s.add(
        EventoAdverso(
            finca_id=finca.id,
            riesgo_id=helada.id,
            inicio=hoy - timedelta(days=400),
            severidad="leve",
        )
    )
    await f.s.commit()
    h = f.cabecera(usuario)
    desde = (hoy - timedelta(days=30)).isoformat()
    r = (await cliente.get(f"{URL}/eventos", params={"desde": desde}, headers=h)).json()
    assert r["total"] == 3
    assert r["perdida_estimada_total"] == 1200000.0
    clima = next(t for t in r["por_tipo"] if t["tipo"] == "clima")
    assert clima["cantidad"] == 2
    assert clima["perdida_promedio_pct"] == 25.0
    assert r["por_severidad"] == {"severa": 1, "leve": 1, "moderada": 1}
    todos = (await cliente.get(f"{URL}/eventos", headers=h)).json()
    assert todos["total"] == 4


async def test_reporte_de_eventos_sin_datos(cliente: AsyncClient, f: Fabrica) -> None:
    r = (await cliente.get(f"{URL}/eventos", headers=f.cabecera(await f.usuario()))).json()
    assert r["total"] == 0
    assert r["aviso"] == "No hay eventos registrados en este periodo."
