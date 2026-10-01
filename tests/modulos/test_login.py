from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import claves
from app.models import IntentoAcceso
from app.services import autenticacion_service
from tests.conftest import CLAVE_PRUEBA, Fabrica

URL = "/api/v1/auth/login"


def formulario(correo, clave=CLAVE_PRUEBA):
    return {"username": correo, "password": clave}


async def test_el_login_devuelve_un_token_que_sirve(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario("agricultor")
    r = await cliente.post(URL, data=formulario(u.correo))
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"access_token", "token_type", "expires_in", "rol", "nombre"}
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["rol"] == "agricultor"
    assert cuerpo["expires_in"] == 3600
    me = await cliente.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {cuerpo['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["correo"] == u.correo
    assert me.json()["rol"] == "agricultor"


@pytest.mark.parametrize("rol", ["admin", "agricultor", "contador", "experto"])
async def test_cada_perfil_recibe_su_rol(cliente: AsyncClient, f: Fabrica, rol: str) -> None:
    u = await f.usuario(rol)
    r = await cliente.post(URL, data=formulario(u.correo))
    assert r.json()["rol"] == rol


async def test_me_trae_las_fincas_del_usuario(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    token = (await cliente.post(URL, data=formulario(u.correo))).json()["access_token"]
    me = await cliente.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["fincas"] == [str(finca.id)]


async def test_clave_incorrecta_y_usuario_inexistente_responden_igual(
    cliente: AsyncClient, f: Fabrica
) -> None:
    u = await f.usuario()
    mala = await cliente.post(URL, data=formulario(u.correo, "otra-clave"))
    fantasma = await cliente.post(URL, data=formulario("nadie@prueba.test"))
    assert mala.status_code == fantasma.status_code == 401
    assert mala.json() == fantasma.json()
    assert mala.json()["error"] == "CREDENCIALES_INVALIDAS"
    assert mala.headers["www-authenticate"] == "Bearer"


async def test_el_correo_no_distingue_mayusculas_ni_espacios(
    cliente: AsyncClient, f: Fabrica
) -> None:
    u = await f.usuario()
    r = await cliente.post(URL, data=formulario("  " + u.correo.upper() + " "))
    assert r.status_code == 200


async def test_un_usuario_inactivo_no_entra(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    u = await f.usuario()
    u.activo = False
    await sesion.commit()
    r = await cliente.post(URL, data=formulario(u.correo))
    assert r.json()["error"] == "CREDENCIALES_INVALIDAS"


async def test_el_login_recibe_formulario_no_json(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.post(URL, json=formulario(u.correo))
    assert r.status_code == 422
    assert r.json()["error"] == "DATOS_INVALIDOS"


async def test_una_clave_demasiado_larga_no_rompe_nada(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.post(URL, data=formulario(u.correo, "x" * 200))
    assert r.status_code == 401


async def test_bloquea_tras_varios_intentos_fallidos(
    cliente: AsyncClient, f: Fabrica, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(autenticacion_service.settings, "intentos_maximos", 3)
    u, otro = await f.usuario(), await f.usuario()
    for _ in range(3):
        assert (await cliente.post(URL, data=formulario(u.correo, "mala"))).status_code == 401
    bloqueado = await cliente.post(URL, data=formulario(u.correo))
    assert bloqueado.status_code == 429
    assert bloqueado.json()["error"] == "DEMASIADOS_INTENTOS"
    assert (await cliente.post(URL, data=formulario(otro.correo))).status_code == 200


async def test_los_fallos_viejos_ya_no_cuentan(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(autenticacion_service.settings, "intentos_maximos", 2)
    u = await f.usuario()
    viejo = datetime.now(UTC) - timedelta(hours=2)
    for _ in range(5):
        sesion.add(IntentoAcceso(correo=u.correo, exitoso=False, creado_en=viejo))
    await sesion.commit()
    assert (await cliente.post(URL, data=formulario(u.correo))).status_code == 200


async def test_registra_los_intentos_y_el_ultimo_acceso(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    u = await f.usuario()
    await cliente.post(URL, data=formulario(u.correo, "mala"))
    await cliente.post(URL, data=formulario(u.correo))
    intentos = list(
        await sesion.scalars(select(IntentoAcceso).where(IntentoAcceso.correo == u.correo))
    )
    assert sorted(i.exitoso for i in intentos) == [False, True]
    await sesion.refresh(u)
    assert u.ultimo_acceso is not None


def test_las_claves_se_guardan_con_bcrypt_y_no_se_repiten() -> None:
    uno, dos = claves.hashear("Una-clave-1"), claves.hashear("Una-clave-1")
    assert uno != dos
    assert uno.startswith("$2")
    assert claves.verificar("Una-clave-1", uno)
    assert not claves.verificar("una-clave-1", uno)
    assert not claves.verificar("x" * 100, uno)
    assert not claves.verificar("Una-clave-1", "no-es-un-hash")
    with pytest.raises(ValueError):
        claves.hashear("x" * 73)


async def test_solo_el_login_y_lo_publico_estan_sin_candado(cliente: AsyncClient) -> None:
    contrato = (await cliente.get("/openapi.json")).json()
    sin_candado = set()
    for ruta, metodos in contrato["paths"].items():
        for metodo, operacion in metodos.items():
            if ruta.startswith("/api/v1") and not operacion.get("security"):
                sin_candado.add(f"{metodo.upper()} {ruta}")
    assert sin_candado == {"POST /api/v1/auth/login", "GET /api/v1/politica"}


async def test_la_documentacion_empieza_por_el_acceso(cliente: AsyncClient) -> None:
    contrato = (await cliente.get("/openapi.json")).json()
    nombres = [t["name"] for t in contrato["tags"]]
    assert nombres[0] == "1. Acceso"
    assert nombres == sorted(nombres, key=lambda n: int(n.split(".")[0]))
    usados = {t for m in contrato["paths"].values() for o in m.values() for t in o["tags"]}
    assert usados <= set(nombres)
    primero = next(iter(contrato["paths"]))
    assert primero.startswith("/api/v1/auth")
