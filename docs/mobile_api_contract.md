# Contrato de API para la app móvil · AgroGestion v1.0.0

Este archivo se genera con `python -m scripts.exportar_contrato`. No se edita a mano: si cambia la API, se vuelve a generar y el cambio aparece en el Pull Request.

Acompañan a este archivo: `openapi.json` (el contrato), `AgroGestion_Postman_Collection.json`, `dart/lib/` (modelos y configuración para Flutter) y `android/network_security_config.xml`.

## URL base por entorno

| Dónde corre Flutter | URL base | Uvicorn debe correr con | Detalle que se olvida |
|---|---|---|---|
| Emulador de Android | `http://10.0.2.2:8025` | `--host 0.0.0.0` | Con `--host 127.0.0.1` no conecta aunque la IP sea correcta |
| Simulador de iOS | `http://127.0.0.1:8025` | `--host 127.0.0.1` basta | Solo existe en macOS |
| Celular físico (Wi-Fi) | `http://<ip-del-anfitrion>:8025` | `--host 0.0.0.0` | La misma red y el firewall de Windows debe permitir el puerto |
| Celular físico (USB) | `http://127.0.0.1:8025` | `--host 127.0.0.1` | Requiere `adb reverse tcp:8025 tcp:8025` antes |
| Flutter Web (Chrome) | `http://localhost:8025` | `--host 0.0.0.0` | Es el único caso donde CORS importa; correr con `--web-port 3000` |
| Producción | `https://<dominio-de-la-api>` | Detrás de un proxy con TLS | Nunca HTTP sin cifrar fuera de la red local |

Arranque del servidor en desarrollo:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8025
```

Prefijo común de los endpoints de datos: `/api/v1`. La salud del servicio está en `/health` (sin prefijo).

En la app, la URL base es una constante de compilación (`dart/lib/api_config.dart`):

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8025
```

## Autenticación

La construye el módulo de acceso (Brayan). Lo previsto, por confirmar con él al entregarlo:

- `POST /api/v1/auth/login` recibe **formulario**, no JSON. Campos: `username` (el correo) y `password`.
- Devuelve `access_token` con vigencia de 60 minutos. No hay token de refresco.
- Todas las demás peticiones llevan `Authorization: Bearer <token>`.
- Un `401` significa: borrar el token del almacenamiento seguro y llevar al inicio de sesión.
- El token se guarda con `flutter_secure_storage`, nunca en `SharedPreferences`.

Mientras ese módulo no esté, se prueba pegando un token en la variable `token` de Postman.

## Roles

| Rol | Puede |
|---|---|
| `admin` | Todo lo de producción y agregar riesgos al catálogo. Solo ve las fincas que tiene asignadas |
| `agricultor` | Catálogo de cultivos, siembras, ciclos, conteo, vivero y eventos adversos de sus fincas |
| `contador` | Solo lee las siembras y sus ciclos, cronograma e índices |
| `experto` | Solo glosario y política de datos |

Un recurso de otra finca responde `404`, nunca `403`, para no confirmar que existe.

## Endpoints

