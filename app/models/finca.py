import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    LargeBinary,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ColumnasComunes, ahora


class Finca(ColumnasComunes, Base):
    __tablename__ = "finca"
    __table_args__ = (CheckConstraint("area_ha > 0", name="area_positiva"),)

    nombre: Mapped[str] = mapped_column(String(120))
    departamento_dane: Mapped[str] = mapped_column(String(2))
    municipio_dane: Mapped[str] = mapped_column(String(5))
    area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    ubicacion_cifrada: Mapped[bytes | None] = mapped_column(LargeBinary)


class FincaUsuario(Base):
    __tablename__ = "finca_usuario"

    finca_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("finca.id"), primary_key=True)
    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("usuario.id"), primary_key=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)


class Lote(ColumnasComunes, Base):
    __tablename__ = "lote"
    __table_args__ = (
        CheckConstraint("area_ha > 0", name="area_positiva"),
        UniqueConstraint("finca_id", "nombre"),
    )

    finca_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("finca.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(80))
    area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    notas: Mapped[str | None] = mapped_column(String(500))
