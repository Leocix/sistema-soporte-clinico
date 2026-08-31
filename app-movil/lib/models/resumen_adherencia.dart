/// Indicadores de adherencia observada que devuelve `/api/adherencia/mi-resumen`.
class ResumenAdherencia {
  const ResumenAdherencia({
    required this.totalEventos,
    required this.cumplidos,
    required this.omitidos,
    required this.tasaAdherencia,
    required this.omisionesConsecutivas,
    this.retrasoPromedioMin,
    this.ultimaTomaRegistrada,
  });

  final int totalEventos;
  final int cumplidos;
  final int omitidos;

  /// Porcentaje de cumplimiento sobre los eventos con desenlace.
  final double tasaAdherencia;

  final int omisionesConsecutivas;
  final double? retrasoPromedioMin;
  final DateTime? ultimaTomaRegistrada;

  bool get sinDatos => totalEventos == 0;

  /// Mensaje de aliento o de alerta, en lenguaje llano.
  ///
  /// El paciente no necesita un semaforo de riesgo clinico —eso es informacion
  /// para el medico—, sino saber como va y que hacer. Etiquetar a alguien como
  /// "riesgo alto" en su propio telefono desalienta mas de lo que ayuda.
  String get mensaje {
    if (sinDatos) {
      return 'Aun no hay tomas registradas. Comience confirmando la primera '
          'dosis del dia.';
    }
    if (omisionesConsecutivas >= 3) {
      return 'Lleva $omisionesConsecutivas dosis seguidas sin tomar. '
          'Converselo con su medico en el proximo control.';
    }
    if (tasaAdherencia >= 90) {
      return 'Muy bien: esta cumpliendo el ${tasaAdherencia.toStringAsFixed(0)} % '
          'de sus tomas.';
    }
    if (tasaAdherencia >= 70) {
      return 'Va por buen camino, con un ${tasaAdherencia.toStringAsFixed(0)} % '
          'de cumplimiento. Intente no saltarse ninguna dosis.';
    }
    return 'Su cumplimiento es del ${tasaAdherencia.toStringAsFixed(0)} %. '
        'Recuerde que el tratamiento funciona mejor si es constante.';
  }

  factory ResumenAdherencia.desdeJson(Map<String, dynamic> json) =>
      ResumenAdherencia(
        totalEventos: json['total_eventos'] as int,
        cumplidos: json['cumplidos'] as int,
        omitidos: json['omitidos'] as int,
        tasaAdherencia: (json['tasa_adherencia'] as num).toDouble(),
        omisionesConsecutivas: json['omisiones_consecutivas'] as int,
        retrasoPromedioMin: (json['retraso_promedio_min'] as num?)?.toDouble(),
        ultimaTomaRegistrada: json['ultima_toma_registrada'] == null
            ? null
            : DateTime.parse(json['ultima_toma_registrada'] as String)
                .toLocal(),
      );
}
