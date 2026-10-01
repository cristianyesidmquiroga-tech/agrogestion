"""Vista 1: Iniciar sesión."""

from tests.conftest import CLAVE_PRUEBA

URL = "/api/v1/auth/login"


async def test_todos_los_perfiles_pueden_entrar(cliente, f, clave):
    u = await f.usuario(clave)
    r = await cliente.post(URL, data={"username": u.correo, "password": CLAVE_PRUEBA})
    assert r.status_code == 200
    assert r.json()["rol"] == clave


async def test_el_token_sirve_en_las_demas_vistas_segun_el_perfil(cliente, f, clave):
    u = await f.usuario(clave)
    token = (await cliente.post(URL, data={"username": u.correo, "password": CLAVE_PRUEBA})).json()[
        "access_token"
    ]
    h = {"Authorization": f"Bearer {token}"}
    esperado = 200 if clave in {"admin", "agricultor"} else 403
    assert (await cliente.get("/api/v1/cultivos", headers=h)).status_code == esperado
    assert (await cliente.get("/api/v1/inicio", headers=h)).status_code == 200
    assert (await cliente.get("/api/v1/glosario", headers=h)).status_code == 200


async def test_sin_token_las_demas_vistas_piden_iniciar_sesion(cliente):
    assert (await cliente.get("/api/v1/inicio")).status_code == 401
    assert (await cliente.get("/api/v1/auth/me")).status_code == 401


async def test_el_error_es_claro_y_no_dice_cual_dato_fallo(cliente, f):
    u = await f.usuario()
    r = await cliente.post(URL, data={"username": u.correo, "password": "mala"})
    assert r.json()["message"] == "Correo o contraseña incorrectos."
    assert r.json()["status_code"] == 401


async def test_un_token_vencido_o_falso_no_sirve(cliente, f):
    from app.core.security import crear_token

    u = await f.usuario()
    vencido = crear_token(u.id, minutos=-5)
    assert (
        await cliente.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {vencido}"})
    ).status_code == 401
    assert (
        await cliente.get("/api/v1/auth/me", headers={"Authorization": "Bearer basura"})
    ).status_code == 401
