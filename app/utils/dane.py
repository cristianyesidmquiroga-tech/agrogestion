"""Validación de los códigos DANE de departamento y municipio."""


def codigos_dane_validos(departamento: str, municipio: str) -> bool:
    """El departamento tiene 2 dígitos y el municipio 5, empezando por el del departamento."""
    return (
        len(departamento) == 2
        and departamento.isdigit()
        and len(municipio) == 5
        and municipio.isdigit()
        and municipio.startswith(departamento)
    )
