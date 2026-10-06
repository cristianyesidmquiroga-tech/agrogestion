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

Los endpoints de datos no llevan prefijo. En la documentación están ordenados por pasos, empezando por **1. Acceso**. La salud del servicio está en `/health` (sin prefijo).

En la app, la URL base es una constante de compilación (`dart/lib/api_config.dart`):

```bash
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8025
```

## Autenticación

Es lo primero que hace la app, y el único endpoint de datos sin candado (además de la política de datos y la salud del servicio).

1. `POST /auth/login` recibe JSON con `email` y `password`.
2. Responde `{ access_token, token_type, expires_in, rol, nombre }`. El token vale 60 minutos; no hay token de refresco.
3. Todas las demás peticiones llevan `Authorization: Bearer <access_token>`.
4. `GET /auth/me` devuelve quién es, su rol, las fincas que tiene asignadas y `permisos`: la lista de funciones de la API que ese perfil puede usar (grupo, método, ruta y resumen), generada con las mismas reglas que las protegen. Úselo al abrir la app para decidir qué pantallas y botones mostrar; el servidor siempre vuelve a validar.
5. Un `401` significa: borrar el token del almacenamiento seguro y llevar al inicio de sesión.
6. El token se guarda con `flutter_secure_storage`, nunca en `SharedPreferences`.

Errores del inicio de sesión:

| `error.code` | Estado | Cuándo |
|---|---|---|
| `CREDENCIALES_INVALIDAS` | 401 | Correo o contraseña incorrectos. El mensaje es el mismo exista o no el correo |
| `DEMASIADOS_INTENTOS` | 429 | 5 intentos fallidos con el mismo correo en 15 minutos; se libera solo |

Para probar cada perfil en la documentación (`/docs`): arriba hay un panel **Paso 1. Inicie sesión**. Escriba el correo y la contraseña del perfil: la página queda autorizada sola, muestra el token (elija copiar solo el token o toda la respuesta) y lista lo que ese perfil puede usar. Pruebe los pasos de abajo con ese perfil y use **Cambiar de perfil** para entrar con otro. También funciona el flujo manual: `POST /auth/login`, copiar el `access_token` y pegarlo en **Authorize**.

En Postman, la petición de login guarda el token sola en la variable `token`; escriba `correo` y `clave` en las variables de la colección (no suba la colección con valores reales).

Es una versión mínima del acceso, suficiente para probar. La administración de usuarios, el cambio de contraseña y el registro los completa el módulo de acceso (Brayan).

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

## Paginación

`skip` y `limit` en la cadena de consulta. `limit` máximo: **50**; pedir más responde `422`.
La respuesta trae `items`, `total`, `page`, `size` y `has_more`. Detenga el scroll infinito cuando `has_more` sea `false`.

## Formato de error

Todo error tiene la misma forma:

```json
{ "error": { "code": "CODIGO_ESTABLE", "message": "Texto para la persona.", "details": null } }
```

- Decida siempre con `error.code`, nunca con `error.message`: el texto puede cambiar, el código no.
- `error.message` está en español claro y se puede mostrar tal cual.
- `error.details` solo viene en `DATOS_INVALIDOS` (`422` de validación): lista de `{campo, mensaje, tipo}` para pintar el error bajo cada campo.

Cómo reacciona la app según el estado:

| Estado | Qué hace la app |
|---|---|
| `401` | Borra el token y navega al inicio de sesión |
| `403` | Muestra el mensaje y oculta la acción |
| `404` | Muestra que ya no existe y vuelve a la lista |
| `409` | Recarga los datos y avisa del choque |
| `422` | Muestra `error.message`; con `details`, cada mensaje bajo su campo |
| `500` | Muestra `error.message` y permite reintentar |

Ejemplo en Dart (`dart/lib/api_exception.dart`):

```dart
try {
  await api.crearSiembra(datos);
} on ApiException catch (e) {
  switch (e.respuesta.error.code) {
    case 'AREA_SUPERA_LOTE':
      mostrarAviso(e.respuesta.error.message);
    case 'SIEMBRA_ESTADO_INVALIDO':
      recargarSiembra();
    default:
      mostrarAviso(e.respuesta.error.message);
  }
}
```

### Códigos de error

