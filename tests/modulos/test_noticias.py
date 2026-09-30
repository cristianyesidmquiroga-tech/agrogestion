from datetime import UTC, datetime, timedelta

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Noticia
from app.services import noticia_service
from tests.conftest import Fabrica

URL = "/api/v1/noticias"


def noticia(**extra):
    base = {
        "titulo": "Alerta de lluvias",
        "resumen": "Se esperan lluvias fuertes esta semana.",
        "enlace": "https://ejemplo.test/noticia",
        "fuente": "Fuente de prueba",
    }
    base.update(extra)
    return base


async def test_toda_noticia_vence_a_los_siete_dias_por_defecto(
    cliente: AsyncClient, f: Fabrica
) -> None:
    h = f.cabecera(await f.usuario("admin"))
    r = await cliente.post(URL, json=noticia(), headers=h)
    assert r.status_code == 201
    publicada = datetime.fromisoformat(r.json()["publicada"])
    vence = datetime.fromisoformat(r.json()["vigente_hasta"])
    assert vence - publicada == timedelta(days=7)


async def test_no_puede_vencer_antes_de_publicarse(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario("admin"))
    ahora = datetime.now(UTC)
    cuerpo = noticia(
        publicada=ahora.isoformat(), vigente_hasta=(ahora - timedelta(days=1)).isoformat()
    )
    r = await cliente.post(URL, json=cuerpo, headers=h)
    assert r.json()["error"] == "NOTICIA_FECHAS_INVALIDAS"


async def test_validaciones_de_la_noticia(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario("admin"))
    assert (
        await cliente.post(URL, json=noticia(enlace="javascript:alert(1)"), headers=h)
    ).status_code == 422
    assert (await cliente.post(URL, json=noticia(region_dane="ABC"), headers=h)).status_code == 422
    assert (await cliente.post(URL, json=noticia(region_dane="123"), headers=h)).status_code == 422
    assert (await cliente.post(URL, json=noticia(region_dane="05"), headers=h)).status_code == 201
    assert (
        await cliente.post(URL, json=noticia(region_dane="05001"), headers=h)
    ).status_code == 201
    inexistente = noticia(cultivo_id="00000000-0000-0000-0000-000000000000")
    assert (await cliente.post(URL, json=inexistente, headers=h)).status_code == 404


async def test_las_vencidas_no_se_muestran(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    ahora = datetime.now(UTC)
    sesion.add_all(
        [
            Noticia(
                titulo="Vigente",
                resumen="r",
                enlace="https://x.test",
                fuente="F",
                publicada=ahora,
                vigente_hasta=ahora + timedelta(days=1),
            ),
            Noticia(
                titulo="Vencida",
                resumen="r",
                enlace="https://x.test",
                fuente="F",
                publicada=ahora - timedelta(days=9),
                vigente_hasta=ahora - timedelta(days=2),
            ),
        ]
    )
    await sesion.commit()
    h = f.cabecera(await f.usuario())
    assert [n["titulo"] for n in (await cliente.get(URL, headers=h)).json()["items"]] == ["Vigente"]


async def test_muestra_lo_de_mi_region_y_lo_nacional(cliente: AsyncClient, f: Fabrica) -> None:
    admin = f.cabecera(await f.usuario("admin"))
    usuario = await f.usuario()
    await f.finca(usuario)  # departamento 05, municipio 05001
    await cliente.post(URL, json=noticia(titulo="Nacional"), headers=admin)
    await cliente.post(URL, json=noticia(titulo="Mi departamento", region_dane="05"), headers=admin)
    await cliente.post(URL, json=noticia(titulo="Mi municipio", region_dane="05001"), headers=admin)
    await cliente.post(
        URL, json=noticia(titulo="Otro departamento", region_dane="76"), headers=admin
    )
    titulos = {
        n["titulo"] for n in (await cliente.get(URL, headers=f.cabecera(usuario))).json()["items"]
    }
    assert titulos == {"Nacional", "Mi departamento", "Mi municipio"}
    otra = await cliente.get(URL, params={"region": "76"}, headers=f.cabecera(usuario))
    assert {n["titulo"] for n in otra.json()["items"]} == {"Nacional", "Otro departamento"}


async def test_sin_fincas_solo_ve_lo_nacional(cliente: AsyncClient, f: Fabrica) -> None:
    admin = f.cabecera(await f.usuario("admin"))
    await cliente.post(URL, json=noticia(titulo="Nacional"), headers=admin)
    await cliente.post(URL, json=noticia(titulo="Regional", region_dane="05"), headers=admin)
    r = await cliente.get(URL, headers=f.cabecera(await f.usuario("experto")))
    assert [n["titulo"] for n in r.json()["items"]] == ["Nacional"]


async def test_filtra_por_cultivo(cliente: AsyncClient, f: Fabrica) -> None:
    admin = f.cabecera(await f.usuario("admin"))
    usuario = await f.usuario()
    finca, lote, cultivo = await f.escenario(usuario)
    await f.siembra(finca, lote, cultivo)
    otro = await f.cultivo("Otro cultivo")
    await cliente.post(URL, json=noticia(titulo="General"), headers=admin)
    await cliente.post(
        URL, json=noticia(titulo="De mi cultivo", cultivo_id=str(cultivo.id)), headers=admin
    )
    await cliente.post(
        URL, json=noticia(titulo="De otro cultivo", cultivo_id=str(otro.id)), headers=admin
    )
    titulos = {
        n["titulo"] for n in (await cliente.get(URL, headers=f.cabecera(usuario))).json()["items"]
    }
    assert titulos == {"General", "De mi cultivo"}


async def test_las_mas_recientes_van_primero(cliente: AsyncClient, f: Fabrica) -> None:
    admin = f.cabecera(await f.usuario("admin"))
    ahora = datetime.now(UTC)
    await cliente.post(
        URL,
        json=noticia(titulo="Vieja", publicada=(ahora - timedelta(days=3)).isoformat()),
        headers=admin,
    )
    await cliente.post(
        URL, json=noticia(titulo="Nueva", publicada=ahora.isoformat()), headers=admin
    )
    r = await cliente.get(URL, headers=admin)
    assert [n["titulo"] for n in r.json()["items"]] == ["Nueva", "Vieja"]


async def test_se_borran_las_vencidas(f: Fabrica, sesion: AsyncSession) -> None:
    ahora = datetime.now(UTC)
    sesion.add_all(
        [
            Noticia(
                titulo="Vigente",
                resumen="r",
                enlace="https://x.test",
                fuente="F",
                publicada=ahora,
                vigente_hasta=ahora + timedelta(days=1),
            ),
            Noticia(
                titulo="Vencida 1",
                resumen="r",
                enlace="https://x.test",
                fuente="F",
                publicada=ahora - timedelta(days=9),
                vigente_hasta=ahora - timedelta(days=2),
            ),
            Noticia(
                titulo="Vencida 2",
                resumen="r",
                enlace="https://x.test",
                fuente="F",
                publicada=ahora - timedelta(days=9),
                vigente_hasta=ahora - timedelta(hours=1),
            ),
        ]
    )
    await sesion.commit()
    assert await noticia_service.borrar_vencidas(sesion) == 2
    assert await noticia_service.borrar_vencidas(sesion) == 0
