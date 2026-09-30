"""Asistente de consultas. Responde solo con fichas validadas; no inventa diagnósticos ni dosis.

La `coincidencia` mide qué tanto se parece lo que describe la persona a la ficha (palabras en
común). No es una probabilidad de acierto: por eso siempre se recomienda confirmar con un técnico.
"""

import re
import unicodedata
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.contexto import UsuarioActual
from app.core.exceptions import LimiteSuperado, NoEncontrado
from app.models.asistente import Consulta, Mensaje, Retroalimentacion
from app.models.conocimiento import ProblemaSanitario
from app.schemas.asistente import (
    CalidadSalida,
    CausaProbable,
    ConsultaCrear,
    ConsultaResumen,
    ConsultaSalida,
    RespuestaAsistente,
    RetroalimentacionEntrada,
    TratamientoValidado,
)
from app.services import siembra_service

settings = get_settings()

PALABRAS_VACIAS = {
    "tiene",
    "tienen",
    "esta",
    "estan",
    "mucho",
    "muchas",
    "muchos",
    "pero",
    "como",
    "cuando",
    "donde",
    "para",
    "porque",
    "desde",
    "hasta",
    "sobre",
    "entre",
    "tambien",
    "cada",
    "todo",
    "todos",
    "todas",
    "tengo",
    "hace",
    "hacen",
    "unas",
    "unos",
    "algunas",
    "algunos",
    "estoy",
}
AVISO = (
    "Es una orientación basada en fichas revisadas por expertos. No reemplaza a un técnico "
    "y no es un diagnóstico."
)
CUANDO_LLAMAR = (
    "Llame a un técnico agropecuario si el problema avanza rápido, afecta a muchas plantas "
    "o no mejora con las medidas de manejo."
)


def _palabras(texto: str) -> dict[str, str]:
    """Raíz de cada palabra significativa -> la palabra tal como la escribió la persona."""
    limpio = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    salida: dict[str, str] = {}
    for palabra in re.findall(r"[a-z0-9]{4,}", limpio):
        raiz = palabra.removesuffix("s") if len(palabra) > 4 else palabra
        if raiz not in PALABRAS_VACIAS and palabra not in PALABRAS_VACIAS:
            salida.setdefault(raiz, palabra)
    return salida


def _coincidencia(comunes: int, consulta: int, ficha: int) -> str | None:
    if not comunes or not consulta or not ficha:
        return None
    if comunes < min(2, consulta):
        return None
    puntaje = comunes / min(consulta, ficha)
    if puntaje >= 0.6:
        return "alta"
    if puntaje >= 0.35:
        return "media"
    return "baja" if puntaje >= 0.2 else None