| Código (`error`) | Estado | Mensaje de ejemplo | Nota |
|---|---|---|---|
| `FUENTE_NO_AUTORIZADA` | 400 | La fuente no está autorizada. |  |
| `FUENTE_NO_DISPONIBLE` | 400 | No se pudo validar la fuente. |  |
| `REFERENCIA_NO_VALIDA` | 400 | El ciclo o la actividad no son válidos. |  |
| `CREDENCIALES_INVALIDAS` | 401 | El correo o la contraseña no son válidos. |  |
| `NO_AUTENTICADO` | 401 | Debe autenticarse para continuar. |  |
| `TOKEN_INVALIDO` | 401 | La autenticación no es válida. |  |
| `PERMISO_DENEGADO` | 403 | No tiene permisos para realizar esta operación. |  |
| `ACTIVIDAD_NO_ENCONTRADA` | 404 | La actividad no existe. |  |
| `ANIMAL_NO_ENCONTRADO` | 404 | El animal no pertenece a la finca. |  |
| `CICLO_NO_ENCONTRADO` | 404 | No encontramos ese ciclo. |  |
| `CONSENTIMIENTO_PENDIENTE` | 404 | Aún no ha aceptado el tratamiento de datos. |  |
| `CONSULTA_NO_ENCONTRADA` | 404 | No encontramos esa consulta. |  |
| `COSECHA_NO_ENCONTRADA` | 404 | La cosecha no pertenece a la finca. |  |
| `CULTIVO_NO_ENCONTRADO` | 404 | No encontramos ese cultivo. |  |
| `ESPECIE_NO_ENCONTRADA` | 404 | La especie no pertenece a la finca. |  |
| `ETAPA_NO_ENCONTRADA` | 404 | La etapa no existe. |  |
| `EVENTO_NO_ENCONTRADO` | 404 | No encontramos ese evento. |  |
| `FINCA_NO_ENCONTRADA` | 404 | La finca no existe o no está asignada al usuario. |  |
| `FUENTE_NO_ENCONTRADA` | 404 | La fuente no existe. |  |
| `GASTO_NO_ENCONTRADO` | 404 | El gasto no existe. |  |
| `INGRESO_NO_ENCONTRADO` | 404 | El ingreso no existe. |  |
| `INSUMO_NO_ENCONTRADO` | 404 | El insumo no existe. |  |
| `JORNALE_NO_ENCONTRADO` | 404 | El jornal no existe. |  |
| `LOTE_NO_ENCONTRADO` | 404 | El lote no pertenece a la finca. |  |
| `NO_ENCONTRADO` | 404 | No encontramos lo que busca. | La dirección no existe. |
| `PROBLEMA_NO_ENCONTRADO` | 404 | No encontramos esa ficha. |  |
| `PROCESO_NO_ENCONTRADO` | 404 | El proceso no pertenece a la finca. |  |
| `PROPAGACION_NO_ENCONTRADA` | 404 | No encontramos ese lote de vivero. |  |
| `RIESGO_NO_ENCONTRADO` | 404 | Uno de los riesgos no existe. |  |
| `SIEMBRA_NO_ENCONTRADA` | 404 | No encontramos esa siembra. |  |
| `TRABAJADOR_NO_ENCONTRADO` | 404 | El trabajador no existe. |  |
| `METODO_NO_PERMITIDO` | 405 | Esa acción no está disponible en esta dirección. |  |
| `CANTIDAD_NO_DISPONIBLE` | 409 | La venta supera la cantidad disponible. |  |
| `CICLO_ACTIVO` | 409 | Cierre el ciclo actual antes de abrir otro. |  |
| `CULTIVO_DUPLICADO` | 409 | Ya existe un cultivo con ese nombre. |  |
| `EMAIL_EN_USO` | 409 | El correo electrónico ya está registrado. |  |
| `EXISTENCIA_INSUFICIENTE` | 409 | La existencia no puede quedar negativa. |  |
| `GASTO_YA_ANULADO` | 409 | El gasto ya está anulado. |  |
| `INGRESO_YA_ANULADO` | 409 | El ingreso ya está anulado. |  |
| `JORNALE_DUPLICADO` | 409 | El trabajador ya tiene un jornal registrado ese día. |  |
| `JORNALE_YA_PAGADO` | 409 | El jornal ya fue procesado. |  |
| `POLITICA_DESACTUALIZADA` | 409 | La política cambió. Léala de nuevo antes de aceptar. |  |
| `RIESGO_DUPLICADO` | 409 | Ya existe un riesgo con ese nombre. |  |
| `RIESGO_REPETIDO` | 409 | Un riesgo no puede repetirse en la misma fase. |  |
| `TRANSICION_INVALIDA` | 409 | La etapa no permite esa transición. |  |
| `ACCION_INVALIDA` | 422 | La acción debe ser iniciar o finalizar. |  |
| `ACTIVIDAD_REQUERIDA` | 422 | El consumo debe estar asociado a una actividad. |  |
| `AREA_SUPERA_LOTE` | 422 | El lote solo tiene … hectáreas libres. |  |
| `CICLO_ESTADO_INVALIDO` | 422 | Solo se puede iniciar un ciclo planeado. |  |
| `CICLO_NO_VALIDO` | 422 | Ese ciclo no pertenece a la finca. |  |
| `CICLO_SIN_COSECHA` | 422 | Registre una cosecha o explique el motivo de la pérdida para cerrar el ciclo. |  |
| `CICLO_TIPO_NO_VALIDO` | 422 | Este cultivo tiene un solo ciclo. |  |
| `CONSENTIMIENTO_REQUERIDO` | 422 | Sin aceptar el tratamiento de datos no se puede continuar. |  |
| `CONTEO_INVALIDO` | 422 | Las plantas vivas no pueden superar las … sembradas y resembradas. |  |
| `CONTEO_NO_APLICA` | 422 | Este cultivo se trabaja por área, no por planta. |  |
| `DATOS_INVALIDOS` | 422 | Hay datos que corregir. | Trae `details` con un mensaje por campo. |
| `ESTADO_NO_PERMITIDO` | 422 | Una ficha … no puede pasar a …. |  |
| `EVENTO_FECHAS_INVALIDAS` | 422 | La fecha final no puede ser anterior a la inicial. |  |
| `FECHAS_INVALIDAS` | 422 | La fecha final no puede ser anterior a la inicial. |  |
| `FICHA_INCOMPLETA` | 422 | Para validar, la ficha necesita al menos un síntoma. |  |
| `FICHA_SIN_FUENTE` | 422 | Para validar, cada manejo debe tener su fuente. |  |
| `MES_INVALIDO` | 422 | El mes debe estar entre 1 y 12. |  |
| `METODO_NO_VALIDO` | 422 | Este cultivo no se propaga con ese método. |  |
| `NOTICIA_FECHAS_INVALIDAS` | 422 | La noticia debe vencer después de publicarse. |  |
| `PLANTAS_OBLIGATORIAS` | 422 | Indique cuántas plantas va a sembrar. |  |
| `PROPAGACION_INVALIDA` | 422 | Las germinadas no pueden superar las puestas. |  |
| `SIEMBRA_ESTADO_INVALIDO` | 422 | La siembra ya no admite conteos. |  |
| `SIEMBRA_NO_VALIDA` | 422 | Esa siembra no pertenece a la finca. |  |
| `TRASPLANTE_INVALIDO` | 422 | La siembra debe ser de la misma finca y el mismo cultivo. |  |
| `VIGENCIA_INVALIDA` | 422 | La vigencia del precio no es válida. |  |
| `LIMITE_DE_CONSULTAS` | 429 | Llegó al máximo de consultas de hoy. Mañana podrá hacer más. |  |
| `ERROR_INTERNO` | 500 | Algo salió mal de nuestro lado. Intente de nuevo. | Permitir reintentar. |
| `SERVICIO_NO_LISTO` | 503 | El servicio aún no puede atender. Intente en un momento. |  |

