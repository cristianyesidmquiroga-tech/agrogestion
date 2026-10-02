from tests.conftest import CLAVE_PRUEBA


async def test_inicia_sesion_y_ve_su_perfil(cliente, yo):
    r = await cliente.post("/auth/login", json={"email": yo.email, "password": CLAVE_PRUEBA})
    assert r.status_code == 200
    assert r.json()["rol"] == "experto"
    token = r.json()["access_token"]
    me = await cliente.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["rol"] == "experto"
    assert me.json()["id"] == str(yo.id)