| Método | Ruta | Quién entra | Pantalla | Qué hace |
|---|---|---|---|---|
| `GET` | `/api/v1/ciclos/{ciclo_id}` | admin, agricultor, contador | Detalle de ciclo | Detalle de un ciclo |
| `POST` | `/api/v1/ciclos/{ciclo_id}/cerrar` | admin, agricultor | Detalle de ciclo | Cerrar un ciclo |
| `GET` | `/api/v1/ciclos/{ciclo_id}/cronograma` | admin, agricultor, contador | Detalle de siembra (Tiempos) | Cronograma planeado del ciclo |
| `POST` | `/api/v1/ciclos/{ciclo_id}/iniciar` | admin, agricultor | Detalle de ciclo | Iniciar un ciclo |
| `GET` | `/api/v1/ciclos/{ciclo_id}/necesidad-insumos` | admin, agricultor, contador | Detalle de ciclo | Cuánto insumo se necesita |
| `GET` | `/api/v1/cuenta/consentimiento` | cualquier usuario con sesión | Autorización de datos | Última autorización aceptada |
| `POST` | `/api/v1/cuenta/consentimiento` | cualquier usuario con sesión | Autorización de datos | Aceptar el tratamiento de datos |
| `GET` | `/api/v1/cultivos` | admin, agricultor | Catálogo de cultivos | Buscar cultivos |
| `POST` | `/api/v1/cultivos` | admin, agricultor | Catálogo de cultivos | Crear un cultivo con su perfil |
| `GET` | `/api/v1/cultivos/{cultivo_id}` | admin, agricultor | Ficha del cultivo | Ver el perfil de un cultivo |
| `PUT` | `/api/v1/cultivos/{cultivo_id}` | admin, agricultor | Ficha del cultivo | Reemplazar el perfil de un cultivo |
| `GET` | `/api/v1/cultivos/{cultivo_id}/dosis` | admin, agricultor | Ficha del cultivo | Dosis de referencia |
| `GET` | `/api/v1/cultivos/{cultivo_id}/fases` | admin, agricultor | Ficha del cultivo | Fases del cultivo |
| `GET` | `/api/v1/cultivos/{cultivo_id}/metodos` | admin, agricultor | Ficha del cultivo | Métodos de propagación |
| `GET` | `/api/v1/cultivos/{cultivo_id}/riesgos` | admin, agricultor | Ficha del cultivo | Riesgos del cultivo |
| `PUT` | `/api/v1/cultivos/{cultivo_id}/riesgos` | admin, agricultor | Ficha del cultivo | Reemplazar los riesgos del cultivo |
| `GET` | `/api/v1/eventos-adversos` | admin, agricultor | Eventos adversos | Eventos adversos |
| `POST` | `/api/v1/eventos-adversos` | admin, agricultor | Eventos adversos | Registrar un evento adverso |
| `GET` | `/api/v1/eventos-adversos/{evento_id}` | admin, agricultor | Detalle de evento | Detalle de un evento |
| `PATCH` | `/api/v1/eventos-adversos/{evento_id}` | admin, agricultor | Detalle de evento | Actualizar un evento |
| `GET` | `/api/v1/glosario` | cualquier usuario con sesión | Ayuda y glosario | Términos del agro explicados |
| `GET` | `/api/v1/politica` | público | Autorización de datos | Política de tratamiento de datos |
| `GET` | `/api/v1/propagacion` | admin, agricultor | Vivero | Lotes de vivero |
| `POST` | `/api/v1/propagacion` | admin, agricultor | Vivero | Crear un lote de vivero |
| `PATCH` | `/api/v1/propagacion/{lote_id}` | admin, agricultor | Vivero | Actualizar germinadas, listas y pérdidas |
| `POST` | `/api/v1/propagacion/{lote_id}/trasplante` | admin, agricultor | Vivero | Pasar plantas listas a una siembra |
| `GET` | `/api/v1/riesgos` | admin, agricultor | Ficha del cultivo (riesgos) | Catálogo de riesgos |
| `POST` | `/api/v1/riesgos` | admin | Ficha del cultivo (riesgos) | Agregar un riesgo al catálogo |
| `GET` | `/api/v1/siembras` | admin, agricultor, contador | Mis siembras | Mis siembras |
| `POST` | `/api/v1/siembras` | admin, agricultor | Mis siembras | Planear una siembra |
| `GET` | `/api/v1/siembras/{siembra_id}` | admin, agricultor, contador | Detalle de siembra | Detalle de una siembra |
| `POST` | `/api/v1/siembras/{siembra_id}/cancelar` | admin, agricultor | Detalle de siembra | Cancelar una siembra |
| `GET` | `/api/v1/siembras/{siembra_id}/ciclos` | admin, agricultor, contador | Detalle de siembra (Ciclos) | Ciclos de una siembra |
| `POST` | `/api/v1/siembras/{siembra_id}/ciclos` | admin, agricultor | Detalle de siembra (Ciclos) | Abrir el siguiente ciclo |
| `GET` | `/api/v1/siembras/{siembra_id}/conteos` | admin, agricultor, contador | Detalle de siembra (Plantas) | Conteos de plantas |
| `POST` | `/api/v1/siembras/{siembra_id}/conteos` | admin, agricultor | Detalle de siembra (Plantas) | Registrar un conteo de plantas |
| `GET` | `/api/v1/siembras/{siembra_id}/indices` | admin, agricultor, contador | Detalle de siembra (Plantas) | Índices por planta |
| `POST` | `/api/v1/siembras/{siembra_id}/iniciar` | admin, agricultor | Detalle de siembra | Iniciar una siembra |
| `POST` | `/api/v1/siembras/{siembra_id}/renovar` | admin, agricultor | Detalle de siembra | Abrir el ciclo de renovación (soqueo) |
| `GET` | `/health` | público | Splash | Salud del servicio |

## Paginación

`skip` y `limit` en la cadena de consulta. `limit` máximo: **50**; pedir más responde `422`.
La respuesta trae `items`, `total`, `page`, `size` y `has_more`. Detenga el scroll infinito cuando `has_more` sea `false`.

## Formato de error

Todo error tiene la misma forma:

```json
{ "error": "CODIGO_ESTABLE", "message": "Texto para la persona.", "status_code": 422, "details": null }
```

