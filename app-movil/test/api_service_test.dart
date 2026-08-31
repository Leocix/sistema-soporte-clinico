// Pruebas del cliente del API (RF01, RF03).
//
// Se ejercita contra un cliente HTTP simulado: verifican el contrato con el
// backend —que es donde se rompen las cosas— sin depender de la red ni del
// servicio desplegado.

import 'dart:async';
import 'dart:convert';

import 'package:cdss_adherencia/models/toma.dart';
import 'package:cdss_adherencia/services/api_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

const _urlBase = 'https://api.pruebas';

ServicioApi _apiQueResponde(
  http.Response Function(http.Request) responder,
) =>
    ServicioApi(
      urlBase: _urlBase,
      cliente: MockClient((peticion) async => responder(peticion)),
    );

http.Response _json(Object cuerpo, int estado) => http.Response(
      jsonEncode(cuerpo),
      estado,
      headers: {'content-type': 'application/json; charset=utf-8'},
    );

void main() {
  group('inicio de sesión', () {
    test('envía siempre el perfil paciente y devuelve token y usuario',
        () async {
      late Map<String, dynamic> enviado;

      final api = _apiQueResponde((peticion) {
        enviado = jsonDecode(peticion.body) as Map<String, dynamic>;
        return _json({
          'access_token': 'jwt-de-prueba',
          'token_type': 'bearer',
          'expira_en_minutos': 60,
          'usuario': {
            'id_usuario': 'u-1',
            'nombres': 'José',
            'apellidos': 'Vásquez',
            'correo': 'jose@correo.pe',
            'rol': 'paciente',
          },
        }, 200);
      });

      final sesion = await api.iniciarSesion('jose@correo.pe', 'Clave12345');

      // La app no ofrece elegir perfil: es exclusiva del paciente.
      expect(enviado['perfil'], 'paciente');
      expect(sesion.token, 'jwt-de-prueba');
      expect(sesion.usuario.nombreCompleto, 'José Vásquez');
    });

    test('un 401 se reconoce como sesión expirada', () async {
      final api = _apiQueResponde(
        (_) => _json({
          'exito': false,
          'codigo': 'NO_AUTENTICADO',
          'mensaje': 'Usuario o contrasena incorrectos.',
          'id_traza': 't-1',
        }, 401),
      );

      await expectLater(
        api.iniciarSesion('jose@correo.pe', 'incorrecta'),
        throwsA(
          isA<ErrorApi>()
              .having((e) => e.sesionExpirada, 'sesionExpirada', isTrue)
              .having((e) => e.mensaje, 'mensaje', contains('incorrectos')),
        ),
      );
    });
  });

  group('traducción de errores', () {
    test('un error de validación de campo antepone el nombre del campo',
        () async {
      final api = _apiQueResponde(
        (_) => _json({
          'codigo': 'VALIDACION_FALLIDA',
          'mensaje': 'Los datos enviados no cumplen el esquema esperado.',
          'detalles': [
            {'campo': 'medicamento', 'motivo': 'demasiado corto'},
          ],
        }, 422),
      );

      await expectLater(
        api.perfil(),
        throwsA(
          isA<ErrorApi>().having(
            (e) => e.mensaje,
            'mensaje',
            'medicamento: demasiado corto',
          ),
        ),
      );
    });

    test('un error de la ficha completa se muestra sin prefijo', () async {
      // El backend etiqueta como "general" los validadores que comparan
      // varios campos entre sí; anteponer ese nombre no aportaría nada.
      final api = _apiQueResponde(
        (_) => _json({
          'codigo': 'VALIDACION_FALLIDA',
          'mensaje': 'Los datos enviados no cumplen el esquema esperado.',
          'detalles': [
            {
              'campo': 'general',
              'motivo': 'Una toma omitida no puede llevar hora de toma.',
            },
          ],
        }, 422),
      );

      await expectLater(
        api.perfil(),
        throwsA(
          isA<ErrorApi>().having(
            (e) => e.mensaje,
            'mensaje',
            'Una toma omitida no puede llevar hora de toma.',
          ),
        ),
      );
    });

    test('un fallo de red se distingue de un error de negocio', () async {
      // `package:http` envuelve los fallos de la plataforma en
      // ClientException: es el tipo que hay que capturar para que el evento
      // acabe en la cola en lugar de mostrarse como un error al paciente.
      final api = ServicioApi(
        urlBase: _urlBase,
        cliente: MockClient(
          (_) async => throw http.ClientException('sin ruta al host'),
        ),
      );

      await expectLater(api.perfil(), throwsA(isA<ErrorDeConexion>()));
    });

    test('agotar el tiempo de espera también encola', () async {
      final api = ServicioApi(
        urlBase: _urlBase,
        cliente: MockClient((_) async => throw TimeoutException('tarde')),
      );

      await expectLater(api.perfil(), throwsA(isA<ErrorDeConexion>()));
    });
  });

  group('registro de tomas', () {
    test('el cuerpo enviado cumple el contrato del API', () async {
      late Map<String, dynamic> enviado;
      late String ruta;

      final api = _apiQueResponde((peticion) {
        ruta = peticion.url.path;
        enviado = jsonDecode(peticion.body) as Map<String, dynamic>;
        return _json({'id_registro': 'r-1'}, 201);
      });
      api.token = 'jwt-de-prueba';

      final programada = DateTime.utc(2026, 9, 1, 13, 0);
      await api.registrarToma(
        Toma.cumplida(
          medicamento: 'Losartán 50 mg',
          dosis: '1 tableta',
          programada: programada,
          momento: programada.add(const Duration(minutes: 10)),
        ),
      );

      expect(ruta, '/api/adherencia/registros');
      expect(enviado['medicamento'], 'Losartán 50 mg');
      expect(enviado['origen'], 'app_movil');
      expect(enviado['estado'], 'tomada');
      // Las horas viajan en UTC: el panel médico puede estar en otro huso.
      expect(enviado['fecha_hora_programada'], endsWith('Z'));
      // El API exige la hora real cuando la toma se marca como cumplida.
      expect(enviado['fecha_hora_registro'], isNotNull);
    });

    test('el retraso lo deduce la app, no lo declara el paciente', () {
      final programada = DateTime.utc(2026, 9, 1, 8, 0);

      final puntual = Toma.cumplida(
        medicamento: 'Metformina 850 mg',
        dosis: '',
        programada: programada,
        momento: programada.add(const Duration(minutes: 20)),
      );
      final tardia = Toma.cumplida(
        medicamento: 'Metformina 850 mg',
        dosis: '',
        programada: programada,
        momento: programada.add(const Duration(minutes: 45)),
      );

      expect(puntual.estado, EstadoToma.tomada);
      expect(tardia.estado, EstadoToma.tomadaTarde);
      expect(tardia.minutosDeRetraso, 45);
    });

    test('una toma omitida no lleva hora de toma', () {
      final omitida = Toma.omitida(
        medicamento: 'Amlodipino 5 mg',
        dosis: '',
        programada: DateTime.utc(2026, 9, 1, 8, 0),
        motivo: 'Me olvidé',
      );

      final cuerpo = omitida.aJsonApi();
      expect(cuerpo['estado'], 'omitida');
      expect(cuerpo.containsKey('fecha_hora_registro'), isFalse);
      expect(cuerpo['motivo_omision'], 'Me olvidé');
    });

    test('la clave del evento sobrevive al viaje de ida y vuelta', () {
      // Es la clave con la que el servidor reconoce un reenvío como el mismo
      // evento; si cambiara al guardarla y releerla, la cola duplicaría tomas.
      final original = Toma.cumplida(
        medicamento: 'Losartán 50 mg',
        dosis: '1 tableta',
        programada: DateTime.utc(2026, 9, 1, 13, 0),
        momento: DateTime.utc(2026, 9, 1, 13, 5),
      );

      final reconstruida = Toma.desdeJsonLocal(original.aJsonLocal());

      expect(reconstruida.clave, original.clave);
    });
  });

  group('sincronización en lote', () {
    test('informa cuántos eventos creó y cuántos actualizó', () async {
      final api = _apiQueResponde(
        (_) => _json({'creados': 2, 'actualizados': 1, 'registros': []}, 200),
      );

      final resultado = await api.sincronizarLote([
        Toma.omitida(
          medicamento: 'A',
          dosis: '',
          programada: DateTime.utc(2026, 9, 1, 8),
        ),
      ]);

      expect(resultado.creados, 2);
      expect(resultado.actualizados, 1);
    });
  });
}
