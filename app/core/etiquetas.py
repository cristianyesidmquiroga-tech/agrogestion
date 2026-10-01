"""Grupos de la documentación, en el orden en que se usa la API: primero entrar, luego el resto."""

ACCESO = "1. Acceso"
CUENTA = "2. Cuenta y ayuda"
INICIO = "3. Inicio"
CULTIVOS = "4. Cultivos"
SIEMBRAS = "5. Siembras y ciclos"
VIVERO = "6. Vivero"
EVENTOS = "7. Eventos adversos"
REPORTES = "8. Reportes"
CONOCIMIENTO = "9. Conocimiento"
ASISTENTE = "10. Asistente"
NOTICIAS = "11. Noticias"
SALUD = "12. Salud"

ETIQUETAS = [
    {
        "name": ACCESO,
        "description": "Paso 1. Inicie sesión con su correo y contraseña: la respuesta trae "
        "el token. Cópielo, toque Authorize y péguelo para probar el resto con ese perfil.",
    },
    {"name": CUENTA, "description": "Política de datos, consentimiento y glosario."},
    {"name": INICIO, "description": "Lo de hoy y avisos de riesgo por fase."},
    {"name": CULTIVOS, "description": "Catálogo de cultivos con su perfil y catálogo de riesgos."},
    {"name": SIEMBRAS, "description": "Siembras, ciclos, conteo de plantas e indicadores."},
    {"name": VIVERO, "description": "Propagación por semilla, esqueje u otros métodos."},
    {"name": EVENTOS, "description": "Heladas, sequías, granizo, plagas y otros eventos."},
    {"name": REPORTES, "description": "Reportes con los datos disponibles."},
    {
        "name": CONOCIMIENTO,
        "description": "Biblioteca de problemas sanitarios revisados por expertos.",
    },
    {
        "name": ASISTENTE,
        "description": "Consultas sobre fichas validadas; no inventa diagnósticos.",
    },
    {"name": NOTICIAS, "description": "Noticias de su región que vencen solas."},
    {"name": SALUD, "description": "Salud del servicio."},
]
