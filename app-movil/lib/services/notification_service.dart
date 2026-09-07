import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/data/latest_all.dart' as datos_zonas;
import 'package:timezone/timezone.dart' as tz;

import '../models/medicamento.dart';

/// Recordatorios de toma en el dispositivo (RF08).
///
/// Responde a la brecha B4 del diagnostico: el olvido es la primera causa de
/// incumplimiento que refirio el medico, y hasta ahora la aplicacion solo
/// registraba la toma sin ayudar a recordarla.
///
/// Los avisos se programan **en el telefono**, no se envian desde el servidor.
/// Es lo que corresponde a un paciente que puede estar sin cobertura justo a la
/// hora de su medicacion: un recordatorio que dependiera de la red fallaria
/// precisamente en el escenario que mas lo necesita.
class ServicioNotificaciones {
  ServicioNotificaciones._();

  static final ServicioNotificaciones instancia = ServicioNotificaciones._();

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();

  static const String _canalId = 'recordatorios_toma';
  static const String _canalNombre = 'Recordatorios de medicación';
  static const String _canalDescripcion =
      'Avisos a la hora de cada toma indicada por su médico.';

  bool _iniciado = false;
  bool _permitido = false;

  bool get permitido => _permitido;

  /// Prepara el complemento y la base de zonas horarias.
  ///
  /// La zona horaria importa: `zonedSchedule` necesita saber en que huso vive
  /// el paciente para que «las 8 de la mañana» sean sus ocho y no las del
  /// servidor. Se consulta al sistema en lugar de fijar Lima, para que la
  /// aplicacion siga siendo correcta si el paciente viaja.
  Future<void> iniciar() async {
    if (_iniciado) return;

    datos_zonas.initializeTimeZones();
    try {
      // `getLocalTimezone` devuelve un objeto; el identificador IANA que
      // necesita la base de zonas horarias esta en `identifier`.
      final zona = await FlutterTimezone.getLocalTimezone();
      tz.setLocalLocation(tz.getLocation(zona.identifier));
    } catch (_) {
      // Si el sistema no informa la zona, se asume la del consultorio.
      tz.setLocalLocation(tz.getLocation('America/Lima'));
    }

    await _plugin.initialize(
      settings: const InitializationSettings(
        android: AndroidInitializationSettings('@mipmap/ic_launcher'),
        iOS: DarwinInitializationSettings(
          // El permiso se pide de forma explicita mas abajo, no al arrancar:
          // un aviso de permisos antes de que el paciente entienda para que
          // sirve se rechaza casi siempre.
          requestAlertPermission: false,
          requestBadgePermission: false,
          requestSoundPermission: false,
        ),
      ),
    );

    _iniciado = true;
    // Se consulta el estado real del sistema, no se asume. El permiso vive en
    // los ajustes del telefono y sobrevive al cierre de la aplicacion: darlo
    // por denegado en cada arranque hacia que `reprogramar` no hiciera nada
    // hasta que el paciente volviera a pulsar «Activar», de modo que cambiar
    // una hora de toma dejaba en pie el aviso viejo sin que nada lo indicara.
    await comprobarPermiso();
  }

  /// Estado actual del permiso segun el sistema operativo.
  ///
  /// El paciente puede haberlo concedido en una sesion anterior, o haberlo
  /// retirado desde los ajustes sin pasar por la aplicacion. La unica fuente
  /// fiable es el propio sistema.
  Future<bool> comprobarPermiso() async {
    if (defaultTargetPlatform == TargetPlatform.android) {
      final android = _plugin.resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin>();
      _permitido = await android?.areNotificationsEnabled() ?? false;
    } else if (defaultTargetPlatform == TargetPlatform.iOS) {
      final ios = _plugin.resolvePlatformSpecificImplementation<
          IOSFlutterLocalNotificationsPlugin>();
      final estado = await ios?.checkPermissions();
      _permitido = estado?.isEnabled ?? false;
    }
    return _permitido;
  }

  /// Solicita el permiso del sistema para mostrar avisos.
  Future<bool> solicitarPermiso() async {
    await iniciar();

    if (defaultTargetPlatform == TargetPlatform.android) {
      final android = _plugin.resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin>();
      // Android 13 y superiores exigen POST_NOTIFICATIONS en tiempo de
      // ejecucion; en versiones anteriores el metodo devuelve verdadero.
      _permitido = await android?.requestNotificationsPermission() ?? false;
    } else if (defaultTargetPlatform == TargetPlatform.iOS) {
      final ios = _plugin.resolvePlatformSpecificImplementation<
          IOSFlutterLocalNotificationsPlugin>();
      _permitido = await ios?.requestPermissions(
              alert: true, badge: true, sound: true) ??
          false;
    }
    return _permitido;
  }

