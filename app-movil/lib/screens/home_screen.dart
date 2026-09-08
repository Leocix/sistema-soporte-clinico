import 'package:flutter/material.dart';

import '../models/medicamento.dart';
import '../models/resumen_adherencia.dart';
import '../models/sesion.dart';
import '../models/toma.dart';
import '../services/almacenamiento.dart';
import '../services/api_service.dart';
import '../services/sincronizacion.dart';
import '../utils/constantes.dart';
import '../utils/tema.dart';
import '../widgets/mensaje_estado.dart';
import '../widgets/tarjeta_toma.dart';
import 'login_screen.dart';
import 'registro_toma.dart';

/// Pestana principal del paciente: las tomas de hoy y como va el cumplimiento.
///
/// Es una de las pestanas de [InicioPaciente], no una pantalla suelta: por eso
/// no lleva ni menu de opciones ni cierre de sesion, que viven en la barra
/// inferior. El estado se declara publico para que el contenedor pueda pedirle
/// que se recargue al volver de la pestana de medicamentos, donde el plan del
/// dia pudo cambiar.
class HomeScreen extends StatefulWidget {
  const HomeScreen({
    super.key,
    required this.api,
    required this.usuario,
    required this.alIrAMedicamentos,
  });

  final ServicioApi api;
  final Usuario usuario;

  /// Lleva a la pestana del plan de tomas, en lugar de apilar otra pantalla
  /// encima y esconder la barra inferior.
  final VoidCallback alIrAMedicamentos;

  @override
  State<HomeScreen> createState() => HomeScreenState();
}

class HomeScreenState extends State<HomeScreen> {
  late final ServicioSincronizacion _sync = ServicioSincronizacion(widget.api);

  List<Medicamento> _plan = const [];
  List<Toma> _registrosDelDia = const [];
  List<Toma> _enCola = const [];
  ResumenAdherencia? _resumen;

  bool _cargando = true;
  bool _sincronizando = false;
  String? _error;

  DateTime get _inicioDelDia {
    final ahora = DateTime.now();
    return DateTime(ahora.year, ahora.month, ahora.day);
  }

  @override
  void initState() {
    super.initState();
    _cargar();
  }

  /// Vuelve a leer el plan y el historial. La invoca el contenedor cuando el
  /// paciente regresa a esta pestana.
  Future<void> recargar() => _cargar();

  /// Carga el plan local y, si hay conexion, lo contrasta con el servidor.
  ///
  /// La falta de red no vacia la pantalla: el plan y la cola son locales, de
  /// modo que el paciente sigue viendo sus tomas de hoy y puede responderlas
  /// aunque el API no conteste.
  Future<void> _cargar() async {
    setState(() => _cargando = true);

    final plan = await Almacenamiento.instancia.leerPlan();
    final cola = await Almacenamiento.instancia.leerCola();

    var registros = const <Toma>[];
    ResumenAdherencia? resumen;
    String? error;

    try {
      registros = await widget.api.misRegistros(desde: _inicioDelDia);
      resumen = await widget.api.miResumen();
    } on ErrorDeConexion {
      // No se afirma que el paciente no tenga internet: la causa mas frecuente
      // es que el servicio este arrancando, y decirle que revise su conexion
      // cuando su conexion esta bien es mandarlo a buscar donde no hay nada.
      error = 'No se pudo conectar con el servidor. Puede registrar sus tomas '
          'igual: se enviarán solas en cuanto vuelva la conexión.';
    } on ErrorApi catch (e) {
      if (e.sesionExpirada) {
        await _cerrarSesion();
        return;
      }
      error = e.mensaje;
    }

    if (!mounted) return;
    setState(() {
      _plan = plan;
      _enCola = cola;
      _registrosDelDia = registros;
      _resumen = resumen;
      _error = error;
      _cargando = false;
    });

    if (cola.isNotEmpty && error == null) {
      await _sincronizar(silencioso: true);
    }
  }

