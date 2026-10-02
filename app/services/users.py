from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import hash_password
from app.models import Usuario
from app.schemas.auth import UsuarioCreate


async def create_user(db: AsyncSession, data: UsuarioCreate) -> Usuario:
    if await db.scalar(select(Usuario).where(Usuario.email == data.email.lower())):
        raise AppError(409, "EMAIL_EN_USO", "El correo electrónico ya está registrado.")
    user = Usuario(
        email=data.email.lower(),
        nombre=data.nombre,
        password_hash=hash_password(data.password),
        rol=data.rol,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
