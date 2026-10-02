from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Auditoria


async def record_audit(
    db: AsyncSession,
    operation: str,
    resource: str,
    user_id: UUID | None = None,
    finca_id: UUID | None = None,
    resource_id: UUID | None = None,
) -> None:
    db.add(
        Auditoria(
            usuario_id=user_id,
            finca_id=finca_id,
            operacion=operation,
            recurso=resource,
            recurso_id=str(resource_id) if resource_id else None,
        )
    )
