"""Genera los entregables para Flutter a partir del código.

Crea en docs/: openapi.json, la colección de Postman, mobile_api_contract.md, los modelos Dart
y la configuración de red de Android.

Uso:
    python -m scripts.exportar_contrato              escribe los archivos
    python -m scripts.exportar_contrato --verificar  falla si alguno está desactualizado
"""

import ast
import json
import os
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("AGRO_SECRET_KEY", "clave-solo-para-exportar-el-contrato-0123456789")
os.environ.setdefault("AGRO_DATABASE_URL", "sqlite+aiosqlite://")

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.core.security import RequiereRol, get_usuario_actual
from app.main import ETIQUETAS, create_app

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
PLANTILLAS = Path(__file__).resolve().parent / "plantillas"

CLASES_ERROR = {
    "NoEncontrado": (404, "NO_ENCONTRADO"),
    "Conflicto": (409, "CONFLICTO"),
    "ReglaNegocio": (422, "REGLA_DE_NEGOCIO"),
    "NoAutenticado": (401, "NO_AUTENTICADO"),
    "SinPermiso": (403, "SIN_PERMISO"),
}

ERRORES_GENERALES = [
    ("DATOS_INVALIDOS", 422, "Hay datos que corregir.", "Trae `details` con un mensaje por campo."),
    ("NO_ENCONTRADO", 404, "No encontramos lo que busca.", "La dirección no existe."),
    (
        "FINCA_NO_ENCONTRADA",
        404,
        "No encontramos esa finca.",
        "No existe o no está asignada al usuario.",
    ),
    ("METODO_NO_PERMITIDO", 405, "Esa acción no está disponible en esta dirección.", ""),
    (
        "ERROR_INTERNO",
        500,
        "Algo salió mal de nuestro lado. Intente de nuevo.",
        "Permitir reintentar.",
    ),
]

PANTALLAS = [
    (r"^/health$", "Splash"),
    (r"^/api/v1/politica$", "Autorización de datos"),
    (r"^/api/v1/cuenta/consentimiento$", "Autorización de datos"),
    (r"^/api/v1/glosario$", "Ayuda y glosario"),
    (r"^/api/v1/cultivos$", "Catálogo de cultivos"),
    (r"^/api/v1/cultivos/\{[a-z_]+\}", "Ficha del cultivo"),
    (r"^/api/v1/riesgos$", "Ficha del cultivo (riesgos)"),
    (r"^/api/v1/siembras$", "Mis siembras"),
    (r"^/api/v1/siembras/\{[a-z_]+\}/(conteos|indices)$", "Detalle de siembra (Plantas)"),
    (r"^/api/v1/siembras/\{[a-z_]+\}/ciclos$", "Detalle de siembra (Ciclos)"),
    (r"^/api/v1/siembras/\{[a-z_]+\}", "Detalle de siembra"),
    (r"^/api/v1/ciclos/\{[a-z_]+\}/cronograma$", "Detalle de siembra (Tiempos)"),
    (r"^/api/v1/ciclos/\{[a-z_]+\}", "Detalle de ciclo"),
    (r"^/api/v1/propagacion", "Vivero"),
    (r"^/api/v1/eventos-adversos$", "Eventos adversos"),
    (r"^/api/v1/eventos-adversos/\{[a-z_]+\}$", "Detalle de evento"),
]

ACCIONES_HTTP = ("get", "post", "put", "patch", "delete")
UUID_CERO = "00000000-0000-0000-0000-000000000000"


def _normalizar(texto: str) -> str:
    return texto.replace("\r\n", "\n")


