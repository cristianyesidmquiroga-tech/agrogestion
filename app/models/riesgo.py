import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalogos import AplicaA, Severidad, Susceptibilidad, TipoRiesgo
from app.models.base import Base, ColumnasComunes, check_en


class Riesgo(ColumnasComunes, Base):
    __tablename__ = "riesgo"
    __table_args__ = (check_en("tipo", TipoRiesgo), check_en("aplica_a", AplicaA))

    nombre: Mapped[str] = mapped_column(String(60), unique=True)
    tipo: Mapped[str] = mapped_column(String(12))
    aplica_a: Mapped[str] = mapped_column(String(8))


class CultivoRiesgo(ColumnasComunes, Base):
    __tablename__ = "cultivo_riesgo"
    __table_args__ = (
        UniqueConstraint("cultivo_id", "riesgo_id", "fase_critica"),
        check_en("susceptibilidad", Susceptibilidad),
    )

    cultivo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cultivo.id"), index=True)
    riesgo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("riesgo.id"))
    fase_critica: Mapped[str | None] = mapped_column(String(24))
    susceptibilidad: Mapped[str] = mapped_column(String(8))
    medidas: Mapped[str | None] = mapped_column(Text)
    por_validar: Mapped[bool] = mapped_column(Boolean, default=True)


class EventoAdverso(ColumnasComunes, Base):
    __tablename__ = "evento_adverso"
    __table_args__ = (
        check_en("severidad", Severidad),
        CheckConstraint(
            "perdida_pct IS NULL OR (perdida_pct >= 0 AND perdida_pct <= 100)",
            name="perdida_pct_rango",
        ),
    )

    finca_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("finca.id"), index=True)
    riesgo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("riesgo.id"))
    siembra_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("siembra.id"))
    ciclo_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("ciclo.id"))
    lote_animal_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    inicio: Mapped[date] = mapped_column(Date)
    fin: Mapped[date | None] = mapped_column(Date)
    severidad: Mapped[str] = mapped_column(String(10))
    area_afectada: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    perdida_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    perdida_estimada: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    notas: Mapped[str | None] = mapped_column(Text)
