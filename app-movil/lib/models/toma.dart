import '../utils/constantes.dart';

/// Desenlace de una dosis, en los mismos terminos que el API.
enum EstadoToma {
  tomada('tomada', 'Tomada'),
  tomadaTarde('tomada_tarde', 'Tomada con retraso'),
  omitida('omitida', 'No tomada'),
  pospuesta('pospuesta', 'Pospuesta');

  const EstadoToma(this.codigo, this.etiqueta);

  final String codigo;
  final String etiqueta;

  bool get cumplida =>
      this == EstadoToma.tomada || this == EstadoToma.tomadaTarde;

  static EstadoToma desdeCodigo(String codigo) => EstadoToma.values.firstWhere(
        (e) => e.codigo == codigo,
        orElse: () => EstadoToma.pospuesta,
      );
}

/// Evento de toma listo para enviarse al API (RF03).
///
/// La terna (paciente, medicamento, horario programado) identifica el evento
/// de forma univoca en el servidor, asi que reenviar este objeto tras una
/// perdida de conectividad actualiza el registro en lugar de duplicarlo. Por
/// eso la cola local puede reintentar sin miedo.
class Toma {
  const Toma({
    required this.medicamento,
    required this.dosis,
    required this.fechaHoraProgramada,
    required this.estado,
    this.fechaHoraRegistro,
    this.motivoOmision,
    this.corroborada = false,
  });

  final String medicamento;
  final String dosis;
  final DateTime fechaHoraProgramada;
  final DateTime? fechaHoraRegistro;
  final EstadoToma estado;
  final String? motivoOmision;

  /// Un familiar dio fe de esta toma (RF09).
  ///
  /// Solo llega desde el servidor: la corroboracion la hace otra persona en su
  /// propio dispositivo, de modo que un evento recien creado en el telefono
  /// del paciente nace siempre sin corroborar.
  final bool corroborada;

  /// Clave local del evento; coincide con la que usa el servidor.
  String get clave =>
      '$medicamento|${fechaHoraProgramada.toUtc().toIso8601String()}';

  /// Minutos transcurridos entre la hora prescrita y la toma real.
  double? get minutosDeRetraso {
    final registro = fechaHoraRegistro;
    if (registro == null) return null;
    final diferencia = registro.difference(fechaHoraProgramada);
    return diferencia.inSeconds / 60;
  }

  /// Construye el evento a partir de la respuesta del paciente.
  ///
  /// El estado no lo elige el paciente entre cuatro opciones: el confirma que
  /// tomo la dosis y la aplicacion decide si fue puntual o con retraso segun
  /// el margen de tolerancia. Preguntarselo seria pedirle que se autoevalue,
  /// justamente el sesgo del autorreporte que el sistema quiere eliminar.
  factory Toma.cumplida({
    required String medicamento,
    required String dosis,
    required DateTime programada,
    DateTime? momento,
  }) {
    final registro = momento ?? DateTime.now();
    final tarde =
        registro.difference(programada) > Constantes.margenPuntualidad;
    return Toma(
      medicamento: medicamento,
      dosis: dosis,
      fechaHoraProgramada: programada,
      fechaHoraRegistro: registro,
      estado: tarde ? EstadoToma.tomadaTarde : EstadoToma.tomada,
    );
  }

  factory Toma.omitida({
    required String medicamento,
    required String dosis,
    required DateTime programada,
    String? motivo,
  }) =>
      Toma(
        medicamento: medicamento,
        dosis: dosis,
        fechaHoraProgramada: programada,
        estado: EstadoToma.omitida,
        motivoOmision: motivo,
      );

  /// Cuerpo que espera `POST /api/adherencia/registros`.
  ///
  /// Las horas viajan en UTC: el servidor las almacena con zona horaria y el
  /// panel medico puede estar en otro huso.
  Map<String, dynamic> aJsonApi() => {
        'medicamento': medicamento,
        if (dosis.isNotEmpty) 'dosis': dosis,
        'fecha_hora_programada': fechaHoraProgramada.toUtc().toIso8601String(),
        if (fechaHoraRegistro != null)
          'fecha_hora_registro': fechaHoraRegistro!.toUtc().toIso8601String(),
        'estado': estado.codigo,
        if (motivoOmision != null && motivoOmision!.isNotEmpty)
          'motivo_omision': motivoOmision,
        'origen': 'app_movil',
      };

  Map<String, dynamic> aJsonLocal() => aJsonApi();

  factory Toma.desdeJsonLocal(Map<String, dynamic> json) => Toma(
        medicamento: json['medicamento'] as String,
        dosis: (json['dosis'] as String?) ?? '',
        fechaHoraProgramada:
            DateTime.parse(json['fecha_hora_programada'] as String).toLocal(),
        fechaHoraRegistro: json['fecha_hora_registro'] == null
            ? null
            : DateTime.parse(json['fecha_hora_registro'] as String).toLocal(),
        estado: EstadoToma.desdeCodigo(json['estado'] as String),
        motivoOmision: json['motivo_omision'] as String?,
      );

  /// Evento tal como lo devuelve el API en las consultas de historial.
  factory Toma.desdeJsonApi(Map<String, dynamic> json) => Toma(
        medicamento: json['medicamento'] as String,
        dosis: (json['dosis'] as String?) ?? '',
        fechaHoraProgramada:
            DateTime.parse(json['fecha_hora_programada'] as String).toLocal(),
        fechaHoraRegistro: json['fecha_hora_registro'] == null
            ? null
            : DateTime.parse(json['fecha_hora_registro'] as String).toLocal(),
        estado: EstadoToma.desdeCodigo(json['estado'] as String),
        motivoOmision: json['motivo_omision'] as String?,
        corroborada: (json['corroborada'] as bool?) ?? false,
      );
}

/// Una dosis del dia: lo que toca tomar y, si ya hubo respuesta, cual fue.
class DosisDelDia {
  const DosisDelDia({
    required this.medicamento,
    required this.dosis,
    required this.programada,
    this.registro,
    this.pendienteDeEnvio = false,
  });

  final String medicamento;
  final String dosis;
  final DateTime programada;

  /// Respuesta ya dada por el paciente, si existe.
  final Toma? registro;

  /// La respuesta existe pero aun no llego al servidor.
  final bool pendienteDeEnvio;

  bool get respondida => registro != null;

  /// Momento desde el que se puede marcar como tomada.
  DateTime get abreVentana => programada.subtract(Constantes.ventanaAntes);

  /// Momento hasta el que se puede marcar como tomada.
  DateTime get cierraVentana => programada.add(Constantes.ventanaDespues);

  /// Aun no se abre la ventana: no se ofrecen los botones de respuesta.
  bool get esFutura => DateTime.now().isBefore(abreVentana);

  /// La ventana ya cerro: solo puede declararse que no se tomo.
  bool get ventanaCerrada => DateTime.now().isAfter(cierraVentana);
}
