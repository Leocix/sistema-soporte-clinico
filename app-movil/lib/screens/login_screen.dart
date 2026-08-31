import 'package:flutter/material.dart';

import '../services/almacenamiento.dart';
import '../services/api_service.dart';
import '../utils/constantes.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';
import 'home_screen.dart';

/// Acceso del paciente (RF01).
///
/// El perfil viaja fijo como `paciente`: esta aplicacion no atiende al
/// personal medico, que usa el panel web. Un medico que intente entrar aqui
/// recibe el mismo mensaje generico que una credencial equivocada, sin pistas
/// sobre cual de los dos datos fallo.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.api});

  final ServicioApi api;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formulario = GlobalKey<FormState>();
  final _correo = TextEditingController();
  final _contrasena = TextEditingController();

  bool _enviando = false;
  bool _ocultarContrasena = true;
  String? _error;

  @override
  void dispose() {
    _correo.dispose();
    _contrasena.dispose();
    super.dispose();
  }

  Future<void> _ingresar() async {
    if (!_formulario.currentState!.validate()) return;

    setState(() {
      _enviando = true;
      _error = null;
    });

    try {
      final sesion = await widget.api.iniciarSesion(
        _correo.text.trim(),
        _contrasena.text,
      );
      widget.api.token = sesion.token;
      await Almacenamiento.instancia.guardarSesion(sesion.token, sesion.usuario);

      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          builder: (_) => HomeScreen(api: widget.api, usuario: sesion.usuario),
        ),
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
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Form(
            key: _formulario,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 32),
                const Icon(
                  Icons.medication_liquid_outlined,
                  size: 72,
                  color: Tema.primario,
                ),
                const SizedBox(height: 20),
                const Text(
                  'Mi tratamiento',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.w700,
                    color: Tema.primarioOscuro,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Consultorio médico Milko Ugaz Zegarra',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 16, color: Tema.neutro),
                ),
                const SizedBox(height: 36),

                if (_error != null)
                  MensajeEstado(texto: _error!, tono: TonoMensaje.error),

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
                    prefixIcon: const Icon(Icons.lock_outline),
                    suffixIcon: IconButton(
                      // Mostrar la contrasena ayuda a quien escribe con
                      // dificultad en una pantalla tactil.
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
                  onFieldSubmitted: (_) => _ingresar(),
                  validator: (valor) => (valor ?? '').isEmpty
                      ? 'Escriba su contraseña.'
                      : null,
                ),
                const SizedBox(height: 28),

                FilledButton(
                  onPressed: _enviando ? null : _ingresar,
                  child: _enviando
                      ? const SizedBox(
                          height: 24,
                          width: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Colors.white,
                          ),
                        )
                      : const Text('Ingresar'),
                ),
                const SizedBox(height: 20),

                const Text(
                  'Si no recuerda sus datos de acceso, consúltelos en el '
                  'consultorio.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 15, color: Tema.neutro),
                ),
                const SizedBox(height: 24),
                Text(
                  Constantes.urlApi,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 12, color: Tema.neutro),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
