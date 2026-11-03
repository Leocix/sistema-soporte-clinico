// Pruebas de caja blanca de la aplicacion movil.
//
//   CB-08 · TarjetaToma.build (V(G) = 5)
//   CB-09 · _Respuesta.build  (V(G) = 5: hora, motivo con dos condiciones, corroborada)
//   CB-10 · ServicioSincronizacion.registrar   (V(G) = 4)
//   CB-11 · ServicioSincronizacion.sincronizar (V(G) = 6)
//
// La tarjeta decide que mostrar segun el estado de la dosis: la respuesta ya
// dada, la espera antes de que abra la ventana, los dos botones o solo
// «No la tomé» si la ventana cerro; ademas, el aviso de envio pendiente. Un
// caso por camino independiente. El analisis esta en el anexo de caja blanca.

import 'dart:convert';

import 'package:cdss_adherencia/models/toma.dart';
import 'package:cdss_adherencia/services/almacenamiento.dart';
import 'package:cdss_adherencia/services/api_service.dart';
import 'package:cdss_adherencia/services/sincronizacion.dart';
import 'package:cdss_adherencia/widgets/tarjeta_toma.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

Future<void> _mostrar(WidgetTester tester, DosisDelDia dosis) async {
  await tester.pumpWidget(MaterialApp(
    home: Scaffold(
      body: SingleChildScrollView(
        child: TarjetaToma(dosis: dosis, alConfirmar: () {}, alOmitir: () {}),
      ),
    ),
  ));
}

DosisDelDia _dosis(Duration desdeAhora, {Toma? registro, bool pendiente = false}) {
  return DosisDelDia(
    medicamento: 'Losartán 50 mg',
    dosis: '50 mg',
    programada: DateTime.now().add(desdeAhora),
    registro: registro,
    pendienteDeEnvio: pendiente,
  );
}

