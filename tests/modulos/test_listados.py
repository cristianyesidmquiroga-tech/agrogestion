from datetime import UTC, datetime
from decimal import Decimal

from tests.conftest import CLAVE_PRUEBA, Fabrica

AHORA = datetime.now(UTC).isoformat()


async def _escenario(cliente, f: Fabrica, rol: str = "agricultor"):
    yo = await f.usuario(rol)
    cliente.headers.update(f.cabecera(yo))
    finca = await f.finca(yo)
    base = f"/fincas/{finca.id}"
    ciclo = (
        await cliente.post(f"{base}/ciclos", json={"nombre": "Ciclo 1", "fecha_inicio": AHORA})
    ).json()
    actividad = (
        await cliente.post(
            f"{base}/actividades",
            json={
                "ciclo_id": ciclo["id"],
                "nombre": "Socola",
                "fase": "preparacion",
                "fecha_inicio": AHORA,
                "area_trabajada": 1,
            },
        )
    ).json()
    trabajador = (
        await cliente.post(
            f"{base}/trabajadores",
            json={"nombre": "Pedro Nel", "tipo": "jornalero", "jornal_habitual": 90000},
        )
    ).json()
    return finca, base, ciclo, actividad, trabajador


async def _jornal(cliente, base, ciclo, actividad, trabajador=None):
    cuerpo = {
        "actividad_id": actividad["id"],
        "ciclo_id": ciclo["id"],
        "fecha": AHORA,
        "obreros": 2,
        "dias": 3,
        "valor_jornal": 60000,
    }
    if trabajador:
        cuerpo["trabajador_id"] = trabajador["id"]
    return await cliente.post(f"{base}/jornales", json=cuerpo)


async def test_los_jornales_traen_trabajador_labor_y_total(cliente, f):
    _, base, ciclo, actividad, trabajador = await _escenario(cliente, f)
    assert (await _jornal(cliente, base, ciclo, actividad, trabajador)).status_code == 201
    lista = (await cliente.get(f"{base}/jornales")).json()
    assert len(lista) == 1
    assert lista[0]["trabajador_nombre"] == "Pedro Nel"
    assert lista[0]["actividad_nombre"] == "Socola"
    assert Decimal(lista[0]["total"]) == Decimal("360000")
    assert lista[0]["estado"] == "pendiente"
    assert lista[0]["pagado_en"] is None


async def test_la_cuadrilla_sin_nombre_sale_sin_trabajador(cliente, f):
    _, base, ciclo, actividad, _ = await _escenario(cliente, f)
    await _jornal(cliente, base, ciclo, actividad)
    lista = (await cliente.get(f"{base}/jornales")).json()
    assert lista[0]["trabajador_id"] is None
    assert lista[0]["trabajador_nombre"] is None


async def test_filtrar_jornales_por_estado_y_pagarlos(cliente, f):
    _, base, ciclo, actividad, trabajador = await _escenario(cliente, f)
    jornal = (await _jornal(cliente, base, ciclo, actividad, trabajador)).json()
    pendientes = await cliente.get(f"{base}/jornales", params={"estado": "pendiente"})
    assert len(pendientes.json()) == 1
    assert (await cliente.get(f"{base}/jornales", params={"estado": "pagado"})).json() == []

    pago = await cliente.post(
        f"{base}/jornales/{jornal['id']}/pagar", headers={"Idempotency-Key": "pago-1"}
    )
    assert pago.status_code == 200

    assert (await cliente.get(f"{base}/jornales", params={"estado": "pendiente"})).json() == []
    pagados = (await cliente.get(f"{base}/jornales", params={"estado": "pagado"})).json()
    assert pagados[0]["pagado_en"] is not None
    gastos = (await cliente.get(f"{base}/gastos")).json()
    assert Decimal(gastos[0]["monto"]) == Decimal("360000")


async def test_un_estado_desconocido_se_rechaza(cliente, f):
    _, base, *_ = await _escenario(cliente, f)
    r = await cliente.get(f"{base}/jornales", params={"estado": "cualquiera"})
    assert r.status_code == 422


async def test_gastos_e_ingresos_traen_fecha_y_comprador(cliente, f):
    _, base, *_ = await _escenario(cliente, f)
    await cliente.post(
        f"{base}/gastos", json={"categoria": "Insumos", "monto": 1500, "fecha": AHORA}
    )
    await cliente.post(
        f"{base}/ingresos",
        json={
            "categoria": "Venta de cosecha",
            "cantidad": 10,
            "precio_unitario": 200,
            "fecha": AHORA,
            "comprador": "Cooperativa",
        },
    )
    gasto = (await cliente.get(f"{base}/gastos")).json()[0]
    ingreso = (await cliente.get(f"{base}/ingresos")).json()[0]
    assert gasto["fecha"] and gasto["comprador"] is None
    assert ingreso["fecha"]
    assert ingreso["comprador"] == "Cooperativa"
    assert Decimal(ingreso["cantidad"]) == Decimal("10")
    assert Decimal(ingreso["precio_unitario"]) == Decimal("200")


