"""M12 pecuario y alertas regionales."""

from alembic import op
from app.models.entities import (
    AlertaRegional,
    AlimentacionAnimal,
    Animal,
    Especie,
    EventoAnimal,
    FuenteAlerta,
    LoteAnimal,
    ProduccionAnimal,
)

revision = "0003_pecuario_alertas"
down_revision = "0002_fase2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for model in (
        Especie,
        LoteAnimal,
        Animal,
        EventoAnimal,
        ProduccionAnimal,
        AlimentacionAnimal,
        FuenteAlerta,
        AlertaRegional,
    ):
        model.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    for model in (
        AlertaRegional,
        FuenteAlerta,
        AlimentacionAnimal,
        ProduccionAnimal,
        EventoAnimal,
        Animal,
        LoteAnimal,
        Especie,
    ):
        model.__table__.drop(bind=bind, checkfirst=True)
