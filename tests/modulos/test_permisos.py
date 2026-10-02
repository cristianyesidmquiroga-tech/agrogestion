from fastapi.routing import APIRoute
from httpx import AsyncClient

from tests.conftest import CLAVE_PRUEBA, Fabrica

ROLES = ("admin", "agricultor", "contador", "experto")


async def entrar(cliente: AsyncClient, f: Fabrica, rol: str):
    u = await f.usuario(rol)
    token = (
        await cliente.post("/auth/login", json={"email": u.email, "password": CLAVE_PRUEBA})
    ).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    me = (await cliente.get("/auth/me", headers=h)).json()
    return h, {(p["metodo"], p["ruta"]) for p in me["permisos"]}, me["permisos"]


async def test_cada_perfil_ve_solo_lo_que_puede_usar(cliente: AsyncClient, f: Fabrica) -> None:
    _, admin, _ = await entrar(cliente, f, "admin")
    _, agricultor, _ = await entrar(cliente, f, "agricultor")
    _, contador, _ = await entrar(cliente, f, "contador")
    _, experto, _ = await entrar(cliente, f, "experto")

    assert ("POST", "/riesgos") in admin
    assert ("POST", "/noticias") in admin
    assert ("GET", "/asistente/calidad") in admin

    assert ("POST", "/siembras") in agricultor
    assert ("POST", "/consultas") in agricultor
    assert ("POST", "/riesgos") not in agricultor
    assert ("GET", "/asistente/calidad") not in agricultor

    assert ("GET", "/siembras") in contador
    assert ("POST", "/siembras") not in contador
    assert ("GET", "/cultivos") not in contador
    assert ("GET", "/reportes/eventos") not in contador

    assert ("POST", "/conocimiento") in experto
    assert ("PATCH", "/conocimiento/{problema_id}/estado") in experto
    assert ("GET", "/siembras") not in experto
    assert ("POST", "/conocimiento") not in agricultor


async def test_lo_publico_y_lo_de_cualquier_sesion_aparece_en_todos(
    cliente: AsyncClient, f: Fabrica
) -> None:
    for rol in ROLES:
        _, permitidos, _ = await entrar(cliente, f, rol)
        assert ("POST", "/auth/login") in permitidos
        assert ("GET", "/politica") in permitidos
        assert ("GET", "/glosario") in permitidos
        assert ("GET", "/inicio") in permitidos


async def test_la_lista_va_en_el_orden_de_la_documentacion(
    cliente: AsyncClient, f: Fabrica
) -> None:
    _, _, lista = await entrar(cliente, f, "admin")
    grupos = []
    for p in lista:
        if p["grupo"] not in grupos:
            grupos.append(p["grupo"])
    assert grupos[0] == "1. Acceso"
    assert grupos == sorted(grupos, key=lambda g: int(g.split(".")[0]))
    assert all(p["resumen"] for p in lista)


async def test_la_lista_coincide_con_lo_que_la_api_realmente_permite(
    cliente: AsyncClient, f: Fabrica
) -> None:
    rutas = [
        r.path
        for r in cliente._transport.app.routes  # type: ignore[attr-defined]
        if isinstance(r, APIRoute)
        and r.include_in_schema
        and "GET" in r.methods
        and "{" not in r.path
        and r.path.startswith("")
    ]
    assert len(rutas) > 15
    for rol in ROLES:
        h, permitidos, _ = await entrar(cliente, f, rol)
        for ruta in rutas:
            estado = (await cliente.get(ruta, headers=h)).status_code
            if ("GET", ruta) in permitidos:
                assert estado != 403, (rol, ruta)
            else:
                assert estado == 403, (rol, ruta)
