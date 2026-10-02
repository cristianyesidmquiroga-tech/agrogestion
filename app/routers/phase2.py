from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppError
from app.dependencies import current_user
from app.models import (
    Actividad,
    Ciclo,
    Cosecha,
    EtapaProceso,
    Gasto,
    Ingreso,
    Insumo,
    Jornal,
    MovimientoInsumo,
    PrecioCategoria,
    Proceso,
    Trabajador,
    Usuario,
    Venta,
)
from app.schemas.phase2 import (
    ActividadCreate,
    ActividadResponse,
    ActividadUpdate,
    AnulacionCreate,
    CicloCreate,
    CicloResponse,
    ContableResponse,
    CosechaAcumuladoResponse,
    CosechaCreate,
    CosechaResponse,
    EtapaCreate,
    EtapaResponse,
    EtapasMetricasResponse,
    FlujoCajaResponse,
    GastoCreate,
    IngresoCreate,
    InsumoCreate,
    InsumoResponse,
    JornalCreate,
    JornalResponse,
    MovimientoCreate,
    MovimientoResponse,
    PrecioCreate,
    PrecioResponse,
    ProcesoCreate,
    ProcesoResponse,
    TrabajadorCreate,
    TrabajadorResponse,
    TrabajadorUpdate,
    VentaCreate,
    VentaResponse,
)
from app.services.phase2 import (
    cancel_expense,
    cancel_income,
    cash_flow,
    create_activity,
    create_cycle,
    create_expense,
    create_harvest,
    create_income,
    create_jornal,
    create_price,
    create_process,
    create_sale,
    create_stage,
    create_supply,
    create_worker,
    deactivate_activity,
    deactivate_worker,
    harvest_accumulated,
    list_expenses,
    list_income,
    list_movements,
    list_prices,
    move_stock,
    pay_jornal,
    stage_metrics,
    transition_stage,
    update_activity,
    update_worker,
)

router = APIRouter(tags=["fase 2"])


