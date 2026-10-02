from httpx import AsyncClient

from tests.conftest import Fabrica

URL = "/conocimiento"


def ficha(**extra):
    base = {
        "nombre": "Mancha de hoja",
        "tipo": "enfermedad",
        "sintomas": [{"descripcion": "Manchas amarillas en las hojas"}],
        "manejos": [],
    }
    base.update(extra)
    return base


async def test_el_experto_crea_una_ficha_en_borrador(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario("experto"))
    r = await cliente.post(URL, json=ficha(), headers=h)
    assert r.status_code == 201
    assert r.json()["estado"] == "borrador"
    assert r.json()["aviso"]


async def test_un_manejo_quimico_exige_el_producto_registrado(
    cliente: AsyncClient, f: Fabrica
) -> None:
    h = f.cabecera(await f.usuario("experto"))
    manejo = {"tipo": "quimico", "descripcion": "Aplicar fungicida"}
    r = await cliente.post(URL, json=ficha(manejos=[manejo]), headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "DATOS_INVALIDOS"


async def test_fuente_inexistente_se_rechaza(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario("experto"))
    manejo = {
        "tipo": "cultural",
        "descripcion": "Retirar hojas",
        "fuente_id": "00000000-0000-0000-0000-000000000000",
    }
    r = await cliente.post(URL, json=ficha(manejos=[manejo]), headers=h)
    assert r.json()["error"]["code"] == "FUENTE_NO_ENCONTRADA"


async def test_validar_exige_sintoma_y_fuente_en_cada_manejo(
    cliente: AsyncClient, f: Fabrica
) -> None:
    h = f.cabecera(await f.usuario("experto"))
    sin_sintoma = (await cliente.post(URL, json=ficha(sintomas=[]), headers=h)).json()["id"]
    r = await cliente.patch(f"{URL}/{sin_sintoma}/estado", json={"estado": "validado"}, headers=h)
    assert r.json()["error"]["code"] == "FICHA_INCOMPLETA"

    manejo = {"tipo": "cultural", "descripcion": "Retirar hojas"}
    sin_fuente = (await cliente.post(URL, json=ficha(manejos=[manejo]), headers=h)).json()["id"]
    r = await cliente.patch(f"{URL}/{sin_fuente}/estado", json={"estado": "validado"}, headers=h)
    assert r.json()["error"]["code"] == "FICHA_SIN_FUENTE"


async def test_validar_deja_registro_de_quien_y_cuando(cliente: AsyncClient, f: Fabrica) -> None:
    experto = await f.usuario("experto")
    h = f.cabecera(experto)
    fuente = (await cliente.post("/fuentes", json={"nombre": "Fuente A"}, headers=h)).json()
    manejo = {"tipo": "cultural", "descripcion": "Retirar hojas", "fuente_id": fuente["id"]}
    creada = (await cliente.post(URL, json=ficha(manejos=[manejo]), headers=h)).json()
    r = await cliente.patch(
        f"{URL}/{creada['id']}/estado",
        json={"estado": "validado", "observacion": "Revisada"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["estado"] == "validado"
    assert r.json()["validaciones"][0]["experto_id"] == str(experto.id)
    assert r.json()["validaciones"][0]["observacion"] == "Revisada"


async def test_transiciones_de_estado(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario("experto"))
    p = await f.ficha(estado="validado")
    retirada = await cliente.patch(f"{URL}/{p.id}/estado", json={"estado": "retirado"}, headers=h)
    assert retirada.json()["estado"] == "retirado"
    invalida = await cliente.patch(f"{URL}/{p.id}/estado", json={"estado": "validado"}, headers=h)
    assert invalida.json()["error"]["code"] == "ESTADO_NO_PERMITIDO"
    reabierta = await cliente.patch(f"{URL}/{p.id}/estado", json={"estado": "borrador"}, headers=h)
    assert reabierta.json()["estado"] == "borrador"


async def test_los_usuarios_solo_ven_lo_validado(cliente: AsyncClient, f: Fabrica) -> None:
    validada = await f.ficha("Ficha validada", estado="validado")
    borrador = await f.ficha("Ficha en borrador", estado="borrador")
    h = f.cabecera(await f.usuario("agricultor"))
    lista = (await cliente.get(URL, headers=h)).json()
    assert [i["nombre"] for i in lista["items"]] == ["Ficha validada"]
    assert (await cliente.get(f"{URL}/{validada.id}", headers=h)).status_code == 200
    oculto = await cliente.get(f"{URL}/{borrador.id}", headers=h)
    assert oculto.status_code == 404
    assert oculto.json()["error"]["code"] == "PROBLEMA_NO_ENCONTRADO"
    # el filtro de estado no le sirve a quien no revisa
    assert (await cliente.get(URL, params={"estado": "borrador"}, headers=h)).json()["total"] == 1


async def test_el_experto_ve_todos_los_estados_y_filtra(cliente: AsyncClient, f: Fabrica) -> None:
    await f.ficha("Ficha validada", estado="validado")
    await f.ficha("Ficha en borrador", estado="borrador")
    h = f.cabecera(await f.usuario("experto"))
    assert (await cliente.get(URL, headers=h)).json()["total"] == 2
    borradores = await cliente.get(URL, params={"estado": "borrador"}, headers=h)
    assert [i["nombre"] for i in borradores.json()["items"]] == ["Ficha en borrador"]


async def test_busca_por_nombre_y_por_sintoma(cliente: AsyncClient, f: Fabrica) -> None:
    await f.ficha("Roya", sintomas=("polvo naranja en el envés",))
    await f.ficha("Broca", sintomas=("perforaciones en el fruto",))
    h = f.cabecera(await f.usuario("agricultor"))
    por_nombre = await cliente.get(URL, params={"q": "roya"}, headers=h)
    assert [i["nombre"] for i in por_nombre.json()["items"]] == ["Roya"]
    por_sintoma = await cliente.get(URL, params={"q": "perforaciones"}, headers=h)
    assert [i["nombre"] for i in por_sintoma.json()["items"]] == ["Broca"]


async def test_filtra_por_cultivo_y_tipo(cliente: AsyncClient, f: Fabrica) -> None:
    cultivo = await f.cultivo()
    await f.ficha("Del cultivo", cultivo=cultivo)
    await f.ficha("General")
    h = f.cabecera(await f.usuario("agricultor"))
    r = await cliente.get(URL, params={"cultivo_id": str(cultivo.id)}, headers=h)
    assert [i["nombre"] for i in r.json()["items"]] == ["Del cultivo"]
    assert (await cliente.get(URL, params={"tipo": "plaga"}, headers=h)).json()["total"] == 0


async def test_las_fuentes_se_crean_y_se_listan(cliente: AsyncClient, f: Fabrica) -> None:
    h = f.cabecera(await f.usuario("admin"))
    r = await cliente.post(
        "/fuentes", json={"nombre": "Fuente B", "url": "https://x.test"}, headers=h
    )
    assert r.status_code == 201
    assert [x["nombre"] for x in (await cliente.get("/fuentes", headers=h)).json()] == ["Fuente B"]
