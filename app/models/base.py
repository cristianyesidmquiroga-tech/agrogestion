"""Base declarativa y columnas comunes de todas las tablas."""

import uuid
from datetime import UTC, datetime
from typing import get_args

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, MetaData, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

CONVENCION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def ahora() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENCION)


class ColumnasComunes:
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=ahora)
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=ahora, onupdate=ahora
    )

    @declared_attr
    def creado_por(cls) -> Mapped[uuid.UUID | None]:  # noqa: N805
        return mapped_column(Uuid, ForeignKey("usuario.id"), nullable=True)


def check_en(columna: str, valores: object) -> CheckConstraint:
    lista = ", ".join(f"'{v}'" for v in get_args(valores))
    return CheckConstraint(f"{columna} IN ({lista})", name=f"{columna}_valido")
