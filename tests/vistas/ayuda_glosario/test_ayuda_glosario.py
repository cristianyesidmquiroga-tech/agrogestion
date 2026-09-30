"""Vista 28: Ayuda y glosario."""

from app.models import GlosarioTermino

URL = "/api/v1/glosario"


async def con_terminos(f):
    f.s.add_all(
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
    await f.s.commit()


async def test_todos_los_roles_con_sesion_entran(cliente, entrar_como, clave):
    await entrar_como(clave)
    assert (await cliente.get(URL)).status_code == 200


async def test_sin_sesion_pide_iniciar_sesion(cliente):
    assert (await cliente.get(URL)).status_code == 401


async def test_lista_ordenada_y_busca(cliente, entrar_como, f):
    await entrar_como("contador")
    await con_terminos(f)
    assert [t["termino"] for t in (await cliente.get(URL)).json()] == ["Jornal", "Zoca"]
    assert [t["termino"] for t in (await cliente.get(URL, params={"q": "zoc"})).json()] == ["Zoca"]


async def test_sin_resultados_devuelve_lista_vacia(cliente, entrar_como, f):
    await entrar_como("agricultor")
    await con_terminos(f)
    assert (await cliente.get(URL, params={"q": "inexistente"})).json() == []
