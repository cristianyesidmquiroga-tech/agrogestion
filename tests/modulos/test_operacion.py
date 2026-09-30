import json
import logging

from httpx import AsyncClient
from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.core.registro import FormatoJson
from tests.conftest import Fabrica


async def test_ready_responde_cuando_la_base_esta_arriba(cliente: AsyncClient) -> None:
    r = await cliente.get("/health/ready")
    assert r.status_code == 200
    assert r.json()["base_de_datos"] == "ok"


async def test_ready_responde_503_si_la_base_no_contesta(cliente: AsyncClient) -> None:
    class SesionCaida:
        async def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, Exception("sin conexión"))

    async def caida():
        yield SesionCaida()

    cliente._transport.app.dependency_overrides[get_db] = caida  # type: ignore[attr-defined]
    r = await cliente.get("/health/ready")
    assert r.status_code == 503
    assert r.json()["error"] == "SERVICIO_NO_LISTO"
    assert (await cliente.get("/health")).status_code == 200


async def test_cada_respuesta_trae_su_identificador(cliente: AsyncClient) -> None:
    r = await cliente.get("/health")
    assert len(r.headers["x-request-id"]) == 12


async def test_el_registro_no_guarda_datos_personales(
    cliente: AsyncClient, f: Fabrica, caplog
) -> None:
    usuario = await f.usuario()
    with caplog.at_level(logging.INFO, logger="agrogestion"):
        caplog.handler.setFormatter(FormatoJson())
        await cliente.get("/api/v1/cultivos?q=secreto", headers=f.cabecera(usuario))
    lineas = [caplog.handler.format(r) for r in caplog.records if r.name == "agrogestion"]
    assert lineas
    datos = json.loads(lineas[-1])
    assert set(datos) == {"momento", "nivel", "evento", "id", "metodo", "ruta", "estado", "ms"}
    assert datos["ruta"] == "/api/v1/cultivos"
    assert datos["estado"] == 200
    texto = " ".join(lineas)
    assert "secreto" not in texto
    assert "Bearer" not in texto
    assert usuario.correo not in texto
