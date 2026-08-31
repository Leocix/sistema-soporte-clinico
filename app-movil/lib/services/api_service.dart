import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/resumen_adherencia.dart';
import '../models/sesion.dart';
import '../models/toma.dart';
import '../utils/constantes.dart';

/// Error de negocio devuelto por el API, ya traducido al espanol por el
/// manejador global del backend.
class ErrorApi implements Exception {
  ErrorApi(this.mensaje, {this.codigo, this.estado, this.idTraza});

  final String mensaje;
  final String? codigo;
  final int? estado;

  /// Identificador para correlacionar el fallo con el log del servidor.
  final String? idTraza;

  /// El token caduco o dejo de ser valido: hay que volver a iniciar sesion.
  bool get sesionExpirada => estado == 401;

  @override
  String toString() => mensaje;
}

/// Fallo de red: el telefono no pudo hablar con el servidor.
///
/// Se distingue de `ErrorApi` a proposito: ante un problema de conectividad la
/// aplicacion encola el evento y sigue funcionando, mientras que ante un error
/// de negocio debe mostrarselo al paciente.
class ErrorDeConexion implements Exception {
  ErrorDeConexion([this.mensaje = 'Sin conexion con el servidor.']);

  final String mensaje;

  @override
  String toString() => mensaje;
}

/// Cliente del API Gateway.
class ServicioApi {
  ServicioApi({http.Client? cliente, String? urlBase})
      : _cliente = cliente ?? http.Client(),
        _urlBase = urlBase ?? Constantes.urlApi;

  final http.Client _cliente;
  final String _urlBase;

  String? _token;

  set token(String? valor) => _token = valor;

