import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import select

from app.models import Ciclo, Cosecha, Gasto, Ingreso

URL = "/usuarios"


async def test_lista_los_perfiles_con_sus_conteos(cliente, f):
    admin = await f.usuario("admin")
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    await f.siembra(finca, lote, cultivo)
    r = await cliente.get(URL, headers=f.cabecera(admin))
    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["total"] == 2
    por_id = {u["id"]: u for u in cuerpo["items"]}
    assert por_id[str(dueno.id)]["fincas"] == 1
    assert por_id[str(dueno.id)]["siembras"] == 1
    assert por_id[str(admin.id)]["fincas"] == 0
    assert "password_hash" not in por_id[str(dueno.id)]


async def test_filtra_por_texto_rol_y_estado(cliente, f):
    admin = await f.usuario("admin")
    contador = await f.usuario("contador")
    inactivo = await f.usuario("agricultor")
    inactivo.activo = False
    f.s.add(inactivo)
    await f.s.commit()
    h = f.cabecera(admin)
    por_rol = (await cliente.get(URL, params={"rol": "contador"}, headers=h)).json()
    assert [u["id"] for u in por_rol["items"]] == [str(contador.id)]
    por_texto = (await cliente.get(URL, params={"q": contador.email}, headers=h)).json()
    assert por_texto["total"] == 1
    inactivos = (await cliente.get(URL, params={"activo": "false"}, headers=h)).json()
    assert [u["id"] for u in inactivos["items"]] == [str(inactivo.id)]


async def test_la_lista_se_pagina(cliente, f):
    admin = await f.usuario("admin")
    for _ in range(3):
        await f.usuario("agricultor")
    r = (await cliente.get(URL, params={"limit": 2}, headers=f.cabecera(admin))).json()
    assert len(r["items"]) == 2
    assert r["total"] == 4
    assert r["has_more"] is True


async def test_el_detalle_suma_produccion_y_dinero_de_sus_fincas(cliente, f):
    admin = await f.usuario("admin")
    dueno = await f.usuario("agricultor")
    finca, lote, cultivo = await f.escenario(dueno)
    siembra = await f.siembra(finca, lote, cultivo, estado="en_curso")
    ciclo = await f.s.scalar(select(Ciclo).where(Ciclo.siembra_id == siembra.id))
    ahora = datetime.now(UTC)
    gastos = [Decimal("1000"), Decimal("250")]
    anulado = Decimal("500")
    cantidad, precio = Decimal("50"), Decimal("30")
    f.s.add(
        Cosecha(
            finca_id=finca.id,
            ciclo_id=ciclo.id,
            cantidad=cantidad,
            unidad="kilo",
            fecha=ahora,
            creado_por=dueno.id,
        )
    )
    f.s.add_all(Gasto(finca_id=finca.id, categoria="Insumos", monto=m, fecha=ahora) for m in gastos)
    f.s.add(
        Gasto(finca_id=finca.id, categoria="Otro", monto=anulado, fecha=ahora, estado="anulado")
    )
    f.s.add(
        Ingreso(
            finca_id=finca.id,
            categoria="Venta",
            cantidad=cantidad,
            precio_unitario=precio,
            total=cantidad * precio,
            fecha=ahora,
        )
    )
    await f.s.commit()
    d = (await cliente.get(f"{URL}/{dueno.id}", headers=f.cabecera(admin))).json()
    assert (d["fincas"], d["siembras"], d["cosechas"]) == (1, 1, 1)
    assert d["gastos"] == float(sum(gastos))
    assert d["ingresos"] == float(cantidad * precio)
    assert d["bloqueado"] is False
    assert d["detalle_fincas"][0]["departamento_dane"] == finca.departamento_dane
    assert d["detalle_fincas"][0]["gastos"] == d["gastos"]


async def test_un_usuario_inexistente_da_404(cliente, f):
    admin = await f.usuario("admin")
    r = await cliente.get(f"{URL}/{uuid.uuid4()}", headers=f.cabecera(admin))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "USUARIO_NO_ENCONTRADO"
