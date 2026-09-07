/// Perfil con el que se entra en la aplicacion (RF01).
///
/// La aplicacion atiende a dos personas distintas: el paciente, que registra
/// sus tomas, y su acompanante familiar, que las corrobora (RF09). No son el
/// mismo usuario con permisos distintos sino dos recorridos separados, y el
/// perfil es lo que decide cual se muestra.
enum PerfilUsuario {
  paciente('paciente'),
  familiar('familiar');

  const PerfilUsuario(this.codigo);

  final String codigo;

  static PerfilUsuario desdeCodigo(String? codigo) =>
      PerfilUsuario.values.firstWhere(
        (p) => p.codigo == codigo,
        // Las sesiones guardadas antes de que existiera el perfil familiar no
        // llevan el campo; todas eran de pacientes.
        orElse: () => PerfilUsuario.paciente,
      );
}

/// Cuenta con la que se inicia sesion (RF01).
class Usuario {
  const Usuario({
    required this.idUsuario,
    required this.nombres,
    required this.apellidos,
    required this.correo,
    this.perfil = PerfilUsuario.paciente,
  });

  final String idUsuario;
  final String nombres;
  final String apellidos;
  final String correo;
  final PerfilUsuario perfil;

  String get nombreCompleto => '$nombres $apellidos'.trim();

  bool get esFamiliar => perfil == PerfilUsuario.familiar;

  factory Usuario.desdeJson(Map<String, dynamic> json) => Usuario(
        idUsuario: json['id_usuario'] as String,
        nombres: json['nombres'] as String,
        apellidos: json['apellidos'] as String,
        correo: json['correo'] as String,
        perfil: PerfilUsuario.desdeCodigo(json['rol'] as String?),
      );

  Map<String, dynamic> aJson() => {
        'id_usuario': idUsuario,
        'nombres': nombres,
        'apellidos': apellidos,
        'correo': correo,
        'rol': perfil.codigo,
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
