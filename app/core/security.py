from datetime import UTC, datetime, timedelta
from functools import lru_cache
from uuid import UUID

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    rounds = get_settings().bcrypt_cost
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=rounds)).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(UTC)
    expira = now + timedelta(minutes=get_settings().jwt_expire_minutes)
    claims = {"sub": str(user_id), "iat": now, "exp": expira}
    return jwt.encode(claims, get_settings().jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
    return UUID(str(payload["sub"]))


@lru_cache
def _hash_de_relleno() -> str:
    return hash_password("relleno-para-igualar-tiempos")


def gastar_el_mismo_tiempo(password: str) -> None:
    verify_password(password, _hash_de_relleno())
