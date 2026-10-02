// Generado por scripts/exportar_contrato.py. No editar a mano.
import 'dart:convert';

import 'modelos.dart';

/// Error devuelto por la API. Decida con `respuesta.error.code`, nunca con `message`.
class ApiException implements Exception {
  final ErrorRespuesta respuesta;

  final int statusCode;

  const ApiException(this.respuesta, this.statusCode);

  /// Lee el cuerpo de una respuesta con error. Si no tiene el formato esperado
  /// (por ejemplo, una página de un proxy), arma un error genérico.
  factory ApiException.desde(int statusCode, String cuerpo) {
    try {
      final json = jsonDecode(cuerpo) as Map<String, dynamic>;
      return ApiException(ErrorRespuesta.fromJson(json), statusCode);
    } catch (_) {
      return ApiException(
        ErrorRespuesta(
          error: ErrorDetalle(
            code: 'ERROR_DE_RED',
            message: 'No pudimos completar la petición. Intente de nuevo.',
          ),
        ),
        statusCode,
      );
    }
  }

  /// Un 401 significa: borrar el token y volver al inicio de sesión.
  bool get sesionVencida => statusCode == 401;

  @override
  String toString() => '${respuesta.error.code}: ${respuesta.error.message}';
}
