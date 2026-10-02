# Matriz de auditoría de Brayan

Estado contra el código real del repositorio. `parcial` significa que existe una parte utilizable, pero faltan criterios de aceptación o pruebas de integración; `bloqueada` indica una dependencia que no existe y pertenece a otro módulo.

| HU | Estado | Evidencia y criterios contrastados |
|---|---|---|
| HU-11 | parcial | `Actividad` valida ciclo abierto, fechas y finca; ahora tiene listado, actualización y anulación. Sigue faltando la relación con siembra.
| HU-23 | completa | Crear, listar, actualizar y anular trabajadores por finca; documento cifrado y nunca expuesto completo.
| HU-24 | parcial | Las cuatro modalidades declaradas por el schema tienen pruebas de cálculo decimal, datos inválidos, duplicados y aislamiento; no existe documentación oficial con fórmulas específicas distintas por modalidad.
| HU-25 | parcial | Pago crea un único gasto, auditoría e idempotencia por clave; SQLite no permite validar la misma concurrencia que PostgreSQL.
| HU-12 | completa | Catálogo, entradas, consumos, historial de movimientos, saldo no negativo e integración de costo de entrada como gasto.
| HU-30 | bloqueada | No existe perfil de cultivo/dosis ni entidad de plantas vivas en el repositorio; no se inventa esa dependencia.
| HU-13 | completa | Registra cosechas por ciclo/finca y expone acumulado e historial filtrado.
| HU-58 | parcial | Procesos, etapas, transición pendiente/en progreso/finalizada, fechas reales y métricas estimadas/reales/diferencia; falta relación con ciclo y acumulado de negocio no definido.
| HU-59 | parcial | Venta, líneas, merma, disponibilidad, ingreso e historial de precios; faltan rendimiento y utilidad por lote.
| HU-14 | completa | Registro, listado filtrable por ciclo, `Numeric(14,2)`, finca, auditoría e idempotencia.
| HU-15 | completa | Registro, listado filtrable por ciclo, total exacto, precisión decimal e idempotencia.
| HU-16 | completa | Anulación lógica de gastos e ingresos, motivo, usuario, auditoría, conservación y exclusión del flujo de caja.
| HU-18 | completa | Flujo mensual por finca y ciclo, ingresos, gastos, saldo y exclusión de anulados.
| HU-54 | parcial | Documentos de trabajadores y ubicación de finca usan cifrado; faltan todos los campos sensibles de módulos pendientes.
| HU-01/HU-05/HU-21/HU-51/HU-52/HU-53/HU-57 | parcial | Base técnica, errores, auditoría de operaciones modificadas, CORS, CI e idempotencia existen; quedan operaciones históricas sin cobertura integral.

## Dependencias de Cristian

HU-30 requiere el perfil agronómico de cultivo, dosis y plantas vivas, que no existe en este repositorio. HU-13 y HU-59 no tienen una entidad de siembra/lote productivo completa; se conserva la relación existente con `cosecha` sin reconstruir M1-M4 ni módulos de Cristian.

## Especificación faltante

No existe en `docs/`, schemas, servicios ni migraciones una especificación funcional que defina fórmulas diferentes para `jornal`, `destajo`, `por_kilo` o `contrato_global`. Se conserva el cálculo vigente y HU-24 permanece parcial para no inventar reglas.
