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