  /// Cruza el plan del dia con lo ya respondido, en el servidor o en la cola.
  List<DosisDelDia> get _dosisDeHoy {
    final base = _inicioDelDia;

    // La cola tiene prioridad sobre el servidor: contiene la respuesta mas
    // reciente, que todavia no ha llegado.
    final respondidas = <String, ({Toma toma, bool pendiente})>{};
    for (final registro in _registrosDelDia) {
      respondidas[registro.clave] = (toma: registro, pendiente: false);
    }
    for (final pendiente in _enCola) {
      respondidas[pendiente.clave] = (toma: pendiente, pendiente: true);
    }

    final dosis = <DosisDelDia>[];
    for (final medicamento in _plan) {
      for (final horario in medicamento.horarios) {
        final partes = horario.split(':');
        if (partes.length != 2) continue;
        final hora = int.tryParse(partes[0]);
        final minuto = int.tryParse(partes[1]);
        if (hora == null || minuto == null) continue;

        final programada = base.add(Duration(hours: hora, minutes: minuto));
        final clave =
            '${medicamento.etiqueta}|${programada.toUtc().toIso8601String()}';
        final respuesta = respondidas[clave];

        dosis.add(
          DosisDelDia(
            medicamento: medicamento.etiqueta,
            dosis: medicamento.dosis,
            programada: programada,
            registro: respuesta?.toma,
            pendienteDeEnvio: respuesta?.pendiente ?? false,
          ),
        );
      }
    }

    dosis.sort((a, b) => a.programada.compareTo(b.programada));
    return dosis;
  }

  Future<void> _responder(Toma toma) async {
    try {
      final enviado = await _sync.registrar(toma);
      final cola = await Almacenamiento.instancia.leerCola();

      if (!mounted) return;
      setState(() => _enCola = cola);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            enviado
                ? 'Registrado. ¡Gracias!'
                : 'Guardado en su teléfono. Se enviará cuando haya internet.',
            style: const TextStyle(fontSize: 17),
          ),
          backgroundColor: enviado ? Tema.exito : Tema.aviso,
        ),
      );

      if (enviado) await _refrescarResumen();
    } on ErrorApi catch (e) {
      if (!mounted) return;
      if (e.sesionExpirada) {
        await _cerrarSesion();
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.mensaje, style: const TextStyle(fontSize: 17)),
          backgroundColor: Tema.peligro,
        ),
      );
    }
  }

  Future<void> _confirmar(DosisDelDia dosis) => _responder(
        Toma.cumplida(
          medicamento: dosis.medicamento,
          dosis: dosis.dosis,
          programada: dosis.programada,
        ),
      );

  Future<void> _omitir(DosisDelDia dosis) async {
    final toma = await Navigator.of(context).push<Toma>(
      MaterialPageRoute(
        builder: (_) => RegistroTomaScreen(
          medicamento: dosis.medicamento,
          dosis: dosis.dosis,
          programada: dosis.programada,
        ),
      ),
    );
    if (toma != null) await _responder(toma);
  }

  Future<void> _refrescarResumen() async {
    try {
      final resumen = await widget.api.miResumen();
      final registros = await widget.api.misRegistros(desde: _inicioDelDia);
      if (!mounted) return;
      setState(() {
        _resumen = resumen;
        _registrosDelDia = registros;
      });
    } on ErrorDeConexion {
      // El resumen es informativo: si no llega, la pantalla sigue siendo util.
    } on ErrorApi {
      // Idem.
    }
  }

  Future<void> _sincronizar({bool silencioso = false}) async {
    setState(() => _sincronizando = true);
    final resultado = await _sync.sincronizar();
    final cola = await Almacenamiento.instancia.leerCola();

    if (!mounted) return;
    setState(() {
      _enCola = cola;
      _sincronizando = false;
      if (resultado.huboFallo) _error = resultado.error;
    });

    if (resultado.enviados > 0) {
      await _refrescarResumen();
      if (!mounted) return;
      setState(() => _error = null);
      if (!silencioso) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Se enviaron ${resultado.enviados} registro(s).',
              style: const TextStyle(fontSize: 17),
            ),
            backgroundColor: Tema.exito,
          ),
        );
      }
    }
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

  @override
  Widget build(BuildContext context) {
    final dosis = _dosisDeHoy;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mi tratamiento'),
        actions: [
          if (_enCola.isNotEmpty)
            IconButton(
              tooltip: 'Enviar registros pendientes',
              icon: _sincronizando
                  ? const SizedBox(
                      height: 22,
                      width: 22,
                      child: CircularProgressIndicator(
                        strokeWidth: 2.5,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.cloud_upload_outlined),
              onPressed: _sincronizando ? null : () => _sincronizar(),
            ),
        ],
      ),
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
                  Text(
                    'Tomas de hoy, ${formatoFecha(DateTime.now())}',
                    style: const TextStyle(fontSize: 17, color: Tema.neutro),
                  ),
                  const SizedBox(height: 16),
                  if (_error != null)
                    MensajeEstado(
                      texto: _error!,
                      tono: TonoMensaje.aviso,
                      textoAccion: 'Reintentar',
                      accion: _cargar,
                    ),
                  if (_enCola.isNotEmpty)
                    MensajeEstado(
                      texto: '${_enCola.length} registro(s) guardado(s) en el '
                          'teléfono, pendientes de enviar.',
                      tono: TonoMensaje.aviso,
                      textoAccion: 'Enviar',
                      accion: _sincronizando ? null : () => _sincronizar(),
                    ),
                  if (_resumen != null) _Resumen(resumen: _resumen!),
                  const SizedBox(height: 8),
                  if (_plan.isEmpty)
                    _SinPlan(alConfigurar: widget.alIrAMedicamentos)
                  else
                    ...dosis.map(
                      (d) => TarjetaToma(
                        dosis: d,
                        alConfirmar: () => _confirmar(d),
                        alOmitir: () => _omitir(d),
                      ),
                    ),
                ],
              ),
      ),
    );
  }
}

