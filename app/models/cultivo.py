import uuid
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.catalogos import BaseDosis, Fase, MetodoPropagacion, TipoCiclo, UnidadConteo
from app.models.base import Base, ColumnasComunes, check_en


class Cultivo(ColumnasComunes, Base):
    __tablename__ = "cultivo"
    __table_args__ = (check_en("tipo_ciclo", TipoCiclo), check_en("unidad_conteo", UnidadConteo))

    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    nombre_cientifico: Mapped[str | None] = mapped_column(String(120))
    grupo: Mapped[str] = mapped_column(String(30))
    tipo_ciclo: Mapped[str] = mapped_column(String(16))
    unidad_conteo: Mapped[str] = mapped_column(String(6))
    tipo_renovacion: Mapped[str | None] = mapped_column(String(20))
    unidad_cosecha: Mapped[str] = mapped_column(String(12))
    pago_cosecha_sugerido: Mapped[str | None] = mapped_column(String(16))
    densidad_ref: Mapped[int | None] = mapped_column(Integer)
    meses_primera_cosecha: Mapped[int | None] = mapped_column(SmallInteger)
    cosechas_por_anio: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    por_validar: Mapped[bool] = mapped_column(Boolean, default=True)
    fuente: Mapped[str | None] = mapped_column(String(200))

    fases: Mapped[list["CultivoFase"]] = relationship(
        back_populates="cultivo",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="CultivoFase.orden",
    )
    metodos: Mapped[list["CultivoMetodo"]] = relationship(
        back_populates="cultivo", cascade="all, delete-orphan", lazy="selectin"
    )
    dosis: Mapped[list["CultivoDosis"]] = relationship(
        back_populates="cultivo", cascade="all, delete-orphan", lazy="selectin"
    )


class CultivoFase(ColumnasComunes, Base):
    __tablename__ = "cultivo_fase"
    __table_args__ = (UniqueConstraint("cultivo_id", "fase"), check_en("fase", Fase))

    cultivo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cultivo.id"), index=True)
    fase: Mapped[str] = mapped_column(String(24))
    orden: Mapped[int] = mapped_column(SmallInteger)
    dias_estimados: Mapped[int | None] = mapped_column(Integer)
    por_validar: Mapped[bool] = mapped_column(Boolean, default=True)

    cultivo: Mapped[Cultivo] = relationship(back_populates="fases")


class CultivoMetodo(ColumnasComunes, Base):
    __tablename__ = "cultivo_metodo"
    __table_args__ = (
        UniqueConstraint("cultivo_id", "metodo"),
        check_en("metodo", MetodoPropagacion),
    )

    cultivo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cultivo.id"), index=True)
    metodo: Mapped[str] = mapped_column(String(12))
    dias_germinacion: Mapped[int | None] = mapped_column(Integer)
    dias_vivero: Mapped[int | None] = mapped_column(Integer)
    por_validar: Mapped[bool] = mapped_column(Boolean, default=True)

    cultivo: Mapped[Cultivo] = relationship(back_populates="metodos")


class CultivoDosis(ColumnasComunes, Base):
    __tablename__ = "cultivo_dosis"
    __table_args__ = (check_en("base", BaseDosis),)

    cultivo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cultivo.id"), index=True)
    insumo_tipo: Mapped[str] = mapped_column(String(30))
    dosis: Mapped[Decimal] = mapped_column(Numeric(10, 3))
    unidad: Mapped[str] = mapped_column(String(12))
    base: Mapped[str] = mapped_column(String(10))
    por_validar: Mapped[bool] = mapped_column(Boolean, default=True)

    cultivo: Mapped[Cultivo] = relationship(back_populates="dosis")
