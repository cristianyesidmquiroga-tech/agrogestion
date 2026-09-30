import uuid

from httpx import AsyncClient

from tests.conftest import Fabrica, payload_siembra

URL = "/api/v1/siembras"


async def preparar(f: Fabrica, area_lote: str = "5", **cultivo):  # type: ignore[no-untyped-def]
    usuario = await f.usuario()
    finca = await f.finca(usuario)
    lote = await f.lote(finca, area=area_lote)
    cultivo_ = await f.cultivo(**cultivo)
    return usuario, finca, lote, cultivo_


async def test_planear_una_siembra_crea_su_ciclo_de_levante(
    cliente: AsyncClient, f: Fabrica
) -> None:
    u, finca, lote, cultivo = await preparar(f)
    r = await cliente.post(
        URL, json=payload_siembra(finca.id, lote.id, cultivo.id), headers=f.cabecera(u)
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert cuerpo["estado"] == "planeada"
    assert len(cuerpo["ciclos"]) == 1
    assert cuerpo["ciclos"][0]["tipo"] == "levante"
    assert cuerpo["ciclos"][0]["estado"] == "planeado"


async def test_el_area_no_puede_superar_lo_libre_del_lote(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f, area_lote="5")
    h = f.cabecera(u)
    uno = await cliente.post(
        URL, json=payload_siembra(finca.id, lote.id, cultivo.id, area_ha=3), headers=h
    )
    assert uno.status_code == 201
    dos = await cliente.post(
        URL, json=payload_siembra(finca.id, lote.id, cultivo.id, area_ha=2), headers=h
    )
    assert dos.status_code == 201
    tres = await cliente.post(
        URL, json=payload_siembra(finca.id, lote.id, cultivo.id, area_ha=0.5), headers=h
    )
    assert tres.status_code == 422
    assert tres.json()["error"] == "AREA_SUPERA_LOTE"


async def test_cancelar_libera_el_area(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f, area_lote="5")
    h = f.cabecera(u)
    creada = (
        await cliente.post(
            URL, json=payload_siembra(finca.id, lote.id, cultivo.id, area_ha=5), headers=h
        )
    ).json()
    cancelada = await cliente.post(f"{URL}/{creada['id']}/cancelar", headers=h)
    assert cancelada.status_code == 200
    assert cancelada.json()["estado"] == "cancelada"
    assert cancelada.json()["ciclos"][0]["estado"] == "cerrado"
    otra = await cliente.post(
        URL, json=payload_siembra(finca.id, lote.id, cultivo.id, area_ha=5), headers=h
    )
    assert otra.status_code == 201
    repetida = await cliente.post(f"{URL}/{creada['id']}/cancelar", headers=h)
    assert repetida.status_code == 422


async def test_cultivo_por_planta_exige_cuantas_plantas(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f)
    r = await cliente.post(
        URL,
        json=payload_siembra(finca.id, lote.id, cultivo.id, plantas_sembradas=None),
        headers=f.cabecera(u),
    )
    assert r.status_code == 422
    assert r.json()["error"] == "PLANTAS_OBLIGATORIAS"


async def test_cultivo_por_area_no_exige_plantas(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f, unidad_conteo="area")
    r = await cliente.post(
        URL,
        json=payload_siembra(finca.id, lote.id, cultivo.id, plantas_sembradas=None),
        headers=f.cabecera(u),
    )
    assert r.status_code == 201


async def test_metodo_fuera_del_perfil_se_rechaza(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f, metodos=("semilla",))
    r = await cliente.post(
        URL,
        json=payload_siembra(finca.id, lote.id, cultivo.id, metodo="injerto"),
        headers=f.cabecera(u),
    )
    assert r.status_code == 422
    assert r.json()["error"] == "METODO_NO_VALIDO"


async def test_lote_de_otra_finca_no_se_encuentra(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, _, cultivo = await preparar(f)
    otra_finca = await f.finca(u)
    lote_ajeno = await f.lote(otra_finca, nombre="Otro")
    r = await cliente.post(
        URL, json=payload_siembra(finca.id, lote_ajeno.id, cultivo.id), headers=f.cabecera(u)
    )
    assert r.status_code == 404
    assert r.json()["error"] == "LOTE_NO_ENCONTRADO"


async def test_iniciar_la_siembra_inicia_su_primer_ciclo(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f)
    h = f.cabecera(u)
    creada = (
        await cliente.post(URL, json=payload_siembra(finca.id, lote.id, cultivo.id), headers=h)
    ).json()
    r = await cliente.post(f"{URL}/{creada['id']}/iniciar", headers=h)
    assert r.status_code == 200
    assert r.json()["estado"] == "en_curso"
    assert r.json()["ciclos"][0]["estado"] == "en_curso"
    assert r.json()["ciclos"][0]["fecha_inicio"] is not None
    otra_vez = await cliente.post(f"{URL}/{creada['id']}/iniciar", headers=h)
    assert otra_vez.status_code == 422


async def test_contador_lee_pero_no_crea(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f)
    contador = await f.usuario("contador")
    await f.finca(contador)
    creada = await cliente.post(
        URL, json=payload_siembra(finca.id, lote.id, cultivo.id), headers=f.cabecera(u)
    )
    assert creada.status_code == 201
    assert (await cliente.get(URL, headers=f.cabecera(contador))).status_code == 200
    bloqueado = await cliente.post(
        URL, json=payload_siembra(finca.id, lote.id, cultivo.id), headers=f.cabecera(contador)
    )
    assert bloqueado.status_code == 403


async def test_listar_filtra_por_estado_y_pagina(cliente: AsyncClient, f: Fabrica) -> None:
    u, finca, lote, cultivo = await preparar(f, area_lote="10")
    h = f.cabecera(u)
    for _ in range(3):
        await cliente.post(
            URL, json=payload_siembra(finca.id, lote.id, cultivo.id, area_ha=1), headers=h
        )
    r = await cliente.get(URL, params={"estado": "planeada", "limit": 2}, headers=h)
    assert r.json()["total"] == 3
    assert r.json()["has_more"] is True
    vacio = await cliente.get(URL, params={"estado": "cerrada"}, headers=h)
    assert vacio.json()["total"] == 0


async def test_siembra_inexistente_responde_404(cliente: AsyncClient, f: Fabrica) -> None:
    u = await f.usuario()
    r = await cliente.get(f"{URL}/{uuid.uuid4()}", headers=f.cabecera(u))
    assert r.status_code == 404
    assert r.json()["error"] == "SIEMBRA_NO_ENCONTRADA"
