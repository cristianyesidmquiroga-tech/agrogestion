"""Arma los textos claros de cada indicador."""

from datetime import date
from decimal import Decimal

from app.schemas.common import Indicador


def indicadores_de_poblacion(
    vivas: int,
    plantadas: int,
    area_ha: Decimal,
    densidad_ref: int | None,
    ref_por_validar: bool,
    fecha: date,
) -> list[Indicador]:
    fecha_txt = fecha.strftime("%d/%m/%Y")
    densidad = float(Decimal(vivas) / area_ha) if area_ha else None
    referencia = ""
    if densidad_ref:
        marca = " (dato por validar)" if ref_por_validar else ""
        referencia = f" La referencia es de {densidad_ref} plantas por hectárea{marca}."
    indicadores = [
        Indicador(
            titulo="Plantas por hectárea",
            valor=round(densidad, 1) if densidad is not None else None,
            unidad="plantas por hectárea",
            explicacion=(
                "Son las plantas vivas del último conteo divididas entre el área sembrada."
                f"{referencia}"
            ),
            estado="informativo",
            fecha_datos=fecha,
        )
    ]
    if plantadas > 0:
        mortalidad = (plantadas - vivas) / plantadas * 100
        indicadores.append(
            Indicador(
                titulo="Plantas perdidas",
                valor=round(mortalidad, 1),
                unidad="por ciento",
                explicacion=(
                    f"De {plantadas} plantas sembradas y resembradas, hoy hay {vivas} vivas "
                    f"(conteo del {fecha_txt})."
                ),
                estado="informativo",
                que_hacer="Si el número sube, revise la causa y considere resembrar."
                if mortalidad > 0
                else None,
                fecha_datos=fecha,
            )
        )
    return indicadores
