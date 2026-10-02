from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.exceptions import AppError
from app.models import Auditoria, Base, Finca, FincaUsuario, Gasto, IdempotencyKey, Usuario
from app.schemas.phase2 import ActividadCreate, CicloCreate, JornalCreate
from app.services.phase2 import create_activity, create_cycle, create_jornal, pay_jornal


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


async def _references(session, user_id, farm_id):  # type: ignore[no-untyped-def]
    cycle = await create_cycle(
        session, user_id, farm_id, CicloCreate(nombre="Ciclo", fecha_inicio=datetime.now(UTC))
    )
    activity = await create_activity(
        session,
        user_id,
        farm_id,
        ActividadCreate(
            ciclo_id=cycle.id,
            nombre="Labor",
            fase="inicio",
            fecha_inicio=datetime.now(UTC),
            area_trabajada=Decimal("1"),
        ),
    )
    return cycle, activity


@pytest.mark.asyncio
async def test_modalidades_declaradas_calculan_con_decimal(session) -> None:  # type: ignore[no-untyped-def]
    user_id = uuid4()
    farm = await setup_farm(session, user_id, "Finca modalidades")
    cycle, activity = await _references(session, user_id, farm.id)
    modalities = ("jornal", "destajo", "por_kilo", "contrato_global")
    for index, modality in enumerate(modalities):
        item = await create_jornal(
            session,
            user_id,
            farm.id,
            JornalCreate(
                actividad_id=activity.id,
                ciclo_id=cycle.id,
                fecha=datetime(2026, 1, 1, tzinfo=UTC) + timedelta(days=index),
                obreros=Decimal("2"),
                dias=Decimal("1.5"),
                valor_jornal=Decimal("10.25"),
                modalidad=modality,
            ),
        )
        assert item.total == Decimal("30.7500")


def test_jornal_rejects_unsupported_modality() -> None:
    with pytest.raises(ValidationError):
        JornalCreate(
            actividad_id=uuid4(),
            ciclo_id=uuid4(),
            fecha=datetime.now(UTC),
            obreros=1,
            dias=1,
            valor_jornal=10,
            modalidad="por_hora",
        )


@pytest.mark.asyncio
async def test_pago_con_misma_clave_no_duplica_gasto(session) -> None:  # type: ignore[no-untyped-def]
    user_id = uuid4()
    farm = await setup_farm(session, user_id, "Finca pago")
    cycle, activity = await _references(session, user_id, farm.id)
    jornal = await create_jornal(
        session,
        user_id,
        farm.id,
        JornalCreate(
            actividad_id=activity.id,
            ciclo_id=cycle.id,
            fecha=datetime(2026, 2, 1, tzinfo=UTC),
            obreros=1,
            dias=1,
            valor_jornal=Decimal("20"),
        ),
    )
    first = await pay_jornal(session, user_id, farm.id, jornal.id, "pay-key")
    second = await pay_jornal(session, user_id, farm.id, jornal.id, "pay-key")
    assert str(first.id) == second["id"]  # type: ignore[union-attr]
    assert (
        await session.scalar(
            select(func.count()).select_from(Gasto).where(Gasto.origen_id == jornal.id)
        )
        == 1
    )
    assert (
        await session.scalar(
            select(func.count())
            .select_from(Auditoria)
            .where(Auditoria.recurso_id == str(jornal.id), Auditoria.operacion == "pago")
        )
        == 1
    )
    assert (
        await session.scalar(
            select(func.count())
            .select_from(IdempotencyKey)
            .where(IdempotencyKey.clave == "pay-key")
        )
        == 1
    )


@pytest.mark.asyncio
async def test_jornal_no_cruza_fincas(session) -> None:  # type: ignore[no-untyped-def]
    user_a, user_b = uuid4(), uuid4()
    farm_a = await setup_farm(session, user_a, "A")
    farm_b = await setup_farm(session, user_b, "B")
    cycle_b, activity_b = await _references(session, user_b, farm_b.id)
    with pytest.raises(AppError) as error:
        await create_jornal(
            session,
            user_a,
            farm_a.id,
            JornalCreate(
                actividad_id=activity_b.id,
                ciclo_id=cycle_b.id,
                fecha=datetime.now(UTC),
                obreros=1,
                dias=1,
                valor_jornal=10,
            ),
        )
    assert error.value.status_code == 400