def _leer_plantilla(nombre: str) -> str:
    return _normalizar((PLANTILLAS / nombre).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ rutas, roles y pantallas
def _dependencias(dep: Dependant) -> list[Dependant]:
    salida: list[Dependant] = []
    for sub in dep.dependencies:
        salida.append(sub)
        salida.extend(_dependencias(sub))
    return salida


def roles_de(ruta: APIRoute) -> str:
    dependencias = _dependencias(ruta.dependant)
    for d in dependencias:
        if isinstance(d.call, RequiereRol):
            return ", ".join(d.call.roles)
    if any(d.call is get_usuario_actual for d in dependencias):
        return "cualquier usuario con sesión"
    return "público"


def pantalla_de(path: str) -> str:
    for patron, nombre in PANTALLAS:
        if re.search(patron, path):
            return nombre
    return ""


def _rutas(app: FastAPI) -> list[tuple[str, str, APIRoute]]:
    filas = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            for metodo in sorted(r.methods):
                filas.append((r.path, metodo.lower(), r))
    return filas


def tabla_endpoints(app: FastAPI, contrato: dict[str, Any]) -> str:
    filas = ["| Método | Ruta | Quién entra | Pantalla | Qué hace |", "|---|---|---|---|---|"]
    orden = {"get": 0, "post": 1, "put": 2, "patch": 3, "delete": 4}
    for path, metodo, ruta in sorted(_rutas(app), key=lambda x: (x[0], orden.get(x[1], 9))):
        resumen = contrato["paths"][path][metodo].get("summary", "")
        filas.append(
            f"| `{metodo.upper()}` | `{path}` | {roles_de(ruta)} | "
            f"{pantalla_de(path)} | {resumen} |"
        )
    return "\n".join(filas)


# ------------------------------------------------------------------ códigos de error
def _texto(nodo: ast.expr) -> str:
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str):
        return nodo.value
    if isinstance(nodo, ast.JoinedStr):
        return "".join(p.value if isinstance(p, ast.Constant) else "…" for p in nodo.values)
    return ""


def codigos_de_error() -> dict[str, tuple[int, str]]:
    encontrados: dict[str, tuple[int, str]] = {}
    for archivo in sorted((RAIZ / "app").rglob("*.py")):
        for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"))):
            if not (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)):
                continue
            if nodo.func.id not in CLASES_ERROR:
                continue
            estado, codigo = CLASES_ERROR[nodo.func.id]
            mensaje = _texto(nodo.args[0]) if nodo.args else ""
            if len(nodo.args) > 1:
                codigo = _texto(nodo.args[1]) or codigo
            for kw in nodo.keywords:
                if kw.arg == "codigo":
                    codigo = _texto(kw.value) or codigo
            if mensaje:
                encontrados.setdefault(codigo, (estado, mensaje))
    return encontrados


def tabla_errores() -> str:
    filas = ["| Código (`error`) | Estado | Mensaje de ejemplo | Nota |", "|---|---|---|---|"]
    todos: list[tuple[str, int, str, str]] = [
        (c, e, m, "") for c, (e, m) in codigos_de_error().items()
    ]
    todos.extend(ERRORES_GENERALES)
    vistos: set[str] = set()
    for codigo, estado, mensaje, nota in sorted(todos, key=lambda x: (x[1], x[0])):
        if codigo in vistos:
            continue
        vistos.add(codigo)
        filas.append(f"| `{codigo}` | {estado} | {mensaje} | {nota} |")
    return "\n".join(filas)


# ------------------------------------------------------------------ valores permitidos
def valores_permitidos(contrato: dict[str, Any]) -> str:
    por_campo: dict[str, list[str]] = {}

    def recorrer(esquema: dict[str, Any], campo: str) -> None:
        if "enum" in esquema:
            por_campo.setdefault(campo, [str(v) for v in esquema["enum"]])
        for clave in ("anyOf", "allOf"):
            for sub in esquema.get(clave, []):
                recorrer(sub, campo)
        if "items" in esquema:
            recorrer(esquema["items"], campo)

    for esquema in contrato["components"]["schemas"].values():
        for nombre, prop in esquema.get("properties", {}).items():
            recorrer(prop, nombre)
    for ruta in contrato["paths"].values():
        for operacion in ruta.values():
            for p in operacion.get("parameters", []):
                recorrer(p.get("schema", {}), p["name"])
    filas = ["| Campo | Valores |", "|---|---|"]
    for campo in sorted(por_campo):
        filas.append(f"| `{campo}` | {', '.join(f'`{v}`' for v in por_campo[campo])} |")
    return "\n".join(filas)


