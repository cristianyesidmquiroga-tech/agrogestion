import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.catalogos import EstadoCiclo, EstadoSiembra, TipoCicloSiembra
from app.models.base import Base, ColumnasComunes, check_en
from app.models.cultivo import Cultivo


class Siembra(ColumnasComunes, Base):
    __tablename__ = "siembra"
    __table_args__ = (
        CheckConstraint("area_ha > 0", name="area_positiva"),
        CheckConstraint(
            "plantas_sembradas IS NULL OR plantas_sembradas >= 0", name="plantas_no_negativas"
        ),
        check_en("estado", EstadoSiembra),
        Index("ix_siembra_lote_estado", "lote_id", "estado"),
    )

    finca_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("finca.id"), index=True)
    lote_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lote.id"))
    cultivo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cultivo.id"))
    metodo: Mapped[str] = mapped_column(String(12))
    area_ha: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    plantas_sembradas: Mapped[int | None] = mapped_column(Integer)
    fecha_plan: Mapped[date] = mapped_column(Date)
    presupuesto: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    estado: Mapped[str] = mapped_column(String(12), default="planeada")

    cultivo: Mapped[Cultivo] = relationship(lazy="selectin")
    ciclos: Mapped[list["Ciclo"]] = relationship(
        back_populates="siembra", lazy="selectin", order_by="Ciclo.numero"
    )


class Ciclo(ColumnasComunes, Base):
    __tablename__ = "ciclo"
    __table_args__ = (
        UniqueConstraint("siembra_id", "numero"),
        check_en("tipo", TipoCicloSiembra),
        check_en("estado", EstadoCiclo),
        Index(
            "ix_ciclo_un_en_curso",
            "siembra_id",
            unique=True,
            postgresql_where=text("estado = 'en_curso'"),
            sqlite_where=text("estado = 'en_curso'"),
        ),
    )

    siembra_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("siembra.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(12))
    numero: Mapped[int] = mapped_column(SmallInteger)
    estado: Mapped[str] = mapped_column(String(10), default="planeado")
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    motivo_perdida: Mapped[str | None] = mapped_column(Text)

    siembra: Mapped[Siembra] = relationship(back_populates="ciclos")


class ConteoPlanta(ColumnasComunes, Base):
    __tablename__ = "conteo_planta"
    __table_args__ = (
        CheckConstraint("vivas >= 0", name="vivas_no_negativas"),
        CheckConstraint("muertas >= 0", name="muertas_no_negativas"),
        CheckConstraint("resiembras >= 0", name="resiembras_no_negativas"),
    )

    siembra_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("siembra.id"), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    vivas: Mapped[int] = mapped_column(Integer)
    muertas: Mapped[int] = mapped_column(Integer, default=0)
    resiembras: Mapped[int] = mapped_column(Integer, default=0)


class LotePropagacion(ColumnasComunes, Base):
    __tablename__ = "lote_propagacion"
    __table_args__ = (
        CheckConstraint("puestas > 0", name="puestas_positivas"),
        CheckConstraint("germinadas <= puestas", name="germinadas_hasta_puestas"),
        CheckConstraint("listas <= germinadas", name="listas_hasta_germinadas"),
        CheckConstraint("trasplantadas <= listas", name="trasplantadas_hasta_listas"),
    )

    finca_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("finca.id"), index=True)
    cultivo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("cultivo.id"))
    siembra_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("siembra.id"))
    metodo: Mapped[str] = mapped_column(String(12))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    puestas: Mapped[int] = mapped_column(Integer)
    germinadas: Mapped[int] = mapped_column(Integer, default=0)
    listas: Mapped[int] = mapped_column(Integer, default=0)
    perdidas: Mapped[int] = mapped_column(Integer, default=0)
    trasplantadas: Mapped[int] = mapped_column(Integer, default=0)


class Cosecha(ColumnasComunes, Base):
    """Contrato del módulo de cosecha; su servicio y router los escribe Brayan."""

    __tablename__ = "cosecha"
    __table_args__ = (CheckConstraint("cantidad > 0", name="cantidad_positiva"),)

    ciclo_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("ciclo.id"), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    unidad: Mapped[str] = mapped_column(String(12))
    calidad: Mapped[str | None] = mapped_column(String(30))
