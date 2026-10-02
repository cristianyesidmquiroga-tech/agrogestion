"""Estados, precios y soporte de consulta para historias pendientes."""

import sqlalchemy as sa

from alembic import op
from app.models.entities import PrecioCategoria

revision = "0005_crud_y_precios"
down_revision = "0004_m5_m7_m8_complementos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    PrecioCategoria.__table__.create(bind=bind, checkfirst=True)
    for table, column in (
        ("actividad", "estado"),
        ("trabajador", "estado"),
        ("insumo", "estado"),
        ("cosecha", "estado"),
        ("etapa_proceso", "estado"),
    ):
        columns = {item["name"] for item in sa.inspect(bind).get_columns(table)}
        if column not in columns:
            op.add_column(
                table, sa.Column(column, sa.String(20), nullable=False, server_default="activo")
            )


def downgrade() -> None:
    bind = op.get_bind()
    for table, column in (
        ("etapa_proceso", "estado"),
        ("cosecha", "estado"),
        ("insumo", "estado"),
        ("trabajador", "estado"),
        ("actividad", "estado"),
    ):
        columns = {item["name"] for item in sa.inspect(bind).get_columns(table)}
        if column in columns:
            op.drop_column(table, column)
    PrecioCategoria.__table__.drop(bind=bind, checkfirst=True)
