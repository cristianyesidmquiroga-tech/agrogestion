import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ColumnasComunes


class Consentimiento(ColumnasComunes, Base):
    __tablename__ = "consentimiento"

    usuario_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("usuario.id"), index=True)
    version_politica: Mapped[str] = mapped_column(String(12))
    aceptado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    acepta_transferencia_ia: Mapped[bool] = mapped_column(Boolean, default=False)
