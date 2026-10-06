import asyncio
import os

from sqlalchemy import select

from app.core.database import session_factory
from app.core.security import hash_password
from app.models import Usuario


async def main() -> None:
    email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
    clave = os.environ.get("ADMIN_PASSWORD", "")
    if not email or len(clave) < 10:
        return
    async with session_factory() as db:
        if await db.scalar(select(Usuario).where(Usuario.email == email)):
            return
        db.add(
            Usuario(
                email=email,
                nombre="Administrador",
                password_hash=hash_password(clave),
                rol="admin",
            )
        )
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
