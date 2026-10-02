from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.etiquetas import ETIQUETAS
from app.core.exceptions import registrar_manejadores
from app.core.registro import configurar_registro, instalar
from app.routers import (
    auth,
    conocimiento,
    consultas,
    cuenta,
    cultivos,
    documentacion,
    eventos,
    health,
    inicio,
    lands,
    noticias,
    pecuario,
    phase2,
    propagacion,
    reportes,
    siembras,
    users,
)
from app.schemas.common import ErrorRespuesta


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, limit: int = 120) -> None:
        super().__init__(app)
        self.limit = limit
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        import time

        now = time.monotonic()
        key = request.client.host if request.client else "unknown"
        recent = [stamp for stamp in self.requests.get(key, []) if now - stamp < 60]
        if len(recent) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {"code": "RATE_LIMIT", "message": "Límite de peticiones excedido."}
                },
            )
        self.requests[key] = [*recent, now]
        return await call_next(request)


settings = get_settings()
DESCRIPCION = (
    "API para gestionar cultivos de principio a fin: siembras, ciclos, conteo de plantas, "
    "vivero, riesgos, labores, insumos, cosechas, dinero y pecuario. Todos los errores usan "
    "el mismo formato: decida siempre con `error.code`, nunca con `error.message`."
)
RESPUESTAS_ERROR: dict[int | str, dict[str, Any]] = {
    401: {"model": ErrorRespuesta, "description": "Sin sesión o sesión vencida."},
    403: {"model": ErrorRespuesta, "description": "El rol no tiene permiso."},
    404: {"model": ErrorRespuesta, "description": "No existe o no pertenece al usuario."},
    409: {"model": ErrorRespuesta, "description": "Choca con algo que ya existe."},
    422: {"model": ErrorRespuesta, "description": "Datos inválidos o regla de negocio."},
}


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description=DESCRIPCION,
        openapi_tags=ETIQUETAS,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    registrar_manejadores(app)
    instalar(app, configurar_registro(settings.log_level))
    limite = settings.rate_limit or (120 if settings.app_env == "development" else 60)
    app.add_middleware(RateLimitMiddleware, limit=limite)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        max_age=600,
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    app.include_router(documentacion.router)
    for router in (
        auth.router,
        users.router,
        lands.router,
        cuenta.router,
        inicio.router,
        cultivos.router,
        siembras.router,
        propagacion.router,
        eventos.router,
        reportes.router,
        conocimiento.router,
        consultas.router,
        noticias.router,
        phase2.router,
        pecuario.router,
    ):
        app.include_router(router, responses=RESPUESTAS_ERROR)
    app.include_router(health.router)
    return app


app = create_app()
