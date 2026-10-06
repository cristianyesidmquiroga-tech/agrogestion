"""Smoke tests over the ASGI boundary used by the Flutter client."""

from httpx import AsyncClient


async def test_health_and_authenticated_startup(cliente: AsyncClient, f) -> None:
    health = await cliente.get("/health")
    assert health.status_code == 200

    usuario = await f.usuario("agricultor")
    cliente.headers.update(f.cabecera(usuario))

    me = await cliente.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["rol"] == "agricultor"

    inicio = await cliente.get("/inicio")
    assert inicio.status_code == 200