- Decida siempre con `error`, nunca con `message`: el texto puede cambiar, el código no.
- `message` está en español claro y se puede mostrar tal cual.
- `details` solo viene en `DATOS_INVALIDOS` (`422` de validación): lista de `{campo, mensaje, tipo}` para pintar el error bajo cada campo.

Cómo reacciona la app según el estado:

| Estado | Qué hace la app |
|---|---|
| `401` | Borra el token y navega al inicio de sesión |
| `403` | Muestra el mensaje y oculta la acción |
| `404` | Muestra que ya no existe y vuelve a la lista |
| `409` | Recarga los datos y avisa del choque |
| `422` | Muestra `message`; con `details`, cada mensaje bajo su campo |
| `500` | Muestra `message` y permite reintentar |

Ejemplo en Dart (`dart/lib/api_exception.dart`):

```dart
try {
  await api.crearSiembra(datos);
} on ApiException catch (e) {
  switch (e.respuesta.error) {
    case 'AREA_SUPERA_LOTE':
      mostrarAviso(e.respuesta.message);
    case 'SIEMBRA_ESTADO_INVALIDO':
      recargarSiembra();
    default:
      mostrarAviso(e.respuesta.message);
  }
}
```

### Códigos de error

| Código (`error`) | Estado | Mensaje de ejemplo | Nota |
|---|---|---|---|
| `NO_AUTENTICADO` | 401 | Su sesión venció o no es válida. Inicie sesión de nuevo. |  |
| `SIN_PERMISO` | 403 | No tiene permiso para esta acción. |  |
| `CICLO_NO_ENCONTRADO` | 404 | No encontramos ese ciclo. |  |
| `CONSENTIMIENTO_PENDIENTE` | 404 | Aún no ha aceptado el tratamiento de datos. |  |
| `CULTIVO_NO_ENCONTRADO` | 404 | No encontramos ese cultivo. |  |
| `EVENTO_NO_ENCONTRADO` | 404 | No encontramos ese evento. |  |
| `FINCA_NO_ENCONTRADA` | 404 | No encontramos esa finca. | No existe o no está asignada al usuario. |
| `LOTE_NO_ENCONTRADO` | 404 | No encontramos ese lote en la finca. |  |
| `NO_ENCONTRADO` | 404 | No encontramos lo que busca. | La dirección no existe. |
| `PROPAGACION_NO_ENCONTRADA` | 404 | No encontramos ese lote de vivero. |  |
| `RIESGO_NO_ENCONTRADO` | 404 | Uno de los riesgos no existe. |  |
| `SIEMBRA_NO_ENCONTRADA` | 404 | No encontramos esa siembra. |  |
| `METODO_NO_PERMITIDO` | 405 | Esa acción no está disponible en esta dirección. |  |
| `CICLO_ACTIVO` | 409 | Cierre el ciclo actual antes de abrir otro. |  |
| `CULTIVO_DUPLICADO` | 409 | Ya existe un cultivo con ese nombre. |  |
| `POLITICA_DESACTUALIZADA` | 409 | La política cambió. Léala de nuevo antes de aceptar. |  |
| `RIESGO_DUPLICADO` | 409 | Ya existe un riesgo con ese nombre. |  |
| `RIESGO_REPETIDO` | 409 | Un riesgo no puede repetirse en la misma fase. |  |
| `AREA_SUPERA_LOTE` | 422 | El lote solo tiene … hectáreas libres. |  |
| `CICLO_ESTADO_INVALIDO` | 422 | Solo se puede iniciar un ciclo planeado. |  |
| `CICLO_NO_VALIDO` | 422 | Ese ciclo no pertenece a la finca. |  |
| `CICLO_SIN_COSECHA` | 422 | Registre una cosecha o explique el motivo de la pérdida para cerrar el ciclo. |  |
| `CICLO_TIPO_NO_VALIDO` | 422 | Este cultivo tiene un solo ciclo. |  |
| `CONSENTIMIENTO_REQUERIDO` | 422 | Sin aceptar el tratamiento de datos no se puede continuar. |  |
| `CONTEO_INVALIDO` | 422 | Las plantas vivas no pueden superar las … sembradas y resembradas. |  |
| `CONTEO_NO_APLICA` | 422 | Este cultivo se trabaja por área, no por planta. |  |
| `DATOS_INVALIDOS` | 422 | Hay datos que corregir. | Trae `details` con un mensaje por campo. |
| `EVENTO_FECHAS_INVALIDAS` | 422 | La fecha final no puede ser anterior a la inicial. |  |
| `METODO_NO_VALIDO` | 422 | Este cultivo no se propaga con ese método. |  |
| `PLANTAS_OBLIGATORIAS` | 422 | Indique cuántas plantas va a sembrar. |  |
| `PROPAGACION_INVALIDA` | 422 | Las germinadas no pueden superar las puestas. |  |
| `SIEMBRA_ESTADO_INVALIDO` | 422 | La siembra ya no admite conteos. |  |
| `SIEMBRA_NO_VALIDA` | 422 | Esa siembra no pertenece a la finca. |  |
| `TRASPLANTE_INVALIDO` | 422 | La siembra debe ser de la misma finca y el mismo cultivo. |  |
| `ERROR_INTERNO` | 500 | Algo salió mal de nuestro lado. Intente de nuevo. | Permitir reintentar. |

