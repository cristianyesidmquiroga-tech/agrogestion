import pytest

from app.core.exceptions import AppError
from app.dependencies import require_role
from app.models import Usuario


@pytest.mark.asyncio
async def test_contador_no_puede_crear_fuentes() -> None:
    dependency = require_role("admin")
    with pytest.raises(AppError) as error:
        await dependency(Usuario(rol="contador"))
    assert error.value.status_code == 403


@pytest.mark.asyncio
async def test_admin_puede_crear_fuentes() -> None:
    dependency = require_role("admin")
    user = await dependency(Usuario(rol="admin"))
    assert user.rol == "admin"