@router.post(
    "/fincas/{finca_id}/ciclos", response_model=CicloResponse, status_code=status.HTTP_201_CREATED
)
async def cycle_route(
    finca_id: UUID,
    data: CicloCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Ciclo:
    return await create_cycle(db, user.id, finca_id, data)


@router.post(
    "/fincas/{finca_id}/actividades",
    response_model=ActividadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def activity_route(
    finca_id: UUID,
    data: ActividadCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Actividad:
    return await create_activity(db, user.id, finca_id, data)


@router.get("/fincas/{finca_id}/actividades", response_model=list[ActividadResponse])
async def activity_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[Actividad]:
    from app.services.lands import user_finca

    await user_finca(db, user.id, finca_id)
    result = await db.scalars(
        select(Actividad).where(Actividad.finca_id == finca_id, Actividad.estado == "activa")
    )
    return list(result)


@router.patch("/fincas/{finca_id}/actividades/{activity_id}", response_model=ActividadResponse)
async def activity_update(
    finca_id: UUID,
    activity_id: UUID,
    data: ActividadUpdate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Actividad:
    return await update_activity(db, user.id, finca_id, activity_id, data)


@router.delete("/fincas/{finca_id}/actividades/{activity_id}", response_model=ActividadResponse)
async def activity_delete(
    finca_id: UUID,
    activity_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Actividad:
    return await deactivate_activity(db, user.id, finca_id, activity_id)


@router.post(
    "/fincas/{finca_id}/trabajadores",
    response_model=TrabajadorResponse,
    status_code=status.HTTP_201_CREATED,
)
async def worker_route(
    finca_id: UUID,
    data: TrabajadorCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> dict[str, object]:
    item = await create_worker(db, user.id, finca_id, data)
    return {
        "id": item.id,
        "finca_id": item.finca_id,
        "nombre": item.nombre,
        "tipo": item.tipo,
        "jornal_habitual": item.jornal_habitual,
        "documento_ultimos4": None,
        "telefono": item.telefono,
        "estado": item.estado,
    }


@router.get("/fincas/{finca_id}/trabajadores", response_model=list[TrabajadorResponse])
async def worker_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[Trabajador]:
    from app.services.lands import user_finca

    await user_finca(db, user.id, finca_id)
    result = await db.scalars(
        select(Trabajador).where(Trabajador.finca_id == finca_id, Trabajador.estado == "activo")
    )
    return list(result)


@router.patch("/fincas/{finca_id}/trabajadores/{worker_id}", response_model=TrabajadorResponse)
async def worker_update(
    finca_id: UUID,
    worker_id: UUID,
    data: TrabajadorUpdate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> dict[str, object]:
    item = await update_worker(db, user.id, finca_id, worker_id, data)
    return {
        "id": item.id,
        "finca_id": item.finca_id,
        "nombre": item.nombre,
        "tipo": item.tipo,
        "jornal_habitual": item.jornal_habitual,
        "documento_ultimos4": None,
        "telefono": item.telefono,
        "estado": item.estado,
    }


@router.delete("/fincas/{finca_id}/trabajadores/{worker_id}", response_model=TrabajadorResponse)
async def worker_delete(
    finca_id: UUID,
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> dict[str, object]:
    item = await deactivate_worker(db, user.id, finca_id, worker_id)
    return {
        "id": item.id,
        "finca_id": item.finca_id,
        "nombre": item.nombre,
        "tipo": item.tipo,
        "jornal_habitual": item.jornal_habitual,
        "documento_ultimos4": None,
        "telefono": item.telefono,
        "estado": item.estado,
    }


@router.post(
    "/fincas/{finca_id}/jornales",
    response_model=JornalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def jornal_route(
    finca_id: UUID,
    data: JornalCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    _: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Jornal:
    return await create_jornal(db, user.id, finca_id, data)


@router.post("/fincas/{finca_id}/jornales/{jornal_id}/pagar", response_model=JornalResponse)
async def pay_route(
    finca_id: UUID,
    jornal_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Jornal:
    return await pay_jornal(db, user.id, finca_id, jornal_id, key)  # type: ignore[return-value]


@router.post(
    "/fincas/{finca_id}/insumos", response_model=InsumoResponse, status_code=status.HTTP_201_CREATED
)
async def supply_route(
    finca_id: UUID,
    data: InsumoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Insumo:
    return await create_supply(db, user.id, finca_id, data)


@router.post("/fincas/{finca_id}/insumos/entrada", response_model=InsumoResponse)
async def input_route(
    finca_id: UUID,
    data: MovimientoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Insumo:
    return await move_stock(db, user.id, finca_id, data, "entrada", key)  # type: ignore[return-value]


@router.post("/fincas/{finca_id}/insumos/consumo", response_model=InsumoResponse)
async def output_route(
    finca_id: UUID,
    data: MovimientoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Insumo:
    if not data.actividad_id:
        raise AppError(
            422, "ACTIVIDAD_REQUERIDA", "El consumo debe estar asociado a una actividad."
        )
    return await move_stock(db, user.id, finca_id, data, "consumo", key)  # type: ignore[return-value]


@router.post(
    "/fincas/{finca_id}/cosechas",
    response_model=CosechaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def harvest_route(
    finca_id: UUID,
    data: CosechaCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Cosecha:
    return await create_harvest(db, user.id, finca_id, data)


@router.get(
    "/fincas/{finca_id}/ciclos/{cycle_id}/cosechas/acumulado",
    response_model=CosechaAcumuladoResponse,
)
async def harvest_total(
    finca_id: UUID,
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> dict[str, object]:
    return await harvest_accumulated(db, user.id, finca_id, cycle_id)


@router.post(
    "/fincas/{finca_id}/precios", response_model=PrecioResponse, status_code=status.HTTP_201_CREATED
)
async def price_route(
    finca_id: UUID,
    data: PrecioCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> PrecioCategoria:
    return await create_price(db, user.id, finca_id, data)


@router.get("/fincas/{finca_id}/precios", response_model=list[PrecioResponse])
async def price_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[PrecioCategoria]:
    return await list_prices(db, user.id, finca_id)


@router.post(
    "/fincas/{finca_id}/procesos",
    response_model=ProcesoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def process_route(
    finca_id: UUID,
    data: ProcesoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Proceso:
    return await create_process(db, user.id, finca_id, data)


@router.post(
    "/fincas/{finca_id}/procesos/{process_id}/etapas",
    response_model=EtapaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def stage_route(
    finca_id: UUID,
    process_id: UUID,
    data: EtapaCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> EtapaProceso:
    return await create_stage(db, user.id, finca_id, process_id, data)


@router.post("/fincas/{finca_id}/etapas/{stage_id}/{action}", response_model=EtapaResponse)
async def stage_transition(
    finca_id: UUID,
    stage_id: UUID,
    action: str,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> EtapaProceso:
    if action not in {"iniciar", "finalizar"}:
        raise AppError(422, "ACCION_INVALIDA", "La acción debe ser iniciar o finalizar.")
    return await transition_stage(db, user.id, finca_id, stage_id, action)


@router.get(
    "/fincas/{finca_id}/procesos/{process_id}/etapas/metricas",
    response_model=EtapasMetricasResponse,
)
async def stage_metrics_route(
    finca_id: UUID,
    process_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> dict[str, object]:
    return await stage_metrics(db, user.id, finca_id, process_id)


@router.get("/fincas/{finca_id}/movimientos-insumo", response_model=list[MovimientoResponse])
async def movement_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[MovimientoInsumo]:
    return await list_movements(db, user.id, finca_id)


@router.post(
    "/fincas/{finca_id}/gastos",
    response_model=ContableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def expense_route(
    finca_id: UUID,
    data: GastoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Gasto:
    return await create_expense(db, user.id, finca_id, data, key)  # type: ignore[return-value]


@router.get("/fincas/{finca_id}/gastos", response_model=list[ContableResponse])
async def expense_list(
    finca_id: UUID,
    ciclo_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> list[Gasto]:
    return await list_expenses(db, user.id, finca_id, ciclo_id)


@router.post(
    "/fincas/{finca_id}/ingresos",
    response_model=ContableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def income_route(
    finca_id: UUID,
    data: IngresoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Ingreso:
    return await create_income(db, user.id, finca_id, data, key)  # type: ignore[return-value]


@router.get("/fincas/{finca_id}/ingresos", response_model=list[ContableResponse])
async def income_list(
    finca_id: UUID,
    ciclo_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> list[Ingreso]:
    return await list_income(db, user.id, finca_id, ciclo_id)


@router.post("/fincas/{finca_id}/gastos/{expense_id}/anular", response_model=ContableResponse)
async def cancel_expense_route(
    finca_id: UUID,
    expense_id: UUID,
    data: AnulacionCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Gasto:
    return await cancel_expense(db, user.id, finca_id, expense_id, data.motivo)


@router.post("/fincas/{finca_id}/ingresos/{income_id}/anular", response_model=ContableResponse)
async def cancel_income_route(
    finca_id: UUID,
    income_id: UUID,
    data: AnulacionCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Ingreso:
    return await cancel_income(db, user.id, finca_id, income_id, data.motivo)


@router.get("/fincas/{finca_id}/flujo-caja", response_model=FlujoCajaResponse)
async def cash_flow_route(
    finca_id: UUID,
    anio: int,
    mes: int,
    ciclo_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> dict[str, object]:
    if not 1 <= mes <= 12:
        raise AppError(422, "MES_INVALIDO", "El mes debe estar entre 1 y 12.")
    return await cash_flow(db, user.id, finca_id, anio, mes, ciclo_id)


@router.post(
    "/fincas/{finca_id}/ventas", response_model=VentaResponse, status_code=status.HTTP_201_CREATED
)
async def sale_route(
    finca_id: UUID,
    data: VentaCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Venta:
    return await create_sale(db, user.id, finca_id, data, key)  # type: ignore[return-value]
