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
                      Text(
                        dosis.medicamento,
                        style: const TextStyle(
                          fontSize: 19,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      if (dosis.dosis.isNotEmpty)
                        Text(
                          dosis.dosis,
                          style: const TextStyle(
                            fontSize: 16,
                            color: Tema.neutro,
                          ),
                        ),
                    ],
                  ),
                ),
                if (dosis.pendienteDeEnvio)
                  const Tooltip(
                    message: 'Guardado en el telefono, pendiente de enviar',
                    child: Icon(Icons.cloud_off, color: Tema.aviso, size: 26),
                  ),
              ],
            ),
            const SizedBox(height: 14),
            if (registro != null)
              _Respuesta(registro: registro)
            else if (dosis.esFutura)
              const _Espera()
            else
              _Acciones(alConfirmar: alConfirmar, alOmitir: alOmitir),
          ],
        ),
      ),
    );
  }
}

class _Acciones extends StatelessWidget {
  const _Acciones({required this.alConfirmar, required this.alOmitir});

  final VoidCallback alConfirmar;
  final VoidCallback alOmitir;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
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
  const _Espera();

  @override
  Widget build(BuildContext context) {
    return const Row(
      children: [
        Icon(Icons.schedule, color: Tema.neutro, size: 22),
        SizedBox(width: 8),
        Expanded(
          child: Text(
            'Aún no es la hora de esta dosis.',
            style: TextStyle(fontSize: 16, color: Tema.neutro),
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
              ],
            ),
          ),
        ],
      ),
    );
  }
}
