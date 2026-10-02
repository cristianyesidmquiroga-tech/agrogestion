"""Vista 1: Iniciar sesión."""

from datetime import UTC, datetime, timedelta

from tests.conftest import CLAVE_PRUEBA

URL = "/auth/login"


async def test_todos_los_perfiles_pueden_entrar(cliente, f, clave):
    u = await f.usuario(clave)
    r = await cliente.post(URL, json={"email": u.email, "password": CLAVE_PRUEBA})
    assert r.status_code == 200
    assert r.json()["rol"] == clave


async def test_el_token_sirve_en_las_demas_vistas_segun_el_perfil(cliente, f, clave):
    u = await f.usuario(clave)
    token = (await cliente.post(URL, json={"email": u.email, "password": CLAVE_PRUEBA})).json()[
        "access_token"
    ]
    h = {"Authorization": f"Bearer {token}"}
    esperado = 200 if clave in {"admin", "agricultor"} else 403
    assert (await cliente.get("/cultivos", headers=h)).status_code == esperado
    assert (await cliente.get("/inicio", headers=h)).status_code == 200
    assert (await cliente.get("/glosario", headers=h)).status_code == 200


async def test_sin_token_las_demas_vistas_piden_iniciar_sesion(cliente):
    assert (await cliente.get("/inicio")).status_code == 401
    assert (await cliente.get("/auth/me")).status_code == 401


async def test_el_error_es_claro_y_no_dice_cual_dato_fallo(cliente, f):
    u = await f.usuario()
    r = await cliente.post(URL, json={"email": u.email, "password": "mala"})
    assert r.json()["error"]["message"] == "El correo o la contraseña no son válidos."
    assert r.status_code == 401


async def test_un_token_vencido_o_falso_no_sirve(cliente, f):
    import jwt

    from app.core.config import get_settings

    u = await f.usuario()
    pasado = datetime.now(UTC) - timedelta(minutes=5)
    vencido = jwt.encode(
        {"sub": str(u.id), "iat": pasado, "exp": pasado}, get_settings().jwt_secret, "HS256"
    )
    assert (
        await cliente.get("/auth/me", headers={"Authorization": f"Bearer {vencido}"})
    ).status_code == 401
    assert (
        await cliente.get("/auth/me", headers={"Authorization": "Bearer basura"})
    ).status_code == 401
