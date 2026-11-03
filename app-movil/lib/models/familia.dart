import '../utils/constantes.dart';

/// Vinculo del acompanante con el paciente.
enum Parentesco {
  conyuge('conyuge', 'Esposo o esposa'),
  hijo('hijo', 'Hijo o hija'),
  hermano('hermano', 'Hermano o hermana'),
  cuidador('cuidador', 'Cuidador'),
  otro('otro', 'Otro familiar');

  const Parentesco(this.codigo, this.etiqueta);

  final String codigo;
  final String etiqueta;

  static Parentesco desdeCodigo(String codigo) =>
      Parentesco.values.firstWhere((p) => p.codigo == codigo,
          orElse: () => Parentesco.otro);
}

/// Situacion de una persona dentro del grupo familiar.
enum EstadoAcompanante {
  invitado('invitado'),
  activo('activo'),
  revocado('revocado');

  const EstadoAcompanante(this.codigo);

  final String codigo;

  static EstadoAcompanante desdeCodigo(String codigo) =>
      EstadoAcompanante.values.firstWhere((e) => e.codigo == codigo,
          orElse: () => EstadoAcompanante.invitado);
}

/// Miembro del grupo familiar, tal como lo ve el paciente (RF09).
class Acompanante {
  const Acompanante({
    required this.id,
    required this.nombre,
    required this.parentesco,
    required this.estado,
    this.correo,
    this.codigoInvitacion,
    this.expiraEn,
    this.tomasCorroboradas = 0,
  });

  final String id;
  final String nombre;
  final Parentesco parentesco;
  final EstadoAcompanante estado;
  final String? correo;

  /// Solo llega mientras la invitacion sigue sin canjear.
  final String? codigoInvitacion;
  final DateTime? expiraEn;

  /// Cuantas tomas ha confirmado; distingue un acompanamiento real de una
  /// pertenencia meramente nominal.
  final int tomasCorroboradas;

  bool get pendiente => estado == EstadoAcompanante.invitado;

  /// Dias que le quedan a la invitacion, redondeados hacia arriba.
  int? get diasParaVencer {
    final vence = expiraEn;
    if (vence == null) return null;
    return vence.difference(DateTime.now()).inHours ~/ 24 + 1;
  }

  factory Acompanante.desdeJson(Map<String, dynamic> json) => Acompanante(
        id: json['id_acompanante'] as String,
        nombre: json['nombre'] as String,
        parentesco: Parentesco.desdeCodigo(json['parentesco'] as String),
        estado: EstadoAcompanante.desdeCodigo(json['estado'] as String),
        correo: json['correo'] as String?,
        codigoInvitacion: json['codigo_invitacion'] as String?,
        expiraEn: json['expira_en'] == null
            ? null
            : DateTime.parse(json['expira_en'] as String).toLocal(),
        tomasCorroboradas: (json['tomas_corroboradas'] as int?) ?? 0,
      );
}

/// Persona a la que acompana el familiar autenticado.
class PacienteAcompanado {
  const PacienteAcompanado({
    required this.id,
    required this.nombre,
    required this.parentesco,
    this.tasaAdherencia,
    this.tomasPorConfirmar = 0,
  });

  final String id;
  final String nombre;
  final Parentesco parentesco;
  final double? tasaAdherencia;
  final int tomasPorConfirmar;

  factory PacienteAcompanado.desdeJson(Map<String, dynamic> json) =>
      PacienteAcompanado(
        id: json['id_acompanante'] as String,
        nombre: json['nombre'] as String,
        parentesco: Parentesco.desdeCodigo(json['parentesco'] as String),
        tasaAdherencia: (json['tasa_adherencia'] as num?)?.toDouble(),
        tomasPorConfirmar: (json['tomas_por_confirmar'] as int?) ?? 0,
      );
}

/// Toma que el paciente reporto como cumplida y espera corroboracion.
class TomaPorConfirmar {
  const TomaPorConfirmar({
    required this.idRegistro,
    required this.paciente,
    required this.medicamento,
    required this.dosis,
    required this.programada,
    this.registrada,
  });

  final String idRegistro;
  final String paciente;
  final String medicamento;
  final String dosis;
  final DateTime programada;
  final DateTime? registrada;

  /// La aplicacion del paciente envia el medicamento con su dosis ya pegada
  /// («Metformina 850 mg»); en ese caso no se repite detras.
  String get descripcion => dosis.isEmpty || medicamento.endsWith(dosis)
      ? medicamento
      : '$medicamento · $dosis';

  /// Hora en que el paciente dijo haberla tomado, o la programada si no consta.
  String get horaReportada => formatoHora(registrada ?? programada);

  factory TomaPorConfirmar.desdeJson(Map<String, dynamic> json) =>
      TomaPorConfirmar(
        idRegistro: json['id_registro'] as String,
        paciente: (json['paciente'] as String?) ?? '',
        medicamento: json['medicamento'] as String,
        dosis: (json['dosis'] as String?) ?? '',
        programada:
            DateTime.parse(json['fecha_hora_programada'] as String).toLocal(),
        registrada: json['fecha_hora_registro'] == null
            ? null
            : DateTime.parse(json['fecha_hora_registro'] as String).toLocal(),
      );
}
