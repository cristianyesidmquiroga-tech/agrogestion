from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from tests.conftest import CLAVE_PRUEBA, Fabrica

URL = "/auth/login"


def datos(email, clave=CLAVE_PRUEBA):
    return {"email": email, "password": clave}


async def test_el_login_devuelve_un_token_que_sirve(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario("agricultor")
    r = await cliente.post(URL, json=datos(u.email))
    assert r.status_code == 200
    cuerpo = r.json()
    assert set(cuerpo) == {"access_token", "token_type", "expires_in", "rol", "nombre"}
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["rol"] == "agricultor"
    assert cuerpo["expires_in"] == 3600
    me = await cliente.get(
        "/auth/me", headers={"Authorization": f"Bearer {cuerpo['access_token']}"}
    )
    assert me.status_code == 200
    assert me.json()["email"] == u.email
    assert me.json()["rol"] == "agricultor"


@pytest.mark.parametrize("rol", ["admin", "agricultor", "contador", "experto"])
async def test_cada_perfil_recibe_su_rol(cliente: AsyncClient, f: Fabrica, rol: str) -> None:
    u = await f.usuario(rol)
    r = await cliente.post(URL, json=datos(u.email))
    assert r.json()["rol"] == rol


async def test_me_trae_las_fincas_del_usuario(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    finca = await f.finca(u)
    token = (await cliente.post(URL, json=datos(u.email))).json()["access_token"]
    me = await cliente.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["fincas"] == [str(finca.id)]


async def test_clave_incorrecta_y_usuario_inexistente_responden_igual(
    cliente: AsyncClient, f: Fabrica
) -> None:
    u = await f.usuario()
    mala = await cliente.post(URL, json=datos(u.email, "otra-clave"))
    fantasma = await cliente.post(URL, json=datos("nadie@prueba.com"))
    assert mala.status_code == fantasma.status_code == 401
    assert mala.json() == fantasma.json()
    assert mala.json()["error"]["code"] == "CREDENCIALES_INVALIDAS"
    assert mala.headers["www-authenticate"] == "Bearer"


async def test_el_correo_no_distingue_mayusculas(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.post(URL, json=datos(u.email.upper()))
    assert r.status_code == 200


async def test_un_usuario_inactivo_no_entra(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    u = await f.usuario()
    u.activo = False
    await sesion.commit()
    r = await cliente.post(URL, json=datos(u.email))
    assert r.json()["error"]["code"] == "CREDENCIALES_INVALIDAS"


async def test_una_clave_demasiado_larga_no_rompe_nada(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.post(URL, json=datos(u.email, "x" * 200))
    assert r.status_code == 401


async def test_bloquea_tras_varios_intentos_fallidos(
    cliente: AsyncClient, f: Fabrica, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "login_max_attempts", 3)
    u, otro = await f.usuario(), await f.usuario()
    for _ in range(3):
        assert (await cliente.post(URL, json=datos(u.email, "mala"))).status_code == 401
    assert (await cliente.post(URL, json=datos(u.email))).status_code == 401
    assert (await cliente.post(URL, json=datos(otro.email))).status_code == 200


async def test_pasado_el_bloqueo_vuelve_a_entrar(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    u = await f.usuario()
    u.intentos_fallidos = 5
    u.bloqueado_hasta = datetime.now(UTC) - timedelta(minutes=1)
    await sesion.commit()
    assert (await cliente.post(URL, json=datos(u.email))).status_code == 200
    await sesion.refresh(u)
    assert u.intentos_fallidos == 0
    assert u.ultimo_acceso is not None


def test_las_claves_se_guardan_con_bcrypt_y_no_se_repiten() -> None:
    uno, dos = hash_password("Una-clave-1"), hash_password("Una-clave-1")
    assert uno != dos
    assert uno.startswith("$2")
    assert verify_password("Una-clave-1", uno)
    assert not verify_password("una-clave-1", uno)
    assert not verify_password("Una-clave-1", "no-es-un-hash")


async def test_solo_el_login_y_lo_publico_estan_sin_candado(cliente: AsyncClient) -> None:
    contrato = (await cliente.get("/openapi.json")).json()
    sin_candado = set()
    for ruta, metodos in contrato["paths"].items():
        for metodo, operacion in metodos.items():
            if not operacion.get("security"):
                sin_candado.add(f"{metodo.upper()} {ruta}")
    assert (
        sin_candado
        == {
            "POST /auth/login",
            "GET /politica",
            "GET /health",
            "GET /health/ready",
            "GET /alertas/fuentes",
        }
        or {"POST /auth/login", "GET /politica"} <= sin_candado
    )


async def test_la_documentacion_empieza_por_el_acceso(cliente: AsyncClient) -> None:
    contrato = (await cliente.get("/openapi.json")).json()
    nombres = [t["name"] for t in contrato["tags"]]
    assert nombres[0] == "1. Acceso"
    usados = {t for m in contrato["paths"].values() for o in m.values() for t in o["tags"]}
    assert usados <= set(nombres)
