"""Complementos de etapas, ventas y anulaciones contables."""

import sqlalchemy as sa

from alembic import op
from app.models.entities import EtapaProceso, LineaVenta, Venta

revision = "0004_m5_m7_m8_complementos"
down_revision = "0003_pecuario_alertas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for model in (EtapaProceso, Venta, LineaVenta):
        model.__table__.create(bind=bind, checkfirst=True)
    columns = {column["name"] for column in sa.inspect(bind).get_columns("ingreso")}
    if "motivo_anulacion" not in columns:
        op.add_column("ingreso", sa.Column("motivo_anulacion", sa.Text(), nullable=True))
    if "anulado_por" not in columns:
        op.add_column("ingreso", sa.Column("anulado_por", sa.Uuid(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("ingreso")}
    if "anulado_por" in columns or "motivo_anulacion" in columns:
        with op.batch_alter_table("ingreso") as batch:
            if "anulado_por" in columns:
                batch.drop_column("anulado_por")
            if "motivo_anulacion" in columns:
                batch.drop_column("motivo_anulacion")
    for model in (LineaVenta, Venta, EtapaProceso):
        model.__table__.drop(bind=bind, checkfirst=True)
