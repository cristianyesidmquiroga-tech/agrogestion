import uuid
from datetime import date

from app.schemas.common import Decimal2, Salida


class ResumenGeneral(Salida):
    usuarios: int
    usuarios_activos: int
    usuarios_por_rol: dict[str, int]
    fincas: int
    area_ha_fincas: Decimal2
    siembras: int
    siembras_por_estado: dict[str, int]
    ciclos_abiertos: int
    ciclos_cerrados: int
    cosechas: int
    trabajadores: int
    gastos: Decimal2
    ingresos: Decimal2
    utilidad: Decimal2
    eventos_adversos: int
    perdida_estimada: Decimal2


class PuntoMensual(Salida):
    mes: str
    usuarios: int
    fincas: int
    siembras: int
    cosechas: int
    gastos: Decimal2
    ingresos: Decimal2


class TotalPorCategoria(Salida):
    categoria: str
    registros: int
    total: Decimal2


class CostosGenerales(Salida):
    gastos_por_categoria: list[TotalPorCategoria]
    ingresos_por_categoria: list[TotalPorCategoria]
    gastos: Decimal2
    ingresos: Decimal2
    area_sembrada_ha: Decimal2
    gasto_por_ha: Decimal2 | None
    ingreso_por_ha: Decimal2 | None


class CantidadPorUnidad(Salida):
    unidad: str
    cantidad: Decimal2


class EstadisticaCultivo(Salida):
    cultivo_id: uuid.UUID
    cultivo: str
    grupo: str
    siembras: int
    fincas: int
    agricultores: int
    area_ha: Decimal2
    plantas: int
    ciclos_abiertos: int
    ciclos_cerrados: int
    duracion_media_dias: float | None
    ciclo_mas_largo_dias: int | None
    cosechas: int
    produccion: list[CantidadPorUnidad]
    primera_cosecha: date | None
    ultima_cosecha: date | None
    dias_entre_cosechas: float | None
    gastos: Decimal2
    ingresos: Decimal2
    utilidad: Decimal2


class EstadisticaZona(Salida):
    zona: str
    fincas: int
    agricultores: int
    area_ha_fincas: Decimal2
    siembras: int
    area_sembrada_ha: Decimal2
    cosechas: int
    produccion: list[CantidadPorUnidad]
    gastos: Decimal2
    ingresos: Decimal2
    utilidad: Decimal2
    gasto_por_ha: Decimal2 | None
    cultivos_principales: list[str]


class CosechaRegistrada(Salida):
    id: uuid.UUID
    fecha: date
    cultivo: str
    cantidad: Decimal2
    unidad: str
    calidad: str | None
    finca: str
    zona: str
    agricultor: str | None


class SiembraRegistrada(Salida):
    id: uuid.UUID
    cultivo: str
    estado: str
    area_ha: Decimal2
    plantas: int | None
    fecha_plan: date
    inicio_ciclo: date | None
    finca: str
    zona: str
    agricultor: str | None


class Productor(Salida):
    usuario_id: uuid.UUID
    nombre: str
    fincas: int
    cosechas: int
    produccion: list[CantidadPorUnidad]
    ultima_cosecha: date | None


class ManoDeObraZona(Salida):
    zona: str
    trabajadores: int
    jornales: int
    pendiente: Decimal2
    pagado: Decimal2


class ManoDeObraGeneral(Salida):
    trabajadores: int
    trabajadores_por_tipo: dict[str, int]
    jornales: int
    jornales_pendientes: int
    total_pendiente: Decimal2
    jornales_pagados: int
    total_pagado: Decimal2
    por_modalidad: list[TotalPorCategoria]
    por_zona: list[ManoDeObraZona]


class InsumoConsumido(Salida):
    nombre: str
    unidad: str
    consumido: Decimal2


class ExistenciaPorUnidad(Salida):
    unidad: str
    insumos: int
    existencia: Decimal2


class InventarioGeneral(Salida):
    insumos: int
    agotados: int
    entradas: int
    costo_entradas: Decimal2
    consumos: int
    por_unidad: list[ExistenciaPorUnidad]
    mas_consumidos: list[InsumoConsumido]


class ProcesoPorProducto(Salida):
    producto: str
    procesos: int
    finalizados: int
    duracion_media_dias: float | None


class ProcesosGeneral(Salida):
    procesos: int
    en_curso: int
    finalizados: int
    duracion_media_dias: float | None
    por_origen: dict[str, int]
    etapas: int
    etapas_finalizadas: int
    etapas_con_retraso: int
    por_producto: list[ProcesoPorProducto]
