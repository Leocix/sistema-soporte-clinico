import 'package:flutter/material.dart';

import '../utils/tema.dart';

/// Resumen de la Politica de privacidad y de los Terminos y condiciones.
///
/// El texto completo vive en el panel web (/privacidad y /terminos). Aqui va
/// lo que el paciente necesita saber antes de usar la aplicacion, en frases
/// cortas y letra grande, sin depender de abrir un navegador.
class LegalScreen extends StatelessWidget {
  const LegalScreen({super.key});

  static const _privacidad = <(String, String)>[
    (
      'Quién cuida sus datos',
      'El Consultorio médico Milko Ugaz Zegarra, de Chiclayo, es el responsable '
          'de sus datos. Se tratan con su consentimiento, según la Ley N.° 29733 '
          'de Protección de Datos Personales.',
    ),
    (
      'Qué datos guardamos',
      'Su nombre y contacto, su diagnóstico y medicamentos, y las tomas que usted '
          'registra. No accedemos a su ubicación, contactos, fotos, cámara ni '
          'micrófono.',
    ),
    (
      'Para qué',
      'Para que su médico acompañe su tratamiento, para recordarle sus tomas y, '
          'solo si usted firmó el consentimiento del estudio, para una '
          'investigación en la que aparece con un código y no con su nombre. '
          'Nunca para publicidad.',
    ),
    (
      'Quién los ve',
      'Su médico tratante. El familiar que usted invite solo ve su cumplimiento '
          'y las tomas por confirmar, y usted puede retirarlo cuando quiera.',
    ),
    (
      'Sus derechos',
      'Puede pedir ver, corregir o eliminar sus datos, o retirar su '
          'consentimiento para el estudio, sin que eso afecte su atención. '
          'Solicítelo en el consultorio.',
    ),
  ];

  static const _terminos = <(String, String)>[
    (
      'No es un servicio de emergencias',
      'Ante una emergencia acuda al establecimiento de salud más cercano o '
          'llame al SAMU (106).',
    ),
    (
      'No reemplaza a su médico',
      'No cambie, suspenda ni duplique un medicamento por lo que vea en la '
          'aplicación. Consulte siempre a su médico.',
    ),
    (
      'Registre con la verdad',
      'Marque sus tomas cuando realmente ocurran, también las que no pudo '
          'hacer. Si es familiar, confirme solo lo que vio.',
    ),
    (
      'Cuide su contraseña',
      'Su cuenta es personal. El consultorio nunca le pedirá su contraseña.',
    ),
    (
      'Recordatorios',
      'Dependen de que su teléfono tenga batería y permiso para notificaciones. '
          'Son una ayuda, no una garantía.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Privacidad y términos')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const _Titulo('Política de privacidad'),
          for (final (titulo, texto) in _privacidad) _Punto(titulo, texto),
          const SizedBox(height: 16),
          const _Titulo('Términos y condiciones'),
          for (final (titulo, texto) in _terminos) _Punto(titulo, texto),
          const SizedBox(height: 16),
          const Text(
            'Los textos completos están en el panel del consultorio, en las '
            'páginas «Privacidad» y «Términos». Al usar la aplicación usted '
            'los acepta.',
            style: TextStyle(fontSize: 15, color: Tema.neutro),
          ),
        ],
      ),
    );
  }
}

class _Titulo extends StatelessWidget {
  const _Titulo(this.texto);

  final String texto;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Text(
          texto,
          style: const TextStyle(
            fontSize: 21,
            fontWeight: FontWeight.w700,
            color: Tema.primarioOscuro,
          ),
        ),
      );
}

class _Punto extends StatelessWidget {
  const _Punto(this.titulo, this.texto);

  final String titulo;
  final String texto;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              titulo,
              style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 2),
            Text(texto, style: const TextStyle(fontSize: 16, height: 1.4)),
          ],
        ),
      );
}

/// Enlace «Privacidad y términos» que abre [LegalScreen].
class EnlaceLegal extends StatelessWidget {
  const EnlaceLegal({super.key, this.prefijo = 'Al ingresar acepta los'});

  final String prefijo;

  @override
  Widget build(BuildContext context) => TextButton(
        onPressed: () => Navigator.of(context).push(
          MaterialPageRoute<void>(builder: (_) => const LegalScreen()),
        ),
        child: Text(
          '$prefijo Términos y la Política de privacidad',
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 14,
            decoration: TextDecoration.underline,
          ),
        ),
      );
}
