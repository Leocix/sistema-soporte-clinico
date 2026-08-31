import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import '../models/medicamento.dart';
import '../models/sesion.dart';
import '../models/toma.dart';
import '../utils/constantes.dart';

/// Persistencia local del dispositivo.
///
/// Guarda tres cosas: la sesion (token y usuario), el plan de tomas que el
/// paciente declara, y la **cola de eventos pendientes de envio**. Esta ultima
/// es la que permite que la aplicacion siga siendo util sin cobertura, que es
/// la condicion real de buena parte de los pacientes del consultorio.
class Almacenamiento {
  Almacenamiento._();

  static final Almacenamiento instancia = Almacenamiento._();

  SharedPreferences? _prefs;

  Future<SharedPreferences> get _p async =>
      _prefs ??= await SharedPreferences.getInstance();

  // --- Sesion --------------------------------------------------------------

  Future<void> guardarSesion(String token, Usuario usuario) async {
    final p = await _p;
    await p.setString(Constantes.claveToken, token);
    await p.setString(Constantes.claveUsuario, jsonEncode(usuario.aJson()));
  }

  Future<String?> leerToken() async =>
      (await _p).getString(Constantes.claveToken);

  Future<Usuario?> leerUsuario() async {
    final crudo = (await _p).getString(Constantes.claveUsuario);
    if (crudo == null) return null;
    try {
      return Usuario.desdeJson(jsonDecode(crudo) as Map<String, dynamic>);
    } catch (_) {
      return null;
    }
  }

  /// Cierra la sesion.
  ///
  /// El plan de tomas y la cola pendiente NO se borran: si el paciente vuelve
  /// a entrar, sus medicamentos siguen configurados y los eventos que aun no
  /// se enviaron no se pierden.
  Future<void> cerrarSesion() async {
    final p = await _p;
    await p.remove(Constantes.claveToken);
    await p.remove(Constantes.claveUsuario);
  }

  // --- Plan de tomas -------------------------------------------------------

  Future<List<Medicamento>> leerPlan() async {
    final crudo = (await _p).getString(Constantes.clavePlan);
    if (crudo == null) return const [];
    try {
      final lista = jsonDecode(crudo) as List<dynamic>;
      return lista
          .whereType<Map<String, dynamic>>()
          .map(Medicamento.desdeJson)
          .toList();
    } catch (_) {
      return const [];
    }
  }

  Future<void> guardarPlan(List<Medicamento> plan) async {
    final p = await _p;
    await p.setString(
      Constantes.clavePlan,
      jsonEncode(plan.map((m) => m.aJson()).toList()),
    );
  }

  // --- Cola de envio pendiente --------------------------------------------

  Future<List<Toma>> leerCola() async {
    final crudo = (await _p).getString(Constantes.claveCola);
    if (crudo == null) return const [];
    try {
      final lista = jsonDecode(crudo) as List<dynamic>;
      return lista
          .whereType<Map<String, dynamic>>()
          .map(Toma.desdeJsonLocal)
          .toList();
    } catch (_) {
      return const [];
    }
  }

  Future<void> guardarCola(List<Toma> cola) async {
    final p = await _p;
    await p.setString(
      Constantes.claveCola,
      jsonEncode(cola.map((t) => t.aJsonLocal()).toList()),
    );
  }

  /// Anade un evento a la cola, sustituyendo cualquier respuesta anterior
  /// para la misma dosis.
  ///
  /// Si el paciente marca "no la tome" y se corrige a continuacion, lo que
  /// debe llegar al servidor es la ultima respuesta, no las dos.
  Future<List<Toma>> encolar(Toma toma) async {
    final cola = List<Toma>.from(await leerCola())
      ..removeWhere((t) => t.clave == toma.clave)
      ..add(toma);
    await guardarCola(cola);
    return cola;
  }

  /// Retira de la cola los eventos ya confirmados por el servidor.
  Future<List<Toma>> descartarDeLaCola(Iterable<String> claves) async {
    final aDescartar = claves.toSet();
    final cola =
        (await leerCola()).where((t) => !aDescartar.contains(t.clave)).toList();
    await guardarCola(cola);
    return cola;
  }
}
