from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.core.exceptions import AppError
from app.schemas.pecuario import AlimentacionCreate, EventoCreate
from app.services.pecuario import validate_external_url


def test_event_requires_one_target() -> None:
    with pytest.raises(ValidationError):
        EventoCreate(tipo="muerte", fecha=datetime.now(UTC))


def test_feed_rejects_negative_values() -> None:
    with pytest.raises(ValidationError):
        AlimentacionCreate(
            lote_animal_id=UUID("00000000-0000-0000-0000-000000000001"),
            alimento="heno",
            cantidad=Decimal("-1"),
            costo=Decimal("2"),
            fecha=datetime.now(UTC),
        )


def test_external_source_requires_allowlisted_https(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERT_ALLOWED_HOSTS", "official.example")
    from app.core.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(AppError):
        validate_external_url("http://official.example/data")
    get_settings.cache_clear()
