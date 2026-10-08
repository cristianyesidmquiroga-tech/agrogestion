import re
import httpx
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.proyeccion import ProyeccionAgricolaEntrada, ProyeccionAgricolaSalida
from app.services import cultivo_service


async def obtener_precio_mercado(cultivo_nombre: str) -> Decimal:
    """
    Busca automáticamente en la web el precio actual del cultivo.
    Esto es un Web Scraper básico que intenta leer de páginas públicas.
    """
    precio_por_defecto = Decimal("12000") # $12,000 por Kg si falla el internet

    # Ejemplo específico para Café (intentaríamos leer el precio interno)
    if "cafe" in cultivo_nombre.lower() or "café" in cultivo_nombre.lower():
        try:
            # Buscamos en una página económica genérica o la FNC (aquí simulamos con Dolar-Colombia o similar)
            # Nota: El web scraping puede romperse si la página cambia su diseño HTML.
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://federaciondecafeteros.org/wp/servicios-al-caficultor/precio-interno/")
                if response.status_code == 200:
                    # Usamos una expresión regular para encontrar patrones de precio como "$ 2,250,000"
                    match = re.search(r'\$\s*([0-9.,]+)', response.text)
                    if match:
                        precio_str = match.group(1).replace(",", "").replace(".", "")
                        precio_carga = Decimal(precio_str)
                        # Asumiendo carga de 125 kg, sacamos el precio por kg:
                        return precio_carga / Decimal("125")
        except Exception as e:
            print(f"Error buscando precio en internet: {e}")
            pass # Si falla, continúa al valor por defecto
            
    # Si es otro cultivo o falló el internet, usa precios base del sistema
    precios_base = {
        "cacao": Decimal("15000"),
        "maiz": Decimal("1800"),
        "maíz": Decimal("1800"),
        "caña": Decimal("2500"),
    }
    for clave, valor in precios_base.items():
        if clave in cultivo_nombre.lower():
            return valor

    return precio_por_defecto


async def calcular_proyeccion_agricola(
    db: AsyncSession, datos: ProyeccionAgricolaEntrada
) -> ProyeccionAgricolaSalida:
    cultivo = await cultivo_service.obtener(db, datos.cultivo_id)

    area_ha = datos.area_m2 / Decimal("10000")

    densidad = cultivo.densidad_ref or 0
    plantas_estimadas = int(area_ha * densidad)

    # Costos simulados como base para la proyección
    costo_por_planta = Decimal("1500")
    costo_semilla_estimado = plantas_estimadas * costo_por_planta

    # Costo estimado de abono por planta al año
    costo_abono_estimado = plantas_estimadas * Decimal("2000")

    # BUSCAMOS EL PRECIO ACTUAL EN INTERNET
    precio_por_kg = await obtener_precio_mercado(cultivo.nombre)

    # Estimación de ingresos (rendimiento promedio * precio actual)
    rendimiento_por_planta = Decimal("2.5")  # Ejemplo: 2.5 kg por planta
    ingreso_estimado_anual = plantas_estimadas * rendimiento_por_planta * precio_por_kg

    # Utilidad estimada
    utilidad_estimada_anual = ingreso_estimado_anual - (
        costo_semilla_estimado + costo_abono_estimado
    )

    return ProyeccionAgricolaSalida(
        area_m2=datos.area_m2,
        cultivo_nombre=cultivo.nombre,
        plantas_estimadas=plantas_estimadas,
        meses_primera_cosecha=cultivo.meses_primera_cosecha,
        cosechas_por_anio=cultivo.cosechas_por_anio,
        costo_semilla_estimado=costo_semilla_estimado,
        costo_abono_estimado=costo_abono_estimado,
        ingreso_estimado_anual=ingreso_estimado_anual,
        utilidad_estimada_anual=utilidad_estimada_anual,
    )