void main() {
  group('CB-08 TarjetaToma', () {
    testWidgets('C1: respondida -> muestra el estado, sin botones',
        (tester) async {
      final programada = DateTime.now().subtract(const Duration(minutes: 30));
      await _mostrar(
        tester,
        _dosis(const Duration(minutes: -30),
            registro: Toma(
              medicamento: 'Losartán 50 mg',
              dosis: '50 mg',
              fechaHoraProgramada: programada,
              fechaHoraRegistro: programada,
              estado: EstadoToma.tomada,
            )),
      );
      expect(find.text('Tomada'), findsOneWidget);
      expect(find.text('Ya la tomé'), findsNothing);
    });

    testWidgets('C2: antes de que abra la ventana -> espera, sin botones',
        (tester) async {
      await _mostrar(tester, _dosis(const Duration(hours: 3)));
      expect(find.textContaining('Podrá registrarla desde las'), findsOneWidget);
      expect(find.text('Ya la tomé'), findsNothing);
      expect(find.text('No la tomé'), findsNothing);
    });

    testWidgets('C3: ventana abierta -> los dos botones', (tester) async {
      await _mostrar(tester, _dosis(const Duration(minutes: -10)));
      expect(find.text('Ya la tomé'), findsOneWidget);
      expect(find.text('No la tomé'), findsOneWidget);
    });

    testWidgets('C4: ventana cerrada -> solo «No la tomé» y el aviso del plazo',
        (tester) async {
      await _mostrar(tester, _dosis(const Duration(hours: -4)));
      expect(find.text('Ya la tomé'), findsNothing);
      expect(find.text('No la tomé'), findsOneWidget);
      expect(find.textContaining('El plazo para marcarla como tomada terminó'),
          findsOneWidget);
    });

    testWidgets('C5: pendiente de envío -> ícono de nube tachada',
        (tester) async {
      await _mostrar(
          tester, _dosis(const Duration(minutes: -10), pendiente: true));
      expect(find.byIcon(Icons.cloud_off), findsOneWidget);
    });
  });

  group('CB-09 respuesta registrada', () {
    final programada = DateTime.now().subtract(const Duration(hours: 1));

    testWidgets('C1: omitida sin hora y con motivo -> muestra el motivo',
        (tester) async {
      await _mostrar(
        tester,
        _dosis(const Duration(hours: -1),
            registro: Toma(
              medicamento: 'Losartán 50 mg',
              dosis: '50 mg',
              fechaHoraProgramada: programada,
              estado: EstadoToma.omitida,
              motivoOmision: 'No tenía el medicamento',
            )),
      );
      expect(find.text('No tomada'), findsOneWidget);
      expect(find.text('Motivo: No tenía el medicamento'), findsOneWidget);
      expect(find.textContaining('Registrada a las'), findsNothing);
    });

    testWidgets('C2: motivo vacío -> no muestra la línea del motivo',
        (tester) async {
      await _mostrar(
        tester,
        _dosis(const Duration(hours: -1),
            registro: Toma(
              medicamento: 'Losartán 50 mg',
              dosis: '50 mg',
              fechaHoraProgramada: programada,
              estado: EstadoToma.omitida,
              motivoOmision: '',
            )),
      );
      expect(find.textContaining('Motivo:'), findsNothing);
    });

    testWidgets('C3: tomada y corroborada -> hora y confirmación familiar',
        (tester) async {
      await _mostrar(
        tester,
        _dosis(const Duration(hours: -1),
            registro: Toma(
              medicamento: 'Losartán 50 mg',
              dosis: '50 mg',
              fechaHoraProgramada: programada,
              fechaHoraRegistro: programada,
              estado: EstadoToma.tomada,
              corroborada: true,
            )),
      );
      expect(find.textContaining('Registrada a las'), findsOneWidget);
      expect(find.text('Confirmada por su familia'), findsOneWidget);
    });

    testWidgets('C4: omitida sin motivo -> ninguna línea opcional',
        (tester) async {
      await _mostrar(
        tester,
        _dosis(const Duration(hours: -1),
            registro: Toma(
              medicamento: 'Losartán 50 mg',
              dosis: '50 mg',
              fechaHoraProgramada: programada,
              estado: EstadoToma.omitida,
            )),
      );
      expect(find.textContaining('Registrada a las'), findsNothing);
      expect(find.textContaining('Motivo:'), findsNothing);
      expect(find.text('Confirmada por su familia'), findsNothing);
    });

    testWidgets('C5: tomada sin corroborar -> hora, sin confirmación',
        (tester) async {
      await _mostrar(
        tester,
        _dosis(const Duration(hours: -1),
            registro: Toma(
              medicamento: 'Losartán 50 mg',
              dosis: '50 mg',
              fechaHoraProgramada: programada,
              fechaHoraRegistro: programada,
              estado: EstadoToma.tomada,
            )),
      );
      expect(find.textContaining('Registrada a las'), findsOneWidget);
      expect(find.text('Confirmada por su familia'), findsNothing);
    });
  });

  // --- Sincronizacion sin conexion (RF03) -----------------------------------
  Toma tomaDePrueba(int minutos) {
    final programada = DateTime.utc(2026, 11, 3, 8, minutos);
    return Toma(
      medicamento: 'Losartán 50 mg',
      dosis: '50 mg',
      fechaHoraProgramada: programada,
      fechaHoraRegistro: programada,
      estado: EstadoToma.tomada,
    );
  }

  ServicioSincronizacion servicio(
          Future<http.Response> Function(http.Request) responder) =>
      ServicioSincronizacion(ServicioApi(
        cliente: MockClient(responder),
        esperasDeReintento: const [],
      ));

  http.Response sinRed(http.Request _) =>
      throw http.ClientException('sin conexión');
  http.Response rechazo(int estado) => http.Response(
      jsonEncode({'codigo': 'X', 'mensaje': 'Rechazado'}), estado);

  // Cada caso parte de una cola vacía en el almacenamiento simulado.
  Future<void> colaVacia() async {
    SharedPreferences.setMockInitialValues({});
    await Almacenamiento.instancia.guardarCola(const []);
  }

  group('CB-10 registrar', () {
    setUp(colaVacia);

    test('C1: el servidor acepta -> true y la cola queda vacía', () async {
      final s = servicio((_) async => http.Response('{}', 201));
      expect(await s.registrar(tomaDePrueba(0)), isTrue);
      expect(await s.pendientes(), 0);
    });

    test('C2: sin conexión -> false y la toma queda en cola', () async {
      final s = servicio((r) async => sinRed(r));
      expect(await s.registrar(tomaDePrueba(0)), isFalse);
      expect(await s.pendientes(), 1);
    });

    test('C3: rechazo de negocio -> se propaga y sale de la cola', () async {
      final s = servicio((_) async => rechazo(422));
      await expectLater(s.registrar(tomaDePrueba(0)), throwsA(isA<ErrorApi>()));
      expect(await s.pendientes(), 0);
    });

    test('C4: sesión vencida -> se propaga y la toma se conserva', () async {
      final s = servicio((_) async => rechazo(401));
      await expectLater(s.registrar(tomaDePrueba(0)), throwsA(isA<ErrorApi>()));
      expect(await s.pendientes(), 1);
    });
  });

  group('CB-11 sincronizar', () {
    setUp(colaVacia);

    Future<void> encolar(int n) async {
      for (var i = 0; i < n; i++) {
        await Almacenamiento.instancia.encolar(tomaDePrueba(i));
      }
    }

    http.Response loteAceptado(http.Request r) {
      final n = (jsonDecode(r.body) as List).length;
      return http.Response(jsonEncode({'creados': n, 'actualizados': 0}), 200);
    }

    test('C1: ya hay una sincronización en curso -> no envía nada', () async {
      await encolar(2);
      var llamadas = 0;
      final s = servicio((r) async {
        llamadas++;
        await Future<void>.delayed(const Duration(milliseconds: 50));
        return loteAceptado(r);
      });
      final primera = s.sincronizar();
      final segunda = await s.sincronizar();
      await primera;
      expect(segunda.enviados, 0);
      expect(llamadas, 1);
    });

    test('C2: cola vacía -> nada que enviar', () async {
      final r = await servicio((r) async => loteAceptado(r)).sincronizar();
      expect(r.enviados, 0);
      expect(r.todoEnviado, isTrue);
    });

    test('C3: un lote -> todo enviado', () async {
      await encolar(3);
      final r = await servicio((r) async => loteAceptado(r)).sincronizar();
      expect(r.enviados, 3);
      expect(r.pendientes, 0);
    });

    test('C4: más de un lote -> el bucle itera hasta vaciar la cola', () async {
      final cola = [
        for (var i = 0; i < ServicioSincronizacion.tamanoLote + 5; i++)
          Toma(
            medicamento: 'M$i',
            dosis: '',
            fechaHoraProgramada: DateTime.utc(2026, 11, 3, 8),
            estado: EstadoToma.omitida,
          ),
      ];
      await Almacenamiento.instancia.guardarCola(cola);
      var lotes = 0;
      final r = await servicio((req) async {
        lotes++;
        return loteAceptado(req);
      }).sincronizar();
      expect(lotes, 2);
      expect(r.enviados, ServicioSincronizacion.tamanoLote + 5);
    });

    test('C5: sin conexión -> informa el fallo y conserva la cola', () async {
      await encolar(2);
      final r = await servicio((r) async => sinRed(r)).sincronizar();
      expect(r.huboFallo, isTrue);
      expect(r.pendientes, 2);
    });

    test('C6: rechazo del servidor -> informa el fallo y conserva la cola',
        () async {
      await encolar(2);
      final r = await servicio((_) async => rechazo(500)).sincronizar();
      expect(r.huboFallo, isTrue);
      expect(r.pendientes, 2);
    });
  });
}
