from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import AppError, app_error_handler
from app.routers import auth, lands, pecuario, phase2, users


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


app = FastAPI(title="AgroGestion", version="0.1.0")
settings = get_settings()
app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
app.add_middleware(RateLimitMiddleware, limit=120 if settings.app_env == "development" else 60)  # type: ignore[arg-type]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):  # type: ignore[no-untyped-def]
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/health", tags=["sistema"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lands.router)
app.include_router(phase2.router)
app.include_router(pecuario.router)
