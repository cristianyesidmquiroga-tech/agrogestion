from datetime import UTC, date, datetime, time


def a_dia(valor: datetime | date | None) -> date | None:
    if isinstance(valor, datetime):
        return valor.date()
    return valor


def a_fecha_hora(dia: date) -> datetime:
    return datetime.combine(dia, time.min, tzinfo=UTC)
