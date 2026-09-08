import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/familia.dart';
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
  ServicioApi({
    http.Client? cliente,
    String? urlBase,
    List<Duration>? esperasDeReintento,
  })  : _cliente = cliente ?? http.Client(),
        _urlBase = urlBase ?? Constantes.urlApi,
        _esperas = esperasDeReintento ?? Constantes.esperasDeReintento;

  final http.Client _cliente;
  final String _urlBase;

  /// Pausas antes de cada reintento de una lectura. Se inyectan para que las
  /// pruebas no tengan que esperar de verdad.
  final List<Duration> _esperas;

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
  ///
  /// `reintentable` solo se activa en las **lecturas**. El alojamiento gratuito
  /// suspende el servicio tras un rato sin trafico, y mientras arranca corta las
  /// primeras conexiones: sin reintento, abrir la aplicacion despues de unas
  /// horas mostraba «sin conexion» a un paciente que tenia internet perfecto.
  /// Las escrituras no se reintentan solas: un envio que fallo en el socket
  /// pudo haber llegado igualmente al servidor, y repetirlo a ciegas es como se
  /// duplican los datos. Para ellas esta la cola local, que reintenta de forma
  /// explicita y con la clave de idempotencia por delante.
  Future<dynamic> _enviar(
    Future<http.Response> Function() peticion, {
    bool reintentable = false,
  }) async {
    final intentos = reintentable ? _esperas.length + 1 : 1;
    ErrorDeConexion? ultimoFallo;

    for (var intento = 0; intento < intentos; intento++) {
      if (intento > 0) await Future<void>.delayed(_esperas[intento - 1]);
      try {
        return await _enviarUnaVez(peticion);
      } on ErrorDeConexion catch (e) {
        ultimoFallo = e;
      }
    }
    throw ultimoFallo!;
  }

  Future<dynamic> _enviarUnaVez(Future<http.Response> Function() peticion) async {
    late final http.Response respuesta;
    try {
      respuesta = await peticion().timeout(Constantes.tiempoDeEspera);
    } on http.ClientException {
      // `package:http` envuelve los fallos de red de la plataforma
      // (SocketException incluida) en ClientException, asi que capturar
      // SocketException directamente no atrapa nada: es este el tipo que
      // llega cuando el telefono no alcanza al servidor.
      // Mensaje neutro a proposito. Antes hablaba de un registro guardado en el
      // telefono, que es cierto al enviar una toma pero absurdo al iniciar
      // sesion, que es donde mas se ve este error: el paciente leia que su
      // registro se habia guardado cuando lo unico que habia ocurrido es que no
      // pudo entrar. Cada pantalla anade su propio matiz.
      throw ErrorDeConexion(
        'No se pudo conectar con el servidor. Revise su conexion a internet e '
        'intentelo de nuevo.',
      );
    } on TimeoutException {
      // Para el paciente agotar el tiempo de espera equivale a no tener
      // conexion: en ambos casos el evento debe quedar en la cola.
      throw ErrorDeConexion(
        'El servidor tardo demasiado en responder. Intentelo de nuevo en un '
        'momento.',
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

  /// Inicia sesion con perfil de paciente o de acompanante familiar.
  ///
  /// El perfil lo declara quien entra, igual que en el panel web. Nunca es
  /// `medico`: esta aplicacion no atiende al personal clinico, y un medico que
  /// intente entrar aqui recibe el mismo 401 generico que una credencial
  /// equivocada.
  Future<({String token, Usuario usuario})> iniciarSesion(
    String correo,
    String contrasena, {
    PerfilUsuario perfil = PerfilUsuario.paciente,
  }) async {
    final datos = await _enviar(
      () => _cliente.post(
        _uri('/api/auth/login'),
        headers: _cabeceras,
        body: jsonEncode({
          'correo': correo,
          'contrasena': contrasena,
          'perfil': perfil.codigo,
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
      reintentable: true,
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
      reintentable: true,
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
      reintentable: true,
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
      reintentable: true,
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

  // --- Recuperacion de la contrasena (RF10) --------------------------------

  /// Pide el enlace de restablecimiento.
  ///
  /// La respuesta es la misma exista o no la cuenta: el servidor no confirma
  /// que direcciones estan registradas. `correoHabilitado` no habla del
  /// usuario sino del servicio: dice si hay un servidor de correo detras o si
  /// hay que dirigir al paciente al consultorio.
  Future<({String mensaje, bool correoHabilitado})> solicitarRecuperacion(
    String correo,
  ) async {
    final datos = await _enviar(
      () => _cliente.post(
        _uri('/api/auth/recuperacion'),
        headers: _cabeceras,
        body: jsonEncode({'correo': correo}),
      ),
    ) as Map<String, dynamic>;

    return (
      mensaje: datos['mensaje'] as String,
      correoHabilitado: (datos['correo_habilitado'] as bool?) ?? false,
    );
  }

  // --- Grupo familiar de acompanamiento (RF09) -----------------------------

  /// Emite el codigo con el que un familiar creara su cuenta.
  Future<Acompanante> invitarFamiliar({
    required String nombre,
    required Parentesco parentesco,
  }) async {
    final datos = await _enviar(
      () => _cliente.post(
        _uri('/api/familiares/invitaciones'),
        headers: _cabeceras,
        body: jsonEncode({
          'nombre_invitado': nombre,
          'parentesco': parentesco.codigo,
        }),
      ),
    ) as Map<String, dynamic>;
    return Acompanante.desdeJson(datos);
  }

  Future<List<Acompanante>> miGrupoFamiliar() async {
    final datos = await _enviar(
      () => _cliente.get(_uri('/api/familiares'), headers: _cabeceras),
      reintentable: true,
    ) as List<dynamic>;
    return datos
        .whereType<Map<String, dynamic>>()
        .map(Acompanante.desdeJson)
        .toList();
  }

  Future<void> retirarFamiliar(String idAcompanante) async {
    await _enviar(
      () => _cliente.delete(
        _uri('/api/familiares/$idAcompanante'),
        headers: _cabeceras,
      ),
    );
  }

  /// Canjea el codigo creando la cuenta del acompanante.
  ///
  /// Es la unica via de alta de cuentas: sin una invitacion vigente emitida
  /// por un paciente, esta llamada no crea nada.
  Future<({String token, Usuario usuario})> registrarFamiliar({
    required String codigo,
    required String nombres,
    required String apellidos,
    required String correo,
    required String contrasena,
  }) async {
    final datos = await _enviar(
      () => _cliente.post(
        _uri('/api/familiares/registro'),
        headers: _cabeceras,
        body: jsonEncode({
          'codigo': codigo,
          'nombres': nombres,
          'apellidos': apellidos,
          'correo': correo,
          'contrasena': contrasena,
        }),
      ),
    ) as Map<String, dynamic>;

    return (
      token: datos['access_token'] as String,
      usuario: Usuario.desdeJson(datos['usuario'] as Map<String, dynamic>),
    );
  }

  /// Anade otro paciente al acompanante que ya tiene cuenta.
  Future<PacienteAcompanado> unirseConCodigo(String codigo) async {
    final datos = await _enviar(
      () => _cliente.post(
        _uri('/api/familiares/vinculaciones'),
        headers: _cabeceras,
        body: jsonEncode({'codigo': codigo}),
      ),
    ) as Map<String, dynamic>;
    return PacienteAcompanado.desdeJson(datos);
  }

  Future<List<PacienteAcompanado>> misPacientes() async {
    final datos = await _enviar(
      () => _cliente.get(
        _uri('/api/familiares/mis-pacientes'),
        headers: _cabeceras,
      ),
      reintentable: true,
    ) as List<dynamic>;
    return datos
        .whereType<Map<String, dynamic>>()
        .map(PacienteAcompanado.desdeJson)
        .toList();
  }

  Future<List<TomaPorConfirmar>> tomasPorConfirmar() async {
    final datos = await _enviar(
      () => _cliente.get(
        _uri('/api/familiares/tomas-por-confirmar'),
        headers: _cabeceras,
      ),
      reintentable: true,
    ) as List<dynamic>;
    return datos
        .whereType<Map<String, dynamic>>()
        .map(TomaPorConfirmar.desdeJson)
        .toList();
  }

  /// Anade el testimonio del acompanante a una toma ya reportada.
  Future<void> confirmarToma(String idRegistro) async {
    await _enviar(
      () => _cliente.post(
        _uri('/api/familiares/tomas/$idRegistro/confirmacion'),
        headers: _cabeceras,
      ),
    );
  }

  void cerrar() => _cliente.close();
}
