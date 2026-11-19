import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password
from app.models import Usuario
from scripts.bootstrap_admin import bootstrap_admin


async def test_crea_admin_y_no_cambia_su_clave_en_siguientes_arranques(
    bd: AsyncSession,
) -> None:
    email = "Admin@ejemplo.com"
    password = "Clave-segura-123"

    assert await bootstrap_admin(bd, email, password) == "Administrador inicial creado: admin@ejemplo.com"
    user = await bd.scalar(select(Usuario).where(Usuario.email == "admin@ejemplo.com"))
    assert user is not None
    assert user.rol == "admin"
    assert verify_password(password, user.password_hash)

    resultado = await bootstrap_admin(bd, email, "Otra-clave-segura-456")
    await bd.refresh(user)
    assert resultado == "El administrador admin@ejemplo.com ya existe; no se modificó."
    assert verify_password(password, user.password_hash)


async def test_falla_si_el_correo_configurado_ya_es_de_un_usuario_no_admin(
    bd: AsyncSession,
) -> None:
    bd.add(
        Usuario(
            email="usuario@ejemplo.com",
            nombre="Usuario",
            password_hash="hash",
            rol="agricultor",
        )
    )
    await bd.commit()

    with pytest.raises(RuntimeError, match="no es admin"):
        await bootstrap_admin(bd, "usuario@ejemplo.com", "Clave-segura-123")
