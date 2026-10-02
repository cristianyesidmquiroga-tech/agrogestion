"""Consultas al asistente, sus mensajes y la valoración de cada respuesta."""

import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalogos import ValorRetroalimentacion
from app.models.base import Base, ColumnasComunes, check_en


class Consulta(ColumnasComunes, Base):
    __tablename__ = "consulta"

    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("usuario.id"), index=True)
    contexto: Mapped[str] = mapped_column(String(12))
    contexto_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    estado: Mapped[str] = mapped_column(String(10), default="respondida")


class Mensaje(ColumnasComunes, Base):
    __tablename__ = "mensaje"

    consulta_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("consulta.id"), index=True)
    rol: Mapped[str] = mapped_column(String(10))
    texto: Mapped[str] = mapped_column(Text)
    contenido: Mapped[dict[str, Any] | None] = mapped_column(JSON)


class Retroalimentacion(ColumnasComunes, Base):
    __tablename__ = "retroalimentacion"
    __table_args__ = (check_en("valor", ValorRetroalimentacion),)

    mensaje_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("mensaje.id"), unique=True)
    valor: Mapped[str] = mapped_column(String(12))
    comentario: Mapped[str | None] = mapped_column(Text)
