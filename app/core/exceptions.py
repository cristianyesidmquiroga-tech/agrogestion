from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(
        self, status_code: int, code: str, message: str, action: str | None = None
    ) -> None:
        super().__init__(message)
        self.status_code, self.code, self.message, self.action = status_code, code, message, action


class DominioError(AppError):
    status_code = 422
    codigo = "REGLA_DE_NEGOCIO"

    def __init__(self, mensaje: str, codigo: str | None = None) -> None:
        super().__init__(self.status_code, codigo or self.codigo, mensaje)
        self.mensaje = mensaje


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
    codigo = "PERMISO_DENEGADO"


def _respuesta(
    code: str,
    message: str,
    status: int,
    action: str | None = None,
    details: list[dict[str, str]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {"code": code, "message": message}
    if action:
        error["action"] = action
    if details is not None:
        error["details"] = details
    return JSONResponse({"error": error}, status_code=status, headers=headers)


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if exc.status_code == 401 else None
    return _respuesta(exc.code, exc.message, exc.status_code, exc.action, headers=headers)


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
    return _respuesta("DATOS_INVALIDOS", "Hay datos que corregir.", 422, details=detalles)


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
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validacion)
    app.add_exception_handler(StarletteHTTPException, _http)
    app.add_exception_handler(Exception, _inesperado)
