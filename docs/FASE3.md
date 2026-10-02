# Fase 3

## Dependencias detectadas

El repositorio recibido no contiene la implementación completa de M1-M4 ni de todas las historias de M5-M8 descritas en la planificación. Esta fase reutiliza los contratos que sí existen (`FincaUsuario`, `Gasto`, `Ingreso`, `Auditoria` e `IdempotencyKey`) y no inventa entidades de siembra, riesgos M9 o ventas.

## M12 y HU-48

`0003_pecuario_alertas.py` crea las entidades pecuarias y las alertas. Todas las operaciones privadas verifican asignación por `finca_id`. Los documentos de animales no se almacenan en esta versión; los eventos sanitarios conservan `retiro_hasta`. Las fuentes externas requieren HTTPS, host permitido por `ALERT_ALLOWED_HOSTS`, resolución no privada, timeout y ausencia de redirecciones.

La sincronización externa devuelve datos validados para que un servicio de integración pueda persistirlos con idempotencia. No se permite que un usuario envíe una URL arbitraria.

Las pruebas de concurrencia de pagos se limitan deliberadamente a la semántica válida de SQLite: idempotencia y ausencia de doble gasto. La garantía de bloqueo concurrente entre conexiones debe validarse cuando el proyecto adopte PostgreSQL.
