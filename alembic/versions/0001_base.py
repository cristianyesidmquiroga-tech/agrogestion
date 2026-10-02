"""Base de usuarios, fincas, lotes y soporte transversal."""

import sqlalchemy as sa

from alembic import op

revision = "0001_base"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    uuid = sa.Uuid(as_uuid=True)
    op.create_table(
        "usuario",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("password_hash", sa.String(100), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("activo", sa.Boolean, nullable=False),
        sa.Column("intentos_fallidos", sa.Integer, nullable=False),
        sa.Column("bloqueado_hasta", sa.DateTime(timezone=True)),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "finca",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("ubicacion_cifrada", sa.Text),
        sa.Column("creado_por", uuid, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "finca_usuario",
        sa.Column(
            "finca_id", uuid, sa.ForeignKey("finca.id", ondelete="CASCADE"), primary_key=True
        ),
        sa.Column(
            "usuario_id", uuid, sa.ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
        ),
    )
    op.create_table(
        "lote",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("finca_id", uuid, sa.ForeignKey("finca.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("area", sa.Numeric(10, 4), nullable=False),
        sa.Column("creado_por", uuid, sa.ForeignKey("usuario.id"), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("finca_id", "nombre"),
    )
    op.create_index("ix_lote_finca_id", "lote", ["finca_id"])
    op.create_table(
        "auditoria",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("usuario_id", uuid, sa.ForeignKey("usuario.id")),
        sa.Column("finca_id", uuid, sa.ForeignKey("finca.id")),
        sa.Column("operacion", sa.String(80), nullable=False),
        sa.Column("recurso", sa.String(80), nullable=False),
        sa.Column("recurso_id", sa.String(36)),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "idempotency_key",
        sa.Column("clave", sa.String(255), primary_key=True),
        sa.Column("operacion", sa.String(100), primary_key=True),
        sa.Column("respuesta", sa.Text, nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    for table in ("idempotency_key", "auditoria", "lote", "finca_usuario", "finca", "usuario"):
        op.drop_table(table)
