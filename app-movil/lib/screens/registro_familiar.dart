import 'package:flutter/material.dart';

import '../services/almacenamiento.dart';
import '../services/api_service.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';
import 'login_screen.dart';

/// Alta de la cuenta del acompanante familiar mediante codigo (RF09).
///
/// Es la unica via de registro del sistema. No hay alta abierta: sin un codigo
/// vigente emitido por un paciente desde su propia aplicacion, esta pantalla no
/// crea nada. Asi el consentimiento del paciente no es una casilla que alguien
/// marca por el, sino la condicion tecnica para que la cuenta exista.
class RegistroFamiliarScreen extends StatefulWidget {
  const RegistroFamiliarScreen({super.key, required this.api});

  final ServicioApi api;

  @override
  State<RegistroFamiliarScreen> createState() => _RegistroFamiliarScreenState();
}

class _RegistroFamiliarScreenState extends State<RegistroFamiliarScreen> {
  final _formulario = GlobalKey<FormState>();
  final _codigo = TextEditingController();
  final _nombres = TextEditingController();
  final _apellidos = TextEditingController();
  final _correo = TextEditingController();
  final _contrasena = TextEditingController();

  bool _enviando = false;
  bool _ocultarContrasena = true;
  String? _error;

  @override
  void dispose() {
    _codigo.dispose();
    _nombres.dispose();
    _apellidos.dispose();
    _correo.dispose();
    _contrasena.dispose();
    super.dispose();
  }

  Future<void> _crear() async {
    if (!_formulario.currentState!.validate()) return;

    setState(() {
      _enviando = true;
      _error = null;
    });

    try {
      final sesion = await widget.api.registrarFamiliar(
        codigo: _codigo.text.trim().toUpperCase(),
        nombres: _nombres.text.trim(),
        apellidos: _apellidos.text.trim(),
        correo: _correo.text.trim(),
        contrasena: _contrasena.text,
      );
      widget.api.token = sesion.token;
      await Almacenamiento.instancia
          .guardarSesion(sesion.token, sesion.usuario);

      if (!mounted) return;
      // El alta deja la sesion abierta: pedirle que inicie sesion justo
      // despues de escribir su contrasena seria hacerle repetir el tramite.
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute<void>(
          builder: (_) => pantallaDeInicio(widget.api, sesion.usuario),
        ),
        (_) => false,
      );
    } on ErrorApi catch (e) {
      setState(() => _error = e.mensaje);
    } on ErrorDeConexion catch (e) {
      setState(() => _error = e.mensaje);
    } finally {
      if (mounted) setState(() => _enviando = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Crear mi cuenta')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formulario,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const MensajeEstado(
                  texto: 'Su familiar le dio un código desde su aplicación. '
                      'Con él podrá confirmar que tomó sus medicamentos.',
                ),
                if (_error != null)
                  MensajeEstado(texto: _error!, tono: TonoMensaje.error),

                TextFormField(
                  controller: _codigo,
                  textCapitalization: TextCapitalization.characters,
                  autocorrect: false,
                  textInputAction: TextInputAction.next,
                  style: const TextStyle(fontSize: 22, letterSpacing: 3),
                  decoration: const InputDecoration(
                    labelText: 'Código',
                    hintText: 'ABCD2345',
                    prefixIcon: Icon(Icons.key_outlined),
                  ),
                  validator: (valor) => (valor ?? '').trim().length < 6
                      ? 'Escriba el código completo.'
                      : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _nombres,
                  textCapitalization: TextCapitalization.words,
                  textInputAction: TextInputAction.next,
                  style: const TextStyle(fontSize: 19),
                  decoration: const InputDecoration(
                    labelText: 'Nombres',
                    prefixIcon: Icon(Icons.badge_outlined),
                  ),
                  validator: (valor) => (valor ?? '').trim().length < 2
                      ? 'Escriba sus nombres.'
                      : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _apellidos,
                  textCapitalization: TextCapitalization.words,
                  textInputAction: TextInputAction.next,
                  style: const TextStyle(fontSize: 19),
                  decoration: const InputDecoration(
                    labelText: 'Apellidos',
                    prefixIcon: Icon(Icons.badge_outlined),
                  ),
                  validator: (valor) => (valor ?? '').trim().length < 2
                      ? 'Escriba sus apellidos.'
                      : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _correo,
                  keyboardType: TextInputType.emailAddress,
                  autocorrect: false,
                  textInputAction: TextInputAction.next,
                  style: const TextStyle(fontSize: 19),
                  decoration: const InputDecoration(
                    labelText: 'Correo electrónico',
                    prefixIcon: Icon(Icons.mail_outline),
                  ),
                  validator: (valor) {
                    final v = (valor ?? '').trim();
                    if (v.isEmpty) return 'Escriba su correo.';
                    if (!v.contains('@')) return 'El correo no parece válido.';
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _contrasena,
                  obscureText: _ocultarContrasena,
                  style: const TextStyle(fontSize: 19),
                  decoration: InputDecoration(
                    labelText: 'Contraseña',
                    helperText: 'Al menos 8 caracteres.',
                    helperStyle: const TextStyle(fontSize: 14),
                    prefixIcon: const Icon(Icons.lock_outline),
                    suffixIcon: IconButton(
                      tooltip: _ocultarContrasena ? 'Mostrar' : 'Ocultar',
                      icon: Icon(
                        _ocultarContrasena
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                      ),
                      onPressed: () => setState(
                        () => _ocultarContrasena = !_ocultarContrasena,
                      ),
                    ),
                  ),
                  onFieldSubmitted: (_) => _crear(),
                  validator: (valor) => (valor ?? '').length < 8
                      ? 'Use al menos 8 caracteres.'
                      : null,
                ),
                const SizedBox(height: 28),
                FilledButton(
                  onPressed: _enviando ? null : _crear,
                  child: _enviando
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Colors.white,
                          ),
                        )
                      : const Text('Crear mi cuenta'),
                ),
                const SizedBox(height: 16),
                const Text(
                  'Solo verá las tomas de la persona que le dio el código, y '
                  'ella puede retirarle el acceso cuando quiera.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 15, color: Tema.neutro),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
