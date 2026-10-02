from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.exceptions import AppError
from app.models import Base, Cosecha, Especie, Finca, FincaUsuario, Usuario
from app.schemas.pecuario import AnimalCreate, EspecieCreate, LoteAnimalCreate
from app.schemas.phase2 import (
    ActividadCreate,
    ActividadUpdate,
    CicloCreate,
    GastoCreate,
    IngresoCreate,
    LineaVentaCreate,
    TrabajadorCreate,
    TrabajadorUpdate,
    VentaCreate,
)
from app.services.pecuario import create_animal, create_lot, create_species
from app.services.phase2 import (
    cancel_expense,
    cash_flow,
    create_activity,
    create_cycle,
    create_expense,
    create_income,
    create_sale,
    create_worker,
    deactivate_worker,
    update_activity,
    update_worker,
)


@pytest.fixture
async def session():  # type: ignore[no-untyped-def]
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        yield db
    await engine.dispose()


async def setup_farm(session, user_id, name):  # type: ignore[no-untyped-def]
    user = Usuario(
        id=user_id,
        email=f"{user_id}@example.com",
        nombre="Test",
        password_hash="x",
        rol="agricultor",
    )
    farm = Finca(id=uuid4(), nombre=name, creado_por=user_id)
    session.add_all([user, farm, FincaUsuario(finca_id=farm.id, usuario_id=user_id)])
    await session.commit()
    return farm


@pytest.mark.asyncio
async def test_animal_is_idempotent_and_cross_farm_is_rejected(session) -> None:  # type: ignore[no-untyped-def]
    user_a = uuid4()
    user_b = uuid4()
    farm_a = await setup_farm(session, user_a, "Finca A")
    farm_b = await setup_farm(session, user_b, "Finca B")
    species_a = await create_species(session, user_a, farm_a.id, EspecieCreate(nombre="Bovino"))
    species_b = await create_species(session, user_b, farm_b.id, EspecieCreate(nombre="Caprino"))

    animal_data = AnimalCreate(
        especie_id=species_a.id,
        arete="A-1",
        sexo="hembra",
        nacimiento=datetime.now(UTC),
    )
    first = await create_animal(session, user_a, farm_a.id, animal_data, "animal-key")
    second = await create_animal(session, user_a, farm_a.id, animal_data, "animal-key")
    assert str(first.id) == second["id"]  # type: ignore[union-attr]

    with pytest.raises(AppError) as error:
        await create_lot(
            session,
            user_a,
            farm_a.id,
            LoteAnimalCreate(especie_id=species_b.id, nombre="Lote B", cantidad=1),
        )
    assert error.value.status_code == 404

    assert await session.scalar(select(func.count()).select_from(Especie)) == 2


@pytest.mark.asyncio
async def test_contabilidad_anula_sin_borrar_y_calcula_flujo(session) -> None:  # type: ignore[no-untyped-def]
    user_id = uuid4()
    farm = await setup_farm(session, user_id, "Finca contable")
    expense = await create_expense(
        session,
        user_id,
        farm.id,
        GastoCreate(categoria="insumo", monto="10.25", fecha="2026-02-05T00:00:00Z"),
    )
    await cancel_expense(session, user_id, farm.id, expense.id, "Compra reversada")
    assert await session.get(type(expense), expense.id) is not None

    await create_income(
        session,
        user_id,
        farm.id,
        IngresoCreate(
            categoria="venta", cantidad="2", precio_unitario="20", fecha="2026-02-06T00:00:00Z"
        ),
    )
    flow = await cash_flow(session, user_id, farm.id, 2026, 2)
    assert flow["ingresos"] == 40
    assert flow["gastos"] == 0
    assert flow["saldo"] == 40


@pytest.mark.asyncio
async def test_venta_controla_disponibilidad_y_es_idempotente(session) -> None:  # type: ignore[no-untyped-def]
    user_id = uuid4()
    farm = await setup_farm(session, user_id, "Finca venta")
    harvest = Cosecha(
        finca_id=farm.id,
        ciclo_id=uuid4(),
        cantidad=Decimal("10"),
        unidad="kg",
        fecha=datetime(2026, 3, 1, tzinfo=UTC),
        creado_por=user_id,
    )
    session.add(harvest)
    await session.commit()
    data = VentaCreate(
        fecha="2026-03-02T00:00:00Z",
        lineas=[
            LineaVentaCreate(
                cosecha_id=harvest.id,
                categoria="primera",
                unidad="kg",
                cantidad="4",
                precio_unitario="12.50",
            )
        ],
    )
    first = await create_sale(session, user_id, farm.id, data, "sale-key")
    second = await create_sale(session, user_id, farm.id, data, "sale-key")
    assert str(first.id) == second["id"]  # type: ignore[union-attr]


@pytest.mark.asyncio
async def test_actividad_y_trabajador_crud_respetan_finca(session) -> None:  # type: ignore[no-untyped-def]
    user_a = uuid4()
    user_b = uuid4()
    farm_a = await setup_farm(session, user_a, "Finca A")
    farm_b = await setup_farm(session, user_b, "Finca B")
    cycle = await create_cycle(
        session,
        user_a,
        farm_a.id,
        CicloCreate(nombre="Ciclo A", fecha_inicio=datetime.now(UTC)),
    )
    activity = await create_activity(
        session,
        user_a,
        farm_a.id,
        ActividadCreate(
            ciclo_id=cycle.id,
            nombre="Siembra",
            fase="inicio",
            fecha_inicio=datetime.now(UTC),
            area_trabajada=Decimal("1.25"),
        ),
    )
    updated = await update_activity(
        session, user_a, farm_a.id, activity.id, ActividadUpdate(nombre="Siembra ajustada")
    )
    assert updated.nombre == "Siembra ajustada"
    worker = await create_worker(
        session,
        user_a,
        farm_a.id,
        TrabajadorCreate(nombre="Ana", tipo="fijo", jornal_habitual=Decimal("50")),
    )
    worker = await update_worker(
        session, user_a, farm_a.id, worker.id, TrabajadorUpdate(nombre="Ana 2")
    )
    assert worker.nombre == "Ana 2"
    with pytest.raises(AppError):
        await update_activity(
            session, user_b, farm_b.id, activity.id, ActividadUpdate(nombre="No permitido")
        )
    await deactivate_worker(session, user_a, farm_a.id, worker.id)
