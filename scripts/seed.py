"""Carga los datos iniciales. Se puede repetir: solo agrega lo que falta.

Uso: python -m scripts.seed
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Cultivo, CultivoFase, CultivoMetodo, GlosarioTermino, Riesgo
from scripts.datos_iniciales import (
    CULTIVOS,
    FASES_FORESTAL,
    FASES_PERMANENTE,
    FASES_TRANSITORIO,
    GLOSARIO,
    RIESGOS,
)

FUENTE = "Estructura inicial del equipo; valores por validar"


def _fases(tipo_ciclo: str) -> tuple[str, ...]:
    if tipo_ciclo == "transitorio":
        return FASES_TRANSITORIO
    return FASES_FORESTAL if tipo_ciclo == "forestal" else FASES_PERMANENTE


async def cargar(db: AsyncSession) -> dict[str, int]:
    existentes = {
        "cultivos": set(await db.scalars(select(Cultivo.nombre))),
        "riesgos": set(await db.scalars(select(Riesgo.nombre))),
        "glosario": set(await db.scalars(select(GlosarioTermino.termino))),
    }
    nuevos = {"cultivos": 0, "riesgos": 0, "glosario": 0}

    for nombre, grupo, tipo, conteo, renovacion, unidad, pago, metodos in CULTIVOS:
        if nombre in existentes["cultivos"]:
            continue
        cultivo = Cultivo(
            nombre=nombre,
            grupo=grupo,
            tipo_ciclo=tipo,
            unidad_conteo=conteo,
            tipo_renovacion=renovacion,
            unidad_cosecha=unidad,
            pago_cosecha_sugerido=pago,
            por_validar=True,
            fuente=FUENTE,
        )
        cultivo.fases = [
            CultivoFase(fase=f, orden=i, por_validar=True) for i, f in enumerate(_fases(tipo), 1)
        ]
        cultivo.metodos = [CultivoMetodo(metodo=m, por_validar=True) for m in metodos]
        db.add(cultivo)
        nuevos["cultivos"] += 1

    for nombre, tipo in RIESGOS:
        if nombre not in existentes["riesgos"]:
            db.add(
                Riesgo(nombre=nombre, tipo=tipo, aplica_a="ambos" if tipo == "clima" else "cultivo")
            )
            nuevos["riesgos"] += 1

    for termino, explicacion, categoria in GLOSARIO:
        if termino not in existentes["glosario"]:
            db.add(GlosarioTermino(termino=termino, explicacion=explicacion, categoria=categoria))
            nuevos["glosario"] += 1

    await db.commit()
    return nuevos


async def main() -> None:
    from app.core.database import get_sessionmaker

    async with get_sessionmaker()() as db:
        print(await cargar(db))


if __name__ == "__main__":
    asyncio.run(main())
