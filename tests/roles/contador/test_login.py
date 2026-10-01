from tests.conftest import CLAVE_PRUEBA


async def test_inicia_sesion_y_ve_su_perfil(cliente, yo):
    r = await cliente.post(
        "/api/v1/auth/login", data={"username": yo.correo, "password": CLAVE_PRUEBA}
    )
    assert r.status_code == 200
    assert r.json()["rol"] == "contador"
    token = r.json()["access_token"]
    me = await cliente.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["rol"] == "contador"
    assert me.json()["id"] == str(yo.id)
