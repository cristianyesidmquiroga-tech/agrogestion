"""Registro de peticiones en JSON. No guarda encabezados, cuerpo ni query: sin datos personales."""

import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request, Response

NOMBRE = "agrogestion"


class FormatoJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        datos: dict[str, Any] = {
            "momento": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "nivel": record.levelname,
            "evento": record.getMessage(),
        }
        datos.update(getattr(record, "datos", {}))
        return json.dumps(datos, ensure_ascii=False)


def configurar_registro(nivel: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(NOMBRE)
    logger.setLevel(nivel.upper())
    if not logger.handlers:
        manejador = logging.StreamHandler()
        manejador.setFormatter(FormatoJson())
        logger.addHandler(manejador)
    return logger


def instalar(app: FastAPI, logger: logging.Logger) -> None:
    @app.middleware("http")
    async def registrar(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        inicio = time.perf_counter()
        id_peticion = uuid.uuid4().hex[:12]
        estado = 500
        try:
            respuesta = await call_next(request)
            estado = respuesta.status_code
            respuesta.headers["X-Request-ID"] = id_peticion
            return respuesta
        finally:
            logger.info(
                "peticion",
                extra={
                    "datos": {
                        "id": id_peticion,
                        "metodo": request.method,
                        "ruta": request.url.path,
                        "estado": estado,
                        "ms": round((time.perf_counter() - inicio) * 1000, 1),
                    }
                },
            )
