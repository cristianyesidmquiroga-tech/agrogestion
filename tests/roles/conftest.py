from pathlib import Path

import pytest_asyncio


@pytest_asyncio.fixture
async def yo(request, f):
    """El usuario del rol que corresponde a la carpeta de la prueba (roles/<rol>/)."""
    return await f.usuario(Path(str(request.node.fspath)).parent.name)


@pytest_asyncio.fixture
async def sesion(cliente, f, yo):
    """Cliente con la sesión iniciada por ese usuario."""
    cliente.headers.update(f.cabecera(yo))
    return cliente
