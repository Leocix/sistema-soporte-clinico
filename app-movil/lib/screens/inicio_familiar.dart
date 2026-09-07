import 'package:flutter/material.dart';

import '../models/familia.dart';
import '../models/sesion.dart';
import '../services/almacenamiento.dart';
import '../services/api_service.dart';
import '../utils/constantes.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';
import 'cuenta_screen.dart';
import 'login_screen.dart';

/// Contenedor de la aplicacion del acompanante familiar (RF09).
///
/// Es un recorrido distinto del que ve el paciente, no el mismo con permisos
/// recortados: el familiar no tiene plan de tomas, ni recordatorios, ni ficha
/// clinica. Solo ve las dosis que su familiar ya reporto y puede dar fe de
/// ellas.
class InicioFamiliar extends StatefulWidget {
  const InicioFamiliar({super.key, required this.api, required this.usuario});

  final ServicioApi api;
  final Usuario usuario;

  @override
  State<InicioFamiliar> createState() => _InicioFamiliarState();
}

class _InicioFamiliarState extends State<InicioFamiliar> {
  final GlobalKey<PorConfirmarState> _confirmar = GlobalKey<PorConfirmarState>();

  int _pestana = 0;

  Future<void> _cerrarSesion() async {
    await Almacenamiento.instancia.cerrarSesion();
    widget.api.token = null;
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute<void>(builder: (_) => LoginScreen(api: widget.api)),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _pestana,
        children: [
          PorConfirmar(
            key: _confirmar,
            api: widget.api,
            usuario: widget.usuario,
          ),
          CuentaScreen(
            usuario: widget.usuario,
            alCerrarSesion: _cerrarSesion,
            api: widget.api,
            // Al acompanar a alguien mas, la lista de pendientes cambia.
            alUnirseAOtroPaciente: () => _confirmar.currentState?.recargar(),
          ),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _pestana,
        onDestinationSelected: (indice) {
          setState(() => _pestana = indice);
          if (indice == 0) _confirmar.currentState?.recargar();
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.fact_check_outlined),
            selectedIcon: Icon(Icons.fact_check),
            label: 'Confirmar',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Mi cuenta',
          ),
        ],
      ),
    );
  }
}

/// Tomas que el acompanante puede corroborar.
class PorConfirmar extends StatefulWidget {
  const PorConfirmar({
    super.key,
    required this.api,
    required this.usuario,
  });

  final ServicioApi api;
  final Usuario usuario;

  @override
  State<PorConfirmar> createState() => PorConfirmarState();
}

class PorConfirmarState extends State<PorConfirmar> {
  List<PacienteAcompanado> _pacientes = const [];
  List<TomaPorConfirmar> _pendientes = const [];

  bool _cargando = true;
  String? _error;
  final Set<String> _enviando = {};

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  Future<void> recargar() => _cargar();

  Future<void> _cargar() async {
    setState(() => _cargando = true);
    try {
      final pacientes = await widget.api.misPacientes();
      final pendientes = await widget.api.tomasPorConfirmar();
      if (!mounted) return;
      setState(() {
        _pacientes = pacientes;
        _pendientes = pendientes;
        _error = null;
        _cargando = false;
      });
    } on ErrorDeConexion {
      if (!mounted) return;
      setState(() {
        // El acompanante no registra nada propio: sin conexion no hay cola que
        // guardar, solo una lista que no se puede leer.
        _error = 'Sin conexión. Vuelva a intentarlo cuando tenga internet.';
        _cargando = false;
      });
    } on ErrorApi catch (e) {
      if (!mounted) return;
      if (e.sesionExpirada) {
        await Almacenamiento.instancia.cerrarSesion();
        widget.api.token = null;
        if (!mounted) return;
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute<void>(builder: (_) => LoginScreen(api: widget.api)),
          (_) => false,
        );
        return;
      }
      setState(() {
        _error = e.mensaje;
        _cargando = false;
      });
    }
  }

  Future<void> _confirmar(TomaPorConfirmar toma) async {
    setState(() => _enviando.add(toma.idRegistro));
    try {
      await widget.api.confirmarToma(toma.idRegistro);
      if (!mounted) return;
      setState(() {
        _pendientes =
            _pendientes.where((t) => t.idRegistro != toma.idRegistro).toList();
        _enviando.remove(toma.idRegistro);
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Confirmado. Gracias.',
              style: TextStyle(fontSize: 17)),
          backgroundColor: Tema.exito,
        ),
      );
      await _cargar();
    } on ErrorDeConexion catch (e) {
      _fallo(toma, e.mensaje);
    } on ErrorApi catch (e) {
      _fallo(toma, e.mensaje);
    }
  }

  void _fallo(TomaPorConfirmar toma, String mensaje) {
    if (!mounted) return;
    setState(() => _enviando.remove(toma.idRegistro));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje, style: const TextStyle(fontSize: 17)),
        backgroundColor: Tema.peligro,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final variosPacientes = _pacientes.length > 1;

    return Scaffold(
      appBar: AppBar(title: const Text('Acompañamiento')),
      body: RefreshIndicator(
        onRefresh: _cargar,
        child: _cargando
            ? const Center(child: CircularProgressIndicator())
            : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  Text(
                    'Hola, ${widget.usuario.nombres}',
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Confirme solo las tomas que usted vio. Si no le consta, '
                    'déjela sin confirmar y converse con su familiar.',
                    style: TextStyle(fontSize: 16, color: Tema.neutro),
                  ),
                  const SizedBox(height: 16),

                  if (_error != null)
                    MensajeEstado(
                      texto: _error!,
                      tono: TonoMensaje.aviso,
                      textoAccion: 'Reintentar',
                      accion: _cargar,
                    ),

                  ..._pacientes.map((p) => _ResumenPaciente(paciente: p)),

                  const SizedBox(height: 8),
                  const Text(
                    'Tomas por confirmar',
                    style: TextStyle(fontSize: 19, fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(height: 10),

                  if (_pendientes.isEmpty && _error == null)
                    const _SinPendientes()
                  else
                    ..._pendientes.map(
                      (t) => _TarjetaPorConfirmar(
                        toma: t,
                        mostrarPaciente: variosPacientes,
                        enviando: _enviando.contains(t.idRegistro),
                        alConfirmar: () => _confirmar(t),
                      ),
                    ),
                ],
              ),
      ),
    );
  }
}

