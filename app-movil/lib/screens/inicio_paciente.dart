import 'package:flutter/material.dart';

import '../models/sesion.dart';
import '../services/almacenamiento.dart';
import '../services/api_service.dart';
import 'cuenta_screen.dart';
import 'familia_screen.dart';
import 'home_screen.dart';
import 'login_screen.dart';
import 'plan_screen.dart';

/// Contenedor de la aplicacion del paciente, con barra inferior.
///
/// Sustituye al menu de tres puntos que antes escondia «Mis medicamentos» y
/// «Cerrar sesion». Para el usuario objetivo —un adulto mayor polimedicado—
/// un icono sin etiqueta en una esquina no es un menu: es una funcion que no
/// existe. Con cuatro destinos rotulados, todo lo que la aplicacion hace queda
/// a la vista y a un solo toque (RNF03).
class InicioPaciente extends StatefulWidget {
  const InicioPaciente({super.key, required this.api, required this.usuario});

  final ServicioApi api;
  final Usuario usuario;

  @override
  State<InicioPaciente> createState() => _InicioPacienteState();
}

class _InicioPacienteState extends State<InicioPaciente> {
  /// Permite pedirle a la pestana de hoy que se recargue cuando el plan
  /// cambia en otra pestana.
  final GlobalKey<HomeScreenState> _hoy = GlobalKey<HomeScreenState>();

  int _pestana = 0;

  /// Pestanas ya abiertas alguna vez.
  ///
  /// `IndexedStack` construye todos sus hijos de golpe, de modo que sin esto
  /// la aplicacion pediria el grupo familiar al servidor nada mas arrancar,
  /// aunque el paciente no fuera a esa pestana. Una vez visitada, la pestana
  /// permanece construida y conserva su estado.
  final Set<int> _abiertas = {0};

  void _irA(int indice) {
    setState(() {
      _pestana = indice;
      _abiertas.add(indice);
    });
    // Al volver a «Hoy» el plan puede haber cambiado en «Medicinas».
    if (indice == 0) _hoy.currentState?.recargar();
  }

  Future<void> _cerrarSesion() async {
    await Almacenamiento.instancia.cerrarSesion();
    widget.api.token = null;
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute<void>(builder: (_) => LoginScreen(api: widget.api)),
      (_) => false,
    );
  }

  Widget _pantalla(int indice) => switch (indice) {
        0 => HomeScreen(
            key: _hoy,
            api: widget.api,
            usuario: widget.usuario,
            alIrAMedicamentos: () => _irA(1),
          ),
        1 => PlanScreen(alCambiarPlan: () => _hoy.currentState?.recargar()),
        2 => FamiliaScreen(api: widget.api),
        _ => CuentaScreen(
            usuario: widget.usuario,
            alCerrarSesion: _cerrarSesion,
          ),
      };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(
        index: _pestana,
        children: List.generate(
          4,
          (i) => _abiertas.contains(i) ? _pantalla(i) : const SizedBox.shrink(),
        ),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _pestana,
        onDestinationSelected: _irA,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.today_outlined),
            selectedIcon: Icon(Icons.today),
            label: 'Hoy',
          ),
          NavigationDestination(
            icon: Icon(Icons.medication_outlined),
            selectedIcon: Icon(Icons.medication),
            label: 'Medicinas',
          ),
          NavigationDestination(
            icon: Icon(Icons.diversity_3_outlined),
            selectedIcon: Icon(Icons.diversity_3),
            label: 'Familia',
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
