"""Base de conocimiento: problemas sanitarios con sus síntomas, manejo y fuentes."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.catalogos import EstadoConocimiento, TipoManejo, TipoProblema
from app.models.base import Base, ColumnasComunes, check_en


class Fuente(ColumnasComunes, Base):
    __tablename__ = "fuente"

    nombre: Mapped[str] = mapped_column(String(120))
    url: Mapped[str | None] = mapped_column(String(255))
    fecha: Mapped[date | None] = mapped_column(Date)
    licencia: Mapped[str | None] = mapped_column(String(80))


class ProblemaSanitario(ColumnasComunes, Base):
    __tablename__ = "problema_sanitario"
    __table_args__ = (check_en("tipo", TipoProblema), check_en("estado", EstadoConocimiento))

    nombre: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[str] = mapped_column(String(16))
    cultivo_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("cultivo.id"), index=True)
    especie_id: Mapped[uuid.UUID | None] = mapped_column(Uuid)
    causa: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(10), default="borrador")

    sintomas: Mapped[list["Sintoma"]] = relationship(
        back_populates="problema", cascade="all, delete-orphan", lazy="selectin"
    )
    manejos: Mapped[list["Manejo"]] = relationship(
        back_populates="problema", cascade="all, delete-orphan", lazy="selectin"
    )
    validaciones: Mapped[list["Validacion"]] = relationship(
        back_populates="problema", lazy="selectin", order_by="Validacion.creado_en"
    )


class Sintoma(ColumnasComunes, Base):
    __tablename__ = "sintoma"

    problema_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problema_sanitario.id"), index=True
    )
    descripcion: Mapped[str] = mapped_column(Text)
    parte: Mapped[str | None] = mapped_column(String(30))
    fase_o_edad: Mapped[str | None] = mapped_column(String(30))

    problema: Mapped[ProblemaSanitario] = relationship(back_populates="sintomas")


class Manejo(ColumnasComunes, Base):
    __tablename__ = "manejo"
    __table_args__ = (check_en("tipo", TipoManejo),)

    problema_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problema_sanitario.id"), index=True
    )
    tipo: Mapped[str] = mapped_column(String(12))
    descripcion: Mapped[str] = mapped_column(Text)
    producto_ica: Mapped[str | None] = mapped_column(String(120))
    fuente_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("fuente.id"))

    problema: Mapped[ProblemaSanitario] = relationship(back_populates="manejos")
    fuente: Mapped[Fuente | None] = relationship(lazy="selectin")


class Validacion(ColumnasComunes, Base):
    __tablename__ = "validacion"
    __table_args__ = (check_en("estado", EstadoConocimiento),)

    problema_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("problema_sanitario.id"), index=True
    )
    experto_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("usuario.id"))
    estado: Mapped[str] = mapped_column(String(10))
    observacion: Mapped[str | None] = mapped_column(Text)

    problema: Mapped[ProblemaSanitario] = relationship(back_populates="validaciones")
