from cryptography.fernet import Fernet

from app.core.config import get_settings


def _cipher() -> Fernet:
    key = get_settings().field_encryption_key
    if not key:
        raise RuntimeError("FIELD_ENCRYPTION_KEY no está configurada")
    return Fernet(key.encode())


def encrypt_sensitive(value: str) -> str:
    return _cipher().encrypt(value.encode()).decode()


def decrypt_sensitive(value: str) -> str:
    return _cipher().decrypt(value.encode()).decode()
