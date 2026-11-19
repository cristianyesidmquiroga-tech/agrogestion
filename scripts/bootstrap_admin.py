"""Crea el administrador inicial en la base de datos de producción."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import session_factory
from app.core.security import hash_password
from app.models import Usuario


async def bootstrap_admin(db: AsyncSession, email: str, password: str) -> str:
    user = await db.scalar(select(Usuario).where(Usuario.email == email.lower()))
    if user is not None:
        if user.rol != "admin":
            raise RuntimeError(
                f"ADMIN_EMAIL ya pertenece a una cuenta que no es admin: {email.lower()}"
            )
        return f"El administrador {email.lower()} ya existe; no se modificó."

    db.add(
        Usuario(
            email=email.lower(),
            nombre="Administrador",
            password_hash=hash_password(password),
            rol="admin",
        )
    )
    await db.commit()
    return f"Administrador inicial creado: {email.lower()}"


async def main() -> None:
    settings = get_settings()
    if settings.admin_email is None and settings.admin_password is None:
        print("ADMIN_EMAIL y ADMIN_PASSWORD no configurados; se omite el bootstrap.")
        return
    if settings.admin_email is None or settings.admin_password is None:
        raise RuntimeError("Configure ADMIN_EMAIL y ADMIN_PASSWORD conjuntamente.")

    async with session_factory() as db:
        resultado = await bootstrap_admin(
            db, str(settings.admin_email), settings.admin_password.get_secret_value()
        )
    print(resultado)


if __name__ == "__main__":
    asyncio.run(main())