## Formatos de los datos

- Los identificadores son `uuid` en texto.
- Las fechas son `YYYY-MM-DD` y los momentos, ISO 8601 en UTC.
- Los decimales (áreas, dinero, dosis) salen como **número**; el servidor calcula con precisión exacta.
- Las listas cerradas (estados, tipos, roles) llegan como texto; estos son los valores permitidos:

| Campo | Valores |
|---|---|
| `base` | `planta`, `hectarea` |
| `estado` | `bien`, `atencion`, `alerta`, `informativo` |
| `fase` | `preparacion`, `siembra`, `mantenimiento`, `cosecha`, `poscosecha`, `renovacion` |
| `fase_critica` | `preparacion`, `siembra`, `mantenimiento`, `cosecha`, `poscosecha`, `renovacion` |
| `metodo` | `semilla`, `esqueje`, `estaca`, `injerto`, `hijuelo`, `acodo`, `in_vitro` |
| `pago_cosecha_sugerido` | `por_kilo`, `por_jornal`, `por_destajo` |
| `severidad` | `leve`, `moderada`, `severa` |
| `susceptibilidad` | `baja`, `media`, `alta` |
| `tipo` | `levante`, `produccion`, `renovacion` |
| `tipo_ciclo` | `transitorio`, `semipermanente`, `permanente`, `forestal` |
| `tipo_renovacion` | `zoca`, `soca`, `poda`, `resiembra` |
| `unidad_conteo` | `planta`, `area` |

## Indicadores explicados

Los índices (por ejemplo `GET /api/v1/siembras/{id}/indices`) traen sus propios textos: `titulo`, `valor`, `unidad`, `explicacion`, `estado` (`bien`, `atencion`, `alerta` o `informativo`), `que_hacer` y `fecha_datos`. La app los muestra tal cual y no los redacta ni los recalcula. `valor` puede ser `null`.

Los valores agronómicos cargados por el equipo llevan `por_validar: true` hasta tener fuente técnica. La app los muestra como estimados.

## Configuración de Android

Android bloquea el tráfico sin cifrar. No active `usesCleartextTraffic` para toda la app: use el archivo `android/network_security_config.xml`, que solo permite HTTP hacia `10.0.2.2` y hacia la IP de desarrollo (cámbiela por la suya), y referencíelo en el manifiesto:

```xml
<application android:networkSecurityConfig="@xml/network_security_config">
```

Para el celular físico por Wi-Fi, permitir el puerto en el firewall de Windows, solo para la red privada:

```powershell
New-NetFirewallRule -DisplayName "AgroGestion dev 8025" -Direction Inbound -LocalPort 8025 -Protocol TCP -Action Allow -Profile Private
```

Para descartar problemas de red: abra en el navegador del celular `http://<ip-del-anfitrion>:8025/health`. Si responde, el problema está en la app.

## Modelos Dart

`dart/lib/modelos.dart` trae una clase por cada esquema del contrato, con `fromJson` y `toJson`, generada desde `openapi.json`. Copie la carpeta `dart/lib` a `lib/api/` de la app. Alternativa con el generador oficial:

```bash
dart pub global activate openapi_generator_cli
openapi-generator generate -i docs/openapi.json -g dart-dio -o lib/api
```

## Limitaciones conocidas

- Sin token de refresco: la sesión caduca a los 60 minutos.
- Sin caché en el servidor: la app debe guardar sus propios datos para trabajar sin conexión.
- Sin carga de imágenes en esta versión (llega con el asistente).
- Los registros que envía la app con mala señal pueden duplicarse hasta que el núcleo agregue la cabecera `Idempotency-Key` (ya permitida en CORS).

## Pendiente de otros módulos

Lo construye Brayan y se suma a este contrato cuando se entregue: inicio de sesión y usuarios, fincas y lotes, labores, jornales y pagos, insumos, cosechas, procesos, dinero, pecuario y alertas.
