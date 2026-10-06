"""Prepara una cuenta de administrador solo para el entorno local SQLite.

Uso: python -m scripts.local_admin
"""

import asyncio

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import session_factory
from app.core.security import hash_password
from app.models import Usuario

LOCAL_ADMIN_EMAIL = "admin@demo.com"
LOCAL_ADMIN_PASSWORD = "1234"


async def main() -> None:
    settings = get_settings()
    if settings.app_env != "development" or not settings.database_url.startswith("sqlite"):
        raise RuntimeError("El administrador local solo se configura en desarrollo con SQLite.")

    async with session_factory() as db:
        user = await db.scalar(select(Usuario).where(Usuario.email == LOCAL_ADMIN_EMAIL))
        if user is None:
            user = Usuario(
                email=LOCAL_ADMIN_EMAIL,
                nombre="Administrador local",
                password_hash=hash_password(LOCAL_ADMIN_PASSWORD),
                rol="admin",
            )
            db.add(user)
        else:
            user.nombre = "Administrador local"
            user.password_hash = hash_password(LOCAL_ADMIN_PASSWORD)
            user.rol = "admin"
            user.activo = True
            user.intentos_fallidos = 0
            user.bloqueado_hasta = None
        await db.commit()

    print(f"Cuenta local lista: {LOCAL_ADMIN_EMAIL} / {LOCAL_ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
