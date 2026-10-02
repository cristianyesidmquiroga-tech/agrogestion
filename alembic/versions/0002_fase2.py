"""Entidades de labores, inventario, cosecha, procesos y contabilidad."""

import sqlalchemy as sa

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
    uuid = sa.Uuid(as_uuid=True)
    if not sa.inspect(bind).has_table("ciclo"):
        op.create_table(
            "ciclo",
            sa.Column("id", uuid, primary_key=True),
            sa.Column("finca_id", uuid, sa.ForeignKey("finca.id", ondelete="CASCADE"), nullable=False),
            sa.Column("nombre", sa.String(150), nullable=False),
            sa.Column("estado", sa.String(20), nullable=False),
            sa.Column("fecha_inicio", sa.DateTime(timezone=True)),
            sa.Column("fecha_fin", sa.DateTime(timezone=True)),
            sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index("ix_ciclo_finca_id", "ciclo", ["finca_id"])
    for model in (
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
