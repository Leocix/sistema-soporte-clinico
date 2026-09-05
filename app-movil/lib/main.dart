import 'package:flutter/material.dart';

import 'models/sesion.dart';
import 'screens/home_screen.dart';
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
  runApp(const AplicacionPaciente());
}

/// Aplicacion del paciente del sistema de soporte clinico.
///
/// Cubre RF01 (acceso con perfil de paciente) y RF03 (registro de la toma de
/// medicamentos). Los recordatorios (RF08) llegan en el Sprint 4.
class AplicacionPaciente extends StatelessWidget {
  const AplicacionPaciente({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mi tratamiento',
      debugShowCheckedModeBanner: false,
      theme: Tema.construir(),
      home: const _Arranque(),
    );
  }
}

/// Decide la primera pantalla segun haya o no una sesion guardada.
class _Arranque extends StatefulWidget {
  const _Arranque();

  @override
  State<_Arranque> createState() => _ArranqueState();
}

class _ArranqueState extends State<_Arranque> {
  final ServicioApi _api = ServicioApi();

  bool _comprobando = true;
  Usuario? _usuario;

  @override
  void initState() {
    super.initState();
    _restaurarSesion();
  }

  @override
  void dispose() {
    _api.cerrar();
    super.dispose();
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
        : HomeScreen(api: _api, usuario: usuario);
  }
}
