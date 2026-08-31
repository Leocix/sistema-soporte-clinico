import 'package:flutter/material.dart';

import '../utils/tema.dart';

/// Tono del aviso mostrado al paciente.
enum TonoMensaje { informacion, aviso, error, exito }

/// Franja de aviso con icono, en lenguaje llano y con contraste suficiente.
class MensajeEstado extends StatelessWidget {
  const MensajeEstado({
    super.key,
    required this.texto,
    this.tono = TonoMensaje.informacion,
    this.accion,
    this.textoAccion,
  });

  final String texto;
  final TonoMensaje tono;
  final VoidCallback? accion;
  final String? textoAccion;

  ({Color color, Color fondo, Color borde, IconData icono}) get _estilo =>
      switch (tono) {
        TonoMensaje.exito => (
            color: Tema.exito,
            fondo: Tema.exitoFondo,
            borde: const Color(0xFFBEE3D0),
            icono: Icons.check_circle_outline,
          ),
        TonoMensaje.aviso => (
            color: Tema.aviso,
            fondo: Tema.avisoFondo,
            borde: const Color(0xFFEFD9A8),
            icono: Icons.cloud_off,
          ),
        TonoMensaje.error => (
            color: Tema.peligro,
            fondo: Tema.peligroFondo,
            borde: const Color(0xFFF2C4C1),
            icono: Icons.error_outline,
          ),
        TonoMensaje.informacion => (
            color: Tema.primarioOscuro,
            fondo: const Color(0xFFE8F1F8),
            borde: const Color(0xFFC3DCEC),
            icono: Icons.info_outline,
          ),
      };

  @override
  Widget build(BuildContext context) {
    final estilo = _estilo;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      margin: const EdgeInsets.only(bottom: 14),
      decoration: BoxDecoration(
        color: estilo.fondo,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: estilo.borde),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(estilo.icono, color: estilo.color, size: 24),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              texto,
              style: TextStyle(fontSize: 16, color: estilo.color),
            ),
          ),
          if (accion != null && textoAccion != null)
            TextButton(
              onPressed: accion,
              child: Text(
                textoAccion!,
                style: TextStyle(color: estilo.color, fontSize: 16),
              ),
            ),
        ],
      ),
    );
  }
}
