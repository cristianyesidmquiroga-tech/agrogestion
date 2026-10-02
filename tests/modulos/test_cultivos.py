from httpx import AsyncClient

from tests.conftest import Fabrica
from tests.conftest import payload_cultivo as perfil

URL = "/cultivos"


async def test_crear_y_leer_un_perfil_completo(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    r = await cliente.post(URL, json=perfil(), headers=h)
    assert r.status_code == 201
    cuerpo = r.json()
    assert [x["fase"] for x in cuerpo["fases"]] == ["preparacion", "siembra"]
    assert cuerpo["metodos"][0]["por_validar"] is True
    assert cuerpo["dosis"][0]["dosis"] == 0.25

    leido = await cliente.get(f"{URL}/{cuerpo['id']}", headers=h)
    assert leido.status_code == 200
    assert leido.json()["nombre"] == "Cultivo de prueba"
    fases = await cliente.get(f"{URL}/{cuerpo['id']}/fases", headers=h)
    assert len(fases.json()) == 2


async def test_nombre_duplicado_responde_409(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    await cliente.post(URL, json=perfil(), headers=h)
    r = await cliente.post(URL, json=perfil(nombre="CULTIVO DE PRUEBA"), headers=h)
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "CULTIVO_DUPLICADO"


async def test_transitorio_no_admite_renovacion(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    r = await cliente.post(URL, json=perfil(tipo_ciclo="transitorio"), headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "DATOS_INVALIDOS"
    assert r.json()["error"]["details"]


async def test_fase_repetida_se_rechaza(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    fases = [{"fase": "siembra", "orden": 1}, {"fase": "siembra", "orden": 2}]
    r = await cliente.post(URL, json=perfil(fases=fases), headers=h)
    assert r.status_code == 422


async def test_campos_extra_se_rechazan(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    r = await cliente.post(URL, json=perfil(rol="admin"), headers=h)
    assert r.status_code == 422


async def test_copiar_perfil_de_otro_cultivo(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    origen = (await cliente.post(URL, json=perfil(), headers=h)).json()
    copia = perfil(nombre="Copia", fases=[], metodos=[], dosis=[], copiar_de=origen["id"])
    r = await cliente.post(URL, json=copia, headers=h)
    assert r.status_code == 201
    assert len(r.json()["fases"]) == 2
    assert len(r.json()["metodos"]) == 2
    assert r.json()["dosis"][0]["por_validar"] is True


async def test_actualizar_reemplaza_el_perfil(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    creado = (await cliente.post(URL, json=perfil(), headers=h)).json()
    nuevo = perfil(
        fases=[{"fase": "siembra", "orden": 1, "dias_estimados": 7}], metodos=[], dosis=[]
    )
    r = await cliente.put(f"{URL}/{creado['id']}", json=nuevo, headers=h)
    assert r.status_code == 200
    assert [x["fase"] for x in r.json()["fases"]] == ["siembra"]
    assert r.json()["metodos"] == []


async def test_buscar_y_paginar(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    await f.cultivo("Maíz de prueba", tipo_ciclo="transitorio", tipo_renovacion=None)
    await f.cultivo("Café de prueba")
    await f.cultivo("Cacao de prueba")
    todos = await cliente.get(URL, params={"limit": 2}, headers=h)
    assert todos.json()["total"] == 3
    assert len(todos.json()["items"]) == 2
    assert todos.json()["has_more"] is True
    buscado = await cliente.get(URL, params={"q": "café"}, headers=h)
    assert [c["nombre"] for c in buscado.json()["items"]] == ["Café de prueba"]
    transitorios = await cliente.get(URL, params={"tipo_ciclo": "transitorio"}, headers=h)
    assert transitorios.json()["total"] == 1


async def test_limite_de_pagina_tiene_tope(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    r = await cliente.get(URL, params={"limit": 51}, headers=h)
    assert r.status_code == 422


async def test_cultivo_inexistente_responde_404(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario())
    r = await cliente.get(f"{URL}/00000000-0000-0000-0000-000000000000", headers=h)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "CULTIVO_NO_ENCONTRADO"
