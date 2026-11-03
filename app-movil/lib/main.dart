import 'package:flutter/material.dart';

import 'models/sesion.dart';
import 'screens/login_screen.dart';
import 'services/almacenamiento.dart';
import 'services/api_service.dart';
import 'services/notification_service.dart';
import 'utils/tema.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Se prepara el complemento y la zona horaria antes de dibujar nada: el
  // recordatorio debe sonar a la hora del paciente, no a la del servidor.
  // No se pide el permiso aqui; eso ocurre cuando el paciente configura su
  // plan y entiende para que sirve.
  await ServicioNotificaciones.instancia.iniciar();
  runApp(AplicacionPaciente(api: ServicioApi()));
}

/// Aplicacion movil del sistema de soporte clinico.
///
/// Cubre RF01 (acceso con perfil diferenciado), RF03 (registro de la toma de
/// medicamentos), RF08 (recordatorios en el dispositivo) y RF09 (grupo
/// familiar de acompanamiento).
class AplicacionPaciente extends StatelessWidget {
  const AplicacionPaciente({super.key, required this.api});

  /// Cliente unico para toda la vida de la aplicacion.
  ///
  /// Antes lo creaba (y lo cerraba en su `dispose`) la pantalla de arranque.
  /// Al iniciar sesion, el ingreso reemplaza esa pantalla, de modo que el
  /// cliente quedaba cerrado y cada peticion fallaba con «Client is already
  /// closed»: el paciente veia «sin conexion» hasta reabrir la aplicacion,
  /// que entonces arrancaba con la sesion guardada y sin reemplazo alguno.
  final ServicioApi api;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mi tratamiento',
      debugShowCheckedModeBanner: false,
      theme: Tema.construir(),
      home: _Arranque(api: api),
    );
  }
}

/// Decide la primera pantalla segun haya o no una sesion guardada.
class _Arranque extends StatefulWidget {
  const _Arranque({required this.api});

  final ServicioApi api;

  @override
  State<_Arranque> createState() => _ArranqueState();
}

class _ArranqueState extends State<_Arranque> {
  ServicioApi get _api => widget.api;

  bool _comprobando = true;
  Usuario? _usuario;

  @override
  void initState() {
    super.initState();
    _restaurarSesion();
  }

  /// Rehidrata la sesion guardada y la valida contra el servidor.
  ///
  /// Un token almacenado puede haber caducado mientras la aplicacion estaba
  /// cerrada. Si el servidor no responde no se cierra la sesion: sin conexion
  /// el paciente debe poder seguir registrando sus tomas contra la cola local,
  /// que es justamente el escenario para el que se diseno el envio en lote.
  Future<void> _restaurarSesion() async {
    final token = await Almacenamiento.instancia.leerToken();
    final guardado = await Almacenamiento.instancia.leerUsuario();

    if (token == null || guardado == null) {
      if (mounted) setState(() => _comprobando = false);
      return;
    }

    _api.token = token;
    var usuario = guardado;

    try {
      usuario = await _api.perfil();
    } on ErrorApi catch (e) {
      if (e.sesionExpirada) {
        await Almacenamiento.instancia.cerrarSesion();
        _api.token = null;
        if (mounted) setState(() => _comprobando = false);
        return;
      }
    } on ErrorDeConexion {
      // Se conserva la sesion guardada y se sigue en modo sin conexion.
    }

    if (!mounted) return;
    setState(() {
      _usuario = usuario;
      _comprobando = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_comprobando) {
      return const Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.medication_liquid_outlined,
                size: 64,
                color: Tema.primario,
              ),
              SizedBox(height: 20),
              CircularProgressIndicator(),
            ],
          ),
        ),
      );
    }

    final usuario = _usuario;
    return usuario == null
        ? LoginScreen(api: _api)
        : pantallaDeInicio(_api, usuario);
  }
}
