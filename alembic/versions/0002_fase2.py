"""Entidades de labores, inventario, cosecha, procesos y contabilidad."""

from alembic import op
from app.models.entities import (
    Actividad,
    Ciclo,
    Cosecha,
    Gasto,
    Ingreso,
    Insumo,
    Jornal,
    MovimientoInsumo,
    Proceso,
    Trabajador,
)

revision = "0002_fase2"
down_revision = "0001_base"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for model in (
        Ciclo,
        Actividad,
        Trabajador,
        Jornal,
        Insumo,
        MovimientoInsumo,
        Cosecha,
        Proceso,
        Gasto,
        Ingreso,
    ):
        model.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for model in (
        Ingreso,
        Gasto,
        Proceso,
        Cosecha,
        MovimientoInsumo,
        Insumo,
        Jornal,
        Trabajador,
        Actividad,
        Ciclo,
    ):
        model.__table__.drop(bind=bind, checkfirst=True)
