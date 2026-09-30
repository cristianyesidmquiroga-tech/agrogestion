from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import GlosarioTermino
from tests.conftest import Fabrica


async def test_glosario_requiere_sesion_y_busca(
    cliente: AsyncClient, f: Fabrica, sesion: AsyncSession
) -> None:
    sesion.add_all(
        [
            GlosarioTermino(
                termino="Jornal",
                explicacion="Un día de trabajo de una persona.",
                categoria="mano de obra",
            ),
            GlosarioTermino(
                termino="Zoca", explicacion="Corte de renovación.", categoria="cultivo"
            ),
        ]
    )
    await sesion.commit()
    assert (await cliente.get("/api/v1/glosario")).status_code == 401
    h = f.cabecera(await f.usuario("contador"))
    todos = await cliente.get("/api/v1/glosario", headers=h)
    assert [t["termino"] for t in todos.json()] == ["Jornal", "Zoca"]
    uno = await cliente.get("/api/v1/glosario", params={"q": "zoc"}, headers=h)
    assert [t["termino"] for t in uno.json()] == ["Zoca"]
