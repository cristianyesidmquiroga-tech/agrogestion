from uuid import UUID

from fastapi import APIRouter, Depends, Header, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.etiquetas import PECUARIO
from app.core.exceptions import AppError
from app.dependencies import current_user, require_role
from app.models import (
    AlertaRegional,
    AlimentacionAnimal,
    Animal,
    Especie,
    EventoAnimal,
    FuenteAlerta,
    LoteAnimal,
    ProduccionAnimal,
    Usuario,
)
from app.schemas.pecuario import (
    AlertaCreate,
    AlertaResponse,
    AlimentacionCreate,
    AlimentacionResponse,
    AnimalCreate,
    AnimalResponse,
    EspecieCreate,
    EspecieResponse,
    EventoCreate,
    EventoResponse,
    FuenteCreate,
    LoteAnimalCreate,
    LoteAnimalResponse,
    ProduccionCreate,
    ProduccionResponse,
)
from app.services.idempotency import cached_response, save_response
from app.services.pecuario import (
    active_alerts,
    create_animal,
    create_event,
    create_feed,
    create_lot,
    create_production,
    create_species,
    fetch_alert_source,
    list_pecuario,
    validate_external_url,
)

router = APIRouter(tags=[PECUARIO])


@router.get("/fincas/{finca_id}/especies", response_model=list[EspecieResponse])
async def species_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[Especie]:
    return await list_pecuario(db, user.id, finca_id, Especie)


@router.get("/fincas/{finca_id}/lotes-animales", response_model=list[LoteAnimalResponse])
async def lot_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[LoteAnimal]:
    return await list_pecuario(db, user.id, finca_id, LoteAnimal)


@router.get("/fincas/{finca_id}/animales", response_model=list[AnimalResponse])
async def animal_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[Animal]:
    return await list_pecuario(db, user.id, finca_id, Animal)


@router.get("/fincas/{finca_id}/eventos-animales", response_model=list[EventoResponse])
async def event_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[EventoAnimal]:
    return await list_pecuario(db, user.id, finca_id, EventoAnimal)


@router.get("/fincas/{finca_id}/produccion-animal", response_model=list[ProduccionResponse])
async def production_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[ProduccionAnimal]:
    return await list_pecuario(db, user.id, finca_id, ProduccionAnimal)


@router.get("/fincas/{finca_id}/alimentacion-animal", response_model=list[AlimentacionResponse])
async def feed_list(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[AlimentacionAnimal]:
    return await list_pecuario(db, user.id, finca_id, AlimentacionAnimal)


@router.post(
    "/fincas/{finca_id}/especies",
    response_model=EspecieResponse,
    status_code=status.HTTP_201_CREATED,
)
async def species_route(
    finca_id: UUID,
    data: EspecieCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> Especie:
    return await create_species(db, user.id, finca_id, data)


@router.post(
    "/fincas/{finca_id}/lotes-animales",
    response_model=LoteAnimalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def lot_route(
    finca_id: UUID,
    data: LoteAnimalCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
) -> LoteAnimal:
    return await create_lot(db, user.id, finca_id, data)


@router.post(
    "/fincas/{finca_id}/animales",
    response_model=AnimalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def animal_route(
    finca_id: UUID,
    data: AnimalCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> Animal:
    return await create_animal(db, user.id, finca_id, data, key)  # type: ignore[return-value]


@router.post(
    "/fincas/{finca_id}/eventos-animales",
    response_model=EventoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def event_route(
    finca_id: UUID,
    data: EventoCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> EventoAnimal:
    return await create_event(db, user.id, finca_id, data, key)  # type: ignore[return-value]


@router.post(
    "/fincas/{finca_id}/produccion-animal",
    response_model=ProduccionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def production_route(
    finca_id: UUID,
    data: ProduccionCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ProduccionAnimal:
    return await create_production(db, user.id, finca_id, data, key)  # type: ignore[return-value]


@router.post(
    "/fincas/{finca_id}/alimentacion-animal",
    response_model=AlimentacionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def feed_route(
    finca_id: UUID,
    data: AlimentacionCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(current_user),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> AlimentacionAnimal:
    return await create_feed(db, user.id, finca_id, data, key)  # type: ignore[return-value]


@router.get("/fincas/{finca_id}/alertas", response_model=list[AlertaResponse])
async def alerts_route(
    finca_id: UUID, db: AsyncSession = Depends(get_db), user: Usuario = Depends(current_user)
) -> list[AlertaRegional]:
    return await active_alerts(db, user.id, finca_id)


@router.post("/alertas/fuentes", status_code=status.HTTP_201_CREATED)
async def source_route(
    data: FuenteCreate,
    db: AsyncSession = Depends(get_db),
    _: Usuario = Depends(require_role("admin")),
) -> dict[str, object]:
    validate_external_url(data.url)
    source = FuenteAlerta(nombre=data.nombre, url=data.url)
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return {"id": source.id, "nombre": source.nombre, "url": source.url}


@router.post(
    "/fincas/{finca_id}/alertas", response_model=AlertaResponse, status_code=status.HTTP_201_CREATED
)
async def alert_route(
    finca_id: UUID,
    data: AlertaCreate,
    db: AsyncSession = Depends(get_db),
    user: Usuario = Depends(require_role("admin", "agricultor")),
    key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> AlertaRegional:
    from app.services.lands import user_finca

    await user_finca(db, user.id, finca_id)
    operation = f"alerta_regional:{finca_id}:{user.id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached  # type: ignore[return-value]
    if not await db.get(FuenteAlerta, data.fuente_id):
        raise AppError(404, "FUENTE_NO_ENCONTRADA", "La fuente no existe.")
    alert = AlertaRegional(finca_id=finca_id, **data.model_dump())
    db.add(alert)
    await db.flush()
    await save_response(db, key, operation, jsonable_encoder(alert))
    await db.commit()
    await db.refresh(alert)
    return alert


@router.post("/alertas/fuentes/{source_id}/sincronizar")
async def sync_route(
    source_id: UUID, db: AsyncSession = Depends(get_db), _: Usuario = Depends(require_role("admin"))
) -> list[dict[str, str]]:
    return await fetch_alert_source(db, source_id)
