/// Medicamento del plan de tomas del paciente.
///
/// El plan vive **en el dispositivo**, no en el servidor. El modelo de datos
/// actual guarda la carga terapeutica de forma agregada (numero de farmacos y
/// tomas al dia), no la lista nominal de prescripciones: esa tabla es trabajo
/// del Sprint 3, cuando el medico gestione el esquema farmacologico desde el
/// panel. Hasta entonces el paciente declara su plan aqui y lo que se
/// sincroniza con el API son los eventos de toma, que es lo que alimenta el
/// calculo de adherencia y las caracteristicas del modelo predictivo.
class Medicamento {
  const Medicamento({
    required this.id,
    required this.nombre,
    required this.dosis,
    required this.horarios,
  });

  final String id;
  final String nombre;
  final String dosis;

  /// Horas de toma en formato `HH:mm`, ordenadas.
  final List<String> horarios;

  /// Etiqueta con la que el evento viaja al API.
  ///
  /// Debe ser estable en el tiempo: junto con el horario programado forma la
  /// clave que hace idempotente la sincronizacion. Si cambia, un reenvio
  /// crearia un evento nuevo en lugar de actualizar el existente.
  String get etiqueta => dosis.isEmpty ? nombre : '$nombre $dosis';

  Medicamento copiarCon(
          {String? nombre, String? dosis, List<String>? horarios}) =>
      Medicamento(
        id: id,
        nombre: nombre ?? this.nombre,
        dosis: dosis ?? this.dosis,
        horarios: horarios ?? this.horarios,
      );

  factory Medicamento.desdeJson(Map<String, dynamic> json) => Medicamento(
        id: json['id'] as String,
        nombre: json['nombre'] as String,
        dosis: (json['dosis'] as String?) ?? '',
        horarios: (json['horarios'] as List<dynamic>).cast<String>(),
      );

  Map<String, dynamic> aJson() => {
        'id': id,
        'nombre': nombre,
        'dosis': dosis,
        'horarios': horarios,
      };
}
