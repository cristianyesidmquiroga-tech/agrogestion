import os
import uuid
from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal

os.environ.setdefault("AGRO_SECRET_KEY", "clave-solo-para-pruebas-0123456789abcdef")
os.environ.setdefault("AGRO_DATABASE_URL", "sqlite+aiosqlite://")

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import crear_token
from app.main import create_app
from app.models import (
    Base,
    Ciclo,
    Cultivo,
    CultivoDosis,
    CultivoFase,
    CultivoMetodo,
    CultivoRiesgo,
    Finca,
    FincaUsuario,
    Fuente,
    Lote,
    Manejo,
    ProblemaSanitario,
    Riesgo,
    Siembra,
    Sintoma,
    Usuario,
)


class Fabrica:
    """Crea datos de prueba directamente en la base."""

    def __init__(self, sesion: AsyncSession) -> None:
        self.s = sesion
        self._n = 0

    async def usuario(self, rol: str = "agricultor") -> Usuario:
        self._n += 1
        u = Usuario(
            nombre=f"Usuario {self._n}", correo=f"u{self._n}@prueba.test", clave_hash="x", rol=rol
        )
        self.s.add(u)
        await self.s.commit()
        return u

    def cabecera(self, usuario: Usuario) -> dict[str, str]:
        return {"Authorization": f"Bearer {crear_token(usuario.id)}"}

    async def finca(self, *usuarios: Usuario, area: str = "10") -> Finca:
        f = Finca(
            nombre="Finca de prueba",
            departamento_dane="05",
            municipio_dane="05001",
            area_ha=Decimal(area),
        )
        self.s.add(f)
        await self.s.flush()
        for u in usuarios:
            self.s.add(FincaUsuario(finca_id=f.id, usuario_id=u.id))
        await self.s.commit()
        return f

    async def lote(self, finca: Finca, area: str = "5", nombre: str = "Lote 1") -> Lote:
        lote = Lote(finca_id=finca.id, nombre=nombre, area_ha=Decimal(area))
        self.s.add(lote)
        await self.s.commit()
        return lote

    async def escenario(self, usuario, area_lote="5", **cultivo):
        finca = await self.finca(usuario)
        lote = await self.lote(finca, area=area_lote)
        return finca, lote, await self.cultivo(**cultivo)

    async def siembra(self, finca, lote, cultivo, area="1", estado="planeada", plantas=100):
        s = Siembra(
            finca_id=finca.id,
            lote_id=lote.id,
            cultivo_id=cultivo.id,
            metodo="semilla",
            area_ha=Decimal(area),
            plantas_sembradas=plantas,
            fecha_plan=date.today(),
            estado=estado,
        )
        self.s.add(s)
        await self.s.flush()
        en_curso = estado == "en_curso"
        self.s.add(
            Ciclo(
                siembra_id=s.id,
                tipo="levante",
                numero=1,
                estado="en_curso" if en_curso else "planeado",
                fecha_inicio=date.today() if en_curso else None,
            )
        )
        await self.s.commit()
        return s

    async def fuente(self, nombre="Fuente de prueba"):
        f = Fuente(nombre=nombre, url="https://ejemplo.test/fuente")
        self.s.add(f)
        await self.s.commit()
        return f

    async def ficha(
        self,
        nombre="Hongo de la hoja",
        cultivo=None,
        estado="validado",
        sintomas=("manchas amarillas en las hojas",),
        manejo=("cultural", "Retire las hojas afectadas y mejore la ventilación.", None),
        quimico=None,
    ):
        """Crea una ficha; `quimico` es (descripción, producto registrado)."""
        fuente = await self.fuente(f"Fuente de {nombre}")
        p = ProblemaSanitario(
            nombre=nombre,
            tipo="enfermedad",
            cultivo_id=cultivo.id if cultivo else None,
            estado=estado,
        )
        p.sintomas = [Sintoma(descripcion=d) for d in sintomas]
        p.manejos = [Manejo(tipo=manejo[0], descripcion=manejo[1], fuente_id=fuente.id)]
        if quimico:
            p.manejos.append(
                Manejo(
                    tipo="quimico",
                    descripcion=quimico[0],
                    producto_ica=quimico[1],
                    fuente_id=fuente.id,
                )
            )
        self.s.add(p)
        await self.s.commit()
        return p

    async def riesgo_de_cultivo(self, cultivo, riesgo, fase, susceptibilidad="alta"):
        self.s.add(
            CultivoRiesgo(
                cultivo_id=cultivo.id,
                riesgo_id=riesgo.id,
                fase_critica=fase,
                susceptibilidad=susceptibilidad,
                medidas="Proteja las plantas.",
            )
        )
        await self.s.commit()

    async def riesgo(self, nombre="Helada", tipo="clima"):
        r = Riesgo(nombre=nombre, tipo=tipo, aplica_a="cultivo")
        self.s.add(r)
        await self.s.commit()
        return r

    async def cultivo(
        self,
        nombre: str | None = None,
        tipo_ciclo: str = "permanente",
        unidad_conteo: str = "planta",
        tipo_renovacion: str | None = "zoca",
        metodos: tuple[str, ...] = ("semilla", "esqueje"),
        dosis: tuple[tuple[str, str, str, str], ...] = (),
    ) -> Cultivo:
        c = Cultivo(
            nombre=nombre or f"Cultivo {uuid.uuid4().hex[:8]}",
            grupo="prueba",
            tipo_ciclo=tipo_ciclo,
            unidad_conteo=unidad_conteo,
            tipo_renovacion=tipo_renovacion,
            unidad_cosecha="kilo",
            por_validar=True,
        )
        c.fases = [
            CultivoFase(fase="preparacion", orden=1, dias_estimados=10),
            CultivoFase(fase="siembra", orden=2, dias_estimados=5),
            CultivoFase(fase="mantenimiento", orden=3, dias_estimados=30),
        ]
        c.metodos = [CultivoMetodo(metodo=m) for m in metodos]
        c.dosis = [
            CultivoDosis(insumo_tipo=t, dosis=Decimal(d), unidad=u, base=b) for t, d, u, b in dosis
        ]
        self.s.add(c)
        await self.s.commit()
        return c


