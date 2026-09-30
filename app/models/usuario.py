import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.catalogos import RolUsuario
from app.models.base import Base, ColumnasComunes, check_en


class Usuario(ColumnasComunes, Base):
    __tablename__ = "usuario"
    __table_args__ = (check_en("rol", RolUsuario),)

    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(160), unique=True)
    clave_hash: Mapped[str] = mapped_column(String(100))
    rol: Mapped[str] = mapped_column(String(12))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    municipio_dane: Mapped[str | None] = mapped_column(String(5))


class Consentimiento(ColumnasComunes, Base):
    __tablename__ = "consentimiento"

    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("usuario.id"), index=True)
    version_politica: Mapped[str] = mapped_column(String(12))
    aceptado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    acepta_transferencia_ia: Mapped[bool] = mapped_column(Boolean, default=False)
