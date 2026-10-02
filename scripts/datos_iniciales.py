"""Datos que se cargan una sola vez: perfiles de cultivo (solo estructura), riesgos y glosario.

Ningún número agronómico va aquí: días, dosis y densidades se cargan desde fuente técnica.
"""

FASES_TRANSITORIO = ("preparacion", "siembra", "mantenimiento", "cosecha", "poscosecha")
FASES_PERMANENTE = (*FASES_TRANSITORIO, "renovacion")
FASES_FORESTAL = ("preparacion", "siembra", "mantenimiento", "cosecha")

# nombre, grupo, tipo_ciclo, unidad_conteo, tipo_renovacion, unidad_cosecha, pago, métodos
CULTIVOS = [
    ("Maíz", "cereal", "transitorio", "area", None, "kilo", None, ("semilla",)),
    ("Frijol", "leguminosa", "transitorio", "area", None, "kilo", None, ("semilla",)),
    ("Papa", "tubérculo", "transitorio", "area", None, "kilo", None, ("semilla",)),
    ("Tomate", "hortaliza", "transitorio", "planta", None, "kilo", None, ("semilla",)),
    ("Cilantro", "hortaliza", "transitorio", "area", None, "kilo", None, ("semilla",)),
    ("Yuca", "tubérculo", "semipermanente", "area", "resiembra", "kilo", None, ("estaca",)),
    ("Plátano", "frutal", "semipermanente", "planta", "resiembra", "racimo", None, ("hijuelo",)),
    ("Lulo", "frutal", "semipermanente", "planta", "poda", "kilo", None, ("semilla", "injerto")),
    ("Bijao", "hoja", "semipermanente", "area", "resiembra", "atado", None, ("hijuelo",)),
    ("Café", "plantación", "permanente", "planta", "zoca", "kilo", "por_kilo", ("semilla",)),
    (
        "Cacao",
        "plantación",
        "permanente",
        "planta",
        "poda",
        "kilo",
        None,
        ("semilla", "injerto", "esqueje"),
    ),
    ("Aguacate", "frutal", "permanente", "planta", "poda", "kilo", None, ("semilla", "injerto")),
    ("Cítricos", "frutal", "permanente", "planta", "poda", "kilo", None, ("injerto", "semilla")),
    (
        "Guayabo",
        "frutal",
        "permanente",
        "planta",
        "poda",
        "kilo",
        None,
        ("semilla", "esqueje", "injerto"),
    ),
    ("Caña", "plantación", "permanente", "area", "soca", "tonelada", None, ("estaca",)),
    ("Pasto", "forraje", "permanente", "area", "resiembra", "kilo", None, ("semilla", "esqueje")),
    ("Pino", "maderable", "forestal", "planta", None, "metro cúbico", None, ("semilla",)),
]

RIESGOS = [
    ("Helada", "clima"),
    ("Sequía", "clima"),
    ("Exceso de lluvia", "clima"),
    ("Granizo", "clima"),
    ("Vientos fuertes", "clima"),
    ("Inundación", "clima"),
    ("Fenómeno de El Niño", "clima"),
    ("Fenómeno de La Niña", "clima"),
    ("Plaga", "plaga"),
    ("Enfermedad", "enfermedad"),
    ("Incendio", "otro"),
    ("Deslizamiento", "otro"),
]

# término, explicación, categoría
GLOSARIO = [
    ("Jornal", "Un día de trabajo de una persona.", "mano de obra"),
    ("Cuadrilla", "Grupo de obreros que trabajan juntos en una labor.", "mano de obra"),
    ("Destajo", "Pago por la cantidad de trabajo hecho, no por los días.", "mano de obra"),
    ("Levante", "Etapa desde preparar el terreno hasta la primera producción.", "ciclo"),
    ("Ciclo", "Período de una siembra: levante, producción o renovación.", "ciclo"),
    (
        "Soqueo",
        "Renovar una planta cortándola para que rebrote. Zoca en el café, soca en la caña.",
        "ciclo",
    ),
    ("Zoca", "Corte de una planta productiva, a ras, para que rebrote y se renueve.", "ciclo"),
    ("Soca", "Rebrote de una planta después de cortarla, como en la caña.", "ciclo"),
    ("Socola", "Limpieza del terreno cortando la maleza y el rastrojo antes de sembrar.", "labor"),
    ("Plateo", "Limpiar de maleza el círculo alrededor de la base de una planta.", "labor"),
    ("Trasplante", "Pasar una planta del vivero al lote donde va a producir.", "labor"),
    (
        "Vivero",
        "Lugar donde se cuidan las plantas pequeñas hasta que pueden sembrarse en el lote.",
        "propagación",
    ),
    (
        "Almácigo",
        "Semillero: lugar donde germinan las semillas antes de llevarlas al lote.",
        "propagación",
    ),
    (
        "Esqueje",
        "Trozo de tallo o rama que se siembra para que eche raíces y dé una planta nueva.",
        "propagación",
    ),
    (
        "Injerto",
        "Unión de una parte de una planta con otra para que crezcan como una sola.",
        "propagación",
    ),
    (
        "Hijuelo",
        "Brote que nace al pie de una planta y sirve para sembrar otra, como en el plátano.",
        "propagación",
    ),
    ("Hectárea", "Medida de superficie de 10.000 metros cuadrados.", "medidas"),
    ("Arroba", "Medida de peso de 12,5 kilos.", "medidas"),
    ("Carga", "Medida de peso que cambia según el producto. En el café son 125 kilos.", "medidas"),
    ("Bulto", "Saco. Su peso depende del producto.", "medidas"),
    (
        "Lona",
        "Saco grande en que se empaca y se vende el producto. Su contenido depende del producto.",
        "medidas",
    ),
    ("Densidad", "Cuántas plantas hay en una hectárea.", "indicadores"),
    ("Poscosecha", "Trabajos después de cosechar: secar, seleccionar y empacar.", "labor"),
]