async def test_el_inventario_calcula_costo_promedio_y_valor(cliente, f):
    _, base, *_ = await _escenario(cliente, f)
    insumo = (
        await cliente.post(f"{base}/insumos", json={"nombre": "Urea 46%", "unidad": "bulto"})
    ).json()
    entrada = {"insumo_id": insumo["id"], "cantidad": 10, "fecha": AHORA, "costo": 1850000}
    r = await cliente.post(
        f"{base}/insumos/entrada", json=entrada, headers={"Idempotency-Key": "e1"}
    )
    assert r.status_code == 200
    lista = (await cliente.get(f"{base}/insumos")).json()
    assert lista[0]["nombre"] == "Urea 46%"
    assert Decimal(lista[0]["existencia"]) == Decimal("10")
    assert Decimal(lista[0]["costo_promedio"]) == Decimal("185000.00")
    assert Decimal(lista[0]["valor"]) == Decimal("1850000.00")
    assert lista[0]["ultimo_movimiento"] is not None


async def test_un_insumo_sin_entradas_no_inventa_costo(cliente, f):
    _, base, *_ = await _escenario(cliente, f)
    await cliente.post(f"{base}/insumos", json={"nombre": "Machete", "unidad": "unidad"})
    item = (await cliente.get(f"{base}/insumos")).json()[0]
    assert item["costo_promedio"] is None
    assert Decimal(item["valor"]) == 0


async def test_los_procesos_cuentan_sus_etapas(cliente, f):
    _, base, *_ = await _escenario(cliente, f)
    proceso = (
        await cliente.post(
            f"{base}/procesos",
            json={
                "nombre": "Secado lote 1",
                "producto": "Bijao seco",
                "materia_prima": "Hoja",
                "origen_materia": "propia",
                "fecha_inicio": AHORA,
            },
        )
    ).json()
    etapa = (
        await cliente.post(
            f"{base}/procesos/{proceso['id']}/etapas",
            json={"nombre": "Secar al sol", "dias_estimados": 5},
        )
    ).json()
    await cliente.post(f"{base}/etapas/{etapa['id']}/iniciar")
    await cliente.post(f"{base}/etapas/{etapa['id']}/finalizar")

    lista = (await cliente.get(f"{base}/procesos")).json()
    assert lista[0]["etapas"] == 1
    assert lista[0]["etapas_finalizadas"] == 1
    assert lista[0]["estado"] == "en_proceso"
    etapas = (await cliente.get(f"{base}/procesos/{proceso['id']}/etapas")).json()
    assert etapas[0]["nombre"] == "Secar al sol"
    assert etapas[0]["finalizado_en"] is not None


async def test_los_listados_son_solo_de_las_fincas_propias(cliente, f):
    otro = await f.usuario()
    ajena = await f.finca(otro)
    await _escenario(cliente, f)
    for ruta in ("jornales", "insumos", "procesos"):
        r = await cliente.get(f"/fincas/{ajena.id}/{ruta}")
        assert r.status_code == 404, ruta


async def test_cambiar_la_clave(cliente, f):
    yo = await f.usuario()
    cliente.headers.update(f.cabecera(yo))
    cuerpo = {"clave_actual": CLAVE_PRUEBA, "clave_nueva": "Clave-Nueva-456"}
    assert (await cliente.post("/cuenta/cambiar-clave", json=cuerpo)).status_code == 204
    nueva = await cliente.post(
        "/auth/login", json={"email": yo.email, "password": "Clave-Nueva-456"}
    )
    assert nueva.status_code == 200
    vieja = await cliente.post("/auth/login", json={"email": yo.email, "password": CLAVE_PRUEBA})
    assert vieja.status_code == 401


async def test_cambiar_la_clave_exige_la_actual_y_una_nueva_distinta(cliente, f):
    yo = await f.usuario()
    cliente.headers.update(f.cabecera(yo))
    ruta = "/cuenta/cambiar-clave"
    mala = await cliente.post(
        ruta, json={"clave_actual": "otra-xyz", "clave_nueva": "Clave-Nueva-456"}
    )
    assert mala.json()["error"]["code"] == "CLAVE_ACTUAL_INCORRECTA"
    igual = await cliente.post(
        ruta, json={"clave_actual": CLAVE_PRUEBA, "clave_nueva": CLAVE_PRUEBA}
    )
    assert igual.json()["error"]["code"] == "CLAVE_REPETIDA"
    corta = await cliente.post(ruta, json={"clave_actual": CLAVE_PRUEBA, "clave_nueva": "corta"})
    assert corta.status_code == 422
