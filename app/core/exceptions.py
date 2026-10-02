from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(
        self, status_code: int, code: str, message: str, action: str | None = None
    ) -> None:
        self.status_code, self.code, self.message, self.action = status_code, code, message, action


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    body: dict[str, Any] = {"error": {"code": exc.code, "message": exc.message}}
    if exc.action:
        body["error"]["action"] = exc.action
    return JSONResponse(status_code=exc.status_code, content=body)
