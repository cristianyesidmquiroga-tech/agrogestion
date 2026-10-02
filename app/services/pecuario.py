import ipaddress
import socket
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

import httpx
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models import (
    AlertaRegional,
    AlimentacionAnimal,
    Animal,
    Especie,
    EventoAnimal,
    FuenteAlerta,
    Gasto,
    LoteAnimal,
    ProduccionAnimal,
)
from app.services.audit import record_audit
from app.services.idempotency import cached_response, save_response
from app.services.lands import user_finca


async def _finca(db: AsyncSession, user_id: UUID, finca_id: UUID) -> None:
    await user_finca(db, user_id, finca_id)


async def create_species(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> Especie:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    item = Especie(finca_id=finca_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_lot(db: AsyncSession, user_id: UUID, finca_id: UUID, data) -> LoteAnimal:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    species = await db.scalar(
        select(Especie).where(Especie.id == data.especie_id, Especie.finca_id == finca_id)
    )
    if not species:
        raise AppError(404, "ESPECIE_NO_ENCONTRADA", "La especie no pertenece a la finca.")
    item = LoteAnimal(finca_id=finca_id, **data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def create_animal(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, key: str | None = None
) -> Animal | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"animal:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    species = await db.scalar(
        select(Especie).where(Especie.id == data.especie_id, Especie.finca_id == finca_id)
    )
    if not species:
        raise AppError(404, "ESPECIE_NO_ENCONTRADA", "La especie no pertenece a la finca.")
    if data.lote_animal_id and not await db.scalar(
        select(LoteAnimal).where(
            LoteAnimal.id == data.lote_animal_id, LoteAnimal.finca_id == finca_id
        )
    ):
        raise AppError(404, "LOTE_NO_ENCONTRADO", "El lote no pertenece a la finca.")
    item = Animal(finca_id=finca_id, estado="activo", **data.model_dump())
    db.add(item)
    await db.flush()
    await record_audit(db, "creacion", "animal", user_id, finca_id, item.id)
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


async def create_event(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, key: str | None = None
) -> EventoAnimal | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"evento_animal:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    if data.animal_id and not await db.scalar(
        select(Animal).where(Animal.id == data.animal_id, Animal.finca_id == finca_id)
    ):
        raise AppError(404, "ANIMAL_NO_ENCONTRADO", "El animal no pertenece a la finca.")
    if data.lote_animal_id and not await db.scalar(
        select(LoteAnimal).where(
            LoteAnimal.id == data.lote_animal_id, LoteAnimal.finca_id == finca_id
        )
    ):
        raise AppError(404, "LOTE_NO_ENCONTRADO", "El lote no pertenece a la finca.")
    item = EventoAnimal(finca_id=finca_id, creado_por=user_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await record_audit(db, "creacion", "evento_animal", user_id, finca_id, item.id)
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


async def create_production(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, key: str | None = None
) -> ProduccionAnimal | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"produccion_animal:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    if not await db.scalar(
        select(LoteAnimal).where(
            LoteAnimal.id == data.lote_animal_id, LoteAnimal.finca_id == finca_id
        )
    ):
        raise AppError(404, "LOTE_NO_ENCONTRADO", "El lote no pertenece a la finca.")
    item = ProduccionAnimal(finca_id=finca_id, creado_por=user_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


async def create_feed(
    db: AsyncSession, user_id: UUID, finca_id: UUID, data: Any, key: str | None = None
) -> AlimentacionAnimal | dict[str, object]:
    await _finca(db, user_id, finca_id)
    operation = f"alimentacion_animal:{finca_id}:{user_id}"
    cached = await cached_response(db, key, operation)
    if cached:
        return cached
    if not await db.scalar(
        select(LoteAnimal).where(
            LoteAnimal.id == data.lote_animal_id, LoteAnimal.finca_id == finca_id
        )
    ):
        raise AppError(404, "LOTE_NO_ENCONTRADO", "El lote no pertenece a la finca.")
    item = AlimentacionAnimal(finca_id=finca_id, creado_por=user_id, **data.model_dump())
    db.add(item)
    await db.flush()
    db.add(
        Gasto(
            finca_id=finca_id,
            categoria="alimentacion_animal",
            monto=data.costo,
            fecha=data.fecha,
            origen_tipo="alimentacion_animal",
            origen_id=item.id,
        )
    )
    await record_audit(db, "creacion", "alimentacion_animal", user_id, finca_id, item.id)
    await save_response(db, key, operation, jsonable_encoder(item))
    await db.commit()
    await db.refresh(item)
    return item


def validate_external_url(url: str) -> None:
    parsed = urlparse(url)
    allowed = get_settings().allowed_alert_hosts
    if parsed.scheme != "https" or not parsed.hostname or parsed.hostname.lower() not in allowed:
        raise AppError(400, "FUENTE_NO_AUTORIZADA", "La fuente no está autorizada.")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        if any(
            ipaddress.ip_address(address[4][0]).is_private
            or ipaddress.ip_address(address[4][0]).is_loopback
            for address in addresses
        ):
            raise AppError(400, "FUENTE_NO_AUTORIZADA", "La fuente no está autorizada.")
    except socket.gaierror as exc:
        raise AppError(400, "FUENTE_NO_DISPONIBLE", "No se pudo validar la fuente.") from exc


async def fetch_alert_source(db: AsyncSession, source_id: UUID) -> list[dict[str, str]]:
    source = await db.get(FuenteAlerta, source_id)
    if not source or not source.activa:
        raise AppError(404, "FUENTE_NO_ENCONTRADA", "La fuente no está disponible.")
    validate_external_url(source.url)
    try:
        async with httpx.AsyncClient(timeout=5, follow_redirects=False) as client:
            response = await client.get(source.url)
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("formato")
        return [item for item in payload if isinstance(item, dict)]
    except (httpx.HTTPError, ValueError) as exc:
        source.ultimo_error = datetime.now(UTC)
        await db.commit()
        raise AppError(
            502, "FUENTE_NO_DISPONIBLE", "La fuente externa no respondió correctamente."
        ) from exc


async def active_alerts(db: AsyncSession, user_id: UUID, finca_id: UUID) -> list[AlertaRegional]:
    await _finca(db, user_id, finca_id)
    now = datetime.now(UTC)
    result = await db.scalars(
        select(AlertaRegional).where(
            AlertaRegional.finca_id == finca_id,
            AlertaRegional.vigente_desde <= now,
            AlertaRegional.vigente_hasta >= now,
        )
    )
    return list(result)


async def list_pecuario(db: AsyncSession, user_id: UUID, finca_id: UUID, model) -> list[Any]:  # type: ignore[no-untyped-def]
    await _finca(db, user_id, finca_id)
    result = await db.scalars(select(model).where(model.finca_id == finca_id))
    return list(result)
