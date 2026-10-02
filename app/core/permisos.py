"""Qué funciones de la API puede usar un perfil, sacado de las mismas reglas que las protegen."""

from collections.abc import Iterable

from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from starlette.routing import BaseRoute

from app.dependencies import RequiereRol

ORDEN_METODOS = {"GET": 0, "POST": 1, "PUT": 2, "PATCH": 3, "DELETE": 4}


def _dependencias(dep: Dependant) -> list[Dependant]:
    salida: list[Dependant] = []
    for sub in dep.dependencies:
        salida.append(sub)
        salida.extend(_dependencias(sub))
    return salida


def roles_permitidos(ruta: APIRoute) -> tuple[str, ...] | None:
    """Roles que exige la ruta, o None si no exige uno en particular."""
    for dep in _dependencias(ruta.dependant):
        if isinstance(dep.call, RequiereRol):
            return dep.call.roles
    return None


def permisos_del_rol(rutas: Iterable[BaseRoute], rol: str) -> list[dict[str, str]]:
    salida: list[tuple[int, str, int, dict[str, str]]] = []
    for ruta in rutas:
        if not isinstance(ruta, APIRoute) or not ruta.include_in_schema:
            continue
        roles = roles_permitidos(ruta)
        if roles is not None and rol not in roles:
            continue
        grupo = (ruta.tags or ["otros"])[0]
        for metodo in sorted(ruta.methods):
            salida.append(
                (
                    int(str(grupo).split(".")[0]) if str(grupo)[:1].isdigit() else 99,
                    ruta.path,
                    ORDEN_METODOS.get(metodo, 9),
                    {
                        "grupo": str(grupo),
                        "metodo": metodo,
                        "ruta": ruta.path,
                        "resumen": ruta.summary or ruta.name,
                    },
                )
            )
    salida.sort(key=lambda x: (x[0], x[1], x[2]))
    return [item[3] for item in salida]
