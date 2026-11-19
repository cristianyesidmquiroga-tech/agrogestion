from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.etiquetas import OPERACION
from app.dependencies import SoloLectura
from app.models import EtapaProceso
from app.schemas.listados import InsumoDetalle, JornalDetalle, ProcesoDetalle
from app.schemas.phase2 import EtapaResponse
from app.services.listados import list_etapas, list_insumos, list_jornales, list_procesos

router = APIRouter(tags=[OPERACION])


@router.get(
    "/fincas/{finca_id}/jornales",
    response_model=list[JornalDetalle],
    summary="Jornales de la finca, con quién trabajó y en qué labor",
)
async def jornal_list(
    finca_id: UUID,
    user: SoloLectura,
    estado: str | None = Query(default=None, pattern="^(pendiente|pagado)$"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    return await list_jornales(db, user.id, finca_id, estado)


@router.get(
    "/fincas/{finca_id}/insumos",
    response_model=list[InsumoDetalle],
    summary="Inventario de insumos con existencia y costo promedio",
)
async def supply_list(
    finca_id: UUID, user: SoloLectura, db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    return await list_insumos(db, user.id, finca_id)


@router.get(
    "/fincas/{finca_id}/procesos",
    response_model=list[ProcesoDetalle],
    summary="Procesos de transformación de la finca",
)
async def process_list(
    finca_id: UUID, user: SoloLectura, db: AsyncSession = Depends(get_db)
) -> list[dict[str, Any]]:
    return await list_procesos(db, user.id, finca_id)


@router.get(
    "/fincas/{finca_id}/procesos/{process_id}/etapas",
    response_model=list[EtapaResponse],
    summary="Etapas de un proceso",
)
async def stage_list(
    finca_id: UUID, process_id: UUID, user: SoloLectura, db: AsyncSession = Depends(get_db)
) -> list[EtapaProceso]:
    return await list_etapas(db, user.id, finca_id, process_id)
