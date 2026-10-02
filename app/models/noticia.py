import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ColumnasComunes


class Noticia(ColumnasComunes, Base):
    """Toda noticia vence; no existe la opción de fijarla."""

    __tablename__ = "noticia"
    __table_args__ = (Index("ix_noticia_region_vigencia", "region_dane", "vigente_hasta"),)

    titulo: Mapped[str] = mapped_column(String(200))
    resumen: Mapped[str] = mapped_column(String(400))
    enlace: Mapped[str] = mapped_column(String(400))
    fuente: Mapped[str] = mapped_column(String(120))
    region_dane: Mapped[str | None] = mapped_column(String(5))
    cultivo_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("cultivo.id"))
    publicada: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    vigente_hasta: Mapped[datetime] = mapped_column(DateTime(timezone=True))
