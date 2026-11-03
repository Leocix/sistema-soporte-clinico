import 'package:flutter/material.dart';

import '../models/toma.dart';
import '../utils/constantes.dart';
import '../utils/tema.dart';

/// Tarjeta de una dosis del dia.
///
/// Cuando la dosis aun no tiene respuesta muestra dos botones grandes y
/// literales. "Ya la tome" resuelve el caso frecuente en un solo toque: el
/// paciente no elige entre "tomada" y "tomada con retraso" —eso lo deduce la
/// aplicacion comparando la hora—, porque pedirselo seria devolverle el
/// autorreporte subjetivo que el sistema quiere sustituir.
class TarjetaToma extends StatelessWidget {
  const TarjetaToma({
    super.key,
    required this.dosis,
    required this.alConfirmar,
    required this.alOmitir,
  });

  final DosisDelDia dosis;
  final VoidCallback alConfirmar;
  final VoidCallback alOmitir;

  @override
  Widget build(BuildContext context) {
    final registro = dosis.registro;

    return Card(
      color: Colors.white,
      elevation: 0,
      margin: Tema.margenTarjeta,
      shape: Tema.formaTarjeta,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: Tema.fondo,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    formatoHora(dosis.programada),
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // La etiqueta ya trae la dosis («Losartán 50 mg»):
                      // repetirla debajo la mostraba dos veces.
                      Text(
                        dosis.medicamento,
                        style: const TextStyle(
                          fontSize: 19,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
                if (dosis.pendienteDeEnvio)
                  const Tooltip(
                    message: 'Guardado en el teléfono, pendiente de enviar',
                    child: Icon(Icons.cloud_off, color: Tema.aviso, size: 26),
                  ),
              ],
            ),
            const SizedBox(height: 14),
            if (registro != null)
              _Respuesta(registro: registro)
            else if (dosis.esFutura)
              _Espera(abre: dosis.abreVentana)
            else
              _Acciones(
                alConfirmar: alConfirmar,
                alOmitir: alOmitir,
                cerrada: dosis.ventanaCerrada,
                cierre: dosis.cierraVentana,
              ),
          ],
        ),
      ),
    );
  }
}

class _Acciones extends StatelessWidget {
  const _Acciones({
    required this.alConfirmar,
    required this.alOmitir,
    required this.cerrada,
    required this.cierre,
  });

  final VoidCallback alConfirmar;
  final VoidCallback alOmitir;

  /// Paso el plazo para marcarla como tomada (ventana de registro).
  final bool cerrada;
  final DateTime cierre;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (cerrada) ...[
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.lock_clock, color: Tema.neutro, size: 22),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'El plazo para marcarla como tomada terminó a las '
                  '${formatoHora(cierre)}. Si no la tomó, regístrelo abajo.',
                  style: const TextStyle(fontSize: 16, color: Tema.neutro),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
        ] else
          FilledButton.icon(
            onPressed: alConfirmar,
            icon: const Icon(Icons.check_circle_outline, size: 26),
            label: const Text('Ya la tomé'),
          ),
        const SizedBox(height: 10),
        OutlinedButton.icon(
          onPressed: alOmitir,
          icon: const Icon(Icons.cancel_outlined, size: 26),
          label: const Text('No la tomé'),
          style: OutlinedButton.styleFrom(foregroundColor: Tema.peligro),
        ),
      ],
    );
  }
}

class _Espera extends StatelessWidget {
  const _Espera({required this.abre});

  /// Hora desde la que se podra registrar la dosis.
  final DateTime abre;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Icon(Icons.schedule, color: Tema.neutro, size: 22),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            'Podrá registrarla desde las ${formatoHora(abre)}.',
            style: const TextStyle(fontSize: 16, color: Tema.neutro),
          ),
        ),
      ],
    );
  }
}

class _Respuesta extends StatelessWidget {
  const _Respuesta({required this.registro});

  final Toma registro;

  @override
  Widget build(BuildContext context) {
    final cumplida = registro.estado.cumplida;
    final color = cumplida ? Tema.exito : Tema.peligro;
    final fondo = cumplida ? Tema.exitoFondo : Tema.peligroFondo;
    final momento = registro.fechaHoraRegistro;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: fondo,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          Icon(
            cumplida ? Icons.check_circle : Icons.cancel,
            color: color,
            size: 26,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  registro.estado.etiqueta,
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    color: color,
                  ),
                ),
                if (momento != null)
                  Text(
                    'Registrada a las ${formatoHora(momento)}',
                    style: const TextStyle(fontSize: 15, color: Tema.neutro),
                  ),
                if (registro.motivoOmision != null &&
                    registro.motivoOmision!.isNotEmpty)
                  Text(
                    'Motivo: ${registro.motivoOmision}',
                    style: const TextStyle(fontSize: 15, color: Tema.neutro),
                  ),
                // Se muestra solo cuando existe. Anunciar «sin confirmar» en
                // cada dosis convertiria el acompanamiento en una sospecha
                // permanente sobre la palabra del paciente.
                if (registro.corroborada)
                  const Padding(
                    padding: EdgeInsets.only(top: 4),
                    child: Row(
                      children: [
                        Icon(Icons.verified_user_outlined,
                            size: 18, color: Tema.exito),
                        SizedBox(width: 6),
                        Text(
                          'Confirmada por su familia',
                          style: TextStyle(fontSize: 15, color: Tema.exito),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
