import 'package:flutter/material.dart';

import '../models/sesion.dart';
import '../services/api_service.dart';
import '../services/notification_service.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';

/// Pestana de cuenta: quien esta dentro, estado de las alertas y salida.
///
/// Recoge lo que antes vivia en el menu de tres puntos. Un menu oculto detras
/// de tres puntos es una barrera para el usuario objetivo de esta aplicacion
/// —un adulto mayor—, que no tiene por que saber que ahi hay algo. En la barra
/// inferior cada funcion es visible desde el primer momento.
class CuentaScreen extends StatefulWidget {
  const CuentaScreen({
    super.key,
    required this.usuario,
    required this.alCerrarSesion,
    this.api,
    this.alUnirseAOtroPaciente,
  });

  final Usuario usuario;
  final Future<void> Function() alCerrarSesion;

  /// Necesario solo en el perfil familiar, para canjear otro codigo.
  final ServicioApi? api;
  final VoidCallback? alUnirseAOtroPaciente;

  @override
  State<CuentaScreen> createState() => _CuentaScreenState();
}

class _CuentaScreenState extends State<CuentaScreen> {
  ({bool permitido, int avisos})? _alertas;

  @override
  void initState() {
    super.initState();
    _consultarAlertas();
  }

  Future<void> _consultarAlertas() async {
    if (widget.usuario.esFamiliar) return;
    final estado = await ServicioNotificaciones.instancia.estado();
    if (!mounted) return;
    setState(() => _alertas = estado);
  }

  Future<void> _activarAlertas() async {
    await ServicioNotificaciones.instancia.solicitarPermiso();
    await _consultarAlertas();
    if (!mounted) return;

    final estado = _alertas;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          estado != null && estado.permitido
              ? 'Alertas activadas.'
              : 'No se activaron. Puede permitirlas en los ajustes del '
                  'teléfono, en Notificaciones.',
          style: const TextStyle(fontSize: 17),
        ),
        backgroundColor:
            estado != null && estado.permitido ? Tema.exito : Tema.aviso,
      ),
    );
  }

  Future<void> _unirseAOtroPaciente() async {
    final api = widget.api;
    if (api == null) return;

    final codigo = await showDialog<String>(
      context: context,
      builder: (_) => const _DialogoCodigo(),
    );
    if (codigo == null || codigo.isEmpty) return;

    try {
      final paciente = await api.unirseConCodigo(codigo);
      widget.alUnirseAOtroPaciente?.call();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Ahora acompaña también a ${paciente.nombre}.',
            style: const TextStyle(fontSize: 17),
          ),
          backgroundColor: Tema.exito,
        ),
      );
    } on ErrorDeConexion catch (e) {
      _avisarError(e.mensaje);
    } on ErrorApi catch (e) {
      _avisarError(e.mensaje);
    }
  }

  void _avisarError(String mensaje) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje, style: const TextStyle(fontSize: 17)),
        backgroundColor: Tema.peligro,
      ),
    );
  }

  Future<void> _confirmarSalida() async {
    final salir = await showDialog<bool>(
      context: context,
      builder: (contexto) => AlertDialog(
        title: const Text('¿Cerrar sesión?'),
        content: const Text(
          'Sus medicamentos y las tomas que aún no se han enviado se quedan '
          'guardados en este teléfono.',
          style: TextStyle(fontSize: 17),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(contexto).pop(false),
            child: const Text('Cancelar', style: TextStyle(fontSize: 17)),
          ),
          FilledButton(
            onPressed: () => Navigator.of(contexto).pop(true),
            style: FilledButton.styleFrom(backgroundColor: Tema.peligro),
            child: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
    if (salir == true) await widget.alCerrarSesion();
  }

  @override
  Widget build(BuildContext context) {
    final usuario = widget.usuario;
    final alertas = _alertas;

    return Scaffold(
      appBar: AppBar(title: const Text('Mi cuenta')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: Colors.white,
            elevation: 0,
            margin: Tema.margenTarjeta,
            shape: Tema.formaTarjeta,
            child: Padding(
              padding: const EdgeInsets.all(18),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: Tema.fondo,
                    child: Icon(
                      usuario.esFamiliar
                          ? Icons.diversity_3_outlined
                          : Icons.person_outline,
                      size: 30,
                      color: Tema.primario,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          usuario.nombreCompleto,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        Text(
                          usuario.correo,
                          style: const TextStyle(
                            fontSize: 16,
                            color: Tema.neutro,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          usuario.esFamiliar
                              ? 'Acompañante familiar'
                              : 'Paciente',
                          style: const TextStyle(
                            fontSize: 16,
                            color: Tema.primarioOscuro,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          if (!usuario.esFamiliar) ...[
            const SizedBox(height: 8),
            const Text(
              'Alertas de sus medicamentos',
              style: TextStyle(fontSize: 19, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 10),
            if (alertas == null)
              const Center(child: CircularProgressIndicator())
            else if (!alertas.permitido)
              MensajeEstado(
                texto: 'Las alertas están desactivadas. Sin ellas la '
                    'aplicación no puede avisarle a la hora de cada toma.',
                tono: TonoMensaje.aviso,
                textoAccion: 'Activar',
                accion: _activarAlertas,
              )
            else if (alertas.avisos == 0)
              const MensajeEstado(
                texto: 'Las alertas están permitidas, pero todavía no hay '
                    'ninguna programada. Agregue sus medicamentos con su hora '
                    'en la pestaña «Medicinas».',
              )
            else
              MensajeEstado(
                texto: 'Tiene ${alertas.avisos} alerta(s) programada(s) en '
                    'este teléfono. Suenan a su hora aunque no tenga internet.',
                tono: TonoMensaje.exito,
              ),
          ],

          if (usuario.esFamiliar) ...[
            const SizedBox(height: 8),
            OutlinedButton.icon(
              onPressed: _unirseAOtroPaciente,
              icon: const Icon(Icons.person_add_alt, size: 24),
              label: const Text('Acompañar a otra persona'),
            ),
            const SizedBox(height: 8),
            const Text(
              'Si otro familiar suyo también usa esta aplicación, pídale su '
              'código y podrá acompañarlo desde esta misma cuenta.',
              style: TextStyle(fontSize: 16, color: Tema.neutro),
            ),
          ],

          const SizedBox(height: 28),
          OutlinedButton.icon(
            onPressed: _confirmarSalida,
            icon: const Icon(Icons.logout, size: 24),
            label: const Text('Cerrar sesión'),
            style: OutlinedButton.styleFrom(foregroundColor: Tema.peligro),
          ),
        ],
      ),
    );
  }
}

/// Pide un codigo de invitacion para acompanar a otra persona.
class _DialogoCodigo extends StatefulWidget {
  const _DialogoCodigo();

  @override
  State<_DialogoCodigo> createState() => _DialogoCodigoState();
}

class _DialogoCodigoState extends State<_DialogoCodigo> {
  final _codigo = TextEditingController();

  @override
  void dispose() {
    _codigo.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Código de invitación'),
      content: TextField(
        controller: _codigo,
        autofocus: true,
        textCapitalization: TextCapitalization.characters,
        style: const TextStyle(fontSize: 22, letterSpacing: 3),
        decoration: const InputDecoration(hintText: 'ABCD2345'),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar', style: TextStyle(fontSize: 17)),
        ),
        FilledButton(
          onPressed: () => Navigator.of(context).pop(_codigo.text.trim()),
          child: const Text('Continuar'),
        ),
      ],
    );
  }
}
