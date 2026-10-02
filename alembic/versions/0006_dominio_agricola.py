"""Cultivos, siembras, ciclos de siembra, conocimiento, asistente y noticias."""

import sqlalchemy as sa

from alembic import op
from app.models import Base

revision = "0006_dominio_agricola"
down_revision = "0005_crud_y_precios"
branch_labels = None
depends_on = None


def _agregar(tabla: str, columna: sa.Column) -> None:
    existentes = {c["name"] for c in sa.inspect(op.get_bind()).get_columns(tabla)}
    if columna.name not in existentes:
        op.add_column(tabla, columna)


def upgrade() -> None:
    uuid = sa.Uuid(as_uuid=True)
    _agregar("usuario", sa.Column("ultimo_acceso", sa.DateTime(timezone=True)))
    _agregar("usuario", sa.Column("municipio_dane", sa.String(5)))
    _agregar("finca", sa.Column("departamento_dane", sa.String(2)))
    _agregar("finca", sa.Column("municipio_dane", sa.String(5)))
    _agregar("finca", sa.Column("area_ha", sa.Numeric(10, 4)))
    _agregar("lote", sa.Column("notas", sa.String(500)))

    bind = op.get_bind()
    existentes = set(sa.inspect(bind).get_table_names())
    nuevas = [t for t in Base.metadata.sorted_tables if t.name not in existentes]
    Base.metadata.create_all(bind, tables=nuevas)

    columnas = {c["name"] for c in sa.inspect(bind).get_columns("ciclo")}
    with op.batch_alter_table("ciclo") as lote:
        lote.alter_column("fecha_inicio", existing_type=sa.DateTime(timezone=True), nullable=True)
        if "siembra_id" not in columnas:
            lote.add_column(sa.Column("siembra_id", uuid))
            lote.add_column(sa.Column("tipo", sa.String(12)))
            lote.add_column(sa.Column("numero", sa.SmallInteger))
            lote.add_column(sa.Column("motivo_perdida", sa.Text))
            lote.add_column(sa.Column("creado_por", uuid))
            lote.create_foreign_key("fk_ciclo_siembra_id", "siembra", ["siembra_id"], ["id"])
            lote.create_foreign_key("fk_ciclo_creado_por", "usuario", ["creado_por"], ["id"])
            lote.create_index("ix_ciclo_siembra_id", ["siembra_id"])
            lote.create_unique_constraint("uq_ciclo_siembra_numero", ["siembra_id", "numero"])
    indices = {i["name"] for i in sa.inspect(bind).get_indexes("ciclo")}
    if "ix_ciclo_uno_abierto_por_siembra" not in indices:
        op.create_index(
            "ix_ciclo_uno_abierto_por_siembra",
            "ciclo",
            ["siembra_id"],
            unique=True,
            postgresql_where=sa.text("estado = 'abierto' AND siembra_id IS NOT NULL"),
            sqlite_where=sa.text("estado = 'abierto' AND siembra_id IS NOT NULL"),
        )


def downgrade() -> None:
    indices = {i["name"] for i in sa.inspect(op.get_bind()).get_indexes("ciclo")}
    if "ix_ciclo_uno_abierto_por_siembra" in indices:
        op.drop_index("ix_ciclo_uno_abierto_por_siembra", table_name="ciclo")
    with op.batch_alter_table("ciclo") as lote:
        for nombre in ("creado_por", "motivo_perdida", "numero", "tipo", "siembra_id"):
            lote.drop_column(nombre)
    nuevas = [
        "validacion", "manejo", "sintoma", "problema_sanitario", "fuente", "retroalimentacion",
        "mensaje", "consulta", "noticia", "consentimiento", "glosario_termino", "evento_adverso",
        "cultivo_riesgo", "riesgo", "lote_propagacion", "conteo_planta", "siembra",
        "cultivo_dosis", "cultivo_metodo", "cultivo_fase", "cultivo",
    ]
    for tabla in nuevas:
        op.drop_table(tabla)
    for tabla, columna in (
        ("lote", "notas"),
        ("finca", "area_ha"),
        ("finca", "municipio_dane"),
        ("finca", "departamento_dane"),
        ("usuario", "municipio_dane"),
        ("usuario", "ultimo_acceso"),
    ):
        op.drop_column(tabla, columna)