class _ResumenPaciente extends StatelessWidget {
  const _ResumenPaciente({required this.paciente});

  final PacienteAcompanado paciente;

  @override
  Widget build(BuildContext context) {
    final tasa = paciente.tasaAdherencia;

    return Card(
      color: Colors.white,
      elevation: 0,
      margin: Tema.margenTarjeta,
      shape: Tema.formaTarjeta,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          children: [
            const CircleAvatar(
              radius: 24,
              backgroundColor: Tema.fondo,
              child: Icon(Icons.favorite_outline, color: Tema.primario, size: 26),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    paciente.nombre,
                    style: const TextStyle(
                      fontSize: 19,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  Text(
                    paciente.parentesco.etiqueta,
                    style: const TextStyle(fontSize: 16, color: Tema.neutro),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    tasa == null
                        ? 'Todavía no hay tomas registradas.'
                        : 'Ha cumplido el ${tasa.toStringAsFixed(0)} % de sus '
                            'tomas.',
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
    );
  }
}

class _TarjetaPorConfirmar extends StatelessWidget {
  const _TarjetaPorConfirmar({
    required this.toma,
    required this.mostrarPaciente,
    required this.enviando,
    required this.alConfirmar,
  });

  final TomaPorConfirmar toma;
  final bool mostrarPaciente;
  final bool enviando;
  final VoidCallback alConfirmar;

  @override
  Widget build(BuildContext context) {
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
            if (mostrarPaciente)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Text(
                  toma.paciente,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Tema.primarioOscuro,
                  ),
                ),
              ),
            Text(
              toma.descripcion,
              style: const TextStyle(fontSize: 19, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 4),
            Text(
              'Dijo haberla tomado a las ${toma.horaReportada} '
              'del ${formatoFecha(toma.programada)}.',
              style: const TextStyle(fontSize: 16, color: Tema.neutro),
            ),
            const SizedBox(height: 14),
            FilledButton.icon(
              onPressed: enviando ? null : alConfirmar,
              icon: enviando
                  ? const SizedBox(
                      height: 22,
                      width: 22,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.verified_user_outlined, size: 26),
              label: const Text('Sí, la tomó'),
            ),
          ],
        ),
      ),
    );
  }
}

class _SinPendientes extends StatelessWidget {
  const _SinPendientes();

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.white,
      elevation: 0,
      margin: Tema.margenTarjeta,
      shape: Tema.formaTarjeta,
      child: const Padding(
        padding: EdgeInsets.all(22),
        child: Column(
          children: [
            Icon(Icons.check_circle_outline, size: 56, color: Tema.exito),
            SizedBox(height: 14),
            Text(
              'No hay nada por confirmar',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 19, fontWeight: FontWeight.w600),
            ),
            SizedBox(height: 8),
            Text(
              'Aquí aparecerán las tomas de las últimas 48 horas que su '
              'familiar haya registrado y usted todavía no haya confirmado.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Tema.neutro),
            ),
          ],
        ),
      ),
    );
  }
}
