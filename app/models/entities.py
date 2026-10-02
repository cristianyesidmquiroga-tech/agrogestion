from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.siembra import Siembra


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Usuario(TimestampMixin, Base):
    __tablename__ = "usuario"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(String(100))
    rol: Mapped[str] = mapped_column(String(20), default="agricultor")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    intentos_fallidos: Mapped[int] = mapped_column(default=0)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    municipio_dane: Mapped[str | None] = mapped_column(String(5), nullable=True)
    fincas: Mapped[list["FincaUsuario"]] = relationship(back_populates="usuario")


class Finca(TimestampMixin, Base):
    __tablename__ = "finca"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(150))
    ubicacion_cifrada: Mapped[str | None] = mapped_column(Text, nullable=True)
    departamento_dane: Mapped[str | None] = mapped_column(String(2), nullable=True)
    municipio_dane: Mapped[str | None] = mapped_column(String(5), nullable=True)
    area_ha: Mapped[Decimal | None] = mapped_column(Numeric(10, 4), nullable=True)
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))
    usuarios: Mapped[list["FincaUsuario"]] = relationship(back_populates="finca")
    lotes: Mapped[list["Lote"]] = relationship(back_populates="finca")


class FincaUsuario(Base):
    __tablename__ = "finca_usuario"
    finca_id: Mapped[UUID] = mapped_column(
        ForeignKey("finca.id", ondelete="CASCADE"), primary_key=True
    )
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), primary_key=True
    )
    finca: Mapped[Finca] = relationship(back_populates="usuarios")
    usuario: Mapped[Usuario] = relationship(back_populates="fincas")


class Lote(TimestampMixin, Base):
    __tablename__ = "lote"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    area: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    notas: Mapped[str | None] = mapped_column(String(500), nullable=True)
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))
    finca: Mapped[Finca] = relationship(back_populates="lotes")
    __table_args__ = (UniqueConstraint("finca_id", "nombre"),)


class Auditoria(Base):
    __tablename__ = "auditoria"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    finca_id: Mapped[UUID | None] = mapped_column(ForeignKey("finca.id"), nullable=True, index=True)
    operacion: Mapped[str] = mapped_column(String(80))
    recurso: Mapped[str] = mapped_column(String(80))
    recurso_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IdempotencyKey(Base):
    __tablename__ = "idempotency_key"
    clave: Mapped[str] = mapped_column(String(255), primary_key=True)
    operacion: Mapped[str] = mapped_column(String(100), primary_key=True)
    respuesta: Mapped[str] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Ciclo(TimestampMixin, Base):
    __tablename__ = "ciclo"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    estado: Mapped[str] = mapped_column(String(20), default="abierto")
    fecha_inicio: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    siembra_id: Mapped[UUID | None] = mapped_column(ForeignKey("siembra.id"), index=True)
    tipo: Mapped[str | None] = mapped_column(String(12), nullable=True)
    numero: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    motivo_perdida: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_por: Mapped[UUID | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    siembra: Mapped["Siembra | None"] = relationship(back_populates="ciclos")
    __table_args__ = (
        UniqueConstraint("siembra_id", "numero"),
        Index(
            "ix_ciclo_uno_abierto_por_siembra",
            "siembra_id",
            unique=True,
            postgresql_where=text("estado = 'abierto' AND siembra_id IS NOT NULL"),
            sqlite_where=text("estado = 'abierto' AND siembra_id IS NOT NULL"),
        ),
    )


class Actividad(TimestampMixin, Base):
    __tablename__ = "actividad"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    ciclo_id: Mapped[UUID] = mapped_column(ForeignKey("ciclo.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    fase: Mapped[str] = mapped_column(String(80))
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    area_trabajada: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))
    estado: Mapped[str] = mapped_column(String(20), default="activa")


class Trabajador(TimestampMixin, Base):
    __tablename__ = "trabajador"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    tipo: Mapped[str] = mapped_column(String(40))
    jornal_habitual: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    documento_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="activo")


class Jornal(TimestampMixin, Base):
    __tablename__ = "jornal"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    trabajador_id: Mapped[UUID | None] = mapped_column(ForeignKey("trabajador.id"), nullable=True)
    actividad_id: Mapped[UUID] = mapped_column(ForeignKey("actividad.id"), index=True)
    ciclo_id: Mapped[UUID] = mapped_column(ForeignKey("ciclo.id"), index=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    obreros: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    dias: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    valor_jornal: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    modalidad: Mapped[str] = mapped_column(String(30), default="jornal")
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")
    pagado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pagado_por: Mapped[UUID | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    __table_args__ = (UniqueConstraint("trabajador_id", "fecha"),)


class Insumo(TimestampMixin, Base):
    __tablename__ = "insumo"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    unidad: Mapped[str] = mapped_column(String(30))
    existencia: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    estado: Mapped[str] = mapped_column(String(20), default="activo")


class MovimientoInsumo(Base):
    __tablename__ = "movimiento_insumo"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id"), index=True)
    insumo_id: Mapped[UUID] = mapped_column(ForeignKey("insumo.id"), index=True)
    actividad_id: Mapped[UUID | None] = mapped_column(ForeignKey("actividad.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(20))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    costo: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))


class Cosecha(TimestampMixin, Base):
    __tablename__ = "cosecha"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id"), index=True)
    ciclo_id: Mapped[UUID] = mapped_column(ForeignKey("ciclo.id"), index=True)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    unidad: Mapped[str] = mapped_column(String(30))
    calidad: Mapped[str | None] = mapped_column(String(60), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))
    estado: Mapped[str] = mapped_column(String(20), default="activa")


class Proceso(TimestampMixin, Base):
    __tablename__ = "proceso"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    producto: Mapped[str] = mapped_column(String(150))
    materia_prima: Mapped[str] = mapped_column(String(150))
    origen_materia: Mapped[str] = mapped_column(String(20))
    fecha_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))


class EtapaProceso(TimestampMixin, Base):
    __tablename__ = "etapa_proceso"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    proceso_id: Mapped[UUID] = mapped_column(
        ForeignKey("proceso.id", ondelete="CASCADE"), index=True
    )
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    dias_estimados: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    iniciado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finalizado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))
    estado: Mapped[str] = mapped_column(String(20), default="pendiente")


