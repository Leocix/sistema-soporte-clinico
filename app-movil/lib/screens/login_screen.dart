import 'package:flutter/material.dart';

import '../models/sesion.dart';
import '../services/almacenamiento.dart';
import '../services/api_service.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';
import 'inicio_familiar.dart';
import 'inicio_paciente.dart';
import 'registro_familiar.dart';

/// Acceso a la aplicacion (RF01).
///
/// Entran dos personas distintas: el paciente y su acompanante familiar
/// (RF09). Quien entra declara su perfil, igual que en el panel web; nunca es
/// `medico`, porque esta aplicacion no atiende al personal clinico. Un medico
/// que lo intente recibe el mismo mensaje generico que una credencial
/// equivocada, sin pistas sobre cual de los datos fallo.
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
  PerfilUsuario _perfil = PerfilUsuario.paciente;
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
        perfil: _perfil,
      );
      widget.api.token = sesion.token;
      await Almacenamiento.instancia
          .guardarSesion(sesion.token, sesion.usuario);

      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(
          // El destino lo decide el perfil que devuelve el servidor, no el que
          // se eligio en el formulario: es el token quien manda.
          builder: (_) => pantallaDeInicio(widget.api, sesion.usuario),
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
                // Quien entra declara su perfil. Se muestra como dos botones
                // grandes y no como una lista desplegable: son solo dos
                // opciones y conviene que ambas se vean sin desplegar nada.
                SegmentedButton<PerfilUsuario>(
                  segments: const [
                    ButtonSegment(
                      value: PerfilUsuario.paciente,
                      icon: Icon(Icons.person_outline),
                      label: Text('Soy el paciente'),
                    ),
                    ButtonSegment(
                      value: PerfilUsuario.familiar,
                      icon: Icon(Icons.diversity_3_outlined),
                      label: Text('Soy familiar'),
                    ),
                  ],
                  selected: {_perfil},
                  showSelectedIcon: false,
                  onSelectionChanged: (seleccion) =>
                      setState(() => _perfil = seleccion.first),
                  style: SegmentedButton.styleFrom(
                    minimumSize: const Size.fromHeight(52),
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(height: 20),
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
                  validator: (valor) =>
                      (valor ?? '').isEmpty ? 'Escriba su contraseña.' : null,
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
                const Divider(height: 36),
                TextButton.icon(
                  onPressed: _enviando
                      ? null
                      : () => Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) =>
                                  RegistroFamiliarScreen(api: widget.api),
                            ),
                          ),
                  icon: const Icon(Icons.key_outlined, size: 22),
                  label: const Text(
                    'Un familiar me dio un código',
                    style: TextStyle(fontSize: 16),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Pantalla inicial que corresponde a la sesion recien abierta.
///
/// Vive aqui, junto al acceso, para que exista un unico lugar donde se decide
/// que ve cada perfil. Repartir esa decision entre el arranque y el inicio de
/// sesion es la forma de que un dia dejen de coincidir.
Widget pantallaDeInicio(ServicioApi api, Usuario usuario) => usuario.esFamiliar
    ? InicioFamiliar(api: api, usuario: usuario)
    : InicioPaciente(api: api, usuario: usuario);
