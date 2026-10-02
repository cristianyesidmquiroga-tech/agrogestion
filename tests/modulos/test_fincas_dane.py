from httpx import AsyncClient

from tests.conftest import Fabrica


async def test_la_finca_guarda_municipio_y_area(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.post(
        "/fincas",
        json={
            "nombre": "Finca uno",
            "departamento_dane": "05",
            "municipio_dane": "05001",
            "area_ha": 10,
        },
        headers=f.cabecera(u),
    )
    assert r.status_code == 201
    assert r.json()["municipio_dane"] == "05001"


async def test_municipio_de_otro_departamento_se_rechaza(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.post(
        "/fincas",
        json={"nombre": "Finca uno", "departamento_dane": "05", "municipio_dane": "08001"},
        headers=f.cabecera(u),
    )
    assert r.status_code == 422


async def test_departamento_sin_municipio_se_rechaza(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.post(
        "/fincas", json={"nombre": "Finca uno", "departamento_dane": "05"}, headers=f.cabecera(u)
    )
    assert r.status_code == 422