async def _responder(db: AsyncSession, cultivo_id: uuid.UUID, texto: str) -> RespuestaAsistente:
    consulta = _palabras(texto)
    raices = set(consulta)
    fichas = await db.scalars(
        select(ProblemaSanitario).where(
            ProblemaSanitario.estado == "validado",
            (ProblemaSanitario.cultivo_id == cultivo_id) | ProblemaSanitario.cultivo_id.is_(None),
        )
    )
    orden = {"alta": 0, "media": 1, "baja": 2}
    candidatas: list[tuple[str, ProblemaSanitario, set[str]]] = []
    for ficha in fichas:
        base = _palabras(ficha.nombre + " " + " ".join(s.descripcion for s in ficha.sintomas))
        comunes = raices & set(base)
        nivel = _coincidencia(len(comunes), len(raices), len(base))
        if nivel:
            candidatas.append((nivel, ficha, comunes))
    candidatas.sort(key=lambda c: (orden[c[0]], c[1].nombre))
    top = candidatas[:3]

    causas = [
        CausaProbable(
            problema_id=f.id,
            problema=f.nombre,
            coincidencia=nivel,
            por_que="Coincide con lo que describe: "
            + ", ".join(sorted(consulta[r] for r in comunes))
            + ".",
            fuentes=sorted({m.fuente.nombre for m in f.manejos if m.fuente}),
        )
        for nivel, f, comunes in top
    ]
    que_hacer: list[str] = []
    tratamientos: list[TratamientoValidado] = []
    for _, f, _c in top:
        for m in f.manejos:
            if m.tipo in ("prevencion", "cultural") and m.descripcion not in que_hacer:
                que_hacer.append(m.descripcion)
            elif m.tipo in ("quimico", "veterinario") and m.producto_ica:
                tratamientos.append(
                    TratamientoValidado(
                        problema=f.nombre,
                        producto_ica=m.producto_ica,
                        descripcion=m.descripcion,
                        fuente=m.fuente.nombre if m.fuente else None,
                    )
                )
    if not top:
        return RespuestaAsistente(
            lo_que_entendi=texto,
            causas_probables=[],
            que_hacer=[],
            tratamientos=[],
            mensaje_tratamiento="No hay información validada para esta descripción.",
            cuando_llamar_al_tecnico=CUANDO_LLAMAR + " Consulte asistencia técnica para este caso.",
            aviso=AVISO,
            hay_informacion=False,
        )
    mensaje = (
        "Tratamientos con producto registrado y fuente, tal como están en la ficha."
        if tratamientos
        else (
            "Las fichas no traen tratamiento validado. "
            "Consulte a un técnico antes de aplicar productos."
        )
    )
    return RespuestaAsistente(
        lo_que_entendi=texto,
        causas_probables=causas,
        que_hacer=que_hacer,
        tratamientos=tratamientos,
        mensaje_tratamiento=mensaje,
        cuando_llamar_al_tecnico=CUANDO_LLAMAR,
        aviso=AVISO,
        hay_informacion=True,
    )


async def _consultas_de_hoy(db: AsyncSession, usuario_id: uuid.UUID) -> int:
    inicio = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    total = await db.scalar(
        select(func.count())
        .select_from(Consulta)
        .where(Consulta.usuario_id == usuario_id, Consulta.creado_en >= inicio)
    )
    return int(total or 0)


async def crear(db: AsyncSession, usuario: UsuarioActual, datos: ConsultaCrear) -> ConsultaSalida:
    siembra = await siembra_service.obtener(db, usuario, datos.siembra_id)
    if await _consultas_de_hoy(db, usuario.id) >= settings.consultas_por_dia:
        raise LimiteSuperado(
            "Llegó al máximo de consultas de hoy. Mañana podrá hacer más.", "LIMITE_DE_CONSULTAS"
        )
    respuesta = await _responder(db, siembra.cultivo_id, datos.texto)
    consulta = Consulta(
        usuario_id=usuario.id, contexto="siembra", contexto_id=siembra.id, creado_por=usuario.id
    )
    db.add(consulta)
    await db.flush()
    db.add(
        Mensaje(consulta_id=consulta.id, rol="usuario", texto=datos.texto, creado_por=usuario.id)
    )
    respuesta_msg = Mensaje(
        consulta_id=consulta.id,
        rol="asistente",
        texto=respuesta.mensaje_tratamiento,
        contenido=respuesta.model_dump(mode="json"),
    )
    db.add(respuesta_msg)
    await db.commit()
    return ConsultaSalida(
        id=consulta.id,
        contexto=consulta.contexto,
        contexto_id=consulta.contexto_id,
        creado_en=consulta.creado_en,
        pregunta=datos.texto,
        respuesta=respuesta,
        mensaje_respuesta_id=respuesta_msg.id,
        valoracion=None,
    )


async def _propia(db: AsyncSession, usuario: UsuarioActual, consulta_id: uuid.UUID) -> Consulta:
    consulta = await db.get(Consulta, consulta_id)
    if consulta is None or consulta.usuario_id != usuario.id:
        raise NoEncontrado("No encontramos esa consulta.", "CONSULTA_NO_ENCONTRADA")
    return consulta


async def _valoraciones(db: AsyncSession, consultas: list[uuid.UUID]) -> dict[uuid.UUID, str]:
    filas = await db.execute(
        select(Mensaje.consulta_id, Retroalimentacion.valor)
        .join(Retroalimentacion, Retroalimentacion.mensaje_id == Mensaje.id)
        .where(Mensaje.consulta_id.in_(consultas))
    )
    return {c: v for c, v in filas}


