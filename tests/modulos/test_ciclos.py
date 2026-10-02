import uuid
from datetime import UTC, datetime
from decimal import Decimal

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ciclo, Cosecha
from tests.conftest import Fabrica, payload_siembra


async def siembra_en_curso(cliente: AsyncClient, f: Fabrica, **cultivo):  # type: ignore[no-untyped-def]
    usuario = await f.usuario()
    finca = await f.finca(usuario)
    lote = await f.lote(finca)
    c = await f.cultivo(**cultivo)
    h = f.cabecera(usuario)
    creada = (
        await cliente.post("/siembras", json=payload_siembra(finca.id, lote.id, c.id), headers=h)
    ).json()
    iniciada = (await cliente.post(f"/siembras/{creada['id']}/iniciar", headers=h)).json()
    return h, iniciada, iniciada["ciclos"][0]["id"]


async def test_cerrar_sin_cosecha_ni_motivo_se_rechaza(cliente: AsyncClient, f: Fabrica) -> None:
    h, _, ciclo = await siembra_en_curso(cliente, f)
    r = await cliente.post(f"/ciclos/{ciclo}/cerrar", headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "CICLO_SIN_COSECHA"


async def test_cerrar_con_motivo_de_perdida(cliente: AsyncClient, f: Fabrica) -> None:
    h, _, ciclo = await siembra_en_curso(cliente, f)
    r = await cliente.post(
        f"/ciclos/{ciclo}/cerrar", json={"motivo_perdida": "Helada total"}, headers=h
    )
    assert r.status_code == 200
    assert r.json()["estado"] == "cerrado"
    assert r.json()["motivo_perdida"] == "Helada total"


async def test_cerrar_con_cosecha_registrada(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    h, _, ciclo = await siembra_en_curso(cliente, f)
    c = await sesion.get(Ciclo, uuid.UUID(ciclo))
    assert c is not None
    sesion.add(
        Cosecha(
            finca_id=c.finca_id,
            ciclo_id=c.id,
            creado_por=c.creado_por,
            fecha=datetime.now(UTC),
            cantidad=Decimal("50"),
            unidad="kilo",
        )
    )
    await sesion.commit()
    r = await cliente.post(f"/ciclos/{ciclo}/cerrar", headers=h)
    assert r.status_code == 200


async def test_en_transitorio_cerrar_el_ciclo_cierra_la_siembra(
    cliente: AsyncClient, f: Fabrica
) -> None:
    h, siembra, ciclo = await siembra_en_curso(
        cliente, f, nombre="Transitorio", tipo_ciclo="transitorio", tipo_renovacion=None
    )
    await cliente.post(f"/ciclos/{ciclo}/cerrar", json={"motivo_perdida": "Sin cosecha"}, headers=h)
    r = await cliente.get(f"/siembras/{siembra['id']}", headers=h)
    assert r.json()["estado"] == "cerrada"
    nuevo = await cliente.post(
        f"/siembras/{siembra['id']}/ciclos", json={"tipo": "produccion"}, headers=h
    )
    assert nuevo.status_code == 422


async def test_ciclos_de_un_cultivo_permanente(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, levante = await siembra_en_curso(cliente, f)
    base = f"/siembras/{siembra['id']}"
    bloqueado = await cliente.post(f"{base}/ciclos", json={"tipo": "produccion"}, headers=h)
    assert bloqueado.status_code == 409
    await cliente.post(
        f"/ciclos/{levante}/cerrar", json={"motivo_perdida": "Cierre de prueba"}, headers=h
    )

    produccion = await cliente.post(f"{base}/ciclos", json={"tipo": "produccion"}, headers=h)
    assert produccion.status_code == 201
    assert produccion.json()["numero"] == 2
    assert produccion.json()["estado"] == "planeado"
    iniciado = await cliente.post(f"/ciclos/{produccion.json()['id']}/iniciar", headers=h)
    assert iniciado.status_code == 200
    assert iniciado.json()["estado"] == "abierto"

    await cliente.post(
        f"/ciclos/{produccion.json()['id']}/cerrar",
        json={"motivo_perdida": "Fin de año"},
        headers=h,
    )
    renovacion = await cliente.post(f"{base}/renovar", headers=h)
    assert renovacion.status_code == 201
    assert renovacion.json()["tipo"] == "renovacion"
    await cliente.post(f"/ciclos/{renovacion.json()['id']}/iniciar", headers=h)
    await cliente.post(
        f"/ciclos/{renovacion.json()['id']}/cerrar",
        json={"motivo_perdida": "Zoca hecha"},
        headers=h,
    )
    nuevo_levante = await cliente.post(f"{base}/ciclos", json={"tipo": "levante"}, headers=h)
    assert nuevo_levante.status_code == 201
    assert nuevo_levante.json()["numero"] == 4


async def test_levante_solo_sigue_a_una_renovacion(cliente: AsyncClient, f: Fabrica) -> None:
    h, siembra, levante = await siembra_en_curso(cliente, f)
    await cliente.post(
        f"/ciclos/{levante}/cerrar", json={"motivo_perdida": "Cierre de prueba"}, headers=h
    )
    r = await cliente.post(f"/siembras/{siembra['id']}/ciclos", json={"tipo": "levante"}, headers=h)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "CICLO_TIPO_NO_VALIDO"


async def test_renovar_exige_que_el_cultivo_tenga_renovacion(
    cliente: AsyncClient, f: Fabrica
) -> None:
    h, siembra, levante = await siembra_en_curso(
        cliente, f, nombre="Sin renovacion", tipo_renovacion=None
    )
    await cliente.post(
        f"/ciclos/{levante}/cerrar", json={"motivo_perdida": "Cierre de prueba"}, headers=h
    )
    r = await cliente.post(f"/siembras/{siembra['id']}/renovar", headers=h)
    assert r.status_code == 422


async def test_solo_un_ciclo_en_curso(cliente: AsyncClient, f: Fabrica) -> None:
    h, _, ciclo = await siembra_en_curso(cliente, f)
    r = await cliente.post(f"/ciclos/{ciclo}/iniciar", headers=h)
    assert r.status_code == 422
