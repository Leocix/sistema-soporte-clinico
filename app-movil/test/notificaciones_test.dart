// Pruebas de los recordatorios de toma (RF08).
//
// Cubren la lógica que no depende de los canales nativos: cuándo debe sonar el
// próximo aviso y cómo se identifica cada uno. Es donde un fallo pasaría
// inadvertido —un recordatorio programado en el pasado no suena nunca y el
// paciente no tiene forma de darse cuenta—, así que conviene fijarlo aquí.

import 'package:cdss_adherencia/services/notification_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:timezone/data/latest_all.dart' as datos_zonas;
import 'package:timezone/timezone.dart' as tz;

void main() {
  late tz.Location lima;

  setUpAll(() {
    datos_zonas.initializeTimeZones();
    lima = tz.getLocation('America/Lima');
  });

  group('próxima ocurrencia del recordatorio', () {
    test('si la hora aún no ha pasado, el aviso es hoy', () {
      final ahora = tz.TZDateTime(lima, 2026, 9, 5, 7, 30);

      final aviso = ServicioNotificaciones.proximaOcurrencia(8, 0, ahora);

      expect(aviso.day, 5);
      expect(aviso.hour, 8);
      expect(aviso.minute, 0);
    });

    test('si la hora ya pasó, el aviso es mañana', () {
      final ahora = tz.TZDateTime(lima, 2026, 9, 5, 9, 15);

      final aviso = ServicioNotificaciones.proximaOcurrencia(8, 0, ahora);

      expect(aviso.day, 6);
      expect(aviso.hour, 8);
    });

    test('justo a la hora en punto el aviso pasa al día siguiente', () {
      // Programarlo para el instante exacto lo dejaría en el pasado en cuanto
      // termine de registrarse, y no sonaría.
      final ahora = tz.TZDateTime(lima, 2026, 9, 5, 8, 0);

      final aviso = ServicioNotificaciones.proximaOcurrencia(8, 0, ahora);

      expect(aviso.day, 6);
    });

    test('el aviso nunca queda en el pasado', () {
      final ahora = tz.TZDateTime(lima, 2026, 9, 5, 23, 59);

      for (final hora in [0, 6, 12, 18, 23]) {
        final aviso = ServicioNotificaciones.proximaOcurrencia(hora, 0, ahora);
        expect(aviso.isAfter(ahora), isTrue,
            reason: 'el aviso de las $hora:00 quedó en el pasado');
      }
    });

    test('cruzar el fin de mes no descoloca la fecha', () {
      final ahora = tz.TZDateTime(lima, 2026, 9, 30, 22, 0);

      final aviso = ServicioNotificaciones.proximaOcurrencia(8, 0, ahora);

      expect(aviso.month, 10);
      expect(aviso.day, 1);
    });
  });

  group('identificador del aviso', () {
    test('es estable para el mismo medicamento y horario', () {
      expect(ServicioNotificaciones.idDeAviso(2, 3),
          ServicioNotificaciones.idDeAviso(2, 3));
    });

    test('no colisiona entre medicamentos ni entre horarios', () {
      final vistos = <int>{};
      for (var medicamento = 0; medicamento < 12; medicamento++) {
        for (var horario = 0; horario < 8; horario++) {
          final id = ServicioNotificaciones.idDeAviso(medicamento, horario);
          expect(vistos.add(id), isTrue,
              reason: 'el id $id se repite en ($medicamento, $horario)');
        }
      }
    });
  });
}
