from fastapi import APIRouter

from app.core.etiquetas import OPERACION
from app.dependencies import SoloLectura
from app.routers.dependencias import BD
from app.schemas.proyeccion import ProyeccionAgricolaEntrada, ProyeccionAgricolaSalida
from app.services import proyeccion_service

router = APIRouter(tags=[OPERACION])


@router.post(
    "/proyecciones/agricola",
    response_model=ProyeccionAgricolaSalida,
    summary="Calcular proyección agrícola",
)
async def proyeccion_agricola(
    db: BD, _: SoloLectura, datos: ProyeccionAgricolaEntrada
) -> ProyeccionAgricolaSalida:
    """Calcula una proyección de costos e ingresos para un área y cultivo dados."""
    return await proyeccion_service.calcular_proyeccion_agricola(db, datos)
