/// Recordatorios de toma en el dispositivo (RF08).
///
/// RF08 tiene prioridad "Could" y esta programado para el Sprint 4. Su
/// implementacion requiere el paquete `flutter_local_notifications` y
/// configuracion nativa por plataforma: canal de notificaciones y permiso
/// POST_NOTIFICATIONS en Android 13 o superior, y autorizacion explicita en
/// iOS. Esa configuracion no puede darse por hecha, asi que el servicio se
/// deja aqui con su interfaz definida y sin dependencia externa: el resto de
/// la aplicacion ya programa y cancela recordatorios contra este contrato, y
/// activarlos consistira en rellenar estos metodos.
class ServicioNotificaciones {
  ServicioNotificaciones._();

  static final ServicioNotificaciones instancia = ServicioNotificaciones._();

  bool _habilitado = false;

  bool get habilitado => _habilitado;

  /// Solicita el permiso del sistema e inicializa el canal.
  Future<bool> solicitarPermiso() async {
    // Sprint 4: inicializar flutter_local_notifications y pedir el permiso.
    _habilitado = false;
    return _habilitado;
  }

  /// Programa el aviso de una dosis concreta.
  Future<void> programarRecordatorio({
    required int id,
    required String medicamento,
    required DateTime cuando,
  }) async {
    if (!_habilitado) return;
    // Sprint 4: zonedSchedule con repeticion diaria.
  }

  /// Cancela los avisos ya programados, p. ej. al cambiar el plan de tomas.
  Future<void> cancelarTodos() async {
    if (!_habilitado) return;
    // Sprint 4: cancelAll().
  }
}
