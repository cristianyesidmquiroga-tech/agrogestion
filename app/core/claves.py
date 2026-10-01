"""Contraseñas con bcrypt. Nunca se guardan ni se comparan en texto."""

from functools import lru_cache

import bcrypt

from app.core.config import get_settings

LIMITE_BYTES = 72  # bcrypt solo mira los primeros 72 bytes: más largo se rechaza, no se recorta


def hashear(clave: str) -> str:
    datos = clave.encode("utf-8")
    if len(datos) > LIMITE_BYTES:
        raise ValueError("La contraseña no puede pasar de 72 bytes.")
    return bcrypt.hashpw(datos, bcrypt.gensalt(rounds=get_settings().bcrypt_cost)).decode("ascii")


def verificar(clave: str, hash_guardado: str) -> bool:
    datos = clave.encode("utf-8")
    if len(datos) > LIMITE_BYTES:
        return False
    try:
        return bcrypt.checkpw(datos, hash_guardado.encode("ascii"))
    except ValueError:
        return False


@lru_cache
def _hash_de_relleno() -> str:
    return hashear("relleno-para-igualar-tiempos")


def gastar_el_mismo_tiempo(clave: str) -> None:
    """Se llama cuando el usuario no existe, para que responder tarde lo mismo que con uno real."""
    verificar(clave, _hash_de_relleno())
