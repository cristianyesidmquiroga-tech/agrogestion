"""Errores de dominio y el único lugar donde se convierten en respuesta JSON."""

from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class DominioError(Exception):
    status_code = 422
    codigo = "REGLA_DE_NEGOCIO"

    def __init__(self, mensaje: str, codigo: str | None = None) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        if codigo:
            self.codigo = codigo


class NoEncontrado(DominioError):
    status_code = 404
    codigo = "NO_ENCONTRADO"


class Conflicto(DominioError):
    status_code = 409
    codigo = "CONFLICTO"


class ReglaNegocio(DominioError):
    status_code = 422


class NoAutenticado(DominioError):
    status_code = 401
    codigo = "NO_AUTENTICADO"


class LimiteSuperado(DominioError):
    status_code = 429
    codigo = "LIMITE_SUPERADO"


class ServicioNoListo(DominioError):
    status_code = 503
    codigo = "SERVICIO_NO_LISTO"


class SinPermiso(DominioError):
    status_code = 403
    codigo = "SIN_PERMISO"


def _respuesta(
    error: str,
    mensaje: str,
    status: int,
    detalles: list[dict[str, str]] | None = None,
    cabeceras: dict[str, str] | None = None,
) -> JSONResponse:
    cuerpo: dict[str, Any] = {"error": error, "message": mensaje, "status_code": status}
    if detalles is not None:
        cuerpo["details"] = detalles
    return JSONResponse(cuerpo, status_code=status, headers=cabeceras)


async def _dominio(_: Request, exc: Exception) -> JSONResponse:
    exc = cast(DominioError, exc)
    cabeceras = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return _respuesta(exc.codigo, exc.mensaje, exc.status_code, cabeceras=cabeceras)


async def _validacion(_: Request, exc: Exception) -> JSONResponse:
    exc = cast(RequestValidationError, exc)
    detalles = [
        {
            "campo": ".".join(str(p) for p in e["loc"] if p not in ("body", "query", "path")),
            "mensaje": str(e["msg"]),
            "tipo": str(e["type"]),
        }
        for e in exc.errors()
    ]
    return _respuesta("DATOS_INVALIDOS", "Hay datos que corregir.", 422, detalles)


_TEXTOS_HTTP = {
    404: ("NO_ENCONTRADO", "No encontramos lo que busca."),
    405: ("METODO_NO_PERMITIDO", "Esa acción no está disponible en esta dirección."),
}


async def _http(_: Request, exc: Exception) -> JSONResponse:
    exc = cast(StarletteHTTPException, exc)
    codigo, mensaje = _TEXTOS_HTTP.get(
        exc.status_code, ("ERROR", "No se pudo completar la petición.")
    )
    return _respuesta(codigo, mensaje, exc.status_code)


async def _inesperado(_: Request, __: Exception) -> JSONResponse:
    return _respuesta("ERROR_INTERNO", "Algo salió mal de nuestro lado. Intente de nuevo.", 500)


def registrar_manejadores(app: FastAPI) -> None:
    app.add_exception_handler(DominioError, _dominio)
    app.add_exception_handler(RequestValidationError, _validacion)
    app.add_exception_handler(StarletteHTTPException, _http)
    app.add_exception_handler(Exception, _inesperado)
