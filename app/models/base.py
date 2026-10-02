import uuid
from datetime import UTC, datetime
from typing import get_args

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.models.entities import Base

__all__ = ["Base", "ColumnasComunes", "ahora", "check_en"]


def ahora() -> datetime:
    return datetime.now(UTC)


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