## Formatos de los datos

- Los identificadores son `uuid` en texto.
- Las fechas son `YYYY-MM-DD` y los momentos, ISO 8601 en UTC.
- Los decimales (áreas, dinero, dosis) salen como **número**; el servidor calcula con precisión exacta.
- Las listas cerradas (estados, tipos, roles) llegan como texto; estos son los valores permitidos:

| Campo | Valores |
|---|---|
| `base` | `planta`, `hectarea` |
| `coincidencia` | `alta`, `media`, `baja` |
| `estado` | `borrador`, `validado`, `retirado` |
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
| `valor` | `sirvio`, `no_sirvio`, `equivocado` |
| `valoracion` | `sirvio`, `no_sirvio`, `equivocado` |

## Indicadores explicados

Los índices (por ejemplo `GET /siembras/{id}/indices`) traen sus propios textos: `titulo`, `valor`, `unidad`, `explicacion`, `estado` (`bien`, `atencion`, `alerta` o `informativo`), `que_hacer` y `fecha_datos`. La app los muestra tal cual y no los redacta ni los recalcula. `valor` puede ser `null`.

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
- Sin carga de imágenes en esta versión: el asistente trabaja con texto.
- El asistente responde solo con fichas de la biblioteca marcadas como validadas y no usa inteligencia artificial generativa. La `coincidencia` (alta, media o baja) mide cuánto se parece la descripción a la ficha, no la probabilidad de acierto. Si no hay ficha validada, lo dice y pide asistencia técnica.
- La biblioteca de conocimiento está vacía hasta que un experto cree y valide fichas; los expertos cargan las fuentes.
- Las noticias vencen solas (7 días por defecto) y un proceso diario (`python -m scripts.limpiar_vencidos`) borra las vencidas. No se pueden fijar.
- Los reportes de dinero, mano de obra y procesos aparecen con `disponible: false` y su motivo hasta que existan esos módulos; la pantalla debe mostrarlos como "próximamente".
- El inicio trae fincas, siembras, avisos por fase y eventos recientes; las labores de hoy y los pagos pendientes llegan con los módulos de labores y dinero.
- Los avisos de riesgo por fase necesitan la duración de las fases en el perfil del cultivo; sin ella, la respuesta trae `siembras_sin_calendario` y un aviso.
- El límite de consultas al asistente es de 20 por usuario y día (`429` con el código `LIMITE_DE_CONSULTAS`).
- Toda respuesta trae la cabecera `X-Request-ID`, útil para reportar un problema.
- Los registros que envía la app con mala señal pueden duplicarse hasta que el núcleo agregue la cabecera `Idempotency-Key` (ya permitida en CORS).

## Pendiente de otros módulos

Lo construye Brayan y se suma a este contrato cuando se entregue: inicio de sesión y usuarios, fincas y lotes, labores, jornales y pagos, insumos, cosechas, procesos, dinero, pecuario y alertas regionales automáticas.