# ------------------------------------------------------------------ ejemplos y Postman
def _resolver(contrato: dict[str, Any], esquema: dict[str, Any]) -> dict[str, Any]:
    while "$ref" in esquema:
        esquema = contrato["components"]["schemas"][esquema["$ref"].split("/")[-1]]
    return esquema


def ejemplo(contrato: dict[str, Any], esquema: dict[str, Any], nivel: int = 0) -> object:
    esquema = _resolver(contrato, esquema)
    if "enum" in esquema:
        return esquema["enum"][0]
    if "default" in esquema and esquema["default"] is not None:
        return esquema["default"]
    for clave in ("anyOf", "oneOf"):
        for sub in esquema.get(clave, []):
            if sub.get("type") != "null":
                return ejemplo(contrato, sub, nivel)
    for sub in esquema.get("allOf", []):
        return ejemplo(contrato, sub, nivel)
    tipo = esquema.get("type")
    if tipo == "string":
        formato = esquema.get("format")
        return {"uuid": UUID_CERO, "date": "2026-01-31", "date-time": "2026-01-31T12:00:00Z"}.get(
            formato, "texto"
        )
    if tipo == "integer":
        return int(esquema.get("minimum", esquema.get("exclusiveMinimum", 0) + 1))
    if tipo == "number":
        return esquema.get("minimum", esquema.get("exclusiveMinimum", 0) + 1)
    if tipo == "boolean":
        return True
    if tipo == "array":
        return [] if nivel > 2 else [ejemplo(contrato, esquema.get("items", {}), nivel + 1)]
    if tipo == "object" or "properties" in esquema:
        if nivel > 3:
            return {}
        return {
            nombre: ejemplo(contrato, prop, nivel + 1)
            for nombre, prop in esquema.get("properties", {}).items()
        }
    return None


def _cuerpo_json(operacion: dict[str, Any]) -> dict[str, Any] | None:
    cuerpo = operacion.get("requestBody", {}).get("content", {})
    return cuerpo.get("application/json", {}).get("schema")


