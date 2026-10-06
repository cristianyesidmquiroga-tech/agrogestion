"""Documentación interactiva (/docs): fondo blanco siempre y un panel para iniciar sesión."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

ESTILO_CLARO = (
    '<meta name="color-scheme" content="light">'
    "<style>:root{color-scheme:light only}"
    "html,body{background:#fff!important;color:#3b4151}</style>"
)
PANEL_ACCESO = (Path(__file__).parent / "docs_acceso.html").read_text(encoding="utf-8")
MENU_API = (Path(__file__).parent / "docs_menu.html").read_text(encoding="utf-8")


@router.get("/docs", include_in_schema=False)
async def documentacion() -> HTMLResponse:
    pagina = get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{settings.app_name} - Documentación",
        swagger_ui_parameters={"persistAuthorization": True, "displayRequestDuration": True},
    )
    html = bytes(pagina.body).decode("utf-8")
    html = html.replace("</head>", ESTILO_CLARO + "</head>", 1)
    html = html.replace("</body>", PANEL_ACCESO + MENU_API + "</body>", 1)
    return HTMLResponse(html)
