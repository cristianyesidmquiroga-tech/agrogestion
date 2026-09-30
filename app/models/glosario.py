from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, ColumnasComunes


class GlosarioTermino(ColumnasComunes, Base):
    __tablename__ = "glosario_termino"

    termino: Mapped[str] = mapped_column(String(60), unique=True)
    explicacion: Mapped[str] = mapped_column(Text)
    categoria: Mapped[str] = mapped_column(String(30))