def postman(app: FastAPI, contrato: dict[str, Any]) -> dict[str, Any]:
    carpetas: dict[str, list[dict[str, Any]]] = {}
    for path, metodo, ruta in sorted(_rutas(app), key=lambda x: (x[0], x[1])):
        operacion = contrato["paths"][path][metodo]
        etiqueta = (operacion.get("tags") or ["otros"])[0]
        partes = [p for p in path.strip("/").split("/")]
        ruta_pm = ["/".join([f":{p[1:-1]}" if p.startswith("{") else p for p in partes])]
        variables = [
            {"key": p[1:-1], "value": UUID_CERO, "description": "Identificador (uuid)"}
            for p in partes
            if p.startswith("{")
        ]
        consulta = []
        for p in operacion.get("parameters", []):
            if p["in"] == "query":
                valor = ejemplo(contrato, p.get("schema", {}))
                consulta.append(
                    {
                        "key": p["name"],
                        "value": "" if valor is None else str(valor),
                        "disabled": True,
                        "description": p.get("description", ""),
                    }
                )
        peticion: dict[str, Any] = {
            "method": metodo.upper(),
            "header": [],
            "url": {
                "raw": "{{base_url}}/" + ruta_pm[0],
                "host": ["{{base_url}}"],
                "path": ruta_pm,
                "query": consulta,
                "variable": variables,
            },
            "description": operacion.get("summary", ""),
        }
        if roles_de(ruta) == "público":
            peticion["auth"] = {"type": "noauth"}
        esquema = _cuerpo_json(operacion)
        if esquema:
            peticion["header"].append({"key": "Content-Type", "value": "application/json"})
            peticion["body"] = {
                "mode": "raw",
                "raw": json.dumps(ejemplo(contrato, esquema), indent=2, ensure_ascii=False),
                "options": {"raw": {"language": "json"}},
            }
        carpetas.setdefault(etiqueta, []).append(
            {"name": f"{metodo.upper()} {operacion.get('summary', path)}", "request": peticion}
        )
    orden = [t["name"] for t in ETIQUETAS]
    items = [
        {"name": nombre, "item": carpetas[nombre]}
        for nombre in sorted(carpetas, key=lambda n: orden.index(n) if n in orden else 99)
    ]
    return {
        "info": {
            "name": "AgroGestion API",
            "description": "Generada por scripts/exportar_contrato.py. "
            "Pegue un token en la variable "
            "`token`; no guarde credenciales reales aquí.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": {
            "type": "bearer",
            "bearer": [{"key": "token", "value": "{{token}}", "type": "string"}],
        },
        "variable": [
            {"key": "base_url", "value": "http://127.0.0.1:8025"},
            {"key": "token", "value": ""},
        ],
        "item": items,
    }


# ------------------------------------------------------------------ modelos Dart
PALABRAS_RESERVADAS = {
    "class",
    "default",
    "enum",
    "extends",
    "new",
    "null",
    "switch",
    "this",
    "throw",
    "true",
    "false",
    "var",
    "void",
    "with",
    "in",
    "is",
    "as",
    "do",
    "if",
    "else",
    "for",
    "while",
}


@dataclass
class TipoDart:
    tipo: str
    desde: Callable[[str], str]
    hacia: Callable[[str], str]
    nulo: bool = False


def _nombre_clase(nombre: str) -> str:
    return nombre.replace("_", "")


def _camel(nombre: str) -> str:
    partes = nombre.split("_")
    camel = partes[0] + "".join(p.capitalize() for p in partes[1:])
    return camel + "_" if camel in PALABRAS_RESERVADAS else camel


def _tipo_dart(esquema: dict[str, Any]) -> TipoDart:
    if "$ref" in esquema:
        clase = _nombre_clase(esquema["$ref"].split("/")[-1])
        return TipoDart(
            clase,
            lambda e: f"{clase}.fromJson({e} as Map<String, dynamic>)",
            lambda e: f"{e}.toJson()",
        )
    for clave in ("anyOf", "oneOf"):
        if clave in esquema:
            utiles = [s for s in esquema[clave] if s.get("type") != "null"]
            hay_nulo = len(utiles) < len(esquema[clave])
            if len(utiles) == 1:
                t = _tipo_dart(utiles[0])
                return TipoDart(t.tipo, t.desde, t.hacia, hay_nulo)
            tipos = {s.get("type") for s in utiles}
            if tipos <= {"number", "integer", "string"}:
                t = _tipo_dart({"type": "number"})
                return TipoDart(t.tipo, t.desde, t.hacia, hay_nulo)
            return TipoDart("dynamic", lambda e: e, lambda e: e, hay_nulo)
    if "allOf" in esquema and len(esquema["allOf"]) == 1:
        return _tipo_dart(esquema["allOf"][0])
    tipo = esquema.get("type")
    if tipo == "string":
        formato = esquema.get("format")
        if formato == "date":
            return TipoDart(
                "DateTime",
                lambda e: f"DateTime.parse({e} as String)",
                lambda e: f"{e}.toIso8601String().substring(0, 10)",
            )
        if formato == "date-time":
            return TipoDart(
                "DateTime",
                lambda e: f"DateTime.parse({e} as String)",
                lambda e: f"{e}.toUtc().toIso8601String()",
            )
        return TipoDart("String", lambda e: f"{e} as String", lambda e: e)
    if tipo == "integer":
        return TipoDart("int", lambda e: f"{e} as int", lambda e: e)
    if tipo == "number":
        return TipoDart("double", lambda e: f"({e} as num).toDouble()", lambda e: e)
    if tipo == "boolean":
        return TipoDart("bool", lambda e: f"{e} as bool", lambda e: e)
    if tipo == "array":
        dentro = _tipo_dart(esquema.get("items", {}))
        return TipoDart(
            f"List<{dentro.tipo}>",
            lambda e: f"({e} as List<dynamic>).map((x) => {dentro.desde('x')}).toList()",
            lambda e: f"{e}.map((x) => {dentro.hacia('x')}).toList()",
        )
    if tipo == "object":
        return TipoDart(
            "Map<String, dynamic>", lambda e: f"{e} as Map<String, dynamic>", lambda e: e
        )
    return TipoDart("dynamic", lambda e: e, lambda e: e, True)


def _clase_dart(nombre: str, esquema: dict[str, Any]) -> str:
    clase = _nombre_clase(nombre)
    requeridos = set(esquema.get("required", []))
    campos = []
    for original, prop in esquema.get("properties", {}).items():
        t = _tipo_dart(prop)
        nulo = t.nulo or original not in requeridos
        campos.append((original, _camel(original), t, nulo, original in requeridos))
    lineas = [f"class {clase} {{"]
    for _, dart, t, nulo, _req in campos:
        lineas.append(f"  final {t.tipo}{'?' if nulo else ''} {dart};")
    lineas.append("")
    if campos:
        lineas.append(f"  const {clase}({{")
        for _, dart, _t, nulo, req in campos:
            lineas.append(f"    {'required ' if req and not nulo else ''}this.{dart},")
        lineas.append("  });")
    else:
        lineas.append(f"  const {clase}();")
    lineas += ["", f"  factory {clase}.fromJson(Map<String, dynamic> json) => {clase}("]
    for original, dart, t, nulo, _req in campos:
        acceso = f"json['{original}']"
        if nulo:
            lineas.append(f"        {dart}: {acceso} == null ? null : {t.desde(acceso)},")
        else:
            lineas.append(f"        {dart}: {t.desde(acceso)},")
    lineas += ["      );", "", "  Map<String, dynamic> toJson() => {"]
    for original, dart, t, nulo, _req in campos:
        if nulo:
            lineas.append(f"        if ({dart} != null) '{original}': {t.hacia(dart + '!')},")
        else:
            lineas.append(f"        '{original}': {t.hacia(dart)},")
    lineas += ["      };", "}"]
    return "\n".join(lineas)


def modelos_dart(contrato: dict[str, Any]) -> str:
    esquemas = contrato["components"]["schemas"]
    cuerpo = [
        _clase_dart(nombre, esquemas[nombre])
        for nombre in sorted(esquemas)
        if nombre not in ("HTTPValidationError", "ValidationError")
    ]
    cabecera = (
        "// Generado por scripts/exportar_contrato.py desde openapi.json. No editar a mano.\n"
        "// Los listados cerrados (estados, tipos, roles) son String; sus valores están\n"
        "// en mobile_api_contract.md.\n"
    )
    return cabecera + "\n" + "\n\n".join(cuerpo) + "\n"


# ------------------------------------------------------------------ armado de todo
def generar() -> dict[Path, str]:
    app = create_app()
    contrato = app.openapi()
    md = _leer_plantilla("contrato_movil.md")
    md = md.replace("{{VERSION}}", contrato["info"]["version"])
    md = md.replace("{{ENDPOINTS}}", tabla_endpoints(app, contrato))
    md = md.replace("{{ERRORES}}", tabla_errores())
    md = md.replace("{{VALORES}}", valores_permitidos(contrato))
    dumps = {"indent": 2, "ensure_ascii": False}
    return {
        DOCS / "openapi.json": json.dumps(contrato, **dumps) + "\n",
        DOCS / "AgroGestion_Postman_Collection.json": json.dumps(postman(app, contrato), **dumps)
        + "\n",
        DOCS / "mobile_api_contract.md": md,
        DOCS / "dart" / "lib" / "modelos.dart": modelos_dart(contrato),
        DOCS / "dart" / "lib" / "api_config.dart": _leer_plantilla("api_config.dart"),
        DOCS / "dart" / "lib" / "api_exception.dart": _leer_plantilla("api_exception.dart"),
        DOCS / "android" / "network_security_config.xml": _leer_plantilla(
            "network_security_config.xml"
        ),
    }


def desactualizados() -> list[Path]:
    malos = []
    for ruta, contenido in generar().items():
        actual = _normalizar(ruta.read_text(encoding="utf-8")) if ruta.exists() else None
        if actual != _normalizar(contenido):
            malos.append(ruta)
    return malos


def main(argumentos: list[str]) -> int:
    if "--verificar" in argumentos:
        malos = desactualizados()
        for ruta in malos:
            print(f"Desactualizado: {ruta.relative_to(RAIZ)}")
        if malos:
            print("Corra: python -m scripts.exportar_contrato")
        return 1 if malos else 0
    for ruta, contenido in generar().items():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8", newline="\n")
        print(f"Escrito: {ruta.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