PERFILES = ("admin", "agricultor", "contador", "experto")


def pytest_generate_tests(metafunc):
    """Toda prueba que pida `clave` se repite una vez por cada rol."""
    if "clave" in metafunc.fixturenames:
        metafunc.parametrize("clave", PERFILES)


@pytest_asyncio.fixture
async def motor() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        "sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    async with engine.begin() as conexion:
        await conexion.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def sesion(motor: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async with async_sessionmaker(motor, expire_on_commit=False)() as s:
        yield s


@pytest_asyncio.fixture
async def cliente(motor: AsyncEngine) -> AsyncIterator[AsyncClient]:
    app = create_app()
    fabrica_sesiones = async_sessionmaker(motor, expire_on_commit=False)

    async def _db() -> AsyncIterator[AsyncSession]:
        async with fabrica_sesiones() as s:
            yield s

    app.dependency_overrides[get_db] = _db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def entrar_como(cliente, f):
    """Inicia sesión con un usuario del rol indicado y devuelve ese usuario."""

    async def _entrar(clave):
        usuario = await f.usuario(clave)
        cliente.headers.update(f.cabecera(usuario))
        return usuario

    return _entrar


@pytest_asyncio.fixture
async def f(sesion: AsyncSession) -> Fabrica:
    return Fabrica(sesion)


def payload_siembra(
    finca_id: uuid.UUID, lote_id: uuid.UUID, cultivo_id: uuid.UUID, **extra: object
) -> dict[str, object]:
    base: dict[str, object] = {
        "finca_id": str(finca_id),
        "lote_id": str(lote_id),
        "cultivo_id": str(cultivo_id),
        "metodo": "semilla",
        "area_ha": 2,
        "plantas_sembradas": 100,
        "fecha_plan": date.today().isoformat(),
    }
    base.update(extra)
    return base


def payload_cultivo(**extra: object) -> dict[str, object]:
    base: dict[str, object] = {
        "nombre": "Cultivo de prueba",
        "grupo": "frutal",
        "tipo_ciclo": "permanente",
        "unidad_conteo": "planta",
        "tipo_renovacion": "zoca",
        "unidad_cosecha": "kilo",
        "fases": [
            {"fase": "preparacion", "orden": 1, "dias_estimados": 20},
            {"fase": "siembra", "orden": 2},
        ],
        "metodos": [{"metodo": "semilla", "dias_germinacion": 30}, {"metodo": "esqueje"}],
        "dosis": [{"insumo_tipo": "abono", "dosis": "0.25", "unidad": "kg", "base": "planta"}],
    }
    base.update(extra)
    return base
