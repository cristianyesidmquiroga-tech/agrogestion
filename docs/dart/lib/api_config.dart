// Generado por scripts/exportar_contrato.py. No editar a mano.
//
// La URL base es una constante de compilación, no un texto suelto por la app:
//   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8025
class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8025',
  );

  static const String prefijo = '';

  static String get api => '$baseUrl$prefijo';
}
