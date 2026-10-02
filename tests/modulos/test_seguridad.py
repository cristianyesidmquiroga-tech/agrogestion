import jwt
from httpx import AsyncClient

from tests.conftest import Fabrica

RUTA = "/cultivos"


async def test_sin_token_responde_401_con_formato_unico(cliente: AsyncClient) -> None:
    r = await cliente.get(RUTA)
    assert r.status_code == 401
    cuerpo = r.json()
    assert set(cuerpo) == {"error"}
    assert set(cuerpo["error"]) == {"code", "message"}
    assert cuerpo["error"]["code"] == "NO_AUTENTICADO"


async def test_token_manipulado_es_rechazado(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    token = f.cabecera(u)["Authorization"].split()[1]
    falso = token[:-2] + ("aa" if not token.endswith("aa") else "bb")
    r = await cliente.get(RUTA, headers={"Authorization": f"Bearer {falso}"})
    assert r.status_code == 401


async def test_token_sin_firma_valida_es_rechazado(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    falso = jwt.encode(
        {"sub": str(u.id)}, "otra-clave-distinta-0123456789abcdef", algorithm="HS256"
    )
    r = await cliente.get(RUTA, headers={"Authorization": f"Bearer {falso}"})
    assert r.status_code == 401


async def test_usuario_inactivo_no_entra(cliente: AsyncClient, f: Fabrica, sesion) -> None:
    u = await f.usuario()
    u.activo = False
    await sesion.commit()
    r = await cliente.get(RUTA, headers=f.cabecera(u))
    assert r.status_code == 401
