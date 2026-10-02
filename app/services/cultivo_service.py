import uuid

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import Conflicto, NoEncontrado
from app.models.cultivo import Cultivo, CultivoDosis, CultivoFase, CultivoMetodo
from app.models.riesgo import CultivoRiesgo, Riesgo
from app.schemas.cultivo import (
    CultivoActualizar,
    CultivoBase,
    CultivoCrear,
    CultivoRiesgoEntrada,
    RiesgoCrear,
)


async def listar(
    db: AsyncSession, q: str | None, tipo_ciclo: str | None, skip: int, limit: int
) -> tuple[list[Cultivo], int]:
    filtros: list[ColumnElement[bool]] = []
    if q:
        filtros.append(Cultivo.nombre.ilike(f"%{q}%"))
    if tipo_ciclo:
        filtros.append(Cultivo.tipo_ciclo == tipo_ciclo)
    total = await db.scalar(select(func.count()).select_from(Cultivo).where(*filtros)) or 0
    filas = await db.scalars(
        select(Cultivo).where(*filtros).order_by(Cultivo.nombre).offset(skip).limit(limit)
    )
    return list(filas), total


async def obtener(db: AsyncSession, cultivo_id: uuid.UUID) -> Cultivo:
    cultivo = await db.get(Cultivo, cultivo_id)
    if cultivo is None:
        raise NoEncontrado("No encontramos ese cultivo.", "CULTIVO_NO_ENCONTRADO")
    return cultivo


async def _nombre_libre(db: AsyncSession, nombre: str, excepto: uuid.UUID | None = None) -> None:
    consulta = select(Cultivo.id).where(func.lower(Cultivo.nombre) == nombre.lower())
    if excepto:
        consulta = consulta.where(Cultivo.id != excepto)
    if await db.scalar(consulta):
        raise Conflicto("Ya existe un cultivo con ese nombre.", "CULTIVO_DUPLICADO")


def _aplicar(cultivo: Cultivo, datos: CultivoBase) -> None:
    for campo in (
        "nombre",
        "nombre_cientifico",
        "grupo",
        "tipo_ciclo",
        "unidad_conteo",
        "tipo_renovacion",
        "unidad_cosecha",
        "pago_cosecha_sugerido",
        "densidad_ref",
        "meses_primera_cosecha",
        "cosechas_por_anio",
        "por_validar",
        "fuente",
    ):
        setattr(cultivo, campo, getattr(datos, campo))
    cultivo.fases = [CultivoFase(**f.model_dump()) for f in datos.fases]
    cultivo.metodos = [CultivoMetodo(**m.model_dump()) for m in datos.metodos]
    cultivo.dosis = [CultivoDosis(**d.model_dump()) for d in datos.dosis]


async def crear(db: AsyncSession, datos: CultivoCrear, usuario_id: uuid.UUID) -> Cultivo:
    await _nombre_libre(db, datos.nombre)
    cultivo = Cultivo(creado_por=usuario_id)
    _aplicar(cultivo, datos)
    if datos.copiar_de:
        origen = await obtener(db, datos.copiar_de)
        if not datos.fases:
            cultivo.fases = [
                CultivoFase(
                    fase=f.fase, orden=f.orden, dias_estimados=f.dias_estimados, por_validar=True
                )
                for f in origen.fases
            ]
        if not datos.metodos:
            cultivo.metodos = [
                CultivoMetodo(
                    metodo=m.metodo,
                    dias_germinacion=m.dias_germinacion,
                    dias_vivero=m.dias_vivero,
                    por_validar=True,
                )
                for m in origen.metodos
            ]
        if not datos.dosis:
            cultivo.dosis = [
                CultivoDosis(
                    insumo_tipo=d.insumo_tipo,
                    dosis=d.dosis,
                    unidad=d.unidad,
                    base=d.base,
                    por_validar=True,
                )
                for d in origen.dosis
            ]
    db.add(cultivo)
    await db.commit()
    return cultivo


async def actualizar(db: AsyncSession, cultivo_id: uuid.UUID, datos: CultivoActualizar) -> Cultivo:
    cultivo = await obtener(db, cultivo_id)
    await _nombre_libre(db, datos.nombre, excepto=cultivo_id)
    cultivo.fases.clear()
    cultivo.metodos.clear()
    cultivo.dosis.clear()
    await db.flush()
    _aplicar(cultivo, datos)
    await db.commit()
    return cultivo


async def listar_riesgos(db: AsyncSession) -> list[Riesgo]:
    return list(await db.scalars(select(Riesgo).order_by(Riesgo.nombre)))


async def crear_riesgo(db: AsyncSession, datos: RiesgoCrear, usuario_id: uuid.UUID) -> Riesgo:
    if await db.scalar(select(Riesgo.id).where(func.lower(Riesgo.nombre) == datos.nombre.lower())):
        raise Conflicto("Ya existe un riesgo con ese nombre.", "RIESGO_DUPLICADO")
    riesgo = Riesgo(
        nombre=datos.nombre, tipo=datos.tipo, aplica_a=datos.aplica_a, creado_por=usuario_id
    )
    db.add(riesgo)
    await db.commit()
    return riesgo


async def riesgos_del_cultivo(db: AsyncSession, cultivo_id: uuid.UUID) -> list[CultivoRiesgo]:
    await obtener(db, cultivo_id)
    return list(
        await db.scalars(select(CultivoRiesgo).where(CultivoRiesgo.cultivo_id == cultivo_id))
    )


async def reemplazar_riesgos(
    db: AsyncSession, cultivo_id: uuid.UUID, datos: list[CultivoRiesgoEntrada]
) -> list[CultivoRiesgo]:
    await obtener(db, cultivo_id)
    ids = {d.riesgo_id for d in datos}
    existentes = (
        set(await db.scalars(select(Riesgo.id).where(Riesgo.id.in_(ids)))) if ids else set()
    )
    if ids - existentes:
        raise NoEncontrado("Uno de los riesgos no existe.", "RIESGO_NO_ENCONTRADO")
    claves = {(d.riesgo_id, d.fase_critica) for d in datos}
    if len(claves) != len(datos):
        raise Conflicto("Un riesgo no puede repetirse en la misma fase.", "RIESGO_REPETIDO")
    for anterior in await riesgos_del_cultivo(db, cultivo_id):
        await db.delete(anterior)
    nuevos = [CultivoRiesgo(cultivo_id=cultivo_id, **d.model_dump()) for d in datos]
    db.add_all(nuevos)
    await db.commit()
    return nuevos
