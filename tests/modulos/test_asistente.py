import pytest
from httpx import AsyncClient

from app.services import asistente_service
from tests.conftest import Fabrica

URL = "/api/v1/consultas"


async def escenario(f: Fabrica, **cultivo):
    usuario = await f.usuario()
    finca, lote, c = await f.escenario(usuario, **cultivo)
    siembra = await f.siembra(finca, lote, c)
    return usuario, c, siembra


def pregunta(siembra, texto="Las hojas tienen manchas amarillas"):
    return {"siembra_id": str(siembra.id), "texto": texto}


async def test_responde_con_la_ficha_que_coincide(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, cultivo, siembra = await escenario(f)
    await f.ficha(
        "Mancha amarilla",
        cultivo=cultivo,
        quimico=("Aplicar según la etiqueta", "Producto Registrado X"),
    )
    r = await cliente.post(URL, json=pregunta(siembra), headers=f.cabecera(usuario))
    assert r.status_code == 201
    respuesta = r.json()["respuesta"]
    assert respuesta["hay_informacion"] is True
    causa = respuesta["causas_probables"][0]
    assert causa["problema"] == "Mancha amarilla"
    assert causa["coincidencia"] in ("alta", "media", "baja")
    assert "manchas" in causa["por_que"]
    assert causa["fuentes"]
    assert respuesta["que_hacer"] == ["Retire las hojas afectadas y mejore la ventilación."]
    assert respuesta["tratamientos"][0]["producto_ica"] == "Producto Registrado X"
    assert respuesta["tratamientos"][0]["fuente"]
    assert "reemplaza a un técnico" in respuesta["aviso"]
    assert respuesta["cuando_llamar_al_tecnico"]


async def test_sin_informacion_validada_lo_dice_y_no_inventa(
    cliente: AsyncClient, f: Fabrica
) -> None:
    usuario, _, siembra = await escenario(f)
    r = await cliente.post(URL, json=pregunta(siembra), headers=f.cabecera(usuario))
    respuesta = r.json()["respuesta"]
    assert respuesta["hay_informacion"] is False
    assert respuesta["causas_probables"] == []
    assert respuesta["tratamientos"] == []
    assert "No hay información validada" in respuesta["mensaje_tratamiento"]


async def test_no_usa_fichas_en_borrador_ni_de_otro_cultivo(
    cliente: AsyncClient, f: Fabrica
) -> None:
    usuario, cultivo, siembra = await escenario(f)
    otro = await f.cultivo("Otro cultivo")
    await f.ficha("Borrador", cultivo=cultivo, estado="borrador")
    await f.ficha("Ajena", cultivo=otro)
    r = await cliente.post(URL, json=pregunta(siembra), headers=f.cabecera(usuario))
    assert r.json()["respuesta"]["hay_informacion"] is False


async def test_una_ficha_general_aplica_a_cualquier_cultivo(
    cliente: AsyncClient, f: Fabrica
) -> None:
    usuario, _, siembra = await escenario(f)
    await f.ficha("Mancha general")
    r = await cliente.post(URL, json=pregunta(siembra), headers=f.cabecera(usuario))
    assert r.json()["respuesta"]["hay_informacion"] is True


async def test_sin_producto_registrado_no_hay_tratamiento(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, cultivo, siembra = await escenario(f)
    await f.ficha("Mancha amarilla", cultivo=cultivo)
    r = await cliente.post(URL, json=pregunta(siembra), headers=f.cabecera(usuario))
    respuesta = r.json()["respuesta"]
    assert respuesta["tratamientos"] == []
    assert "Consulte a un técnico" in respuesta["mensaje_tratamiento"]


async def test_la_siembra_de_otro_no_se_consulta(cliente: AsyncClient, f: Fabrica) -> None:
    _, _, siembra = await escenario(f)
    intruso = await f.usuario()
    r = await cliente.post(URL, json=pregunta(siembra), headers=f.cabecera(intruso))
    assert r.status_code == 404


async def test_historial_solo_propio_y_con_busqueda(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, cultivo, siembra = await escenario(f)
    otro = await f.usuario()
    h = f.cabecera(usuario)
    await cliente.post(URL, json=pregunta(siembra, "Las hojas tienen manchas amarillas"), headers=h)
    await cliente.post(URL, json=pregunta(siembra, "El fruto tiene perforaciones"), headers=h)
    lista = (await cliente.get(URL, headers=h)).json()
    assert lista["total"] == 2
    filtrada = (await cliente.get(URL, params={"q": "perforaciones"}, headers=h)).json()
    assert filtrada["total"] == 1
    assert (await cliente.get(URL, headers=f.cabecera(otro))).json()["total"] == 0
    consulta = lista["items"][0]["id"]
    assert (await cliente.get(f"{URL}/{consulta}", headers=h)).status_code == 200
    assert (await cliente.get(f"{URL}/{consulta}", headers=f.cabecera(otro))).status_code == 404


async def test_limite_de_consultas_por_dia(
    cliente: AsyncClient, f: Fabrica, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(asistente_service.settings, "consultas_por_dia", 2)
    usuario, _, siembra = await escenario(f)
    h = f.cabecera(usuario)
    for _ in range(2):
        assert (await cliente.post(URL, json=pregunta(siembra), headers=h)).status_code == 201
    r = await cliente.post(URL, json=pregunta(siembra), headers=h)
    assert r.status_code == 429
    assert r.json()["error"] == "LIMITE_DE_CONSULTAS"


async def test_retroalimentacion_y_calidad(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, _, siembra = await escenario(f)
    h = f.cabecera(usuario)
    admin = f.cabecera(await f.usuario("admin"))
    vacia = (await cliente.get("/api/v1/asistente/calidad", headers=admin)).json()
    assert vacia["porcentaje_que_sirvio"] is None
    assert "Aún no hay" in vacia["aviso"]

    c1 = (await cliente.post(URL, json=pregunta(siembra), headers=h)).json()["id"]
    c2 = (
        await cliente.post(URL, json=pregunta(siembra, "Las plantas se secan rápido"), headers=h)
    ).json()["id"]
    assert (
        await cliente.post(f"{URL}/{c1}/retroalimentacion", json={"valor": "sirvio"}, headers=h)
    ).status_code == 201
    await cliente.post(
        f"{URL}/{c2}/retroalimentacion",
        json={"valor": "equivocado", "comentario": "Era otra cosa"},
        headers=h,
    )
    corregida = await cliente.post(
        f"{URL}/{c2}/retroalimentacion", json={"valor": "no_sirvio"}, headers=h
    )
    assert corregida.json()["valor"] == "no_sirvio"
    calidad = (await cliente.get("/api/v1/asistente/calidad", headers=admin)).json()
    assert calidad["consultas"] == 2
    assert calidad["con_valoracion"] == 2
    assert calidad["sirvieron"] == 1
    assert calidad["no_sirvieron"] == 1
    assert calidad["porcentaje_que_sirvio"] == 50.0
    assert (await cliente.get(f"{URL}/{c1}", headers=h)).json()["valoracion"] == "sirvio"


async def test_no_se_valora_la_consulta_de_otro(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, _, siembra = await escenario(f)
    c = (await cliente.post(URL, json=pregunta(siembra), headers=f.cabecera(usuario))).json()["id"]
    otro = await f.usuario()
    r = await cliente.post(
        f"{URL}/{c}/retroalimentacion", json={"valor": "sirvio"}, headers=f.cabecera(otro)
    )
    assert r.status_code == 404


async def test_la_pregunta_tiene_limites(cliente: AsyncClient, f: Fabrica) -> None:
    usuario, _, siembra = await escenario(f)
    h = f.cabecera(usuario)
    assert (await cliente.post(URL, json=pregunta(siembra, "hoy"), headers=h)).status_code == 422
    assert (
        await cliente.post(URL, json=pregunta(siembra, "x" * 1001), headers=h)
    ).status_code == 422
