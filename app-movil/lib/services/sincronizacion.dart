import '../models/toma.dart';
import 'almacenamiento.dart';
import 'api_service.dart';

/// Resultado de un intento de vaciar la cola.
class ResultadoSincronizacion {
  const ResultadoSincronizacion({
    required this.enviados,
    required this.pendientes,
    this.error,
  });

  final int enviados;
  final int pendientes;
  final String? error;

  bool get todoEnviado => pendientes == 0;
  bool get huboFallo => error != null;
}

/// Envio de eventos de adherencia con tolerancia a la falta de conexion.
///
/// El criterio de aceptacion de HU03 exige que "cada toma quede registrada y
/// sincronizada". Como el paciente puede estar sin cobertura en el momento de
/// tomar su medicacion, la aplicacion nunca bloquea la confirmacion: guarda el
/// evento en la cola local y lo envia cuando puede.
///
/// El reenvio es seguro porque el servidor identifica cada evento por la terna
/// (paciente, medicamento, horario programado): un envio repetido actualiza el
/// registro existente en lugar de duplicarlo. Sin esa garantia, reintentar
/// inflaria la tasa de adherencia y contaminaria las caracteristicas del
/// modelo predictivo.
class ServicioSincronizacion {
  ServicioSincronizacion(this._api);

  final ServicioApi _api;
  final Almacenamiento _local = Almacenamiento.instancia;

  /// Tope de eventos por envio; coincide con el maximo que acepta el API.
  static const int tamanoLote = 200;

  bool _enCurso = false;

  /// Registra una respuesta del paciente.
  ///
  /// Devuelve `true` si el evento llego al servidor y `false` si quedo en cola.
  /// En ninguno de los dos casos se pierde: la interfaz confirma la accion
  /// igualmente y solo cambia el distintivo de "pendiente de envio".
  Future<bool> registrar(Toma toma) async {
    await _local.encolar(toma);
    try {
      await _api.registrarToma(toma);
      await _local.descartarDeLaCola([toma.clave]);
      return true;
    } on ErrorDeConexion {
      return false;
    } on ErrorApi catch (e) {
      // Un rechazo de negocio no se reintenta: reenviarlo fallaria igual y la
      // cola crecería sin fin. Se retira y se propaga para avisar al paciente.
      if (!e.sesionExpirada) {
        await _local.descartarDeLaCola([toma.clave]);
      }
      rethrow;
    }
  }

  /// Intenta vaciar la cola pendiente.
  Future<ResultadoSincronizacion> sincronizar() async {
    if (_enCurso) {
      final pendientes = await _local.leerCola();
      return ResultadoSincronizacion(
        enviados: 0,
        pendientes: pendientes.length,
      );
    }

    _enCurso = true;
    try {
      var cola = await _local.leerCola();
      if (cola.isEmpty) {
        return const ResultadoSincronizacion(enviados: 0, pendientes: 0);
      }

      var enviados = 0;
      while (cola.isNotEmpty) {
        final lote = cola.take(tamanoLote).toList();
        await _api.sincronizarLote(lote);
        cola = await _local.descartarDeLaCola(lote.map((t) => t.clave));
        enviados += lote.length;
      }
      return ResultadoSincronizacion(enviados: enviados, pendientes: 0);
    } on ErrorDeConexion catch (e) {
      final pendientes = await _local.leerCola();
      return ResultadoSincronizacion(
        enviados: 0,
        pendientes: pendientes.length,
        error: e.mensaje,
      );
    } on ErrorApi catch (e) {
      final pendientes = await _local.leerCola();
      return ResultadoSincronizacion(
        enviados: 0,
        pendientes: pendientes.length,
        error: e.mensaje,
      );
    } finally {
      _enCurso = false;
    }
  }

  Future<int> pendientes() async => (await _local.leerCola()).length;
}
