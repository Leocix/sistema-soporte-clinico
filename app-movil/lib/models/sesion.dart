/// Cuenta con la que el paciente inicia sesion (RF01).
class Usuario {
  const Usuario({
    required this.idUsuario,
    required this.nombres,
    required this.apellidos,
    required this.correo,
  });

  final String idUsuario;
  final String nombres;
  final String apellidos;
  final String correo;

  String get nombreCompleto => '$nombres $apellidos'.trim();

  factory Usuario.desdeJson(Map<String, dynamic> json) => Usuario(
        idUsuario: json['id_usuario'] as String,
        nombres: json['nombres'] as String,
        apellidos: json['apellidos'] as String,
        correo: json['correo'] as String,
      );

  Map<String, dynamic> aJson() => {
        'id_usuario': idUsuario,
        'nombres': nombres,
        'apellidos': apellidos,
        'correo': correo,
      };
}

/// Ficha clinica del paciente, tal como la devuelve `/api/pacientes/mi-ficha`.
///
/// Solo se conservan los campos que la aplicacion muestra. El resto de
/// variables del Anexo n.o 04 son competencia del panel medico.
class FichaPaciente {
  const FichaPaciente({
    required this.idPaciente,
    required this.codigoAnonimizado,
    required this.numeroFarmacos,
    required this.tomasDia,
  });

  final String idPaciente;
  final String codigoAnonimizado;
  final int numeroFarmacos;
  final int tomasDia;

  factory FichaPaciente.desdeJson(Map<String, dynamic> json) => FichaPaciente(
        idPaciente: json['id_paciente'] as String,
        codigoAnonimizado: json['codigo_anonimizado'] as String,
        numeroFarmacos: json['numero_farmacos'] as int,
        tomasDia: json['tomas_dia'] as int,
      );
}