class Gasto(TimestampMixin, Base):
    __tablename__ = "gasto"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id"), index=True)
    ciclo_id: Mapped[UUID | None] = mapped_column(ForeignKey("ciclo.id"), nullable=True)
    categoria: Mapped[str] = mapped_column(String(80))
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estado: Mapped[str] = mapped_column(String(20), default="activo")
    motivo_anulacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    anulado_por: Mapped[UUID | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)
    origen_tipo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    origen_id: Mapped[UUID | None] = mapped_column(nullable=True)


class Ingreso(TimestampMixin, Base):
    __tablename__ = "ingreso"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id"), index=True)
    ciclo_id: Mapped[UUID | None] = mapped_column(ForeignKey("ciclo.id"), nullable=True)
    categoria: Mapped[str] = mapped_column(String(80))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    comprador: Mapped[str | None] = mapped_column(String(150), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estado: Mapped[str] = mapped_column(String(20), default="activo")
    motivo_anulacion: Mapped[str | None] = mapped_column(Text, nullable=True)
    anulado_por: Mapped[UUID | None] = mapped_column(ForeignKey("usuario.id"), nullable=True)


class Venta(TimestampMixin, Base):
    __tablename__ = "venta"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    comprador: Mapped[str | None] = mapped_column(String(150), nullable=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    estado: Mapped[str] = mapped_column(String(20), default="activa")
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))


class LineaVenta(Base):
    __tablename__ = "linea_venta"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    venta_id: Mapped[UUID] = mapped_column(ForeignKey("venta.id", ondelete="CASCADE"), index=True)
    cosecha_id: Mapped[UUID] = mapped_column(ForeignKey("cosecha.id"), index=True)
    categoria: Mapped[str] = mapped_column(String(80))
    unidad: Mapped[str] = mapped_column(String(30))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    merma: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))


class PrecioCategoria(TimestampMixin, Base):
    __tablename__ = "precio_categoria"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    categoria: Mapped[str] = mapped_column(String(80))
    unidad: Mapped[str] = mapped_column(String(30))
    precio: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    vigente_desde: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    vigente_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))


class Especie(TimestampMixin, Base):
    __tablename__ = "especie"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(80))
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)


class LoteAnimal(TimestampMixin, Base):
    __tablename__ = "lote_animal"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    especie_id: Mapped[UUID] = mapped_column(ForeignKey("especie.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    ubicacion: Mapped[str | None] = mapped_column(String(150), nullable=True)


class Animal(TimestampMixin, Base):
    __tablename__ = "animal"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    especie_id: Mapped[UUID] = mapped_column(ForeignKey("especie.id"), index=True)
    lote_animal_id: Mapped[UUID | None] = mapped_column(ForeignKey("lote_animal.id"), nullable=True)
    arete: Mapped[str] = mapped_column(String(80))
    nombre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sexo: Mapped[str] = mapped_column(String(20))
    raza: Mapped[str | None] = mapped_column(String(80), nullable=True)
    nacimiento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    madre_id: Mapped[UUID | None] = mapped_column(ForeignKey("animal.id"), nullable=True)
    padre_id: Mapped[UUID | None] = mapped_column(ForeignKey("animal.id"), nullable=True)
    estado: Mapped[str] = mapped_column(String(30), default="activo")
    __table_args__ = (UniqueConstraint("finca_id", "arete"),)


class EventoAnimal(Base):
    __tablename__ = "evento_animal"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    animal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("animal.id"), nullable=True, index=True
    )
    lote_animal_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("lote_animal.id"), nullable=True, index=True
    )
    tipo: Mapped[str] = mapped_column(String(30))
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    producto: Mapped[str | None] = mapped_column(String(120), nullable=True)
    dosis: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    retiro_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))


class ProduccionAnimal(Base):
    __tablename__ = "produccion_animal"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id"), index=True)
    lote_animal_id: Mapped[UUID] = mapped_column(ForeignKey("lote_animal.id"), index=True)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    tipo: Mapped[str] = mapped_column(String(30))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    unidad: Mapped[str] = mapped_column(String(30))
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))


class AlimentacionAnimal(Base):
    __tablename__ = "alimentacion_animal"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id"), index=True)
    lote_animal_id: Mapped[UUID] = mapped_column(ForeignKey("lote_animal.id"), index=True)
    alimento: Mapped[str] = mapped_column(String(120))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    costo: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    creado_por: Mapped[UUID] = mapped_column(ForeignKey("usuario.id"))


class FuenteAlerta(Base):
    __tablename__ = "fuente_alerta"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(100), unique=True)
    url: Mapped[str] = mapped_column(String(500), unique=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    ultimo_error: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AlertaRegional(Base):
    __tablename__ = "alerta_regional"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    finca_id: Mapped[UUID] = mapped_column(ForeignKey("finca.id", ondelete="CASCADE"), index=True)
    fuente_id: Mapped[UUID] = mapped_column(ForeignKey("fuente_alerta.id"), index=True)
    tipo: Mapped[str] = mapped_column(String(20))
    region_dane: Mapped[str] = mapped_column(String(20), index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    resumen: Mapped[str] = mapped_column(Text)
    vigente_desde: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    vigente_hasta: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
