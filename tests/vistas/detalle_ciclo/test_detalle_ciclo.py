"""Vista 10: Detalle de ciclo."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from app.models import Cosecha

URL = "/ciclos"
ENTRAN = {"admin", "agricultor", "contador"}


async def ciclo_de(f, yo, estado="en_curso"):
    siembra = await f.siembra(*await f.escenario(yo), estado=estado)
    await f.s.refresh(siembra, attribute_names=["ciclos"])
    return siembra, siembra.ciclos[0]


async def test_acceso_segun_el_rol(cliente, entrar_como, f, clave):
    yo = await entrar_como(clave)
    _, ciclo = await ciclo_de(f, yo)
    r = await cliente.get(f"{URL}/{ciclo.id}")
    assert r.status_code == (200 if clave in ENTRAN else 403)


async def test_sin_sesion_pide_iniciar_sesion(cliente, f):
    _, ciclo = await ciclo_de(f, await f.usuario())
    assert (await cliente.get(f"{URL}/{ciclo.id}")).status_code == 401


async def test_el_ciclo_de_otro_no_se_abre(cliente, entrar_como, f):
    await entrar_como("agricultor")
    _, ciclo = await ciclo_de(f, await f.usuario())
    assert (await cliente.get(f"{URL}/{ciclo.id}")).status_code == 404


async def test_ciclo_inexistente(cliente, entrar_como):
    await entrar_como("agricultor")
    r = await cliente.get(f"{URL}/{uuid.uuid4()}")
    assert r.json()["error"]["code"] == "CICLO_NO_ENCONTRADO"


async def test_no_cierra_sin_cosecha_ni_motivo(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    _, ciclo = await ciclo_de(f, yo)
    r = await cliente.post(f"{URL}/{ciclo.id}/cerrar")
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "CICLO_SIN_COSECHA"


async def test_cierra_cuando_hay_cosecha(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    _, ciclo = await ciclo_de(f, yo)
    f.s.add(
        Cosecha(
            finca_id=ciclo.finca_id,
            ciclo_id=ciclo.id,
            creado_por=ciclo.creado_por,
            fecha=datetime.now(UTC),
            cantidad=Decimal("20"),
            unidad="kilo",
        )
    )
    await f.s.commit()
    r = await cliente.post(f"{URL}/{ciclo.id}/cerrar")
    assert r.status_code == 200
    assert r.json()["estado"] == "cerrado"
    assert r.json()["fecha_fin"] == date.today().isoformat()


async def test_iniciar_un_ciclo_planeado(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    siembra, ciclo = await ciclo_de(f, yo, estado="planeada")
    r = await cliente.post(f"/siembras/{siembra.id}/iniciar")
    assert r.json()["ciclos"][0]["estado"] == "abierto"
    repetido = await cliente.post(f"{URL}/{ciclo.id}/iniciar")
    assert repetido.status_code == 422


async def test_necesidad_de_insumos_de_la_vista(cliente, entrar_como, f):
    yo = await entrar_como("agricultor")
    _, ciclo = await ciclo_de(f, yo)
    r = await cliente.get(f"{URL}/{ciclo.id}/necesidad-insumos")
    assert r.status_code == 200
    assert "Falta cargar las dosis" in r.json()["aviso"]
