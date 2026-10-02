import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IdempotencyKey


async def cached_response(
    db: AsyncSession, key: str | None, operation: str
) -> dict[str, Any] | None:
    if not key:
        return None
    record = await db.scalar(
        select(IdempotencyKey).where(
            IdempotencyKey.clave == key, IdempotencyKey.operacion == operation
        )
    )
    return json.loads(record.respuesta) if record else None


async def save_response(
    db: AsyncSession, key: str | None, operation: str, response: dict[str, Any]
) -> None:
    if key:
        db.add(
            IdempotencyKey(
                clave=key,
                operacion=operation,
                respuesta=json.dumps(response, ensure_ascii=True, default=str),
            )
        )