  /// Reprograma los recordatorios de todo el plan de tomas.
  ///
  /// Se cancelan todos antes de volver a crearlos: si el paciente quita un
  /// medicamento o cambia una hora, un aviso viejo seguiria sonando y le diria
  /// que tome algo que ya no toma.
  Future<void> reprogramar(List<Medicamento> plan) async {
    await iniciar();
    if (!_permitido && !await comprobarPermiso()) return;

    await _plugin.cancelAll();

    for (var iMedicamento = 0; iMedicamento < plan.length; iMedicamento++) {
      final medicamento = plan[iMedicamento];
      for (var iHora = 0; iHora < medicamento.horarios.length; iHora++) {
        final partes = medicamento.horarios[iHora].split(':');
        if (partes.length != 2) continue;
        final hora = int.tryParse(partes[0]);
        final minuto = int.tryParse(partes[1]);
        if (hora == null || minuto == null) continue;

        await _programarDiario(
          id: idDeAviso(iMedicamento, iHora),
          titulo: 'Hora de su medicación',
          cuerpo: medicamento.dosis.isEmpty
              ? 'Le toca ${medicamento.nombre}.'
              : 'Le toca ${medicamento.nombre} · ${medicamento.dosis}.',
          hora: hora,
          minuto: minuto,
        );
      }
    }
  }

  Future<void> _programarDiario({
    required int id,
    required String titulo,
    required String cuerpo,
    required int hora,
    required int minuto,
  }) async {
    await _plugin.zonedSchedule(
      id: id,
      title: titulo,
      body: cuerpo,
      scheduledDate: _proximaOcurrencia(hora, minuto),
      notificationDetails: const NotificationDetails(
        android: AndroidNotificationDetails(
          _canalId,
          _canalNombre,
          channelDescription: _canalDescripcion,
          importance: Importance.max,
          priority: Priority.high,
          // El paciente objetivo es un adulto mayor: el aviso debe verse en la
          // pantalla de bloqueo sin tener que desplegar la bandeja.
          category: AndroidNotificationCategory.reminder,
          visibility: NotificationVisibility.public,
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
      // `inexact` no requiere el permiso de alarmas exactas, que Android
      // reserva para relojes y calendarios. Para un recordatorio de medicacion
      // un margen de minutos es aceptable y evita pedir un permiso que el
      // sistema puede denegar.
      androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
      matchDateTimeComponents: DateTimeComponents.time, // se repite cada día
    );
  }

  tz.TZDateTime _proximaOcurrencia(int hora, int minuto) =>
      proximaOcurrencia(hora, minuto, tz.TZDateTime.now(tz.local));

  /// Primera ocurrencia futura de esa hora: hoy si aún no pasó, mañana si sí.
  ///
  /// Se expone y recibe el instante de referencia para poder verificarla sin
  /// depender del reloj ni de los canales nativos. Es la pieza con más
  /// probabilidad de fallar en silencio: un recordatorio programado en el
  /// pasado no suena nunca y el paciente no tiene forma de notarlo.
  @visibleForTesting
  static tz.TZDateTime proximaOcurrencia(
    int hora,
    int minuto,
    tz.TZDateTime referencia,
  ) {
    var momento = tz.TZDateTime(
      referencia.location,
      referencia.year,
      referencia.month,
      referencia.day,
      hora,
      minuto,
    );
    if (!momento.isAfter(referencia)) {
      momento = momento.add(const Duration(days: 1));
    }
    return momento;
  }

  /// Identificador estable de un aviso dentro del plan.
  ///
  /// Reprogramar debe sustituir el aviso anterior, no acumular uno nuevo: si
  /// el identificador cambiara, el paciente acabaria recibiendo dos avisos por
  /// la misma dosis.
  @visibleForTesting
  static int idDeAviso(int indiceMedicamento, int indiceHorario) =>
      indiceMedicamento * 100 + indiceHorario;

  /// Cantidad de avisos actualmente programados; se usa para informar al
  /// paciente de que sus recordatorios están activos.
  Future<int> programados() async {
    await iniciar();
    final pendientes = await _plugin.pendingNotificationRequests();
    return pendientes.length;
  }

  /// Estado de los recordatorios tal como debe verlo el paciente.
  ///
  /// Que el permiso este concedido y que haya avisos en cola son dos cosas
  /// distintas —se puede tener permiso y ningun medicamento registrado— y la
  /// pantalla necesita distinguirlas para decir algo util en cada caso.
  Future<({bool permitido, int avisos})> estado() async {
    await iniciar();
    return (permitido: await comprobarPermiso(), avisos: await programados());
  }

  Future<void> cancelarTodos() async {
    await iniciar();
    await _plugin.cancelAll();
  }
}
