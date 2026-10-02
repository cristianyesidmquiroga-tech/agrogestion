from decimal import Decimal

import pytest

from app.schemas.phase2 import IngresoCreate, JornalCreate


def test_jornal_uses_decimal_formula() -> None:
    data = JornalCreate(
        actividad_id="00000000-0000-0000-0000-000000000001",
        ciclo_id="00000000-0000-0000-0000-000000000002",
        fecha="2026-01-01T00:00:00Z",
        obreros=Decimal("2"),
        dias=Decimal("3"),
        valor_jornal=Decimal("45.50"),
    )
    assert data.obreros * data.dias * data.valor_jornal == Decimal("273.00")


def test_income_rejects_inconsistent_total() -> None:
    with pytest.raises(ValueError):
        IngresoCreate(
            categoria="venta",
            cantidad=Decimal("2"),
            precio_unitario=Decimal("10"),
            total=Decimal("19"),
            fecha="2026-01-01T00:00:00Z",
        )
