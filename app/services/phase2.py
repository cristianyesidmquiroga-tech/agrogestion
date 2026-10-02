from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import encrypt_sensitive
from app.core.exceptions import AppError
from app.models import (
    Actividad,
    Ciclo,
    Cosecha,
    EtapaProceso,
    Gasto,
    Ingreso,
    Insumo,
    Jornal,
    LineaVenta,
    MovimientoInsumo,
    PrecioCategoria,
    Proceso,
    Trabajador,
    Venta,
)
from app.services.audit import record_audit
from app.services.idempotency import cached_response, save_response
from app.services.lands import user_finca


async def _finca(db: AsyncSession, user_id: UUID, finca_id: UUID) -> None:
    await user_finca(db, user_id, finca_id)


async def create_cycle(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Ciclo:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    item = Ciclo(finca_id=finca_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_supply(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Insumo:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    item = Insumo(finca_id=finca_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_harvest(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Cosecha:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    cycle = await db.scalar(
        select(Ciclo).where(Ciclo.id == data.ciclo_id, Ciclo.finca_id == finca_id)
    )
    if not cycle or cycle.estado != "abierto":
        raise AppError(400, "CICLO_NO_VALIDO", "El ciclo no existe o no está abierto.")
    item = Cosecha(finca_id=finca_id, creado_por=user_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_process(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Proceso:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    item = Proceso(finca_id=finca_id, creado_por=user_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_stage(
    db: AsyncSession, user_id: UUID, finca_id: UUID, process_id: UUID, data: Any
) -> EtapaProceso:
    await _finca(db, user_id, finca_id)
    if not await db.scalar(
        select(Proceso).where(Proceso.id == process_id, Proceso.finca_id == finca_id)
    ):
        raise AppError(404, "PROCESO_NO_ENCONTRADO", "El proceso no pertenece a la finca.")
    item = EtapaProceso(
        finca_id=finca_id, proceso_id=process_id, creado_por=user_id, **data.model_dump()
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_activity(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Actividad:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    ciclo = await db.scalar(
        select(Ciclo).where(Ciclo.id == data.ciclo_id, Ciclo.finca_id == finca_id)
    )
    if not ciclo or ciclo.estado != "abierto":
        raise AppError(400, "CICLO_NO_VALIDO", "El ciclo no existe o no está abierto.")
    if data.fecha_fin and data.fecha_fin < data.fecha_inicio:
        raise AppError(
            422, "FECHAS_INVALIDAS", "La fecha final no puede ser anterior a la inicial."
        )
    item = Actividad(finca_id=finca_id, creado_por=user_id, estado="activa", **data.model_dump())
    db.add(item)
    await db.flush()
    await record_audit(db, "creacion", "actividad", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def update_activity(
    db: AsyncSession, user_id: UUID, finca_id: UUID, activity_id: UUID, data: Any
) -> Actividad:
    await _finca(db, user_id, finca_id)
    item = await db.scalar(
        select(Actividad).where(Actividad.id == activity_id, Actividad.finca_id == finca_id)
    )
    if not item or item.estado != "activa":
        raise AppError(404, "ACTIVIDAD_NO_ENCONTRADA", "La actividad no existe.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    if item.fecha_fin and item.fecha_fin < item.fecha_inicio:
        raise AppError(
            422, "FECHAS_INVALIDAS", "La fecha final no puede ser anterior a la inicial."
        )
    await record_audit(db, "actualizacion", "actividad", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def deactivate_activity(
    db: AsyncSession, user_id: UUID, finca_id: UUID, activity_id: UUID
) -> Actividad:
    await _finca(db, user_id, finca_id)
    item = await db.scalar(
        select(Actividad).where(Actividad.id == activity_id, Actividad.finca_id == finca_id)
    )
    if not item:
        raise AppError(404, "ACTIVIDAD_NO_ENCONTRADA", "La actividad no existe.")
    item.estado = "anulada"
    await record_audit(db, "anulacion", "actividad", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def create_worker(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Trabajador:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    values = data.model_dump(exclude={"documento"})
    if data.documento:
        values["documento_cifrado"] = encrypt_sensitive(data.documento)
    item = Trabajador(finca_id=finca_id, **values)
    db.add(item)
    await db.flush()
    await record_audit(db, "creacion", "trabajador", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def update_worker(
    db: AsyncSession, user_id: UUID, finca_id: UUID, worker_id: UUID, data: Any
) -> Trabajador:
    await _finca(db, user_id, finca_id)
    item = await db.scalar(
        select(Trabajador).where(Trabajador.id == worker_id, Trabajador.finca_id == finca_id)
    )
    if not item or item.estado != "activo":
        raise AppError(404, "TRABAJADOR_NO_ENCONTRADO", "El trabajador no existe.")
    values = data.model_dump(exclude_unset=True, exclude={"documento"})
    if data.documento is not None:
        values["documento_cifrado"] = encrypt_sensitive(data.documento)
    for field, value in values.items():
        setattr(item, field, value)
    await record_audit(db, "actualizacion", "trabajador", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def deactivate_worker(
    db: AsyncSession, user_id: UUID, finca_id: UUID, worker_id: UUID
) -> Trabajador:
    await _finca(db, user_id, finca_id)
    item = await db.scalar(
        select(Trabajador).where(Trabajador.id == worker_id, Trabajador.finca_id == finca_id)
    )
    if not item:
        raise AppError(404, "TRABAJADOR_NO_ENCONTRADO", "El trabajador no existe.")
    item.estado = "anulado"
    await record_audit(db, "anulacion", "trabajador", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def list_movements(db: AsyncSession, user_id: UUID, finca_id: UUID) -> list[MovimientoInsumo]:
    await _finca(db, user_id, finca_id)
    result = await db.scalars(
        select(MovimientoInsumo)
        .where(MovimientoInsumo.finca_id == finca_id)
        .order_by(MovimientoInsumo.fecha.desc())
    )
    return list(result)


async def harvest_accumulated(
    db: AsyncSession, user_id: UUID, finca_id: UUID, cycle_id: UUID
) -> dict[str, object]:
    await _finca(db, user_id, finca_id)
    total = await db.scalar(
        select(func.coalesce(func.sum(Cosecha.cantidad), 0)).where(
            Cosecha.finca_id == finca_id, Cosecha.ciclo_id == cycle_id, Cosecha.estado == "activa"
        )
    )
    history = await db.scalars(
        select(Cosecha)
        .where(
            Cosecha.finca_id == finca_id, Cosecha.ciclo_id == cycle_id, Cosecha.estado == "activa"
        )
        .order_by(Cosecha.fecha)
    )
    return {
        "finca_id": finca_id,
        "ciclo_id": cycle_id,
        "total": total or Decimal("0"),
        "registros": list(history),
    }


async def transition_stage(
    db: AsyncSession, user_id: UUID, finca_id: UUID, stage_id: UUID, action: str
) -> EtapaProceso:
    await _finca(db, user_id, finca_id)
    item = await db.scalar(
        select(EtapaProceso)
        .where(EtapaProceso.id == stage_id, EtapaProceso.finca_id == finca_id)
        .with_for_update()
    )
    if not item:
        raise AppError(404, "ETAPA_NO_ENCONTRADA", "La etapa no existe.")
    now = datetime.now(UTC)
    if action == "iniciar" and item.estado == "pendiente":
        item.estado, item.iniciado_en = "en_progreso", now
    elif action == "finalizar" and item.estado == "en_progreso":
        item.estado, item.finalizado_en = "finalizada", now
    else:
        raise AppError(409, "TRANSICION_INVALIDA", "La etapa no permite esa transición.")
    await db.commit()
    await db.refresh(item)
    return item


async def stage_metrics(
    db: AsyncSession, user_id: UUID, finca_id: UUID, process_id: UUID
) -> dict[str, object]:
    await _finca(db, user_id, finca_id)
    if not await db.scalar(
        select(Proceso).where(Proceso.id == process_id, Proceso.finca_id == finca_id)
    ):
        raise AppError(404, "PROCESO_NO_ENCONTRADO", "El proceso no pertenece a la finca.")
    stages = list(
        await db.scalars(
            select(EtapaProceso).where(
                EtapaProceso.proceso_id == process_id, EtapaProceso.finca_id == finca_id
            )
        )
    )
    estimated = sum((stage.dias_estimados for stage in stages), Decimal("0"))
    now = datetime.now(UTC)
    real = Decimal("0")
    for stage in stages:
        if stage.iniciado_en:
            end = stage.finalizado_en or now
            real += Decimal(str((end - stage.iniciado_en).total_seconds() / 86400)).quantize(
                Decimal("0.01")
            )
    return {
        "proceso_id": process_id,
        "dias_estimados": estimated,
        "dias_reales": real,
        "diferencia": real - estimated,
    }


async def create_price(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> PrecioCategoria:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    if data.vigente_hasta and data.vigente_hasta <= data.vigente_desde:
        raise AppError(422, "VIGENCIA_INVALIDA", "La vigencia del precio no es válida.")
    item = PrecioCategoria(finca_id=finca_id, creado_por=user_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def list_prices(db: AsyncSession, user_id: UUID, finca_id: UUID) -> list[PrecioCategoria]:
    await _finca(db, user_id, finca_id)
    result = await db.scalars(
        select(PrecioCategoria)
        .where(PrecioCategoria.finca_id == finca_id)
        .order_by(PrecioCategoria.vigente_desde.desc())
    )
    return list(result)


async def create_jornal(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Jornal:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    ciclo = await db.scalar(
        select(Ciclo).where(Ciclo.id == data.ciclo_id, Ciclo.finca_id == finca_id)
    )
    activity = await db.scalar(
        select(Actividad).where(Actividad.id == data.actividad_id, Actividad.finca_id == finca_id)
    )
    if not ciclo or ciclo.estado != "abierto" or not activity:
        raise AppError(400, "REFERENCIA_NO_VALIDA", "El ciclo o la actividad no son válidos.")
    if data.trabajador_id:
        duplicate = await db.scalar(
            select(Jornal).where(
                Jornal.trabajador_id == data.trabajador_id,
                Jornal.fecha == data.fecha,
                Jornal.finca_id == finca_id,
            )
        )
        if duplicate:
            raise AppError(
                409, "JORNALE_DUPLICADO", "El trabajador ya tiene un jornal registrado ese día."
            )
    total = data.obreros * data.dias * data.valor_jornal
    item = Jornal(finca_id=finca_id, total=total, **data.model_dump())
    db.add(item)
    await db.flush()
    await record_audit(db, "creacion", "jornal", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def pay_jornal(
    db: AsyncSession, user_id: UUID, finca_id: UUID, jornal_id: UUID, key: str | None = None
) -> Jornal | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"pago_jornal:{finca_id}:{user_id}:{jornal_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    item = await db.scalar(
        select(Jornal).where(Jornal.id == jornal_id, Jornal.finca_id == finca_id).with_for_update()
    )
    if not item:
        raise AppError(404, "JORNALE_NO_ENCONTRADO", "El jornal no existe.")
    if item.estado != "pendiente":
        raise AppError(409, "JORNALE_YA_PAGADO", "El jornal ya fue procesado.")
    item.estado, item.pagado_en, item.pagado_por = "pagado", datetime.now(UTC), user_id
    gasto = Gasto(
        finca_id=finca_id,
        categoria="mano_de_obra",
        monto=item.total,
        fecha=item.pagado_en,
        origen_tipo="jornal",
        origen_id=item.id,
    )
    db.add(gasto)
    await record_audit(db, "pago", "jornal", user_id, finca_id, item.id)
    await db.flush()
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


async def move_stock(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, kind: str, key: str | None = None
) -> Insumo | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"movimiento_insumo:{kind}:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    item = await db.scalar(
        select(Insumo)
        .where(Insumo.id == data.insumo_id, Insumo.finca_id == finca_id)
        .with_for_update()
    )
    if not item:
        raise AppError(404, "INSUMO_NO_ENCONTRADO", "El insumo no existe.")
    if kind == "consumo" and not await db.scalar(
        select(Actividad).where(Actividad.id == data.actividad_id, Actividad.finca_id == finca_id)
    ):
        raise AppError(404, "ACTIVIDAD_NO_ENCONTRADA", "La actividad no pertenece a la finca.")
    if kind == "consumo" and item.existencia < data.cantidad:
        raise AppError(409, "EXISTENCIA_INSUFICIENTE", "La existencia no puede quedar negativa.")
    item.existencia += data.cantidad if kind == "entrada" else -data.cantidad
    movement = MovimientoInsumo(
        finca_id=finca_id, tipo=kind, creado_por=user_id, **data.model_dump()
    )
    db.add(movement)
    await db.flush()
    if kind == "entrada" and data.costo > 0:
        db.add(
            Gasto(
                finca_id=finca_id,
                categoria="insumo",
                monto=data.costo,
                fecha=data.fecha,
                origen_tipo="movimiento_insumo",
                origen_id=movement.id,
            )
        )
    await record_audit(db, "creacion", kind, user_id, finca_id, movement.id)
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


async def create_expense(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, key: str | None = None
) -> Gasto | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"gasto:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    item = Gasto(finca_id=finca_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await record_audit(db, "creacion", "gasto", user_id, finca_id, item.id)
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


async def create_income(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, key: str | None = None
) -> Ingreso | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"ingreso:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    item = Ingreso(finca_id=finca_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await record_audit(db, "creacion", "ingreso", user_id, finca_id, item.id)
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


async def cancel_expense(
    db: AsyncSession, user_id: UUID, finca_id: UUID, expense_id: UUID, reason: str
) -> Gasto:
    await _finca(db, user_id, finca_id)
    item = await db.scalar(
        select(Gasto).where(Gasto.id == expense_id, Gasto.finca_id == finca_id).with_for_update()
    )
    if not item:
        raise AppError(404, "GASTO_NO_ENCONTRADO", "El gasto no existe.")
    if item.estado == "anulado":
        raise AppError(409, "GASTO_YA_ANULADO", "El gasto ya está anulado.")
    item.estado, item.motivo_anulacion, item.anulado_por = "anulado", reason, user_id
    await record_audit(db, "anulacion", "gasto", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def cancel_income(
    db: AsyncSession, user_id: UUID, finca_id: UUID, income_id: UUID, reason: str
) -> Ingreso:
    await _finca(db, user_id, finca_id)
    item = await db.scalar(
        select(Ingreso)
        .where(Ingreso.id == income_id, Ingreso.finca_id == finca_id)
        .with_for_update()
    )
    if not item:
        raise AppError(404, "INGRESO_NO_ENCONTRADO", "El ingreso no existe.")
    if item.estado == "anulado":
        raise AppError(409, "INGRESO_YA_ANULADO", "El ingreso ya está anulado.")
    item.estado, item.motivo_anulacion, item.anulado_por = "anulado", reason, user_id
    await record_audit(db, "anulacion", "ingreso", user_id, finca_id, item.id)
    await db.commit()
    await db.refresh(item)
    return item


async def cash_flow(
    db: AsyncSession,
    user_id: UUID,
    finca_id: UUID,
    year: int,
    month: int,
    cycle_id: UUID | None = None,
) -> dict[str, object]:
    await _finca(db, user_id, finca_id)
    income = await db.scalar(
        select(func.coalesce(func.sum(Ingreso.total), 0)).where(
            Ingreso.finca_id == finca_id,
            Ingreso.estado == "activo",
            func.extract("year", Ingreso.fecha) == year,
            func.extract("month", Ingreso.fecha) == month,
            *([Ingreso.ciclo_id == cycle_id] if cycle_id else []),
        )
    )
    expenses = await db.scalar(
        select(func.coalesce(func.sum(Gasto.monto), 0)).where(
            Gasto.finca_id == finca_id,
            Gasto.estado == "activo",
            func.extract("year", Gasto.fecha) == year,
            func.extract("month", Gasto.fecha) == month,
            *([Gasto.ciclo_id == cycle_id] if cycle_id else []),
        )
    )
    income_value = income or 0
    expense_value = expenses or 0
    return {
        "finca_id": finca_id,
        "ciclo_id": cycle_id,
        "anio": year,
        "mes": month,
        "ingresos": income_value,
        "gastos": expense_value,
        "saldo": income_value - expense_value,
    }


async def list_expenses(
    db: AsyncSession, user_id: UUID, finca_id: UUID, cycle_id: UUID | None = None
) -> list[Gasto]:
    await _finca(db, user_id, finca_id)
    query = select(Gasto).where(Gasto.finca_id == finca_id)
    if cycle_id:
        query = query.where(Gasto.ciclo_id == cycle_id)
    return list(await db.scalars(query.order_by(Gasto.fecha.desc())))


async def list_income(
    db: AsyncSession, user_id: UUID, finca_id: UUID, cycle_id: UUID | None = None
) -> list[Ingreso]:
    await _finca(db, user_id, finca_id)
    query = select(Ingreso).where(Ingreso.finca_id == finca_id)
    if cycle_id:
        query = query.where(Ingreso.ciclo_id == cycle_id)
    return list(await db.scalars(query.order_by(Ingreso.fecha.desc())))


async def create_sale(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, key: str | None = None
) -> Venta | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"venta:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    sale = Venta(
        finca_id=finca_id, comprador=data.comprador, fecha=data.fecha, creado_por=user_id, total=0
    )
    db.add(sale)
    await db.flush()
    total = Decimal("0")
    for line in data.lineas:
        harvest = await db.scalar(
            select(Cosecha)
            .where(Cosecha.id == line.cosecha_id, Cosecha.finca_id == finca_id)
            .with_for_update()
        )
        if not harvest:
            raise AppError(404, "COSECHA_NO_ENCONTRADA", "La cosecha no pertenece a la finca.")
        sold = await db.scalar(
            select(func.coalesce(func.sum(LineaVenta.cantidad), 0))
            .join(Venta)
            .where(LineaVenta.cosecha_id == line.cosecha_id, Venta.estado == "activa")
        )
        available = harvest.cantidad - (sold or 0) - line.merma
        if line.cantidad > available:
            raise AppError(409, "CANTIDAD_NO_DISPONIBLE", "La venta supera la cantidad disponible.")
        line_total = line.cantidad * line.precio_unitario
        total += line_total
        db.add(LineaVenta(venta_id=sale.id, total=line_total, **line.model_dump()))
    sale.total = total
    db.add(
        Ingreso(
            finca_id=finca_id,
            categoria="venta",
            cantidad=1,
            precio_unitario=total,
            total=total,
            fecha=data.fecha,
            comprador=data.comprador,
            estado="activo",
        )
    )
    await db.flush()
    await record_audit(db, "creacion", "venta", user_id, finca_id, sale.id)
    await save_response(db, key, operation, jsonable_encoder(sale))
    await db.commit()
    await db.refresh(sale)
    return sale
