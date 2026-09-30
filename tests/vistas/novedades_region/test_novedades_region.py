"""Vista 40: Novedades de mi región."""

from datetime import UTC, datetime, timedelta

from app.models import Noticia

URL = "/api/v1/noticias"


def nueva(f, titulo, region=None, dias=3):
    ahora = datetime.now(UTC)
    f.s.add(
        Noticia(
            titulo=titulo,
            resumen="Resumen",
            enlace="https://ejemplo.test/n",
            fuente="Fuente",
            region_dane=region,
            publicada=ahora,
            vigente_hasta=ahora + timedelta(days=dias),
        )
    )


async def test_todos_los_roles_entran(cliente, entrar_como, clave):
    await entrar_como(clave)
    assert (await cliente.get(URL)).status_code == 200


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_muestra_lo_de_mi_region(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    await f.finca(yo)
    nueva(f, "Nacional")
    nueva(f, "Mi municipio", "05001")
    nueva(f, "Otra region", "76")
    await f.s.commit()
    assert {n["titulo"] for n in (await cliente.get(URL)).json()["items"]} == {
        "Nacional",
        "Mi municipio",
    }


async def test_lo_vencido_desaparece(cliente, entrar_como, f):
    await entrar_como("agricultor")
    nueva(f, "Vigente", dias=1)
    nueva(f, "Vencida", dias=-1)
    await f.s.commit()
    assert [n["titulo"] for n in (await cliente.get(URL)).json()["items"]] == ["Vigente"]


async def test_trae_fuente_fecha_y_enlace(cliente, entrar_como, f):
    await entrar_como("agricultor")
    nueva(f, "Nacional")
    await f.s.commit()
    n = (await cliente.get(URL)).json()["items"][0]
    assert (
        n["fuente"] and n["enlace"].startswith("https://") and n["publicada"] and n["vigente_hasta"]
    )


async def test_la_region_debe_ser_un_codigo_dane(cliente, entrar_como):
    await entrar_como("agricultor")
    assert (await cliente.get(URL, params={"region": "abc"})).status_code == 422
    assert (await cliente.get(URL, params={"region": "05"})).status_code == 200


async def test_solo_el_admin_carga_noticias(cliente, entrar_como, clave):
    await entrar_como(clave)
    cuerpo = {
        "titulo": "Alerta",
        "resumen": "Resumen corto",
        "enlace": "https://ejemplo.test/n",
        "fuente": "Fuente",
    }
    r = await cliente.post(URL, json=cuerpo)
    assert r.status_code == (201 if clave == "admin" else 403)
