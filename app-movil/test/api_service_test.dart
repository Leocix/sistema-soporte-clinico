// Pruebas del cliente del API (RF01, RF03).
//
// Se ejercita contra un cliente HTTP simulado: verifican el contrato con el
// backend —que es donde se rompen las cosas— sin depender de la red ni del
// servicio desplegado.

import 'dart:async';
import 'dart:convert';

import 'package:cdss_adherencia/models/familia.dart';
import 'package:cdss_adherencia/models/sesion.dart';
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
    test('por defecto entra como paciente y devuelve token y usuario',
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

      expect(enviado['perfil'], 'paciente');
      expect(sesion.token, 'jwt-de-prueba');
      expect(sesion.usuario.nombreCompleto, 'José Vásquez');
      expect(sesion.usuario.esFamiliar, isFalse);
    });

    test('el acompañante entra declarando su propio perfil', () async {
      late Map<String, dynamic> enviado;

      final api = _apiQueResponde((peticion) {
        enviado = jsonDecode(peticion.body) as Map<String, dynamic>;
        return _json({
          'access_token': 'jwt-familiar',
          'token_type': 'bearer',
          'expira_en_minutos': 60,
          'usuario': {
            'id_usuario': 'u-2',
            'nombres': 'Rosa',
            'apellidos': 'Vásquez',
            'correo': 'rosa@correo.pe',
            'rol': 'familiar',
          },
        }, 200);
      });

      final sesion = await api.iniciarSesion(
        'rosa@correo.pe',
        'Clave12345',
        perfil: PerfilUsuario.familiar,
      );

      expect(enviado['perfil'], 'familiar');
      // Quien decide el recorrido es el rol que devuelve el servidor.
      expect(sesion.usuario.esFamiliar, isTrue);
    });

    test('una sesión guardada sin perfil se lee como paciente', () {
      // Las sesiones anteriores al perfil familiar no llevan el campo; darlas
      // por familiares dejaría al paciente sin su plan de tomas.
      final usuario = Usuario.desdeJson(const {
        'id_usuario': 'u-1',
        'nombres': 'José',
        'apellidos': 'Vásquez',
        'correo': 'jose@correo.pe',
      });

      expect(usuario.perfil, PerfilUsuario.paciente);
      // Y al volver a guardarla ya queda con su perfil explícito.
      expect(usuario.aJson()['rol'], 'paciente');
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

  group('grupo familiar (RF09)', () {
    test('la invitación viaja con el nombre y el parentesco', () async {
      late Map<String, dynamic> enviado;

      final api = _apiQueResponde((peticion) {
        enviado = jsonDecode(peticion.body) as Map<String, dynamic>;
        return _json({
          'id_acompanante': 'a-1',
          'nombre': 'Rosa Vásquez',
          'parentesco': 'hijo',
          'estado': 'invitado',
          'codigo_invitacion': 'ABCD2345',
          'expira_en': DateTime.now()
              .add(const Duration(days: 7))
              .toUtc()
              .toIso8601String(),
          'tomas_corroboradas': 0,
        }, 201);
      });

      final acompanante = await api.invitarFamiliar(
        nombre: 'Rosa Vásquez',
        parentesco: Parentesco.hijo,
      );

      expect(enviado['nombre_invitado'], 'Rosa Vásquez');
      expect(enviado['parentesco'], 'hijo');
      expect(acompanante.pendiente, isTrue);
      expect(acompanante.codigoInvitacion, 'ABCD2345');
      // Se le muestra al paciente cuánto le queda para dárselo a su familiar.
      expect(acompanante.diasParaVencer, 7);
    });

    test('un acompañante ya vinculado no expone ningún código', () {
      final acompanante = Acompanante.desdeJson(const {
        'id_acompanante': 'a-1',
        'nombre': 'Rosa Vásquez',
        'parentesco': 'hijo',
        'estado': 'activo',
        'correo': 'rosa@correo.pe',
        'codigo_invitacion': null,
        'tomas_corroboradas': 12,
      });

      expect(acompanante.pendiente, isFalse);
      expect(acompanante.codigoInvitacion, isNull);
      expect(acompanante.tomasCorroboradas, 12);
    });

    test('la confirmación se envía contra el registro indicado', () async {
      late http.Request peticionRecibida;

      final api = _apiQueResponde((peticion) {
        peticionRecibida = peticion;
        return _json({
          'id_registro': 'r-1',
          'paciente': 'José Vásquez',
          'medicamento': 'Losartán 50 mg',
          'dosis': '1 tableta',
          'fecha_hora_programada': '2026-09-07T13:00:00Z',
          'fecha_hora_registro': '2026-09-07T13:05:00Z',
          'corroborada': true,
        }, 200);
      });

      await api.confirmarToma('r-1');

      expect(peticionRecibida.method, 'POST');
      expect(
        peticionRecibida.url.path,
        '/api/familiares/tomas/r-1/confirmacion',
      );
    });

    test('la toma por confirmar muestra la hora que declaró el paciente', () {
      final toma = TomaPorConfirmar.desdeJson({
        'id_registro': 'r-1',
        'paciente': 'José Vásquez',
        'medicamento': 'Losartán',
        'dosis': '50 mg',
        'fecha_hora_programada':
            DateTime(2026, 9, 7, 8).toUtc().toIso8601String(),
        'fecha_hora_registro':
            DateTime(2026, 9, 7, 8, 25).toUtc().toIso8601String(),
        'corroborada': false,
      });

      expect(toma.descripcion, 'Losartán · 50 mg');
      // No la programada: el acompañante corrobora lo que el paciente declaró.
      expect(toma.horaReportada, '08:25');
    });

    test('una toma sin hora de registro cae en la programada', () {
      final toma = TomaPorConfirmar.desdeJson({
        'id_registro': 'r-2',
        'paciente': 'José Vásquez',
        'medicamento': 'Enalapril',
        'dosis': '',
        'fecha_hora_programada':
            DateTime(2026, 9, 7, 20).toUtc().toIso8601String(),
        'fecha_hora_registro': null,
        'corroborada': false,
      });

      expect(toma.descripcion, 'Enalapril');
      expect(toma.horaReportada, '20:00');
    });
  });

  group('corroboración en el historial del paciente', () {
    test('el historial trae si la toma fue confirmada por la familia', () {
      final toma = Toma.desdeJsonApi({
        'medicamento': 'Losartán 50 mg',
        'dosis': '1 tableta',
        'fecha_hora_programada': '2026-09-07T13:00:00Z',
        'fecha_hora_registro': '2026-09-07T13:05:00Z',
        'estado': 'tomada',
        'motivo_omision': null,
        'corroborada': true,
      });

      expect(toma.corroborada, isTrue);
    });

    test('una toma recién creada en el teléfono nace sin corroborar', () {
      final toma = Toma.cumplida(
        medicamento: 'Losartán 50 mg',
        dosis: '1 tableta',
        programada: DateTime.now(),
      );

      // La corroboración la hace otra persona en su propio dispositivo.
      expect(toma.corroborada, isFalse);
      expect(toma.aJsonApi().containsKey('corroborada'), isFalse);
    });
  });

  group('reintento cuando el servicio está arrancando', () {
    ServicioApi _conFallos(int fallosPrevios, {List<Duration>? esperas}) {
      var intentos = 0;
      return ServicioApi(
        urlBase: _urlBase,
        // Sin pausas reales: la prueba verifica la política, no el reloj.
        esperasDeReintento: esperas ?? const [Duration.zero, Duration.zero],
        cliente: MockClient((peticion) async {
          intentos++;
          if (intentos <= fallosPrevios) {
            throw http.ClientException('Connection reset by peer', peticion.url);
          }
          return _json({
            'id_paciente': 'p-1', 'codigo_anonimizado': 'P-001',
            'desde': null, 'hasta': null, 'total_eventos': 4, 'cumplidos': 3,
            'omitidos': 1, 'tasa_adherencia': 75.0, 'retraso_promedio_min': 12.0,
            'omisiones_consecutivas': 0, 'ultima_toma_registrada': null,
          }, 200);
        }),
      );
    }

    test('una lectura sobrevive a que el servicio corte las dos primeras',
        () async {
      // Es lo que hace el alojamiento gratuito al despertar: no responde
      // despacio, corta la conexión. Sin reintento, el paciente veía «sin
      // conexión» teniendo internet perfecto.
      final resumen = await _conFallos(2).miResumen();

      expect(resumen.tasaAdherencia, 75.0);
    });

    test('si el fallo persiste, se rinde y lo informa', () async {
      await expectLater(
        _conFallos(99).miResumen(),
        throwsA(isA<ErrorDeConexion>()),
      );
    });

    test('el mensaje del fallo no culpa a la conexión del paciente', () async {
      try {
        await _conFallos(99).miResumen();
        fail('debía fallar');
      } on ErrorDeConexion catch (e) {
        expect(e.mensaje, contains('No se pudo conectar con el servidor'));
        expect(e.mensaje.toLowerCase(), isNot(contains('su registro se guardo')));
      }
    });

    test('una escritura NO se reintenta sola', () async {
      // Un envío que falló en el socket pudo haber llegado igualmente:
      // repetirlo a ciegas es como se duplican los datos. Para eso está la
      // cola local, que reintenta con la clave de idempotencia por delante.
      var intentos = 0;
      final api = ServicioApi(
        urlBase: _urlBase,
        esperasDeReintento: const [Duration.zero, Duration.zero],
        cliente: MockClient((peticion) async {
          intentos++;
          throw http.ClientException('Connection reset by peer', peticion.url);
        }),
      );

      await expectLater(
        api.registrarToma(Toma.cumplida(
          medicamento: 'Losartán 50 mg',
          dosis: '1 tableta',
          programada: DateTime.now(),
        )),
        throwsA(isA<ErrorDeConexion>()),
      );
      expect(intentos, 1);
    });
  });
}
