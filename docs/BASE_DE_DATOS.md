# Base de datos

La migración `alembic/versions/0001_base.py` crea usuarios, fincas, relación `finca_usuario`, lotes, auditoría e idempotencia. La migración `0002_fase2.py` crea ciclos, actividades, trabajadores, jornales, insumos, movimientos, cosechas, procesos, gastos e ingresos. La migración `0003_pecuario_alertas.py` crea las estructuras de M12 y HU-48. Las migraciones usan tipos UUID compatibles con el backend SQLite actual; PostgreSQL podrá utilizarse posteriormente sin cambiar los modelos.

La bitácora y el registro de idempotencia están disponibles como servicios (`app/services/audit.py` y `app/services/idempotency.py`) para que cada módulo crítico los use dentro de su misma transacción. La ubicación se almacena en la columna cifrada `ubicacion_cifrada`; la clave se configura exclusivamente mediante `FIELD_ENCRYPTION_KEY`.

La migración `0003_pecuario_alertas.py` añade especies, lotes y animales, eventos, producción, alimentación, fuentes y alertas regionales. `alerta_regional` es privada por `finca_id`; `fuente_alerta` no contiene datos de finca y solo acepta URLs HTTPS incluidas en `ALERT_ALLOWED_HOSTS`.

La migración `0004_m5_m7_m8_complementos.py` añade etapas de proceso, ventas y líneas de venta, además de campos de anulación de ingresos.

La migración `0005_crud_y_precios.py` añade estados de baja lógica, historial de precios por categoría/unidad y soporte de consultas de actividades, trabajadores, movimientos e inventario.