async def obtener(
    db: AsyncSession, usuario: UsuarioActual, consulta_id: uuid.UUID
) -> ConsultaSalida:
    consulta = await _propia(db, usuario, consulta_id)
    mensajes = list(
        await db.scalars(
            select(Mensaje).where(Mensaje.consulta_id == consulta.id).order_by(Mensaje.creado_en)
        )
    )
    pregunta = next(m for m in mensajes if m.rol == "usuario")
    respuesta = next(m for m in mensajes if m.rol == "asistente")
    valoracion = (await _valoraciones(db, [consulta.id])).get(consulta.id)
    return ConsultaSalida(
        id=consulta.id,
        contexto=consulta.contexto,
        contexto_id=consulta.contexto_id,
        creado_en=consulta.creado_en,
        pregunta=pregunta.texto,
        respuesta=RespuestaAsistente.model_validate(respuesta.contenido),
        mensaje_respuesta_id=respuesta.id,
        valoracion=valoracion,
    )


async def listar(
    db: AsyncSession, usuario: UsuarioActual, q: str | None, skip: int, limit: int
) -> tuple[list[ConsultaResumen], int]:
    base = select(Consulta).where(Consulta.usuario_id == usuario.id)
    if q:
        base = base.where(
            Consulta.id.in_(
                select(Mensaje.consulta_id).where(
                    Mensaje.rol == "usuario", Mensaje.texto.ilike(f"%{q}%")
                )
            )
        )
    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    consultas = list(
        await db.scalars(base.order_by(Consulta.creado_en.desc()).offset(skip).limit(limit))
    )
    ids = [c.id for c in consultas]
    preguntas: dict[uuid.UUID, str] = {}
    if ids:
        filas = await db.execute(
            select(Mensaje.consulta_id, Mensaje.texto).where(
                Mensaje.consulta_id.in_(ids), Mensaje.rol == "usuario"
            )
        )
        preguntas = {c: t for c, t in filas}
    valoraciones = await _valoraciones(db, ids) if ids else {}
    items = [
        ConsultaResumen(
            id=c.id,
            contexto_id=c.contexto_id,
            creado_en=c.creado_en,
            pregunta=preguntas.get(c.id, ""),
            valoracion=valoraciones.get(c.id),
        )
        for c in consultas
    ]
    return items, total


async def valorar(
    db: AsyncSession,
    usuario: UsuarioActual,
    consulta_id: uuid.UUID,
    datos: RetroalimentacionEntrada,
) -> Retroalimentacion:
    consulta = await _propia(db, usuario, consulta_id)
    respuesta = await db.scalar(
        select(Mensaje).where(Mensaje.consulta_id == consulta.id, Mensaje.rol == "asistente")
    )
    if respuesta is None:
        raise NoEncontrado("No encontramos la respuesta.", "CONSULTA_NO_ENCONTRADA")
    fila = await db.scalar(
        select(Retroalimentacion).where(Retroalimentacion.mensaje_id == respuesta.id)
    )
    if fila is None:
        fila = Retroalimentacion(mensaje_id=respuesta.id, creado_por=usuario.id, valor=datos.valor)
        db.add(fila)
    fila.valor = datos.valor
    fila.comentario = datos.comentario
    await db.commit()
    return fila


async def calidad(db: AsyncSession) -> CalidadSalida:
    consultas = await db.scalar(select(func.count()).select_from(Consulta)) or 0
    filas = await db.execute(
        select(Retroalimentacion.valor, func.count()).group_by(Retroalimentacion.valor)
    )
    por_valor = {v: n for v, n in filas}
    con = sum(por_valor.values())
    sirvieron = por_valor.get("sirvio", 0)
    return CalidadSalida(
        consultas=consultas,
        con_valoracion=con,
        sirvieron=sirvieron,
        no_sirvieron=por_valor.get("no_sirvio", 0),
        equivocadas=por_valor.get("equivocado", 0),
        porcentaje_que_sirvio=round(sirvieron / con * 100, 1) if con else None,
        aviso=None if con else "Aún no hay respuestas valoradas para medir.",
    )