class _Resumen extends StatelessWidget {
  const _Resumen({required this.resumen});

  final ResumenAdherencia resumen;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.white,
      elevation: 0,
      margin: Tema.margenTarjeta,
      shape: Tema.formaTarjeta,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Cómo va su tratamiento',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            if (!resumen.sinDatos)
              Row(
                children: [
                  Text(
                    '${resumen.tasaAdherencia.toStringAsFixed(0)} %',
                    style: const TextStyle(
                      fontSize: 40,
                      fontWeight: FontWeight.w800,
                      color: Tema.primario,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Text(
                      'de sus tomas cumplidas\n'
                      '(${resumen.cumplidos} de ${resumen.totalEventos})',
                      style: const TextStyle(fontSize: 16, color: Tema.neutro),
                    ),
                  ),
                ],
              ),
            const SizedBox(height: 10),
            Text(
              resumen.mensaje,
              style: const TextStyle(fontSize: 17, height: 1.4),
            ),
          ],
        ),
      ),
    );
  }
}

class _SinPlan extends StatelessWidget {
  const _SinPlan({required this.alConfigurar});

  final VoidCallback alConfigurar;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.white,
      elevation: 0,
      margin: Tema.margenTarjeta,
      shape: Tema.formaTarjeta,
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          children: [
            const Icon(Icons.medication_outlined, size: 56, color: Tema.neutro),
            const SizedBox(height: 14),
            const Text(
              'Todavía no ha registrado sus medicamentos',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 19, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            const Text(
              'Agréguelos con la hora en que los toma y aquí aparecerá su '
              'lista de cada día.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 16, color: Tema.neutro),
            ),
            const SizedBox(height: 18),
            FilledButton.icon(
              onPressed: alConfigurar,
              icon: const Icon(Icons.add),
              label: const Text('Agregar mis medicamentos'),
            ),
          ],
        ),
      ),
    );
  }
}
