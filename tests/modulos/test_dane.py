import pytest

from app.utils.dane import codigos_dane_validos


@pytest.mark.parametrize(
    ("departamento", "municipio", "esperado"),
    [
        ("05", "05001", True),
        ("76", "76001", True),
        ("5", "05001", False),
        ("05", "5001", False),
        ("05", "76001", False),
        ("0A", "0A001", False),
        ("", "", False),
    ],
)
def test_codigos_dane(departamento: str, municipio: str, esperado: bool) -> None:
    assert codigos_dane_validos(departamento, municipio) is esperado
