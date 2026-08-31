import 'package:flutter/material.dart';

import '../models/toma.dart';
import '../utils/constantes.dart';
import '../utils/tema.dart';

/// Registro de una dosis no tomada (RF03).
///
/// Confirmar una toma se resuelve en el listado con un solo boton; esta
/// pantalla es para el caso contrario, donde si conviene preguntar el motivo:
/// el olvido, la complejidad del regimen y la falta de comprension de las
/// indicaciones son las tres causas que el diagnostico identifico (OE1), y
/// registrarlas convierte una omision en informacion util para la consulta.
///
/// El motivo es opcional a proposito. Obligar a justificarse antes de poder
/// continuar invita a responder cualquier cosa con tal de cerrar la pantalla,
/// y un dato inventado es peor que un dato ausente.
class RegistroTomaScreen extends StatefulWidget {
  const RegistroTomaScreen({
    super.key,
    required this.medicamento,
    required this.dosis,
    required this.programada,
  });

  final String medicamento;
  final String dosis;
  final DateTime programada;

  @override
  State<RegistroTomaScreen> createState() => _RegistroTomaScreenState();
}

class _RegistroTomaScreenState extends State<RegistroTomaScreen> {
  static const List<String> _motivosFrecuentes = [
    'Me olvidé',
    'No tenía el medicamento',
    'Me sentí mal al tomarlo',
    'Me sentía bien y no lo creí necesario',
    'No estaba en casa',
  ];

  String? _motivoElegido;
  final _otroMotivo = TextEditingController();

  @override
  void dispose() {
    _otroMotivo.dispose();
    super.dispose();
  }

  String? get _motivoFinal {
    if (_motivoElegido == 'Otro') {
      final texto = _otroMotivo.text.trim();
      return texto.isEmpty ? null : texto;
    }
    return _motivoElegido;
  }

  void _guardar() {
    final toma = Toma.omitida(
      medicamento: widget.medicamento,
      dosis: widget.dosis,
      programada: widget.programada,
      motivo: _motivoFinal,
    );
    Navigator.of(context).pop(toma);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('No tomé esta dosis')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.medicamento,
                        style: const TextStyle(
                          fontSize: 21,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Programada para las '
                        '${formatoHora(widget.programada)} del '
                        '${formatoFecha(widget.programada)}',
                        style: const TextStyle(
                          fontSize: 16,
                          color: Tema.neutro,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              const Text(
                '¿Por qué no pudo tomarla?',
                style: TextStyle(fontSize: 19, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 4),
              const Text(
                'Es opcional, pero ayuda a su médico a acompañarle mejor.',
                style: TextStyle(fontSize: 15, color: Tema.neutro),
              ),
              const SizedBox(height: 12),

              ..._motivosFrecuentes.map(
                (motivo) => RadioListTile<String>(
                  value: motivo,
                  groupValue: _motivoElegido,
                  onChanged: (valor) => setState(() => _motivoElegido = valor),
                  title: Text(motivo, style: const TextStyle(fontSize: 18)),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
              RadioListTile<String>(
                value: 'Otro',
                groupValue: _motivoElegido,
                onChanged: (valor) => setState(() => _motivoElegido = valor),
                title: const Text('Otro motivo', style: TextStyle(fontSize: 18)),
                contentPadding: EdgeInsets.zero,
              ),

              if (_motivoElegido == 'Otro') ...[
                const SizedBox(height: 8),
                TextField(
                  controller: _otroMotivo,
                  maxLength: 200,
                  maxLines: 3,
                  style: const TextStyle(fontSize: 18),
                  decoration: const InputDecoration(
                    hintText: 'Cuéntenos brevemente qué ocurrió',
                  ),
                ),
              ],

              const SizedBox(height: 20),
              FilledButton(
                onPressed: _guardar,
                style: FilledButton.styleFrom(backgroundColor: Tema.peligro),
                child: const Text('Registrar que no la tomé'),
              ),
              const SizedBox(height: 10),
              OutlinedButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cancelar'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
