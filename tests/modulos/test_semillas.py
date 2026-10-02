from sqlalchemy import func, select

from app.models import Cultivo
from scripts.datos_iniciales import CULTIVOS, GLOSARIO, RIESGOS
from scripts.seed import cargar


async def test_carga_los_datos_iniciales(sesion):
    nuevos = await cargar(sesion)
    assert nuevos == {"cultivos": len(CULTIVOS), "riesgos": len(RIESGOS), "glosario": len(GLOSARIO)}


async def test_se_puede_repetir_sin_duplicar(sesion):
    await cargar(sesion)
    segunda = await cargar(sesion)
    assert segunda == {"cultivos": 0, "riesgos": 0, "glosario": 0}
    assert await sesion.scalar(select(func.count()).select_from(Cultivo)) == len(CULTIVOS)


async def test_todo_perfil_precargado_queda_por_validar(sesion):
    await cargar(sesion)
    for cultivo in await sesion.scalars(select(Cultivo)):
        assert cultivo.por_validar is True
        assert all(f.por_validar and f.dias_estimados is None for f in cultivo.fases)
        assert all(m.por_validar for m in cultivo.metodos)
        assert cultivo.dosis == []


async def test_cubre_todos_los_tipos_de_ciclo(sesion):
    await cargar(sesion)
    tipos = set(await sesion.scalars(select(Cultivo.tipo_ciclo).distinct()))
    assert tipos == {"transitorio", "semipermanente", "permanente", "forestal"}


async def test_un_transitorio_no_trae_renovacion(sesion):
    await cargar(sesion)
    cultivos = await sesion.scalars(select(Cultivo).where(Cultivo.tipo_ciclo == "transitorio"))
    for c in cultivos:
        assert c.tipo_renovacion is None
        assert "renovacion" not in [f.fase for f in c.fases]