  Map<String, String> get _cabeceras => {
        'Content-Type': 'application/json; charset=utf-8',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Uri _uri(String ruta, [Map<String, String>? parametros]) =>
      Uri.parse('$_urlBase$ruta').replace(queryParameters: parametros);

  /// Ejecuta la peticion y normaliza cualquier fallo a una de las dos
  /// excepciones del servicio.
  Future<dynamic> _enviar(Future<http.Response> Function() peticion) async {
    late final http.Response respuesta;
    try {
      respuesta = await peticion().timeout(Constantes.tiempoDeEspera);
    } on http.ClientException {
      // `package:http` envuelve los fallos de red de la plataforma
      // (SocketException incluida) en ClientException, asi que capturar
      // SocketException directamente no atrapa nada: es este el tipo que
      // llega cuando el telefono no alcanza al servidor.
      throw ErrorDeConexion(
        'No se pudo conectar con el servidor. Su registro se guardo en el '
        'telefono y se enviara automaticamente.',
      );
    } on TimeoutException {
      // Para el paciente agotar el tiempo de espera equivale a no tener
      // conexion: en ambos casos el evento debe quedar en la cola.
      throw ErrorDeConexion(
        'El servidor tardo demasiado en responder. Se guardo su registro y se '
        'enviara automaticamente.',
      );
    }

    final cuerpo = respuesta.body.isEmpty
        ? null
        : jsonDecode(utf8.decode(respuesta.bodyBytes));

    if (respuesta.statusCode >= 200 && respuesta.statusCode < 300) {
      return cuerpo;
    }

    if (cuerpo is Map<String, dynamic>) {
      throw ErrorApi(
        _mensajeDeError(cuerpo),
        codigo: cuerpo['codigo'] as String?,
        estado: respuesta.statusCode,
        idTraza: cuerpo['id_traza'] as String?,
      );
    }
    throw ErrorApi(
      'No se pudo completar la operacion.',
      estado: respuesta.statusCode,
    );
  }

  String _mensajeDeError(Map<String, dynamic> cuerpo) {
    final detalles = cuerpo['detalles'];
    if (cuerpo['codigo'] == 'VALIDACION_FALLIDA' &&
        detalles is List &&
        detalles.isNotEmpty) {
      return detalles.whereType<Map<String, dynamic>>().map((d) {
        final campo = d['campo'] as String?;
        final motivo = d['motivo'] as String? ?? '';
        return (campo == null || campo.isEmpty || campo == 'general')
            ? motivo
            : '$campo: $motivo';
      }).join(' · ');
    }
    return (cuerpo['mensaje'] as String?) ?? 'Ocurrio un error inesperado.';
  }

  // --- Sesion (RF01) -------------------------------------------------------

  /// Inicia sesion con perfil de paciente.
  ///
  /// El perfil viaja fijo: esta aplicacion no atiende al personal medico, que
  /// usa el panel web. Un medico que intente entrar aqui recibe el mismo 401
  /// generico que una credencial equivocada.
  Future<({String token, Usuario usuario})> iniciarSesion(
    String correo,
    String contrasena,
  ) async {
    final datos = await _enviar(
      () => _cliente.post(
        _uri('/api/auth/login'),
        headers: _cabeceras,
        body: jsonEncode({
          'correo': correo,
          'contrasena': contrasena,
          'perfil': 'paciente',
        }),
      ),
    ) as Map<String, dynamic>;

    return (
      token: datos['access_token'] as String,
      usuario: Usuario.desdeJson(datos['usuario'] as Map<String, dynamic>),
    );
  }

  Future<Usuario> perfil() async {
    final datos = await _enviar(
      () => _cliente.get(_uri('/api/auth/me'), headers: _cabeceras),
    ) as Map<String, dynamic>;
    return Usuario.desdeJson(datos);
  }

  // --- Ficha y adherencia propias -----------------------------------------

  /// Ficha clinica del paciente autenticado.
  ///
  /// La aplicacion no conoce el `id_paciente`: el servidor lo resuelve desde
  /// el token, de modo que ningun identificador de terceros llegue al
  /// dispositivo.
  Future<FichaPaciente> miFicha() async {
    final datos = await _enviar(
      () => _cliente.get(_uri('/api/pacientes/mi-ficha'), headers: _cabeceras),
    ) as Map<String, dynamic>;
    return FichaPaciente.desdeJson(datos);
  }

  Future<ResumenAdherencia> miResumen({DateTime? desde}) async {
    final datos = await _enviar(
      () => _cliente.get(
        _uri('/api/adherencia/mi-resumen', {
          if (desde != null) 'desde': desde.toUtc().toIso8601String(),
        }),
        headers: _cabeceras,
      ),
    ) as Map<String, dynamic>;
    return ResumenAdherencia.desdeJson(datos);
  }

  Future<List<Toma>> misRegistros({DateTime? desde, int limite = 100}) async {
    final datos = await _enviar(
      () => _cliente.get(
        _uri('/api/adherencia/mis-registros', {
          'limite': '$limite',
          if (desde != null) 'desde': desde.toUtc().toIso8601String(),
        }),
        headers: _cabeceras,
      ),
    ) as List<dynamic>;

    return datos
        .whereType<Map<String, dynamic>>()
        .map(Toma.desdeJsonApi)
        .toList();
  }

  // --- Registro de tomas (RF03) -------------------------------------------

  /// Envia una toma. El servidor responde 201 si es nueva y 200 si el envio
  /// actualizo un evento ya existente.
  Future<void> registrarToma(Toma toma) async {
    await _enviar(
      () => _cliente.post(
        _uri('/api/adherencia/registros'),
        headers: _cabeceras,
        body: jsonEncode(toma.aJsonApi()),
      ),
    );
  }

  /// Vacia la cola acumulada sin conexion en una sola transaccion.
  Future<({int creados, int actualizados})> sincronizarLote(
    List<Toma> tomas,
  ) async {
    final datos = await _enviar(
      () => _cliente.post(
        _uri('/api/adherencia/registros/lote'),
        headers: _cabeceras,
        body: jsonEncode(tomas.map((t) => t.aJsonApi()).toList()),
      ),
    ) as Map<String, dynamic>;

    return (
      creados: datos['creados'] as int,
      actualizados: datos['actualizados'] as int,
    );
  }

  void cerrar() => _cliente.close();
}
