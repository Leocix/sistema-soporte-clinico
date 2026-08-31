/// Constantes de configuracion de la aplicacion del paciente.
class Constantes {
  Constantes._();

  /// URL del API Gateway.
  ///
  /// Se puede sobrescribir al compilar sin tocar el codigo:
  ///   flutter run --dart-define=API_URL=http://10.0.2.2:8000
  ///
  /// Nota para pruebas en el emulador de Android: `localhost` apunta al propio
  /// emulador, no al PC. La direccion del equipo anfitrion es `10.0.2.2`.
  static const String urlApi = String.fromEnvironment(
    'API_URL',
    defaultValue: 'https://cdss-adherencia-api.onrender.com',
  );

  /// El plan gratuito de Render suspende el servicio tras 15 minutos sin
  /// trafico; la primera peticion puede tardar cerca de un minuto en volver.
  static const Duration tiempoDeEspera = Duration(seconds: 90);

  // --- Claves del almacenamiento local ---
  static const String claveToken = 'cdss.token';
  static const String claveUsuario = 'cdss.usuario';
  static const String clavePlan = 'cdss.plan';
  static const String claveCola = 'cdss.cola';

  /// Margen tras el cual una toma cumplida se considera realizada con retraso.
  static const Duration margenPuntualidad = Duration(minutes: 30);
}

/// Formatea una hora como `08:05`, sin depender de paquetes de localizacion.
String formatoHora(DateTime fecha) {
  final h = fecha.hour.toString().padLeft(2, '0');
  final m = fecha.minute.toString().padLeft(2, '0');
  return '$h:$m';
}

/// Formatea una fecha como `01/09/2026`.
String formatoFecha(DateTime fecha) {
  final d = fecha.day.toString().padLeft(2, '0');
  final m = fecha.month.toString().padLeft(2, '0');
  return '$d/$m/${fecha.year}';
}

/// Formatea fecha y hora como `01/09/2026 08:05`.
String formatoFechaHora(DateTime fecha) =>
    '${formatoFecha(fecha)} ${formatoHora(fecha)}';
