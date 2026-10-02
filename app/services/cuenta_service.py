"""Glosario, política de tratamiento de datos y consentimiento del usuario."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from app.models.glosario import GlosarioTermino
from app.models.usuario import Consentimiento
from app.schemas.cuenta import ConsentimientoEntrada, PoliticaSalida

settings = get_settings()


async def glosario(db: AsyncSession, q: str | None) -> list[GlosarioTermino]:
    consulta = select(GlosarioTermino).order_by(GlosarioTermino.termino)
    if q:
        consulta = consulta.where(GlosarioTermino.termino.ilike(f"%{q}%"))
    return list(await db.scalars(consulta))


def politica() -> PoliticaSalida:
    return PoliticaSalida(
        version=settings.politica_version,
        estado="borrador",
        datos_que_usamos=[
            "Su nombre y correo, para identificarlo.",
            "El municipio de su finca y, solo si usted lo autoriza, su ubicación exacta.",
            "Los datos de sus cultivos, animales, trabajadores y dinero que usted registre.",
            "Las fotos que envíe al asistente, si lo autoriza.",
        ],
        para_que=[
            "Que pueda llevar la gestión de su finca.",
            "Mostrarle avisos de su región que lo afecten.",
            "Responder sus consultas con el asistente.",
        ],
        sus_derechos=[
            "Conocer, actualizar y corregir sus datos.",
            "Pedir que se borren sus datos y su cuenta.",
            "Retirar la autorización del asistente cuando quiera.",
        ],
    )


async def ultimo(db: AsyncSession, usuario_id: uuid.UUID) -> Consentimiento:
    fila = await db.scalar(
        select(Consentimiento)
        .where(Consentimiento.usuario_id == usuario_id)
        .order_by(Consentimiento.aceptado_en.desc())
        .limit(1)
    )
    if fila is None:
        raise NoEncontrado(
            "Aún no ha aceptado el tratamiento de datos.", "CONSENTIMIENTO_PENDIENTE"
        )
    return fila


async def registrar(
    db: AsyncSession, usuario_id: uuid.UUID, datos: ConsentimientoEntrada
) -> Consentimiento:
    if not datos.acepta_tratamiento:
        raise ReglaNegocio(
            "Sin aceptar el tratamiento de datos no se puede continuar.", "CONSENTIMIENTO_REQUERIDO"
        )
    if datos.version_politica != settings.politica_version:
        raise Conflicto(
            "La política cambió. Léala de nuevo antes de aceptar.", "POLITICA_DESACTUALIZADA"
        )
    fila = Consentimiento(
        usuario_id=usuario_id,
        version_politica=datos.version_politica,
        aceptado_en=datetime.now(UTC),
        acepta_transferencia_ia=datos.acepta_transferencia_ia,
        creado_por=usuario_id,
    )
    db.add(fila)
    await db.commit()
    return fila
