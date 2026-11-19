"""Borra las noticias vencidas. Se programa a diario (por ejemplo, con las tareas de Coolify).

Uso: python -m scripts.limpiar_vencidos
"""

import asyncio

from app.core.database import session_factory
from app.services import noticia_service


async def main() -> None:
    async with session_factory() as db:
        borradas = await noticia_service.borrar_vencidas(db)
    print(f"Noticias vencidas borradas: {borradas}")


if __name__ == "__main__":
    asyncio.run(main())
