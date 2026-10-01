"""Crea una base SQLite de ejemplo para probar la API en local, con un usuario por perfil.

Reinicia la base cada vez. Se niega a correr contra cualquier base que no sea SQLite.
La clave de las cuentas sale de AGRO_SEED_PASSWORD (archivo .env); no hay valor por defecto.

Uso: python -m scripts.demo
"""

import asyncio
import sys
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core import claves
from app.core.config import get_settings
from app.models import (
    Base,
    Ciclo,
    ConteoPlanta,
    Cultivo,
    CultivoRiesgo,
    EventoAdverso,
    Finca,
    FincaUsuario,
    Fuente,
    Lote,
    Manejo,
    Noticia,
    ProblemaSanitario,
    Riesgo,
    Siembra,
    Sintoma,
    Usuario,
)
from scripts.seed import cargar

ROLES = ("admin", "agricultor", "contador", "experto")
DIAS_DE_EJEMPLO = (30, 15, 120, 60, 20, 30)


async def main() -> int:
    ajustes = get_settings()
    if not ajustes.database_url.startswith("sqlite"):
        print("Este script solo corre contra SQLite. Cambie AGRO_DATABASE_URL a una base sqlite.")
        return 1
    if not ajustes.seed_password:
        print("Defina AGRO_SEED_PASSWORD en su .env (clave de las cuentas de ejemplo).")
        return 1

    motor = create_async_engine(ajustes.database_url)
    async with motor.begin() as conexion:
        await conexion.run_sync(Base.metadata.drop_all)
        await conexion.run_sync(Base.metadata.create_all)

    async with async_sessionmaker(motor, expire_on_commit=False)() as db:
        await cargar(db)
        clave_hash = claves.hashear(ajustes.seed_password)
        usuarios = {
            rol: Usuario(
                nombre=f"Usuario {rol}", correo=f"{rol}@demo.test", clave_hash=clave_hash, rol=rol
            )
            for rol in ROLES
        }
        db.add_all(usuarios.values())
        finca = Finca(
            nombre="Finca de ejemplo",
            departamento_dane="05",
            municipio_dane="05001",
            area_ha=Decimal("12"),
        )
        db.add(finca)
        await db.flush()
        for rol in ("admin", "agricultor", "contador"):
            db.add(FincaUsuario(finca_id=finca.id, usuario_id=usuarios[rol].id))
        lote = Lote(finca_id=finca.id, nombre="Lote 1", area_ha=Decimal("5"))
        db.add_all([lote, Lote(finca_id=finca.id, nombre="Lote 2", area_ha=Decimal("3"))])
        await db.flush()

        cafe = await db.scalar(select(Cultivo).where(Cultivo.nombre == "Café"))
        if cafe is None:
            raise RuntimeError("Faltan los cultivos iniciales.")
        # Días de ejemplo para el cronograma y los avisos; en serio los carga el equipo.
        for fase, dias in zip(cafe.fases, DIAS_DE_EJEMPLO, strict=False):
            fase.dias_estimados = dias
        siembra = Siembra(
            finca_id=finca.id,
            lote_id=lote.id,
            cultivo_id=cafe.id,
            metodo="semilla",
            area_ha=Decimal("2"),
            plantas_sembradas=4000,
            fecha_plan=date.today(),
            estado="en_curso",
        )
        db.add(siembra)
        await db.flush()
        db.add(
            Ciclo(
                siembra_id=siembra.id,
                tipo="levante",
                numero=1,
                estado="en_curso",
                fecha_inicio=date.today() - timedelta(days=40),
            )
        )
        db.add(
            ConteoPlanta(
                siembra_id=siembra.id,
                fecha=date.today() - timedelta(days=5),
                vivas=3820,
                muertas=180,
            )
        )
        helada = await db.scalar(select(Riesgo).where(Riesgo.nombre == "Helada"))
        if helada is None:
            raise RuntimeError("Faltan los riesgos iniciales.")
        db.add(
            CultivoRiesgo(
                cultivo_id=cafe.id,
                riesgo_id=helada.id,
                fase_critica="siembra",
                susceptibilidad="alta",
                medidas="Proteja las plantas jóvenes de la helada.",
            )
        )
        db.add(
            EventoAdverso(
                finca_id=finca.id,
                riesgo_id=helada.id,
                siembra_id=siembra.id,
                inicio=date.today() - timedelta(days=10),
                severidad="moderada",
                perdida_pct=Decimal("12"),
                perdida_estimada=Decimal("800000"),
            )
        )
        fuente = Fuente(nombre="Fuente de ejemplo", url="https://ejemplo.test/fuente")
        db.add(fuente)
        await db.flush()
        ficha = ProblemaSanitario(
            nombre="Manchas amarillas en la hoja",
            tipo="enfermedad",
            cultivo_id=cafe.id,
            estado="validado",
            causa="Ficha de ejemplo para probar el asistente.",
        )
        ficha.sintomas = [Sintoma(descripcion="manchas amarillas en las hojas")]
        ficha.manejos = [
            Manejo(
                tipo="cultural",
                descripcion="Retire las hojas afectadas y mejore la ventilación.",
                fuente_id=fuente.id,
            )
        ]
        db.add(ficha)
        ahora = datetime.now(UTC)
        db.add(
            Noticia(
                titulo="Alerta de lluvias en su región",
                resumen="Se esperan lluvias fuertes esta semana.",
                enlace="https://ejemplo.test/noticia",
                fuente="Fuente de ejemplo",
                region_dane="05",
                publicada=ahora,
                vigente_hasta=ahora + timedelta(days=7),
            )
        )
        await db.commit()
    await motor.dispose()
    print("Base de ejemplo lista. Cuentas (la clave es AGRO_SEED_PASSWORD de su .env):")
    for rol in ROLES:
        print(f"  {rol:11} {rol}@demo.test")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
